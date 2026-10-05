"""Schedule parsing and real PostgreSQL import/rollback/authorization integration."""
import base64,io
from copy import deepcopy
from datetime import UTC,datetime,timedelta
from openpyxl import Workbook
import pytest
from sqlalchemy import select,func,text
from backend.app.schemas.ingestion import ScheduleImportRequest,FileInput
from backend.app.services.schedule_ingestion import preview,compare_versions
from backend.app.services.document_processor import decode_file,provider_result
from backend.app.models import ScheduleVersion,ScheduleDependency,ScheduleActivity,FieldAttachment
from backend.tests.test_api import request,submit

CSV="activityId,activityName,discipline,location,plannedStart,plannedEnd,level,predecessors,teamId,progress,Extra\nPIP-NEW,Erect spool Line 999-XX,Piping,Rack B,2026-10-01,2026-10-03,L6,,TEAM-PIP-A,20,retained\nELE-NEW,Cable tray installation,Electrical,Block 3,2026-10-04,2026-10-08,L6,PIP-NEW:FS:1,,0,retained\n"

def payload(content=CSV,filename='schedule.csv'):
 return {'filename':filename,'contentBase64':base64.b64encode(content.encode() if isinstance(content,str) else content).decode()}


def test_csv_preview_extra_columns_relationships_dates_and_diff():
 result=preview(ScheduleImportRequest(**payload()),'PRJ-001')
 assert result['canImport'] and result['accepted']==2 and result['rows'][0]['extraColumns']['Extra']=='retained'
 assert result['dependencies']==[{'predecessor':'PIP-NEW','successor':'ELE-NEW','type':'FS','lagDays':1}]
 diff=compare_versions(result['rows'],[{**result['rows'][0],'plannedEnd':'2026-10-05'}])
 assert diff['removed']==['ELE-NEW'] and diff['changed'][0]['fields']['plannedEnd']['new']=='2026-10-05'

@pytest.mark.parametrize('old,new',[('2026-10-03','bad-date'),('TEAM-PIP-A,20','TEAM-PIP-A,101'),('ELE-NEW,Cable','PIP-NEW,Cable'),('PIP-NEW:FS:1','MISSING:FS:1'),('PIP-NEW:FS:1','PIP-NEW:BAD:1')])
def test_invalid_schedule_rejects_without_silent_truncation(old,new):
 result=preview(ScheduleImportRequest(**payload(CSV.replace(old,new))),'PRJ-001')
 assert not result['canImport'] and result['errors']


def test_xlsx_and_mapping_preview():
 workbook=Workbook();sheet=workbook.active
 sheet.append(['Code','Task','Begin','Finish']);sheet.append(['A','Pipe work',datetime(2026,10,1),datetime(2026,10,2)])
 buffer=io.BytesIO();workbook.save(buffer)
 body=ScheduleImportRequest(**payload(buffer.getvalue(),'mapped.xlsx'),mapping={'Code':'activityId','Task':'activityName','Begin':'plannedStart','Finish':'plannedEnd'})
 result=preview(body,'PRJ-001');assert result['canImport'] and result['sourceFormat']=='xlsx'
 assert result['rows'][0]['plannedStart']=='2026-10-01'


def test_cycle_and_formula_are_rejected():
 cyclic=CSV.replace('L6,,TEAM-PIP-A','L6,ELE-NEW:FS:0,TEAM-PIP-A')
 assert not preview(ScheduleImportRequest(**payload(cyclic)),'PRJ-001')['canImport']
 formula=CSV.replace('Erect spool Line 999-XX','=1+1')
 assert not preview(ScheduleImportRequest(**payload(formula)),'PRJ-001')['canImport']


def import_api(client,identities,data=None):
 body=data or payload()
 result=request(client,'/api/projects/PRJ-001/imports/preview',identities['pm'],'POST',body)
 assert result.status_code==200,result.text
 preview_data=result.json()
 body={**body,'mapping':preview_data['mapping']}
 committed=request(client,'/api/projects/PRJ-001/imports/commit',identities['pm'],'POST',{**body,'previewChecksum':preview_data['checksum'],'expectedVersionId':preview_data['currentVersionId']})
 assert committed.status_code==201,committed.text
 return committed.json()


