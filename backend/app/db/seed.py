"""Explicit, transactional demo seeding; blank credentials never enable accounts."""
import json
import os
from copy import deepcopy
from pathlib import Path

from sqlalchemy import func, select

from backend.app.db.repository import parse_datetime, utc_now
from backend.app.models import (
    ActivityMatch, AuditEvent, FieldUpdate, Organization, Project,
    ProjectManagerAssignment, Review, ReviewHistory, ScheduleActivity,
    ScheduleActivityContribution, Team, TeamLeaderAssignment, User,
)

DEMO_FILE = Path(__file__).resolve().parents[3] / "database" / "seed" / "demo.json"


def seed_database(session, credentials=None, hash_password=None):
    from backend.app.core.security import hash_password as default_hash, is_valid_password
    if session.scalar(select(func.count()).select_from(Organization)):
        return {"seeded": False}
    values = credentials if credentials is not None else os.environ
    enabled = {}
    for kind, user_id in (("ADMIN", "ADMIN-001"), ("PM", "PM-001"), ("TL", "TL-001")):
        email = values.get(f"SEED_{kind}_EMAIL", "").strip().lower()
        password = values.get(f"SEED_{kind}_PASSWORD", "")
        if not email or "@" not in email or not is_valid_password(password):
            raise ValueError(f"SEED_{kind}_EMAIL and a policy-compliant SEED_{kind}_PASSWORD are required before demo seeding. Passwords must be 12–128 characters with uppercase, lowercase, number and special character.")
        enabled[user_id] = (email, password)
    if len({email for email, _ in enabled.values()}) != 3:
        raise ValueError("Seed email addresses must be distinct.")
    hasher = hash_password or default_hash
    # Validate/hash all configuration before the first database write.
    hashed = {user_id: (email, hasher(password)) for user_id, (email, password) in enabled.items()}
    data = json.loads(DEMO_FILE.read_text(encoding="utf-8"))
    organization = data["organization"]
    organization_id = organization["id"]
    session.add(Organization(id=organization_id, name=organization["name"], data_label=organization["dataLabel"], payload_json=organization))
    session.flush()
    people = [("ADMIN-001", "ADMIN", "Organization Administrator")]
    people += [(item["id"], "PROJECT_MANAGER", item["name"]) for item in data["projectManagers"]]
    people += [(item["id"], "TEAM_LEADER", item["name"]) for item in data["teamLeaders"]]
    for user_id, role, name in people:
        email, password_hash = hashed.get(user_id, (f"{user_id.lower()}@pravaha.local", None))
        session.add(User(id=user_id, organization_id=organization_id, email=email, full_name=name, role=role, password_hash=password_hash, active=user_id in hashed, created_at=utc_now()))
    for item in data["projects"]:
        payload = deepcopy(item)
        payload["projectManagerId"] = "PM-001" if item.get("projectManagerId") == "PM-001" else None
        session.add(Project(id=item["id"], organization_id=organization_id, name=item["name"], status=item["status"], payload_json=payload))
    session.flush()
    for manager in data["projectManagers"]:
        if manager["id"] == "PM-001":
            for project_id in manager.get("assignedProjectIds", []):
                session.add(ProjectManagerAssignment(project_id=project_id, user_id="PM-001", assigned_at=utc_now()))
    for item in data["teams"]:
        leader = "TL-001" if item.get("teamLeaderId") == "TL-001" else None
        payload = {**item, "teamLeaderId": leader}
        session.add(Team(id=item["id"], organization_id=organization_id, project_id=item.get("projectId"), payload_json=payload))
    session.flush()
    for item in data["teams"]:
        if item.get("teamLeaderId") == "TL-001":
            session.add(TeamLeaderAssignment(team_id=item["id"], user_id="TL-001", assigned_at=utc_now()))
    for item in data["scheduleActivities"]:
        session.add(ScheduleActivity(id=item["id"], project_id=item["projectId"], team_id=item.get("teamId"), baseline_json=data["scheduleActivityBaselines"].get(item["id"], item), payload_json=item))
    for item in data["fieldUpdates"]:
        session.add(FieldUpdate(id=item["id"], project_id=item["projectId"], team_id=item.get("teamId"), submitter_user_id=item.get("submitterUserId"), status=item.get("reviewStatus", "submitted"), payload_json=item))
    session.flush()
    for item in data["activityMatches"]:
        session.add(ActivityMatch(field_update_id=item["fieldUpdateId"], schedule_activity_id=item.get("scheduleActivityId"), match_status=item["matchStatus"], payload_json=item))
    for item in data["reviewItems"]:
        session.add(Review(id=item["id"], field_update_id=item["fieldUpdateId"], reviewer_user_id=item.get("reviewerUserId"), status=item["status"], payload_json=item))
    for item in data.get("scheduleActivityContributions", []):
        session.add(ScheduleActivityContribution(field_update_id=item["fieldUpdateId"], schedule_activity_id=item["scheduleActivityId"], recorded_at=parse_datetime(item["recordedAt"]), state_json=item["state"]))
    for update in data["fieldUpdates"]:
        for index, history in enumerate(update.get("reviewHistory", []), start=1):
            session.add(ReviewHistory(id=f"{update['id']}-H{index}", field_update_id=update["id"], actor_user_id=history.get("actorUserId"), actor_label=history["actor"], action=history["action"], occurred_at=parse_datetime(history["occurredAt"])))
    for event in data.get("organizationActivity", []):
        session.add(AuditEvent(id=event["id"], organization_id=organization_id, actor_user_id=event.get("actorUserId"), actor_label=event["actor"], action=event["action"], entity=event.get("type", "organization"), entity_id=event["id"], occurred_at=parse_datetime(event["occurredAt"]), details_json={}))
    session.flush()
    return {"seeded": True}
