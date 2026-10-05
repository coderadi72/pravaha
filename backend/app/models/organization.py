"""Organization identity, explicit account capabilities and dated allocation."""
from datetime import date
from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base


class OrgRecord:
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey('organizations.id'), index=True)


class Department(OrgRecord, Base):
    __tablename__ = 'departments'
    __table_args__ = (UniqueConstraint('organization_id', 'name', name='uq_department_name'),)
    name: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Location(OrgRecord, Base):
    __tablename__ = 'locations'
    name: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text, default='')
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class DepartmentUnit(OrgRecord, Base):
    __tablename__ = 'department_units'
    name: Mapped[str] = mapped_column(Text)
    department_id: Mapped[str] = mapped_column(ForeignKey('departments.id'))
    location_id: Mapped[str | None] = mapped_column(ForeignKey('locations.id'))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Designation(OrgRecord, Base):
    __tablename__ = 'designations'
    name: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Skill(OrgRecord, Base):
    __tablename__ = 'skills'
    name: Mapped[str] = mapped_column(Text)
    discipline: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Employee(OrgRecord, Base):
    __tablename__ = 'employees'
    __table_args__ = (UniqueConstraint('organization_id', 'workforce_code', name='uq_employee_code'),
        Index('idx_employee_org_department', 'organization_id', 'department_id'))
    workforce_code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    department_id: Mapped[str] = mapped_column(ForeignKey('departments.id'))
    unit_id: Mapped[str | None] = mapped_column(ForeignKey('department_units.id'))
    designation_id: Mapped[str | None] = mapped_column(ForeignKey('designations.id'))
    location_id: Mapped[str | None] = mapped_column(ForeignKey('locations.id'))
    manager_id: Mapped[str | None] = mapped_column(ForeignKey('employees.id'))
    account_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), unique=True)
    discipline: Mapped[str] = mapped_column(Text, default='')
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class EmployeeSkill(Base):
    __tablename__ = 'employee_skills'
    employee_id: Mapped[str] = mapped_column(ForeignKey('employees.id'), primary_key=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey('skills.id'), primary_key=True)


class DepartmentGrant(Base):
    __tablename__ = 'department_grants'
    __table_args__ = (CheckConstraint("capability IN ('business','materials','people','quality','hse','hr-confidential')", name='ck_department_capability'),)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), primary_key=True)
    capability: Mapped[str] = mapped_column(Text, primary_key=True)
    granted_by: Mapped[str] = mapped_column(ForeignKey('users.id'))


class ProjectDepartment(Base):
    __tablename__ = 'project_departments'
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'), primary_key=True)
    department_id: Mapped[str] = mapped_column(ForeignKey('departments.id'), primary_key=True)


class ProjectMember(Base):
    __tablename__ = 'project_members'
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'), primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey('employees.id'), primary_key=True)
    responsibility: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class WorkforceAssignment(OrgRecord, Base):
    __tablename__ = 'workforce_assignments'
    __table_args__ = (Index('uq_workforce_active', 'employee_id', unique=True, postgresql_where=text("status = 'ACTIVE'")),
        Index('idx_workforce_project_team', 'organization_id', 'project_id', 'team_id'),
        CheckConstraint("status IN ('ACTIVE','ENDED')", name='ck_workforce_status'),
        CheckConstraint('effective_end IS NULL OR effective_end >= effective_start', name='ck_workforce_dates'))
    employee_id: Mapped[str] = mapped_column(ForeignKey('employees.id'))
    project_id: Mapped[str] = mapped_column(ForeignKey('projects.id'))
    team_id: Mapped[str] = mapped_column(ForeignKey('teams.id'))
    effective_start: Mapped[date] = mapped_column(Date)
    effective_end: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text)
    assigned_by: Mapped[str] = mapped_column(ForeignKey('users.id'))
