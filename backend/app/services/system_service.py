"""Safe readiness and administrator operations; no credentials in responses."""
from pathlib import Path
from uuid import uuid4
from sqlalchemy import select,text,func
from backend.app.models import Project,ScheduleVersion,FieldAttachment
from backend.app.db.repository import lock_organization,append_audit
from backend.app.core.permissions import actor
from backend.app.core.errors import ApiError
from alembic.config import Config
from alembic.script import ScriptDirectory
from backend.app.services.chat_provider import provider_status


def validate_schema(session):
    cfg=Config(str(Path(__file__).resolve().parents[2]/'alembic.ini'))
    expected=ScriptDirectory.from_config(cfg).get_current_head()
    current=session.execute(text('SELECT version_num FROM alembic_version')).scalar()
    if current!=expected:raise RuntimeError('Database migration is required before startup.')
    return current


def readiness(session):
    session.execute(text('SELECT 1'))
    validate_schema(session)
    return {'status':'ready','database':'available','migrations':'current'}


def system_status(session,settings):
    result=readiness(session)
    return {**result,'version':'12.0','rateLimitBackend':settings.rate_limit_backend,
        'cookieSecure':settings.session_cookie_secure,'poolMode':settings.db_pool_mode,
        'providers':{**{k:('NOT_CONFIGURED' if v.lower() in {'','none'} else 'UNAVAILABLE') for k,v in [('ocr',settings.ocr_provider),('asr',settings.asr_provider),('advanced',settings.ai_provider)]},'chat':provider_status(settings)},
        'limits':{'uploadBytes':settings.attachment_max_bytes,'importActivities':settings.schedule_max_rows,'importRelationships':settings.schedule_max_relationships},
        'backupStatus':'NOT_VERIFIED','providerAdapters':'Groq and NVIDIA chat adapters installed; OCR, ASR and advanced ranking adapters unavailable'}


def create_project(session,user,body):
    lock_organization(session,user.organization_id)
    name=body.name.strip()
    if not name:raise ApiError(400,'INVALID_INPUT','Project name is required.')
    identifier='PRJ-'+str(uuid4())
    payload={'id':identifier,'name':name,'location':body.location.strip(),'status':'Not Started','teamIds':[],'projectManagerId':None,'dataLabel':'User-created project'}
    session.add(Project(id=identifier,organization_id=user.organization_id,name=name,status='Not Started',payload_json=payload))
    session.flush()
    append_audit(session,actor(user),'Project created','project',identifier,{'projectId':identifier,'name':name})
    return {'project':payload}
