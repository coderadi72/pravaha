"""Organization-scoped persistence for the existing camelCase workflow contract.

Mutations lock the organization before loading their snapshot. These functions
flush but never commit: workflow and audit share the request transaction.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import (
    ActivityMatch, AuditEvent, FieldUpdate, Organization, Project,
    ProjectManagerAssignment, Review, ReviewHistory, ScheduleActivity,
    ScheduleActivityContribution, Team, TeamLeaderAssignment, User,
)


def utc_now():
    return datetime.now(timezone.utc)


def parse_datetime(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def iso_datetime(value):
    return parse_datetime(value).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def lock_organization(session: Session, organization_id: str):
    organization = session.scalar(select(Organization).where(Organization.id == organization_id).with_for_update())
    if organization is None:
        raise ValueError("Organization not found.")
    return organization


def load_workflow_data(session: Session, organization_id: str):
    organization = session.get(Organization, organization_id)
    if organization is None:
        return None
    users = list(session.scalars(select(User).where(User.organization_id == organization_id, User.role.in_(['ADMIN', 'PROJECT_MANAGER', 'TEAM_LEADER'])).order_by(User.id)))
    projects = list(session.scalars(select(Project).where(Project.organization_id == organization_id).order_by(Project.id)))
    project_ids = [project.id for project in projects]
    teams = list(session.scalars(select(Team).where(Team.organization_id == organization_id).order_by(Team.id)))
    team_ids = [team.id for team in teams]
    managers = list(session.scalars(select(ProjectManagerAssignment).where(ProjectManagerAssignment.project_id.in_(project_ids))))
    leaders = list(session.scalars(select(TeamLeaderAssignment).where(TeamLeaderAssignment.team_id.in_(team_ids))))
    manager_by_project = {assignment.project_id: assignment.user_id for assignment in managers}
    leader_by_team = {assignment.team_id: assignment.user_id for assignment in leaders}
    team_by_leader = {assignment.user_id: next(team for team in teams if team.id == assignment.team_id) for assignment in leaders}
    schedules = list(session.scalars(select(ScheduleActivity).where(ScheduleActivity.project_id.in_(project_ids), ScheduleActivity.payload_json["archived"].astext.is_distinct_from("true")).order_by(ScheduleActivity.id)))
    updates = list(session.scalars(select(FieldUpdate).where(FieldUpdate.project_id.in_(project_ids))))
    updates.sort(key=lambda item: (item.payload_json.get("submittedAt", ""), item.id), reverse=True)
    update_ids = [item.id for item in updates]
    matches = list(session.scalars(select(ActivityMatch).where(ActivityMatch.field_update_id.in_(update_ids)).order_by(ActivityMatch.field_update_id)))
    reviews = list(session.scalars(select(Review).where(Review.field_update_id.in_(update_ids)).order_by(Review.id)))
    contributions = list(session.scalars(select(ScheduleActivityContribution).where(ScheduleActivityContribution.field_update_id.in_(update_ids)).order_by(ScheduleActivityContribution.recorded_at, ScheduleActivityContribution.field_update_id)))
    histories = list(session.scalars(select(ReviewHistory).where(ReviewHistory.field_update_id.in_(update_ids)).order_by(ReviewHistory.occurred_at, ReviewHistory.sequence, ReviewHistory.id)))
    events = list(session.scalars(select(AuditEvent).where(AuditEvent.organization_id == organization_id).order_by(AuditEvent.occurred_at.desc(), AuditEvent.id.desc()).limit(500)))
    project_payloads = [{**deepcopy(item.payload_json), "projectManagerId": manager_by_project.get(item.id), "teamIds": [team.id for team in teams if team.project_id == item.id]} for item in projects]
    team_payloads = [{**deepcopy(item.payload_json), "projectId": item.project_id, "teamLeaderId": leader_by_team.get(item.id)} for item in teams]
    field_payloads = []
    for item in updates:
        field_payloads.append({**deepcopy(item.payload_json), "projectId": item.project_id, "teamId": item.team_id, "submitterUserId": item.submitter_user_id, "reviewHistory": [{"actorUserId": history.actor_user_id, "actor": history.actor_label, "action": history.action, "occurredAt": iso_datetime(history.occurred_at)} for history in histories if history.field_update_id == item.id]})
    return {
        "organization": deepcopy(organization.payload_json),
        "users": [{"id": item.id, "email": item.email, "name": item.full_name, "role": item.role, "active": int(item.active), "loginEnabled": int(bool(item.active and item.password_hash))} for item in sorted(users, key=lambda item: (item.role, item.id))],
        "projectManagers": [{"id": item.id, "name": item.full_name, "email": item.email, "assignedProjectIds": sorted(assignment.project_id for assignment in managers if assignment.user_id == item.id), "loginEnabled": bool(item.active and item.password_hash), "status": ("Active" if any(assignment.user_id == item.id for assignment in managers) else "Available") if item.active and item.password_hash else "Sign-in disabled", "lastActivity": "Persistent account" if item.active and item.password_hash else "Provision credentials to enable sign-in"} for item in users if item.role == "PROJECT_MANAGER"],
        "teamLeaders": [{"id": item.id, "name": item.full_name, "teamId": team_by_leader[item.id].id if item.id in team_by_leader else None, "projectId": team_by_leader[item.id].project_id if item.id in team_by_leader else None, "loginEnabled": bool(item.active and item.password_hash), "status": ("Active" if item.id in team_by_leader else "Available") if item.active and item.password_hash else "Sign-in disabled"} for item in users if item.role == "TEAM_LEADER"],
        "projects": project_payloads, "teams": team_payloads,
        "scheduleActivities": [{**deepcopy(item.payload_json), "projectId": item.project_id, "teamId": item.team_id} for item in schedules],
        "scheduleActivityBaselines": {item.id: deepcopy(item.baseline_json) for item in schedules},
        "scheduleActivityContributions": [{"fieldUpdateId": item.field_update_id, "scheduleActivityId": item.schedule_activity_id, "recordedAt": iso_datetime(item.recorded_at), "state": deepcopy(item.state_json)} for item in contributions],
        "fieldUpdates": field_payloads,
        "activityMatches": [{**deepcopy(item.payload_json), "fieldUpdateId": item.field_update_id, "scheduleActivityId": item.schedule_activity_id, "matchStatus": item.match_status} for item in matches],
        "reviewItems": [{**deepcopy(item.payload_json), "reviewerUserId": item.reviewer_user_id} for item in reviews],
        "organizationActivity": [{"id": item.id, "actorUserId": item.actor_user_id, "actor": item.actor_label, "action": item.action, "type": item.entity, "occurredAt": iso_datetime(item.occurred_at)} for item in events],
    }


def _upsert(session, model, key, values):
    row = session.get(model, key)
    if row is None:
        row = model(**values)
        session.add(row)
    else:
        for field, value in values.items():
            setattr(row, field, value)
    return row


def _enabled_actor(session, user_id, role, organization_id):
    user = session.get(User, user_id)
    if not user or user.organization_id != organization_id or user.role != role or not user.active or not user.password_hash:
        raise ValueError("Assignment requires an enabled account in this organization.")


def save_workflow_data(session: Session, data):
    organization_id = data["organization"]["id"]
    project_ids = {item.id for item in session.scalars(select(Project).where(Project.organization_id == organization_id))}
    team_ids = {item.id for item in session.scalars(select(Team).where(Team.organization_id == organization_id))}
    if any(item["id"] not in project_ids for item in data["projects"]) or any(item["id"] not in team_ids for item in data["teams"]):
        raise ValueError("Workflow contains resources outside this organization.")
    for item in data["projects"]:
        _upsert(session, Project, item["id"], {"id": item["id"], "organization_id": organization_id, "name": item["name"], "status": item["status"], "payload_json": deepcopy(item)})
    manager_targets = {project_id: manager["id"] for manager in data["projectManagers"] for project_id in manager.get("assignedProjectIds", [])}
    if not set(manager_targets).issubset(project_ids):
        raise ValueError("Assignment project is outside this organization.")
    existing_managers = list(session.scalars(select(ProjectManagerAssignment).where(ProjectManagerAssignment.project_id.in_(project_ids))))
    for assignment in existing_managers:
        if manager_targets.get(assignment.project_id) != assignment.user_id:
            session.delete(assignment)
    session.flush()
    for project_id, user_id in manager_targets.items():
        _enabled_actor(session, user_id, "PROJECT_MANAGER", organization_id)
        if session.get(ProjectManagerAssignment, project_id) is None:
            session.add(ProjectManagerAssignment(project_id=project_id, user_id=user_id, assigned_at=utc_now()))
    leader_targets = {item["id"]: item["teamLeaderId"] for item in data["teams"] if item.get("teamLeaderId")}
    existing_leaders = list(session.scalars(select(TeamLeaderAssignment).where(TeamLeaderAssignment.team_id.in_(team_ids))))
    for assignment in existing_leaders:
        if leader_targets.get(assignment.team_id) != assignment.user_id:
            session.delete(assignment)
    session.flush()
    for item in data["teams"]:
        if item.get("projectId") is not None and item["projectId"] not in project_ids:
            raise ValueError("Team project is outside this organization.")
        _upsert(session, Team, item["id"], {"id": item["id"], "organization_id": organization_id, "project_id": item.get("projectId"), "payload_json": deepcopy(item)})
    for team_id, user_id in leader_targets.items():
        _enabled_actor(session, user_id, "TEAM_LEADER", organization_id)
        if session.get(TeamLeaderAssignment, team_id) is None:
            session.add(TeamLeaderAssignment(team_id=team_id, user_id=user_id, assigned_at=utc_now()))
    schedule_ids = {item.id for item in session.scalars(select(ScheduleActivity).where(ScheduleActivity.project_id.in_(project_ids)))}
    for item in data["scheduleActivities"]:
        if item["id"] not in schedule_ids or item["projectId"] not in project_ids or (item.get("teamId") and item["teamId"] not in team_ids):
            raise ValueError("Schedule activity is outside this organization.")
        row = session.get(ScheduleActivity, item["id"])
        row.project_id, row.team_id, row.payload_json = item["projectId"], item.get("teamId"), deepcopy(item)
    for item in data["fieldUpdates"]:
        if item["projectId"] not in project_ids or (item.get("teamId") and item["teamId"] not in team_ids):
            raise ValueError("Field update is outside this organization.")
        _upsert(session, FieldUpdate, item["id"], {"id": item["id"], "project_id": item["projectId"], "team_id": item.get("teamId"), "submitter_user_id": item.get("submitterUserId"), "status": item.get("reviewStatus", item.get("status", "submitted")), "payload_json": deepcopy(item)})
    session.flush()
    update_ids = {item["id"] for item in data["fieldUpdates"]}
    for item in data["activityMatches"]:
        if item["fieldUpdateId"] not in update_ids or (item.get("scheduleActivityId") and item["scheduleActivityId"] not in schedule_ids):
            raise ValueError("Match resources are outside this organization.")
        _upsert(session, ActivityMatch, item["fieldUpdateId"], {"field_update_id": item["fieldUpdateId"], "schedule_activity_id": item.get("scheduleActivityId"), "match_status": item["matchStatus"], "payload_json": deepcopy(item)})
    review_ids = {item["id"] for item in data["reviewItems"]}
    for row in session.scalars(select(Review).where(Review.field_update_id.in_(update_ids))):
        if row.id not in review_ids:
            session.delete(row)
    for item in data["reviewItems"]:
        if item["fieldUpdateId"] not in update_ids:
            raise ValueError("Review update is outside this organization.")
        _upsert(session, Review, item["id"], {"id": item["id"], "field_update_id": item["fieldUpdateId"], "reviewer_user_id": item.get("reviewerUserId"), "status": item["status"], "payload_json": deepcopy(item)})
    targets = {item["fieldUpdateId"]: item for item in data.get("scheduleActivityContributions", [])}
    for row in session.scalars(select(ScheduleActivityContribution).where(ScheduleActivityContribution.field_update_id.in_(update_ids))):
        if row.field_update_id not in targets:
            session.delete(row)
    for update_id, item in targets.items():
        if update_id not in update_ids or item["scheduleActivityId"] not in schedule_ids:
            raise ValueError("Contribution resources are outside this organization.")
        _upsert(session, ScheduleActivityContribution, update_id, {"field_update_id": update_id, "schedule_activity_id": item["scheduleActivityId"], "recorded_at": parse_datetime(item["recordedAt"]), "state_json": deepcopy(item["state"])})
    # Append-only history preserves imported IDs and historical duplicate events.
    for update in data["fieldUpdates"]:
        existing = list(session.scalars(select(ReviewHistory).where(ReviewHistory.field_update_id == update["id"])))
        counts = Counter((row.actor_user_id, row.actor_label, row.action, iso_datetime(row.occurred_at)) for row in existing)
        for history in update.get("reviewHistory", []):
            key = (history.get("actorUserId"), history["actor"], history["action"], iso_datetime(history["occurredAt"]))
            if counts[key]:
                counts[key] -= 1
            else:
                session.add(ReviewHistory(id=f"H-{uuid4()}", field_update_id=update["id"], actor_user_id=history.get("actorUserId"), actor_label=history["actor"], action=history["action"], occurred_at=parse_datetime(history["occurredAt"])))
    session.flush()


def append_audit(session, actor, action, entity, entity_id, details=None):
    event = AuditEvent(id=f"AUD-{uuid4()}", organization_id=actor["organizationId"], actor_user_id=actor.get("id"), actor_label=actor["fullName"], action=action, entity=entity, entity_id=entity_id, occurred_at=utc_now(), details_json=deepcopy(details or {}))
    session.add(event)
    session.flush()
    return event.id


def persist_workflow_and_audit(session, data, actor, action, entity, entity_id, details=None, intelligence_update_id=None):
    if data["organization"]["id"] != actor["organizationId"]:
        raise ValueError("Actor organization does not own this workflow.")
    save_workflow_data(session, data)
    append_audit(session, actor, action, entity, entity_id, details)
    if intelligence_update_id:
        match = next(item for item in data["activityMatches"] if item["fieldUpdateId"] == intelligence_update_id)
        update = next(item for item in data["fieldUpdates"] if item["id"] == intelligence_update_id)
        fields = ("matcherVersion", "generatedAt", "confidence", "confidenceLevel", "recommendedMatchId", "recommendationStatus", "candidates", "evidence", "matchReason", "unmatchReason")
        event = AuditEvent(id=f"AUD-{uuid4()}", organization_id=actor["organizationId"], actor_user_id=None, actor_label="PRAVAHA matcher", action="Activity match recommendation generated", entity="field_update", entity_id=intelligence_update_id, occurred_at=parse_datetime(match["generatedAt"]), details_json={"extractedActivity": deepcopy(update["extractedActivity"]), **{field: deepcopy(match.get(field)) for field in fields}})
        session.add(event)
        session.flush()

    # Phase 8 observes the existing workflow; it does not alter matching or actuals.
    if entity in {"field_update", "schedule_activity"}:
        from backend.app.core.config import Settings
        from backend.app.services.project_intelligence_service import reconcile
        collection = data["fieldUpdates"] if entity == "field_update" else data["scheduleActivities"]
        item = next((item for item in collection if item["id"] == entity_id), None)
        if item:
            reconcile(session, actor, item["projectId"], session.info.get("settings") or Settings())
