"""Transactional workflow orchestration for routes; scoring remains pure."""
from uuid import uuid4

from sqlalchemy import select

from backend.app.core.errors import ApiError
from backend.app.core.permissions import actor, leader_team, project_for, require_project_access, require_team_access, team_for
from backend.app.db.repository import load_workflow_data, lock_organization, persist_workflow_and_audit
from backend.app.models import FieldUpdate, User, WorkforceAssignment, ScheduleActivity
from backend.app.services.project_service import scoped_workspace
from backend.app.services.workflow_service import (
    assign_project_manager, assign_team, assign_team_leader, block_activity,
    change_match, complete_activity, confirm_match, mark_unmatched,
    rematch_field_update, request_information, request_planner_review,
    start_activity, submit_field_update, update_activity,
)


def _locked_data(session, user):
    lock_organization(session, user.organization_id)
    return load_workflow_data(session, user.organization_id)


def _enabled_user(session, user, identifier, role, code, message):
    if identifier and not session.scalar(select(User).where(User.id == identifier, User.organization_id == user.organization_id, User.role == role, User.active.is_(True), User.password_hash.is_not(None))):
        raise ApiError(400, code, message)


def set_project_manager(session, user, project_id, body):
    data = _locked_data(session, user)
    project_for(session, user, project_id)
    identifier = body.projectManagerId or None
    if not identifier and session.scalar(select(WorkforceAssignment.id).where(WorkforceAssignment.project_id == project_id, WorkforceAssignment.status == 'ACTIVE').limit(1)):
        raise ApiError(409, 'ACTIVE_ALLOCATION', 'A project with active workforce must retain a Project Manager.')
    _enabled_user(session, user, identifier, "PROJECT_MANAGER", "INVALID_MANAGER", "Project Manager account is not enabled for sign-in.")
    next_data = assign_project_manager(data, {"projectId": project_id, "projectManagerId": identifier, "actor": user.full_name, "actorUserId": user.id})
    persist_workflow_and_audit(session, next_data, actor(user), "Assigned Project Manager" if identifier else "Cleared Project Manager assignment", "project", project_id, {"projectManagerId": identifier})
    return {"data": scoped_workspace(session, user)}


def set_team_assignment(session, user, team_id, body):
    data = _locked_data(session, user)
    team = team_for(session, user, team_id)
    project_id = body.projectId or None
    assigned = body.assigned and project_id is not None
    if not assigned:
        project_id = team.project_id
    if not project_id:
        raise ApiError(400, "INVALID_PROJECT", "A project is required to unassign this team.")
    project_for(session, user, project_id)
    if (not assigned or team.project_id != project_id) and any(session.scalar(select(model.id).where(model.team_id == team_id).limit(1)) for model in (FieldUpdate, WorkforceAssignment, ScheduleActivity)):
        raise ApiError(409, 'TEAM_HISTORY', 'Teams with execution or workforce history cannot move projects. Create a new team and explicitly transfer workforce instead.')
    next_data = assign_team(data, {"projectId": project_id, "teamId": team_id, "assigned": assigned, "actor": user.full_name, "actorUserId": user.id})
    persist_workflow_and_audit(session, next_data, actor(user), "Assigned team to project" if assigned else "Unassigned team from project", "team", team_id, {"projectId": project_id if assigned else None})
    return {"data": scoped_workspace(session, user)}


