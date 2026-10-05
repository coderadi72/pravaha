"""Pure workflow mutations shared by API services, independent of the database.

The persisted camelCase contract is retained from Phase 7. Every public mutator
copies its input. Authorization and atomic persistence belong to the API and DB
services, while these functions enforce the workflow's domain invariants.
"""

from copy import deepcopy
from datetime import datetime, timezone
from math import isfinite
from uuid import uuid4

from .matching_service import analyze_field_activity

TRACKED_ACTIVITY_FIELDS = ("actualStart", "actualEnd", "progress", "status", "blockedReason", "observation")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _new_id(prefix):
    return f"{prefix}-{uuid4()}"


def _find(items, key, value):
    return next((item for item in items if item.get(key) == value), None)


def _nullish(value, fallback):
    return fallback if value is None else value


def _valid_progress(progress):
    return progress is None or isinstance(progress, (int, float)) and not isinstance(progress, bool) and isfinite(progress) and 0 <= progress <= 100


def _number_text(value):
    # JSON/Pydantic may deserialize integral progress as a float. JavaScript
    # Number stringification still displays 45 rather than 45.0 in history.
    return str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)


def _capture_state(activity):
    return {field: activity.get(field) for field in TRACKED_ACTIVITY_FIELDS}


def _apply_contributions(data, activity_id):
    activity = _find(data["scheduleActivities"], "id", activity_id)
    if activity is None:
        return
    state = deepcopy(data.get("scheduleActivityBaselines", {}).get(activity_id, _capture_state(activity)))
    contributions = sorted((item for item in data["scheduleActivityContributions"] if item["scheduleActivityId"] == activity_id), key=lambda item: item["recordedAt"])
    for contribution in contributions:
        state.update(contribution["state"])
    activity.update(state)


def _remove_contribution(data, field_update_id, schedule_activity_id=None):
    affected = {item["scheduleActivityId"] for item in data["scheduleActivityContributions"] if item["fieldUpdateId"] == field_update_id}
    if schedule_activity_id:
        affected.add(schedule_activity_id)
    data["scheduleActivityContributions"] = [item for item in data["scheduleActivityContributions"] if item["fieldUpdateId"] != field_update_id]
    for activity_id in affected:
        _apply_contributions(data, activity_id)


def _match_contribution(update, activity_id, recorded_at):
    observation = update.get("observation") or ""
    return {"fieldUpdateId": update["id"], "scheduleActivityId": activity_id, "recordedAt": recorded_at, "state": {
        "actualStart": update.get("actualStart"), "actualEnd": update.get("actualEnd"),
        "progress": _nullish(update.get("progress"), 100 if update.get("actualEnd") else 0),
        "status": "Complete" if update.get("actualEnd") else "In Progress",
        "blockedReason": observation[9:].split(".")[0] if observation.startswith("Blocked:") else "", "observation": observation,
    }}


def _schedule_actual_start(schedule):
    if not schedule or not schedule.get("actualStart"):
        return None
    actual_start = schedule["actualStart"]
    return actual_start if len(actual_start) > 10 else actual_start + "T08:00:00"


def _analyze_update(data, update, now):
    return analyze_field_activity(update["rawText"], data["scheduleActivities"], {"projectId": update["projectId"], "discipline": update.get("reportedDiscipline"), "location": update.get("reportedLocation"), "generatedAt": now})


def _recommendation_history(match):
    recommended = match.get("recommendedMatchId") or "PM selection required"
    return {"actorUserId": None, "actor": "PRAVAHA matcher", "action": f"{match['matcherVersion']}: {match['recommendationStatus']} · {match['confidence']}% confidence · {recommended}", "occurredAt": match["generatedAt"]}


def enrich_match_intelligence(data, generated_at=None):
    result = deepcopy(data)
    generated_at = generated_at or _now()
    for update in result["fieldUpdates"]:
        analysis = _analyze_update(result, update, generated_at)
        update.update(extractedActivity=analysis["extractedActivity"], confidence=analysis["match"]["confidence"])
        match = _find(result["activityMatches"], "fieldUpdateId", update["id"])
        if match is not None:
            match.update(analysis["match"])
    return result


