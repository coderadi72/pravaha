from fastapi import APIRouter, Depends, Request, Response

from backend.app.api.deps import CurrentUser, SessionDep, SettingsDep
from backend.app.core.security import COOKIE_NAME
from backend.app.schemas.contracts import AuthResponse, LoginRequest, OkResponse
from backend.app.services.auth_service import iso_date, safe_user, sign_in, sign_out
from backend.app.schemas.registration import SignupRequest, SignupResponse
from backend.app.services.registration_service import reserve_signup_attempt, submit_registration

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=SignupResponse, status_code=202, dependencies=[Depends(reserve_signup_attempt)])
def signup(body: SignupRequest, session: SessionDep, settings: SettingsDep):
    return submit_registration(session, settings, body)


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, request: Request, response: Response, session: SessionDep, settings: SettingsDep):
    result, token = sign_in(session, request, body)
    response.set_cookie(COOKIE_NAME, token, max_age=settings.session_ttl_seconds, httponly=True, secure=settings.session_cookie_secure, samesite=settings.session_cookie_samesite, path="/")
    return result


@router.post("/logout", response_model=OkResponse)
def logout(request: Request, response: Response, session: SessionDep, settings: SettingsDep):
    sign_out(session, request)
    response.delete_cookie(COOKIE_NAME, httponly=True, secure=settings.session_cookie_secure, samesite=settings.session_cookie_samesite, path="/")
    return {"ok": True}


@router.get("/me", response_model=AuthResponse)
def me(request: Request, user: CurrentUser):
    return {"user": safe_user(user), "expiresAt": iso_date(request.state.login_session.expires_at)}
