"""PostgreSQL entities with stable legacy IDs and explicit ownership relations."""
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, Float, LargeBinary, UniqueConstraint, ForeignKeyConstraint, CheckConstraint, DateTime, ForeignKey, Identity, Index, Integer, Text, column, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, query_expression

from backend.app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    data_label: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('ADMIN','PROJECT_MANAGER','TEAM_LEADER','WORKFORCE','DEPARTMENT')", name="ck_users_role"),
        CheckConstraint("login_id IS NULL OR login_id ~ '^[a-zA-Z0-9][a-zA-Z0-9._-]{2,79}$'", name='ck_login_identifier'),
        Index("uq_users_email_lower", func.lower(column("email")), unique=True),
        Index("uq_users_login_lower", func.lower(column("login_id")), unique=True),
        Index("idx_users_org", "organization_id"),
    )
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    email: Mapped[str] = mapped_column(Text, unique=True)
    login_id: Mapped[str | None] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (Index("idx_projects_org", "organization_id"),)
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class ProjectManagerAssignment(Base):
    __tablename__ = "project_manager_assignments"
    __table_args__ = (Index("idx_project_manager_user", "user_id"),)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (Index("idx_teams_project", "project_id"), Index("idx_teams_org", "organization_id"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class TeamLeaderAssignment(Base):
    __tablename__ = "team_leader_assignments"
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ScheduleActivity(Base):
    __tablename__ = "schedule_activities"
    __table_args__ = (Index("idx_schedule_project_team", "project_id", "team_id"), UniqueConstraint("id", "project_id", name="uq_schedule_id_project"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id"))
    baseline_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class FieldUpdate(Base):
    __tablename__ = "field_updates"
    __table_args__ = (Index("idx_updates_project", "project_id", "team_id"), Index("idx_updates_submitter", "submitter_user_id"), UniqueConstraint("id", "project_id", name="uq_update_id_project"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    team_id: Mapped[str | None] = mapped_column(ForeignKey("teams.id"))
    submitter_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class ActivityMatch(Base):
    retired_schedule_link: Mapped[bool | None] = query_expression()
    __tablename__ = "activity_matches"
    __table_args__ = (Index("idx_match_schedule", "schedule_activity_id"),)
    field_update_id: Mapped[str] = mapped_column(ForeignKey("field_updates.id", ondelete="CASCADE"), primary_key=True)
    schedule_activity_id: Mapped[str | None] = mapped_column(ForeignKey("schedule_activities.id"))
    match_status: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (Index("idx_reviews_status", "status"), Index("idx_reviews_update", "field_update_id"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    field_update_id: Mapped[str] = mapped_column(ForeignKey("field_updates.id", ondelete="CASCADE"))
    reviewer_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class ReviewHistory(Base):
    __tablename__ = "review_history"
    __table_args__ = (Index("idx_history_update_time", "field_update_id", "occurred_at"),)
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    sequence: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True)
    field_update_id: Mapped[str] = mapped_column(ForeignKey("field_updates.id", ondelete="CASCADE"))
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    actor_label: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ScheduleActivityContribution(Base):
    __tablename__ = "schedule_activity_contributions"
    __table_args__ = (Index("idx_contribution_schedule_time", "schedule_activity_id", "recorded_at"),)
    field_update_id: Mapped[str] = mapped_column(ForeignKey("field_updates.id", ondelete="CASCADE"), primary_key=True)
    schedule_activity_id: Mapped[str] = mapped_column(ForeignKey("schedule_activities.id"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    state_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (Index("idx_audit_org_time", "organization_id", "occurred_at"),
        Index("idx_audit_scope_entity", "organization_id", "entity", "entity_id", "occurred_at"),
        Index("idx_audit_project_time", "organization_id", __import__("sqlalchemy").text("(details_json->>'projectId')"), "occurred_at"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    actor_label: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    entity: Mapped[str] = mapped_column(Text)
    entity_id: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    details_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class SessionToken(Base):
    __tablename__ = "sessions"
    __table_args__ = (Index("idx_sessions_expiry", "expires_at"), Index("idx_sessions_user", "user_id"))
    token_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LegacyMigration(Base):
    """SQLite migration provenance; Alembic owns canonical schema history."""
    __tablename__ = "legacy_schema_migrations"
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# Alias for callers that describe this persisted opaque session as a login session.
LoginSession = SessionToken


class ExecutionWarning(Base):
    """Stable warning lifecycle; transitions live in the existing audit ledger."""
    __tablename__ = "execution_warnings"
    __table_args__ = (Index("idx_warning_project_status", "project_id", "status"),
        CheckConstraint("status IN ('OPEN','ACKNOWLEDGED','RESOLVED')", name="ck_warning_status"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    activity_id: Mapped[str | None] = mapped_column(ForeignKey("schedule_activities.id"))
    warning_type: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class ScheduleVersion(Base):
    __tablename__ = "schedule_versions"
    __table_args__ = (Index("idx_versions_project_time", "project_id", "created_at"), UniqueConstraint("id", "project_id", name="uq_version_id_project"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    importer_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_format: Mapped[str] = mapped_column(Text)
    filename: Mapped[str] = mapped_column(Text)
    checksum: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB)


class ScheduleDependency(Base):
    __tablename__ = "schedule_dependencies"
    __table_args__ = (Index("idx_dependencies_project_version", "project_id", "version_id"),
        UniqueConstraint("version_id", "predecessor_id", "successor_id", "dependency_type", name="uq_dependency_version_edge"),
        CheckConstraint("dependency_type IN ('FS','SS','FF','SF')", name="ck_dependency_type"),
        CheckConstraint("predecessor_id <> successor_id", name="ck_dependency_not_self"),
        ForeignKeyConstraint(["predecessor_id","project_id"],["schedule_activities.id","schedule_activities.project_id"],name="fk_dependency_predecessor_project"),
        ForeignKeyConstraint(["successor_id","project_id"],["schedule_activities.id","schedule_activities.project_id"],name="fk_dependency_successor_project"),
        ForeignKeyConstraint(["version_id","project_id"],["schedule_versions.id","schedule_versions.project_id"],name="fk_dependency_version_project"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    version_id: Mapped[str] = mapped_column(ForeignKey("schedule_versions.id"))
    predecessor_id: Mapped[str] = mapped_column(ForeignKey("schedule_activities.id"))
    successor_id: Mapped[str] = mapped_column(ForeignKey("schedule_activities.id"))
    dependency_type: Mapped[str] = mapped_column(Text)
    lag_days: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FieldAttachment(Base):
    __tablename__ = "field_attachments"
    __table_args__ = (Index("idx_attachments_project_update", "project_id", "field_update_id"), ForeignKeyConstraint(["field_update_id","project_id"],["field_updates.id","field_updates.project_id"],name="fk_attachment_update_project"))
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    field_update_id: Mapped[str] = mapped_column(ForeignKey("field_updates.id"))
    uploader_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(Text)
    mime_type: Mapped[str] = mapped_column(Text)
    size_bytes: Mapped[int] = mapped_column(Integer)
    checksum: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)


class LoginRateBucket(Base):
    __tablename__ = "login_rate_buckets"
    key_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    attempts: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
