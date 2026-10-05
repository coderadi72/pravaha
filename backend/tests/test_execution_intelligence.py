"""Phase 8 rules and real PostgreSQL API regressions."""
from copy import deepcopy
from datetime import UTC, datetime
from types import SimpleNamespace
import pytest
from sqlalchemy import func, select
from backend.app.services.execution_intelligence import calculate
from backend.app.models import AuditEvent, ExecutionWarning, FieldUpdate
from backend.tests.test_api import request, submit

NOW = datetime(2026, 10, 10, tzinfo=UTC)
RULES = SimpleNamespace(intelligence_stale_days=7, intelligence_finish_window_days=3, intelligence_min_progress=80, intelligence_high_delay_days=7, intelligence_incomplete_threshold=3)
A = {"id": "A", "activityName": "Pipe work", "plannedStart": "2026-10-01", "plannedEnd": "2026-10-05"}
U = {"id": "U", "reviewStatus": "reviewed", "submittedAt": "2026-10-02", "extractedActivity": {"activityName": "Pipe", "discipline": "Piping", "location": "Rack"}}
M = {"fieldUpdateId": "U", "scheduleActivityId": "A", "matchStatus": "matched"}
C = {"fieldUpdateId": "U", "scheduleActivityId": "A", "recordedAt": "2026-10-02", "state": {"actualStart": "2026-10-04", "actualEnd": None, "progress": 50}}


def run(activities=None, updates=None, matches=None, contributions=None, now=NOW):
    return calculate("P", activities if activities is not None else [A], updates if updates is not None else [U], matches if matches is not None else [M], contributions if contributions is not None else [C], RULES, now)


def test_empty_denominator_and_missing_actuals_are_unknown():
    empty = run([], [], [], [])
    assert empty["dataHealth"]["linkageCoverage"] is None
    assert empty["dataHealth"]["dataCoverage"] is None
    assert not empty["warnings"]
    result = run(contributions=[])
    row = result["activities"][0]
    assert row["timing"] == "UNKNOWN" and row["status"] == "UNKNOWN"
    assert row["actualStart"] is None and row["confirmedProgress"] is None
    assert result["summary"]["missingActuals"] == 1
    assert result["summary"]["completedActivities"] == 0


def test_confirmed_actual_days_stale_and_delay_evidence():
    result = run()
    row = result["activities"][0]
    assert row["startVarianceDays"] == 3 and row["overdueDays"] == 5
    assert row["finishVarianceDays"] is None and row["durationVarianceDays"] is None
    assert row["timing"] == "DELAYED" and row["stale"]
    warning = next(w for w in result["warnings"] if w["type"] == "DELAY")
    assert warning["evidence"]["confirmedUpdateIds"] == ["U"]
    assert warning["evidence"]["delayDays"] == 5 and warning["severity"] == "MEDIUM"


@pytest.mark.parametrize("actual_start,actual_end,timing,start_variance,finish_variance,duration", [
    ("2026-10-01", "2026-10-05", "ON_TIME", 0, 0, 0),
    ("2026-09-30", "2026-10-04", "EARLY", -1, -1, 0),
    ("2026-10-02", "2026-10-08", "DELAYED", 1, 3, 2),
])
def test_completed_confirmed_variance(actual_start, actual_end, timing, start_variance, finish_variance, duration):
    c = deepcopy(C); c["state"].update(actualStart=actual_start, actualEnd=actual_end, progress=100)
    row = run(contributions=[c])["activities"][0]
    assert row["status"] == "COMPLETED" and row["timing"] == timing
    assert [row["startVarianceDays"], row["finishVarianceDays"], row["durationVarianceDays"]] == [start_variance, finish_variance, duration]
    assert not row["stale"] and row["overdueDays"] == 0


def test_provisional_contribution_and_completion_are_not_confirmed():
    u = {**U, "reviewStatus": "needs_review"}
    c = deepcopy(C); c["state"].update(progress=100, actualEnd="2026-10-05")
    result = run(updates=[u], matches=[{**M, "matchStatus": "review_required"}], contributions=[c])
    assert result["summary"]["confirmedActuals"] == 0 and result["summary"]["completedActivities"] == 0
    assert any(w["type"] == "PENDING_REVIEW" for w in result["warnings"])


def test_finish_approach_unmatched_and_incomplete():
    result = run(activities=[{**A, "plannedEnd": "2026-10-12"}], updates=[{**U, "reviewStatus": "needs_review"}], contributions=[])
    assert any(w["type"] == "APPROACHING_FINISH" and w["evidence"]["confirmedProgress"] is None for w in result["warnings"])
    unmatched = run(matches=[], contributions=[])
    assert unmatched["summary"]["unmatchedUpdates"] == 1
    assert any(w["type"] == "UNMATCHED" for w in unmatched["warnings"])
    us = [{**U, "id": str(i), "extractedActivity": {}} for i in range(3)]
    ms = [{**M, "fieldUpdateId": str(i)} for i in range(3)]
    incomplete = run(updates=us, matches=ms, contributions=[])
    assert any(w["type"] == "REPEATED_INCOMPLETE" and w["evidence"]["count"] == 3 for w in incomplete["warnings"])