def rematch_field_update(data, update_id, context=None):
    result, context = deepcopy(data), context or {}
    update = _find(result["fieldUpdates"], "id", update_id)
    match = _find(result["activityMatches"], "fieldUpdateId", update_id)
    if update is None or match is None:
        return {"data": result, "error": "Field update or activity match could not be found."}
    now = context.get("now") or _now()
    _remove_contribution(result, update_id, match.get("scheduleActivityId"))
    if (update.get("progress") or 0) < 100:
        update["actualEnd"] = None
    analysis = _analyze_update(result, update, now)
    schedule = _find(result["scheduleActivities"], "id", analysis["match"]["recommendedMatchId"])
    match_status = "review_required" if schedule or analysis["match"]["recommendationStatus"] == "ambiguous" else "unmatched"
    update.update({
        "activity": analysis["extractedActivity"]["activityName"], "discipline": analysis["extractedActivity"]["discipline"], "location": analysis["extractedActivity"]["location"],
        "confidence": analysis["match"]["confidence"], "matchStatus": match_status, "reviewStatus": "needs_review" if match_status == "review_required" else "unmatched",
        "status": "Submitted", "pmFeedback": "", "reviewer": None, "reviewerUserId": None, "reviewedAt": None, "extractedActivity": analysis["extractedActivity"],
        "reviewHistory": [*(update.get("reviewHistory") or []), _recommendation_history(analysis["match"]), {"actorUserId": context.get("actorUserId"), "actor": _nullish(context.get("actor"), update.get("submittedBy")), "action": "Field update edited; schedule suggestion recalculated", "occurredAt": now}],
    })
    schedule_id = schedule["id"] if schedule else None
    match.update(analysis["match"])
    match.update({"scheduleActivityId": schedule_id, "matchStatus": match_status, "matchedBy": None, "matchedByUserId": None, "reviewedAt": None, "reviewComment": None, "alternatives": [item["scheduleActivityId"] for item in analysis["match"]["candidates"] if item["scheduleActivityId"] != schedule_id]})
    review = _find(result["reviewItems"], "fieldUpdateId", update_id)
    next_review = {"id": review["id"] if review else _new_id("REV"), "fieldUpdateId": update_id, "reason": analysis["match"]["unmatchReason"], "confidence": analysis["match"]["confidence"], "status": "open", "reviewer": None, "reviewerUserId": None, "reviewedAt": None, "category": "Suggested schedule match" if schedule else "Unmatched activity"}
    if review is None:
        result["reviewItems"].insert(0, next_review)
    else:
        result["reviewItems"] = [deepcopy(next_review) if item["fieldUpdateId"] == update_id else item for item in result["reviewItems"]]
    return {"data": result, "error": ""}


def get_team_activities(data, team_id):
    team = _find(data["teams"], "id", team_id)
    if not team or not team.get("projectId"):
        return []
    return [{**deepcopy(activity), "plannedStart": _nullish(activity.get("plannedStartTime"), activity.get("plannedStart")), "plannedEnd": _nullish(activity.get("plannedEndTime"), activity.get("plannedEnd"))} for activity in data["scheduleActivities"] if activity.get("teamId") == team_id and activity["projectId"] == team["projectId"]]


def _add_organization_activity(data, action, options):
    event = {"id": _new_id("ORG-ACT"), "action": action, "actorUserId": options.get("actorUserId"), "actor": options.get("actor", "Administrator · Demo"), "occurredAt": options.get("now") or _now(), "type": "assignment"}
    data["organizationActivity"] = [event, *(data.get("organizationActivity") or [])]
    return data


def assign_project_manager(data, options=None):
    result, options = deepcopy(data), options or {}
    project_id, manager_id = options.get("projectId"), options.get("projectManagerId")
    project = _find(result["projects"], "id", project_id)
    manager = _find(result["projectManagers"], "id", manager_id)
    if project is None or manager_id and manager is None:
        return result
    previous_manager_id = project.get("projectManagerId")
    project["projectManagerId"] = manager_id or None
    for item in result["projectManagers"]:
        assignments = item.get("assignedProjectIds", [])
        next_ids = list(dict.fromkeys([*assignments, project_id])) if manager_id == item["id"] else [identifier for identifier in assignments if identifier != project_id]
        item["status"] = "Active" if next_ids else "Available"
        if manager_id == item["id"] or item["id"] == previous_manager_id:
            item["assignedProjectIds"] = next_ids
    name = manager["name"] if manager else "Project Manager assignment cleared"
    return _add_organization_activity(result, f"{name} {'assigned to' if manager else 'removed from'} {project['name']}", options)


