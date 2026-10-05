"""Organization and departmental acceptance against isolated real PostgreSQL."""
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace
import pytest
from sqlalchemy import func, select, text
from backend.app import models as m
from backend.app.core.security import hash_password, verify_password
from backend.app.db.demo_organization import generate
from backend.app.services import module_service, organization_service
from backend.app.schemas.organization import AllocationRequest

ORG = 'ORG-OIL-DEMO'


def req(client, cookie, path, method='GET', body=None):
    client.cookies.clear()
    return client.request(method, path, headers={'Cookie':cookie}, json=body)


def create(client, cookie, resource, values):
    result = req(client, cookie, '/api/modules/'+resource, 'POST', {'values':values})
    assert result.status_code == 201, result.text
    return result.json()


def change(client, cookie, resource, row, target):
    return req(client, cookie, f"/api/modules/{resource}/{row['id']}/transition", 'POST', {'status':target})


@pytest.fixture
def organization(client, identities, session_factory):
    admin = identities['admin']
    department = create(client, admin, 'departments', {'name':'Civil','category':'Project & Operations'})
    with session_factory.begin() as session:
        for identifier, role in [('WF-TEST','WORKFORCE'),('HR-TEST','DEPARTMENT')]:
            session.add(m.User(id=identifier, organization_id=ORG, email=identifier.lower()+'@demo.invalid', login_id=identifier.lower(), full_name='Kavita Sharma', role=role, password_hash=hash_password('UniqueTestPass123!'), active=True, created_at=datetime.now(UTC)))
    employee = create(client, admin, 'employees', {'workforce_code':'WF-TEST','name':'Kavita Sharma','department_id':department['id'],'account_id':'WF-TEST','discipline':'Civil'})
    cookies = {}
    for identifier in ['WF-TEST','HR-TEST']:
        response = client.post('/api/auth/login', json={'email':identifier.lower(),'password':'UniqueTestPass123!'})
        assert response.status_code == 200, response.text
        cookies[identifier] = response.headers['set-cookie'].split(';')[0]
    return {'admin':admin, 'employee':employee, 'department':department, **cookies}


def allocation(client, organization, **overrides):
    return req(client, organization['admin'], '/api/organization/allocations', 'POST', {'employee_id':organization['employee']['id'],'project_id':'PRJ-001','team_id':'TEAM-PIP-A','effective_start':'2026-10-01', **overrides})


def test_workforce_authentication_login_ids_and_management_denial(client, identities, organization, session_factory):
    cookie = organization['WF-TEST']
    me = req(client, cookie, '/api/auth/me')
    assert me.status_code == 200
    assert me.json()['user']['role'] == 'WORKFORCE'
    assert 'password_hash' not in me.text
    paths = ['/api/workspace','/api/admin/system','/api/organization/context','/api/organization/overview','/api/organization/roster','/api/organization/lookups/projects','/api/team-leader/activities','/api/projects','/api/search?q=Kavita']
    for path in paths:
        assert req(client, cookie, path).status_code == 403, path
    for resource in module_service.RESOURCES:
        assert req(client, cookie, '/api/modules/'+resource).status_code == 403
        assert req(client, cookie, '/api/modules/'+resource, 'POST', {'values':{}}).status_code == 403
    assert req(client, cookie, '/api/reviews/FU-1043/confirm', 'POST', {}).status_code == 403
    assert req(client, cookie, '/api/auth/logout', 'POST', {}).status_code == 200
    assert req(client, cookie, '/api/auth/me').status_code == 401
    with session_factory() as session:
        assert verify_password('UniqueTestPass123!', session.get(m.User,'WF-TEST').password_hash)


