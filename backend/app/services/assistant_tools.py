"""Bounded authorized projections over existing intelligence, dependencies and memory."""
from datetime import UTC, datetime, timedelta
import re
from sqlalchemy import func, select
from backend.app.core.errors import ApiError
from backend.app.db.intelligence_repository import memory, project_inputs, visible_projects
from backend.app.db.ingestion_repository import current_dependencies
from backend.app.db.repository import iso_datetime
from backend.app.models import AuditEvent, ExecutionWarning, FieldUpdate, ScheduleActivity
from backend.app.schemas.assistant import TOOL_NAMES, ToolArgs
from backend.app.services.execution_intelligence import calculate
from backend.app.services.project_intelligence_service import compute, enrich
from backend.app.services.assistant_catalogue import TEXT
from backend.app.services.assistant_security import private_prose


def safe_text(value, settings, limit=None):
    text = str(value or "")
    if re.search(r"medical|mental[ -]?health|diagnos|grievance|depression|salary|चिकित्सा|मानसिक|शिकायत", text, re.I):
        return "[SENSITIVE_CONTENT_WITHHELD]"
    if private_prose(text):
        return "[PRIVATE_CONTENT_WITHHELD]"
    for name, secret in settings.model_dump().items():
        if not isinstance(secret, str) or not re.search(r"password|secret|api_key|database_url", name):
            continue
        if secret:
            text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"(?i)(?:bearer\s+\S+|(?:password|api[_ -]?key|secret|session[_ -]?token|jwt[_ -]?secret|database[_ -]?url)\s*[:=]\s*\S+|(?:postgres(?:ql)?|https?)://[^\s]*:[^\s]*@[^\s]*)", "[REDACTED]", text)
    return text[:limit or settings.assistant_excerpt_chars]


def clean(value, settings):
    if isinstance(value, str):
        return safe_text(value, settings)
    if isinstance(value, list):
        return [clean(v, settings) for v in value[:settings.assistant_record_limit]]
    if isinstance(value, dict):
        return {k: clean(v, settings) for k, v in value.items() if not re.search(r"password|secret|token|api.?key|database.?url|source.?code|server.?config|system.?prompt|medical|mental|grievance|attachment|actor|submitter|reviewer", k, re.I)}
    return value


def execution(session, user, context, settings):
    pid, tid = context["projectId"], context["teamId"]
    if not tid:
        result = compute(session, pid, settings)
    else:
        inputs = project_inputs(session, pid, settings.intelligence_max_input_rows, team_ids=[tid])
        visible = {a["id"] for a in inputs[0]}
        # Ignore recommendations/links outside team scope rather than exposing their IDs.
        for row in inputs[0]:
            row["predecessorIds"] = [i for i in row.get("predecessorIds", []) if i in visible] if isinstance(row.get("predecessorIds", []), list) else []
        for match in inputs[2]:
            for key in ("scheduleActivityId", "recommendedMatchId", "reportedActivityId"):
                if match.get(key) not in visible:
                    match[key] = None
        result = calculate(pid, *inputs, settings)
        edges = [e for e in current_dependencies(session, pid) if e["predecessorId"] in visible and e["successorId"] in visible]
        result = enrich(result, edges, pid)
    warnings = result["warnings"]
    saved = {r.id: r for r in session.scalars(select(ExecutionWarning).where(ExecutionWarning.project_id == pid, ExecutionWarning.id.in_([w["id"] for w in warnings])))}
    for warning in warnings:
        row = saved.get(warning["id"])
        if row and row.status != "RESOLVED":
            warning["status"] = row.status
            warning["generatedAt"] = iso_datetime(row.generated_at)
    return result


