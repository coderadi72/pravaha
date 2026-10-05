"""Real PostgreSQL regressions. SQLite appears only as a legacy import fixture."""
import json
import sqlite3
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import func, inspect, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import DBAPIError, IntegrityError

from backend.app.db.base import Base
from backend.app.db.repository import (
    append_audit, iso_datetime, load_workflow_data, lock_organization,
    persist_workflow_and_audit, utc_now,
)
from backend.app.db.seed import DEMO_FILE, seed_database
from backend.app.db.session import create_engine_and_factory
from backend.app.models import (
    AuditEvent, Organization, Project, ProjectManagerAssignment, SessionToken,
    TeamLeaderAssignment, User,
)
from scripts.migrate_sqlite import TABLES, import_sqlite


def _seed(factory, credentials):
    with factory.begin() as session:
        return seed_database(session, credentials)


def _legacy_fixture(path, credentials):
    """Build a disposable Phase 7 SQLite file with the prior table contract."""
    from backend.app.core.security import digest_token, hash_password
    data = json.loads(DEMO_FILE.read_text(encoding="utf-8"))
    now = iso_datetime(utc_now())
    organization = data["organization"]
    organization_id = organization["id"]
    rows = {name: [] for name, _ in TABLES}
    rows["organizations"] = [{"id": organization_id, "name": organization["name"], "data_label": organization["dataLabel"], "payload_json": organization}]
    people = [("ADMIN-001", "ADMIN", "Organization Administrator")]
    people += [(item["id"], "PROJECT_MANAGER", item["name"]) for item in data["projectManagers"]]
    people += [(item["id"], "TEAM_LEADER", item["name"]) for item in data["teamLeaders"]]
    kinds = {"ADMIN-001": "ADMIN", "PM-001": "PM", "TL-001": "TL"}
    for user_id, role, name in people:
        kind = kinds.get(user_id)
        rows["users"].append({"id": user_id, "organization_id": organization_id, "email": credentials[f"SEED_{kind}_EMAIL"] if kind else f"{user_id.lower()}@pravaha.local", "full_name": name, "role": role, "password_hash": hash_password(credentials[f"SEED_{kind}_PASSWORD"]) if kind else None, "active": int(bool(kind)), "created_at": now})
    rows["projects"] = [{"id": item["id"], "organization_id": organization_id, "name": item["name"], "status": item["status"], "payload_json": item} for item in data["projects"]]
    rows["project_manager_assignments"] = [{"project_id": project_id, "user_id": "PM-001", "assigned_at": now} for person in data["projectManagers"] if person["id"] == "PM-001" for project_id in person["assignedProjectIds"]]
    rows["teams"] = [{"id": item["id"], "project_id": item.get("projectId"), "team_leader_id": "TL-001" if item.get("teamLeaderId") == "TL-001" else None, "payload_json": item} for item in data["teams"]]
    rows["schedule_activities"] = [{"id": item["id"], "project_id": item["projectId"], "team_id": item.get("teamId"), "baseline_json": data["scheduleActivityBaselines"][item["id"]], "payload_json": item} for item in data["scheduleActivities"]]
    rows["field_updates"] = [{"id": item["id"], "project_id": item["projectId"], "team_id": item.get("teamId"), "submitter_user_id": item.get("submitterUserId"), "status": item.get("reviewStatus", "submitted"), "payload_json": item} for item in data["fieldUpdates"]]
    rows["activity_matches"] = [{"field_update_id": item["fieldUpdateId"], "schedule_activity_id": item.get("scheduleActivityId"), "match_status": item["matchStatus"], "payload_json": item} for item in data["activityMatches"]]
    rows["reviews"] = [{"id": item["id"], "field_update_id": item["fieldUpdateId"], "reviewer_user_id": item.get("reviewerUserId"), "status": item["status"], "payload_json": item} for item in data["reviewItems"]]
    rows["review_history"] = [{"id": f"{update['id']}-H{index}", "field_update_id": update["id"], "actor_user_id": item.get("actorUserId"), "actor_label": item["actor"], "action": item["action"], "occurred_at": item["occurredAt"]} for update in data["fieldUpdates"] for index, item in enumerate(update.get("reviewHistory", []), start=1)]
    rows["schedule_activity_contributions"] = [{"field_update_id": item["fieldUpdateId"], "schedule_activity_id": item["scheduleActivityId"], "recorded_at": item["recordedAt"], "state_json": item["state"]} for item in data.get("scheduleActivityContributions", [])]
    rows["audit_events"] = [{"id": item["id"], "organization_id": organization_id, "actor_user_id": item.get("actorUserId"), "actor_label": item["actor"], "action": item["action"], "entity": item.get("type", "organization"), "entity_id": item["id"], "occurred_at": item["occurredAt"], "details_json": {}} for item in data.get("organizationActivity", [])]
    rows["sessions"] = [{"token_hash": digest_token("legacy-test-token"), "user_id": "TL-001", "created_at": now, "expires_at": iso_datetime(utc_now() + timedelta(hours=1))}]
    rows["schema_migrations"] = [{"version": version, "applied_at": now} for version in range(1, 6)]
    with sqlite3.connect(path) as connection:
        for name, model in TABLES:
            columns = [(column.name, "INTEGER" if column.name in {"active", "version"} else "TEXT") for column in model.__table__.columns if column.name not in {"sequence", "login_id"} and (name != "teams" or column.name != "organization_id")]
            if name == "teams":
                columns.insert(2, ("team_leader_id", "TEXT"))
            names = [name for name, _ in columns]
            connection.execute(f'CREATE TABLE "{name}" ({",".join(chr(34) + column + chr(34) + " " + kind for column, kind in columns)})')
            for row in rows[name]:
                values = [json.dumps(row[column]) if column.endswith("_json") else row[column] for column in names]
                connection.execute(f'INSERT INTO "{name}" ({",".join(names)}) VALUES ({",".join("?" for _ in names)})', values)
    return rows


