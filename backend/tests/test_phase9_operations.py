"""Phase 9 shared throttling, scoped search, structured observations and traversal."""
from copy import deepcopy
from datetime import datetime,UTC,timedelta
import pytest
from sqlalchemy import select,func
from backend.app.models import LoginRateBucket,FieldAttachment,Project
from backend.app.core.security import PostgresLoginRateLimiter
from backend.app.services.dependency_service import downstream
from backend.tests.test_api import request,submit
from backend.tests.test_ingestion import payload


def activity(id,**values):
    return {'activityId':id,'delayDays':10 if id=='A' else 0,'plannedStart':'2026-01-01','plannedEnd':'2026-01-05','actualStart':None,'confirmedProgress':0,'startVarianceDays':10 if id=='A' else None,'finishVarianceDays':10 if id=='A' else None,'overdueDays':0,'status':'NOT_STARTED','timing':'UNKNOWN',**values}

@pytest.mark.parametrize('kind',['FS','SS','FF','SF'])
def test_typed_dependency_lag_and_transitive_exposure(kind):
    rows=[activity('A'),activity('B'),activity('C')]
    edges=[{'id':'D1','versionId':'V','predecessorId':'A','successorId':'B','type':kind,'lagDays':1},{'id':'D2','versionId':'V','predecessorId':'B','successorId':'C','type':'FS','lagDays':0}]
    result=downstream(rows,edges)
    assert result==downstream(list(reversed(rows)),list(reversed(edges)))
    assert result['status']=='KNOWN'
    assert [i['depth'] for i in result['items']]==[1,2]
    assert all(i['status']=='ESTIMATED' for i in result['items'])
    assert result['items'][1]['evidence']['path']==['A','B','C']
    assert result['items'][0]['evidence']['type']==kind


def test_started_and_missing_date_dependencies_are_honest():
    edge={'id':'D','versionId':'V','predecessorId':'A','successorId':'B','type':'FS','lagDays':0}
    result=downstream([activity('A'),activity('B',actualStart='2026-01-06')],[edge])
    assert result['items'][0]['status']=='NOT_APPLICABLE'
    result=downstream([activity('A'),activity('B',plannedStart=None)],[edge])
    assert result['items'][0]['status']=='UNKNOWN' and result['items'][0]['potentialExposureDays'] is None


def test_shared_limiter_survives_multiple_instances_and_expiry(seeded_session_factory):
    first=PostgresLoginRateLimiter(seeded_session_factory);second=PostgresLoginRateLimiter(seeded_session_factory)
    key='127.0.0.1:fake@example.invalid'
    for index in range(5):assert not (first if index%2 else second).is_limited(key)
    assert second.is_limited(key)
    with seeded_session_factory.begin() as session:
        row=session.scalar(select(LoginRateBucket));assert row.attempts==6 and key not in row.key_hash
        row.expires_at=datetime.now(UTC)-timedelta(seconds=1)
    assert not first.is_limited(key)
    second.clear(key)
    with seeded_session_factory() as session:assert session.scalar(select(func.count()).select_from(LoginRateBucket))==0


def test_search_scopes_pagination_and_literal_wildcards(client,identities):
    for role in ['admin','pm','tl']:
        r=request(client,'/api/search?q=&limit=1',identities[role]);assert r.status_code==200,r.text
        body=r.json();assert len(body['items'])==1 and body['total']>1
        if role!='admin':assert body['items'][0]['projectId']=='PRJ-001'
    r=request(client,'/api/search?q=%25&kind=projects',identities['pm']);assert r.json()['items']==[]
    assert request(client,'/api/search?kind=audit',identities['tl']).json()['items']==[]
    assert request(client,'/api/search').status_code==401
    r=request(client,'/api/search?kind=projects',identities['pm']).json()
    assert all(x['projectId']=='PRJ-001' for x in r['items'])