@pytest.mark.parametrize('kind', ['grievance','wellbeing','employee-relations','performance'])
def test_sensitive_hr_requires_separate_grant_even_admin(client, identities, organization, kind, session_factory):
    admin, hr = organization['admin'], organization['HR-TEST']
    values = {'employee_id':organization['employee']['id'],'kind':kind,'title':'Private sample case','narrative':'DO-NOT-EXPOSE-CONFIDENTIAL','start_on':'2026-10-01'}
    assert req(client, admin, '/api/modules/people','POST',{'values':values}).status_code == 403
    for capability in ['people','hr-confidential']:
        assert req(client, admin, '/api/organization/grants','POST',{'user_id':'HR-TEST','capability':capability}).status_code == 200
    row = create(client, hr, 'people', values)
    assert 'narrative' not in row
    assert req(client, hr, f"/api/modules/people/{row['id']}").json()['narrative'] == values['narrative']
    for cookie in [admin, identities['pm'],identities['tl']]:
        listing = req(client, cookie, '/api/modules/people')
        assert listing.status_code == 200
        assert row['id'] not in listing.text
        assert req(client, cookie, f"/api/modules/people/{row['id']}").status_code == 404
        assert 'DO-NOT-EXPOSE' not in req(client, cookie, '/api/workspace').text
    with session_factory() as session:
        assert all('DO-NOT-EXPOSE' not in str(event.details_json) for event in session.scalars(select(m.AuditEvent)))
    assert req(client, admin, '/api/organization/grants','POST',{'user_id':'HR-TEST','capability':'hr-confidential','granted':False}).status_code == 200
    assert req(client, hr, f"/api/modules/people/{row['id']}").status_code == 404


def test_explicit_allocation_conflict_transfer_dates_and_history(client, identities, organization, session_factory):
    first = allocation(client, organization)
    assert first.status_code == 201, first.text
    assert allocation(client, organization).status_code == 409
    assert allocation(client, organization, team_id='TEAM-CIV-B').status_code == 400
    assert allocation(client, organization, transfer=True, effective_start='2026-09-30').status_code == 400
    second = allocation(client, organization, transfer=True, effective_start='2026-10-02')
    assert second.status_code == 201, second.text
    history = req(client, organization['admin'], '/api/organization/allocations/'+organization['employee']['id']).json()['items']
    assert [row['status'] for row in history] == ['ENDED','ACTIVE']
    assert history[0]['effective_end'] == '2026-10-01'
    assert len(req(client, identities['tl'], '/api/organization/roster').json()['items']) == 1
    assert req(client, identities['pm'], '/api/organization/allocations', 'POST', {}).status_code in {400,403}
    end = req(client, organization['admin'], f"/api/organization/allocations/{second.json()['id']}/end", 'POST', {'effective_end':'2026-10-03'})
    assert end.status_code == 200
    assert req(client, identities['tl'], '/api/organization/roster').json()['total'] == 0


def materials(client, admin):
    location = create(client, admin,'locations',{'name':'Sample store site'})
    store = create(client,admin,'stores',{'name':'Main store','location_id':location['id']})
    material = create(client,admin,'materials',{'name':'Cable','unit':'m'})
    vendor = create(client,admin,'vendors',{'name':'Sample Vendor'})
    request = create(client,admin,'material-requests',{'project_id':'PRJ-001','team_id':'TEAM-PIP-A','material_id':material['id'],'quantity':10,'required_on':'2026-10-04'})
    return store, material, vendor, request


def test_material_chain_bounds_stock_and_authorization(client, identities, organization):
    admin, pm, tl = organization['admin'], identities['pm'],identities['tl']
    store, material, vendor, request = materials(client,admin)
    order_values = {'request_id':request['id'],'vendor_id':vendor['id'],'quantity':10,'unit_price':50}
    assert req(client,admin,'/api/modules/purchase-orders','POST',{'values':order_values}).status_code == 409
    assert change(client,tl,'material-requests',request,'APPROVED').status_code == 403
    assert change(client,pm,'material-requests',request,'APPROVED').status_code == 200
    order = create(client,admin,'purchase-orders',order_values)
    receipt = {'order_id':order['id'],'store_id':store['id'],'quantity':11,'received_on':'2026-10-03'}
    assert req(client,admin,'/api/modules/receipts','POST',{'values':receipt}).status_code == 409
    receipt['quantity'] = 10
    create(client,admin,'receipts',receipt)
    issue = {'material_id':material['id'],'store_id':store['id'],'project_id':'PRJ-001','team_id':'TEAM-PIP-A','quantity':6,'occurred_on':'2026-10-04'}
    create(client,admin,'movements',issue)
    stock = req(client,admin,'/api/organization/stock').json()
    assert stock['total'] == 1 and stock['items'][0]['balance'] == 4
    assert req(client,tl,'/api/organization/stock').status_code == 403
    assert req(client,admin,'/api/modules/movements','POST',{'values':issue}).status_code == 409
    assert req(client,tl,'/api/modules/purchase-orders','POST',{'values':order_values}).status_code == 403
    assert req(client,pm,'/api/modules/material-requests?limit=101').status_code == 400


