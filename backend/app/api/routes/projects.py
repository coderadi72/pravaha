from fastapi import APIRouter

from backend.app.api.deps import AdminUser, CurrentUser, ManagerUser, SessionDep
from backend.app.core.errors import ApiError
from backend.app.core.permissions import require_project_access
from backend.app.schemas.contracts import ErrorResponse, FieldUpdatesResponse, ProjectResponse, ProjectsResponse, ReviewsResponse, ScheduleResponse, WorkspaceResponse
from backend.app.services.auth_service import safe_user
from backend.app.services.project_service import scoped_workspace

router = APIRouter(tags=["Workspace and projects"])


@router.get("/api/workspace", response_model=WorkspaceResponse)
def workspace(session: SessionDep, user: CurrentUser):
    return {"user": safe_user(user), "data": scoped_workspace(session, user)}


@router.get("/api/projects", response_model=ProjectsResponse)
def projects(session: SessionDep, user: ManagerUser):
    return {"projects": scoped_workspace(session, user)["projects"]}


@router.get("/api/projects/{project_id}", response_model=ProjectResponse)
def project(project_id: str, session: SessionDep, user: ManagerUser):
    require_project_access(session, user, project_id)
    return {"project": next(item for item in scoped_workspace(session, user)["projects"] if item["id"] == project_id)}


@router.get("/api/projects/{project_id}/schedule", response_model=ScheduleResponse)
def schedule(project_id: str, session: SessionDep, user: ManagerUser):
    require_project_access(session, user, project_id)
    return {"schedule": [item for item in scoped_workspace(session, user)["scheduleActivities"] if item["projectId"] == project_id]}


@router.get("/api/projects/{project_id}/field-updates", response_model=FieldUpdatesResponse)
def updates(project_id: str, session: SessionDep, user: ManagerUser):
    require_project_access(session, user, project_id)
    return {"fieldUpdates": [item for item in scoped_workspace(session, user)["fieldUpdates"] if item["projectId"] == project_id]}


@router.get("/api/projects/{project_id}/reviews", response_model=ReviewsResponse)
def reviews(project_id: str, session: SessionDep, user: ManagerUser):
    require_project_access(session, user, project_id)
    data = scoped_workspace(session, user)
    update_ids = {item["id"] for item in data["fieldUpdates"] if item["projectId"] == project_id}
    return {"reviews": [item for item in data["reviewItems"] if item["fieldUpdateId"] in update_ids]}


@router.patch("/api/projects/{project_id}/schedule/{activity_id}/baseline", response_model=ErrorResponse, status_code=501)
def baseline(project_id: str, activity_id: str, user: AdminUser):
    raise ApiError(501, "NOT_IMPLEMENTED", "Baseline editing is not part of the current workflow API.")
