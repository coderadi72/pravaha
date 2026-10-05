from fastapi import APIRouter

from backend.app.api.deps import LeaderUser, SessionDep
from backend.app.schemas.contracts import ActivityActionRequest, DataResponse
from backend.app.services.field_update_service import perform_activity_action

router = APIRouter(prefix="/api/team-leader/activities", tags=["Activity actions"])


@router.post("/{activity_id}/actions", response_model=DataResponse)
def action(activity_id: str, body: ActivityActionRequest, session: SessionDep, user: LeaderUser):
    return perform_activity_action(session, user, activity_id, body)