def test_team_creation_and_master_edit(client, identities, organization):
    admin = organization['admin']
    assert req(client,identities['pm'],'/api/organization/teams','POST',{'name':'Unauthorized','project_id':'PRJ-001'}).status_code == 403
    row = req(client,admin,'/api/organization/teams','POST',{'name':'New site team','project_id':'PRJ-001','site':'Sample site'})
    assert row.status_code == 201, row.text
    assert row.json()['id'] in next(p for p in req(client,admin,'/api/workspace').json()['data']['projects'] if p['id'] == 'PRJ-001')['teamIds']
    result = req(client,admin,f"/api/modules/employees/{organization['employee']['id']}",'PATCH',{'values':{'name':'Aditi Borah'}})
    assert result.status_code == 200, result.text
    assert result.json()['name'] == 'Aditi Borah'
    assert req(client,admin,f"/api/modules/employees/{organization['employee']['id']}",'PATCH',{'values':{'id':'FORGED'}}).status_code == 400


def test_commercial_traceability_and_invalid_transitions(client, identities):
    admin = identities['admin']
    client_row = create(client,admin,'clients',{'name':'Sample client'})
    contact = create(client,admin,'contacts',{'client_id':client_row['id'],'name':'Arjun Rao','email':'arjun@demo.invalid'})
    opportunity = create(client,admin,'opportunities',{'client_id':client_row['id'],'title':'Expansion'})
    tender = create(client,admin,'tenders',{'opportunity_id':opportunity['id'],'title':'Tender'})
    proposal = create(client,admin,'proposals',{'tender_id':tender['id'],'title':'Delivery proposal','amount':100})
    contract = {'proposal_id':proposal['id'],'project_id':'PRJ-001','title':'Contract','amount':100}
    assert req(client,admin,'/api/modules/contracts','POST',{'values':contract}).status_code == 409
    assert change(client,admin,'proposals',proposal,'ACCEPTED').status_code == 409
    assert change(client,admin,'proposals',proposal,'SUBMITTED').status_code == 200
    assert change(client,admin,'proposals',proposal,'ACCEPTED').status_code == 200
    row = create(client,admin,'contracts',contract)
    assert row['project_id'] == 'PRJ-001' and contact['client_id'] == client_row['id']
    assert req(client,identities['tl'],'/api/modules/clients').status_code == 403


@pytest.mark.parametrize('source', ['quality','hse'])
def test_assurance_actions_block_closure_and_scope(client, identities, organization, source):
    assert allocation(client,organization).status_code == 201
    pm, tl = identities['pm'], identities['tl']
    if source == 'quality':
        inspection = create(client,tl,'inspections',{'project_id':'PRJ-001','team_id':'TEAM-PIP-A','activity_id':'SA-1024','title':'Sample inspection'})
        assert change(client,pm,'inspections',inspection,'FAILED').status_code == 200
        row = create(client,pm,'quality-issues',{'inspection_id':inspection['id'],'title':'Sample NCR','kind':'NCR'})
        key, reference = 'quality-issues', 'quality_issue_id'
    else:
        row = create(client,tl,'safety',{'project_id':'PRJ-001','team_id':'TEAM-PIP-A','title':'Sample incident','kind':'INCIDENT'})
        key, reference = 'safety','safety_event_id'
    action = create(client,pm,'corrective-actions',{reference:row['id'],'assigned_employee_id':organization['employee']['id'],'title':'Sample corrective action','due_on':'2026-10-04'})
    assert change(client,pm,key,row,'CLOSED').status_code == 409
    assert change(client,pm,'corrective-actions',action,'VERIFIED').status_code == 409
    assert change(client,pm,'corrective-actions',action,'COMPLETED').status_code == 200
    assert change(client,pm,'corrective-actions',action,'VERIFIED').status_code == 200
    assert change(client,pm,key,row,'CLOSED').status_code == 200
    assert req(client,tl,'/api/modules/inspections','POST',{'values':{'project_id':'PRJ-002','team_id':'TEAM-CIV-B','title':'Forbidden'}}).status_code == 403


