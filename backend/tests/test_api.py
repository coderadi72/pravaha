"""FastAPI regression scenarios exercised against isolated PostgreSQL schemas."""
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import json
from uuid import uuid4

import pytest
from sqlalchemy import func, select, text

from backend.app.core.security import digest_token, hash_password
from backend.app.db import repository
from backend.app.db.repository import load_workflow_data, save_workflow_data
from backend.app.models import ActivityMatch, AuditEvent, FieldUpdate, Organization, Project, ProjectManagerAssignment, Review, ReviewHistory, ScheduleActivity, ScheduleActivityContribution, SessionToken, Team, TeamLeaderAssignment, User

ORG = "ORG-OIL-DEMO"


def request(client, path, cookie=None, method="GET", body=None, headers=None, **kwargs):
    client.cookies.clear()
    headers = {**(headers or {}), **({"Cookie": cookie} if cookie else {})}
    result = client.request(method, path, headers=headers, **({"json": body} if body is not None else {}), **kwargs)
    client.cookies.clear()
    return result


def login(client, email, password):
    result = request(client, "/api/auth/login", method="POST", body={"email": email, "password": password})
    assert result.status_code == 200, result.text
    return result.headers["set-cookie"].split(";", 1)[0]


def workspace(session_factory):
    with session_factory() as session:
        return load_workflow_data(session, ORG)


def submit(client, identities, description="Spool erected for Line 247-XX", **context):
    response = request(client, "/api/team-leader/field-updates", identities["tl"], "POST", {"description": description, **context})
    assert response.status_code == 201, response.text
    return response.json()["fieldUpdate"]["id"]