def test_structured_update_safe_health_and_admin_project(client,identities):
    assert request(client,'/api/ready').json()['status']=='ready'
    assert request(client,'/api/admin/system',identities['tl']).status_code==403
    health=request(client,'/api/admin/system',identities['admin']);assert health.status_code==200,health.text
    assert 'database_url' not in health.text and 'api_key' not in health.text
    body={'description':'Spool erected for Line 247-XX','quantity':3.5,'unit':'spools','remarks':'Ready for inspection','blocker':'Crane unavailable','crew':'Crew A','equipment':'Crane 2'}
    r=request(client,'/api/team-leader/field-updates',identities['tl'],'POST',body)
    assert r.status_code==201,r.text
    assert all(r.json()['fieldUpdate'][k]==v for k,v in body.items() if k!='description')
    assert request(client,'/api/admin/projects',identities['pm'],'POST',{'name':'New project'}).status_code==403
    project=request(client,'/api/admin/projects',identities['admin'],'POST',{'name':'New project','location':'Assam'})
    assert project.status_code==201,project.text
    id=project.json()['project']['id']
    assert request(client,f'/api/projects/{id}/schedule-versions',identities['pm']).status_code==403


def test_attachment_audit_failure_rolls_back_bytes(client,identities,seeded_session_factory,monkeypatch):
    import backend.app.services.ingestion_service as service
    uid=submit(client,identities)
    def fail(*a,**k):raise RuntimeError('Injected attachment audit failure')
    monkeypatch.setattr(service,'append_audit',fail)
    r=request(client,f'/api/field-updates/{uid}/attachments',identities['tl'],'POST',payload('note','site.txt'))
    assert r.status_code==500
    with seeded_session_factory() as session:assert session.scalar(select(func.count()).select_from(FieldAttachment))==0


@pytest.mark.parametrize('format',['PNG','JPEG','WAV'])
def test_real_binary_attachments_validate_and_tampered_content_rejects(format):
    import io,wave
    from PIL import Image
    from backend.app.schemas.ingestion import FileInput
    from backend.app.services.document_processor import decode_file
    buffer=io.BytesIO()
    if format=='WAV':
        with wave.open(buffer,'wb') as audio:
            audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(8000);audio.writeframes(b'\\0' * 16000)
        filename='sample.wav'
    else:
        Image.new('RGB',(5,5),'white').save(buffer,format=format)
        filename='sample.'+('png' if format=='PNG' else 'jpg')
    result=decode_file(FileInput(**payload(buffer.getvalue(),filename)))
    assert result['size']==len(buffer.getvalue()) and result['checksum']
    from backend.app.core.errors import ApiError
    with pytest.raises(ApiError):decode_file(FileInput(**payload(b'not binary',filename)))


def test_preview_mapping_checksum_and_hierarchy_cycle():
    from backend.app.schemas.ingestion import ScheduleImportRequest
    from backend.app.services.schedule_ingestion import preview
    csv='activityId,activityName,plannedStart,plannedEnd,parentActivityId\nA,Pipe,2026-10-01,2026-10-02,B\nB,Valve,2026-10-01,2026-10-03,A\n'
    assert not preview(ScheduleImportRequest(**payload(csv)),'PRJ-001')['canImport']
    csv=csv.replace(',B\n',',\n').replace(',A\n',',\n')
    first=preview(ScheduleImportRequest(**payload(csv)),'PRJ-001')
    second=preview(ScheduleImportRequest(**payload(csv),mapping={'parentActivityId':''}),'PRJ-001')
    assert first['canImport'] and first['checksum']!=second['checksum']


def test_reversible_phase9_migration_in_isolated_schema(engine):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    from pathlib import Path
    config=Config(str(Path('backend/alembic.ini').resolve()))
    with engine.begin() as c:
        config.attributes['connection']=c
        command.downgrade(config,'0002_execution_warnings')
        assert 'schedule_versions' not in inspect(c).get_table_names()
        command.upgrade(config,'head')
        command.check(config)
        assert 'schedule_dependencies' in inspect(c).get_table_names()
