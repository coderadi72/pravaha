"""Typed departmental records; explicit workflows and transactional audit."""
from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from sqlalchemy import Boolean, Date, Numeric, func, select
from backend.app import models as m
from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor
from backend.app.core.organization_permissions import permitted, project_ids, team_ids
from backend.app.db.organization_repository import RESOURCES, page, public
from backend.app.db.repository import append_audit, lock_organization
from backend.app.services.organization_service import scoped

PRIVATE_KINDS = {'grievance','wellbeing','employee-relations','performance'}
PEOPLE_KINDS = PRIVATE_KINDS | {'recruitment','attendance','leave','training'}
REFERENCES = {'department_id': m.Department, 'unit_id': m.DepartmentUnit, 'location_id': m.Location,
    'designation_id': m.Designation, 'manager_id': m.Employee, 'account_id': m.User, 'employee_id': m.Employee,
    'client_id': m.Client, 'opportunity_id': m.Opportunity, 'tender_id': m.Tender, 'proposal_id': m.Proposal,
    'project_id': m.Project, 'team_id': m.Team, 'material_id': m.Material, 'vendor_id': m.Vendor,
    'store_id': m.Store, 'request_id': m.MaterialRequest, 'order_id': m.PurchaseOrder,
    'inspection_id': m.Inspection, 'quality_issue_id': m.QualityIssue, 'safety_event_id': m.SafetyEvent,
    'assigned_employee_id': m.Employee}


def resource(key):
    if key not in RESOURCES:
        raise ApiError(404, 'NOT_FOUND', 'Unknown organization resource.')
    return RESOURCES[key]


def project_scope(model):
    if 'project_id' in model.__table__.c:
        return model.project_id
    if model is m.QualityIssue:
        return select(m.Inspection.project_id).where(m.Inspection.id == model.inspection_id).scalar_subquery()
    if model is m.PurchaseOrder:
        return select(m.MaterialRequest.project_id).where(m.MaterialRequest.id == model.request_id).scalar_subquery()
    if model is m.GoodsReceipt:
        return select(m.MaterialRequest.project_id).join(m.PurchaseOrder, m.PurchaseOrder.request_id == m.MaterialRequest.id).where(m.PurchaseOrder.id == model.order_id).scalar_subquery()
    if model is m.CorrectiveAction:
        return func.coalesce(select(m.SafetyEvent.project_id).where(m.SafetyEvent.id == model.safety_event_id).scalar_subquery(),
            select(m.Inspection.project_id).join(m.QualityIssue, m.QualityIssue.inspection_id == m.Inspection.id).where(m.QualityIssue.id == model.quality_issue_id).scalar_subquery())
    return None


def team_scope(model):
    if 'team_id' in model.__table__.c:
        return model.team_id
    if model is m.QualityIssue:
        return select(m.Inspection.team_id).where(m.Inspection.id == model.inspection_id).scalar_subquery()
    if model is m.PurchaseOrder:
        return select(m.MaterialRequest.team_id).where(m.MaterialRequest.id == model.request_id).scalar_subquery()
    if model is m.GoodsReceipt:
        return select(m.MaterialRequest.team_id).join(m.PurchaseOrder, m.PurchaseOrder.request_id == m.MaterialRequest.id).where(m.PurchaseOrder.id == model.order_id).scalar_subquery()
    if model is m.CorrectiveAction:
        return func.coalesce(select(m.SafetyEvent.team_id).where(m.SafetyEvent.id == model.safety_event_id).scalar_subquery(),
            select(m.Inspection.team_id).join(m.QualityIssue, m.QualityIssue.inspection_id == m.Inspection.id).where(m.QualityIssue.id == model.quality_issue_id).scalar_subquery())
    return None


