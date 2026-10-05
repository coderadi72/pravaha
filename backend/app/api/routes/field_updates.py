from fastapi import APIRouter

from backend.app.api.deps import LeaderUser, SessionDep
from backend.app.schemas.contracts import FieldUpdateEditRequest, FieldUpdateRequest, FieldUpdateResponse
from backend.app.services.field_update_service import create_field_update, edit_field_update

router = APIRouter(prefix="/api/team-leader/field-updates", tags=["Field updates"])


@router.post("", response_model=FieldUpdateResponse, status_code=201)
def submit(body: FieldUpdateRequest, session: SessionDep, user: LeaderUser):
    return create_field_update(session, user, body)


@router.patch("/{update_id}", response_model=FieldUpdateResponse)
def edit(update_id: str, body: FieldUpdateEditRequest, session: SessionDep, user: LeaderUser):
    return edit_field_update(session, user, update_id, body)
