"""Organization master data and auditable explicit workforce allocation."""
from datetime import date
from uuid import uuid4
from sqlalchemy import func, select
from backend.app import models as m
from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor, require_project_access
from backend.app.core.organization_permissions import grants, project_ids, team_ids
from backend.app.db.repository import append_audit, lock_organization
from backend.app.db.organization_repository import public, page


def scoped(session, user, model, identifier):
    row = session.get(model, identifier)
    if not row or row.organization_id != user.organization_id:
        raise ApiError(404, 'NOT_FOUND', 'Record not found in this organization.')
    return row


def admin(user):
    if user.role != 'ADMIN':
        raise ApiError(403, 'FORBIDDEN', 'Organization administration requires Admin access.')


def create_team(session, user, body):
    admin(user)
    lock_organization(session, user.organization_id)
    project = scoped(session, user, m.Project, body.project_id)
    if project.status in {'Inactive','Closed'} or not body.name.strip():
        raise ApiError(400, 'INVALID_TEAM', 'Team requires a name and an active project.')
    identifier = 'TEAM-'+str(uuid4())
    payload = {'id':identifier, 'name':body.name.strip(), 'projectId':project.id, 'teamLeaderId':None,
        'site':body.site.strip(), 'members':0, 'active':0, 'onLeave':0, 'other':0, 'status':'Active'}
    session.add(m.Team(id=identifier, organization_id=user.organization_id, project_id=project.id, payload_json=payload))
    project.payload_json = {**project.payload_json, 'teamIds':[*project.payload_json.get('teamIds',[]),identifier]}
    session.flush()
    append_audit(session, actor(user), 'Project team created', 'team', identifier, {'projectId':project.id})
    return payload


def context(session, user):
    if user.role == 'WORKFORCE':
        raise ApiError(403, 'FORBIDDEN', 'Workforce accounts have no management workspace permissions.')
    from backend.app.db.organization_repository import RESOURCES
    capabilities = grants(session, user)
    return {'capabilities': sorted(capabilities), 'role': user.role, 'dataLabel': session.get(m.Organization, user.organization_id).data_label,
        'resources': [{'key': key, 'capability': r.capability, 'fields': [{'name': field, 'required': not r.model.__table__.c[field].nullable and r.model.__table__.c[field].default is None,
            'type': r.model.__table__.c[field].type.__class__.__name__} for field in r.fields], 'transitions': r.transitions or {},
            'canCreate': user.role == 'ADMIN' or r.capability in capabilities or (key == 'corrective-actions' and 'hse' in capabilities) or (user.role in {'PROJECT_MANAGER','TEAM_LEADER'} and key in {'material-requests','inspections','safety','people'}) or (user.role == 'PROJECT_MANAGER' and key in {'quality-issues','corrective-actions'}),
            'canEdit': user.role == 'ADMIN' and r.capability == 'organization', 'canReview': user.role != 'TEAM_LEADER'}
            for key, r in RESOURCES.items() if user.role == 'ADMIN' or r.capability in capabilities or (key == 'corrective-actions' and 'hse' in capabilities) or (user.role in {'PROJECT_MANAGER','TEAM_LEADER'} and r.capability in {'materials','people','quality','hse'}) or (user.role == 'PROJECT_MANAGER' and key == 'contracts')],
        'confidentialAccess': 'hr-confidential' in capabilities}