def filters_for(session, user, key):
    r = resource(key)
    if user.role == 'WORKFORCE':
        raise ApiError(403, 'FORBIDDEN', 'Workforce accounts cannot access management records.')
    filters = [r.model.organization_id == user.organization_id]
    if key == 'people' and not permitted(session, user, 'people', True):
        filters.append(m.PeopleRecord.confidential.is_(False))
    if permitted(session, user, r.capability):
        if key == 'corrective-actions' and user.role != 'ADMIN' and not permitted(session, user, 'hse'):
            filters.append(m.CorrectiveAction.quality_issue_id.is_not(None))
        return filters
    if key == 'corrective-actions' and permitted(session, user, 'hse'):
        filters.append(m.CorrectiveAction.safety_event_id.is_not(None))
        return filters
    if user.role not in {'PROJECT_MANAGER','TEAM_LEADER'}:
        raise ApiError(403, 'FORBIDDEN', 'This module is not authorized for the account.')
    if key in {'materials','vendors','stores','departments','units','locations','skills','designations'}:
        return filters
    column = project_scope(r.model)
    if column is None:
        raise ApiError(403, 'FORBIDDEN', 'This resource requires departmental authorization.')
    filters.append(column.in_(project_ids(session, user)))
    if user.role == 'TEAM_LEADER':
        team_column = team_scope(r.model)
        if team_column is None:
            raise ApiError(403, 'FORBIDDEN', 'This resource requires project review permissions.')
        filters.append(team_column.in_(team_ids(user)))
        if key == 'people':
            filters.append(m.PeopleRecord.kind == 'attendance')
    return filters


def list_records(session, user, key, q, limit, offset):
    if key == 'employees':
        if user.role != 'ADMIN':
            raise ApiError(403, 'FORBIDDEN', 'Employee administration requires Admin access.')
        from backend.app.services.organization_service import roster
        return roster(session, user, q, limit, offset)
    r = resource(key)
    rows, total = page(session, r.model, filters_for(session, user, key), q, limit, offset)
    return {'items': [public(row) for row in rows], 'total': total, 'limit': limit, 'offset': offset}


def accessible(session, user, key, identifier):
    row = session.scalar(select(resource(key).model).where(resource(key).model.id == identifier, *filters_for(session, user, key)))
    if row is None:
        raise ApiError(404, 'NOT_FOUND', 'Record not found or not accessible.')
    return row


def detail(session, user, key, identifier):
    row = accessible(session, user, key, identifier)
    return public(row, narrative=key == 'people')


def values_for(session, user, r, values):
    if set(values) - set(r.fields):
        raise ApiError(400, 'INVALID_INPUT', 'Unknown or protected fields were supplied.')
    result = {}
    for field in r.fields:
        column = r.model.__table__.c[field]
        value = values.get(field)
        if value in (None, ''):
            if not column.nullable and column.default is None:
                raise ApiError(400, 'INVALID_INPUT', f'{field} is required.')
            if column.nullable:
                result[field] = None
            continue
        try:
            if isinstance(column.type, Boolean):
                if not isinstance(value, bool): raise ValueError()
            elif isinstance(column.type, Date):
                value = date.fromisoformat(str(value))
            elif isinstance(column.type, Numeric):
                value = Decimal(str(value))
                if not value.is_finite() or value < 0: raise ValueError()
            else:
                if not isinstance(value, str) or not value.strip() or len(value) > (2000 if field == 'narrative' else 500): raise ValueError()
                value = value.strip()
        except (ValueError, InvalidOperation):
            raise ApiError(400, 'INVALID_INPUT', f'{field} has an invalid value.') from None
        if field in REFERENCES:
            reference = scoped(session, user, REFERENCES[field], value)
            if hasattr(reference, 'active') and not reference.active:
                raise ApiError(400, 'INACTIVE', 'Cannot link inactive records.')
        result[field] = value
    project_id, team_id = result.get('project_id'), result.get('team_id')
    if team_id and session.get(m.Team, team_id).project_id != project_id:
        raise ApiError(400, 'INVALID_LINK', 'Team and project must agree.')
    if result.get('activity_id'):
        activity = session.get(m.ScheduleActivity, result['activity_id'])
        if not activity or activity.project_id != project_id:
            raise ApiError(400, 'INVALID_LINK', 'Activity and project must agree.')
        if user.role == 'TEAM_LEADER' and activity.team_id != team_id:
            raise ApiError(403, 'FORBIDDEN', 'Activity does not belong to this team.')
    return result


