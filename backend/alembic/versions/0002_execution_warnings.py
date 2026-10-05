"""Persist execution warning lifecycle without changing existing workflow data."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "0002_execution_warnings"
down_revision = "0001_postgresql_foundation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("execution_warnings",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("project_id", sa.Text(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activity_id", sa.Text(), sa.ForeignKey("schedule_activities.id")),
        sa.Column("warning_type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint("status IN ('OPEN','ACKNOWLEDGED','RESOLVED')", name="ck_warning_status"))
    op.create_index("idx_warning_project_status", "execution_warnings", ["project_id", "status"])


def downgrade():
    op.drop_table("execution_warnings")
