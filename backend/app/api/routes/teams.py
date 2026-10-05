from fastapi import APIRouter

from backend.app.api.deps import LeaderUser, SessionDep
from backend.app.core.permissions import leader_team
from backend.app.schemas.contracts import ActivitiesResponse, FieldUpdatesResponse, TeamLeaderResponse
from backend.app.services.auth_service import safe_user
from backend.app.services.project_service import scoped_workspace

router = APIRouter(prefix="/api/team-leader", tags=["Team Leader"])


@router.get("/me", response_model=TeamLeaderResponse)
def team_leader(session: SessionDep, user: LeaderUser):
    team = leader_team(session, user)
    data = scoped_workspace(session, user)
    return {"user": safe_user(user), "team": next((item for item in data["teams"] if team and item["id"] == team.id), None)}


@router.get("/activities", response_model=ActivitiesResponse)
def activities(session: SessionDep, user: LeaderUser):
    return {"activities": scoped_workspace(session, user)["scheduleActivities"]}


@router.get("/field-updates", response_model=FieldUpdatesResponse)
def field_updates(session: SessionDep, user: LeaderUser):
    return {"fieldUpdates": scoped_workspace(session, user)["fieldUpdates"]}