def roster(session, user, q, limit, offset):
    if user.role not in {'ADMIN','PROJECT_MANAGER','TEAM_LEADER'}:
        if not grants(session, user).intersection({'people','hr-confidential'}):
            raise ApiError(403, 'FORBIDDEN', 'Roster access is not authorized.')
    filters = [m.Employee.organization_id == user.organization_id]
    if user.role in {'PROJECT_MANAGER','TEAM_LEADER'}:
        allocation = select(m.WorkforceAssignment.employee_id).where(m.WorkforceAssignment.project_id.in_(project_ids(session, user)), m.WorkforceAssignment.status == 'ACTIVE')
        if user.role == 'TEAM_LEADER':
            allocation = allocation.where(m.WorkforceAssignment.team_id.in_(team_ids(user)))
        filters.append(m.Employee.id.in_(allocation))
    rows, total = page(session, m.Employee, filters, q, limit, offset)
    ids = [r.id for r in rows]
    allocations = session.scalars(select(m.WorkforceAssignment).where(m.WorkforceAssignment.employee_id.in_(ids), m.WorkforceAssignment.status == 'ACTIVE')).all()
    skills = session.execute(select(m.EmployeeSkill.employee_id, m.Skill.name).join(m.Skill).where(m.EmployeeSkill.employee_id.in_(ids))).all()
    return {'items': [{**public(r), 'assignment': next((public(a) for a in allocations if a.employee_id == r.id), None), 'skills': [s.name for s in skills if s.employee_id == r.id]} for r in rows], 'total': total, 'limit': limit, 'offset': offset}


def allocate(session, user, body):
    admin(user)
    lock_organization(session, user.organization_id)
    employee = scoped(session, user, m.Employee, body.employee_id)
    project = scoped(session, user, m.Project, body.project_id)
    team = scoped(session, user, m.Team, body.team_id)
    if not employee.active or not session.get(m.Department, employee.department_id).active or team.payload_json.get('status') == 'Inactive' or project.status in {'Inactive','Closed'}:
        raise ApiError(409, 'INACTIVE', 'Allocation requires active employee, project and team.')
    if body.effective_start > date.today():
        raise ApiError(400, 'INVALID_DATE', 'Active allocation cannot start in the future.')
    if team.project_id != project.id:
        raise ApiError(400, 'INVALID_ASSIGNMENT', 'Team does not belong to the selected project.')
    pm = session.get(m.ProjectManagerAssignment, project.id)
    tl = session.get(m.TeamLeaderAssignment, team.id)
    if not pm or not tl or any(not (account := session.get(m.User, a.user_id)) or not account.active or not account.password_hash for a in (pm, tl)):
        raise ApiError(409, 'INVALID_ASSIGNMENT', 'An enabled PM and TL must be assigned before workforce allocation.')
    old = session.scalar(select(m.WorkforceAssignment).where(m.WorkforceAssignment.employee_id == employee.id, m.WorkforceAssignment.status == 'ACTIVE').with_for_update())
    if old:
        if not body.transfer:
            raise ApiError(409, 'ALREADY_ASSIGNED', 'Use an explicit transfer for an already allocated employee.')
        if body.effective_start <= old.effective_start:
            raise ApiError(400, 'INVALID_DATE', 'Transfer must start after the existing allocation start.')
        from datetime import timedelta
        old.status, old.effective_end = 'ENDED', body.effective_start - timedelta(days=1)
        if old.project_id != project.id:
            old_membership = session.get(m.ProjectMember, (old.project_id, employee.id))
            if old_membership and old_membership.responsibility in {'Workforce','Field execution'}:
                old_membership.active = False
        session.flush()
    ended = session.scalar(select(func.max(m.WorkforceAssignment.effective_end)).where(m.WorkforceAssignment.employee_id == employee.id))
    if ended and body.effective_start <= ended:
        raise ApiError(400, 'OVERLAP', 'Allocation overlaps existing history.')
    new = m.WorkforceAssignment(id='WA-'+str(uuid4()), organization_id=user.organization_id, employee_id=employee.id, project_id=project.id, team_id=team.id,
        effective_start=body.effective_start, effective_end=None, status='ACTIVE', assigned_by=user.id)
    session.add(new)
    member = session.get(m.ProjectMember, (project.id, employee.id))
    if member:
        member.active = True
    else:
        session.add(m.ProjectMember(project_id=project.id, employee_id=employee.id, responsibility='Workforce', active=True))
    if not session.get(m.ProjectDepartment, (project.id, employee.department_id)):
        session.add(m.ProjectDepartment(project_id=project.id, department_id=employee.department_id))
    session.flush()
    append_audit(session, actor(user), 'Workforce transferred' if old else 'Workforce allocated', 'workforce_assignment', new.id,
        {'projectId': project.id, 'employeeId': employee.id, 'previousAssignmentId': old.id if old else None, 'teamId': team.id})
    return public(new)


