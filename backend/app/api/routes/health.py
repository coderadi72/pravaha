from fastapi import APIRouter
from sqlalchemy import text

from backend.app.api.deps import SessionDep
from backend.app.schemas.contracts import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/api/health", response_model=HealthResponse)
def health(session: SessionDep):
    session.execute(text("SELECT 1"))
    return {"status": "ok", "service": "pravaha-api"}


@router.get('/api/ready')
def ready(session: SessionDep):
    from backend.app.services.system_service import readiness
    return readiness(session)