def assign_team(data, options=None):
    result, options = deepcopy(data), options or {}
    project_id, team_id, assigned = options.get("projectId"), options.get("teamId"), options.get("assigned", True)
    project, team = _find(result["projects"], "id", project_id), _find(result["teams"], "id", team_id)
    if project is None or team is None or not assigned and team.get("projectId") != project_id:
        return result
    previous_project_id = team.get("projectId")
    project["teamIds"] = list(dict.fromkeys([*(project.get("teamIds") or []), team_id])) if assigned else [identifier for identifier in project.get("teamIds", []) if identifier != team_id]
    if assigned and previous_project_id != project_id:
        previous_project = _find(result["projects"], "id", previous_project_id)
        if previous_project:
            previous_project["teamIds"] = [identifier for identifier in previous_project.get("teamIds", []) if identifier != team_id]
    previous_leader_id = team.get("teamLeaderId")
    team.update({"projectId": project_id if assigned else None, "teamLeaderId": previous_leader_id if assigned else None, "status": "Active" if assigned else "Available"})
    # Historic schedule project/team ownership remains stable when a team moves.
    for leader in result["teamLeaders"]:
        if leader.get("teamId") == team_id or leader["id"] == previous_leader_id:
            leader.update({"teamId": team_id if assigned else None, "projectId": project_id if assigned else None, "status": "Active" if assigned else "Available"})
    return _add_organization_activity(result, f"{team['name']} {'assigned to' if assigned else 'removed from'} {project['name']}", options)


def assign_team_leader(data, options=None):
    result, options = deepcopy(data), options or {}
    team_id, leader_id = options.get("teamId"), options.get("teamLeaderId")
    team, leader = _find(result["teams"], "id", team_id), _find(result["teamLeaders"], "id", leader_id)
    if team is None or leader_id and leader is None:
        return result
    previous_leader_id = team.get("teamLeaderId")
    for item in result["teams"]:
        if item["id"] == team_id:
            item["teamLeaderId"] = leader_id or None
        elif leader_id and item.get("teamLeaderId") == leader_id:
            item["teamLeaderId"] = None
    for item in result["teamLeaders"]:
        if item["id"] == leader_id:
            item.update({"teamId": team_id, "projectId": team.get("projectId"), "status": "Active" if team.get("projectId") else "Available"})
        elif item["id"] == previous_leader_id:
            item.update({"teamId": None, "projectId": None, "status": "Available"})
    name = leader["name"] if leader else "Team Leader assignment cleared"
    return _add_organization_activity(result, f"{name} {'assigned to' if leader else 'removed from'} {team['name']}", options)


def request_planner_review(data, update_id, context=None):
    result, context = deepcopy(data), context or {}
    if not _find(result["fieldUpdates"], "id", update_id) or any(item["fieldUpdateId"] == update_id and item["status"] == "open" for item in result["reviewItems"]):
        return result
    match = _find(result["activityMatches"], "fieldUpdateId", update_id)
    result["reviewItems"].append({"id": _new_id("REV"), "fieldUpdateId": update_id, "reason": "Planner requested a schedule link review.", "confidence": match["confidence"] if match else 0, "status": "open", "reviewer": context.get("reviewer"), "reviewerUserId": context.get("reviewerUserId"), "reviewedAt": None, "category": "Planner requested review"})
    return result


