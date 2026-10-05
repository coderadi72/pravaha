from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.core.errors import ApiError
from backend.app.models import User
from backend.app.services.auth_service import authenticate_session


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session(request: Request):
    """Commit before sending a response; any workflow/audit failure rolls back."""
    with request.app.state.session_factory() as session:
        session.info["settings"] = request.app.state.settings
        with session.begin():
            yield session


SessionDep = Annotated[Session, Depends(get_session, scope="function")]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_current_user(request: Request, session: SessionDep) -> User:
    user, login_session = authenticate_session(session, request)
    request.state.login_session = login_session
    request.state.role = user.role
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def admin_user(user: CurrentUser) -> User:
    if user.role != "ADMIN":
        raise ApiError(403, "FORBIDDEN", "You are not authorized to perform this action.")
    return user


def manager_user(user: CurrentUser) -> User:
    if user.role != "PROJECT_MANAGER":
        raise ApiError(403, "FORBIDDEN", "You are not authorized to perform this action.")
    return user


def leader_user(user: CurrentUser) -> User:
    if user.role != "TEAM_LEADER":
        raise ApiError(403, "FORBIDDEN", "You are not authorized to access team data.")
    return user


AdminUser = Annotated[User, Depends(admin_user)]
ManagerUser = Annotated[User, Depends(manager_user)]
LeaderUser = Annotated[User, Depends(leader_user)]
