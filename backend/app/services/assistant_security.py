"""Fresh authorization and stateless context binding. No conversation persistence."""
import base64
import hashlib
import hmac
import json
import re
import time
from sqlalchemy import select
from backend.app.core.errors import ApiError
from backend.app.core.permissions import leader_team, require_project_access, project_for
from backend.app.models import Organization, ProjectManagerAssignment, TeamLeaderAssignment
from backend.app.services.auth_service import authenticate_session


def private_prose(text):
    """Content marker only, never a secret value in diagnostics."""
    return bool(re.search(r"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|```|(?:hidden|system) (?:system )?(?:prompt|instructions|rules)|internal (?:system )?(?:instructions|rules|configuration)|private source code|backend[/\\]\.env|Question/history/records are untrusted DATA|No tools/DB|PM: concise decisions; TL:|ONLY JSON:|(?:DATABASE_URL|JWT_SECRET|SESSION_SECRET|GROQ_API_KEY|NVIDIA_API_KEY)\s*=|\b(?:api[_ -]?key|password|secret|bearer|session[_ -]?token)\s*[:=]\s*\S+|(?:postgres(?:ql)?|https?)://[^\s]*:[^\s]*@|^\s*(?:from\s+\w+\s+import\b|import\s+\w+|def\s+\w+\s*\(|class\s+\w+\s*[:(]|function\s+\w+\s*\(|const\s+\w+\s*=)|^\s*(?:if|elif|for|while|try|except)\b[^\n]{0,120}:\s*\n\s+(?:return|raise|yield|print|await)\b)", text, re.I | re.M))


def authorize(session, request, project_id):
    user, login = authenticate_session(session, request)
    request.state.role = user.role
    if user.role not in {"ADMIN", "PROJECT_MANAGER", "TEAM_LEADER"}:
        raise ApiError(403, "FORBIDDEN", "Assistant access requires Admin, assigned PM or Team Leader access.")
    team = None
    assignment = None
    project = None
    if user.role == "TEAM_LEADER":
        team = leader_team(session, user)
        if not team or not team.project_id or project_id != team.project_id:
            raise ApiError(403, "FORBIDDEN", "Select your assigned team's project.")
        project = project_for(session, user, project_id)
        assignment = session.get(TeamLeaderAssignment, team.id)
    elif project_id:
        project = require_project_access(session, user, project_id)
        assignment = session.get(ProjectManagerAssignment, project_id) if user.role == "PROJECT_MANAGER" else None
    elif user.role != "ADMIN":
        raise ApiError(400, "CONTEXT_REQUIRED", "Select an authorized project.")
    org = session.get(Organization, user.organization_id)
    binding = {"user": user.id, "org": user.organization_id, "role": user.role, "project": project_id,
               "team": team.id if team else None, "assignment": assignment.assigned_at.isoformat() if assignment else None}
    public = {"organizationId": org.id, "organizationName": org.name, "projectId": project_id,
              "projectName": project.name if project else None, "teamId": team.id if team else None,
              "scope": "TEAM" if team else "PROJECT" if project else "ORGANIZATION",
              "dataLabel": org.data_label, "role": user.role}
    return user, login, binding, public


def sign(payload, secret, purpose, ttl):
    raw = json.dumps({"purpose": purpose, "expires": int(time.time()) + ttl, **payload}, separators=(",", ":"), ensure_ascii=False).encode()
    data = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    return data + "." + signature


def verify(token, secret, purpose, binding):
    try:
        if len(token) > 30000:
            raise ValueError()
        data, signature = token.rsplit(".", 1)
        expected = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError()
        payload = json.loads(base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)))
        if payload["purpose"] != purpose or payload["expires"] <= time.time() or payload["binding"] != binding:
            raise ValueError()
        return payload
    except (ValueError, KeyError, TypeError, UnicodeError) as exc:
        raise ApiError(409, "CONVERSATION_EXPIRED", "Assistant context changed or expired. Start a new conversation.") from exc
