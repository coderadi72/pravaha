"""Bounded synthetic organization generator; never touches another organization."""
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime
import secrets
from sqlalchemy import func, select, text
from backend.app import models as m
from backend.app.core.security import hash_password, is_valid_password
from backend.app.core.permissions import actor
from backend.app.db.repository import append_audit

DEPARTMENTS = {
    'Business & Corporate': ['Marketing & Business Development','Finance & Accounts','Contracts & Commercial','Legal & Compliance'],
    'Project & Operations': ['Project Management','Planning / Project Controls','Civil','Mechanical','Piping','Electrical','Instrumentation & Controls','Structural','Survey','Commissioning','Maintenance','QA/QC','HSE'],
    'Supply Chain': ['Procurement','Materials','Warehouse / Stores','Logistics'],
    'People & Technology': ['HR','Training & Development','IT / Digital'],
}
FIRST = ['Aarav','Aditi','Akash','Ananya','Anil','Anjali','Arjun','Bhavna','Deepak','Divya','Farhan','Gautam','Harini','Ishaan','Kavita','Kiran','Lakshmi','Manoj','Meera','Nandini','Neha','Nikhil','Pallavi','Pooja','Pranav','Priya','Rahul','Rajesh','Rekha','Rohan','Sanjay','Shreya','Siddharth','Sneha','Sunil','Surya','Tanvi','Varun','Vikram','Zoya']
LAST = ['Borah','Chakraborty','Das','Gogoi','Hazarika','Sharma','Singh','Verma','Gupta','Yadav','Mehta','Patel','Shah','Nair','Menon','Iyer','Rao','Reddy','Naidu','Kumar','Joshi','Deshmukh','Kulkarni','Mukherjee','Banerjee','Sen','Roy','Saha','Khan','Ahmed','Ali','Thomas','Mathew','Joseph','Dutta','Saikia','Ghosh','Bose','Pandey','Tripathi','Mishra','Chauhan','Thakur','Saxena','Bhat','Kapoor','Malhotra','Sethi','Dubey','Soni','Sinha','Pillai','Prasad','Shetty','Hegde','Barman','Baruah','Mahanta','Talukdar','Deka','Biswas','Mondal','Pal','Choudhury','Adhikari','Behera','Sahoo','Nayak','Patnaik','Mohanty','Jain','Agarwal','Bansal','Goel','Chawla','Arora','Dhillon','Gill','Sandhu','Bedi','Kaur','Puri','Bajaj','Batra','Wadhwa','Grover','Kohli','Khanna','Suri','Dhingra','Chandra','Rajan','Narayanan','Balakrishnan','Srinivasan','Venkatesh','Krishnan','Subramanian','Sundaram','Ramakrishnan']
DISCIPLINES = ['Civil','Mechanical','Piping','Electrical','Instrumentation & Controls','Structural','Survey','Commissioning']


def password():
    while True:
        value = secrets.token_urlsafe(24)
        if is_valid_password(value):
            return value


def totals(session, organization_id):
    count = lambda model: session.scalar(select(func.count()).select_from(model).where(model.organization_id == organization_id))
    roles = dict(session.execute(select(m.User.role, func.count()).where(m.User.organization_id == organization_id).group_by(m.User.role)).all())
    return {'organizationId': organization_id, 'roles': roles, 'employees': count(m.Employee), 'projects': count(m.Project), 'teams': count(m.Team), 'allocations': count(m.WorkforceAssignment), 'departments': count(m.Department)}


