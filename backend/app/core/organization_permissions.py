"""Explicit grants; department or designation membership never confers access."""
from sqlalchemy import select
from backend.app.core.errors import ApiError
from backend.app.models import DepartmentGrant, ProjectManagerAssignment, TeamLeaderAssignment, Team


def grants(session, user):
    return set(session.scalars(select(DepartmentGrant.capability).where(DepartmentGrant.user_id == user.id)))


def permitted(session, user, capability, confidential=False):
    if user.role == 'WORKFORCE':
        return False
    if confidential:
        return 'hr-confidential' in grants(session, user)
    return user.role == 'ADMIN' or capability in grants(session, user)


def require_capability(session, user, capability, confidential=False):
    if not permitted(session, user, capability, confidential):
        raise ApiError(403, 'FORBIDDEN', 'This operation requires an explicitly authorized capability.')


def project_ids(session, user):
    if user.role == 'PROJECT_MANAGER':
        return select(ProjectManagerAssignment.project_id).where(ProjectManagerAssignment.user_id == user.id)
    if user.role == 'TEAM_LEADER':
        return select(Team.project_id).join(TeamLeaderAssignment, TeamLeaderAssignment.team_id == Team.id).where(TeamLeaderAssignment.user_id == user.id)
    return select(Team.project_id).where(False)


def team_ids(user):
    return select(TeamLeaderAssignment.team_id).where(TeamLeaderAssignment.user_id == user.id)
