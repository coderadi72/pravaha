"""Official-domain approval requests; existing accounts and sessions are preserved."""
from alembic import op
import sqlalchemy as sa

revision = "0005_registration_requests"
down_revision = "0004_organization"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "registration_requests",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("requested_role_category", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("review_organization_id", sa.Text(), nullable=False),
        sa.Column("approved_role", sa.Text(), nullable=True),
        sa.Column("organization_id", sa.Text(), nullable=True),
        sa.Column("account_id", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("requested_role_category IN ('MANAGEMENT','SUPERVISOR')", name="ck_registration_category"),
        sa.CheckConstraint("status IN ('PENDING','APPROVED','REJECTED')", name="ck_registration_status"),
        sa.CheckConstraint("email = lower(email) AND ((requested_role_category = 'MANAGEMENT' AND split_part(email, '@', 2) = 'pravaha.management.com') OR (requested_role_category = 'SUPERVISOR' AND split_part(email, '@', 2) = 'pravaha.supervisor.com'))", name="ck_registration_email_category"),
        sa.CheckConstraint("(status = 'PENDING' AND password_hash IS NOT NULL AND approved_role IS NULL AND organization_id IS NULL AND account_id IS NULL AND reviewed_by IS NULL AND reviewed_at IS NULL AND rejection_reason IS NULL) OR (status = 'APPROVED' AND password_hash IS NULL AND approved_role IS NOT NULL AND organization_id = review_organization_id AND organization_id IS NOT NULL AND account_id IS NOT NULL AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND rejection_reason IS NULL AND ((requested_role_category = 'MANAGEMENT' AND approved_role IN ('PROJECT_MANAGER','DEPARTMENT')) OR (requested_role_category = 'SUPERVISOR' AND approved_role = 'TEAM_LEADER'))) OR (status = 'REJECTED' AND password_hash IS NULL AND approved_role IS NULL AND organization_id IS NULL AND account_id IS NULL AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND rejection_reason IS NOT NULL)", name="ck_registration_state"),
        sa.ForeignKeyConstraint(["review_organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["account_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id"),
    )
    op.create_index("uq_registration_email_lower", "registration_requests", [sa.text("lower(email)")], unique=True)
    op.create_index("idx_registration_review_status_created", "registration_requests", ["review_organization_id", "status", "created_at"])


def downgrade():
    op.drop_index("idx_registration_review_status_created", table_name="registration_requests")
    op.drop_index("uq_registration_email_lower", table_name="registration_requests")
    op.drop_table("registration_requests")
