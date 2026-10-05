"""Typed people cases and project-linked assurance workflows."""
from datetime import date
from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base
from backend.app.models.organization import OrgRecord


class PeopleRecord(OrgRecord, Base):
    __tablename__ = 'people_records'
    __table_args__ = (CheckConstraint('end_on IS NULL OR end_on >= start_on', name='ck_people_dates'),
        CheckConstraint("confidential = (kind IN ('grievance','wellbeing','employee-relations','performance'))", name='ck_people_privacy'),)
    employee_id: Mapped[str | None] = mapped_column(ForeignKey('employees.id'))
    project_id: Mapped[str | None] = mapped_column(ForeignKey('projects.id'))
    team_id: Mapped[str | None] = mapped_column(ForeignKey('teams.id'))
    kind: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    narrative: Mapped[str] = mapped_column(Text, default='', deferred=True)
    confidential: Mapped[bool] = mapped_column(Boolean, default=False)
    start_on: Mapped[date] = mapped_column(Date)
    end_on: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text)


class Inspection(OrgRecord, Base):
    __tablename__ = 'inspections'
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'))
    team_id: Mapped[str | None] = mapped_column(ForeignKey('teams.id'))
    activity_id: Mapped[str | None] = mapped_column(ForeignKey('schedule_activities.id'))
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default='PLANNED')


class QualityIssue(OrgRecord, Base):
    __tablename__ = 'quality_issues'
    inspection_id: Mapped[str] = mapped_column(ForeignKey('inspections.id'))
    title: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(Text, default='ISSUE')
    status: Mapped[str] = mapped_column(Text, default='OPEN')


class SafetyEvent(OrgRecord, Base):
    __tablename__ = 'safety_events'
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'))
    team_id: Mapped[str | None] = mapped_column(ForeignKey('teams.id'))
    title: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default='OPEN')


class CorrectiveAction(OrgRecord, Base):
    __tablename__ = 'corrective_actions'
    __table_args__ = (CheckConstraint('(quality_issue_id IS NOT NULL) <> (safety_event_id IS NOT NULL)', name='ck_action_source'),)
    quality_issue_id: Mapped[str | None] = mapped_column(ForeignKey('quality_issues.id'))
    safety_event_id: Mapped[str | None] = mapped_column(ForeignKey('safety_events.id'))
    assigned_employee_id: Mapped[str] = mapped_column(ForeignKey('employees.id'))
    title: Mapped[str] = mapped_column(Text)
    due_on: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text, default='OPEN')
