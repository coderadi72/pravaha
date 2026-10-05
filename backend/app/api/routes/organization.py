"""Paged organization data, explicit assignments and capability administration."""
from fastapi import APIRouter, Query
from sqlalchemy import select
from backend.app import models as m
from backend.app.api.deps import AdminUser, CurrentUser, SessionDep, SettingsDep
from backend.app.core.errors import ApiError
from backend.app.core.organization_permissions import grants, project_ids, team_ids
from backend.app.db.organization_repository import page, public
from backend.app.db.repository import append_audit, lock_organization
from backend.app.core.permissions import actor, require_project_access
from backend.app.schemas.organization import AllocationRequest, GrantRequest, LinkRequest, SkillRequest, EndAllocationRequest, TeamCreateRequest
from backend.app.services import organization_service as service

router = APIRouter(prefix='/api/organization', tags=['Organization and workforce'])


@router.post('/teams', status_code=201)
def create_team(body: TeamCreateRequest, session: SessionDep, user: AdminUser):
    return service.create_team(session, user, body)


@router.get('/stock')
def stock(session: SessionDep, user: CurrentUser, q: str = Query('', max_length=120), limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):
    from backend.app.core.organization_permissions import require_capability
    from backend.app.services.material_service import stock_page
    require_capability(session, user, 'materials')
    return stock_page(session, user.organization_id, q, limit, offset)


@router.get('/context')
def context(session: SessionDep, user: CurrentUser):
    return service.context(session, user)


@router.get('/overview')
def overview(session: SessionDep, user: AdminUser):
    return service.overview(session, user)


@router.get('/analytics')
def dashboard_analytics(session: SessionDep, user: AdminUser, settings: SettingsDep):
    from backend.app.services.dashboard_analytics import analytics
    return analytics(session, user, settings)


@router.get('/roster')
def roster(session: SessionDep, user: CurrentUser, q: str = Query('', max_length=120), limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):
    return service.roster(session, user, q, limit, offset)


@router.get('/lookups/{kind}')
def lookups(kind: str, session: SessionDep, user: CurrentUser, q: str = Query('', max_length=120), limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):
    if user.role not in {'ADMIN','PROJECT_MANAGER','TEAM_LEADER'} and not (user.role == 'DEPARTMENT' and grants(session, user).intersection({'business','materials','people','quality','hse'})):
        raise ApiError(403, 'FORBIDDEN', 'Management lists require explicit responsibility.')
    model = {'projects': m.Project, 'teams': m.Team, 'accounts': m.User}.get(kind)
    if model is None:
        raise ApiError(404, 'NOT_FOUND', 'Unknown lookup.')
    if kind == 'accounts': service.admin(user)
    filters = [model.organization_id == user.organization_id]
    if user.role in {'PROJECT_MANAGER','TEAM_LEADER'}:
        if kind == 'projects': filters.append(model.id.in_(project_ids(session, user)))
        if kind == 'teams': filters.append(model.id.in_(team_ids(user)) if user.role == 'TEAM_LEADER' else model.project_id.in_(project_ids(session, user)))
    rows, total = page(session, model, filters, q, limit, offset)
    items = [{'id': r.id, 'name': r.full_name, 'role': r.role, 'login_id': r.login_id, 'email': r.email, 'active': r.active} if kind == 'accounts' else
        {'id': r.id, 'name': r.name if kind == 'projects' else r.payload_json.get('name', r.id), 'project_id': r.id if kind == 'projects' else r.project_id} for r in rows]
    return {'items': items, 'total': total, 'limit': limit, 'offset': offset}


@router.post('/allocations', status_code=201)
def allocate(body: AllocationRequest, session: SessionDep, user: AdminUser):
    return service.allocate(session, user, body)


@router.get('/allocations/{employee_id}')
def history(employee_id: str, session: SessionDep, user: AdminUser):
    return service.allocation_history(session, user, employee_id)


@router.post('/allocations/{identifier}/end')
def end(identifier: str, body: EndAllocationRequest, session: SessionDep, user: AdminUser):
    return service.end_allocation(session, user, identifier, body.effective_end)


@router.post('/grants')
def grant(body: GrantRequest, session: SessionDep, user: AdminUser):
    return service.grant(session, user, body)


@router.get('/grants')
def list_grants(session: SessionDep, user: AdminUser):
    service.admin(user)
    return {'items': [{'user_id': r.user_id, 'capability': r.capability} for r in session.scalars(select(m.DepartmentGrant).join(m.User, m.User.id == m.DepartmentGrant.user_id).where(m.User.organization_id == user.organization_id))]}


@router.post('/memberships')
def membership(body: LinkRequest, session: SessionDep, user: AdminUser):
    return service.link(session, user, body)


@router.get('/memberships/{project_id}')
def members(project_id: str, session: SessionDep, user: AdminUser):
    service.admin(user)
    require_project_access(session, user, project_id)
    return {'employees': [public(r) for r in session.scalars(select(m.ProjectMember).where(m.ProjectMember.project_id == project_id))],
        'departments': [public(r) for r in session.scalars(select(m.ProjectDepartment).where(m.ProjectDepartment.project_id == project_id))]}


@router.post('/skills')
def add_skill(body: SkillRequest, session: SessionDep, user: AdminUser):
    service.admin(user)
    lock_organization(session, user.organization_id)
    service.scoped(session, user, m.Employee, body.employee_id)
    service.scoped(session, user, m.Skill, body.skill_id)
    if not session.get(m.EmployeeSkill, (body.employee_id, body.skill_id)):
        session.add(m.EmployeeSkill(employee_id=body.employee_id, skill_id=body.skill_id))
    append_audit(session, actor(user), 'Employee skill assigned', 'employee', body.employee_id, {'skillId': body.skill_id})
    return {'ok': True}
