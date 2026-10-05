"""Versioned schedules, dependencies, attachments and shared login throttling."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
revision="0003_schedule_ingestion"
down_revision="0002_execution_warnings"
branch_labels=None
depends_on=None


def upgrade():
    op.create_unique_constraint("uq_schedule_id_project","schedule_activities",["id","project_id"])
    op.create_unique_constraint("uq_update_id_project","field_updates",["id","project_id"])
    op.create_table("schedule_versions", sa.Column("id",sa.Text(),primary_key=True),
        sa.Column("project_id",sa.Text(),sa.ForeignKey("projects.id"),nullable=False),
        sa.Column("importer_user_id",sa.Text(),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        *[sa.Column(k,sa.Text(),nullable=False) for k in ["source_format","filename","checksum"]],
        sa.Column("payload_json",JSONB(),nullable=False),sa.UniqueConstraint("id","project_id",name="uq_version_id_project"))
    op.create_index("idx_versions_project_time","schedule_versions",["project_id","created_at"])
    op.create_table("schedule_dependencies",sa.Column("id",sa.Text(),primary_key=True),
        sa.Column("project_id",sa.Text(),sa.ForeignKey("projects.id"),nullable=False),
        sa.Column("version_id",sa.Text(),sa.ForeignKey("schedule_versions.id"),nullable=False),
        sa.Column("predecessor_id",sa.Text(),sa.ForeignKey("schedule_activities.id"),nullable=False),
        sa.Column("successor_id",sa.Text(),sa.ForeignKey("schedule_activities.id"),nullable=False),
        sa.Column("dependency_type",sa.Text(),nullable=False),sa.Column("lag_days",sa.Float(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint("version_id","predecessor_id","successor_id","dependency_type",name="uq_dependency_version_edge"),
        sa.CheckConstraint("dependency_type IN ('FS','SS','FF','SF')",name="ck_dependency_type"),
        sa.CheckConstraint("predecessor_id <> successor_id",name="ck_dependency_not_self"),
        sa.ForeignKeyConstraint(["predecessor_id","project_id"],["schedule_activities.id","schedule_activities.project_id"],name="fk_dependency_predecessor_project"),
        sa.ForeignKeyConstraint(["successor_id","project_id"],["schedule_activities.id","schedule_activities.project_id"],name="fk_dependency_successor_project"),
        sa.ForeignKeyConstraint(["version_id","project_id"],["schedule_versions.id","schedule_versions.project_id"],name="fk_dependency_version_project"))
    op.create_index("idx_dependencies_project_version","schedule_dependencies",["project_id","version_id"])
    op.create_table("field_attachments",sa.Column("id",sa.Text(),primary_key=True),
        sa.Column("project_id",sa.Text(),sa.ForeignKey("projects.id"),nullable=False),
        sa.Column("field_update_id",sa.Text(),sa.ForeignKey("field_updates.id"),nullable=False),
        sa.Column("uploader_user_id",sa.Text(),sa.ForeignKey("users.id"),nullable=False),
        *[sa.Column(k,sa.Text(),nullable=False) for k in ["filename","mime_type","checksum"]],
        sa.Column("size_bytes",sa.Integer(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("content",sa.LargeBinary(),nullable=False),
        sa.ForeignKeyConstraint(["field_update_id","project_id"],["field_updates.id","field_updates.project_id"],name="fk_attachment_update_project"))
    op.create_index("idx_attachments_project_update","field_attachments",["project_id","field_update_id"])
    op.create_table("login_rate_buckets",sa.Column("key_hash",sa.Text(),primary_key=True),sa.Column("attempts",sa.Integer(),nullable=False),sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_login_rate_buckets_expires_at","login_rate_buckets",["expires_at"])
    op.create_index("idx_audit_scope_entity","audit_events",["organization_id","entity","entity_id","occurred_at"])
    op.execute("CREATE INDEX idx_audit_project_time ON audit_events (organization_id, (details_json->>'projectId'), occurred_at)")


def downgrade():
    op.drop_index("idx_audit_project_time",table_name="audit_events")
    op.drop_index("idx_audit_scope_entity",table_name="audit_events")
    for table in ["login_rate_buckets","field_attachments","schedule_dependencies","schedule_versions"]:op.drop_table(table)
    op.drop_constraint("uq_update_id_project","field_updates",type_="unique")
    op.drop_constraint("uq_schedule_id_project","schedule_activities",type_="unique")
