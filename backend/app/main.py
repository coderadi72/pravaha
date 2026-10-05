"""The single production API: FastAPI → services → SQLAlchemy → PostgreSQL."""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from backend.app.api.routes import activities, admin, auth, field_updates, health, intelligence, ingestion, projects, reviews, teams, search, organization, modules, assistant
from backend.app.core.config import Settings
from backend.app.core.errors import ApiError, error_payload
from backend.app.core.middleware import RequestProtectionMiddleware, StructuredRequestLoggingMiddleware
from backend.app.core.security import LoginRateLimiter, PostgresLoginRateLimiter
from backend.app.db.session import create_engine_and_factory
from backend.app.schemas.contracts import ErrorResponse
from backend.app.services.auth_service import cleanup_expired_sessions

logger = logging.getLogger("pravaha.api")


def create_app(settings: Settings | None = None, session_factory=None, engine=None):
    settings = settings or Settings()
    owns_engine = session_factory is None
    if owns_engine:
        engine, session_factory = create_engine_and_factory(settings)

    @asynccontextmanager
    async def lifespan(application):
        with application.state.session_factory() as session, session.begin():
            from backend.app.services.system_service import validate_schema
            validate_schema(session)
            cleanup_expired_sessions(session)
        yield
        if owns_engine:
            engine.dispose()

    api = FastAPI(
        title="PRAVAHA API", version="12.0", lifespan=lifespan,
        docs_url="/docs" if settings.enable_api_docs else None,
        redoc_url="/redoc" if settings.enable_api_docs else None,
        openapi_url="/openapi.json" if settings.enable_api_docs else None,
        responses={status: {"model": ErrorResponse} for status in (400, 401, 403, 404, 409, 413, 429, 500)},
    )
    api.state.settings, api.state.session_factory, api.state.engine = settings, session_factory, engine
    limiter_kwargs = {
        "max_attempts": settings.login_max_attempts,
        "window_seconds": settings.login_window_seconds,
        "max_buckets": settings.login_max_buckets,
    }
    api.state.login_limiter = PostgresLoginRateLimiter(session_factory, **{k: v for k, v in limiter_kwargs.items() if k != "max_buckets"}) if settings.rate_limit_backend == "postgresql" else LoginRateLimiter(**limiter_kwargs)
    import threading
    signup_kwargs = {"max_attempts": settings.signup_max_attempts, "window_seconds": settings.signup_window_seconds, "max_buckets": settings.signup_max_buckets}
    api.state.signup_limiter = PostgresLoginRateLimiter(session_factory, **{k: v for k, v in signup_kwargs.items() if k != "max_buckets"}) if settings.rate_limit_backend == "postgresql" else LoginRateLimiter(**signup_kwargs)
    api.state.signup_rate_lock = threading.Lock()
    from backend.app.services.chat_provider import ProviderPool
    api.state.assistant_providers = ProviderPool(settings)
    api.state.assistant_slots = threading.BoundedSemaphore(settings.assistant_max_concurrent)
    api.state.assistant_rate_lock = threading.Lock()
    api.state.assistant_limiter = PostgresLoginRateLimiter(session_factory, max_attempts=settings.assistant_max_requests, window_seconds=settings.assistant_window_seconds)
    api.add_middleware(
        RequestProtectionMiddleware,
        allowed_origins=settings.cors_origins,
        production=settings.app_env == "production",
        body_limit=settings.request_body_limit_bytes,
        upload_body_limit=settings.request_upload_body_limit_bytes,
    )
    api.add_middleware(StructuredRequestLoggingMiddleware)
    if settings.cors_origins:
        api.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "OPTIONS"], allow_headers=["Content-Type"])

    @api.exception_handler(ApiError)
    async def api_error(request: Request, exc: ApiError):
        return JSONResponse(error_payload(exc.code, exc.message), status_code=exc.status)

    @api.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        if any(item["type"] == "json_invalid" for item in errors):
            code, message = "INVALID_JSON", "Request body must be valid JSON."
        elif any(item["type"] == "model_attributes_type" for item in errors):
            code, message = "INVALID_BODY", "Request body must be a JSON object."
        elif any("progress" in item.get("loc", ()) for item in errors):
            code, message = "INVALID_PROGRESS", "Progress must be between 0 and 100."
        else:
            code, message = "INVALID_INPUT", "Request values are invalid."
        return JSONResponse(error_payload(code, message), status_code=400)

    @api.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return JSONResponse(error_payload("NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR", "API route not found." if exc.status_code == 404 else "Request could not be accepted."), status_code=exc.status_code)

    @api.exception_handler(IntegrityError)
    async def constraint_error(request: Request, exc: IntegrityError):
        if getattr(exc.orig, "sqlstate", "") == "23505":
            return JSONResponse(error_payload("CONFLICT", "The requested record conflicts with existing data."), status_code=409)
        logger.error("Database constraint failure on %s (%s)", request.url.path, type(exc.orig).__name__)
        return JSONResponse(error_payload("INTERNAL_ERROR", "An unexpected server error occurred."), status_code=500)

    @api.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logger.error("API failure on %s (%s)", request.url.path, type(exc).__name__)
        return JSONResponse(error_payload("INTERNAL_ERROR", "An unexpected server error occurred."), status_code=500)

    for route in (health, auth, projects, admin, teams, field_updates, activities, reviews, intelligence, ingestion, search, organization, modules, assistant):
        api.include_router(route.router)
    return api


app = create_app()
