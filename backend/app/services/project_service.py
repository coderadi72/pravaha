"""Organization, project and team scope; candidate/history redaction."""
from copy import deepcopy
import re

from sqlalchemy import select

from backend.app.core.permissions import leader_team
from backend.app.core.errors import ApiError
from backend.app.db.repository import load_workflow_data
from backend.app.models import ProjectManagerAssignment


def scoped_workspace(session, user):
    if user.role not in {'ADMIN', 'PROJECT_MANAGER', 'TEAM_LEADER'}:
        raise ApiError(403, 'FORBIDDEN', 'This account has no project-management workspace permissions.')
    all_data = load_workflow_data(session, user.organization_id)
    if user.role == "ADMIN":
        return all_data
    workspace = deepcopy(all_data)
    if user.role == "PROJECT_MANAGER":
        projects = set(session.scalars(select(ProjectManagerAssignment.project_id).where(ProjectManagerAssignment.user_id == user.id)))
        workspace["users"] = [item for item in all_data["users"] if item["id"] == user.id]
        workspace["projectManagers"] = [item for item in all_data["projectManagers"] if item["id"] == user.id]
        workspace["projects"] = [item for item in all_data["projects"] if item["id"] in projects]
        workspace["teams"] = [item for item in all_data["teams"] if item.get("projectId") in projects]
        teams = {item["id"] for item in workspace["teams"]}
        workspace["teamLeaders"] = [item for item in all_data["teamLeaders"] if item.get("teamId") in teams]
        workspace["scheduleActivities"] = [item for item in all_data["scheduleActivities"] if item.get("projectId") in projects]
        workspace["fieldUpdates"] = [item for item in all_data["fieldUpdates"] if item.get("projectId") in projects]
    else:
        team = leader_team(session, user)
        workspace["users"], workspace["projectManagers"] = [], []
        workspace["teamLeaders"] = [item for item in all_data["teamLeaders"] if item["id"] == user.id]
        workspace["projects"] = [item for item in all_data["projects"] if team and item["id"] == team.project_id]
        workspace["teams"] = [item for item in all_data["teams"] if team and item["id"] == team.id]
        workspace["scheduleActivities"] = [item for item in all_data["scheduleActivities"] if team and item.get("teamId") == team.id and item.get("projectId") == team.project_id]
        workspace["fieldUpdates"] = [item for item in all_data["fieldUpdates"] if item.get('submitterUserId') == user.id or (team and item.get("teamId") == team.id and item.get("projectId") == team.project_id)]
    update_ids = {item["id"] for item in workspace["fieldUpdates"]}
    allowed = {item["id"] for item in workspace["scheduleActivities"]}
    workspace["activityMatches"] = [item for item in all_data["activityMatches"] if item.get("fieldUpdateId") in update_ids]
    workspace["reviewItems"] = [item for item in all_data["reviewItems"] if item.get("fieldUpdateId") in update_ids]
    workspace["scheduleActivityContributions"] = [item for item in all_data["scheduleActivityContributions"] if item.get("scheduleActivityId") in allowed]
    workspace["organizationActivity"] = []
    restricted_updates = set()
    for match in workspace["activityMatches"]:
        original = match.get("candidates", [])
        candidates = [item for item in original if item.get("scheduleActivityId") in allowed]
        ids = [match.get(key) for key in ("recommendedMatchId", "scheduleActivityId", "reportedActivityId")] + match.get("alternatives", [])
        restricted = len(candidates) != len(original) or any(item and item not in allowed for item in ids)
        match["candidates"] = candidates
        for key in ("recommendedMatchId", "scheduleActivityId", "reportedActivityId"):
            if match.get(key) not in allowed:
                match[key] = None
        match["alternatives"] = [item for item in match.get("alternatives", []) if item in allowed]
        if restricted:
            restricted_updates.add(match["fieldUpdateId"])
            match.update(recommendationRestricted=True, evidence=[], matchReason="Recommendation details are available to the assigned Project Manager.", unmatchReason="Waiting for PM review of the submitted field information.")
    for update in workspace["fieldUpdates"]:
        if user.role == "TEAM_LEADER" or update["id"] in restricted_updates:
            for event in update.get("reviewHistory", []):
                if not event.get("actorUserId") and re.fullmatch(r"PRAVAHA (?:demo )?matcher", event.get("actor", "")):
                    event["action"] = "Schedule recommendation generated; details are available to the assigned Project Manager."
    workspace["scheduleActivityBaselines"] = {key: value for key, value in all_data["scheduleActivityBaselines"].items() if key in allowed}
    for review in workspace["reviewItems"]:
        if review.get("fieldUpdateId") in restricted_updates and not review.get("reviewerUserId"):
            review["reason"] = "Recommendation details are available to the assigned Project Manager."
    return workspace