def test_dependency_exposure_uses_finish_slack_and_no_invented_graph():
    target = {"id": "B", "plannedStart": "2026-10-07", "plannedEnd": "2026-10-20", "predecessorIds": ["A"]}
    result = run(activities=[A, target])
    warning = next(w for w in result["warnings"] if w["type"] == "DEPENDENCY_EXPOSURE")
    assert warning["evidence"]["potentialExposureDays"] == 3
    assert "Potential downstream" in warning["reason"] and warning["severity"] == "HIGH"
    assert run()["health"]["dependencyExposure"]["status"] == "UNAVAILABLE"
    assert not any(w["type"] == "DEPENDENCY_EXPOSURE" for w in run(activities=[A, {**target, "plannedStart": "2026-10-20"}])["warnings"])


def test_duplicate_ids_determinism_invalid_dates_and_thresholds():
    assert run() == run([A,A], [U,U], [M,M], [C,C])
    assert all(w["severity"] != "CRITICAL" for w in run()["warnings"])
    bad = run(activities=[{**A, "plannedStart": "garbage"}])
    assert bad["activities"][0]["startVarianceDays"] is None
    assert any(w["type"] == "DATA_QUALITY" for w in bad["warnings"])
    assert {w["id"] for w in run()["warnings"]} == {w["id"] for w in run(now=datetime(2026,10,11,tzinfo=UTC))["warnings"]}


def test_phase8_api_scope_pagination_and_memory(client, identities):
    path = "/api/intelligence/projects/PRJ-001"
    assert request(client, path).status_code == 401
    assert request(client, path, identities["tl"]).status_code == 403
    assert request(client, "/api/intelligence/projects/PRJ-002", identities["pm"]).status_code == 403
    for role in ("admin", "pm"):
        response = request(client, path+"?limit=1", identities[role]); assert response.status_code == 200, response.text
        assert len(response.json()["activities"]) == 1 and response.json()["activityTotal"] == 10
        assert "password_hash" not in response.text
    assert request(client, path+"?limit=101", identities["pm"]).status_code == 400
    assert request(client, path+"/memory?limit=2", identities["pm"]).json()["limit"] == 2
    result = request(client, path+"/memory?q=Line%20247", identities["pm"])
    assert result.status_code == 200, result.text
    assert result.json()["total"] > 0
    assert request(client,path+"/memory?activity_id=NOT-OWNED",identities["pm"]).status_code == 404
    for suffix in ("/memory", "/refresh"):
        assert request(client,path+suffix,identities["tl"],"POST" if suffix=="/refresh" else "GET").status_code == 403


def test_warning_lifecycle_idempotence_feedback_and_history(client, identities, seeded_session_factory):
    path = "/api/intelligence/projects/PRJ-001"
    first = request(client,path+"/refresh",identities["pm"],"POST"); assert first.status_code == 200, first.text
    with seeded_session_factory() as session:
        before = session.scalar(select(func.count()).select_from(AuditEvent))
    second = request(client,path+"/refresh",identities["pm"],"POST"); assert second.status_code == 200,second.text
    with seeded_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(AuditEvent)) == before
    warning = second.json()["warnings"][0]
    ack = request(client,path+f'/warnings/{warning["id"]}/acknowledge',identities["admin"],"PATCH")
    assert ack.status_code == 200,ack.text
    uid = submit(client,identities,progress=82)
    response = request(client,f'/api/reviews/{uid}/confirm',identities["pm"],"POST",{"scheduleActivityId":"SA-1024","feedback":"Phase 8 evidence confirmation"})
    assert response.status_code == 200,response.text
    result = request(client,path,identities["pm"]).json()
    assert next(a for a in result["activities"] if a["activityId"]=="SA-1024")["confirmedProgress"] == 82
    with seeded_session_factory() as session:
        warnings = list(session.scalars(select(ExecutionWarning)))
        assert any(w.status == "RESOLVED" and w.payload_json.get("fieldUpdateId") == uid for w in warnings)
    memory = request(client,path+"/memory?q=Phase%208%20evidence",identities["pm"])
    assert memory.status_code == 200,memory.text
    assert memory.json()["total"] > 0
    action = request(client,f'/api/reviews/{uid}/unmatch',identities["pm"],"POST",{"reason":"Correct previous link"})
    assert action.status_code == 200
    result = request(client,path,identities["pm"]).json()
    assert next(a for a in result["activities"] if a["activityId"]=="SA-1024")["confirmedProgress"] == 65
    history = request(client,path+"/memory?kind=audit",identities["admin"]).json()
    assert any(e["action"] == "Execution intelligence changed" for e in history["items"])