def submit_field_update(data, form, context=None):
    result, context = deepcopy(data), context or {}
    team_id = context.get("teamId")
    team = _find(result["teams"], "id", team_id)
    if not team or not team.get("projectId") or not isinstance(form.get("description"), str) or not form["description"].strip() or not _valid_progress(form.get("progress")):
        return result
    selected = _find(result["scheduleActivities"], "id", form.get("activityId")) if form.get("activityId") else None
    if form.get("activityId") and (not selected or selected["projectId"] != team["projectId"] or selected.get("teamId") != team_id):
        return result
    now, update_id = context.get("now") or _now(), context.get("id") or _new_id("FU")
    submitted_by, submitter_id = context.get("submittedBy", "Ravi Singh · Team Leader"), context.get("submitterUserId")
    analysis = analyze_field_activity(form["description"], result["scheduleActivities"], {"projectId": team["projectId"], "discipline": form.get("discipline"), "location": form.get("location"), "generatedAt": now})
    schedule = selected or _find(result["scheduleActivities"], "id", analysis["match"]["recommendedMatchId"])
    match_status = "review_required" if schedule or analysis["match"]["recommendationStatus"] == "ambiguous" else "unmatched"
    progress = _nullish(form.get("progress"), _nullish(analysis["extractedActivity"]["progress"], 0))
    extracted = analysis["extractedActivity"]
    update = {
        "id": update_id, "projectId": team["projectId"], "teamId": team_id, "submittedBy": submitted_by, "submitterUserId": submitter_id,
        "source": f"Supervisor Field Update · {form['attachmentName']}" if form.get("attachmentName") else "Daily Field Update",
        "rawText": form["description"], "discipline": extracted["discipline"], "location": extracted["location"], "activity": extracted["activityName"], "progress": progress,
        "reportedDiscipline": form.get("discipline") or None, "reportedLocation": form.get("location") or None,
        "actualStart": _nullish(selected.get("actualStart") if selected else None, _schedule_actual_start(schedule)),
        "actualEnd": now if progress >= 100 else None,
        "observation": _nullish(form.get("observation"), ""), "status": "Submitted", "reviewStatus": "needs_review" if match_status == "review_required" else "unmatched", "matchStatus": match_status, "confidence": analysis["match"]["confidence"], "submittedAt": now,
        "extractedActivity": extracted, "pmFeedback": "", "reviewHistory": [{"actorUserId": submitter_id, "actor": submitted_by, "action": "Field update submitted", "occurredAt": now}, _recommendation_history(analysis["match"])],
    }
    schedule_id = schedule["id"] if schedule else None
    result["fieldUpdates"].insert(0, update)
    result["activityMatches"].insert(0, {"fieldUpdateId": update_id, **analysis["match"], "reportedActivityId": selected["id"] if selected else None, "scheduleActivityId": schedule_id, "matchStatus": match_status, "matchedBy": None, "reviewedAt": None, "reviewComment": None, "alternatives": [item["scheduleActivityId"] for item in analysis["match"]["candidates"] if item["scheduleActivityId"] != schedule_id]})
    result["reviewItems"].insert(0, {"id": _new_id("REV"), "fieldUpdateId": update_id, "reason": analysis["match"]["unmatchReason"], "confidence": analysis["match"]["confidence"], "status": "open", "reviewer": None, "reviewedAt": None, "category": "Suggested schedule match" if match_status == "review_required" else "Unmatched activity"})
    return result


