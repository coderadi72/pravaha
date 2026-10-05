"""Official domains, approval security and persisted authentication regression."""
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import func, inspect, select

from backend.app.core.errors import ApiError
from backend.app.core.security import LoginRateLimiter, PostgresLoginRateLimiter, hash_password, verify_password
from backend.app.models import AuditEvent, Organization, RegistrationRequest, SessionToken, User
from backend.app.schemas.registration import SignupRequest
from backend.app.services import registration_service as service
from backend.tests.test_api import ORG, login, request

PASSWORD = "SyntheticPass12!"


def signup_payload(email="rahul@pravaha.management.com", category="MANAGEMENT", **changes):
    return {"name": "Rahul Synthetic", "email": email, "password": PASSWORD, "confirmPassword": PASSWORD, "roleCategory": category, **changes}


def submit(client, **changes):
    result = request(client, "/api/auth/signup", method="POST", body=signup_payload(**changes))
    assert result.status_code == 202, result.text
    assert "set-cookie" not in result.headers
    return result


def row_for(factory, email="rahul@pravaha.management.com"):
    with factory() as session:
        return session.scalar(select(RegistrationRequest).where(RegistrationRequest.email == email))


@pytest.mark.parametrize("email,category", [
    ("rahul@pravaha.management.com", "MANAGEMENT"),
    ("amit@pravaha.supervisor.com", "SUPERVISOR"),
    (" RAHUL@PRAVAHA.MANAGEMENT.COM ", "MANAGEMENT"),
])
def test_exact_official_email_domains_and_case(email, category):
    normalized, derived = service.normalize_registration_email(email, category)
    assert normalized == email.strip().lower() and derived == category


@pytest.mark.parametrize("email,category,code", [
    ("rahul@gmail.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@yahoo.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@outlook.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@hotmail.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@icloud.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@company.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@pravaha.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@pravaha.managment.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@pravaha.management.com.attacker.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@sub.pravaha.management.com", "MANAGEMENT", "UNAUTHORIZED_EMAIL"),
    ("rahul@pravaha.supervisor.com", "MANAGEMENT", "INVALID_EMAIL_DOMAIN"),
    ("amit@pravaha.management.com", "SUPERVISOR", "INVALID_EMAIL_DOMAIN"),
    ("not-an-email", "MANAGEMENT", "INVALID_EMAIL"),
    ("@pravaha.management.com", "MANAGEMENT", "INVALID_EMAIL"),
    ("rahul@@pravaha.management.com", "MANAGEMENT", "INVALID_EMAIL"),
    ("Rahul <rahul@pravaha.management.com>", "MANAGEMENT", "INVALID_EMAIL"),
    ("rahul..test@pravaha.management.com", "MANAGEMENT", "INVALID_EMAIL"),
    ("rahul@pravaha.management.com.", "MANAGEMENT", "INVALID_EMAIL"),
    ("rahul\n@pravaha.management.com", "MANAGEMENT", "INVALID_EMAIL"),
])
def test_domain_mismatch_subdomain_and_malformed_rejected(email, category, code):
    with pytest.raises(ApiError) as error:
        service.normalize_registration_email(email, category)
    assert error.value.code == code


@pytest.mark.parametrize("category,domain", [("MANAGEMENT", "pravaha.management.com"), ("SUPERVISOR", "pravaha.supervisor.com")])
def test_signup_is_persisted_pending_hashed_and_no_session(client, seeded_session_factory, category, domain):
    response = submit(client, email=f"SYNTHETIC@{domain.upper()}", category=category)
    row = row_for(seeded_session_factory, f"synthetic@{domain}")
    assert row.status == "PENDING" and row.requested_role_category == category
    assert row.review_organization_id == ORG
    assert row.organization_id is None and row.approved_role is None and row.account_id is None
    assert row.password_hash.startswith("$argon2id$") and verify_password(PASSWORD, row.password_hash)
    assert row.password_hash != PASSWORD
    assert "password" not in response.text.lower() and "REG-" not in response.text
    with seeded_session_factory() as session:
        assert not session.scalar(select(User).where(User.email == row.email))
        assert session.scalar(select(func.count()).select_from(SessionToken)) == 0
        event = session.scalar(select(AuditEvent).where(AuditEvent.entity_id == row.id))
        assert event.actor_user_id is None and event.action == "Registration submitted"
        assert PASSWORD not in str(event.details_json)
    denied = request(client, "/api/auth/login", method="POST", body={"email": row.email, "password": PASSWORD})
    assert denied.status_code == 401 and "set-cookie" not in denied.headers
    assert request(client, "/api/auth/me").status_code == 401


