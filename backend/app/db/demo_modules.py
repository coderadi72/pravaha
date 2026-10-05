"""Connected synthetic examples use the same services as authorized API requests."""
from backend.app import models as m
from backend.app.services import module_service as service


def seed_modules(session, prefix, location, employees):
    admin, pm, tl, hr = [session.get(m.User, f'{prefix}-{suffix}') for suffix in ('ADMIN','PM-01','TL-01-01','DEPT-HR')]
    project, team = f'{prefix}-P-01', f'{prefix}-T-01-01'
    worker = employees['WF-01-01-001']
    create = lambda key, values, user=admin: service.create(session, user, key, values)
    transition = lambda key, row, state, user=admin: service.transition(session, user, key, row['id'], state)
    client = create('clients', {'name':'Sample Infrastructure Client','sector':'Infrastructure — Demo Data'})
    create('contacts', {'client_id':client['id'], 'name':'Meera Sharma', 'email':'meera@demo.invalid'})
    opportunity = create('opportunities', {'client_id':client['id'], 'title':'Sample site expansion requirement'})
    transition('opportunities', opportunity, 'QUALIFIED')
    tender = create('tenders', {'opportunity_id':opportunity['id'], 'title':'Demo engineering tender'})
    transition('tenders', tender, 'SUBMITTED')
    proposal = create('proposals', {'tender_id':tender['id'], 'title':'Demo scope and delivery proposal', 'amount':2500000})
    transition('proposals', proposal, 'SUBMITTED')
    transition('proposals', proposal, 'ACCEPTED')
    transition('tenders', tender, 'AWARDED')
    transition('opportunities', opportunity, 'WON')
    create('contracts', {'proposal_id':proposal['id'], 'project_id':project, 'title':'Sample site expansion contract','amount':2500000})
    vendor = create('vendors', {'name':'Sample Industrial Supplies','email':'supply@demo.invalid'})
    material = create('materials', {'name':'Sample reinforcement steel','unit':'kg'})
    store = create('stores', {'name':'Sample site warehouse','location_id':location})
    request = create('material-requests', {'project_id':project,'team_id':team,'activity_id':f'{prefix}-A-01-01','material_id':material['id'],'quantity':100,'required_on':'2026-10-05'}, tl)
    transition('material-requests', request, 'APPROVED', pm)
    order = create('purchase-orders', {'request_id':request['id'],'vendor_id':vendor['id'],'quantity':100,'unit_price':60})
    create('receipts', {'order_id':order['id'],'store_id':store['id'],'quantity':100,'received_on':'2026-10-03'})
    create('movements', {'material_id':material['id'],'store_id':store['id'],'project_id':project,'team_id':team,'quantity':20,'occurred_on':'2026-10-04'})
    for kind, title in [('recruitment','Sample technician recruitment'),('attendance','Sample shift attendance'),('leave','Sample leave request'),('training','Sample induction training'),('performance','Sample confidential performance discussion'),('employee-relations','Sample confidential employee relations case'),('grievance','Sample confidential grievance'),('wellbeing','Sample confidential wellbeing support request')]:
        create('people', {'employee_id':worker,'project_id':project,'team_id':team,'kind':kind,'title':title,'narrative':'Synthetic example only. No real personal information.','start_on':'2026-10-04'}, hr)
    inspection = create('inspections', {'project_id':project,'team_id':team,'activity_id':f'{prefix}-A-01-01','title':'Sample civil hold-point inspection'}, tl)
    transition('inspections', inspection, 'FAILED', pm)
    issue = create('quality-issues', {'inspection_id':inspection['id'],'title':'Sample nonconformance','kind':'NCR'}, pm)
    action = create('corrective-actions', {'quality_issue_id':issue['id'],'assigned_employee_id':worker,'title':'Rework and reinspect sample joint','due_on':'2026-10-08'}, pm)
    observation = create('safety', {'project_id':project,'team_id':team,'kind':'OBSERVATION','title':'Sample work-zone barrier observation'}, tl)
    create('corrective-actions', {'safety_event_id':observation['id'],'assigned_employee_id':worker,'title':'Restore sample work-zone barriers','due_on':'2026-10-05'}, pm)
    return action