def test_health_postgresql_connection_openapi_and_secret_free_contracts(client, settings):
    response = request(client, "/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pravaha-api"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert request(client, "/docs").status_code == 200
    openapi = request(client, "/openapi.json")
    assert openapi.status_code == 200
    document = openapi.json()
    assert "/api/workspace" in document["paths"]
    assert "/api/team-leader/field-updates" in document["paths"]
    assert document["components"]["schemas"]["FieldUpdateRequest"]["properties"]["description"]
    assert settings.database_url not in openapi.text
    assert "password_hash" not in openapi.text
    assert "SEED_ADMIN_PASSWORD" not in openapi.text


def test_auth_generic_errors_hashed_sessions_expiry_and_logout(client, identities, session_factory):
    me = request(client, "/api/auth/me", identities["pm"])
    assert me.status_code == 200
    assert me.json()["user"]["role"] == "PROJECT_MANAGER"
    assert set(me.json()["user"]) == {"id", "email", "name", "role", "organizationId"}
    unknown = request(client, "/api/auth/login", method="POST", body={"email": "unknown@pravaha.local", "password": "WrongPass123!"})
    known = request(client, "/api/auth/login", method="POST", body={"email": "tl001@pravaha.local", "password": "WrongPass123!"})
    assert unknown.status_code == known.status_code == 401
    assert unknown.json() == known.json() == {"error": {"code": "INVALID_CREDENTIALS", "message": "Email or password is incorrect."}}
    assert request(client, "/api/auth/me", "pravaha_session=invalid").status_code == 401
    token = identities["tl"].split("=", 1)[1]
    with session_factory() as session, session.begin():
        stored = session.get(SessionToken, digest_token(token))
        assert stored is not None and stored.token_hash != token
        assert timedelta(hours=7, minutes=59) < stored.expires_at - datetime.now(UTC) <= timedelta(hours=8)
        stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    assert request(client, "/api/auth/me", identities["tl"]).status_code == 401
    logout = request(client, "/api/auth/logout", identities["pm"], "POST", {})
    assert logout.status_code == 200
    assert "Max-Age=0" in logout.headers["set-cookie"]
    assert request(client, "/api/auth/me", identities["pm"]).status_code == 401
    with session_factory() as session:
        assert session.get(SessionToken, digest_token(identities["pm"].split("=", 1)[1])) is None
        assert session.scalar(select(AuditEvent).where(AuditEvent.action == "Signed out")).actor_user_id == "PM-001"


def test_startup_cleanup_expired_sessions_leaves_active_sessions(app, session_factory):
    from fastapi.testclient import TestClient
    with session_factory() as session, session.begin():
        session.add_all([
            SessionToken(token_hash="expired", user_id="ADMIN-001", created_at=datetime.now(UTC), expires_at=datetime.now(UTC) - timedelta(days=1)),
            SessionToken(token_hash="active", user_id="ADMIN-001", created_at=datetime.now(UTC), expires_at=datetime.now(UTC) + timedelta(days=1)),
        ])
    with TestClient(app):
        with session_factory() as session:
            assert session.get(SessionToken, "expired") is None
            assert session.get(SessionToken, "active") is not None


def test_roles_project_team_baseline_ownership_enforced_server_side(client, identities):
    assert request(client, "/api/admin/organization").status_code == 401
    for kind in ("pm", "tl"):
        assert request(client, "/api/admin/organization", identities[kind]).status_code == 403
    assert request(client, "/api/admin/organization", identities["admin"]).status_code == 200
    assert request(client, "/api/projects/PRJ-002", identities["pm"]).status_code == 403
    assert request(client, "/api/projects/PRJ-001", identities["pm"]).status_code == 200
    assert request(client, "/api/team-leader/activities", identities["tl"]).status_code == 200
    assert request(client, "/api/team-leader/activities/SA-1031/actions", identities["tl"], "POST", {"action": "start"}).status_code == 403
    assert request(client, "/api/reviews/FU-1043/confirm", identities["tl"], "POST", {"scheduleActivityId": "SA-1031"}).status_code == 403
    assert request(client, "/api/projects/PRJ-001/schedule/SA-1024/baseline", identities["tl"], "PATCH", {}).status_code == 403
    assert request(client, "/api/projects/PRJ-001/schedule/SA-1024/baseline", identities["admin"], "PATCH", {}).status_code == 501
    for view in ("schedule", "field-updates", "reviews"):
        assert request(client, f"/api/projects/PRJ-001/{view}", identities["pm"]).status_code == 200
    assert request(client, "/api/team-leader/me", identities["tl"]).json()["team"]["id"] == "TEAM-PIP-A"


def test_admin_assignments_provisioning_and_disabled_accounts(client, identities, session_factory):
    rejected = request(client, "/api/admin/projects/PRJ-002/manager", identities["admin"], "PATCH", {"projectManagerId": "PM-002"})
    assert rejected.status_code == 400
    assert request(client, "/api/admin/projects/PRJ-002/manager", identities["admin"], "PATCH", {"projectManagerId": "PM-001"}).status_code == 200
    assert request(client, "/api/projects/PRJ-002", identities["pm"]).status_code == 200
    assert request(client, "/api/admin/teams/TEAM-CIV-A/leader", identities["admin"], "PATCH", {"teamLeaderId": "TL-001"}).status_code == 200
    assert [item["id"] for item in request(client, "/api/workspace", identities["tl"]).json()["data"]["teams"]] == ["TEAM-CIV-A"]
    assert request(client, "/api/admin/teams/TEAM-HSE-A/assignment", identities["admin"], "PATCH", {"projectId": "PRJ-004", "assigned": True}).status_code == 200
    assert request(client, "/api/admin/teams/TEAM-HSE-A/assignment", identities["admin"], "PATCH", {"assigned": False}).status_code == 200
    assert next(item for item in workspace(session_factory)["teams"] if item["id"] == "TEAM-HSE-A")["projectId"] is None
    result = request(client, "/api/admin/users", identities["admin"], "POST", {"name": "Additional PM", "email": "additional@pravaha.local", "role": "PROJECT_MANAGER", "password": "NewManager123!"})
    assert result.status_code == 201, result.text
    identifier = result.json()["user"]["id"]
    assert request(client, "/api/admin/projects/PRJ-002/manager", identities["admin"], "PATCH", {"projectManagerId": identifier}).status_code == 200
    cookie = login(client, "additional@pravaha.local", "NewManager123!")
    assert request(client, "/api/projects/PRJ-002", cookie).status_code == 200
    assert request(client, "/api/projects/PRJ-002", identities["pm"]).status_code == 403
    assert request(client, "/api/admin/users", identities["admin"], "POST", {"name": "Weak", "email": "weak@pravaha.local", "role": "TEAM_LEADER", "password": "weak"}).status_code == 400
    assert request(client, "/api/admin/users", identities["admin"], "POST", {"name": "No field worker", "email": "worker@pravaha.local", "role": "FIELD_WORKER", "password": "WorkerPass123!"}).status_code == 400
    assert request(client, "/api/admin/users", identities["admin"], "POST", {"name": "Duplicate", "email": "ADDITIONAL@pravaha.local", "role": "TEAM_LEADER", "password": "LeaderPass123!"}).status_code == 409
    with session_factory() as session:
        assert session.scalar(select(AuditEvent).where(AuditEvent.action == "Assigned Team Leader")).actor_user_id == "ADMIN-001"


def test_intelligence_generated_server_side_persisted_and_scoped(client, identities, session_factory):
    identifier = submit(client, identities, "Spool erected for Line 247-XX in Unit 4 / Rack B, 70% progress", confidence=1, matcherVersion="forged", candidates=[{"scheduleActivityId": "outside", "score": 100}], submitterUserId="ADMIN-001")
    data = workspace(session_factory)
    match = next(item for item in data["activityMatches"] if item["fieldUpdateId"] == identifier)
    update = next(item for item in data["fieldUpdates"] if item["id"] == identifier)
    assert match["matcherVersion"] == "matcher-v1"
    assert match["confidence"] == 100
    assert match["recommendedMatchId"] == "SA-1024"
    assert match["matchStatus"] == "review_required"
    assert not match.get("matchedByUserId")
    assert update["submitterUserId"] == "TL-001"
    assert update["extractedActivity"]["identifiers"] == ["Line 247-XX"]
    assert update["extractedActivity"]["location"] == "Unit 4 / Rack B"
    assert update["progress"] == 70
    assert match["candidates"][0]["evidence"]
    assert match["matchReason"] and match["unmatchReason"]
    assert not any(item["fieldUpdateId"] == identifier for item in data["scheduleActivityContributions"])
    with session_factory() as session:
        automatic = session.scalar(select(AuditEvent).where(AuditEvent.entity_id == identifier, AuditEvent.action == "Activity match recommendation generated"))
        assert automatic.actor_user_id is None
        assert automatic.details_json["candidates"] == match["candidates"]
        assert session.scalar(select(AuditEvent).where(AuditEvent.entity_id == identifier, AuditEvent.action == "Submitted field update")).actor_user_id == "TL-001"
    edited = request(client, f"/api/team-leader/field-updates/{identifier}", identities["tl"], "PATCH", {"description": "Cable tray installation completed in Block 3"})
    assert edited.status_code == 200, edited.text
    visible = edited.json()
    assert "SA-1031" not in json.dumps(visible["fieldUpdate"])
    tl_data = visible["data"]
    allowed = {item["id"] for item in tl_data["scheduleActivities"]}
    assert set(tl_data["scheduleActivityBaselines"]).issubset(allowed)
    assert all(candidate["scheduleActivityId"] in allowed for match in tl_data["activityMatches"] for candidate in match.get("candidates", []))
    restricted = next(item for item in tl_data["activityMatches"] if item["fieldUpdateId"] == identifier)
    assert restricted["recommendationRestricted"] is True
    pm = request(client, "/api/workspace", identities["pm"]).json()["data"]
    suggested = next(item for item in pm["activityMatches"] if item["fieldUpdateId"] == identifier)
    assert suggested["recommendedMatchId"] == "SA-1031"
    assert any(item["signal"] == "location" and item["outcome"] == "support" for item in suggested["evidence"])
    generated_at = suggested["generatedAt"]
    assert request(client, f"/api/reviews/{identifier}/confirm", identities["pm"], "POST", {"scheduleActivityId": "SA-1031", "feedback": "Phase 7 confirmed"}).status_code == 200
    after = workspace(session_factory)
    assert next(item for item in after["activityMatches"] if item["fieldUpdateId"] == identifier)["generatedAt"] == generated_at


def test_confirm_change_unmatch_reconfirm_reconciliation_history_and_tl_feedback(client, identities, session_factory):
    before = workspace(session_factory)
    baselines = deepcopy(before["scheduleActivityBaselines"])
    unrelated = deepcopy(before["scheduleActivityContributions"])
    identifier = submit(client, identities, progress=65)
    for decision, activity_id, feedback in (
        ("confirm", "SA-1024", "Spool confirmed"),
        ("change-match", "SA-1031", "Corrected by PM"),
        ("unmatch", None, "Awaiting correct schedule item"),
        ("confirm", "SA-1024", "Reconfirmed by PM"),
    ):
        result = request(client, f"/api/reviews/{identifier}/{decision}", identities["pm"], "POST", {"scheduleActivityId": activity_id, "feedback": feedback, "reason": "Verified field observation"})
        assert result.status_code == 200, result.text
        data = workspace(session_factory)
        own = [item for item in data["scheduleActivityContributions"] if item["fieldUpdateId"] == identifier]
        assert len(own) == (0 if decision == "unmatch" else 1)
        if own:
            assert own[0]["scheduleActivityId"] == activity_id
        for item in unrelated:
            assert item in data["scheduleActivityContributions"]
        update = next(item for item in data["fieldUpdates"] if item["id"] == identifier)
        assert update["pmFeedback"] == feedback
        assert update["reviewerUserId"] == "PM-001"
        if decision in {"change-match", "unmatch"}:
            for schedule_id in ("SA-1024", "SA-1031"):
                if schedule_id != activity_id:
                    schedule = next(item for item in data["scheduleActivities"] if item["id"] == schedule_id)
                    remaining = [item for item in data["scheduleActivityContributions"] if item["scheduleActivityId"] == schedule_id]
                    if not remaining:
                        assert schedule["progress"] == baselines[schedule_id]["progress"]
    tl = request(client, "/api/team-leader/field-updates", identities["tl"]).json()["fieldUpdates"]
    assert next(item for item in tl if item["id"] == identifier)["pmFeedback"] == "Reconfirmed by PM"
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(ReviewHistory).where(ReviewHistory.field_update_id == identifier)) >= 5
        assert session.scalar(select(Review).where(Review.field_update_id == identifier)).reviewer_user_id == "PM-001"
    audits = request(client, "/api/admin/organization", identities["admin"]).json()["activity"]
    assert any(item["actorUserId"] == "PM-001" and item["action"] == "Review decision: confirm" for item in audits)


