"""Initial PostgreSQL foundation preserving existing PRAVAHA entity IDs.

Revision ID: 0001_postgresql_foundation
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_postgresql_foundation"
down_revision = None
branch_labels = None
depends_on = None


def text(name, nullable=False, primary_key=False):
    return sa.Column(name, sa.Text(), nullable=nullable, primary_key=primary_key)


def fk(name, target, nullable=False, primary_key=False, ondelete=None):
    return sa.Column(name, sa.Text(), sa.ForeignKey(target, ondelete=ondelete), nullable=nullable, primary_key=primary_key)


def timestamp(name):
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False)


def payload(name="payload_json"):
    return sa.Column(name, postgresql.JSONB(), nullable=False)


def upgrade():
    op.create_table("organizations", text("id", primary_key=True), text("name"), text("data_label"), payload())
    op.create_table("users", text("id", primary_key=True), fk("organization_id", "organizations.id"), text("email"), text("full_name"), text("role"), text("password_hash", nullable=True), sa.Column("active", sa.Boolean(), nullable=False), timestamp("created_at"), sa.UniqueConstraint("email"), sa.CheckConstraint("role IN ('ADMIN','PROJECT_MANAGER','TEAM_LEADER')", name="ck_users_role"))
    op.create_index("uq_users_email_lower", "users", [sa.text("lower(email)")], unique=True)
    op.create_index("idx_users_org", "users", ["organization_id"])
    op.create_table("projects", text("id", primary_key=True), fk("organization_id", "organizations.id"), text("name"), text("status"), payload())
    op.create_index("idx_projects_org", "projects", ["organization_id"])
    op.create_table("project_manager_assignments", fk("project_id", "projects.id", primary_key=True, ondelete="CASCADE"), fk("user_id", "users.id", ondelete="CASCADE"), timestamp("assigned_at"))
    op.create_index("idx_project_manager_user", "project_manager_assignments", ["user_id"])
    op.create_table("teams", text("id", primary_key=True), fk("organization_id", "organizations.id"), fk("project_id", "projects.id", nullable=True), payload())
    op.create_index("idx_teams_project", "teams", ["project_id"])
    op.create_index("idx_teams_org", "teams", ["organization_id"])
    op.create_table("team_leader_assignments", fk("team_id", "teams.id", primary_key=True, ondelete="CASCADE"), fk("user_id", "users.id", ondelete="CASCADE"), timestamp("assigned_at"), sa.UniqueConstraint("user_id"))
    op.create_table("schedule_activities", text("id", primary_key=True), fk("project_id", "projects.id"), fk("team_id", "teams.id", nullable=True), payload("baseline_json"), payload())
    op.create_index("idx_schedule_project_team", "schedule_activities", ["project_id", "team_id"])
    op.create_table("field_updates", text("id", primary_key=True), fk("project_id", "projects.id"), fk("team_id", "teams.id", nullable=True), fk("submitter_user_id", "users.id", nullable=True), text("status"), payload())
    op.create_index("idx_updates_project", "field_updates", ["project_id", "team_id"])
    op.create_index("idx_updates_submitter", "field_updates", ["submitter_user_id"])
    op.create_table("activity_matches", fk("field_update_id", "field_updates.id", primary_key=True, ondelete="CASCADE"), fk("schedule_activity_id", "schedule_activities.id", nullable=True), text("match_status"), payload())
    op.create_index("idx_match_schedule", "activity_matches", ["schedule_activity_id"])
    op.create_table("reviews", text("id", primary_key=True), fk("field_update_id", "field_updates.id", ondelete="CASCADE"), fk("reviewer_user_id", "users.id", nullable=True), text("status"), payload())
    op.create_index("idx_reviews_status", "reviews", ["status"])
    op.create_index("idx_reviews_update", "reviews", ["field_update_id"])
    op.create_table("review_history", text("id", primary_key=True), sa.Column("sequence", sa.BigInteger(), sa.Identity(), nullable=False), fk("field_update_id", "field_updates.id", ondelete="CASCADE"), fk("actor_user_id", "users.id", nullable=True), text("actor_label"), text("action"), timestamp("occurred_at"), sa.UniqueConstraint("sequence"))
    op.create_index("idx_history_update_time", "review_history", ["field_update_id", "occurred_at"])
    op.create_table("schedule_activity_contributions", fk("field_update_id", "field_updates.id", primary_key=True, ondelete="CASCADE"), fk("schedule_activity_id", "schedule_activities.id"), timestamp("recorded_at"), payload("state_json"))
    op.create_index("idx_contribution_schedule_time", "schedule_activity_contributions", ["schedule_activity_id", "recorded_at"])
    op.create_table("audit_events", text("id", primary_key=True), fk("organization_id", "organizations.id"), fk("actor_user_id", "users.id", nullable=True), text("actor_label"), text("action"), text("entity"), text("entity_id", nullable=True), timestamp("occurred_at"), payload("details_json"))
    op.create_index("idx_audit_org_time", "audit_events", ["organization_id", "occurred_at"])
    op.create_table("sessions", text("token_hash", primary_key=True), fk("user_id", "users.id", ondelete="CASCADE"), timestamp("created_at"), timestamp("expires_at"))
    op.create_index("idx_sessions_expiry", "sessions", ["expires_at"])
    op.create_index("idx_sessions_user", "sessions", ["user_id"])
    op.create_table("legacy_schema_migrations", sa.Column("version", sa.Integer(), primary_key=True), timestamp("applied_at"))


def downgrade():
    # Downgrade is an explicitly requested destructive operation, never startup.
    for table in ("legacy_schema_migrations", "sessions", "audit_events", "schedule_activity_contributions", "review_history", "reviews", "activity_matches", "field_updates", "schedule_activities", "team_leader_assignments", "teams", "project_manager_assignments", "projects", "users", "organizations"):
        op.drop_table(table)