def create(session, user, key, values):
    r = resource(key)
    lock_organization(session, user.organization_id)
    allowed = permitted(session, user, r.capability)
    if key == 'corrective-actions' and values.get('safety_event_id'):
        allowed = permitted(session, user, 'hse')
    if not allowed and not (user.role in {'PROJECT_MANAGER','TEAM_LEADER'} and key in {'material-requests','inspections','safety','people'}) and not (user.role == 'PROJECT_MANAGER' and key in {'quality-issues','corrective-actions'}):
        raise ApiError(403, 'FORBIDDEN', 'Creation requires authorized departmental responsibility.')
    data = values_for(session, user, r, values)
    if key == 'quality-issues':
        source_project = session.get(m.Inspection, data['inspection_id']).project_id
    elif key == 'corrective-actions':
        if bool(data.get('quality_issue_id')) == bool(data.get('safety_event_id')):
            raise ApiError(400, 'INVALID_LINK', 'Choose exactly one quality or safety source.')
        source_project = session.get(m.SafetyEvent, data['safety_event_id']).project_id if data.get('safety_event_id') else session.get(m.Inspection, session.get(m.QualityIssue, data['quality_issue_id']).inspection_id).project_id
        if not session.get(m.ProjectMember, (source_project, data['assigned_employee_id'])):
            raise ApiError(400, 'INVALID_LINK', 'Corrective responsibility requires a member of the source project.')
    else:
        source_project = data.get('project_id')
    if user.role in {'PROJECT_MANAGER','TEAM_LEADER'} and not allowed:
        project_id = source_project
        if project_id not in session.scalars(project_ids(session, user)):
            raise ApiError(403, 'FORBIDDEN', 'Project is not assigned to this account.')
        if user.role == 'TEAM_LEADER' and data.get('team_id') not in session.scalars(team_ids(user)):
            raise ApiError(403, 'FORBIDDEN', 'Team is not assigned to this account.')
    if key == 'employees':
        if data.get('unit_id') and session.get(m.DepartmentUnit, data['unit_id']).department_id != data['department_id']:
            raise ApiError(400, 'INVALID_LINK', 'Unit must belong to the employee department.')
    if key == 'people':
        kind = data['kind']
        if kind not in PEOPLE_KINDS or (kind != 'recruitment' and not data.get('employee_id')):
            raise ApiError(400, 'INVALID_INPUT', 'People kind and employee are invalid.')
        if kind in PRIVATE_KINDS and not permitted(session, user, 'people', True):
            raise ApiError(403, 'FORBIDDEN', 'Confidential HR access must be explicitly granted.')
        if user.role == 'PROJECT_MANAGER' and not allowed and data.get('employee_id') and not session.scalar(select(m.ProjectMember.employee_id).where(m.ProjectMember.project_id == data['project_id'], m.ProjectMember.employee_id == data['employee_id'], m.ProjectMember.active.is_(True))):
            raise ApiError(403, 'FORBIDDEN', 'Employee must be a member of this project.')
        if user.role == 'TEAM_LEADER' and (kind != 'attendance' or not session.scalar(select(m.WorkforceAssignment.id).where(m.WorkforceAssignment.employee_id == data['employee_id'], m.WorkforceAssignment.team_id == data['team_id'], m.WorkforceAssignment.status == 'ACTIVE'))):
            raise ApiError(403, 'FORBIDDEN', 'TL attendance requires an employee currently on the same team.')
        if data.get('end_on') and data['end_on'] < data['start_on']:
            raise ApiError(400, 'INVALID_DATE', 'End date precedes start date.')
        data['confidential'] = kind in PRIVATE_KINDS
        data['status'] = {'leave':'REQUESTED','training':'PLANNED','attendance':'RECORDED'}.get(kind, 'OPEN')
    if key == 'contracts' and session.get(m.Proposal, data['proposal_id']).status != 'ACCEPTED':
        raise ApiError(409, 'INVALID_STATE', 'A contract requires an accepted proposal.')
    if key == 'material-requests':
        if data['quantity'] <= 0: raise ApiError(400, 'INVALID_INPUT', 'Quantity must be positive.')
        data['requested_by'] = user.id
    if key == 'purchase-orders':
        request = session.get(m.MaterialRequest, data['request_id'])
        if request.status != 'APPROVED' or data['quantity'] != request.quantity:
            raise ApiError(409, 'INVALID_STATE', 'Order requires an approved request and its exact quantity.')
    if key == 'receipts':
        from backend.app.services.material_service import receive
        return receive(session, user, data)
    if key == 'movements':
        from backend.app.services.material_service import issue
        return issue(session, user, data)
    if key in {'quality-issues','safety'} and data.get('kind','ISSUE') not in ({'ISSUE','NCR'} if key == 'quality-issues' else {'OBSERVATION','INCIDENT'}):
        raise ApiError(400, 'INVALID_INPUT', 'Invalid assurance record kind.')
    if key == 'corrective-actions' and bool(data.get('quality_issue_id')) == bool(data.get('safety_event_id')):
        raise ApiError(400, 'INVALID_LINK', 'Choose exactly one quality or safety source.')
    if r.initial:
        data['status'] = r.initial
    row = r.model(id=key.upper()+'-'+str(uuid4()), organization_id=user.organization_id, **data)
    session.add(row)
    session.flush()
    append_audit(session, actor(user), 'Organization record created', key, row.id, {'kind': key, 'projectId': data.get('project_id'), 'status': getattr(row, 'status', None)})
    return public(row)