def test_edit_rematches_resets_review_removes_old_contribution_and_recalculates(client, identities, session_factory):
    before = workspace(session_factory)
    identifier = submit(client, identities, progress=65)
    with session_factory() as session, session.begin():
        data = load_workflow_data(session, ORG)
        data["scheduleActivityContributions"].append({"fieldUpdateId": identifier, "scheduleActivityId": "SA-1024", "recordedAt": datetime.now(UTC).isoformat(), "state": {"progress": 65, "status": "In Progress", "actualStart": "2026-10-04", "actualEnd": None}})
        schedule = next(item for item in data["scheduleActivities"] if item["id"] == "SA-1024")
        schedule.update(progress=65, status="In Progress", actualStart="2026-10-04")
        save_workflow_data(session, data)
    response = request(client, f"/api/team-leader/field-updates/{identifier}", identities["tl"], "PATCH", {"description": "Cable tray installation completed in Block 3", "progress": 100})
    assert response.status_code == 200, response.text
    data = workspace(session_factory)
    update = next(item for item in data["fieldUpdates"] if item["id"] == identifier)
    match = next(item for item in data["activityMatches"] if item["fieldUpdateId"] == identifier)
    assert update["extractedActivity"]["discipline"] == "Electrical"
    assert update["extractedActivity"]["location"] == "Block 3"
    assert match["confidence"] == 100
    assert match["recommendedMatchId"] == "SA-1031"
    assert match["scheduleActivityId"] == "SA-1031"
    assert match["matchStatus"] == "review_required"
    assert not any(item["fieldUpdateId"] == identifier for item in data["scheduleActivityContributions"])
    schedule = next(item for item in data["scheduleActivities"] if item["id"] == "SA-1024")
    assert schedule["progress"] == next(item for item in before["scheduleActivities"] if item["id"] == "SA-1024")["progress"]
    assert all(item in data["scheduleActivityContributions"] for item in before["scheduleActivityContributions"])
    assert update["reviewHistory"][-1]["actorUserId"] == "TL-001"