def test_postgresql_schema_and_alembic_history(engine, settings):
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT 1")) == 1
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0005_registration_requests"
    inspector = inspect(engine)
    assert set(Base.metadata.tables).issubset(inspector.get_table_names(schema=settings.db_schema))
    assert inspector.get_foreign_keys("field_updates", schema=settings.db_schema)
    assert inspector.get_foreign_keys("team_leader_assignments", schema=settings.db_schema)
    assert any(index["name"] == "idx_audit_org_time" for index in inspector.get_indexes("audit_events", schema=settings.db_schema))
    assert all(isinstance(column.type, JSONB) for table in Base.metadata.tables.values() for column in table.columns if column.name.endswith("_json"))
    assert "team_leader_id" not in Base.metadata.tables["teams"].columns
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0005_registration_requests"


def test_database_runtime_rejects_sqlite():
    with pytest.raises(ValueError, match="PostgreSQL"):
        create_engine_and_factory(SimpleNamespace(database_url="sqlite:///:memory:", db_schema=None, sql_echo=False))


def test_seed_configuration_fails_before_writes_and_seed_is_idempotent(session_factory, credentials):
    with pytest.raises(ValueError, match="required before demo seeding"):
        with session_factory.begin() as session:
            seed_database(session, {})
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Organization)) == 0
        assert session.scalar(select(func.count()).select_from(User)) == 0
    assert _seed(session_factory, credentials) == {"seeded": True}
    assert _seed(session_factory, {}) == {"seeded": False}
    with session_factory() as session:
        data = load_workflow_data(session, "ORG-OIL-DEMO")
        assert data["projectManagers"][0]["assignedProjectIds"] == ["PRJ-001"]
        assert all(not item["assignedProjectIds"] for item in data["projectManagers"] if not item["loginEnabled"])
        assert all(item["teamId"] is None for item in data["teamLeaders"] if not item["loginEnabled"])
        assert session.scalar(select(func.count()).select_from(TeamLeaderAssignment)) == 1


