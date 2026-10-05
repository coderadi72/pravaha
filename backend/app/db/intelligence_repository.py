"""Project-scoped intelligence inputs and paginated persisted memory queries."""
from sqlalchemy.orm import with_expression
from sqlalchemy import DateTime, String, and_, cast, func, literal, or_, select, union_all
from backend.app.core.errors import ApiError
from backend.app.db.repository import iso_datetime
from backend.app.models import ActivityMatch, AuditEvent, FieldUpdate, Project, ProjectManagerAssignment, Review, ReviewHistory, ScheduleActivity, ScheduleActivityContribution

DEFAULT_MAX_INPUT_ROWS = 10000


def _bounded(session, query, max_input_rows=DEFAULT_MAX_INPUT_ROWS):
    rows = list(session.scalars(query.limit(max_input_rows + 1)))
    if len(rows) > max_input_rows:
        raise ApiError(409, "INTELLIGENCE_CAPACITY", f"Project intelligence exceeds the current {max_input_rows:,}-row input limit; partition or extend aggregation before use.")
    return rows


def project_inputs(session, project_id, max_input_rows=DEFAULT_MAX_INPUT_ROWS, team_ids=None):
    project_ids = project_id if isinstance(project_id, list) else [project_id]
    schedule_q = select(ScheduleActivity).where(ScheduleActivity.project_id.in_(project_ids), ScheduleActivity.payload_json["archived"].astext.is_distinct_from("true"))
    if team_ids is not None:
        schedule_q = schedule_q.where(ScheduleActivity.team_id.in_(team_ids))
    schedules = _bounded(session, schedule_q, max_input_rows)
    # Accepted evidence for retired schedule rows remains in memory/history, outside current execution coverage.
    retired = select(ActivityMatch.field_update_id).join(ScheduleActivity, ScheduleActivity.id == ActivityMatch.schedule_activity_id).where(ScheduleActivity.project_id.in_(project_ids), ScheduleActivity.payload_json["archived"].astext == "true", ActivityMatch.match_status == "matched")
    update_query = select(FieldUpdate.id).where(FieldUpdate.project_id.in_(project_ids), FieldUpdate.id.not_in(retired))
    if team_ids is not None:
        update_query = update_query.where(FieldUpdate.team_id.in_(team_ids))
    updates = _bounded(session, select(FieldUpdate).where(FieldUpdate.id.in_(update_query)), max_input_rows)
    matches = _bounded(session, select(ActivityMatch).outerjoin(ScheduleActivity, ScheduleActivity.id == ActivityMatch.schedule_activity_id).options(with_expression(ActivityMatch.retired_schedule_link, ScheduleActivity.payload_json["archived"].astext == "true")).where(ActivityMatch.field_update_id.in_(update_query)), max_input_rows)
    contributions = _bounded(session, select(ScheduleActivityContribution).where(ScheduleActivityContribution.field_update_id.in_(update_query)), max_input_rows)
    # Relations override JSON keys; consumers never trust stale client payload IDs.
    return (
        [{**a.payload_json, "id": a.id, "projectId": a.project_id, "teamId": a.team_id} for a in schedules],
        [{**u.payload_json, "id": u.id, "projectId": u.project_id, "teamId": u.team_id} for u in updates],
        [{**m.payload_json, "fieldUpdateId": m.field_update_id, "scheduleActivityId": m.schedule_activity_id, "matchStatus": m.match_status, "retiredScheduleLink": bool(m.retired_schedule_link)} for m in matches],
        [{"fieldUpdateId": c.field_update_id, "scheduleActivityId": c.schedule_activity_id, "recordedAt": iso_datetime(c.recorded_at), "state": c.state_json} for c in contributions],
    )


def visible_projects(session, user, limit, offset):
    q = select(Project).where(Project.organization_id == user.organization_id)
    if user.role != "ADMIN":
        q = q.join(ProjectManagerAssignment).where(ProjectManagerAssignment.user_id == user.id)
    total = session.scalar(select(func.count()).select_from(q.subquery()))
    return list(session.scalars(q.order_by(Project.id).offset(offset).limit(limit))), total