def test_import_versions_graph_authorization_and_phase7_match(client,identities,seeded_session_factory):
 for role in ['tl']:
  assert request(client,'/api/projects/PRJ-001/imports/preview',identities[role],'POST',payload()).status_code==403
 assert request(client,'/api/projects/PRJ-002/imports/preview',identities['pm'],'POST',payload()).status_code==403
 result=import_api(client,identities)
 version_id=result['version']['id']
 with seeded_session_factory() as session:
  assert session.scalar(select(func.count()).select_from(ScheduleVersion))==2
  assert session.scalar(select(func.count()).select_from(ScheduleDependency))==1
  assert session.get(ScheduleActivity,'SA-1024').payload_json['progress']==65
 versions=request(client,'/api/projects/PRJ-001/schedule-versions',identities['pm']).json()['items']
 assert len(versions)==2 and any(v['kind']=='BASELINE' for v in versions)
 graph=request(client,'/api/projects/PRJ-001/dependencies',identities['pm']);assert graph.status_code==200 and len(graph.json()['items'])==1
 assert request(client,'/api/projects/PRJ-001/dependencies',identities['tl']).status_code==403
 data=request(client,'/api/workspace',identities['pm']).json()['data']
 assert len(data['scheduleActivities'])==2
 uid=submit(client,identities,'Spool erected for Line 999-XX in Rack B',progress=40)
 match=next(m for m in request(client,'/api/workspace',identities['pm']).json()['data']['activityMatches'] if m['fieldUpdateId']==uid)
 assert match['recommendedMatchId'] and match['matcherVersion']=='matcher-v1'
 confirm=request(client,f'/api/reviews/{uid}/confirm',identities['pm'],'POST',{'scheduleActivityId':match['recommendedMatchId']})
 assert confirm.status_code==200,confirm.text
 intelligence=request(client,'/api/intelligence/projects/PRJ-001',identities['pm']);assert intelligence.status_code==200,intelligence.text
 assert intelligence.json()['dependencyRelationships']==1
 next_import=import_api(client,identities,payload(CSV.replace('2026-10-08','2026-10-09')))
 compared=request(client,'/api/projects/PRJ-001/schedule-versions/compare?before_id='+version_id+'&after_id='+next_import['version']['id'],identities['pm'],'POST',{})
 assert compared.status_code==200 and compared.json()['changed']
 stale=request(client,'/api/projects/PRJ-001/imports/commit',identities['pm'],'POST',{**payload(),'previewChecksum':result['version']['checksum'],'expectedVersionId':version_id})
 assert stale.status_code==409


def test_import_audit_failure_rolls_back_all_schedule_changes(client,identities,seeded_session_factory,monkeypatch):
 import backend.app.services.ingestion_service as service
 body=payload();p=request(client,'/api/projects/PRJ-001/imports/preview',identities['pm'],'POST',body).json()
 with seeded_session_factory() as session:
  before={a.id:deepcopy(a.payload_json) for a in session.scalars(select(ScheduleActivity))}
 def fail(*args,**kwargs):raise RuntimeError('Injected import audit failure')
 monkeypatch.setattr(service,'append_audit',fail)
 response=request(client,'/api/projects/PRJ-001/imports/commit',identities['pm'],'POST',{**body,'previewChecksum':p['checksum'],'expectedVersionId':p['currentVersionId']})
 assert response.status_code==500
 with seeded_session_factory() as session:
  assert before=={a.id:a.payload_json for a in session.scalars(select(ScheduleActivity))}
  assert session.scalar(select(func.count()).select_from(ScheduleVersion))==0
  assert session.scalar(select(func.count()).select_from(ScheduleDependency))==0


def test_attachment_validation_scope_providers_and_persistence(client,identities,seeded_session_factory):
 uid=submit(client,identities)
 response=request(client,f'/api/field-updates/{uid}/attachments',identities['tl'],'POST',payload('Site diary text','../../diary.txt'))
 assert response.status_code==201,response.text
 attachment=response.json();assert attachment['filename']=='diary.txt'
 assert request(client,f'/api/attachments/{attachment["id"]}',identities['pm']).content==b'Site diary text'
 for provider in ['ocr','asr','advanced']:
  processed=request(client,f'/api/attachments/{attachment["id"]}/process',identities['tl'],'POST',{'provider':provider})
  assert processed.status_code==200 and processed.json()['status']=='NOT_CONFIGURED' and processed.json()['text'] is None
 invalid=request(client,f'/api/field-updates/{uid}/attachments',identities['tl'],'POST',payload(b'not a PNG','malware.png'));assert invalid.status_code==400
 assert request(client,f'/api/field-updates/{uid}/attachments',identities['pm'],'POST',payload('x','diary.txt')).status_code==403
 with seeded_session_factory() as session:
  assert session.scalar(select(func.count()).select_from(FieldAttachment))==1



def test_minimal_schedule_optional_metadata_supports_tl_activity_actions(client,identities):
 csv='activityId,activityName,plannedStart,plannedEnd,teamId\nMINIMAL,Erect spool Line 247-XX,2026-10-01,2026-10-03,TEAM-PIP-A\n'
 import_api(client,identities,payload(csv))
 workspace=request(client,'/api/workspace',identities['tl']).json()['data']
 activity=workspace['scheduleActivities'][0]
 assert activity['progress'] is None and activity['discipline']=='' and activity['location']==''
 result=request(client,f'/api/team-leader/activities/{activity["id"]}/actions',identities['tl'],'POST',{'action':'start'})
 assert result.status_code==200,result.text
 new=next(a for a in result.json()['data']['scheduleActivities'] if a['id']==activity['id'])
 assert new['actualStart'] and new['progress']==0