def read_tool(session, user, context, name, args, settings, execution_cache=None):
    if name not in TOOL_NAMES:
        raise ApiError(400, "INVALID_TOOL", "Only approved assistant read tools are available.")
    args = ToolArgs.model_validate(args)
    args.limit = min(args.limit, settings.assistant_record_limit)
    pid, tid = context["projectId"], context["teamId"]
    now = datetime.now(UTC).isoformat()
    records = []
    limitations = []
    total = 0
    def record(kind, identifier, data, timestamp=None, category="DERIVED_METRICS"):
        records.append({"evidenceId": f"{name}:{kind}:{identifier}", "kind": kind, "recordId": identifier,
                        "timestamp": timestamp, "dataCategory": category, "data": clean(data, settings)})
        if category == "APPLICATION_GUIDANCE" and "approvedWorkflow" in data:
            records[-1]["data"]["approvedWorkflow"] = safe_text(data["approvedWorkflow"], settings, settings.assistant_question_chars)
    if args.activity_id:
        q = select(ScheduleActivity.id).where(ScheduleActivity.id == args.activity_id, ScheduleActivity.project_id == pid)
        if tid:
            q = q.where(ScheduleActivity.team_id == tid)
        if not session.scalar(q):
            raise ApiError(404, "NOT_FOUND", "Activity is outside the authorized assistant context.")
    if name == "get_project_summary" and args.conversational:
        record("assistant_context", pid or context["organizationId"], {
            "assistantIdentity": "PRAVAHA Project Assistant",
            "projectName": context.get("projectName"), "scope": context["scope"], "role": context["role"],
            "dataLabel": context["dataLabel"],
            "approvedCapabilities": "Explain authorized progress, assigned work, reviews, warnings, dependencies and field-update workflows. Read-only; cannot approve or modify project data.",
        }, now, "APPLICATION_GUIDANCE")
    elif not pid:
        if name != "get_project_summary":
            raise ApiError(400, "CONTEXT_REQUIRED", "Choose a project for detailed execution evidence.")
        rows, total = visible_projects(session, user, args.limit, args.offset)
        for row in rows:
            record("project", row.id, {"id": row.id, "name": row.name, "status": row.status}, category="RECORDED")
    elif name in {"search_project_memory", "get_activity_timeline"}:
        if name == "get_activity_timeline" and not args.activity_id:
            raise ApiError(400, "ACTIVITY_REQUIRED", "Select an activity for its timeline.")
        since = datetime.now(UTC) - timedelta(days=args.recent_days) if args.recent_days else None
        result = memory(session, user, pid, activity_id=args.activity_id, query=args.query,
                        limit=args.limit, offset=args.offset, team_ids=[tid] if tid else None,
                        assistant_safe=True, since=since)
        total = result["total"]
        for event in result["items"]:
            details = event.get("details") or {}
            # Never send whole JSON payloads or audit actor identities to inference.
            safe = {k: details[k] for k in ("fieldUpdateId", "activityId", "scheduleActivityId", "reviewStatus", "status", "decision", "progress", "actualStart", "actualEnd", "reason", "feedback", "pmFeedback") if k in details}
            if event["kind"] == "confirmed_actual":
                safe["state"] = {k: details.get("state", {}).get(k) for k in ("progress", "actualStart", "actualEnd", "status")}
            record("memory", event["id"], {"kind": event["kind"], "excerpt": event["action"], "details": safe}, event["occurredAt"], "RECORDED")
        if not records:
            record("memory_summary", pid, {"matchingRecords": total, "status": "No matching authorized execution records; insufficient evidence for an event or cause."}, now)
        limitations.append("Memory contains recorded execution events; absence of a decision/lesson record is not evidence that one occurred.")
    elif name == "get_pending_reviews":
        q = select(FieldUpdate).where(FieldUpdate.project_id == pid, FieldUpdate.payload_json["reviewStatus"].astext.is_distinct_from("reviewed"))
        if tid:
            q = q.where(FieldUpdate.team_id == tid)
        total = session.scalar(select(func.count()).select_from(q.subquery()))
        grouped = select(FieldUpdate.team_id, func.count()).where(FieldUpdate.id.in_(q.with_only_columns(FieldUpdate.id))).group_by(FieldUpdate.team_id).order_by(FieldUpdate.team_id).offset(args.offset).limit(args.limit)
        teams = [{"teamId": row[0], "pendingReviews": row[1]} for row in session.execute(grouped)]
        record("pending_summary", pid, {"pendingReviewCount": total, "teams": teams, "teamPagePartial": len(teams) == args.limit}, now)
        for row in session.scalars(q.order_by(FieldUpdate.id).offset(args.offset).limit(args.limit)):
            p = row.payload_json
            record("field_update", row.id, {"id": row.id, "teamId": row.team_id, "status": row.status,
                   "reviewStatus": p.get("reviewStatus"), "rawText": p.get("rawText"), "pmFeedback": p.get("pmFeedback")}, p.get("submittedAt"), "RECORDED")
    else:
        cache_key = (pid, tid)
        if execution_cache is None:
            result = execution(session, user, context, settings)
        else:
            if cache_key not in execution_cache:
                execution_cache[cache_key] = execution(session, user, context, settings)
            result = execution_cache[cache_key]
        if name == "get_project_summary":
            record("summary", pid, {"projectName": context["projectName"], "summary": result["summary"], "dataHealth": result["dataHealth"]}, result["evaluatedAt"])
        elif name == "get_project_health":
            record("health", pid, {"health": result["health"], "summary": result["summary"], "dataHealth": result["dataHealth"]}, result["evaluatedAt"])
            if not tid:
                q = select(AuditEvent.id, AuditEvent.occurred_at, AuditEvent.details_json["new"]["health"].label("health")).where(AuditEvent.organization_id == user.organization_id, AuditEvent.entity == "project_intelligence", AuditEvent.entity_id == pid).order_by(AuditEvent.occurred_at.desc(), AuditEvent.id.desc()).limit(args.limit)
                for row in session.execute(q):
                    record("health_history", row.id, {"health": row.health}, iso_datetime(row.occurred_at), "RECORDED_DERIVED_SNAPSHOT")
            limitations.append("History includes recorded refresh snapshots only, not a continuous score series. Current health alone establishes neither a decline nor its cause. Correlations do not prove causes.")
            if tid:
                limitations.append("TEAM-only health; whole-project health/history and dependencies outside the team are unavailable.")
        elif name == "get_execution_warnings":
            rows = result["warnings"]
            if args.activity_id:
                rows = [r for r in rows if r.get("activityId") == args.activity_id]
            total = len(rows)
            record("warning_summary", pid, {"warningCount": total}, result["evaluatedAt"])
            for row in rows[args.offset:args.offset + args.limit]:
                record("warning", row["id"], row, row["generatedAt"])
        elif name == "get_dependency_impact":
            impact = result.get("dependencyImpact", {"status": "NOT_AVAILABLE", "items": []})
            rows = impact.get("items", [])
            if args.activity_id:
                rows = [r for r in rows if r.get("activityId") == args.activity_id or r.get("sourceActivityId") == args.activity_id]
            total = len(rows)
            record("dependency_summary", pid, {"status": impact.get("status"), "reason": impact.get("reason"), "relationships": result["dependencyRelationships"]}, result["evaluatedAt"])
            for i, row in enumerate(rows[args.offset:args.offset + args.limit], args.offset):
                record("dependency", str(i), row, result["evaluatedAt"])
            limitations.append("Exposure uses existing persisted dependencies; it is an estimate, not a promised finish date or critical-path calculation.")
        else:
            rows = result["activities"]
            if name == "get_delayed_activities":
                risks = {w.get("activityId") for w in result["warnings"]}
                rows = [r for r in rows if r["timing"] == "DELAYED" or (args.at_risk and r["activityId"] in risks)]
            if args.activity_id:
                rows = [r for r in rows if r["activityId"] == args.activity_id]
            total = len(rows)
            if name == "get_delayed_activities":
                record("delay_summary", pid, {"matchingActivities": total, "includesAtRisk": args.at_risk, "missingActuals": result["summary"]["missingActuals"]}, result["evaluatedAt"])
            for row in rows[args.offset:args.offset + args.limit]:
                record("activity", row["activityId"], row, row.get("lastUpdateDate"))
        limitations.append(f"{result['summary']['missingActuals']} activities lack PM-confirmed actuals; {result['summary']['staleActivities']} have stale reports. Null actuals/variance are UNKNOWN, not zero.")
    if name in {"get_project_health", "get_project_summary"} and pid:
        total = len(records)
    if args.guidance_topic:
        if name != "get_project_summary":
            raise ApiError(400, "INVALID_TOOL", "Workflow guidance requires project summary scope.")
        record("workflow_guidance", args.guidance_topic, {"topic": args.guidance_topic, "approvedWorkflow": TEXT["en"][args.guidance_topic]}, now, "APPLICATION_GUIDANCE")
    partial = args.offset > 0 or total > args.offset + args.limit
    return {"tool": name, "context": context, "checkedAt": now, "records": records, "total": total,
            "limit": args.limit, "offset": args.offset, "partial": partial, "status": "AVAILABLE" if records else "NOT_AVAILABLE",
            "dataset": "SYNTHETIC_DEMO" if re.search(r"demo|synthetic|demonstration", context["dataLabel"], re.I) else "RECORDED_DATA",
            "limitations": limitations + (["Result is a bounded page; use offset for additional records."] if partial else [])}