def test_foreign_keys_case_insensitive_email_and_assignment_constraints(session_factory, credentials):
    _seed(session_factory, credentials)
    with session_factory.begin() as session:
        with pytest.raises(IntegrityError), session.begin_nested():
            session.add(User(id="BAD-FK", organization_id="MISSING", email="bad-fk@example.test", full_name="Bad", role="PROJECT_MANAGER", active=False, created_at=utc_now()))
            session.flush()
        admin = session.get(User, "ADMIN-001")
        with pytest.raises(IntegrityError), session.begin_nested():
            session.add(User(id="BAD-EMAIL", organization_id=admin.organization_id, email=admin.email.upper(), full_name="Bad", role="PROJECT_MANAGER", active=False, created_at=utc_now()))
            session.flush()
        with pytest.raises(IntegrityError), session.begin_nested():
            session.add(ProjectManagerAssignment(project_id="PRJ-001", user_id="PM-002", assigned_at=utc_now()))
            session.flush()
        with pytest.raises(IntegrityError), session.begin_nested():
            session.add(TeamLeaderAssignment(team_id="TEAM-CIV-A", user_id="TL-001", assigned_at=utc_now()))
            session.flush()
        token = SessionToken(token_hash="test-delete", user_id="TL-001", created_at=utc_now(), expires_at=utc_now() + timedelta(hours=1))
        session.add(token)
        session.flush()
        token.expires_at = utc_now()
        session.flush()
        session.delete(token)
        session.flush()
        assert session.get(SessionToken, "test-delete") is None


def test_organization_lock_serializes_snapshot_mutations(session_factory, credentials):
    _seed(session_factory, credentials)
    with session_factory.begin() as first:
        lock_organization(first, "ORG-OIL-DEMO")
        with pytest.raises(DBAPIError):
            with session_factory.begin() as second:
                second.execute(text("SET LOCAL lock_timeout = '100ms'"))
                lock_organization(second, "ORG-OIL-DEMO")


def test_workflow_and_human_system_audits_rollback_together(session_factory, credentials):
    _seed(session_factory, credentials)
    with session_factory.begin() as session:
        before = load_workflow_data(session, "ORG-OIL-DEMO")
        before_audits = session.scalar(select(func.count()).select_from(AuditEvent))
        session.execute(text("CREATE FUNCTION reject_recommendation_audit() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action='Activity match recommendation generated' THEN RAISE EXCEPTION 'recommendation audit unavailable'; END IF; RETURN NEW; END $$"))
        session.execute(text("CREATE TRIGGER reject_recommendation_audit BEFORE INSERT ON audit_events FOR EACH ROW EXECUTE FUNCTION reject_recommendation_audit()"))
    actor = {"id": "TL-001", "organizationId": "ORG-OIL-DEMO", "fullName": "Ravi Singh", "role": "TEAM_LEADER"}
    with pytest.raises(DBAPIError, match="recommendation audit unavailable"):
        with session_factory.begin() as session:
            lock_organization(session, actor["organizationId"])
            data = load_workflow_data(session, actor["organizationId"])
            data["projects"][0]["name"] = "Rollback this name"
            persist_workflow_and_audit(session, data, actor, "User write before failed system audit", "field_update", data["fieldUpdates"][0]["id"], {}, data["fieldUpdates"][0]["id"])
    with session_factory() as session:
        assert load_workflow_data(session, actor["organizationId"])["projects"] == before["projects"]
        assert session.scalar(select(func.count()).select_from(AuditEvent)) == before_audits


def test_sqlite_import_preserves_every_table_and_refuses_populated_target(session_factory, credentials, tmp_path):
    source = tmp_path / "legacy.sqlite"
    rows = _legacy_fixture(source, credentials)
    source_bytes = source.read_bytes()
    with session_factory.begin() as session:
        report = import_sqlite(source, session, tmp_path / "backups")
    assert source.read_bytes() == source_bytes
    assert Path(report["backupPath"]).exists()
    assert all(row["difference"] == 0 for row in report["tables"].values())
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(User)) == len(rows["users"])
        assert session.get(User, "TL-001").password_hash == next(item["password_hash"] for item in rows["users"] if item["id"] == "TL-001")
        data = load_workflow_data(session, "ORG-OIL-DEMO")
        assert len(data["fieldUpdates"]) == len(rows["field_updates"])
        assert len(data["scheduleActivityContributions"]) == len(rows["schedule_activity_contributions"])
    with pytest.raises(ValueError, match="not empty"):
        with session_factory.begin() as session:
            import_sqlite(source, session, tmp_path / "backups")