def test_warning_audit_failure_rolls_back_field_submission(client, identities, seeded_session_factory, monkeypatch):
    import backend.app.services.project_intelligence_service as service
    with seeded_session_factory() as session:
        before = session.scalar(select(func.count()).select_from(FieldUpdate))
        warnings = session.scalar(select(func.count()).select_from(ExecutionWarning))
    def fail(*args, **kwargs):
        raise RuntimeError("Injected Phase 8 audit failure")
    monkeypatch.setattr(service,"append_audit",fail)
    result = request(client,"/api/team-leader/field-updates",identities["tl"],"POST",{"description":"Spool erected for Line 247-XX in Unit 4 / Rack B","progress":82})
    assert result.status_code == 500 and "Injected" not in result.text
    with seeded_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(FieldUpdate)) == before
        assert session.scalar(select(func.count()).select_from(ExecutionWarning)) == warnings


def test_portfolio_uses_bounded_batched_project_queries(client, identities, engine):
    from sqlalchemy import event
    statements=[]
    def capture(conn, cursor, statement, parameters, context, many):
        statements.append(statement)
    event.listen(engine,"before_cursor_execute",capture)
    try:
        response=request(client,"/api/intelligence/portfolio",identities["admin"])
        assert response.status_code==200,response.text
        assert response.json()["total"]==4
        assert len(statements)<=9  # session auth + authorized project count/list + 4 batched inputs
        assert all(p["summary"]["scheduledActivities"]==0 for p in response.json()["items"] if p["id"]!="PRJ-001")
    finally:
        event.remove(engine,"before_cursor_execute",capture)
    assert request(client,"/api/intelligence/portfolio",identities["tl"]).status_code==403
    assert request(client,"/api/intelligence/portfolio",identities["pm"]).json()["total"]==1


def test_future_dates_and_empty_confirmed_state_not_invented():
    c=deepcopy(C);c["state"]={"actualStart":"2027-01-01","progress":None}
    result=run(contributions=[c])
    assert result["activities"][0]["startVarianceDays"] is None
    assert result["summary"]["missingActuals"]==1
    assert result["activities"][0]["timing"]=="UNKNOWN"
    assert any(w["type"]=="DATA_QUALITY" for w in result["warnings"])


def test_memory_timestamps_sort_chronologically_without_invented_review_times(client, identities):
    response=request(client,"/api/intelligence/projects/PRJ-001/memory",identities["pm"])
    assert response.status_code==200,response.text
    events=response.json()["items"]
    dates=[datetime.fromisoformat(e["occurredAt"].replace("Z","+00:00")) for e in events if e["occurredAt"]]
    assert dates==sorted(dates,reverse=True)
    assert any(e["kind"]=="review" and e["occurredAt"] is None for e in events)


@pytest.mark.parametrize("action", ["review", "refresh", "acknowledge"])
def test_intelligence_audit_failure_rolls_back_every_new_mutation(client, identities, seeded_session_factory, monkeypatch, action):
    import backend.app.services.project_intelligence_service as service
    path="/api/intelligence/projects/PRJ-001"
    uid=submit(client,identities,progress=91)
    first=request(client,path+"/refresh",identities["pm"],"POST");assert first.status_code==200
    def snapshot():
        with seeded_session_factory() as session:
            return {table:[dict(r) for r in session.execute(__import__('sqlalchemy').text(f'SELECT * FROM {table} ORDER BY id')).mappings()] for table in ["field_updates","reviews","execution_warnings","audit_events"]}
    before=snapshot()
    def fail(*args,**kwargs):raise RuntimeError("Injected intelligence audit failure")
    monkeypatch.setattr(service,"append_audit",fail)
    if action=="review":
        response=request(client,f'/api/reviews/{uid}/confirm',identities["pm"],"POST",{"scheduleActivityId":"SA-1024"})
    elif action=="acknowledge":
        warning=first.json()["warnings"][0]["id"]
        response=request(client,path+f'/warnings/{warning}/acknowledge',identities["pm"],"PATCH")
    else:
        # Make a real data change so refresh has a meaningful transition to audit.
        from backend.app.models import ScheduleActivity
        with seeded_session_factory.begin() as session:
            activity=session.get(ScheduleActivity,"SA-1024")
            activity.payload_json={**activity.payload_json,"plannedStart":"2026-01-01"}
        response=request(client,path+"/refresh",identities["admin"],"POST")
    assert response.status_code==500 and 'Injected' not in response.text
    assert snapshot()==before
