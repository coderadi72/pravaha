"""Authorized project intelligence and atomic warning lifecycle orchestration."""
from copy import deepcopy
from uuid import NAMESPACE_URL, uuid5
from sqlalchemy import select
from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor, require_project_access
from backend.app.db.intelligence_repository import project_inputs
from backend.app.db.repository import append_audit, iso_datetime, lock_organization, utc_now
from backend.app.models import AuditEvent, ExecutionWarning
from backend.app.services.execution_intelligence import calculate


def authorize(session, user, project_id):
    if user.role not in {"ADMIN", "PROJECT_MANAGER"}:
        raise ApiError(403, "FORBIDDEN", "Project intelligence requires Admin or assigned Project Manager access.")
    return require_project_access(session, user, project_id)


def compute(session, project_id, settings):
    from backend.app.db.ingestion_repository import current_dependencies
    from backend.app.services.dependency_service import downstream
    result = calculate(project_id, *project_inputs(session, project_id, settings.intelligence_max_input_rows), settings)
    edges = current_dependencies(session, project_id)
    return enrich(result, edges, project_id)


def enrich(result, edges, project_id):
    from backend.app.services.dependency_service import downstream
    impact = downstream(result['activities'], edges)
    result['dependencyImpact'] = impact
    if edges:
        result['dependencyRelationships'] = len(edges)
        estimates = [i for i in impact['items'] if i['status']=='ESTIMATED']
        result['health']['dependencyExposure'] = {'status':'HIGH' if estimates else impact['status'], 'reason':impact['reason']}
        for item in estimates:
            source = next(a for a in result['activities'] if a['activityId']==item['sourceActivityId'])
            source['potentialDownstream'].append(item)
            result['warnings'].append({'id':'EW-'+str(uuid5(NAMESPACE_URL,f"{project_id}:{item['sourceActivityId']}:{item['activityId']}:DEPENDENCY_CHAIN")),
                'projectId':project_id,'activityId':item['activityId'],'fieldUpdateId':None,'type':'DEPENDENCY_CHAIN','severity':'HIGH','status':'OPEN',
                'generatedAt':result['evaluatedAt'],'reason':item['reason'],'evidence':item['evidence'],'attention':'Review predecessor and successor execution evidence; no forecast date is asserted.'})
        result['summary']['atRiskActivities'] = len({w['activityId'] for w in result['warnings'] if w['activityId']})
        result['health']['warnings'] = {'status':'HIGH' if any(w['severity']=='HIGH' for w in result['warnings']) else 'ATTENTION' if result['warnings'] else 'CLEAR','reason':f"{len(result['warnings'])} evidence-backed signals."}
        result['warnings'].sort(key=lambda w:({'HIGH':0,'MEDIUM':1,'LOW':2}[w['severity']],w['id']))
    return result


def read_intelligence(session, user, project_id, settings, limit=50, offset=0):
    authorize(session, user, project_id)
    result = compute(session, project_id, settings)
    persisted = {w.id: w for w in session.scalars(select(ExecutionWarning).where(ExecutionWarning.project_id == project_id, ExecutionWarning.id.in_([w["id"] for w in result["warnings"]])))}
    for w in result["warnings"]:
        old = persisted.get(w["id"])
        if old and old.status != "RESOLVED":
            w["status"], w["generatedAt"] = old.status, iso_datetime(old.generated_at)
    result["warningTotal"] = len(result["warnings"])
    result["activityTotal"] = len(result["activities"])
    result["warnings"] = result["warnings"][offset:offset + limit]
    result["activities"] = result["activities"][offset:offset + limit]
    result["limit"], result["offset"] = limit, offset
    return result


def _state(payload):
    return {k: deepcopy(v) for k, v in payload.items() if k not in {"generatedAt", "status"}}


