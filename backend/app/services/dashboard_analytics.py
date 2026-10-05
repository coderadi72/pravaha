"""Read-only Admin presentation aggregates over existing execution intelligence."""
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from backend.app import models as m
from backend.app.core.errors import ApiError
from backend.app.db.intelligence_repository import project_inputs
from backend.app.db.ingestion_repository import dependencies_for_projects
from backend.app.services.execution_intelligence import calculate, day, ratio
from backend.app.services.organization_service import admin, overview
from backend.app.services.project_intelligence_service import enrich


def progress(rows):
    values = [r['confirmedProgress'] for r in rows if r['confirmedProgress'] is not None]
    return {'value': round(sum(values) / len(values), 1) if values else None,
            'known': len(values), 'total': len(rows)}


def completion_series(rows, today):
    """Cumulative completion counts, not invented historical percent-complete."""
    planned = [day(r['plannedEnd']) for r in rows if day(r['plannedEnd'])]
    actual = [day(r['actualEnd']) for r in rows if r['status'] == 'COMPLETED'
              and day(r['actualEnd']) and day(r['actualEnd']) <= today
              and (not day(r['actualStart']) or day(r['actualStart']) <= day(r['actualEnd']))]
    if not planned:
        return {'points': [], 'scheduled': 0, 'datedActuals': len(actual), 'total': len(rows)}
    start, end = min(planned + actual), max(planned + [today])
    span = (end - start).days
    dates = sorted({start + timedelta(days=round(span * n / 11)) for n in range(12)} | {today})
    return {'points': [{'date': d.isoformat(), 'planned': ratio(sum(p <= d for p in planned), len(rows)),
                        'actual': ratio(sum(a <= d for a in actual), len(rows)) if d <= today else None}
                       for d in dates], 'scheduled': len(planned), 'datedActuals': len(actual), 'total': len(rows)}


def analytics(session, user, settings):
    admin(user)
    now = datetime.now(UTC)
    limit = settings.intelligence_max_input_rows
    projects = list(session.scalars(select(m.Project).where(m.Project.organization_id == user.organization_id)
                                   .order_by(m.Project.id).limit(limit + 1)))
    if len(projects) > limit:
        raise ApiError(409, 'INTELLIGENCE_CAPACITY', 'Organization analytics exceeds the configured input limit.')
    ids = [p.id for p in projects]
    activities, updates, matches, contributions = project_inputs(session, ids, limit)
    edges = dependencies_for_projects(session, ids)
    by_project, updates_by_project, matches_by_project, contributions_by_project, edges_by_project = (defaultdict(list) for _ in range(5))
    for a in activities:
        by_project[a['projectId']].append(a)
    update_projects = {u['id']: u['projectId'] for u in updates}
    for u in updates:
        updates_by_project[u['projectId']].append(u)
    for item in matches:
        matches_by_project[update_projects[item['fieldUpdateId']]].append(item)
    for item in contributions:
        contributions_by_project[update_projects[item['fieldUpdateId']]].append(item)
    for edge in edges:
        edges_by_project[edge['projectId']].append(edge)
    rows, warnings, portfolio = [], [], []
    for project in projects:
        result = enrich(calculate(project.id, by_project[project.id], updates_by_project[project.id],
                                  matches_by_project[project.id], contributions_by_project[project.id], settings, now),
                        edges_by_project[project.id], project.id)
        rows.extend(result['activities'])
        warnings.extend(result['warnings'])
        portfolio.append({'id': project.id, 'name': project.name, 'location': project.payload_json.get('location'),
                          'status': project.status, 'health': result['health']['schedule']['status'],
                          'progress': progress(result['activities']), 'activities': len(result['activities']),
                          'delayed': result['summary']['delayedActivities']})
    source = {a['id']: a for a in activities}
    disciplines = defaultdict(list)
    for row in rows:
        disciplines[source[row['activityId']].get('discipline') or 'Unclassified'].append(row)
    match_by_update = {item['fieldUpdateId']: item for item in matches}

    def match_category(update):
        match = match_by_update.get(update['id'], {})
        if match.get('matchStatus') == 'matched' and match.get('scheduleActivityId') in source and update.get('reviewStatus') == 'reviewed':
            return 'Matched'
        if match.get('matchStatus') == 'unmatched' or not match:
            return 'Unmatched'
        if match.get('matchStatus') == 'low_confidence':
            return 'Low confidence'
        return 'Pending review'

    matching = Counter(match_category(u) for u in updates)
    states = Counter(row['status'] for row in rows)
    project_status = Counter({'On Track': 0, 'At Risk': 0, 'Delayed': 0})
    for item in portfolio:
        project_status[{'NO_DELAY_SIGNAL': 'On Track', 'DELAYED': 'Delayed', 'AT_RISK': 'At Risk', 'UNKNOWN': 'At Risk'}.get(item['health'], 'At Risk')] += 1
    discipline_counts = Counter(source[row['activityId']].get('discipline') or 'Unclassified' for row in rows)
    alerts = {}
    for warning in warnings:
        entry = alerts.setdefault(warning['type'], {'type': warning['type'], 'count': 0, 'severity': 'LOW', 'projectId': warning['projectId']})
        entry['count'] += 1
        if {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}[warning['severity']] > {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}[entry['severity']]:
            entry['severity'] = warning['severity']
    organization = overview(session, user)
    pending = session.scalar(select(func.count()).select_from(m.RegistrationRequest).where(
        m.RegistrationRequest.review_organization_id == user.organization_id, m.RegistrationRequest.status == 'PENDING'))
    supervised = session.scalar(select(func.count()).select_from(m.TeamLeaderAssignment).join(m.Team).where(
        m.Team.organization_id == user.organization_id, m.Team.project_id.is_not(None)))
    names = {p.id: p.name for p in projects}
    recent = sorted(updates, key=lambda u: (u.get('submittedAt') or '', u['id']), reverse=True)[:6]
    return {'evaluatedAt': now.isoformat(), 'dataLabel': organization['dataLabel'], 'organization': organization,
            'kpis': {'projects': len(projects), 'progress': progress(rows),
                     'delayed': sum(r['timing'] == 'DELAYED' for r in rows), 'fieldUpdates': len(updates),
                     'supervisedTeams': supervised, 'workers': organization['workers'], 'pendingRegistrations': pending},
            'completion': completion_series(rows, now.date()), 'projects': portfolio,
            'projectStatus': [{'label': label, 'value': project_status[label]} for label in ('On Track', 'At Risk', 'Delayed')],
            'activityDistribution': [{'label': label, 'value': value} for label, value in discipline_counts.most_common()],
            'disciplines': [{'name': name, **progress(items)} for name, items in sorted(disciplines.items())],
            'matching': [{'label': label, 'value': matching[label]} for label in ('Matched', 'Low confidence', 'Unmatched', 'Pending review')],
            'activityStatus': [{'label': label, 'value': states[key]} for key, label in (
                ('COMPLETED', 'Completed'), ('IN_PROGRESS', 'In progress'), ('NOT_STARTED', 'Not started'), ('UNKNOWN', 'Unknown'))],
            'recentUpdates': [{'id': u['id'], 'description': u.get('rawText') or u.get('activity') or u['id'],
                               'discipline': u.get('discipline'), 'projectId': u['projectId'], 'projectName': names[u['projectId']],
                               'submittedAt': u.get('submittedAt'), 'status': match_category(u)} for u in recent],
            'alerts': sorted(alerts.values(), key=lambda a: (-{'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}[a['severity']], -a['count'], a['type']))}
