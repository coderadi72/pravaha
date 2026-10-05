"""Authorized versioned imports and attachments using existing audit/locking."""
from uuid import uuid4
from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor,require_project_access,require_team_access
from backend.app.db import ingestion_repository as repo
from backend.app.db.repository import append_audit,lock_organization,utc_now
from backend.app.models import FieldAttachment,FieldUpdate
from backend.app.services.schedule_ingestion import preview,compare_versions
from backend.app.services.document_processor import decode_file,provider_result
from backend.app.services.project_intelligence_service import reconcile,authorize


def schedule_preview(session,user,project_id,body,settings):
    project=authorize(session,user,project_id)
    result=preview(body,project_id,settings)
    result['currentVersionId']=project.payload_json.get('currentScheduleVersionId')
    result['changeSummary']=compare_versions([r.payload_json for r in repo.schedules(session,project_id) if not r.payload_json.get('archived')],result['rows'])
    return result


def import_schedule(session,user,project_id,body,settings):
    project=authorize(session,user,project_id);lock_organization(session,user.organization_id)
    session.refresh(project)
    current=project.payload_json.get('currentScheduleVersionId')
    if body.expectedVersionId!=current:raise ApiError(409,'STALE_PREVIEW','Schedule changed since preview. Preview the current file again.')
    result=preview(body,project_id,settings)
    if not body.previewChecksum or body.previewChecksum!=result['checksum']:raise ApiError(409,'PREVIEW_REQUIRED','Preview this exact file before importing.')
    if not result['canImport']:raise ApiError(400,'INVALID_SCHEDULE','Import rejected. Correct all preview validation errors before committing.')
    change=compare_versions([a.payload_json for a in repo.schedules(session,project_id) if not a.payload_json.get('archived')],result['rows'])
    version=repo.save_import(session,user,project,result)
    append_audit(session,actor(user),'Schedule version imported','schedule_version',version.id,{'projectId':project_id,'versionId':version.id,'previousVersionId':current,'checksum':result['checksum'],'accepted':result['accepted'],'rejected':0,'warnings':result['warnings'],'changes':change})
    append_audit(session,actor(user),'Dependency graph imported','schedule_version',version.id,{'projectId':project_id,'versionId':version.id,'relationships':result['dependencies']})
    reconcile(session,actor(user),project_id,settings)
    return {'version':repo.version_public(version),'changes':change}


def compare(session,user,project_id,before_id,after_id):
    authorize(session,user,project_id)
    before=repo.get_version(session,project_id,before_id);after=repo.get_version(session,project_id,after_id)
    result=compare_versions(before.payload_json['rows'],after.payload_json['rows'])
    append_audit(session,actor(user),'Schedule versions compared','schedule_version',after.id,{'projectId':project_id,'beforeVersionId':before.id,'afterVersionId':after.id,'changes':result})
    return result


def accessible_update(session,user,update_id,upload=False):
    update=session.get(FieldUpdate,update_id)
    if not update:raise ApiError(404,'NOT_FOUND','Field update not found.')
    if user.role=='TEAM_LEADER':
        require_team_access(session,user,update.team_id)
        if update.submitter_user_id!=user.id:raise ApiError(403,'FORBIDDEN','Attachments require ownership of this field update.')
    else:require_project_access(session,user,update.project_id)
    if upload and user.role!='TEAM_LEADER':raise ApiError(403,'FORBIDDEN','Only the reporting Team Leader can upload attachments.')
    return update


def upload_attachment(session,user,update_id,body,settings):
    update=accessible_update(session,user,update_id,True);lock_organization(session,user.organization_id)
    file=decode_file(body,settings)
    row=FieldAttachment(id='ATT-'+str(uuid4()),project_id=update.project_id,field_update_id=update.id,uploader_user_id=user.id,filename=file['filename'],mime_type=file['mimeType'],size_bytes=file['size'],checksum=file['checksum'],created_at=utc_now(),content=file['content'])
    session.add(row);session.flush()
    append_audit(session,actor(user),'Field attachment uploaded','field_update',update.id,{'projectId':update.project_id,'attachment':repo.attachment_public(row)})
    return repo.attachment_public(row)


def attachment_for(session,user,attachment_id):
    row=session.get(FieldAttachment,attachment_id)
    if not row:raise ApiError(404,'NOT_FOUND','Attachment not found.')
    accessible_update(session,user,row.field_update_id)
    return row


def process_attachment(session,user,attachment_id,kind,settings):
    row=attachment_for(session,user,attachment_id)
    result=provider_result(kind,getattr(settings,'ai_provider' if kind=='advanced' else kind+'_provider'))
    append_audit(session,actor(user),kind.upper()+' processing requested','field_update',row.field_update_id,{'projectId':row.project_id,'attachmentId':row.id,'result':result})
    return result