def test_same_name_leader_cannot_edit_another_authenticated_users_update(client, identities):
    identifier = submit(client, identities)
    response = request(client, "/api/admin/users", identities["admin"], "POST", {"name": "Ravi Singh", "email": "same-name@pravaha.local", "role": "TEAM_LEADER", "password": "OtherLeader123!"})
    assert response.status_code == 201
    other_id = response.json()["user"]["id"]
    assert request(client, "/api/admin/teams/TEAM-PIP-A/leader", identities["admin"], "PATCH", {"teamLeaderId": other_id}).status_code == 200
    cookie = login(client, "same-name@pravaha.local", "OtherLeader123!")
    assert request(client, f"/api/team-leader/field-updates/{identifier}", cookie, "PATCH", {"description": "Spool erected for Line 247-XX"}).status_code == 403


def test_duplicate_manager_names_keep_authenticated_review_history_and_audit_ids(client, identities, session_factory):
    with session_factory() as session, session.begin():
        session.add(User(id="PM-SAME-NAME", organization_id=ORG, email="same-name-pm@pravaha.local", full_name="Priya Mehta", role="PROJECT_MANAGER", password_hash=hash_password("DuplicateManager123!"), active=True, created_at=datetime.now(UTC)))
    assert request(client, "/api/admin/projects/PRJ-001/manager", identities["admin"], "PATCH", {"projectManagerId": "PM-SAME-NAME"}).status_code == 200
    cookie = login(client, "same-name-pm@pravaha.local", "DuplicateManager123!")
    result = request(client, "/api/reviews/FU-1043/change-match", cookie, "POST", {"scheduleActivityId": "SA-1031"})
    assert result.status_code == 200, result.text
    with session_factory() as session:
        assert session.scalar(select(Review).where(Review.field_update_id == "FU-1043")).reviewer_user_id == "PM-SAME-NAME"
        assert session.scalar(select(AuditEvent).where(AuditEvent.entity_id == "FU-1043", AuditEvent.action == "Review decision: change-match")).actor_user_id == "PM-SAME-NAME"
    assert next(item for item in workspace(session_factory)["activityMatches"] if item["fieldUpdateId"] == "FU-1043")["matchedByUserId"] == "PM-SAME-NAME"


