from typing import Literal

from fastapi import APIRouter

from backend.app.api.deps import ManagerUser, SessionDep
from backend.app.schemas.contracts import ReviewRequest, ReviewResponse
from backend.app.services.field_update_service import review_field_update

router = APIRouter(prefix="/api/reviews", tags=["PM review"])


@router.post("/{update_id}/{decision}", response_model=ReviewResponse)
def review(update_id: str, decision: Literal["confirm", "change-match", "unmatch", "request-info", "request-review"], body: ReviewRequest, session: SessionDep, user: ManagerUser):
    return review_field_update(session, user, update_id, decision, body)