def allocation_history(session, user, employee_id):
    admin(user)
    scoped(session, user, m.Employee, employee_id)
    return {'items': [public(r) for r in session.scalars(select(m.WorkforceAssignment).where(m.WorkforceAssignment.employee_id == employee_id).order_by(m.WorkforceAssignment.effective_start))]}


def end_allocation(session, user, identifier, end):
    admin(user)
    lock_organization(session, user.organization_id)
    row = scoped(session, user, m.WorkforceAssignment, identifier)
    if row.status != 'ACTIVE' or end < row.effective_start:
        raise ApiError(409, 'INVALID_ALLOCATION', 'Only an active allocation can be ended, on or after its start.')
    row.status, row.effective_end = 'ENDED', end
    append_audit(session, actor(user), 'Workforce allocation ended', 'workforce_assignment', row.id, {'projectId': row.project_id, 'employeeId': row.employee_id, 'effectiveEnd': end.isoformat()})
    return public(row)


def grant(session, user, body):
    admin(user)
    lock_organization(session, user.organization_id)
    account = scoped(session, user, m.User, body.user_id)
    if not account.active or account.role == 'WORKFORCE':
        raise ApiError(400, 'INVALID_GRANT', 'Capabilities require an active management account.')
    row = session.get(m.DepartmentGrant, (account.id, body.capability))
    if body.granted and not row:
        session.add(m.DepartmentGrant(user_id=account.id, capability=body.capability, granted_by=user.id))
    elif not body.granted and row:
        session.delete(row)
    append_audit(session, actor(user), 'Department capability changed', 'user', account.id, {'capability': body.capability, 'granted': body.granted})
    return {'ok': True}


def link(session, user, body):
    admin(user)
    lock_organization(session, user.organization_id)
    scoped(session, user, m.Project, body.project_id)
    if bool(body.employee_id) == bool(body.department_id):
        raise ApiError(400, 'INVALID_LINK', 'Choose exactly one employee or department.')
    model, target = (m.Employee, body.employee_id) if body.employee_id else (m.Department, body.department_id)
    row = scoped(session, user, model, target)
    if not row.active:
        raise ApiError(400, 'INACTIVE', 'Membership requires an active entity.')
    if body.employee_id:
        membership = session.get(m.ProjectMember, (body.project_id, target))
        if membership:
            membership.responsibility, membership.active = body.responsibility, True
        else:
            session.add(m.ProjectMember(project_id=body.project_id, employee_id=target, responsibility=body.responsibility, active=True))
    elif not session.get(m.ProjectDepartment, (body.project_id, target)):
        session.add(m.ProjectDepartment(project_id=body.project_id, department_id=target))
    append_audit(session, actor(user), 'Project membership changed', 'project', body.project_id, {'projectId': body.project_id, 'targetId': target})
    return {'ok': True}


def overview(session, user):
    admin(user)
    count = lambda model: session.scalar(select(func.count()).select_from(model).where(model.organization_id == user.organization_id))
    worker_count = session.scalar(select(func.count()).select_from(m.User).where(m.User.organization_id == user.organization_id, m.User.role == 'WORKFORCE'))
    allocated = session.scalar(select(func.count()).select_from(m.WorkforceAssignment).where(m.WorkforceAssignment.organization_id == user.organization_id, m.WorkforceAssignment.status == 'ACTIVE'))
    projects = session.scalars(select(m.Project).where(m.Project.organization_id == user.organization_id)).all()
    pm_projects = set(session.scalars(select(m.ProjectManagerAssignment.project_id).where(m.ProjectManagerAssignment.project_id.in_([p.id for p in projects]))))
    return {'dataLabel': session.get(m.Organization, user.organization_id).data_label,
        'projects': len(projects), 'employees': count(m.Employee), 'departments': count(m.Department), 'teams': count(m.Team),
        'workers': worker_count, 'allocatedWorkers': allocated, 'attention': [{'id': p.id, 'reason': 'PM not assigned' if p.id not in pm_projects else 'Recorded execution risk'} for p in projects if p.id not in pm_projects or p.status == 'At Risk']}
