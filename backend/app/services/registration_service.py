"""Official-domain registration with organization-scoped administrator approval."""
from datetime import UTC, datetime
import re
from uuid import uuid4

from fastapi import Request
from sqlalchemy import func, or_, select, text

from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor
from backend.app.core.security import digest_token, hash_password, is_valid_password
from backend.app.db.repository import append_audit, lock_organization
from backend.app.models import Organization, RegistrationRequest, User
from backend.app.services.auth_service import iso_date

DOMAIN_CATEGORIES = {
    "pravaha.management.com": "MANAGEMENT",
    "pravaha.supervisor.com": "SUPERVISOR",
}
ALLOWED_ROLES = {"MANAGEMENT": {"PROJECT_MANAGER", "DEPARTMENT"}, "SUPERVISOR": {"TEAM_LEADER"}}
SUBMISSION_MESSAGE = "Your registration request has been submitted for administrator approval. If an account or registration already exists for this email, please contact your organization administrator."
DUPLICATE_MESSAGE = "If an account or registration already exists for this email, please contact your organization administrator."


def normalize_registration_email(value, requested_category):
    email = value.strip().lower()
    # Explicit ASCII dot-atom mailbox syntax. Display names, quoted local parts,
    # Unicode lookalikes, multiple @ characters and trailing dots are rejected.
    if len(email) > 254 or not re.fullmatch(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z0-9]+", email) or len(email.split("@", 1)[0]) > 64:
        raise ApiError(400, "INVALID_EMAIL", "Email address is invalid.")
    domain = email.split("@", 1)[1]
    category = DOMAIN_CATEGORIES.get(domain)
    if not category:
        raise ApiError(400, "UNAUTHORIZED_EMAIL", "Please use your authorized PRAVAHA work email.")
    if requested_category != category:
        raise ApiError(400, "INVALID_EMAIL_DOMAIN", "This email domain is not valid for the selected role.")
    return email, category


def reserve_signup_attempt(request: Request):
    peer = request.client.host if request.client else "unknown"
    key = f"signup:{peer}"
    # The PostgreSQL limiter atomically reserves; memory reservations use one
    # lock around check + record so concurrent requests cannot bypass the bound.
    with request.app.state.signup_rate_lock:
        limiter = request.app.state.signup_limiter
        if limiter.is_limited(key):
            raise ApiError(429, "RATE_LIMITED", "Too many registration attempts. Try again later.")
        limiter.record_failure(key)


def lock_registration_email(session, email):
    # Shared with Admin provisioning. Serialize email claims across organizations
    # in addition to the database's case-insensitive unique constraints.
    key = int(digest_token("registration:" + email)[:16], 16)
    if key >= 2 ** 63:
        key -= 2 ** 64
    session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})


def review_organization(session, settings):
    configured = settings.registration_review_organization_id.strip()
    if configured:
        organization = session.get(Organization, configured)
        if organization:
            return organization.id
    else:
        ids = list(session.scalars(select(Organization.id).order_by(Organization.id).limit(2)))
        if len(ids) == 1:
            return ids[0]
    # Organization selection is operator configuration, never public input.
    raise ApiError(503, "REGISTRATION_UNAVAILABLE", "Registration is unavailable right now. Please contact your organization administrator.")


def existing_account(session, email):
    return session.scalar(select(User.id).where(or_(func.lower(User.email) == email, func.lower(User.login_id) == email)))


def submit_registration(session, settings, body):
    name = body.name.strip()
    if not name or any(ord(char) < 32 for char in name):
        raise ApiError(400, "INVALID_INPUT", "Full name is required.")
    email, category = normalize_registration_email(body.email, body.roleCategory)
    if not is_valid_password(body.password):
        raise ApiError(400, "WEAK_PASSWORD", "Password must be 12-128 characters and include uppercase, lowercase, number, and special character.")
    if body.password != body.confirmPassword:
        raise ApiError(400, "PASSWORD_MISMATCH", "Passwords do not match.")
    # Hash on duplicate submissions too: both outcomes have the same expensive
    # work and identical status/body, without disclosing account existence.
    password_hash = hash_password(body.password)
    organization_id = review_organization(session, settings)
    lock_organization(session, organization_id)
    lock_registration_email(session, email)
    duplicate = existing_account(session, email) or session.scalar(select(RegistrationRequest.id).where(func.lower(RegistrationRequest.email) == email))
    if not duplicate:
        now = datetime.now(UTC)
        registration = RegistrationRequest(id=f"REG-{uuid4()}", full_name=name, email=email, password_hash=password_hash, requested_role_category=category, status="PENDING", review_organization_id=organization_id, created_at=now, updated_at=now)
        session.add(registration)
        session.flush()
        append_audit(session, {"id": None, "fullName": "PRAVAHA registration", "organizationId": organization_id}, "Registration submitted", "registration_request", registration.id, {"category": category, "status": "PENDING"})
    return {"status": "SUBMITTED", "message": SUBMISSION_MESSAGE}