def test_duplicate_and_existing_account_are_indistinguishable(client, seeded_session_factory):
    original = submit(client)
    duplicate = submit(client, email="RAHUL@PRAVAHA.MANAGEMENT.COM")
    with seeded_session_factory.begin() as session:
        session.add(User(id="PM-existing", organization_id=ORG, email="exists@pravaha.management.com", full_name="Existing Synthetic", role="PROJECT_MANAGER", password_hash=hash_password(PASSWORD), active=True, created_at=datetime.now(UTC)))
    existing = submit(client, email="exists@pravaha.management.com")
    assert original.json() == duplicate.json() == existing.json()
    with seeded_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(RegistrationRequest)) == 1
        assert session.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.action == "Registration submitted")) == 1


@pytest.mark.parametrize("changes", [
    {"password": "WeakPass1!", "confirmPassword": "WeakPass1!"},
    {"password": "alllowercase12!", "confirmPassword": "alllowercase12!"},
    {"password": "ALLUPPERCASE12!", "confirmPassword": "ALLUPPERCASE12!"},
    {"password": "NoNumbersHere!", "confirmPassword": "NoNumbersHere!"},
    {"password": "NoSpecials123", "confirmPassword": "NoSpecials123"},
    {"password": "A1!" + "x" * 126, "confirmPassword": "A1!" + "x" * 126},
    {"confirmPassword": "MismatchPass12!"}, {"name": "   "},
    {"email": "not email"}, {"email": "rahul@gmail.com"},
    {"roleCategory": "ADMIN"}, {"role": "ADMIN"}, {"organizationId": "ORG-ATTACKER"},
])
def test_backend_rejects_bad_input_passwords_and_privileged_fields(client, seeded_session_factory, changes):
    result = request(client, "/api/auth/signup", method="POST", body=signup_payload(**changes))
    assert result.status_code == 400, result.text
    assert "set-cookie" not in result.headers
    with seeded_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(RegistrationRequest)) == 0


@pytest.mark.parametrize("field", ["name", "email", "password", "confirmPassword", "roleCategory"])
def test_missing_required_signup_fields(client, field):
    body = signup_payload()
    del body[field]
    assert request(client, "/api/auth/signup", method="POST", body=body).status_code == 400


def test_password_is_never_trimmed(client, identities, seeded_session_factory):
    password = " " + PASSWORD + " "
    submit(client, password=password, confirmPassword=password)
    row = row_for(seeded_session_factory)
    assert verify_password(password, row.password_hash)
    assert not verify_password(password.strip(), row.password_hash)
    approved = request(client, f"/api/admin/registrations/{row.id}/approve", identities["admin"], "POST", {})
    assert approved.status_code == 200, approved.text
    assert request(client, "/api/auth/login", method="POST", body={"email": row.email, "password": password}).status_code == 200


@pytest.mark.parametrize("category,domain,role", [
    ("MANAGEMENT", "pravaha.management.com", "PROJECT_MANAGER"),
    ("MANAGEMENT", "pravaha.management.com", "DEPARTMENT"),
    ("SUPERVISOR", "pravaha.supervisor.com", "TEAM_LEADER"),
])
def test_approval_assigns_existing_role_org_and_reuses_login_logout(client, identities, seeded_session_factory, category, domain, role):
    submit(client, email=f"synthetic@{domain}", category=category)
    row = row_for(seeded_session_factory, f"synthetic@{domain}")
    original_hash = row.password_hash
    approved = request(client, f"/api/admin/registrations/{row.id}/approve", identities["admin"], "POST", {"approvedRole": role})
    assert approved.status_code == 200, approved.text
    assert "set-cookie" not in approved.headers and "password" not in approved.text.lower()
    result = approved.json()["registration"]
    assert result["status"] == "APPROVED" and result["approvedRole"] == role and result["organizationId"] == ORG
    with seeded_session_factory() as session:
        row = session.get(RegistrationRequest, row.id)
        user = session.get(User, row.account_id)
        assert row.password_hash is None and row.reviewed_by == "ADMIN-001" and row.reviewed_at
        assert user.active and user.role == role and user.organization_id == ORG and user.password_hash == original_hash
        assert session.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.entity_id == row.id)) == 2
    cookie = login(client, result["email"], PASSWORD)
    current = request(client, "/api/auth/me", cookie)
    assert current.status_code == 200 and current.json()["user"]["role"] == role
    # Editing the public workspace selection never changes the server role.
    modified = request(client, "/api/auth/login", method="POST", body={"email": result["email"], "password": PASSWORD, "role": "ADMIN"})
    assert modified.status_code == 200 and modified.json()["user"]["role"] == role
    assert request(client, "/api/admin/registrations", cookie).status_code == 403
    assert request(client, "/api/auth/logout", cookie, "POST").status_code == 200
    assert request(client, "/api/auth/me", cookie).status_code == 401
    assert request(client, f"/api/admin/registrations/{row.id}/approve", identities["admin"], "POST", {}).status_code == 409