def set_team_leader(session, user, team_id, body):
    data = _locked_data(session, user)
    team_for(session, user, team_id)
    identifier = body.teamLeaderId or None
    from backend.app.models import TeamLeaderAssignment
    previous = session.scalar(select(TeamLeaderAssignment.team_id).where(TeamLeaderAssignment.user_id == identifier)) if identifier else None
    protected = team_id if not identifier else previous if previous != team_id else None
    if protected and session.scalar(select(WorkforceAssignment.id).where(WorkforceAssignment.team_id == protected, WorkforceAssignment.status == 'ACTIVE').limit(1)):
        raise ApiError(409, 'ACTIVE_ALLOCATION', 'A team with active workforce must retain a Team Leader. Assign a replacement first.')
    _enabled_user(session, user, identifier, "TEAM_LEADER", "INVALID_TEAM_LEADER", "Team Leader account is not enabled for sign-in.")
    next_data = assign_team_leader(data, {"teamId": team_id, "teamLeaderId": identifier, "actor": user.full_name, "actorUserId": user.id})
    persist_workflow_and_audit(session, next_data, actor(user), "Assigned Team Leader" if identifier else "Cleared Team Leader assignment", "team", team_id, {"teamLeaderId": identifier})
    return {"data": scoped_workspace(session, user)}


def create_field_update(session, user, body):
    data = _locked_data(session, user)
    team = leader_team(session, user)
    if not team or not team.project_id:
        raise ApiError(403, "FORBIDDEN", "A team must be assigned before submitting field updates.")
    if not body.description.strip():
        raise ApiError(400, "INVALID_INPUT", "Field observation is invalid.")
    payload = body.model_dump(exclude_none=True)
    identifier = f"FU-{uuid4()}"
    next_data = submit_field_update(data, payload, {"teamId": team.id, "submittedBy": user.full_name, "submitterUserId": user.id, "id": identifier})
    update = next((item for item in next_data["fieldUpdates"] if item["id"] == identifier), None)
    if not update or update["teamId"] != team.id or update["projectId"] != team.project_id:
        raise ApiError(400, "INVALID_UPDATE", "Field update could not be accepted.")
    update.update({k: payload[k] for k in ("quantity", "unit", "remarks", "blocker", "crew", "equipment") if k in payload})
    persist_workflow_and_audit(session, next_data, actor(user), "Submitted field update", "field_update", update["id"], {"projectId": update["projectId"], "teamId": update["teamId"]}, update["id"])
    workspace = scoped_workspace(session, user)
    return {"fieldUpdate": next(item for item in workspace["fieldUpdates"] if item["id"] == identifier), "data": workspace}


def perform_activity_action(session, user, activity_id, body):
    data = _locked_data(session, user)
    activity = next((item for item in data["scheduleActivities"] if item["id"] == activity_id), None)
    if not activity:
        raise ApiError(404, "NOT_FOUND", "Schedule activity not found.")
    team = require_team_access(session, user, activity.get("teamId"))
    if activity["projectId"] != team.project_id:
        raise ApiError(403, "FORBIDDEN", "Schedule activity is outside your assigned project.")
    operations = {"start": start_activity, "update": update_activity, "complete": complete_activity, "block": block_activity}
    if body.action not in operations:
        raise ApiError(400, "INVALID_ACTION", "Activity action is invalid.")
    details = body.details.model_dump(exclude_none=True) if body.details else {}
    if details.get("blockedReason") is not None and not details["blockedReason"].strip():
        raise ApiError(400, "INVALID_INPUT", "blockedReason is invalid.")
    identifier = f"FU-{uuid4()}"
    next_data = operations[body.action](data, {"activityId": activity_id, "details": details, "submittedBy": user.full_name, "submitterUserId": user.id, "id": identifier})
    if not any(item["id"] == identifier for item in next_data["fieldUpdates"]):
        raise ApiError(400, "INVALID_ACTION", "Activity action details are invalid.")
    persist_workflow_and_audit(session, next_data, actor(user), f"Recorded activity {body.action}", "schedule_activity", activity_id, {"projectId": activity["projectId"], "teamId": team.id}, identifier)
    return {"data": scoped_workspace(session, user)}