def safe_registration(row):
    return {"id": row.id, "name": row.full_name, "email": row.email, "emailDomain": row.email.split("@", 1)[1], "requestedRoleCategory": row.requested_role_category, "status": row.status, "reviewOrganizationId": row.review_organization_id, "approvedRole": row.approved_role, "organizationId": row.organization_id, "createdAt": iso_date(row.created_at), "updatedAt": iso_date(row.updated_at), "reviewedAt": iso_date(row.reviewed_at) if row.reviewed_at else None, "rejectionReason": row.rejection_reason}


def list_registrations(session, user, status=None, limit=25, offset=0):
    filters = [RegistrationRequest.review_organization_id == user.organization_id]
    if status:
        filters.append(RegistrationRequest.status == status)
    total = session.scalar(select(func.count()).select_from(RegistrationRequest).where(*filters))
    rows = session.scalars(select(RegistrationRequest).where(*filters).order_by(RegistrationRequest.created_at.desc(), RegistrationRequest.id).limit(limit).offset(offset))
    return {"registrations": [safe_registration(row) for row in rows], "total": total, "limit": limit, "offset": offset}


def pending_registration(session, user, registration_id):
    lock_organization(session, user.organization_id)
    row = session.scalar(select(RegistrationRequest).where(RegistrationRequest.id == registration_id, RegistrationRequest.review_organization_id == user.organization_id).with_for_update())
    if not row:
        raise ApiError(404, "NOT_FOUND", "Registration request not found.")
    if row.status != "PENDING":
        raise ApiError(409, "REGISTRATION_REVIEWED", "This registration request has already been reviewed.")
    return row


def approve_registration(session, user, registration_id, body):
    row = pending_registration(session, user, registration_id)
    email, category = normalize_registration_email(row.email, row.requested_role_category)
    role = body.approvedRole or ("PROJECT_MANAGER" if category == "MANAGEMENT" else "TEAM_LEADER")
    if role not in ALLOWED_ROLES[category]:
        raise ApiError(400, "INVALID_ROLE", "The selected role is not allowed for this registration category.")
    lock_registration_email(session, email)
    if existing_account(session, email):
        raise ApiError(409, "DUPLICATE_EMAIL", DUPLICATE_MESSAGE)
    if not row.password_hash:
        raise ApiError(409, "REGISTRATION_REVIEWED", "This registration request cannot be activated.")
    now = datetime.now(UTC)
    prefix = {"PROJECT_MANAGER": "PM", "DEPARTMENT": "DEPT", "TEAM_LEADER": "TL"}[role]
    account_id = f"{prefix}-{uuid4()}"
    session.add(User(id=account_id, organization_id=user.organization_id, email=email, full_name=row.full_name, role=role, password_hash=row.password_hash, active=True, created_at=now))
    session.flush()
    row.status, row.approved_role, row.organization_id, row.account_id = "APPROVED", role, user.organization_id, account_id
    row.reviewed_by, row.reviewed_at, row.updated_at, row.password_hash = user.id, now, now, None
    session.flush()
    append_audit(session, actor(user), "Registration approved", "registration_request", row.id, {"category": category, "status": "APPROVED", "role": role, "accountId": account_id})
    return {"registration": safe_registration(row), "message": "Your account has been approved. You can now sign in."}


def reject_registration(session, user, registration_id, body):
    reason = body.rejectionReason.strip()
    if not reason:
        raise ApiError(400, "INVALID_INPUT", "A rejection reason is required.")
    row = pending_registration(session, user, registration_id)
    now = datetime.now(UTC)
    row.status, row.password_hash, row.rejection_reason = "REJECTED", None, reason
    row.reviewed_by, row.reviewed_at, row.updated_at = user.id, now, now
    session.flush()
    append_audit(session, actor(user), "Registration rejected", "registration_request", row.id, {"category": row.requested_role_category, "status": "REJECTED"})
    return {"registration": safe_registration(row), "message": "Your registration request was not approved. Please contact your organization administrator."}