@pytest.mark.parametrize("scenario", ["submission", "review", "manager", "team", "leader", "activity", "edit"])
def test_workflow_and_audit_failures_roll_back_atomically(client, identities, session_factory, monkeypatch, scenario):
    if scenario == 'team':
        from backend.app.models import Team
        with session_factory.begin() as session:
            session.add(Team(id='TEAM-EMPTY', organization_id=ORG, project_id='PRJ-001', payload_json={'id':'TEAM-EMPTY','name':'Empty team','projectId':'PRJ-001','members':0,'active':0,'onLeave':0,'other':0}))
    identifier = submit(client, identities)
    before = workspace(session_factory)
    operations = {
        "submission": ("/api/team-leader/field-updates", "tl", "POST", {"description": "Spool erected for Line 247-XX", "progress": 20}),
        "review": (f"/api/reviews/{identifier}/confirm", "pm", "POST", {"scheduleActivityId": "SA-1024"}),
        "manager": ("/api/admin/projects/PRJ-002/manager", "admin", "PATCH", {"projectManagerId": "PM-001"}),
        "team": ("/api/admin/teams/TEAM-EMPTY/assignment", "admin", "PATCH", {"assigned": False}),
        "leader": ("/api/admin/teams/TEAM-PIP-A/leader", "admin", "PATCH", {"teamLeaderId": None}),
        "activity": ("/api/team-leader/activities/SA-1024/actions", "tl", "POST", {"action": "start"}),
        "edit": (f"/api/team-leader/field-updates/{identifier}", "tl", "PATCH", {"description": "Cable tray installation completed in Block 3"}),
    }
    def reject_audit(*args, **kwargs):
        raise RuntimeError("audit unavailable")
    monkeypatch.setattr(repository, "append_audit", reject_audit)
    path, kind, method, body = operations[scenario]
    result = request(client, path, identities[kind], method, body)
    assert result.status_code == 500, result.text
    assert result.json()["error"]["code"] == "INTERNAL_ERROR"
    assert workspace(session_factory) == before


