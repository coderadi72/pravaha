"""Thin authorized execution intelligence routes."""
from typing import Literal
from fastapi import APIRouter, Query
from backend.app.api.deps import CurrentUser, SessionDep, SettingsDep
from backend.app.core.errors import ApiError
from backend.app.db.intelligence_repository import memory, visible_projects
from backend.app.models import ScheduleActivity
from backend.app.schemas.intelligence import IntelligenceResponse, MemoryResponse
from backend.app.services.project_intelligence_service import acknowledge, authorize, read_intelligence, refresh, portfolio

router = APIRouter(prefix="/api/intelligence", tags=["Execution intelligence"])

@router.get("/portfolio")
def organization_overview(session: SessionDep, user: CurrentUser, settings: SettingsDep, limit: int = Query(20, ge=1, le=20), offset: int = Query(0, ge=0)):
    return portfolio(session, user, settings, limit, offset)

@router.get("/projects")
def projects(session: SessionDep, user: CurrentUser, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    if user.role not in {"ADMIN", "PROJECT_MANAGER"}:
        raise ApiError(403, "FORBIDDEN", "Project intelligence requires Admin or assigned Project Manager access.")
    rows, total = visible_projects(session, user, limit, offset)
    return {"items": [{"id": p.id, "name": p.name} for p in rows], "total": total, "limit": limit, "offset": offset}

@router.get("/projects/{project_id}", response_model=IntelligenceResponse)
def summary(project_id: str, session: SessionDep, user: CurrentUser, settings: SettingsDep, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    return read_intelligence(session, user, project_id, settings, limit, offset)

@router.post("/projects/{project_id}/refresh", response_model=IntelligenceResponse)
def update(project_id: str, session: SessionDep, user: CurrentUser, settings: SettingsDep):
    return refresh(session, user, project_id, settings)

@router.patch("/projects/{project_id}/warnings/{warning_id}/acknowledge")
def acknowledge_warning(project_id: str, warning_id: str, session: SessionDep, user: CurrentUser):
    return acknowledge(session, user, project_id, warning_id)

@router.get("/projects/{project_id}/memory", response_model=MemoryResponse)
def history(project_id: str, session: SessionDep, user: CurrentUser, activity_id: str | None = None,
            q: str = Query("", max_length=200), kind: Literal["field_update", "review_history", "review", "confirmed_actual", "audit"] | None = None,
            limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    authorize(session, user, project_id)
    if activity_id:
        activity = session.get(ScheduleActivity, activity_id)
        if not activity or activity.project_id != project_id:
            raise ApiError(404, "NOT_FOUND", "Activity not found in this project.")
    return memory(session, user, project_id, activity_id, q.strip(), kind, limit, offset)