def edit_field_update(session, user, update_id, body):
    data = _locked_data(session, user)
    update = next((item for item in data["fieldUpdates"] if item["id"] == update_id), None)
    if not update:
        raise ApiError(404, "NOT_FOUND", "Field update not found.")
    require_team_access(session, user, update.get("teamId"))
    owner = session.get(FieldUpdate, update_id)
    if owner.submitter_user_id != user.id:
        raise ApiError(403, "FORBIDDEN", "You can only edit your own field updates.")
    if update.get("reviewStatus") in {"reviewed", "action_required"}:
        raise ApiError(409, "INVALID_STATE", "Reviewed updates cannot be edited.")
    values = body.model_dump(exclude_unset=True)
    if any(value is None for value in values.values()):
        raise ApiError(400, "INVALID_INPUT", "Field update values are invalid.")
    for key, value in values.items():
        if isinstance(value, str):
            value = value.strip()
        if key == "description":
            if not value:
                raise ApiError(400, "INVALID_INPUT", "Field observation is invalid.")
            update["rawText"] = value
        else:
            update[key] = value
        if key in {"discipline", "location"}:
            update[f"reported{key.capitalize()}"] = value
    result = rematch_field_update(data, update_id, {"actor": user.full_name, "actorUserId": user.id})
    if result.get("error"):
        raise ApiError(400, "INVALID_UPDATE", result["error"])
    match = next((item for item in result["data"]["activityMatches"] if item["fieldUpdateId"] == update_id), {})
    persist_workflow_and_audit(session, result["data"], actor(user), "Edited field update and recalculated schedule suggestion", "field_update", update_id, {"scheduleActivityId": match.get("scheduleActivityId")}, update_id)
    workspace = scoped_workspace(session, user)
    return {"fieldUpdate": next(item for item in workspace["fieldUpdates"] if item["id"] == update_id), "data": workspace}


def review_field_update(session, user, update_id, decision, body):
    data = _locked_data(session, user)
    update = next((item for item in data["fieldUpdates"] if item["id"] == update_id), None)
    if not update:
        raise ApiError(404, "NOT_FOUND", "Field update not found.")
    require_project_access(session, user, update["projectId"])
    if decision == "request-review":
        next_data = request_planner_review(data, update_id, {"reviewer": user.full_name, "reviewerUserId": user.id})
        persist_workflow_and_audit(session, next_data, actor(user), "Requested planner review", "field_update", update_id, {})
        return {"data": scoped_workspace(session, user)}
    operations = {"confirm": confirm_match, "change-match": change_match, "unmatch": mark_unmatched, "request-info": request_information}
    if decision not in operations:
        raise ApiError(404, "NOT_FOUND", "API route not found.")
    result = operations[decision](data, {"updateId": update_id, "scheduleActivityId": body.scheduleActivityId, "reason": body.reason.strip(), "feedback": body.feedback.strip(), "reviewer": user.full_name, "reviewerUserId": user.id})
    if result.get("error"):
        raise ApiError(400, "INVALID_REVIEW", result["error"])
    reviewed = next(item for item in result["data"]["fieldUpdates"] if item["id"] == update_id)
    reviewed_match = next(item for item in result["data"]["activityMatches"] if item["fieldUpdateId"] == update_id)
    persist_workflow_and_audit(session, result["data"], actor(user), f"Review decision: {decision}", "field_update", update_id,
        {"projectId": update["projectId"], "scheduleActivityId": reviewed_match.get("scheduleActivityId"),
         "previous": {"reviewStatus": update.get("reviewStatus"), "feedback": update.get("pmFeedback"),
                      "scheduleActivityId": next((m.get("scheduleActivityId") for m in data["activityMatches"] if m["fieldUpdateId"] == update_id), None)},
         "new": {"reviewStatus": reviewed.get("reviewStatus"), "feedback": reviewed.get("pmFeedback"),
                 "actualStart": reviewed.get("actualStart"), "actualEnd": reviewed.get("actualEnd"), "progress": reviewed.get("progress")}})
    return {"message": result.get("message"), "shouldClose": result.get("shouldClose"), "data": scoped_workspace(session, user)}