def test_real_postgres_system_audit_failure_rolls_back_user_audit_and_workflow(client, identities, engine, session_factory):
    before = workspace(session_factory)
    with engine.begin() as connection:
        connection.execute(text("CREATE FUNCTION reject_recommendation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'recommendation audit unavailable'; END $$"))
        connection.execute(text("CREATE TRIGGER reject_recommendation BEFORE INSERT ON audit_events FOR EACH ROW WHEN (NEW.action = 'Activity match recommendation generated') EXECUTE FUNCTION reject_recommendation()"))
    result = request(client, "/api/team-leader/field-updates", identities["tl"], "POST", {"description": "Spool erected for Line 247-XX"})
    assert result.status_code == 500, result.text
    assert workspace(session_factory) == before


def test_validation_cross_project_match_body_limits_origins_and_throttling(client, identities, session_factory):
    assert request(client, "/api/team-leader/field-updates", identities["tl"], "POST", {"description": ""}).status_code == 400
    identifier = submit(client, identities)
    with session_factory() as session, session.begin():
        session.add(ScheduleActivity(id="SA-OTHER-PROJECT", project_id="PRJ-002", team_id="TEAM-CIV-B", baseline_json={}, payload_json={"id": "SA-OTHER-PROJECT", "projectId": "PRJ-002", "teamId": "TEAM-CIV-B", "activityName": "Other project activity", "level": "L6", "discipline": "Civil", "status": "Not Started", "progress": 0}))
    assert request(client, f"/api/reviews/{identifier}/change-match", identities["pm"], "POST", {"scheduleActivityId": "SA-OTHER-PROJECT"}).status_code == 400
    oversized = request(client, "/api/team-leader/field-updates", identities["tl"], "POST", content='{"description":"' + "x" * 1_100_000 + '"}', headers={"Content-Type": "application/json"})
    assert oversized.status_code == 413
    assert request(client, "/api/auth/login", method="POST", body={"email": "admin@pravaha.local", "password": "AdminPass123!"}, headers={"Origin": "https://evil.invalid"}).status_code == 403
    allowed = request(client, "/api/auth/login", method="POST", body={"email": "admin@pravaha.local", "password": "AdminPass123!"}, headers={"Origin": "http://localhost:5174"})
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5174"
    assert allowed.headers["access-control-allow-credentials"] == "true"
    assert request(client, "/api/team-leader/field-updates", identities["tl"], "POST", body={"description": "Valid", "progress": True}).status_code == 400
    invalid_json = request(client, "/api/auth/login", method="POST", content="{bad", headers={"Content-Type": "application/json"})
    assert invalid_json.json()["error"]["code"] == "INVALID_JSON"
    failures = [request(client, "/api/auth/login", method="POST", body={"email": "throttle@pravaha.local", "password": "WrongPass123!"}) for _ in range(6)]
    assert [item.status_code for item in failures] == [401] * 5 + [429]


def test_ambiguous_and_unknown_updates_explain_why_not_and_never_approve(client, identities, session_factory):
    ambiguous_id = submit(client, identities, "Cable tray installation completed")
    unknown_id = submit(client, identities, "Lunch delivered to the site office")
    matches = workspace(session_factory)["activityMatches"]
    ambiguous = next(item for item in matches if item["fieldUpdateId"] == ambiguous_id)
    unknown = next(item for item in matches if item["fieldUpdateId"] == unknown_id)
    assert ambiguous["recommendationStatus"] == "ambiguous"
    assert ambiguous["recommendedMatchId"] is None
    assert len(ambiguous["candidates"]) >= 2
    assert ambiguous["unmatchReason"]
    assert unknown["recommendationStatus"] == "unmatched"
    assert unknown["recommendedMatchId"] is None
    assert unknown["confidence"] < 60
    assert unknown["unmatchReason"]
    assert not ambiguous.get("matchedByUserId") and not unknown.get("matchedByUserId")


