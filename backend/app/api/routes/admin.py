from typing import Literal

from fastapi import APIRouter, Query

from backend.app.api.deps import AdminUser, SessionDep, SettingsDep
from backend.app.schemas.ingestion import ProjectCreateRequest
from backend.app.db.repository import load_workflow_data, lock_organization
from backend.app.schemas.contracts import DataResponse, LeaderAssignmentRequest, ManagerAssignmentRequest, OrganizationResponse, ProjectsResponse, ProvisionUserRequest, ProvisionUserResponse, TeamAssignmentRequest, TeamsResponse, UsersResponse
from backend.app.services.auth_service import provision_user
from backend.app.services.field_update_service import set_project_manager, set_team_assignment, set_team_leader
from backend.app.schemas.registration import ApproveRegistrationRequest, RejectRegistrationRequest, RegistrationsResponse, RegistrationReviewResponse
from backend.app.services.registration_service import list_registrations, approve_registration, reject_registration

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/registrations", response_model=RegistrationsResponse)
def registrations(session: SessionDep, user: AdminUser, status: Literal["PENDING", "APPROVED", "REJECTED"] | None = None, limit: int = Query(default=25, ge=1, le=100), offset: int = Query(default=0, ge=0, le=100000)):
    return list_registrations(session, user, status, limit, offset)


@router.post("/registrations/{registration_id}/approve", response_model=RegistrationReviewResponse)
def approve(registration_id: str, body: ApproveRegistrationRequest, session: SessionDep, user: AdminUser):
    return approve_registration(session, user, registration_id, body)


@router.post("/registrations/{registration_id}/reject", response_model=RegistrationReviewResponse)
def reject(registration_id: str, body: RejectRegistrationRequest, session: SessionDep, user: AdminUser):
    return reject_registration(session, user, registration_id, body)


@router.get("/organization", response_model=OrganizationResponse)
def organization(session: SessionDep, user: AdminUser):
    data = load_workflow_data(session, user.organization_id)
    return {"organization": data["organization"], "activity": data["organizationActivity"]}


@router.get("/projects", response_model=ProjectsResponse)
def projects(session: SessionDep, user: AdminUser):
    return {"projects": load_workflow_data(session, user.organization_id)["projects"]}


@router.get("/users", response_model=UsersResponse)
def users(session: SessionDep, user: AdminUser):
    return {"users": load_workflow_data(session, user.organization_id)["users"]}


@router.get("/teams", response_model=TeamsResponse)
def teams(session: SessionDep, user: AdminUser):
    return {"teams": load_workflow_data(session, user.organization_id)["teams"]}


@router.post("/users", response_model=ProvisionUserResponse, status_code=201)
def create_user(body: ProvisionUserRequest, session: SessionDep, user: AdminUser):
    lock_organization(session, user.organization_id)
    return provision_user(session, user, body)


@router.patch("/projects/{project_id}/manager", response_model=DataResponse)
def assign_manager(project_id: str, body: ManagerAssignmentRequest, session: SessionDep, user: AdminUser):
    return set_project_manager(session, user, project_id, body)


@router.patch("/teams/{team_id}/assignment", response_model=DataResponse)
def assign_team(team_id: str, body: TeamAssignmentRequest, session: SessionDep, user: AdminUser):
    return set_team_assignment(session, user, team_id, body)


@router.patch("/teams/{team_id}/leader", response_model=DataResponse)
def assign_leader(team_id: str, body: LeaderAssignmentRequest, session: SessionDep, user: AdminUser):
    return set_team_leader(session, user, team_id, body)


@router.get('/system')
def system(session: SessionDep, user: AdminUser, settings: SettingsDep):
    from backend.app.services.system_service import system_status
    return system_status(session,settings)


@router.post('/projects',status_code=201)
def add_project(body: ProjectCreateRequest, session: SessionDep, user: AdminUser):
    from backend.app.services.system_service import create_project
    return create_project(session,user,body)
