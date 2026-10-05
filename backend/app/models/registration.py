"""Approval requests reserve an email without granting any authenticated access."""
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, column, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class RegistrationRequest(Base):
    __tablename__ = "registration_requests"
    __table_args__ = (
        CheckConstraint("requested_role_category IN ('MANAGEMENT','SUPERVISOR')", name="ck_registration_category"),
        CheckConstraint("status IN ('PENDING','APPROVED','REJECTED')", name="ck_registration_status"),
        CheckConstraint("email = lower(email) AND ((requested_role_category = 'MANAGEMENT' AND split_part(email, '@', 2) = 'pravaha.management.com') OR (requested_role_category = 'SUPERVISOR' AND split_part(email, '@', 2) = 'pravaha.supervisor.com'))", name="ck_registration_email_category"),
        CheckConstraint("(status = 'PENDING' AND password_hash IS NOT NULL AND approved_role IS NULL AND organization_id IS NULL AND account_id IS NULL AND reviewed_by IS NULL AND reviewed_at IS NULL AND rejection_reason IS NULL) OR (status = 'APPROVED' AND password_hash IS NULL AND approved_role IS NOT NULL AND organization_id = review_organization_id AND organization_id IS NOT NULL AND account_id IS NOT NULL AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND rejection_reason IS NULL AND ((requested_role_category = 'MANAGEMENT' AND approved_role IN ('PROJECT_MANAGER','DEPARTMENT')) OR (requested_role_category = 'SUPERVISOR' AND approved_role = 'TEAM_LEADER'))) OR (status = 'REJECTED' AND password_hash IS NULL AND approved_role IS NULL AND organization_id IS NULL AND account_id IS NULL AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND rejection_reason IS NOT NULL)", name="ck_registration_state"),
        Index("uq_registration_email_lower", func.lower(column("email")), unique=True),
        Index("idx_registration_review_status_created", "review_organization_id", "status", "created_at"),
    )
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str | None] = mapped_column(Text)
    requested_role_category: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="PENDING")
    review_organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    approved_role: Mapped[str | None] = mapped_column(Text)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), unique=True)
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
