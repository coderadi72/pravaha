"""One-way legacy SQLite import. This module is never used by API runtime."""
import argparse
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from sqlalchemy import func, select

from backend.app.db.repository import parse_datetime, utc_now
from backend.app.models import (
    ActivityMatch, AuditEvent, FieldUpdate, LegacyMigration, Organization,
    Project, ProjectManagerAssignment, Review, ReviewHistory, ScheduleActivity,
    ScheduleActivityContribution, SessionToken, Team, TeamLeaderAssignment, User,
)

TABLES = (
    ("organizations", Organization), ("users", User), ("projects", Project),
    ("project_manager_assignments", ProjectManagerAssignment), ("teams", Team),
    ("schedule_activities", ScheduleActivity), ("field_updates", FieldUpdate),
    ("activity_matches", ActivityMatch), ("reviews", Review),
    ("review_history", ReviewHistory),
    ("schedule_activity_contributions", ScheduleActivityContribution),
    ("audit_events", AuditEvent), ("sessions", SessionToken),
    ("schema_migrations", LegacyMigration),
)


def backup_sqlite(source_path, backup_directory=None):
    source = Path(source_path).resolve(strict=True)
    if not source.is_file():
        raise ValueError("Legacy SQLite source must be an existing file.")
    directory = Path(backup_directory).resolve() if backup_directory else source.parent
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{source.stem}-pre-postgresql-{uuid4().hex}.sqlite"
    # SQLite's online backup API includes committed WAL pages. No source writes.
    with sqlite3.connect(f"{source.as_uri()}?mode=ro", uri=True) as original:
        with sqlite3.connect(destination) as backup:
            original.backup(backup)
    return destination


def _read_backup(path):
    with sqlite3.connect(f"{Path(path).as_uri()}?mode=ro", uri=True) as source:
        source.row_factory = sqlite3.Row
        if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Legacy SQLite integrity check failed.")
        if source.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Legacy SQLite has foreign-key violations; import refused.")
        existing = {row[0] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing = {table for table, _ in TABLES} - existing
        if missing:
            raise ValueError(f"Legacy SQLite is missing required tables: {', '.join(sorted(missing))}.")
        return {table: [dict(row) for row in source.execute(f'SELECT * FROM "{table}"')] for table, _ in TABLES}


def _transform(rows):
    organization_ids = {row["id"] for row in rows["organizations"]}
    project_orgs = {row["id"]: row["organization_id"] for row in rows["projects"]}
    users = {row["id"]: row for row in rows["users"]}
    transformed = {}
    leader_assignments = []
    seen_leaders = set()
    for table, model in TABLES:
        entities = []
        for original in rows[table]:
            values = dict(original)
            for column in list(values):
                if column.endswith("_json"):
                    values[column] = json.loads(values[column])
                elif column in {"created_at", "expires_at", "assigned_at", "occurred_at", "recorded_at", "applied_at"}:
                    values[column] = parse_datetime(values[column])
            if table == "users":
                values["active"] = bool(values["active"])
            if table == "teams":
                leader_id = values.pop("team_leader_id", None)
                organization_id = project_orgs.get(values.get("project_id")) or values["payload_json"].get("organizationId")
                if organization_id is None and len(organization_ids) == 1:
                    organization_id = next(iter(organization_ids))
                if organization_id not in organization_ids:
                    raise ValueError(f"Cannot safely determine organization for team {values['id']}.")
                values["organization_id"] = organization_id
                if leader_id:
                    leader = users.get(leader_id)
                    if not leader or leader["role"] != "TEAM_LEADER" or not leader["active"] or not leader["password_hash"] or leader["organization_id"] != organization_id:
                        raise ValueError(f"Team {values['id']} has an invalid or disabled leader assignment.")
                    if leader_id in seen_leaders:
                        raise ValueError("A legacy Team Leader is assigned to multiple teams; resolve this before import.")
                    seen_leaders.add(leader_id)
                    leader_assignments.append({"team_id": values["id"], "user_id": leader_id, "assigned_at": utc_now()})
            if table == "project_manager_assignments":
                manager = users.get(values["user_id"])
                if not manager or manager["role"] != "PROJECT_MANAGER" or not manager["active"] or not manager["password_hash"] or manager["organization_id"] != project_orgs.get(values["project_id"]):
                    raise ValueError("Legacy Project Manager assignment is invalid, disabled or crosses organizations.")
            fields = {column.name for column in model.__table__.columns}
            unknown = set(values) - fields
            if unknown:
                raise ValueError(f"Unsupported legacy columns in {table}: {', '.join(sorted(unknown))}.")
            entities.append(values)
        if table == "review_history":
            entities.sort(key=lambda item: (item["occurred_at"], item["id"]))
        transformed[table] = entities
    transformed["team_leader_assignments"] = leader_assignments
    return transformed


def import_sqlite(source_path, session, backup_directory=None):
    """Backup, validate and import into the caller's empty migrated transaction."""
    backup_path = backup_sqlite(source_path, backup_directory)
    rows = _read_backup(backup_path)
    values = _transform(rows)
    for _, model in TABLES:
        if session.scalar(select(func.count()).select_from(model)):
            raise ValueError("PostgreSQL target is not empty; import refused without changing existing data.")
    if session.scalar(select(func.count()).select_from(TeamLeaderAssignment)):
        raise ValueError("PostgreSQL target is not empty; import refused.")
    counts = {}
    for table, model in TABLES:
        for entity in values[table]:
            session.add(model(**entity))
        session.flush()
        target_count = session.scalar(select(func.count()).select_from(model))
        source_count = len(rows[table])
        if target_count != source_count:
            raise ValueError(f"Row-count verification failed for {table}.")
        # Check every persisted value, including IDs, hashes, JSON and history.
        primary = [column.name for column in model.__table__.primary_key.columns]
        for entity in values[table]:
            identity = tuple(entity[column] for column in primary)
            actual = session.get(model, identity[0] if len(identity) == 1 else identity)
            if actual is None or any(getattr(actual, key) != value for key, value in entity.items()):
                raise ValueError(f"Content verification failed for {table}.")
        counts[table] = {"sqlite": source_count, "postgresql": target_count, "difference": target_count - source_count}
    for entity in values["team_leader_assignments"]:
        session.add(TeamLeaderAssignment(**entity))
    session.flush()
    counts["team_leader_assignments"] = {"sqlite": len(values["team_leader_assignments"]), "postgresql": session.scalar(select(func.count()).select_from(TeamLeaderAssignment)), "difference": 0, "derivedFrom": "teams.team_leader_id"}
    return {"backupPath": str(backup_path), "tables": counts, "passwords": "Argon2id hashes preserved; legacy format supported", "sessions": "Opaque session token hashes and expiration preserved"}


def main():
    parser = argparse.ArgumentParser(description="Import explicitly selected legacy SQLite into empty migrated PostgreSQL.")
    parser.add_argument("source_path", nargs="?")
    parser.add_argument("--source")
    parser.add_argument("--backup-dir")
    parser.add_argument("--report", help="Optional JSON verification report path (contains no account secrets).")
    options = parser.parse_args()
    source = options.source or options.source_path
    if not source:
        parser.error("An explicit legacy source path is required.")
    from backend.app.core.config import Settings
    from backend.app.db.session import create_engine_and_factory
    engine, factory = create_engine_and_factory(Settings())
    try:
        with factory.begin() as session:
            report = import_sqlite(source, session, options.backup_dir)
        if options.report:
            Path(options.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
