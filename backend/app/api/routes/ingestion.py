"""Thin Phase 9 routes: strict contracts, authorization delegated to services."""
from fastapi import APIRouter,Query
from starlette.responses import Response
from backend.app.api.deps import CurrentUser,SessionDep,SettingsDep
from backend.app.db import ingestion_repository as repo
from backend.app.schemas.ingestion import ScheduleImportRequest,FileInput,ProviderRequest
from backend.app.services import ingestion_service as service
from backend.app.services.project_intelligence_service import authorize
router=APIRouter(tags=['Schedule and field ingestion'])

@router.post('/api/projects/{project_id}/imports/preview')
def preview(project_id:str,body:ScheduleImportRequest,session:SessionDep,user:CurrentUser,settings:SettingsDep):
    return service.schedule_preview(session,user,project_id,body,settings)

@router.post('/api/projects/{project_id}/imports/commit',status_code=201)
def commit(project_id:str,body:ScheduleImportRequest,session:SessionDep,user:CurrentUser,settings:SettingsDep):
    return service.import_schedule(session,user,project_id,body,settings)

@router.get('/api/projects/{project_id}/schedule-versions')
def versions(project_id:str,session:SessionDep,user:CurrentUser,limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0)):
    authorize(session,user,project_id);return repo.versions(session,project_id,limit,offset)

@router.post('/api/projects/{project_id}/schedule-versions/compare')
def compare(project_id:str,before_id:str,after_id:str,session:SessionDep,user:CurrentUser):
    return service.compare(session,user,project_id,before_id,after_id)

@router.get('/api/projects/{project_id}/dependencies')
def dependencies(project_id:str,session:SessionDep,user:CurrentUser,limit:int=Query(100,ge=1,le=500),offset:int=Query(0,ge=0)):
    authorize(session,user,project_id);return repo.dependency_page(session,project_id,limit,offset)

@router.post('/api/field-updates/{update_id}/attachments',status_code=201)
def upload(update_id:str,body:FileInput,session:SessionDep,user:CurrentUser,settings:SettingsDep):
    return service.upload_attachment(session,user,update_id,body,settings)

@router.get('/api/field-updates/{update_id}/attachments')
def attachments(update_id:str,session:SessionDep,user:CurrentUser,limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0)):
    service.accessible_update(session,user,update_id);return repo.attachments(session,update_id,limit,offset)

@router.get('/api/attachments/{attachment_id}')
def download(attachment_id:str,session:SessionDep,user:CurrentUser):
    row=service.attachment_for(session,user,attachment_id)
    return Response(row.content,media_type='application/octet-stream',headers={'Content-Disposition':f'attachment; filename="{row.filename}"','X-Content-Type-Options':'nosniff'})

@router.post('/api/attachments/{attachment_id}/process')
def process(attachment_id:str,body:ProviderRequest,session:SessionDep,user:CurrentUser,settings:SettingsDep):
    return service.process_attachment(session,user,attachment_id,body.provider,settings)