def test_failed_import_rolls_back_all_tables(session_factory, credentials, tmp_path):
    source = tmp_path / "invalid.sqlite"
    _legacy_fixture(source, credentials)
    with sqlite3.connect(source) as connection:
        connection.execute("UPDATE schedule_activities SET project_id='MISSING' WHERE id='SA-1024'")
    with pytest.raises(IntegrityError):
        with session_factory.begin() as session:
            import_sqlite(source, session, tmp_path / "backups")
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Organization)) == 0
        assert session.scalar(select(func.count()).select_from(User)) == 0
        assert session.scalar(select(func.count()).select_from(Project)) == 0


def test_audit_append_has_authenticated_id_and_survives_reopen(session_factory, credentials):
    _seed(session_factory, credentials)
    actor = {"id": "PM-001", "organizationId": "ORG-OIL-DEMO", "fullName": "Priya Mehta", "role": "PROJECT_MANAGER"}
    with session_factory.begin() as session:
        event_id = append_audit(session, actor, "Persistence proof", "test", "proof", {"result": True})
    with session_factory() as session:
        event = session.get(AuditEvent, event_id)
        assert event.actor_user_id == "PM-001"
        assert event.details_json == {"result": True}


def test_history_keeps_system_and_human_order_at_identical_timestamps(session_factory, credentials):
    from backend.app.services.workflow_service import rematch_field_update, submit_field_update
    _seed(session_factory, credentials)
    actor = {"id": "TL-001", "organizationId": "ORG-OIL-DEMO", "fullName": "Ravi Singh", "role": "TEAM_LEADER"}
    timestamp = "2026-10-04T00:00:00.000Z"
    with session_factory.begin() as session:
        lock_organization(session, actor["organizationId"])
        data = load_workflow_data(session, actor["organizationId"])
        data = submit_field_update(data, {"description": "Spool erected for Line 247-XX"}, {"teamId": "TEAM-PIP-A", "submittedBy": actor["fullName"], "submitterUserId": actor["id"], "id": "FU-history-order", "now": timestamp})
        persist_workflow_and_audit(session, data, actor, "Submitted field update", "field_update", "FU-history-order", {}, "FU-history-order")
    with session_factory.begin() as session:
        lock_organization(session, actor["organizationId"])
        data = load_workflow_data(session, actor["organizationId"])
        history = next(item for item in data["fieldUpdates"] if item["id"] == "FU-history-order")["reviewHistory"]
        assert [item["actorUserId"] for item in history] == ["TL-001", None]
        rematched = rematch_field_update(data, "FU-history-order", {"actor": actor["fullName"], "actorUserId": actor["id"], "now": timestamp})
        persist_workflow_and_audit(session, rematched["data"], actor, "Edited field update", "field_update", "FU-history-order", {}, "FU-history-order")
    with session_factory() as session:
        data = load_workflow_data(session, actor["organizationId"])
        history = next(item for item in data["fieldUpdates"] if item["id"] == "FU-history-order")["reviewHistory"]
        assert [item["actorUserId"] for item in history] == ["TL-001", None, None, "TL-001"]


def test_missing_configured_schema_never_falls_back_to_public(settings):
    isolated = settings.model_copy(update={"db_schema": "pravaha_missing_schema_guard"})
    engine, _ = create_engine_and_factory(isolated)
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT current_schema()")) is None
            assert connection.scalar(text("SHOW search_path")) == isolated.db_schema
            with pytest.raises(DBAPIError):
                connection.execute(text("SELECT count(*) FROM organizations"))
    finally:
        engine.dispose()
