"""Presentation aggregates must preserve evidence, scope and missingness."""
from datetime import UTC, date, datetime
from sqlalchemy import select
from backend.app.models import Organization, Project, User, AuditEvent
from backend.app.services.dashboard_analytics import completion_series, progress, analytics


def test_unknown_progress_is_not_zero_or_weighted():
    assert progress([{'confirmedProgress': None}]) == {'value': None, 'known': 0, 'total': 1}
    assert progress([{'confirmedProgress': 20}, {'confirmedProgress': 100}, {'confirmedProgress': None}]) == {'value': 60, 'known': 2, 'total': 3}


def test_completion_curve_never_fabricates_finish_dates_or_future_actuals():
    rows = [
        {'plannedEnd': '2026-10-02', 'actualStart': '2026-10-01', 'actualEnd': '2026-10-03', 'status': 'COMPLETED'},
        {'plannedEnd': '2026-10-12', 'actualStart': None, 'actualEnd': None, 'status': 'UNKNOWN'},
        {'plannedEnd': None, 'actualStart': None, 'actualEnd': None, 'status': 'COMPLETED'},
        {'plannedEnd': '2026-10-04', 'actualStart': None, 'actualEnd': '2026-11-01', 'status': 'COMPLETED'},
    ]
    result = completion_series(rows, date(2026, 10, 5))
    today = next(p for p in result['points'] if p['date'] == '2026-10-05')
    assert today == {'date': '2026-10-05', 'planned': 50, 'actual': 25}
    assert result['datedActuals'] == 1 and result['scheduled'] == 3
    assert all(p['actual'] is None for p in result['points'] if p['date'] > '2026-10-05')
    assert completion_series([], date(2026, 10, 5))['points'] == []


def test_analytics_admin_only_and_counts_match_existing_intelligence(client, identities):
    url = '/api/organization/analytics'
    assert client.get(url).status_code == 401
    for role in ('pm', 'tl'):
        assert client.get(url, headers={'cookie': identities[role]}).status_code == 403
    response = client.get(url, headers={'cookie': identities['admin']})
    assert response.status_code == 200
    data = response.json()
    assert 'password' not in response.text
    portfolio = client.get('/api/intelligence/portfolio', headers={'cookie': identities['admin']}).json()
    assert data['kpis']['projects'] == portfolio['total']
    assert data['kpis']['delayed'] == sum(p['summary']['delayedActivities'] for p in portfolio['items'])
    assert sum(s['value'] for s in data['activityStatus']) == sum(p['summary']['scheduledActivities'] for p in portfolio['items'])
    assert sum(s['value'] for s in data['matching']) == data['kpis']['fieldUpdates']
    assert data['kpis']['progress']['known'] <= data['kpis']['progress']['total']
    assert sum(item['value'] for item in data['projectStatus']) == data['kpis']['projects']
    assert sum(item['value'] for item in data['activityDistribution']) == sum(p['summary']['scheduledActivities'] for p in portfolio['items'])


def test_analytics_excludes_other_organizations_and_is_read_only(seeded_session_factory, settings):
    with seeded_session_factory.begin() as session:
        session.add(Organization(id='ANALYTICS-OTHER', name='Other synthetic', data_label='Synthetic', payload_json={}))
        session.flush()
        session.add(Project(id='ANALYTICS-PRIVATE', name='Hidden project', organization_id='ANALYTICS-OTHER', status='Active', payload_json={}))
        session.add(User(id='ANALYTICS-ADMIN', organization_id='ANALYTICS-OTHER', email='analytics@synthetic.invalid', full_name='Synthetic Admin', role='ADMIN', active=True, created_at=datetime.now(UTC)))
    with seeded_session_factory() as session:
        user = session.get(User, 'ANALYTICS-ADMIN')
        before = list(session.scalars(select(AuditEvent.id)))
        data = analytics(session, user, settings)
        assert [p['id'] for p in data['projects']] == ['ANALYTICS-PRIVATE']
        assert data['kpis']['fieldUpdates'] == 0
        assert data['kpis']['progress']['value'] is None
        assert data['recentUpdates'] == [] and data['alerts'] == []
        assert list(session.scalars(select(AuditEvent.id))) == before
