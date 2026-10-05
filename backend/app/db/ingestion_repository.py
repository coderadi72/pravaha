"""Scoped, incremental schedule/attachment persistence; callers own transactions."""
from uuid import uuid4
from sqlalchemy import func,select
from backend.app.core.errors import ApiError
from backend.app.db.repository import iso_datetime,utc_now
from backend.app.models import FieldAttachment,Project,ScheduleActivity,ScheduleDependency,ScheduleVersion,Team


def schedules(session, project_id):
    return list(session.scalars(select(ScheduleActivity).where(ScheduleActivity.project_id==project_id).order_by(ScheduleActivity.id).limit(10001)))


def version_public(row):
    return {'id':row.id,'projectId':row.project_id,'importerUserId':row.importer_user_id,'createdAt':iso_datetime(row.created_at),'sourceFormat':row.source_format,'filename':row.filename,'checksum':row.checksum,**{k:v for k,v in row.payload_json.items() if k!='rows'}}


def versions(session,project_id,limit,offset):
    q=select(ScheduleVersion).where(ScheduleVersion.project_id==project_id)
    return {'items':[version_public(v) for v in session.scalars(q.order_by(ScheduleVersion.created_at.desc(),ScheduleVersion.id).offset(offset).limit(limit))], 'total':session.scalar(select(func.count()).select_from(q.subquery())),'limit':limit,'offset':offset}


def get_version(session,project_id,identifier):
    version=session.scalar(select(ScheduleVersion).where(ScheduleVersion.project_id==project_id,ScheduleVersion.id==identifier))
    if not version:raise ApiError(404,'NOT_FOUND','Schedule version not found in this project.')
    return version


def current_dependencies(session,project_id):
    q=select(ScheduleDependency).join(Project,Project.id==ScheduleDependency.project_id).where(ScheduleDependency.project_id==project_id,ScheduleDependency.version_id==Project.payload_json['currentScheduleVersionId'].astext)
    return [{'id':d.id,'projectId':d.project_id,'versionId':d.version_id,'predecessorId':d.predecessor_id,'successorId':d.successor_id,'type':d.dependency_type,'lagDays':d.lag_days,'createdAt':iso_datetime(d.created_at)} for d in session.scalars(q.limit(10001))]


def save_import(session,user,project,preview):
    now=utc_now();old=schedules(session,project.id)
    if len(old)>10000:raise ApiError(409,'IMPORT_CAPACITY','Current schedule exceeds supported import capacity.')
    current=project.payload_json.get('currentScheduleVersionId')
    if not project.payload_json.get('baselineScheduleVersionId'):
        baseline=ScheduleVersion(id='SV-'+str(uuid4()),project_id=project.id,importer_user_id=user.id,created_at=now,source_format='existing',filename='Existing preserved schedule',checksum='',payload_json={'kind':'BASELINE','rows':[r.payload_json for r in old],'accepted':len(old),'rejected':0,'warnings':[]})
        session.add(baseline);session.flush()
        project.payload_json={**project.payload_json,'baselineScheduleVersionId':baseline.id}
    version=ScheduleVersion(id='SV-'+str(uuid4()),project_id=project.id,importer_user_id=user.id,created_at=now,source_format=preview['sourceFormat'],filename=preview['filename'],checksum=preview['checksum'],payload_json={'kind':'IMPORTED','previousVersionId':current,'rows':preview['rows'],'accepted':preview['accepted'],'rejected':0,'warnings':preview['warnings']})
    session.add(version);session.flush()
    teams={t.id for t in session.scalars(select(Team).where(Team.project_id==project.id,Team.organization_id==user.organization_id))}
    existing={a.payload_json.get('activityId',a.id):a for a in old};new_ids={r['activityId'] for r in preview['rows']};internal={}
    for row in preview['rows']:
        if row.get('teamId') and row['teamId'] not in teams:raise ApiError(400,'INVALID_TEAM','An imported team is outside this project.')
        activity=existing.get(row['activityId']);payload={**row,'scheduleVersionId':version.id,'archived':False,'actualSource':'schedule_import','importedActuals':{k:row.get(k) for k in ['actualStart','actualEnd','progress']}}
        if activity:
            # Existing confirmed/provisional actual state and original baseline survive schedule changes.
            payload={**activity.payload_json,**payload,**{k:activity.payload_json.get(k) for k in ['actualStart','actualEnd','progress','status','blockedReason','observation','actualSource'] if k in activity.payload_json}}
            payload['actualSource']=activity.payload_json.get('actualSource','legacy_schedule')
            payload['importedActuals']=activity.payload_json.get('importedActuals',{})
            activity.payload_json={**payload,'id':activity.id};activity.team_id=row.get('teamId') or activity.team_id
        else:
            identifier='SA-'+str(uuid4());state={'actualStart':row.get('actualStart'),'actualEnd':row.get('actualEnd'),'progress':row.get('progress'),'status':'Complete' if row.get('actualEnd') or row.get('progress')==100 else 'In Progress' if row.get('actualStart') or row.get('progress',0)>0 else 'Not Started','blockedReason':'','observation':''}
            payload={**payload,**state,'id':identifier}
            activity=ScheduleActivity(id=identifier,project_id=project.id,team_id=row.get('teamId'),baseline_json=state,payload_json=payload)
            session.add(activity)
        internal[row['activityId']]=activity.id
    for identifier,row in existing.items():
        if identifier not in new_ids:row.payload_json={**row.payload_json,'archived':True,'removedInVersionId':version.id}
    session.flush()
    for e in preview['dependencies']:
        session.add(ScheduleDependency(id='DEP-'+str(uuid4()),project_id=project.id,version_id=version.id,predecessor_id=internal[e['predecessor']],successor_id=internal[e['successor']],dependency_type=e['type'],lag_days=e['lagDays'],created_at=now))
    project.payload_json={**project.payload_json,'currentScheduleVersionId':version.id,'previousScheduleVersionId':current}
    session.flush()
    return version


