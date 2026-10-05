from fastapi import APIRouter, Request, Query
from backend.app.schemas.assistant import Ask
from backend.app.services import assistant_service

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.get("/contexts")
def contexts(request: Request, limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0, le=10000)):
    return assistant_service.contexts(request, limit, offset)


@router.post("/ask")
async def ask(request: Request, body: Ask):
    return await assistant_service.ask(request, body)


@router.get("/source")
def source(request: Request, reference: str = Query(min_length=1, max_length=30000)):
    return assistant_service.source(request, reference)
