"""Explicit stateful departmental APIs with organization/project/team scope."""
from fastapi import APIRouter, Query
from backend.app.api.deps import CurrentUser, SessionDep
from backend.app.schemas.organization import ValuesRequest, TransitionRequest
from backend.app.services import module_service as service

router = APIRouter(prefix='/api/modules', tags=['Department workflows'])


@router.get('/{resource}')
def records(resource: str, session: SessionDep, user: CurrentUser, q: str = Query('', max_length=120), limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):
    return service.list_records(session, user, resource, q, limit, offset)


@router.post('/{resource}', status_code=201)
def create(resource: str, body: ValuesRequest, session: SessionDep, user: CurrentUser):
    return service.create(session, user, resource, body.values)


@router.get('/{resource}/{identifier}')
def detail(resource: str, identifier: str, session: SessionDep, user: CurrentUser):
    return service.detail(session, user, resource, identifier)


@router.patch('/{resource}/{identifier}')
def update(resource: str, identifier: str, body: ValuesRequest, session: SessionDep, user: CurrentUser):
    return service.update_master(session, user, resource, identifier, body.values)


@router.post('/{resource}/{identifier}/transition')
def transition(resource: str, identifier: str, body: TransitionRequest, session: SessionDep, user: CurrentUser):
    return service.transition(session, user, resource, identifier, body.status)
