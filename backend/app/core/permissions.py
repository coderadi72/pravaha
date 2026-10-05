from sqlalchemy import select

from backend.app.core.errors import ApiError
from backend.app.models import Project, ProjectManagerAssignment, Team, TeamLeaderAssignment


def actor(user):
    return {"id": user.id, "email": user.email, "fullName": user.full_name, "role": user.role, "organizationId": user.organization_id}


def project_for(session, user, project_id):
    project = session.scalar(select(Project).where(Project.id == project_id, Project.organization_id == user.organization_id))
    if not project:
        raise ApiError(404, "NOT_FOUND", "Project not found.")
    return project


def require_project_access(session, user, project_id):
    project = project_for(session, user, project_id)
    if user.role == "ADMIN":
        return project
    if user.role == "PROJECT_MANAGER" and session.scalar(select(ProjectManagerAssignment).where(ProjectManagerAssignment.project_id == project_id, ProjectManagerAssignment.user_id == user.id)):
        return project
    raise ApiError(403, "FORBIDDEN", "You do not have access to this project.")


def team_for(session, user, team_id):
    team = session.scalar(select(Team).where(Team.id == team_id, Team.organization_id == user.organization_id))
    if not team:
        raise ApiError(404, "NOT_FOUND", "Team not found.")
    return team


def leader_team(session, user):
    return session.scalar(select(Team).join(TeamLeaderAssignment, TeamLeaderAssignment.team_id == Team.id).where(TeamLeaderAssignment.user_id == user.id, Team.organization_id == user.organization_id))


def require_team_access(session, user, team_id):
    if user.role == "ADMIN":
        return team_for(session, user, team_id)
    if user.role == "TEAM_LEADER":
        team = leader_team(session, user)
        if team and team.id == team_id:
            return team
    raise ApiError(403, "FORBIDDEN", "You do not have access to this team.")
