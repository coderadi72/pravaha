"""Registry of normalized master/module records, and SQL-only paging."""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, cast, func, or_, select
from backend.app import models as m


@dataclass(frozen=True)
class Resource:
    model: type
    capability: str
    fields: tuple[str, ...]
    initial: str | None = None
    transitions: dict | None = None


RESOURCES = {
    'departments': Resource(m.Department, 'organization', ('name','category','active')),
    'units': Resource(m.DepartmentUnit, 'organization', ('name','department_id','location_id','active')),
    'locations': Resource(m.Location, 'organization', ('name','address','active')),
    'designations': Resource(m.Designation, 'organization', ('name','active')),
    'skills': Resource(m.Skill, 'organization', ('name','discipline','active')),
    'employees': Resource(m.Employee, 'organization', ('workforce_code','name','department_id','unit_id','designation_id','location_id','manager_id','account_id','discipline','active')),
    'clients': Resource(m.Client, 'business', ('name','sector')),
    'contacts': Resource(m.Contact, 'business', ('client_id','name','email')),
    'opportunities': Resource(m.Opportunity, 'business', ('client_id','title'), 'OPEN', {'OPEN':['QUALIFIED','LOST'], 'QUALIFIED':['WON','LOST']}),
    'tenders': Resource(m.Tender, 'business', ('opportunity_id','title'), 'OPEN', {'OPEN':['SUBMITTED','WITHDRAWN'], 'SUBMITTED':['AWARDED','LOST']}),
    'proposals': Resource(m.Proposal, 'business', ('tender_id','title','amount'), 'DRAFT', {'DRAFT':['SUBMITTED'], 'SUBMITTED':['ACCEPTED','REJECTED']}),
    'contracts': Resource(m.CommercialContract, 'business', ('proposal_id','project_id','title','amount'), 'ACTIVE', {'ACTIVE':['COMPLETED','TERMINATED']}),
    'vendors': Resource(m.Vendor, 'materials', ('name','email')),
    'materials': Resource(m.Material, 'materials', ('name','unit')),
    'stores': Resource(m.Store, 'materials', ('name','location_id')),
    'material-requests': Resource(m.MaterialRequest, 'materials', ('project_id','team_id','activity_id','material_id','quantity','required_on'), 'REQUESTED', {'REQUESTED':['APPROVED','REJECTED']}),
    'purchase-orders': Resource(m.PurchaseOrder, 'materials', ('request_id','vendor_id','quantity','unit_price'), 'ORDERED', {}),
    'receipts': Resource(m.GoodsReceipt, 'materials', ('order_id','store_id','quantity','received_on')),
    'movements': Resource(m.MaterialMovement, 'materials', ('material_id','store_id','project_id','team_id','quantity','occurred_on')),
    'people': Resource(m.PeopleRecord, 'people', ('employee_id','project_id','team_id','kind','title','narrative','start_on','end_on'), None,
        {'REQUESTED':['APPROVED','REJECTED'], 'PLANNED':['COMPLETED'], 'OPEN':['CLOSED','HIRED'], 'RECORDED':['CLOSED']}),
    'inspections': Resource(m.Inspection, 'quality', ('project_id','team_id','activity_id','title'), 'PLANNED', {'PLANNED':['PASSED','FAILED']}),
    'quality-issues': Resource(m.QualityIssue, 'quality', ('inspection_id','title','kind'), 'OPEN', {'OPEN':['CLOSED']}),
    'safety': Resource(m.SafetyEvent, 'hse', ('project_id','team_id','title','kind'), 'OPEN', {'OPEN':['CLOSED']}),
    'corrective-actions': Resource(m.CorrectiveAction, 'quality', ('quality_issue_id','safety_event_id','assigned_employee_id','title','due_on'), 'OPEN', {'OPEN':['COMPLETED'], 'COMPLETED':['VERIFIED']}),
}


def public(row, narrative=False):
    result = {}
    for column in row.__table__.columns:
        if column.name in {'organization_id','password_hash','narrative'} and not (narrative and column.name == 'narrative'):
            continue
        value = getattr(row, column.name)
        result[column.name] = value.isoformat() if isinstance(value, (date, datetime)) else float(value) if isinstance(value, Decimal) else value
    return result


def page(session, model, filters, query='', limit=25, offset=0):
    statement = select(model).where(*filters)
    if query:
        pattern = '%' + query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_') + '%'
        columns = [column for column in model.__table__.columns if column.name in {'id','name','title','workforce_code','email','full_name','login_id'}]
        statement = statement.where(or_(*[cast(column, String).ilike(pattern, escape='\\') for column in columns]))
    total = session.scalar(select(func.count()).select_from(statement.subquery()))
    return list(session.scalars(statement.order_by(model.id).limit(limit).offset(offset))), total