def reconcile(session, actor_data, project_id, settings):
    # Caller owns organization lock and transaction. Any audit error rolls everything back.
    result = compute(session, project_id, settings)
    now = utc_now()
    rows = {w.id: w for w in session.scalars(select(ExecutionWarning).where(ExecutionWarning.project_id == project_id))}
    system = {"organizationId": actor_data["organizationId"], "fullName": "PRAVAHA execution intelligence", "id": None}
    active = {w["id"] for w in result["warnings"]}
    for payload in result["warnings"]:
        row = rows.get(payload["id"])
        previous = ({**row.payload_json, "status": row.status} if row else None)
        changed = not row or row.status == "RESOLVED" or _state(row.payload_json) != _state(payload)
        if not changed:
            continue
        if not row:
            row = ExecutionWarning(id=payload["id"], project_id=project_id, activity_id=payload["activityId"], warning_type=payload["type"], status="OPEN", generated_at=now, updated_at=now, payload_json=payload)
            session.add(row)
        else:
            row.status = "OPEN" if row.status == "RESOLVED" else row.status
            row.updated_at, row.payload_json = now, {**payload, "generatedAt": iso_datetime(row.generated_at), "status": row.status}
        append_audit(session, system, "Execution warning generated" if previous is None else "Execution warning changed", "execution_warning", row.id, {"projectId": project_id, "activityId": row.activity_id, "previous": previous, "new": {**row.payload_json, "status": row.status}})
    for row in rows.values():
        if row.id not in active and row.status != "RESOLVED":
            previous = {**row.payload_json, "status": row.status}
            row.status, row.updated_at = "RESOLVED", now
            append_audit(session, system, "Execution warning resolved", "execution_warning", row.id, {"projectId": project_id, "activityId": row.activity_id, "previous": previous, "new": {**row.payload_json, "status": row.status}})
    snapshot = {"summary": result["summary"], "health": result["health"], "dataHealth": result["dataHealth"], "activities": result["activities"], "version": result["version"], "dependencyImpact": result.get("dependencyImpact")}
    last = session.scalar(select(AuditEvent).where(AuditEvent.organization_id == actor_data["organizationId"], AuditEvent.entity == "project_intelligence", AuditEvent.entity_id == project_id).order_by(AuditEvent.occurred_at.desc(), AuditEvent.id.desc()).limit(1))
    previous = last.details_json.get("new") if last else None
    if previous != snapshot:
        append_audit(session, system, "Execution intelligence changed", "project_intelligence", project_id, {"projectId": project_id, "previous": previous, "new": snapshot})
    session.flush()


def refresh(session, user, project_id, settings):
    authorize(session, user, project_id)
    lock_organization(session, user.organization_id)
    reconcile(session, actor(user), project_id, settings)
    return read_intelligence(session, user, project_id, settings)


def acknowledge(session, user, project_id, warning_id):
    authorize(session, user, project_id)
    lock_organization(session, user.organization_id)
    row = session.scalar(select(ExecutionWarning).where(ExecutionWarning.project_id == project_id, ExecutionWarning.id == warning_id))
    if not row:
        raise ApiError(404, "NOT_FOUND", "Warning not found. Refresh intelligence to persist current warnings.")
    if row.status == "RESOLVED":
        raise ApiError(409, "INVALID_STATE", "Resolved warnings cannot be acknowledged.")
    if row.status != "ACKNOWLEDGED":
        previous = row.status
        row.status, row.updated_at = "ACKNOWLEDGED", utc_now()
        append_audit(session, actor(user), "Execution warning acknowledged", "execution_warning", row.id, {"projectId": project_id, "activityId": row.activity_id, "previous": previous, "new": row.status, "evidence": row.payload_json.get("evidence")})
    return {"id": row.id, "status": row.status}


def portfolio(session, user, settings, limit=20, offset=0):
    from backend.app.db.intelligence_repository import visible_projects
    if user.role not in {"ADMIN", "PROJECT_MANAGER"}:
        raise ApiError(403, "FORBIDDEN", "Project intelligence requires Admin or assigned Project Manager access.")
    projects, total = visible_projects(session, user, limit, offset)
    activities, updates, matches, contributions = project_inputs(session, [p.id for p in projects], settings.intelligence_max_input_rows)
    from backend.app.db.ingestion_repository import dependencies_for_projects
    graph = dependencies_for_projects(session, [p.id for p in projects])
    items = []
    for project in projects:
        project_updates = [u for u in updates if u["projectId"] == project.id]
        update_ids = {u["id"] for u in project_updates}
        result = calculate(project.id, [a for a in activities if a["projectId"] == project.id], project_updates,
            [m for m in matches if m["fieldUpdateId"] in update_ids], [c for c in contributions if c["fieldUpdateId"] in update_ids], settings)
        result = enrich(result, [e for e in graph if e["projectId"] == project.id], project.id)
        items.append({"id": project.id, "name": project.name, "summary": result["summary"], "health": result["health"], "dataHealth": result["dataHealth"], "evaluatedAt": result["evaluatedAt"]})
    return {"items": items, "total": total, "limit": limit, "offset": offset}