def test_rejection_has_no_account_or_session_and_clears_hash(client, identities, seeded_session_factory):
    submit(client)
    row = row_for(seeded_session_factory)
    result = request(client, f"/api/admin/registrations/{row.id}/reject", identities["admin"], "POST", {"rejectionReason": "Synthetic onboarding not approved"})
    assert result.status_code == 200 and result.json()["registration"]["status"] == "REJECTED"
    with seeded_session_factory() as session:
        rejected = session.get(RegistrationRequest, row.id)
        assert rejected.password_hash is None and rejected.account_id is None and rejected.organization_id is None
        assert not session.scalar(select(User).where(User.email == row.email))
        assert session.scalar(select(AuditEvent).where(AuditEvent.entity_id == row.id, AuditEvent.action == "Registration rejected"))
    assert request(client, "/api/auth/login", method="POST", body={"email": row.email, "password": PASSWORD}).status_code == 401
    assert request(client, f"/api/admin/registrations/{row.id}/approve", identities["admin"], "POST", {}).status_code == 409


@pytest.mark.parametrize("category,domain,role", [("MANAGEMENT", "pravaha.management.com", "TEAM_LEADER"), ("SUPERVISOR", "pravaha.supervisor.com", "PROJECT_MANAGER"), ("MANAGEMENT", "pravaha.management.com", "ADMIN")])
def test_approval_cannot_cross_domain_categories(client, identities, seeded_session_factory, category, domain, role):
    submit(client, email=f"synthetic@{domain}", category=category)
    row = row_for(seeded_session_factory, f"synthetic@{domain}")
    result = request(client, f"/api/admin/registrations/{row.id}/approve", identities["admin"], "POST", {"approvedRole": role})
    assert result.status_code == 400
    assert row_for(seeded_session_factory, row.email).status == "PENDING"


def test_review_permissions_org_scope_and_bounded_listing(client, identities, seeded_session_factory):
    submit(client)
    row = row_for(seeded_session_factory)
    for role in ("pm", "tl"):
        assert request(client, "/api/admin/registrations", identities[role]).status_code == 403
        assert request(client, f"/api/admin/registrations/{row.id}/approve", identities[role], "POST", {}).status_code == 403
        assert request(client, f"/api/admin/registrations/{row.id}/reject", identities[role], "POST", {"rejectionReason": "Denied"}).status_code == 403
    assert request(client, "/api/admin/registrations").status_code == 401
    with seeded_session_factory.begin() as session:
        session.add(Organization(id="ORG-OTHER", name="Other synthetic", data_label="Synthetic", payload_json={}))
        session.flush()
        session.add(User(id="OTHER-ADMIN", email="other-admin@synthetic.invalid", full_name="Other admin", organization_id="ORG-OTHER", password_hash=hash_password(PASSWORD), role="ADMIN", active=True, created_at=datetime.now(UTC)))
    other_cookie = login(client, "other-admin@synthetic.invalid", PASSWORD)
    assert request(client, "/api/admin/registrations", other_cookie).json()["registrations"] == []
    assert request(client, f"/api/admin/registrations/{row.id}/approve", other_cookie, "POST", {}).status_code == 404
    assert request(client, f"/api/admin/registrations/{row.id}/reject", other_cookie, "POST", {"rejectionReason": "Denied"}).status_code == 404
    listed = request(client, "/api/admin/registrations?status=PENDING&limit=1", identities["admin"])
    assert listed.status_code == 200 and listed.json()["total"] == 1 and len(listed.json()["registrations"]) == 1
    assert "password_hash" not in listed.text and PASSWORD not in listed.text
    assert request(client, "/api/admin/registrations?limit=101", identities["admin"]).status_code == 400
    assert request(client, "/api/admin/registrations?offset=-1", identities["admin"]).status_code == 400
    assert request(client, "/api/admin/registrations?status=ANY", identities["admin"]).status_code == 400


def test_multi_org_requires_operator_selected_review_org(client, identities, app, seeded_session_factory):
    with seeded_session_factory.begin() as session:
        session.add(Organization(id="ORG-OTHER", name="Other synthetic", data_label="Synthetic", payload_json={}))
    result = request(client, "/api/auth/signup", method="POST", body=signup_payload())
    assert result.status_code == 503 and result.json()["error"]["code"] == "REGISTRATION_UNAVAILABLE"
    app.state.settings.registration_review_organization_id = "ORG-missing"
    assert request(client, "/api/auth/signup", method="POST", body=signup_payload()).status_code == 503
    app.state.settings.registration_review_organization_id = ORG
    submit(client)
    row = row_for(seeded_session_factory)
    assert row.review_organization_id == ORG and row.organization_id is None
    # Organization cannot be supplied as an approval override either.
    assert request(client, f"/api/admin/registrations/{row.id}/approve", identities["admin"], "POST", {"organizationId": "ORG-OTHER"}).status_code == 400