@pytest.mark.parametrize('kind,first,target', [('recruitment','OPEN','HIRED'),('attendance','RECORDED','CLOSED'),('leave','REQUESTED','APPROVED'),('training','PLANNED','COMPLETED')])
def test_people_workflows(client, identities, organization, kind, first, target):
    assert allocation(client,organization).status_code == 201
    row = create(client,organization['admin'],'people',{'employee_id':organization['employee']['id'],'project_id':'PRJ-001','team_id':'TEAM-PIP-A','kind':kind,'title':'Sample '+kind,'start_on':'2026-10-01'})
    assert row['status'] == first
    assert change(client,identities['pm'],'people',row,target).status_code == 200


@pytest.mark.parametrize('operation', ['create','transition','allocate','grant','membership','edit','receipt','issue'])
def test_phase10_real_database_audit_failure_is_atomic(client, identities, organization, session_factory, engine, operation):
    admin = organization['admin']
    row = create(client,admin,'opportunities',{'client_id':create(client,admin,'clients',{'name':'Sample'})['id'],'title':'Sample'})
    store, material, vendor, request = materials(client,admin)
    assert change(client,admin,'material-requests',request,'APPROVED').status_code == 200
    order = create(client,admin,'purchase-orders',{'request_id':request['id'],'vendor_id':vendor['id'],'quantity':10,'unit_price':2})
    if operation == 'issue': create(client,admin,'receipts',{'order_id':order['id'],'store_id':store['id'],'quantity':10,'received_on':'2026-10-01'})
    def snapshot():
        with session_factory() as session:
            return {table.name:session.execute(text(f'SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text),\'[]\'::jsonb) FROM "{table.name}" t')).scalar() for table in m.Organization.metadata.sorted_tables if table.name != 'alembic_version'}
    before = snapshot()
    with engine.begin() as connection:
        connection.execute(text("CREATE FUNCTION reject_phase10_audit() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'audit unavailable'; END $$"))
        connection.execute(text('CREATE TRIGGER reject_phase10_audit BEFORE INSERT ON audit_events FOR EACH ROW EXECUTE FUNCTION reject_phase10_audit()'))
    operations = {
        'create':('/api/modules/clients','POST',{'values':{'name':'Must roll back'}}),
        'transition':(f"/api/modules/opportunities/{row['id']}/transition",'POST',{'status':'QUALIFIED'}),
        'allocate':('/api/organization/allocations','POST',{'employee_id':organization['employee']['id'],'project_id':'PRJ-001','team_id':'TEAM-PIP-A','effective_start':'2026-10-01'}),
        'grant':('/api/organization/grants','POST',{'user_id':'HR-TEST','capability':'people'}),
        'membership':('/api/organization/memberships','POST',{'project_id':'PRJ-001','employee_id':organization['employee']['id']}),
        'edit':(f"/api/modules/employees/{organization['employee']['id']}",'PATCH',{'values':{'name':'Must roll back'}}),
        'receipt':('/api/modules/receipts','POST',{'values':{'order_id':order['id'],'store_id':store['id'],'quantity':10,'received_on':'2026-10-01'}}),
        'issue':('/api/modules/movements','POST',{'values':{'material_id':material['id'],'store_id':store['id'],'project_id':'PRJ-001','quantity':2,'occurred_on':'2026-10-01'}}),
    }
    path, method, body = operations[operation]
    result = req(client,admin,path,method,body)
    assert result.status_code == 500, result.text
    assert snapshot() == before


