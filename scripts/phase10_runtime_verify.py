"""Live localhost API verification. Secrets remain in the restricted initial export."""
import argparse
import json
from pathlib import Path
import httpx
from sqlalchemy import select, func, text
from backend.app import models as m
from backend.app.core.config import Settings
from backend.app.core.security import verify_password
from backend.app.db.session import create_engine_and_factory

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--after-restart', action='store_true')
    args = parser.parse_args()
    settings = Settings()
    base = f'http://{settings.api_host}:{settings.api_port}'
    credentials = json.loads((ROOT / '.audit/provisioning/phase10-credentials.json').read_text())['accounts']
    accounts = {key:next(r for r in credentials if r['id'] == 'PHASE10-'+suffix) for key,suffix in [('admin','ADMIN'),('pm','PM-01'),('tl','TL-01-01'),('worker','WF-01-01-001'),('hr','DEPT-HR')]}
    clients = {}
    for role, row in accounts.items():
        client = httpx.Client(base_url=base, timeout=45)
        result = client.post('/api/auth/login', json={'email':row['loginId'], 'password':row['initialPassword']})
        assert result.status_code == 200, (role, result.status_code)
        assert 'password_hash' not in result.text
        clients[role] = client
    report = {'health':httpx.get(base+'/api/health').status_code, 'logins':{role:True for role in clients}}
    assert report['health'] == 200
    worker = clients['worker']
    for path in ['/api/workspace','/api/search?q=installation','/api/organization/roster','/api/modules/materials','/api/admin/system','/api/projects','/api/team-leader/activities']:
        assert worker.get(path).status_code == 403, path
    report['workerDenied'] = True
    assert clients['admin'].get('/api/organization/overview').json()['workers'] == 3200
    assert clients['pm'].get('/api/organization/roster').json()['total'] == 160
    assert clients['tl'].get('/api/organization/roster').json()['total'] == 20
    assert clients['admin'].get('/api/modules/people').json()['total'] == 4
    assert clients['hr'].get('/api/modules/people').json()['total'] == 8
    report['rosterAndHrScopes'] = True
    state_file = ROOT / '.audit/phase10-runtime-state.json'
    if not args.after_restart:
        if state_file.exists():
            previous = json.loads(state_file.read_text())
            # Preserve the earlier audit/review history while withdrawing this
            # test contribution before re-verifying corrected completion logic.
            result = clients['pm'].post('/api/reviews/'+previous['updateId']+'/unmatch', json={'reason':'Superseded verification contribution after partial-progress completion fix.'})
            assert result.status_code == 200, result.text
        result = clients['tl'].post('/api/team-leader/field-updates', json={'description':'Civil installation at Duliajan Block 1 is 30 percent complete.', 'progress':30, 'actualStart':'2026-10-04'})
        assert result.status_code == 201, result.text
        update = result.json()['fieldUpdate']
        state = {'updateId':update['id'],'activityId':'PHASE10-A-01-01','progress':30,'feedback':'Phase 10 live verification: progress accepted.'}
        result = clients['pm'].post('/api/reviews/'+update['id']+'/confirm', json={'scheduleActivityId':state['activityId'],'feedback':state['feedback']})
        assert result.status_code == 200, result.text
        state_file.write_text(json.dumps(state,indent=2), encoding='utf-8')
    else:
        state = json.loads(state_file.read_text())
    schedule = clients['pm'].get('/api/projects/PHASE10-P-01/schedule').json()['schedule']
    activity = next(r for r in schedule if r['id'] == state['activityId'])
    assert activity['progress'] == state['progress'], activity
    assert activity['actualEnd'] is None and activity['status'] == 'In Progress', activity
    update = next(r for r in clients['tl'].get('/api/team-leader/field-updates').json()['fieldUpdates'] if r['id'] == state['updateId'])
    assert update['pmFeedback'] == state['feedback'], update
    audit = clients['admin'].get('/api/search', params={'q':'Review decision: confirm','kind':'audit'}).json()
    assert audit['total'] >= 1
    report.update(workflow=True, feedback=True, audit=True, persistenceAfterRestart=args.after_restart)
    engine, factory = create_engine_and_factory(settings)
    with factory() as session:
        users = session.scalars(select(m.User).where(m.User.organization_id == 'DEMO-phase10')).all()
        assert len({r.login_id.lower() for r in users}) == len(users)
        assert len({r['initialPassword'] for r in credentials}) == len(credentials)
        workers = [r for r in credentials if r['role'] == 'WORKFORCE']
        for row in [workers[0],workers[len(workers)//2],workers[-1]]:
            assert verify_password(row['initialPassword'],session.get(m.User,row['id']).password_hash)
        checks = {
            'employeeDepartmentOrg': 'SELECT count(*) FROM employees e JOIN departments d ON d.id=e.department_id WHERE e.organization_id <> d.organization_id',
            'allocationProjectTeam': 'SELECT count(*) FROM workforce_assignments w JOIN teams t ON t.id=w.team_id JOIN projects p ON p.id=w.project_id JOIN employees e ON e.id=w.employee_id WHERE t.project_id <> p.id OR w.organization_id <> p.organization_id OR w.organization_id <> t.organization_id OR w.organization_id <> e.organization_id',
            'activeAllocationDuplicate': "SELECT count(*) FROM (SELECT employee_id FROM workforce_assignments WHERE status='ACTIVE' GROUP BY employee_id HAVING count(*)>1) t",
            'disabledPm': 'SELECT count(*) FROM project_manager_assignments a JOIN users u ON u.id=a.user_id WHERE NOT u.active OR u.password_hash IS NULL',
            'disabledTl': 'SELECT count(*) FROM team_leader_assignments a JOIN users u ON u.id=a.user_id WHERE NOT u.active OR u.password_hash IS NULL',
        }
        report['consistency'] = {key:session.scalar(text(sql)) for key,sql in checks.items()}
        assert all(value == 0 for value in report['consistency'].values())
    report['credentialUniquenessAndRepresentativeHashes'] = True
    engine.dispose()
    for client in clients.values(): client.close()
    (ROOT / '.audit' / ('phase10-runtime-after.json' if args.after_restart else 'phase10-runtime-before.json')).write_text(json.dumps(report,indent=2), encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
