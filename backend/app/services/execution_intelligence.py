"""Deterministic execution signals. No matching, inferred dates or causal predictions."""
from datetime import UTC, date, datetime
from uuid import NAMESPACE_URL, uuid5

VERSION = "execution-8.0"


def day(value):
    # Use the reported calendar day, not a timezone-dependent conversion.
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except (ValueError, TypeError):
        return None


def ratio(numerator, denominator):
    return round(100 * numerator / denominator, 1) if denominator else None


def calculate(project_id, activities, updates, matches, contributions, settings, now=None):
    now = now or datetime.now(UTC)
    today = now.date()
    # IDs are authoritative: duplicate inputs never inflate metrics or evidence.
    activities = {a["id"]: a for a in activities}
    updates = {u["id"]: u for u in updates}
    matches = {m["fieldUpdateId"]: m for m in matches if m["fieldUpdateId"] in updates}
    contributions = {c["fieldUpdateId"]: c for c in contributions if c["fieldUpdateId"] in updates}
    confirmed = {uid: c for uid, c in contributions.items() if matches.get(uid, {}).get("matchStatus") == "matched" and updates[uid].get("reviewStatus") == "reviewed" and matches[uid].get("scheduleActivityId") == c["scheduleActivityId"] and c["scheduleActivityId"] in activities}
    confirmed_by_activity = {aid: [] for aid in activities}
    for contribution in confirmed.values():
        confirmed_by_activity[contribution["scheduleActivityId"]].append(contribution)
    by_activity = {aid: [] for aid in activities}
    for uid, m in matches.items():
        aid = m.get("scheduleActivityId") or m.get("reportedActivityId") or m.get("recommendedMatchId")
        if aid in by_activity:
            by_activity[aid].append(updates[uid])
    warnings, rows = [], []

    def warn(kind, aid, reason, evidence, severity="MEDIUM", update_id=None, attention="Review the execution evidence and confirm or correct the record."):
        identity = f"{project_id}:{aid or '-'}:{kind}:{update_id or '-'}"
        warnings.append({"id": "EW-" + str(uuid5(NAMESPACE_URL, identity)), "projectId": project_id, "activityId": aid,
            "fieldUpdateId": update_id, "type": kind, "severity": severity, "status": "OPEN",
            "generatedAt": now.isoformat(), "reason": reason, "evidence": evidence, "attention": attention})

    for aid, a in sorted(activities.items()):
        total_float = a.get("totalFloat")
        if isinstance(total_float, (int, float)) and not isinstance(total_float, bool) and total_float < 0:
            warn("NEGATIVE_FLOAT", aid, "Imported schedule reports negative total float.", {"totalFloatDays": total_float, "source": "schedule_import", "versionId": a.get("scheduleVersionId")}, "HIGH", attention="Check the supplied schedule float and dependency constraints. No critical path is inferred.")
        cs = sorted(confirmed_by_activity[aid], key=lambda c: (c["recordedAt"], c["fieldUpdateId"]))
        imported = a.get("actualSource") == "schedule_import"
        authoritative = bool(cs) or imported
        state = cs[-1]["state"] if cs else a.get("importedActuals", {}) if imported else {}
        start, finish = day(state.get("actualStart")), day(state.get("actualEnd"))
        planned_start, planned_end = day(a.get("plannedStart")), day(a.get("plannedEnd"))
        progress = state.get("progress") if authoritative else None
        invalid_dates = bool((start and start > today) or (finish and finish > today) or (start and finish and finish < start))
        if invalid_dates:
            start, finish = None, None
        valid_progress = isinstance(progress, (int, float)) and not isinstance(progress, bool) and 0 <= progress <= 100
        progress = progress if valid_progress else None
        complete = authoritative and (finish is not None or progress == 100)
        sv = (start - planned_start).days if start and planned_start else None
        fv = (finish - planned_end).days if finish and planned_end else None
        duration = ((finish - start) - (planned_end - planned_start)).days if start and finish and planned_start and planned_end and finish >= start and planned_end >= planned_start else None
        has_actual = authoritative and (progress is not None or start is not None or finish is not None)
        overdue = (today - planned_end).days if planned_end and today > planned_end and has_actual and not complete else 0
        delay = max(sv or 0, fv or 0, overdue)
        dates_known = sv is not None or fv is not None
        timing = "DELAYED" if delay > 0 else "EARLY" if (fv if fv is not None else sv or 0) < 0 else "ON_TIME" if dates_known else "UNKNOWN"
        status = "COMPLETED" if complete else "IN_PROGRESS" if authoritative and (start or (progress or 0) > 0) else "NOT_STARTED" if authoritative and progress == 0 else "UNKNOWN"
        related = by_activity[aid]
        latest = max((day(u.get("submittedAt")) for u in related if day(u.get("submittedAt"))), default=None)
        reference = latest or planned_start
        stale_days = (today - reference).days if reference else None
        stale = not complete and stale_days is not None and stale_days >= settings.intelligence_stale_days and (not planned_start or planned_start <= today)
        row = {"activityId": aid, "name": a.get("activityName", aid), "plannedStart": a.get("plannedStart"), "plannedEnd": a.get("plannedEnd"),
            "actualStart": state.get("actualStart"), "actualEnd": state.get("actualEnd"), "confirmedProgress": progress,
            "confirmedUpdateIds": [c["fieldUpdateId"] for c in cs], "hasConfirmedActual": has_actual, "actualSource": "pm_review" if cs else "schedule_import" if imported else None, "status": status, "timing": timing,
            "startVarianceDays": sv, "finishVarianceDays": fv, "durationVarianceDays": duration,
            "overdueDays": overdue, "delayDays": delay, "stale": stale, "lastUpdateDate": latest.isoformat() if latest else None,
            "potentialDownstream": []}
        rows.append(row)
        evidence = {"plannedStart": row["plannedStart"], "plannedEnd": row["plannedEnd"], "actualStart": row["actualStart"], "actualEnd": row["actualEnd"], "confirmedProgress": progress, "confirmedUpdateIds": row["confirmedUpdateIds"], "asOfDate": today.isoformat()}
        if delay > 0:
            warn("DELAY", aid, f"Confirmed execution has a {delay}-day delay signal; finish overrun is {overdue} days.", {**evidence, "delayDays": delay}, "HIGH" if delay >= settings.intelligence_high_delay_days else "MEDIUM")
        if max(sv or 0, fv or 0) >= settings.intelligence_high_delay_days:
            warn("SIGNIFICANT_VARIANCE", aid, "Confirmed dates exceed the configured adverse variance threshold.", {**evidence, "startVarianceDays": sv, "finishVarianceDays": fv, "thresholdDays": settings.intelligence_high_delay_days}, "HIGH")
        if not complete and planned_end and 0 <= (planned_end - today).days <= settings.intelligence_finish_window_days and (progress is None or progress < settings.intelligence_min_progress):
            warn("APPROACHING_FINISH", aid, "Planned finish is approaching with insufficient confirmed progress evidence.", {**evidence, "windowDays": settings.intelligence_finish_window_days, "minimumProgress": settings.intelligence_min_progress})
        if stale:
            warn("STALE", aid, "No recent linked execution report; this is a capture gap, not proof of inactivity.", {"lastUpdateDate": row["lastUpdateDate"], "plannedStart": row["plannedStart"], "ageDays": stale_days, "thresholdDays": settings.intelligence_stale_days, "asOfDate": today.isoformat()})
        incomplete = [u["id"] for u in related if not u.get("extractedActivity", {}).get("activityName") or not u.get("extractedActivity", {}).get("discipline") or not u.get("extractedActivity", {}).get("location")]
        if len(incomplete) >= settings.intelligence_incomplete_threshold:
            warn("REPEATED_INCOMPLETE", aid, "Repeated reports lack activity, discipline or location evidence.", {"fieldUpdateIds": sorted(incomplete), "count": len(incomplete), "threshold": settings.intelligence_incomplete_threshold})
        issues = []
        if not planned_start or not planned_end or (planned_start and planned_end and planned_end < planned_start):
            issues.append("Missing or invalid planned dates")
        if authoritative and (invalid_dates or not valid_progress or (start and finish and finish < start) or (state.get("actualStart") and not start) or (state.get("actualEnd") and not finish) or (start and start > today) or (finish and finish > today)):
            issues.append("Invalid or future confirmed actual information")
        if issues:
            warn("DATA_QUALITY", aid, "; ".join(issues), {**evidence, "issues": issues}, "LOW")

    for uid, u in sorted(updates.items()):
        m = matches.get(uid, {})
        aid = m.get("scheduleActivityId") or m.get("reportedActivityId") or m.get("recommendedMatchId")
        if aid not in activities:
            aid = None
        if m.get("matchStatus") == "unmatched" or not m:
            warn("UNMATCHED", aid, "Execution report has no accepted schedule link.", {"fieldUpdateId": uid, "matcherVersion": m.get("matcherVersion"), "matchStatus": m.get("matchStatus"), "reason": m.get("unmatchReason")}, "LOW", uid)
        if u.get("reviewStatus") != "reviewed":
            warn("PENDING_REVIEW", aid, "PM review is outstanding; reported progress is not confirmed intelligence.", {"fieldUpdateId": uid, "reviewStatus": u.get("reviewStatus"), "submittedAt": u.get("submittedAt")}, "MEDIUM", uid)
        if m.get("scheduleActivityId") and m["scheduleActivityId"] not in activities:
            if m.get("retiredScheduleLink"):
                warn("SCHEDULE_VERSION_CHANGE", None, "This report links to an activity retired by a schedule import; PM review is needed.", {"fieldUpdateId": uid, "issue": "retired schedule activity"}, "MEDIUM", uid)
            else:
                warn("LINKAGE_QUALITY", None, "Stored activity linkage is outside this project schedule.", {"fieldUpdateId": uid, "issue": "cross-project or missing activity"}, "HIGH", uid)

    # No dependency graph currently exists in PRAVAHA. Only explicitly persisted
    # predecessorIds (internal schedule IDs, finish-to-start) are recognized.
    row_map = {r["activityId"]: r for r in rows}
    dependency_count = 0
    for aid, a in activities.items():
        dependencies = a.get("predecessorIds", [])
        if not isinstance(dependencies, list):
            warn("DATA_QUALITY", aid, "Invalid persisted predecessor list.", {"issue": "predecessorIds must be a list"}, "LOW")
            continue
        for predecessor in sorted(set(p for p in dependencies if isinstance(p, str))):
            source = row_map.get(predecessor)
            if not source or predecessor == aid:
                warn("DATA_QUALITY", aid, "Persisted dependency references a missing or invalid predecessor.", {"predecessorId": predecessor}, "LOW")
                continue
            dependency_count += 1
            target_start, source_finish = day(a.get("plannedStart")), day(activities[predecessor].get("plannedEnd"))
            # Only a finish delay exposes a successor; late start alone is insufficient.
            finish_delay = max(source["finishVarianceDays"] or 0, source["overdueDays"])
            slack = (target_start - source_finish).days if target_start and source_finish else None
            exposure = max(0, finish_delay - max(0, slack)) if slack is not None and finish_delay > 0 else 0
            if exposure and not row_map[aid]["status"] == "COMPLETED":
                impact = {"activityId": aid, "predecessorId": predecessor, "relationship": "finish-to-start", "potentialExposureDays": exposure, "plannedStart": a.get("plannedStart"), "predecessorPlannedEnd": activities[predecessor].get("plannedEnd"), "finishDelayDays": finish_delay, "slackDays": slack}
                source["potentialDownstream"].append(impact)
                warn("DEPENDENCY_EXPOSURE", aid, f"Potential downstream impact: predecessor may expose this activity to {exposure} days of delay.", impact, "HIGH")

    matched_updates = sum(m.get("scheduleActivityId") in activities and m.get("matchStatus") != "unmatched" for m in matches.values())
    unmatched = sum(not m or m.get("matchStatus") == "unmatched" for m in (matches.get(uid) for uid in updates))
    pending = sum(u.get("reviewStatus") != "reviewed" for u in updates.values())
    warning_activities = {w["activityId"] for w in warnings if w["activityId"]}
    summary = {"scheduledActivities": len(rows), "activitiesWithUpdates": sum(bool(us) for us in by_activity.values()),
        "matchedActivities": len({m.get("scheduleActivityId") for m in matches.values() if m.get("scheduleActivityId") in activities and m.get("matchStatus") != "unmatched"}),
        "pendingReviewActivities": len({m.get("scheduleActivityId") or m.get("recommendedMatchId") or m.get("reportedActivityId") for uid, m in matches.items() if updates[uid].get("reviewStatus") != "reviewed"} & set(activities)),
        "confirmedActuals": sum(r["hasConfirmedActual"] for r in rows), "completedActivities": sum(r["status"] == "COMPLETED" for r in rows),
        "delayedActivities": sum(r["timing"] == "DELAYED" for r in rows), "atRiskActivities": len(warning_activities),
        "staleActivities": sum(r["stale"] for r in rows), "missingActuals": sum(not r["hasConfirmedActual"] for r in rows),
        "unmatchedUpdates": unmatched, "dataQualityIssues": sum(w["type"] in {"DATA_QUALITY", "LINKAGE_QUALITY", "REPEATED_INCOMPLETE"} for w in warnings)}
    health = {}
    def dimension(key, status, reason):
        health[key] = {"status": status, "reason": reason}
    dimension("schedule", "DELAYED" if summary["delayedActivities"] else "AT_RISK" if any(w["type"] == "APPROACHING_FINISH" for w in warnings) else "UNKNOWN" if summary["missingActuals"] or not rows else "NO_DELAY_SIGNAL", f'{summary["delayedActivities"]} activities have confirmed delay signals; {summary["missingActuals"]} lack confirmed actuals.')
    dimension("execution", "PARTIAL" if summary["missingActuals"] else "AVAILABLE" if rows else "N/A", f'{summary["completedActivities"]} completed; {summary["confirmedActuals"]} with confirmed actuals. No weighted project progress is inferred.')
    dimension("dataCapture", "STALE" if summary["staleActivities"] else "PARTIAL" if summary["activitiesWithUpdates"] < len(rows) else "AVAILABLE" if rows else "N/A", f'{summary["activitiesWithUpdates"]} of {len(rows)} activities have linked reports; {summary["staleActivities"]} stale.')
    dimension("linkage", "DEGRADED" if unmatched or summary["dataQualityIssues"] else "AVAILABLE" if updates else "N/A", f'{matched_updates} of {len(updates)} updates have valid proposed or accepted links; {unmatched} unmatched.')
    dimension("reviewBacklog", "ATTENTION" if pending else "CLEAR", f"{pending} updates await a reviewed state.")
    dimension("dependencyExposure", "HIGH" if any(w["type"] == "DEPENDENCY_EXPOSURE" for w in warnings) else "NO_EXPOSURE_SIGNAL" if dependency_count else "UNAVAILABLE", f"{dependency_count} persisted finish-to-start relationships evaluated; no relationships are inferred.")
    dimension("warnings", "HIGH" if any(w["severity"] == "HIGH" for w in warnings) else "ATTENTION" if warnings else "CLEAR", f"{len(warnings)} evidence-backed signals; no critical severity is inferred.")
    return {"projectId": project_id, "version": VERSION, "evaluatedAt": now.isoformat(), "summary": summary, "health": health,
        "dataHealth": {"updatesReceived": len(updates), "matchedUpdates": matched_updates, "unmatchedUpdates": unmatched, "pendingReview": pending,
            "confirmedUpdates": len(confirmed), "activitiesWithoutActuals": summary["missingActuals"], "staleActivities": summary["staleActivities"], "linkageCoverage": ratio(matched_updates, len(updates)), "dataCoverage": ratio(summary["activitiesWithUpdates"], len(rows)),
            "linkageFormula": "100 × valid proposed or accepted linked updates / all project updates", "dataFormula": "100 × activities with linked reports / scheduled activities"},
        "activities": rows, "warnings": sorted(warnings, key=lambda w: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[w["severity"]], w["id"])), "dependencyRelationships": dependency_count}
