from datetime import UTC, datetime, timedelta
import re
import secrets
from uuid import uuid4

from sqlalchemy import delete, func, select, or_

from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor
from backend.app.core.security import COOKIE_NAME, digest_token, hash_password, is_valid_password, new_session_token, verify_password
from backend.app.db.repository import append_audit
from backend.app.models import RegistrationRequest, SessionToken, User

_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(24))


def iso_date(value):
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def safe_user(user):
    return {"id": user.id, "email": user.email, "name": user.full_name, "role": user.role, "organizationId": user.organization_id}


def cleanup_expired_sessions(session, now=None):
    result = session.execute(delete(SessionToken).where(SessionToken.expires_at <= (now or datetime.now(UTC))))
    return result.rowcount


def authenticate_session(session, request):
    token = request.cookies.get(COOKIE_NAME)
    row = session.get(SessionToken, digest_token(token)) if token and len(token) <= 256 else None
    user = session.get(User, row.user_id) if row else None
    if not row or row.expires_at <= datetime.now(UTC) or not user or not user.active:
        raise ApiError(401, "UNAUTHENTICATED", "Sign in to continue.")
    return user, row


def sign_in(session, request, body):
    email, password = body.email.strip().lower(), body.password
    if not email or not password:
        raise ApiError(400, "INVALID_INPUT", "Email or password is invalid.")
    peer = request.client.host if request.client else "unknown"
    key = f"{peer}:{email}"
    limiter = request.app.state.login_limiter
    if limiter.is_limited(key):
        raise ApiError(429, "RATE_LIMITED", "Too many sign-in attempts. Try again later.")
    user = session.scalar(select(User).where(or_(func.lower(User.email) == email, func.lower(User.login_id) == email), User.active.is_(True)))
    valid = verify_password(password, user.password_hash if user and user.password_hash else _DUMMY_PASSWORD_HASH)
    if not valid or not user or not user.password_hash:
        limiter.record_failure(key)
        raise ApiError(401, "INVALID_CREDENTIALS", "Email or password is incorrect.")
    limiter.clear(key)
    token, now = new_session_token(), datetime.now(UTC)
    expires_at = now + timedelta(seconds=request.app.state.settings.session_ttl_seconds)
    session.add(SessionToken(token_hash=digest_token(token), user_id=user.id, created_at=now, expires_at=expires_at))
    append_audit(session, actor(user), "Signed in", "session", user.id, {})
    session.flush()
    return {"user": safe_user(user), "expiresAt": iso_date(expires_at)}, token


def sign_out(session, request):
    token = request.cookies.get(COOKIE_NAME)
    login_session = session.get(SessionToken, digest_token(token)) if token and len(token) <= 256 else None
    if login_session:
        user = session.get(User, login_session.user_id)
        if user:
            append_audit(session, actor(user), "Signed out", "session", user.id, {})
        session.delete(login_session)
        session.flush()


def provision_user(session, user, body):
    full_name, email = body.name.strip(), body.email.strip().lower()
    if not full_name:
        raise ApiError(400, "INVALID_INPUT", "Name is invalid.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ApiError(400, "INVALID_EMAIL", "Email address is invalid.")
    if not is_valid_password(body.password):
        raise ApiError(400, "WEAK_PASSWORD", "Password must be 12–128 characters and include uppercase, lowercase, number, and special character.")
    if body.role not in {"PROJECT_MANAGER", "TEAM_LEADER", "DEPARTMENT"}:
        raise ApiError(400, "INVALID_ROLE", "Only management accounts can be provisioned here. Workforce accounts use secure demo provisioning.")
    from backend.app.services.registration_service import lock_registration_email
    lock_registration_email(session, email)
    if session.scalar(select(User.id).where(or_(func.lower(User.email) == email, func.lower(User.login_id) == email))) or session.scalar(select(RegistrationRequest.id).where(func.lower(RegistrationRequest.email) == email, RegistrationRequest.status == "PENDING")):
        raise ApiError(409, "DUPLICATE_EMAIL", "An account with that email already exists.")
    prefix = {'PROJECT_MANAGER':'PM', 'TEAM_LEADER':'TL', 'DEPARTMENT':'DEPT'}[body.role]
    identifier = f"{prefix}-{str(uuid4())[:8].upper()}"
    session.add(User(id=identifier, organization_id=user.organization_id, email=email, full_name=full_name, role=body.role, password_hash=hash_password(body.password), active=True, created_at=datetime.now(UTC)))
    append_audit(session, actor(user), "Provisioned account", "user", identifier, {"role": body.role})
    session.flush()
    return {"user": {"id": identifier, "email": email, "name": full_name, "role": body.role, "active": 1}}