def generate(session, namespace, pms=20, teams_per_pm=8, workers_per_team=20):
    """Caller owns transaction and restricted credential output. Returns secrets only to CLI."""
    if not 1 <= pms <= 25 or not 1 <= teams_per_pm <= 9 or not 1 <= workers_per_team <= 30:
        raise ValueError('Generator bounds: PM 1..25, teams per PM 1..9, workers per team 1..30.')
    import re
    if not re.fullmatch('[a-z][a-z0-9-]{2,19}', namespace):
        raise ValueError('Namespace must be 3..20 lowercase letters/digits/hyphens.')
    org_id, prefix = 'DEMO-'+namespace, namespace.upper()
    session.execute(text('SELECT pg_advisory_xact_lock(hashtext(:key))'), {'key': org_id})
    expected = {'pms':pms, 'teamsPerPm':teams_per_pm, 'workersPerTeam':workers_per_team}
    existing = session.get(m.Organization, org_id)
    if existing:
        if existing.payload_json.get('generator') != expected:
            raise ValueError('Namespace already exists with different dimensions; choose another namespace.')
        report = totals(session, org_id)
        if report['roles'].get('WORKFORCE') != pms*teams_per_pm*workers_per_team or report['allocations'] != pms*teams_per_pm*workers_per_team:
            raise ValueError('Existing dataset changed; refusing destructive reseeding.')
        return {'created':False, **report}, []
    session.add(m.Organization(id=org_id, name='PRAVAHA '+namespace+' demonstration organization', data_label='Demo Data — synthetic organization', payload_json={'id':org_id, 'name':'PRAVAHA '+namespace+' demonstration organization', 'dataLabel':'Demo Data — synthetic organization', 'generator':expected}))
    session.flush()
    departments, units, locations, designations, skills = {}, {}, [], {}, {}
    for i, city in enumerate(['Duliajan','Guwahati','Jorhat','Dibrugarh']):
        identifier = f'{prefix}-LOC-{i+1}'
        locations.append(identifier)
        session.add(m.Location(id=identifier, organization_id=org_id, name=city+' sample site', address='Synthetic site location', active=True))
    for i, name in enumerate(['Organization Administrator','Project Manager','Team Leader','Skilled Technician','Department Lead']):
        identifier = f'{prefix}-DES-{i+1}'
        designations[name] = identifier
        session.add(m.Designation(id=identifier, organization_id=org_id, name=name, active=True))
    session.flush()
    for i, (category, name) in enumerate((c,n) for c,names in DEPARTMENTS.items() for n in names):
        identifier, unit = f'{prefix}-DEP-{i+1:02}', f'{prefix}-UNIT-{i+1:02}'
        departments[name], units[name] = identifier, unit
        session.add(m.Department(id=identifier, organization_id=org_id, name=name, category=category, active=True))
    session.flush()
    for name, identifier in units.items():
        session.add(m.DepartmentUnit(id=identifier, organization_id=org_id, name=name+' delivery unit', department_id=departments[name], location_id=locations[0], active=True))
    for i, discipline in enumerate(DISCIPLINES):
        identifier = f'{prefix}-SK-{i+1}'
        skills[discipline] = identifier
        session.add(m.Skill(id=identifier, organization_id=org_id, name=discipline+' field execution', discipline=discipline, active=True))
    accounts = [('ADMIN', 'ADMIN', 'Organization Administrator', 'Project Management')]
    accounts += [(f'PM-{p+1:02}', 'PROJECT_MANAGER', 'Project Manager', 'Project Management') for p in range(pms)]
    accounts += [(f'TL-{p+1:02}-{t+1:02}', 'TEAM_LEADER', 'Team Leader', DISCIPLINES[t % len(DISCIPLINES)]) for p in range(pms) for t in range(teams_per_pm)]
    accounts += [(f'WF-{p+1:02}-{t+1:02}-{w+1:03}', 'WORKFORCE', 'Skilled Technician', DISCIPLINES[t % len(DISCIPLINES)]) for p in range(pms) for t in range(teams_per_pm) for w in range(workers_per_team)]
    support = [('BUSINESS','Marketing & Business Development'),('MATERIALS','Procurement'),('HR','HR'),('QUALITY','QA/QC'),('HSE','HSE')]
    accounts += [(f'DEPT-{key}', 'DEPARTMENT', 'Department Lead', department) for key,department in support]
    secrets_list = [password() for _ in accounts]
    with ThreadPoolExecutor(max_workers=4) as executor:
        hashes = list(executor.map(hash_password, secrets_list))
    export, employee_ids = [], {}
    now = datetime.now(UTC)
    for i, ((suffix, role, designation, department), initial, hashed) in enumerate(zip(accounts, secrets_list, hashes)):
        identifier = f'{prefix}-{suffix}'
        login = namespace+'.'+suffix.lower()
        name = FIRST[i % len(FIRST)]+' '+LAST[(i // len(FIRST)) % len(LAST)]
        session.add(m.User(id=identifier, organization_id=org_id, email=login+'@demo.invalid', login_id=login, full_name=name, role=role, password_hash=hashed, active=True, created_at=now))
        export.append({'id':identifier, 'name':name, 'role':role, 'loginId':login, 'initialPassword':initial})
        employee_ids[suffix] = 'EMP-'+identifier
    session.flush()
    for suffix, role, designation, department in accounts:
        account = session.get(m.User, f'{prefix}-{suffix}')
        manager = None if role == 'ADMIN' else employee_ids['ADMIN']
        if role == 'TEAM_LEADER': manager = employee_ids['PM-'+suffix.split('-')[1]]
        if role == 'WORKFORCE': manager = employee_ids['TL-'+'-'.join(suffix.split('-')[1:3])]
        session.add(m.Employee(id=employee_ids[suffix], organization_id=org_id, workforce_code=f'{prefix}-{suffix}', name=account.full_name,
            department_id=departments[department], unit_id=units[department], designation_id=designations[designation], location_id=locations[0], manager_id=manager, account_id=account.id, discipline=department if department in DISCIPLINES else '', active=True))
        # Insert managers before subordinates: SQLAlchemy has no relationships to infer this order.
        if role in {'ADMIN','PROJECT_MANAGER','TEAM_LEADER'}: session.flush()
    session.flush()
    for key, _ in support:
        capability = {'HR':'people'}.get(key, key.lower())
        session.add(m.DepartmentGrant(user_id=f'{prefix}-DEPT-{key}', capability=capability, granted_by=f'{prefix}-ADMIN'))
    session.add(m.DepartmentGrant(user_id=f'{prefix}-DEPT-HR', capability='hr-confidential', granted_by=f'{prefix}-ADMIN'))
    start = date(2026,10,1)
    for p in range(pms):
        project_id = f'{prefix}-P-{p+1:02}'
        pm_id = f'{prefix}-PM-{p+1:02}'
        team_ids = [f'{prefix}-T-{p+1:02}-{t+1:02}' for t in range(teams_per_pm)]
        payload = {'id':project_id, 'name':f'{["Pipeline","Processing Facility","Site Infrastructure","Commissioning"][p%4]} Sample Project {p+1:02}', 'status':'At Risk' if p%5==0 else 'On Track',
            'projectManagerId':pm_id, 'teamIds':team_ids, 'site': ['Duliajan','Guwahati','Jorhat','Dibrugarh'][p%4], 'location':['Duliajan','Guwahati','Jorhat','Dibrugarh'][p%4], 'disciplines':list(dict.fromkeys(DISCIPLINES[t % len(DISCIPLINES)] for t in range(teams_per_pm))), 'discipline':'Multi-discipline', 'plannedProgress':25, 'actualProgress':0, 'dataLabel':'Demo Data'}
        session.add(m.Project(id=project_id, organization_id=org_id, name=payload['name'], status=payload['status'], payload_json=payload))
        session.flush()
        session.add(m.ProjectManagerAssignment(project_id=project_id, user_id=pm_id, assigned_at=now))
        session.add(m.ProjectMember(project_id=project_id, employee_id=employee_ids[f'PM-{p+1:02}'], responsibility='Project Manager', active=True))
        participating = {departments['Project Management'], departments['Planning / Project Controls']}
        for t, team_id in enumerate(team_ids):
            discipline = DISCIPLINES[t % len(DISCIPLINES)]
            tl_suffix = f'TL-{p+1:02}-{t+1:02}'
            tl_id = f'{prefix}-{tl_suffix}'
            team = {'id':team_id, 'name':discipline+' site team', 'projectId':project_id, 'teamLeaderId':tl_id, 'members':workers_per_team, 'active':workers_per_team, 'onLeave':0, 'other':0, 'status':'Active', 'site':payload['site']}
            session.add(m.Team(id=team_id, organization_id=org_id, project_id=project_id, payload_json=team))
            session.flush()
            session.add(m.TeamLeaderAssignment(team_id=team_id, user_id=tl_id, assigned_at=now))
            session.add(m.ProjectMember(project_id=project_id, employee_id=employee_ids[tl_suffix], responsibility='Team Leader', active=True))
            participating.add(departments[discipline])
            activity_id = f'{prefix}-A-{p+1:02}-{t+1:02}'
            activity = {'id':activity_id, 'projectId':project_id, 'teamId':team_id, 'activityName':discipline+' installation', 'discipline':discipline, 'location':payload['site']+' Block '+str(t+1), 'wbsCode':f'{p+1}.1.1.1.{t+1}.1', 'wbsLevel':6, 'level':'L6', 'plannedStart':'2026-10-01', 'plannedEnd':'2026-10-20', 'plannedProgress':25, 'progress':0, 'actualProgress':0, 'actualStart':None, 'actualEnd':None, 'status':'Not Started'}
            session.add(m.ScheduleActivity(id=activity_id, project_id=project_id, team_id=team_id, baseline_json=activity.copy(), payload_json=activity))
            for w in range(workers_per_team):
                suffix = f'WF-{p+1:02}-{t+1:02}-{w+1:03}'
                employee_id = employee_ids[suffix]
                session.add(m.EmployeeSkill(employee_id=employee_id, skill_id=skills[discipline]))
                session.add(m.ProjectMember(project_id=project_id, employee_id=employee_id, responsibility='Field execution', active=True))
                session.add(m.WorkforceAssignment(id='WA-'+f'{prefix}-{suffix}', organization_id=org_id, employee_id=employee_id, project_id=project_id, team_id=team_id, effective_start=start, effective_end=None, status='ACTIVE', assigned_by=f'{prefix}-ADMIN'))
        for department_id in participating:
            session.add(m.ProjectDepartment(project_id=project_id, department_id=department_id))
    session.flush()
    from backend.app.db.demo_modules import seed_modules
    seed_modules(session, prefix, locations[0], employee_ids)
    admin = session.get(m.User, f'{prefix}-ADMIN')
    append_audit(session, actor(admin), 'Demo organization provisioned', 'organization', org_id, {'demo':True, **expected, 'workers':pms*teams_per_pm*workers_per_team, 'accounts':len(accounts)})
    session.flush()
    return {'created':True, **totals(session, org_id)}, export