def memory(session, user, project_id, activity_id=None, query="", kind=None, limit=50, offset=0, team_ids=None, assistant_safe=False, since=None):
    scoped_updates = select(FieldUpdate.id).where(FieldUpdate.project_id == project_id)
    scoped_schedules = select(ScheduleActivity.id).where(ScheduleActivity.project_id == project_id)
    if team_ids is not None:
        scoped_updates = scoped_updates.where(FieldUpdate.team_id.in_(team_ids))
        scoped_schedules = scoped_schedules.where(ScheduleActivity.team_id.in_(team_ids))
    if activity_id:
        historic_update_ids = select(AuditEvent.entity_id).where(AuditEvent.organization_id == user.organization_id,
            AuditEvent.entity == "field_update", AuditEvent.details_json["projectId"].astext == project_id,
            or_(AuditEvent.details_json["scheduleActivityId"].astext == activity_id, AuditEvent.details_json["previous"]["scheduleActivityId"].astext == activity_id))
        scoped_updates = scoped_updates.outerjoin(ActivityMatch).where(or_(ActivityMatch.schedule_activity_id == activity_id,
            ActivityMatch.payload_json["recommendedMatchId"].astext == activity_id, ActivityMatch.payload_json["reportedActivityId"].astext == activity_id,
            FieldUpdate.id.in_(historic_update_ids)))
    # Existing records, not a parallel event ledger. IDs are namespaced by kind.
    statements = [
        select(FieldUpdate.id.label("id"), literal("field_update").label("kind"), cast(FieldUpdate.payload_json["submittedAt"].astext, DateTime(timezone=True)).label("occurred_at"), FieldUpdate.payload_json["submittedBy"].astext.label("actor"), FieldUpdate.payload_json["rawText"].astext.label("action"), FieldUpdate.payload_json.label("details")).where(FieldUpdate.id.in_(scoped_updates)),
        select(ReviewHistory.id, literal("review_history"), ReviewHistory.occurred_at, ReviewHistory.actor_label, ReviewHistory.action, func.jsonb_build_object("fieldUpdateId", ReviewHistory.field_update_id)).where(ReviewHistory.field_update_id.in_(scoped_updates)),
        select(Review.id, literal("review"), cast(Review.payload_json["reviewedAt"].astext, DateTime(timezone=True)), Review.payload_json["reviewer"].astext, Review.payload_json["reason"].astext, Review.payload_json).join(FieldUpdate, Review.field_update_id == FieldUpdate.id).where(Review.field_update_id.in_(scoped_updates)),
        select(ScheduleActivityContribution.field_update_id, literal("confirmed_actual"), ScheduleActivityContribution.recorded_at, literal("PM confirmed"), literal("Confirmed actual progress"), func.jsonb_build_object("activityId", ScheduleActivityContribution.schedule_activity_id, "state", ScheduleActivityContribution.state_json)).join(FieldUpdate, FieldUpdate.id == ScheduleActivityContribution.field_update_id).join(ActivityMatch, ActivityMatch.field_update_id == FieldUpdate.id).where(FieldUpdate.id.in_(scoped_updates), ActivityMatch.match_status == "matched", FieldUpdate.payload_json["reviewStatus"].astext == "reviewed"),
    ]
    audit_scope = or_(and_(AuditEvent.entity == "field_update", AuditEvent.entity_id.in_(scoped_updates)), and_(AuditEvent.entity == "schedule_activity", AuditEvent.entity_id.in_(scoped_schedules)), AuditEvent.details_json["projectId"].astext == project_id, and_(AuditEvent.entity == "project", AuditEvent.entity_id == project_id))
    aq = select(AuditEvent.id, literal("audit"), AuditEvent.occurred_at, AuditEvent.actor_label, AuditEvent.action, AuditEvent.details_json).where(AuditEvent.organization_id == user.organization_id, audit_scope)
    if assistant_safe:
        # Execution-only material; generic projectId on an HR audit is not permission.
        aq = aq.where(AuditEvent.entity.in_(["field_update", "schedule_activity", "review", "project_intelligence", "execution_warning", "schedule_version", "schedule_import", "project"]))
    if team_ids is not None:
        aq = aq.where(or_(and_(AuditEvent.entity == "field_update", AuditEvent.entity_id.in_(scoped_updates)), and_(AuditEvent.entity == "schedule_activity", AuditEvent.entity_id.in_(scoped_schedules))))
    if activity_id:
        aq = aq.where(or_(AuditEvent.entity_id == activity_id, AuditEvent.entity_id.in_(scoped_updates), AuditEvent.details_json["activityId"].astext == activity_id, AuditEvent.details_json["scheduleActivityId"].astext == activity_id, AuditEvent.details_json["previous"]["scheduleActivityId"].astext == activity_id))
    statements.append(aq)
    events = union_all(*statements).subquery()
    q = select(events)
    if since is not None:
        q = q.where(events.c.occurred_at >= since)
    if kind:
        q = q.where(events.c.kind == kind)
    if query:
        # Escape wildcard characters: search is literal, parameterized and bounded.
        pattern = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        q = q.where(or_(events.c.action.ilike(pattern, escape="\\"), cast(events.c.details, String).ilike(pattern, escape="\\")))
    total = session.scalar(select(func.count()).select_from(q.subquery()))
    results = session.execute(q.order_by(events.c.occurred_at.desc().nulls_last(), events.c.kind, events.c.id).offset(offset).limit(limit)).mappings()
    return {"items": [{"id": f'{r["kind"]}:{r["id"]}', "kind": r["kind"], "occurredAt": iso_datetime(r["occurred_at"]) if r["occurred_at"] else None, "actor": r["actor"], "action": r["action"], "projectId": project_id, "details": r["details"]} for r in results], "total": total, "limit": limit, "offset": offset}