def test_request_information_request_review_and_activity_actions_preserve_behavior(client, identities, session_factory):
    identifier = submit(client, identities)
    result = request(client, f"/api/reviews/{identifier}/request-info", identities["pm"], "POST", {"feedback": "Please verify location"})
    assert result.status_code == 200, result.text
    assert next(item for item in workspace(session_factory)["fieldUpdates"] if item["id"] == identifier)["pmFeedback"] == "Please verify location"
    assert request(client, f"/api/reviews/{identifier}/request-review", identities["pm"], "POST", {}).status_code == 200
    for action, details in (("start", {}), ("update", {"progress": 43}), ("block", {"blockedReason": "Material unavailable"}), ("complete", {})):
        result = request(client, "/api/team-leader/activities/SA-1024/actions", identities["tl"], "POST", {"action": action, "details": details})
        assert result.status_code == 200, result.text
    assert next(item for item in workspace(session_factory)["scheduleActivities"] if item["id"] == "SA-1024")["progress"] == 100


def test_restart_new_app_preserves_workflow_sessions_and_feedback(client, identities, settings, engine, session_factory):
    from fastapi.testclient import TestClient
    from backend.app.main import create_app
    identifier = submit(client, identities, progress=66)
    assert request(client, f"/api/reviews/{identifier}/confirm", identities["pm"], "POST", {"scheduleActivityId": "SA-1024", "feedback": "Persistence verified"}).status_code == 200
    before = workspace(session_factory)
    with TestClient(create_app(settings, session_factory=session_factory, engine=engine), raise_server_exceptions=False) as reopened:
        assert request(reopened, "/api/auth/me", identities["pm"]).status_code == 200
        actual = request(reopened, "/api/workspace", identities["pm"])
        assert actual.status_code == 200, actual.text
        assert next(item for item in actual.json()["data"]["fieldUpdates"] if item["id"] == identifier)["pmFeedback"] == "Persistence verified"
        assert workspace(session_factory) == before


def test_admin_and_managers_cannot_cross_organization_by_guessed_ids(client, identities, session_factory):
    with session_factory() as session, session.begin():
        session.add(Organization(id="ORG-OTHER", name="Other organization", data_label="Test", payload_json={"id": "ORG-OTHER", "name": "Other organization", "dataLabel": "Test"}))
        session.flush()
        session.add_all([
            User(id="PM-OTHER", organization_id="ORG-OTHER", email="pm-other@pravaha.local", full_name="Other PM", role="PROJECT_MANAGER", password_hash=hash_password("OtherManager123!"), active=True, created_at=datetime.now(UTC)),
            User(id="ADMIN-OTHER", organization_id="ORG-OTHER", email="admin-other@pravaha.local", full_name="Other Admin", role="ADMIN", password_hash=hash_password("OtherAdmin123!"), active=True, created_at=datetime.now(UTC)),
            Project(id="PRJ-OTHER", organization_id="ORG-OTHER", name="Other project", status="Planning", payload_json={"id": "PRJ-OTHER", "name": "Other project", "status": "Planning"}),
        ])
        session.flush()
        session.add(Team(id="TEAM-OTHER", organization_id="ORG-OTHER", project_id="PRJ-OTHER", payload_json={"id": "TEAM-OTHER", "name": "Other team", "projectId": "PRJ-OTHER"}))
    assert request(client, "/api/admin/projects/PRJ-OTHER/manager", identities["admin"], "PATCH", {"projectManagerId": "PM-001"}).status_code == 404
    assert request(client, "/api/admin/teams/TEAM-OTHER/leader", identities["admin"], "PATCH", {"teamLeaderId": "TL-001"}).status_code == 404
    assert request(client, "/api/admin/projects/PRJ-001/manager", identities["admin"], "PATCH", {"projectManagerId": "PM-OTHER"}).status_code == 400
    other_admin = login(client, "admin-other@pravaha.local", "OtherAdmin123!")
    other = request(client, "/api/workspace", other_admin)
    assert other.status_code == 200, other.text
    data = other.json()["data"]
    assert {item["id"] for item in data["projects"]} == {"PRJ-OTHER"}
    assert {item["id"] for item in data["teams"]} == {"TEAM-OTHER"}
    assert not data["fieldUpdates"] and not data["scheduleActivities"]
    assert request(client, "/api/projects/PRJ-OTHER", identities["pm"]).status_code == 404