def update_master(session, user, key, identifier, values):
    if user.role != 'ADMIN' or key not in {'employees','departments','units','locations','designations','skills'}:
        raise ApiError(403, 'FORBIDDEN', 'Only Admin can edit organization master records.')
    lock_organization(session, user.organization_id)
    r = resource(key)
    row = scoped(session, user, r.model, identifier)
    data = values_for(session, user, r, {field: values.get(field, getattr(row, field)) for field in r.fields})
    if set(values) - set(r.fields):
        raise ApiError(400, 'INVALID_INPUT', 'Unknown or protected fields were supplied.')
    if key == 'employees':
        if data.get('unit_id') and session.get(m.DepartmentUnit, data['unit_id']).department_id != data['department_id']:
            raise ApiError(400, 'INVALID_LINK', 'Unit must belong to the employee department.')
        manager_id, seen = data.get('manager_id'), {identifier}
        while manager_id:
            if manager_id in seen:
                raise ApiError(400, 'REPORTING_CYCLE', 'Reporting relationships cannot contain cycles.')
            seen.add(manager_id)
            manager_id = session.get(m.Employee, manager_id).manager_id
        if not data['active'] and session.scalar(select(m.WorkforceAssignment.id).where(m.WorkforceAssignment.employee_id == row.id, m.WorkforceAssignment.status == 'ACTIVE')):
            raise ApiError(409, 'ACTIVE_ALLOCATION', 'End the active workforce allocation before disabling an employee.')
    elif data.get('active') is False:
        employee_field = {'departments':'department_id','units':'unit_id','locations':'location_id','designations':'designation_id'}.get(key)
        if employee_field and session.scalar(select(m.Employee.id).where(getattr(m.Employee, employee_field) == row.id, m.Employee.active.is_(True)).limit(1)):
            raise ApiError(409, 'ACTIVE_EMPLOYEES', 'Move or disable active employees before disabling their organization master record.')
    for field, value in data.items():
        setattr(row, field, value)
    session.flush()
    append_audit(session, actor(user), 'Organization master updated', key, row.id, {'fields': sorted(values)})
    return public(row)


def transition(session, user, key, identifier, target):
    r = resource(key)
    lock_organization(session, user.organization_id)
    row = accessible(session, user, key, identifier)
    capability = 'hse' if key == 'corrective-actions' and row.safety_event_id else r.capability
    if user.role == 'TEAM_LEADER' or not (permitted(session, user, capability) or user.role == 'PROJECT_MANAGER'):
        raise ApiError(403, 'FORBIDDEN', 'Transitions require an authorized reviewer.')
    if not r.transitions or target not in r.transitions.get(row.status, []):
        raise ApiError(409, 'INVALID_STATE', 'This status transition is not allowed.')
    if key == 'people' and target == 'HIRED' and row.kind != 'recruitment':
        raise ApiError(409, 'INVALID_STATE', 'Only recruitment records can transition to hired.')
    if key == 'people' and row.confidential and not permitted(session, user, 'people', True):
        raise ApiError(403, 'FORBIDDEN', 'Confidential HR access is required.')
    if key in {'quality-issues','safety'} and target == 'CLOSED':
        column = m.CorrectiveAction.quality_issue_id if key == 'quality-issues' else m.CorrectiveAction.safety_event_id
        if session.scalar(select(func.count()).select_from(m.CorrectiveAction).where(column == row.id, m.CorrectiveAction.status != 'VERIFIED')):
            raise ApiError(409, 'OPEN_ACTIONS', 'Verify all corrective actions before closing this source.')
    old = row.status
    row.status = target
    append_audit(session, actor(user), 'Department workflow transitioned', key, row.id, {'previous': old, 'status': target, 'projectId': getattr(row, 'project_id', None)})
    return public(row)