def record_activity_action(data, options=None):
    result, options = deepcopy(data), options or {}
    activity_id, action, details = options.get("activityId"), options.get("action"), options.get("details") or {}
    activity = _find(result["scheduleActivities"], "id", activity_id)
    if not activity or action not in ("start", "update", "complete", "block") or not _valid_progress(details.get("progress")) or action == "block" and not (details.get("blockedReason") or "").strip():
        return result
    now, update_id = options.get("now") or _now(), options.get("id") or _new_id("FU")
    submitted_by, submitter_id = options.get("submittedBy", "Ravi Singh · Team Leader"), options.get("submitterUserId")
    actual_start = now if action == "start" else activity.get("actualStart")
    actual_end = now if action == "complete" else activity.get("actualEnd")
    progress = 100 if action == "complete" else _nullish(details.get("progress"), _nullish(activity.get("progress"), 0))
    event = f"Started {activity['activityName']}" if action == "start" else f"Completed {activity['activityName']}" if action == "complete" else f"{activity['activityName']} blocked: {details['blockedReason']}" if action == "block" else f"Progress update for {activity['activityName']}: {_number_text(progress)}%"
    observation = f"Blocked: {details['blockedReason']}. Expected impact: planned work may slip." if details.get("blockedReason") else _nullish(details.get("observation"), _nullish(activity.get("observation"), ""))
    analysis = analyze_field_activity(event, result["scheduleActivities"], {"projectId": activity["projectId"], "discipline": activity.get("discipline"), "location": activity.get("location"), "generatedAt": now})
    update = {"id": update_id, "projectId": activity["projectId"], "submittedBy": submitted_by, "submitterUserId": submitter_id, "source": "Supervisor Field Update", "rawText": event, "discipline": activity["discipline"], "activity": activity["activityName"], "progress": progress, "actualStart": actual_start, "actualEnd": actual_end, "observation": observation, "status": "Submitted", "reviewStatus": "needs_review", "matchStatus": "review_required", "confidence": analysis["match"]["confidence"], "submittedAt": now, "reportedDiscipline": activity["discipline"], "extractedActivity": analysis["extractedActivity"], "pmFeedback": "", "reviewHistory": [{"actorUserId": submitter_id, "actor": submitted_by, "action": event, "occurredAt": now}, _recommendation_history(analysis["match"])]}
    for key in ("teamId", "location"):
        if key in activity:
            update[key] = activity[key]
    if "location" in activity:
        update["reportedLocation"] = activity["location"]
    contribution = {"fieldUpdateId": update_id, "scheduleActivityId": activity_id, "recordedAt": now, "state": {"actualStart": actual_start, "actualEnd": actual_end, "progress": progress, "status": "Complete" if action == "complete" else "Blocked" if action == "block" else "In Progress", "blockedReason": details["blockedReason"] if action == "block" else "" if action == "start" else _nullish(activity.get("blockedReason"), ""), "observation": observation}}
    result["scheduleActivityContributions"] = [item for item in result["scheduleActivityContributions"] if item["fieldUpdateId"] != update_id] + [contribution]
    _apply_contributions(result, activity_id)
    result["fieldUpdates"].insert(0, update)
    result["activityMatches"].insert(0, {"fieldUpdateId": update_id, **analysis["match"], "reportedActivityId": activity_id, "scheduleActivityId": activity_id, "matchStatus": "review_required", "matchedBy": None, "reviewedAt": None, "reviewComment": None, "alternatives": [item["scheduleActivityId"] for item in analysis["match"]["candidates"] if item["scheduleActivityId"] != activity_id]})
    result["reviewItems"].insert(0, {"id": _new_id("REV"), "fieldUpdateId": update_id, "reason": f"Activity blocked: {details['blockedReason']}. Expected impact: planned work may slip." if action == "block" else "Supervisor activity update is ready for Project Manager review.", "confidence": analysis["match"]["confidence"], "status": "open", "reviewer": None, "reviewedAt": None, "category": "Blocked activity" if action == "block" else "Field activity update"})
    return result


def start_activity(data, options=None):
    return record_activity_action(data, {**(options or {}), "action": "start"})


def update_activity(data, options=None):
    return record_activity_action(data, {**(options or {}), "action": "update"})


def complete_activity(data, options=None):
    return record_activity_action(data, {**(options or {}), "action": "complete"})


def block_activity(data, options=None):
    return record_activity_action(data, {**(options or {}), "action": "block"})