def test_generator_repeatability_unique_credentials_and_database_integrity(session_factory, credentials):
    with session_factory.begin() as session:
        from backend.app.db.seed import seed_database
        seed_database(session,credentials)
        existing = session.scalar(select(func.count()).select_from(m.User))
        report, initial = generate(session,'small-demo',2,2,2)
        assert report['roles']['WORKFORCE'] == 8
        assert report['teams'] == 4 and report['departments'] == 24
        for project in session.scalars(select(m.Project).where(m.Project.organization_id == report['organizationId'])):
            assert project.payload_json['location'] and project.payload_json['disciplines']
        for activity in session.scalars(select(m.ScheduleActivity).join(m.Project).where(m.Project.organization_id == report['organizationId'])):
            assert activity.payload_json['level'] == 'L6'
            assert activity.payload_json['progress'] == 0
        assert len({row['loginId'].lower() for row in initial}) == len(initial)
        assert len({row['initialPassword'] for row in initial}) == len(initial)
        workers = [r for r in initial if r['role'] == 'WORKFORCE']
        assert all(verify_password(r['initialPassword'],session.get(m.User,r['id']).password_hash) for r in workers)
        again, second = generate(session,'small-demo',2,2,2)
        assert not again['created'] and second == []
        assert session.scalar(select(func.count()).select_from(m.User).where(m.User.organization_id == ORG)) == existing
        assert session.scalar(select(func.count()).select_from(m.WorkforceAssignment).where(m.WorkforceAssignment.organization_id == report['organizationId'])) == 8
        with pytest.raises(ValueError,match='different dimensions'):
            generate(session,'small-demo',3,2,2)


def test_cross_organization_references_and_reporting_cycles(client, identities, organization, session_factory):
    with session_factory.begin() as session:
        session.add(m.Organization(id='OTHER',name='Other',data_label='Test',payload_json={}))
        session.flush()
        session.add(m.Department(id='OTHER-DEP',organization_id='OTHER',name='Other',category='Test',active=True))
    assert req(client,organization['admin'],'/api/modules/employees','POST',{'values':{'workforce_code':'BAD','name':'Bad link','department_id':'OTHER-DEP'}}).status_code == 404
    assert req(client,organization['admin'],f"/api/modules/employees/{organization['employee']['id']}",'PATCH',{'values':{'manager_id':organization['employee']['id']}}).status_code == 400
    assert req(client,identities['tl'],'/api/modules/people','POST',{'values':{'employee_id':organization['employee']['id'],'project_id':'PRJ-001','team_id':'TEAM-PIP-A','kind':'attendance','title':'Unallocated','start_on':'2026-10-01'}}).status_code == 403


def test_original_tl_keeps_own_reports_after_reassignment(client, identities, session_factory):
    response = req(client,identities['tl'],'/api/team-leader/field-updates','POST',{'description':'Spool erection completed for Line 247-XX','progress':20})
    assert response.status_code == 201, response.text
    identifier = response.json()['fieldUpdate']['id']
    # Moving a populated team is rejected. Replacing its leader preserves original submitter history.
    assert req(client,identities['admin'],'/api/admin/teams/TEAM-PIP-A/assignment','PATCH',{'projectId':'PRJ-002','assigned':True}).status_code == 409
    with session_factory.begin() as session:
        session.add(m.User(id='TL-NEW',organization_id=ORG,email='tl-new@demo.invalid',full_name='New Leader',role='TEAM_LEADER',password_hash=hash_password('NewLeaderPass123!'),active=True,created_at=datetime.now(UTC)))
    assert req(client,identities['admin'],'/api/admin/teams/TEAM-PIP-A/leader','PATCH',{'teamLeaderId':'TL-NEW'}).status_code == 200
    history = req(client,identities['tl'],'/api/team-leader/field-updates').json()['fieldUpdates']
    assert identifier in {row['id'] for row in history}
    assert req(client,identities['tl'],f'/api/team-leader/field-updates/{identifier}','PATCH',{'description':'Attempt edit'}).status_code == 403