def attachment_public(row):
    return {'id':row.id,'projectId':row.project_id,'fieldUpdateId':row.field_update_id,'uploaderUserId':row.uploader_user_id,'filename':row.filename,'mimeType':row.mime_type,'size':row.size_bytes,'checksum':row.checksum,'createdAt':iso_datetime(row.created_at)}


def attachments(session,update_id,limit,offset):
    q=select(FieldAttachment).where(FieldAttachment.field_update_id==update_id)
    return {'items':[attachment_public(a) for a in session.scalars(q.order_by(FieldAttachment.created_at.desc()).offset(offset).limit(limit))],'total':session.scalar(select(func.count()).select_from(q.subquery())),'limit':limit,'offset':offset}


def dependencies_for_projects(session, project_ids):
    if not project_ids:return []
    rows=session.scalars(select(ScheduleDependency).join(Project,Project.id==ScheduleDependency.project_id).where(Project.id.in_(project_ids),ScheduleDependency.version_id==Project.payload_json['currentScheduleVersionId'].astext).limit(10001)).all()
    if len(rows)>10000:raise ApiError(413,'INTELLIGENCE_CAPACITY','Dependency batch exceeds 10,000 relationships. Narrow the project page.')
    return [{'id':r.id,'projectId':r.project_id,'versionId':r.version_id,'predecessorId':r.predecessor_id,'successorId':r.successor_id,'type':r.dependency_type,'lagDays':r.lag_days} for r in rows]


def dependency_page(session,project_id,limit,offset):
    q=select(ScheduleDependency).join(Project,Project.id==ScheduleDependency.project_id).where(ScheduleDependency.project_id==project_id,ScheduleDependency.version_id==Project.payload_json['currentScheduleVersionId'].astext)
    total=session.scalar(select(func.count()).select_from(q.subquery()))
    rows=session.scalars(q.order_by(ScheduleDependency.id).offset(offset).limit(limit))
    return {'items':[{'id':r.id,'projectId':r.project_id,'versionId':r.version_id,'predecessorId':r.predecessor_id,'successorId':r.successor_id,'type':r.dependency_type,'lagDays':r.lag_days,'createdAt':iso_datetime(r.created_at)} for r in rows],'total':total,'limit':limit,'offset':offset}