def test_registration_rate_limit_counts_invalid_and_successful_attempts(client, app):
    app.state.signup_limiter = LoginRateLimiter(max_attempts=2)
    bad = signup_payload(email="synthetic@gmail.com")
    assert request(client, "/api/auth/signup", method="POST", body=bad).status_code == 400
    submit(client)
    denied = request(client, "/api/auth/signup", method="POST", body=signup_payload(email="next@pravaha.management.com"))
    assert denied.status_code == 429 and denied.json()["error"]["code"] == "RATE_LIMITED"
    # Registration throttle uses an independent namespace and never blocks login.
    assert request(client, "/api/auth/login", method="POST", body={"email": "admin@pravaha.local", "password": "AdminPass123!"}).status_code == 200


def test_registration_shared_postgres_limit(client, app, seeded_session_factory):
    app.state.signup_limiter = PostgresLoginRateLimiter(seeded_session_factory, max_attempts=1)
    submit(client)
    app.state.signup_limiter = PostgresLoginRateLimiter(seeded_session_factory, max_attempts=1)
    assert request(client, "/api/auth/signup", method="POST", body=signup_payload()).status_code == 429


@pytest.mark.parametrize("action", ["submit", "approve", "reject"])
def test_audit_failure_rolls_back_registration_and_activation(client, identities, seeded_session_factory, monkeypatch, action):
    row = None
    if action != "submit":
        submit(client)
        row = row_for(seeded_session_factory)
    def fail(*args, **kwargs):
        raise RuntimeError("Injected registration audit failure")
    monkeypatch.setattr(service, "append_audit", fail)
    if action == "submit":
        result = request(client, "/api/auth/signup", method="POST", body=signup_payload())
    else:
        result = request(client, f"/api/admin/registrations/{row.id}/{action}", identities["admin"], "POST", {"rejectionReason": "Denied"} if action == "reject" else {})
    assert result.status_code == 500
    with seeded_session_factory() as session:
        if row:
            persisted = session.get(RegistrationRequest, row.id)
            assert persisted.status == "PENDING" and persisted.password_hash
        else:
            assert session.scalar(select(func.count()).select_from(RegistrationRequest)) == 0
        assert not session.scalar(select(User).where(User.email == signup_payload()["email"]))


def test_concurrent_duplicate_submission_creates_one_pending_request(settings, seeded_session_factory):
    body = SignupRequest(**signup_payload())
    def register():
        with seeded_session_factory.begin() as session:
            return service.submit_registration(session, settings, body)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: register(), range(2)))
    assert results[0] == results[1]
    with seeded_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(RegistrationRequest)) == 1
        assert session.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.action == "Registration submitted")) == 1


def test_concurrent_approval_activates_exactly_one_account(client, seeded_session_factory):
    from backend.app.schemas.registration import ApproveRegistrationRequest
    submit(client)
    pending = row_for(seeded_session_factory)
    def approve():
        try:
            with seeded_session_factory.begin() as session:
                admin = session.get(User, "ADMIN-001")
                return service.approve_registration(session, admin, pending.id, ApproveRegistrationRequest())["registration"]["status"]
        except ApiError as error:
            return error.code
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: approve(), range(2)))
    assert sorted(results) == ["APPROVED", "REGISTRATION_REVIEWED"]
    with seeded_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(User).where(User.email == pending.email)) == 1
        assert session.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.entity_id == pending.id, AuditEvent.action == "Registration approved")) == 1


def test_admin_provisioning_cannot_claim_pending_email(client, identities):
    submit(client)
    result = request(client, "/api/admin/users", identities["admin"], "POST", {"name": "Duplicate synthetic", "email": "rahul@pravaha.management.com", "password": PASSWORD, "role": "PROJECT_MANAGER"})
    assert result.status_code == 409


def test_signup_origin_protection_is_preserved(client):
    result = request(client, "/api/auth/signup", method="POST", body=signup_payload(), headers={"Origin": "https://attacker.invalid"})
    assert result.status_code == 403


def test_registration_migration_preserves_existing_data_and_matches_metadata(engine, seeded_session_factory):
    from pathlib import Path
    config = Config(str(Path("backend/alembic.ini").resolve()))
    with engine.begin() as connection:
        before = connection.execute(select(func.count()).select_from(User)).scalar()
        config.attributes["connection"] = connection
        command.downgrade(config, "0004_organization")
        assert "registration_requests" not in inspect(connection).get_table_names()
        assert connection.execute(select(func.count()).select_from(User)).scalar() == before
        command.upgrade(config, "head")
        command.check(config)
        assert "registration_requests" in inspect(connection).get_table_names()