def _decide_match(data, options):
    result = deepcopy(data)
    update_id, schedule_id = options.get("updateId"), options.get("scheduleActivityId")
    reason, feedback = options.get("reason", ""), options.get("feedback", "")
    reviewer, reviewer_id, now = options.get("reviewer", "Priya Mehta · Project Manager"), options.get("reviewerUserId"), options.get("now") or _now()
    decision = options.get("decision")

    def error(message):
        return {"data": result, "error": message}

    if decision not in ("confirm", "change", "unmatched", "feedback"):
        return error("Unsupported review decision.")
    update, match = _find(result["fieldUpdates"], "id", update_id), _find(result["activityMatches"], "fieldUpdateId", update_id)
    if update is None or match is None:
        return error("Field update or activity match could not be found.")
    accepted, unmatched, requested_info = decision in ("confirm", "change"), decision == "unmatched", decision == "feedback"
    if accepted and (update.get("progress") or 0) >= 100 and not update.get("actualEnd"):
        return error("Actual completion time is required before confirming this update.")
    if accepted and not schedule_id:
        return error("Select a schedule activity before confirming this update.")
    if requested_info and not feedback.strip():
        return error("Add a short note before requesting more information.")
    schedule = _find(result["scheduleActivities"], "id", schedule_id)
    if accepted and not schedule:
        return error("The selected schedule activity could not be found.")
    if accepted and schedule["projectId"] != update["projectId"]:
        return error("The selected schedule activity belongs to a different project.")
    result_status = "action_required" if requested_info or unmatched and feedback.strip() else "reviewed"
    decision_text = f"{'PM changed and confirmed the schedule link' if decision == 'change' else 'PM confirmed the schedule link'} · {schedule['activityName']}." if accepted else f"PM marked this update unmatched · {reason or 'No schedule activity found'}." if unmatched else feedback
    history_event = {"actorUserId": reviewer_id, "actor": reviewer, "action": f"Requested information: {feedback}" if requested_info else decision_text, "occurredAt": now}
    if accepted or unmatched:
        _remove_contribution(result, update_id, match.get("scheduleActivityId"))
        if accepted:
            result["scheduleActivityContributions"].append(_match_contribution(update, schedule_id, now))
            _apply_contributions(result, schedule_id)
    match_status = "matched" if accepted else "unmatched" if unmatched else match["matchStatus"]
    match.update({"matchedByUserId": match.get("matchedByUserId") if requested_info else reviewer_id if accepted else None, "scheduleActivityId": schedule_id if accepted else None if unmatched else match.get("scheduleActivityId"), "matchStatus": match["matchStatus"] if requested_info else match_status, "matchedBy": match.get("matchedBy") if requested_info else reviewer, "reviewedAt": match.get("reviewedAt") if requested_info else now, "reviewComment": match.get("reviewComment") if requested_info else decision_text})
    reviews = [item for item in result["reviewItems"] if item["fieldUpdateId"] == update_id]
    if reviews:
        for review in reviews:
            review.update({"status": "open" if requested_info or unmatched and feedback.strip() else "accepted", "reviewer": reviewer, "reviewerUserId": reviewer_id, "reviewedAt": now})
            if requested_info:
                review["reason"] = f"Information requested: {feedback}"
            elif unmatched:
                review["reason"] = (reason or "No schedule activity found") + (f" · {feedback}" if feedback else "")
    else:
        result["reviewItems"].append({"id": _new_id("REV"), "fieldUpdateId": update_id, "reason": reason or "Planner review decision recorded.", "confidence": match["confidence"], "status": "open" if requested_info else "accepted", "reviewer": reviewer, "reviewerUserId": reviewer_id, "reviewedAt": now, "category": "Planner review"})
    if requested_info and not any(item["fieldUpdateId"] == update_id and item["status"] == "open" for item in result["reviewItems"]):
        result["reviewItems"].append({"id": _new_id("REV"), "fieldUpdateId": update_id, "reason": f"Information requested: {feedback}", "confidence": match["confidence"], "status": "open", "reviewer": reviewer, "reviewerUserId": reviewer_id, "reviewedAt": now, "category": "Information requested"})
    update.update({"status": "Action Required" if result_status == "action_required" else "Reviewed", "reviewStatus": result_status, "matchStatus": update["matchStatus"] if requested_info else match_status, "pmFeedback": feedback if requested_info or feedback.strip() else decision_text if accepted else reason or "No schedule match found.", "reviewer": reviewer, "reviewerUserId": reviewer_id, "reviewedAt": now, "reviewHistory": [*(update.get("reviewHistory") or []), history_event]})
    message = "Match confirmed successfully. Actual field progress is linked to the schedule." if accepted else ("Update marked unmatched. PM feedback was sent to the Team Leader." if feedback.strip() else "Update marked unmatched and recorded in review history.") if unmatched else "Action required. Your feedback was sent to the Team Leader."
    return {"data": result, "error": "", "message": message, "shouldClose": not requested_info}


def confirm_match(data, options=None):
    return _decide_match(data, {**(options or {}), "decision": "confirm"})


def change_match(data, options=None):
    return _decide_match(data, {**(options or {}), "decision": "change"})


def mark_unmatched(data, options=None):
    return _decide_match(data, {**(options or {}), "decision": "unmatched"})


def request_information(data, options=None):
    return _decide_match(data, {**(options or {}), "decision": "feedback"})
