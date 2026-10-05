import UiText from "../../ui/UiText.jsx";
import FieldEvidence from "./FieldEvidence.jsx";
import { useMemo, useState } from "react";
import MatchEvidencePanel from "./MatchEvidencePanel.jsx";
import MatchingHealth from "./MatchingHealth.jsx";
import {
  ArrowRight,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronDown,
  ClipboardList,
  FileSpreadsheet,
  FileText,
  MapPin,
  Search,
  ShieldAlert,
  Unlink,
  X,
} from "lucide-react";

const WORKFLOW_STEPS = ["Field Updates", "Activity Matching", "Planner Review", "Schedule"];

const TITLES = {
  Projects: ["Projects", "Portfolio status and project execution context."],
  "Field Updates": ["Field Updates", "Captured site reports, extracted work, and schedule links."],
  "Activity Matching": ["Activity Matching", "Compare field observations with suggested L5/L6 schedule activities."],
  "Planner Review": ["Field Update Review", "Review field execution updates and confirm schedule-linked actuals."],
  Schedule: ["Schedule", "Review planned dates alongside actual field progress."],
  Analytics: ["Execution Analytics", "Project variance and discipline activity status."],
  Reports: ["Reports", "Current reporting period built from persisted execution records."],
  "Knowledge Base": ["Execution Knowledge", "Reusable project context from observed execution patterns."],
  Settings: ["Workspace Settings", "Environment details for this local product prototype."],
};

const DATE_FORMAT = new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" });

function formatDate(value) {
  if (!value) return "Not recorded";
  return DATE_FORMAT.format(new Date(value.length > 10 ? value : `${value}T12:00:00`));
}

function formatDateTime(value) {
  if (!value) return "Not reviewed";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not recorded";
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }).format(date);
}

function formatScheduleVariance(schedule, update) {
  if (!schedule) return "No schedule baseline";
  const actualEnd = update?.actualEnd ?? schedule.actualEnd;
  if (!actualEnd || (update?.progress ?? 0) < 100) return "In progress · actual end not recorded";
  const planned = new Date(`${schedule.plannedEnd}T${schedule.plannedEndTime ?? "12:00"}:00`);
  const actual = new Date(actualEnd.length > 10 ? actualEnd : `${actualEnd}T12:00:00`);
  const minutes = Math.round((actual - planned) / 60000);
  if (minutes === 0) return "On planned finish";
  const hours = Math.floor(Math.abs(minutes) / 60);
  const remainder = Math.abs(minutes) % 60;
  const duration = `${hours ? `${hours}h ` : ""}${remainder ? `${remainder}m` : ""}`.trim();
  return `${minutes > 0 ? "+" : "−"}${duration} · ${minutes > 0 ? "Delayed" : "Ahead"}`;
}

function formatActual(value) {
  if (!value) return "Not recorded";
  return value.length > 10 ? `${formatDate(value)} · ${formatDateTime(value)}` : formatDate(value);
}

function getMatch(data, fieldUpdateId) {
  return data.activityMatches.find((match) => match.fieldUpdateId === fieldUpdateId);
}

function getScheduleActivity(data, scheduleActivityId) {
  return data.scheduleActivities.find((activity) => activity.id === scheduleActivityId) ?? null;
}

function StatusBadge({ status }) {
  const labels = {
    submitted: "Submitted",
    processing: "Processing",
    matched: "Matched",
    low_confidence: "Low confidence",
    review_required: "Review required",
    unmatched: "Unmatched",
    rejected: "Rejected",
    reviewed: "Reviewed",
    action_required: "Action required",
    needs_review: "Needs Review",
    open: "Open",
    accepted: "Accepted",
  };
  const className = String(status).toLowerCase().replaceAll("_", "-").replaceAll(" ", "-");
  return <span className={`pm-workflow-status is-${className}`}>{labels[status] ?? status}</span>;
}

function reviewStatusFor(data, update) {
  if (update.reviewStatus) return update.reviewStatus;
  const match = getMatch(data, update.id);
  if (match?.matchStatus === "matched") return "reviewed";
  if (match?.matchStatus === "unmatched") return "unmatched";
  if (match?.matchStatus === "processing") return "processing";
  if (match?.matchStatus === "review_required" || match?.matchStatus === "low_confidence") return "needs_review";
  const item = data.reviewItems.find((entry) => entry.fieldUpdateId === update.id);
  if (item?.status === "accepted" || item?.status === "rejected") return "reviewed";
  return "submitted";
}

function Confidence({ value }) {
  const tone = value >= 80 ? "high" : value >= 60 ? "medium" : "low";
  return (
    <span className={`pm-confidence is-${tone}`}>
      <span className="pm-confidence-value">{value}%</span>
      <span className="pm-confidence-track" aria-hidden="true"><span style={{ width: `${value}%` }} /></span>
      <span className="pm-confidence-label">{tone === "high" ? "High" : tone === "medium" ? "Medium" : "Low"}</span>
    </span>
  );
}

function SourceIcon({ source }) {
  if (source.includes("Spreadsheet")) return <FileSpreadsheet size={15} />;
  if (source.includes("Diary")) return <ClipboardList size={15} />;
  if (source.includes("Supervisor")) return <MapPin size={15} />;
  return <FileText size={15} />;
}

function WorkflowPageHeader({ view, data, currentProjectId, openReviews, notice, clearNotice }) {
  const [title, description] = TITLES[view] ?? [view, "Project execution workspace."];
  const openCount = data.reviewItems.filter((item) => item.status === "open").length;
  const currentProject = data.projects.find((item) => item.id === currentProjectId);
  return (
    <>
      <div className="pm-workflow-heading">
        <div>
          <p className="pm-workflow-eyebrow">{currentProject ? `${currentProject.name} · ${currentProject.location}` : "NO ASSIGNED PROJECT"}</p>
          <h1><UiText>{title}</UiText></h1>
          <p><UiText>{description}</UiText></p>
        </div>
        <div className="pm-workflow-heading-context">
          {currentProject && <span className="pm-project-status"><span /> {currentProject.status}</span>}
          <button className="pm-workflow-review-count" type="button" onClick={openReviews}>
            <ShieldAlert size={15} /> {openCount}<UiText> open reviews </UiText><ArrowRight size={14} />
          </button>
        </div>
      </div>
      {notice && (
        <div className="pm-workflow-notice" role="status">
          <CheckCircle2 size={16} /> <span>{notice}</span>
          <button type="button" aria-label="Dismiss notification" onClick={clearNotice}><X size={15} /></button>
        </div>
      )}
    </>
  );
}

function WorkflowStepNav({ view, onNavigate }) {
  return (
    <nav className="pm-workflow-steps" aria-label="Field-to-schedule workflow">
      {WORKFLOW_STEPS.map((step, index) => (
        <div className="pm-workflow-step-wrap" key={step}>
          <button className={view === step ? "is-current" : ""} type="button" onClick={() => onNavigate(step)}>
            <span>{String(index + 1).padStart(2, "0")}</span>{step}
          </button>
          {index < WORKFLOW_STEPS.length - 1 && <ArrowRight size={14} aria-hidden="true" />}
        </div>
      ))}
    </nav>
  );
}

function OverviewMetrics({ data }) {
  const captured = data.fieldUpdates.length;
  const matched = data.activityMatches.filter((match) => match.matchStatus === "matched").length;
  const unmatched = data.activityMatches.filter((match) => match.matchStatus === "unmatched").length;
  const pending = data.reviewItems.filter((item) => item.status === "open").length;
  return (
    <div className="pm-workflow-metrics">
      <div><span><UiText>Field updates captured</UiText></span><strong>{captured}</strong><small><UiText>Records in assigned scope</UiText></small></div>
      <div><span><UiText>Linked to schedule</UiText></span><strong>{matched}</strong><small><UiText>Confirmed by planner</UiText></small></div>
      <div><span><UiText>Pending review</UiText></span><strong className="is-amber">{pending}</strong><small><UiText>Human decision required</UiText></small></div>
      <div><span><UiText>Unmatched activities</UiText></span><strong className="is-red">{unmatched}</strong><small><UiText>Schedule link not confirmed</UiText></small></div>
    </div>
  );
}

function FieldUpdateRows({ data, onOpenDetails, onNavigate, onSelectUpdate }) {
  return (
    <div className="pm-workflow-list">
      {data.fieldUpdates.map((update) => {
        const match = getMatch(data, update.id);
        const schedule = getScheduleActivity(data, match?.scheduleActivityId);
        return (
          <article className="pm-field-record" key={update.id}>
            <div className="pm-field-record-source"><span className="pm-source-icon"><SourceIcon source={update.source} /></span><div><strong>{update.source}</strong><small>{formatDateTime(update.submittedAt)} · {update.submittedBy}</small></div></div>
            <div className="pm-field-record-observation"><span className="pm-data-label"><UiText>FIELD INPUT</UiText></span><p>“{update.rawText}”</p><small>{update.discipline} · {update.location}</small></div>
            <div className="pm-field-record-extraction"><span className="pm-data-label"><UiText>EXTRACTED ACTIVITY</UiText></span><p>{update.extractedActivity.activityName}</p><small><UiText>Actual: </UiText>{formatDate(update.actualStart)} → {formatDate(update.actualEnd)}</small></div>
            <div className="pm-field-record-link"><span className="pm-data-label"><UiText>SUGGESTED SCHEDULE LINK</UiText></span><p>{schedule ? `${schedule.activityName} · ${schedule.level}` : "No schedule link"}</p><small>{schedule ? `${schedule.activityId} · ${schedule.discipline}` : "Find a matching activity"}</small></div>
            <div className="pm-field-record-result"><Confidence value={match?.confidence ?? 0} /><StatusBadge status={update.reviewStatus === "action_required" ? "action_required" : match?.matchStatus ?? "unmatched"} /><div className="pm-field-record-actions"><button type="button" onClick={() => onOpenDetails(update.id)}><UiText>Details</UiText></button><button type="button" onClick={() => { onSelectUpdate(update.id); onNavigate(match?.matchStatus === "matched" ? "Schedule" : "Planner Review"); }}><UiText>{match?.matchStatus === "matched" ? "Schedule" : "Review"}</UiText><ArrowRight size={13} /></button></div></div>
          </article>
        );
      })}
    </div>
  );
}

function FieldUpdatesPage({ data, onOpenDetails, onNavigate, onSelectUpdate }) {
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const updates = [...data.fieldUpdates].sort((left, right) => new Date(right.submittedAt) - new Date(left.submittedAt)).filter((update) => {
    const match = getMatch(data, update.id);
    const text = `${update.rawText} ${update.source} ${update.discipline} ${update.submittedBy}`.toLowerCase();
    const matchesQuery = text.includes(query.toLowerCase());
    const matchesStatus = statusFilter === "All statuses" || match?.matchStatus === statusFilter;
    return matchesQuery && matchesStatus;
  });
  return (
    <>
      <OverviewMetrics data={data} />
      <section className="pm-workflow-panel">
        <div className="pm-workflow-panel-heading"><div><h2><UiText>Captured field records</UiText></h2><p><UiText>Raw source text remains available alongside the extracted activity and its current plan link.</UiText></p></div><span>{updates.length}<UiText> of </UiText>{data.fieldUpdates.length}<UiText> records</UiText></span></div>
        <div className="pm-workflow-toolbar">
          <label className="pm-workflow-search"><Search size={15} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search field text, source, discipline" /></label>
          <label className="pm-workflow-select-label"><UiText>Status </UiText><span className="pm-workflow-select-wrap"><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="All statuses"><UiText>All statuses</UiText></option><option value="matched"><UiText>Matched</UiText></option><option value="low_confidence"><UiText>Low confidence</UiText></option><option value="review_required"><UiText>Review required</UiText></option><option value="unmatched"><UiText>Unmatched</UiText></option><option value="rejected"><UiText>Rejected</UiText></option></select><ChevronDown size={14} /></span></label>
        </div>
        {updates.length ? <FieldUpdateRows data={{ ...data, fieldUpdates: updates }} onOpenDetails={onOpenDetails} onNavigate={onNavigate} onSelectUpdate={onSelectUpdate} /> : <div className="pm-workflow-empty"><UiText>No field updates match these filters.</UiText></div>}
      </section>
    </>
  );
}

function MatchingPage({ data, selectedUpdateId, onSelectUpdate, onOpenDetails, onDecision, onCreateReview }) {
  const [scheduleChoice, setScheduleChoice] = useState("");
  const update = data.fieldUpdates.find((item) => item.id === selectedUpdateId) ?? data.fieldUpdates[0];
  const match = update ? getMatch(data, update.id) : null;
  const alternatives = data.scheduleActivities.filter((item) => item.projectId === update?.projectId);
  const selectedScheduleId = scheduleChoice || match?.scheduleActivityId || "";
  const selectedSchedule = getScheduleActivity(data, selectedScheduleId);

  return (
    <>
      <OverviewMetrics data={data} />
      <div className="pm-matching-layout">
        <section className="pm-workflow-panel pm-matching-queue">
          <div className="pm-workflow-panel-heading"><div><h2><UiText>Field observations</UiText></h2><p><UiText>Select a captured update to inspect its match.</UiText></p></div><span>{data.fieldUpdates.length}<UiText> records</UiText></span></div>
          <div className="pm-matching-select-list">
            {data.fieldUpdates.map((item) => {
              const itemMatch = getMatch(data, item.id);
              return <button className={item.id === update?.id ? "is-selected" : ""} type="button" key={item.id} onClick={() => { onSelectUpdate(item.id); setScheduleChoice(""); }}><span><SourceIcon source={item.source} /></span><span className="pm-matching-select-copy"><strong>{item.rawText}</strong><small>{item.discipline} · {formatDateTime(item.submittedAt)}</small></span><StatusBadge status={itemMatch?.matchStatus ?? "unmatched"} /></button>;
            })}
          </div>
        </section>

        {update && match && (
          <section className="pm-workflow-panel pm-match-detail">
            <div className="pm-workflow-panel-heading"><div><h2><UiText>Field-to-plan match</UiText></h2><p>{update.id} · {update.source}<UiText> · submitted by </UiText>{update.submittedBy}</p></div><button className="pm-text-button" type="button" onClick={() => onOpenDetails(update.id)}><UiText>Full activity details</UiText></button></div>
            <div className="pm-match-bridge">
              <div className="pm-match-side"><span className="pm-data-label"><UiText>FIELD OBSERVATION</UiText></span><p>“{update.rawText}”</p><small>{update.discipline} · {update.location}</small><small><UiText>Actual dates: </UiText>{formatDate(update.actualStart)} → {formatDate(update.actualEnd)}</small></div>
              <div className="pm-match-connector"><ArrowRight size={17} /><span><UiText>extracted</UiText></span></div>
              <div className="pm-match-side"><span className="pm-data-label"><UiText>EXTRACTED ACTIVITY</UiText></span><p>{update.extractedActivity.activityName}</p><small>{update.extractedActivity.discipline} · {update.extractedActivity.location}</small><small><UiText>Source retained in audit trail</UiText></small></div>
            </div>
            <div className="pm-schedule-suggestion">
              <div className="pm-schedule-suggestion-heading"><div><span className="pm-data-label"><UiText>SCHEDULE ACTIVITY</UiText></span><h3>{selectedSchedule?.activityName ?? "No schedule activity selected"}</h3><p>{selectedSchedule ? `${selectedSchedule.activityId} · ${selectedSchedule.level} · ${selectedSchedule.discipline}` : "Choose an activity from this project's schedule below."}</p></div><Confidence value={match.confidence} /></div>
              {selectedSchedule && <div className="pm-schedule-dates"><span><CalendarDays size={14} /><UiText> Planned </UiText>{formatDate(selectedSchedule.plannedStart)} → {formatDate(selectedSchedule.plannedEnd)}</span><span><UiText>Actual </UiText>{formatDate(selectedSchedule.actualStart ?? update.actualStart)} → {formatDate(selectedSchedule.actualEnd ?? update.actualEnd)}</span></div>}
              <label className="pm-schedule-choice-label">{match.scheduleActivityId ? "Choose another schedule activity" : "Find a schedule activity"}<span className="pm-workflow-select-wrap"><select value={selectedScheduleId} onChange={(event) => setScheduleChoice(event.target.value)}><option value=""><UiText>Select an activity</UiText></option>{alternatives.map((activity) => <option value={activity.id} key={activity.id}>{activity.activityName} · {activity.activityId} ({activity.level})</option>)}</select><ChevronDown size={14} /></span></label>
            </div>
            <FieldEvidence update={update} />
        <MatchEvidencePanel match={match} selectedActivityId={selectedScheduleId} onSelectCandidate={setScheduleChoice} />
            {match.matchStatus === "matched" ? <div className="pm-match-confirmed"><CheckCircle2 size={17} /><UiText> Confirmed by </UiText>{match.matchedBy} · {formatDateTime(match.reviewedAt)}<button type="button" onClick={() => onOpenDetails(update.id)}><UiText>View audit</UiText></button></div> : (
              <div className="pm-workflow-actions">
                {match.matchStatus === "unmatched" && <button className="pm-button-secondary" type="button" onClick={() => onCreateReview(update.id)}><UiText>Create review item</UiText></button>}
                <button className="pm-button-secondary" type="button" onClick={() => onOpenDetails(update.id)}><UiText>Review context</UiText></button>
                {selectedSchedule && <button className="pm-button-primary" type="button" onClick={() => onDecision(update.id, "confirm", selectedSchedule.id)}><Check size={15} /><UiText> Confirm match</UiText></button>}
                {match.matchStatus === "unmatched" && !selectedSchedule && <span className="pm-workflow-inline-note"><Unlink size={14} /><UiText> No schedule link selected</UiText></span>}
              </div>
            )}
          </section>
        )}
      </div>
    </>
  );
}

function ReviewQueuePage({ data, onOpenDetails }) {
  const [statusFilter, setStatusFilter] = useState("open");
  const [projectFilter, setProjectFilter] = useState("all");
  const [disciplineFilter, setDisciplineFilter] = useState("all");
  const [confidenceFilter, setConfidenceFilter] = useState("all");
  const [query, setQuery] = useState("");
  const openStatuses = new Set(["needs_review", "action_required", "unmatched", "submitted", "processing"]);
  const updates = data.fieldUpdates.filter((update) => {
    const match = getMatch(data, update.id);
    const status = reviewStatusFor(data, update);
    const confidence = match?.confidence ?? 0;
    const project = data.projects.find((item) => item.id === update.projectId);
    const searchText = `${update.rawText} ${update.extractedActivity?.activityName ?? ""} ${update.submittedBy} ${update.location} ${project?.name ?? ""}`.toLowerCase();
    const statusMatches = statusFilter === "all" || (statusFilter === "open" ? openStatuses.has(status) : statusFilter === "matched" ? match?.matchStatus === "matched" : statusFilter === "unmatched" ? match?.matchStatus === "unmatched" && status !== "action_required" : status === statusFilter);
    const confidenceMatches = confidenceFilter === "all" || (confidenceFilter === "high" ? confidence >= 80 : confidenceFilter === "medium" ? confidence >= 60 && confidence < 80 : confidence < 60);
    return statusMatches && confidenceMatches && (projectFilter === "all" || update.projectId === projectFilter) && (disciplineFilter === "all" || update.discipline === disciplineFilter) && searchText.includes(query.trim().toLowerCase());
  }).sort((left, right) => new Date(right.submittedAt) - new Date(left.submittedAt));
  return (
    <>
      <OverviewMetrics data={data} />
      <section className="pm-workflow-panel">
        <div className="pm-workflow-panel-heading"><div><h2><UiText>Field Update Review</UiText></h2><p><UiText>Inspect the field report, proposed L5/L6 link, and actual data before recording a decision.</UiText></p></div><span>{updates.length}<UiText> updates</UiText></span></div>
        <div className="pm-review-filters">
          <label><span><UiText>Search</UiText></span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search field text, activity, submitter" /></label>
          <label><span><UiText>Status</UiText></span><select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="open"><UiText>Open review</UiText></option><option value="all"><UiText>All statuses</UiText></option><option value="needs_review"><UiText>Needs Review</UiText></option><option value="matched"><UiText>Matched</UiText></option><option value="unmatched"><UiText>Unmatched</UiText></option><option value="action_required"><UiText>Action Required</UiText></option><option value="reviewed"><UiText>Reviewed</UiText></option><option value="submitted"><UiText>Submitted</UiText></option><option value="processing"><UiText>Processing</UiText></option></select></label>
          <label><span><UiText>Project</UiText></span><select value={projectFilter} onChange={(event) => setProjectFilter(event.target.value)}><option value="all"><UiText>All projects</UiText></option>{data.projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label>
          <label><span><UiText>Discipline</UiText></span><select value={disciplineFilter} onChange={(event) => setDisciplineFilter(event.target.value)}><option value="all"><UiText>All disciplines</UiText></option>{[...new Set(data.fieldUpdates.map((item) => item.discipline))].sort().map((discipline) => <option key={discipline}>{discipline}</option>)}</select></label>
          <label><span><UiText>Confidence</UiText></span><select value={confidenceFilter} onChange={(event) => setConfidenceFilter(event.target.value)}><option value="all"><UiText>Any confidence</UiText></option><option value="high"><UiText>High · 80%+</UiText></option><option value="medium"><UiText>Medium · 60–79%</UiText></option><option value="low"><UiText>Low · below 60%</UiText></option></select></label>
        </div>
        {updates.length ? <div className="pm-review-list">{updates.map((update) => {
          const match = getMatch(data, update.id);
          const schedule = getScheduleActivity(data, match?.scheduleActivityId);
          const reviewItem = data.reviewItems.find((item) => item.fieldUpdateId === update.id);
          const status = reviewStatusFor(data, update);
          const project = data.projects.find((item) => item.id === update.projectId);
          const suggested = schedule ? `${schedule.level} · ${schedule.activityName}` : "No confident schedule match";
          return <article className="pm-review-record" key={update.id}>
            <div className="pm-review-category"><span className="pm-review-category-icon"><ClipboardList size={16} /></span><div><span>{update.id}</span><small>{formatDateTime(update.submittedAt)} · {update.submittedBy}</small></div></div>
            <div className="pm-review-context"><strong><UiText>FIELD INPUT</UiText></strong><p>“{update.rawText}”</p><small>{project?.name} · {update.discipline} · {update.location}</small></div>
            <div className="pm-review-context"><strong><UiText>EXTRACTED / SUGGESTED</UiText></strong><p>{update.extractedActivity?.activityName ?? update.activity ?? "Field activity pending extraction"}</p><small>{suggested} · {match?.confidence ?? 0}%</small></div>
            <div className="pm-review-confidence"><Confidence value={match?.confidence ?? 0} /><div className="pm-review-badges"><StatusBadge status={status} />{match?.matchStatus && <StatusBadge status={match.matchStatus} />}</div>{update.pmFeedback && <p className="pm-review-feedback-preview">PM: {update.pmFeedback}</p>}{reviewItem?.reason && <p>{reviewItem.reason}</p>}</div>
            <div className="pm-review-actions"><button type="button" className="pm-button-primary" onClick={() => onOpenDetails(update.id)}><UiText>Review update </UiText><ArrowRight size={13} /></button></div>
          </article>;
        })}</div> : <div className="pm-workflow-empty"><CheckCircle2 size={18} /> <UiText>{statusFilter === "open" ? "No updates require review." : "No field updates match these filters."}</UiText></div>}
      </section>
    </>
  );
}

function SchedulePage({ data, currentProjectId, onOpenDetails }) {
  const project = data.projects.find((item) => item.id === currentProjectId);
  const scheduleActivities = project ? data.scheduleActivities.filter((item) => item.projectId === project.id) : [];
  return (
    <>
      <p><UiText>Recorded schedule state can include provisional TL actions. PM-confirmed variance and completion are shown in Execution intelligence.</UiText></p>
      <section className="pm-workflow-panel">
        <div className="pm-workflow-panel-heading"><div><h2>{project ? `${project.name} schedule activities · L5/L6` : "Schedule activities · L5/L6"}</h2><p><UiText>Actual dates are drawn from confirmed or reported field execution.</UiText></p></div><span>{scheduleActivities.length}<UiText> activities</UiText></span></div>
        {scheduleActivities.length ? <div className="pm-schedule-table-wrap"><table className="pm-schedule-table"><thead><tr><th><UiText>Activity</UiText></th><th><UiText>Discipline</UiText></th><th><UiText>Level</UiText></th><th><UiText>Planned dates</UiText></th><th><UiText>Actual dates</UiText></th><th><UiText>Status</UiText></th><th><UiText>Field link</UiText></th></tr></thead><tbody>{scheduleActivities.map((activity) => {
          const update = data.fieldUpdates.find((record) => {
            const match = getMatch(data, record.id);
            return match?.scheduleActivityId === activity.id && match.matchStatus === "matched";
          });
          return <tr key={activity.id}><td><button className="pm-table-link" type="button" onClick={() => update && onOpenDetails(update.id)}><strong>{activity.activityName}</strong><small>{activity.activityId} · {activity.id}</small></button></td><td>{activity.discipline}</td><td><span className="pm-level-tag">{activity.level}</span></td><td>{formatDate(activity.plannedStart)}<small><UiText>to </UiText>{formatDate(activity.plannedEnd)}</small></td><td>{formatDate(activity.actualStart)}<small><UiText>to </UiText>{formatDate(activity.actualEnd)}</small></td><td><span className={`pm-schedule-status is-${activity.status.toLowerCase().replaceAll(" ", "-")}`}>{activity.status}</span></td><td>{update ? <button type="button" className="pm-text-button" onClick={() => onOpenDetails(update.id)}>{update.id}</button> : <span className="pm-muted-cell"><UiText>No confirmed field link</UiText></span>}</td></tr>;
        })}</tbody></table></div> : <div className="pm-workflow-empty">{project ? "No schedule activities are assigned to this project." : "No assigned project. Ask an administrator to assign a project to this Project Manager."}</div>}
      </section>
    </>
  );
}

function ProjectsPage({ data, currentProjectId, onSelectProject, onNavigate }) {
  return <section className="pm-workflow-panel"><div className="pm-workflow-panel-heading"><div><h2><UiText>Assigned project portfolio</UiText></h2><p><UiText>Choose a current project to scope its schedule and execution analytics.</UiText></p></div><span>{data.projects.length}<UiText> assigned </UiText>{data.projects.length === 1 ? "project" : "projects"}</span></div>{data.projects.length ? <div className="pm-project-list">{data.projects.map((project) => <article key={project.id}><div><span className="pm-project-status"><span /> {project.status}</span><h3>{project.name}</h3><p><MapPin size={14} /> {project.location}</p><small>{project.id}<UiText> · Disciplines: </UiText>{project.disciplines.join(" · ")}</small></div><div className="pm-project-progress"><span><UiText>Confirmed activity actuals available in execution intelligence</UiText></span><button className="pm-button-secondary" type="button" onClick={() => { onSelectProject(project.id); onNavigate("Schedule"); }}>{project.id === currentProjectId ? "Current schedule" : "Set current project"} <ArrowRight size={14} /></button></div></article>)}</div> : <div className="pm-workflow-empty"><UiText>No assigned projects. Ask an administrator to assign a project to this Project Manager.</UiText></div>}</section>;
}

function SettingsPage() {
  return <section className="pm-workflow-panel"><div className="pm-workflow-panel-heading"><div><h2><UiText>Workspace environment</UiText></h2><p><UiText>Operational configuration is read-only for Project Managers.</UiText></p></div><span><UiText>Persistent API data</UiText></span></div><div className="pm-settings-list"><div><span><UiText>Project data source</UiText></span><strong>PostgreSQL-backed FastAPI</strong></div><div><span><UiText>Activity hierarchy</UiText></span><strong><UiText>L5 / L6 schedule activities</UiText></strong></div><div><span><UiText>Match decisions</UiText></span><strong>PostgreSQL-backed and persistent</strong></div><div><span><UiText>Authentication</UiText></span><strong>HttpOnly server session · role checked server-side</strong></div></div></section>;
}

function ActivityDetailDrawer({ data, updateId, onClose, onDecision }) {
  if (!updateId) return null;
  const update = data.fieldUpdates.find((item) => item.id === updateId);
  const match = getMatch(data, updateId);
  if (!update || !match) return null;
  return <ActivityDetailContent key={update.id} data={data} update={update} match={match} onClose={onClose} onDecision={onDecision} />;
}

function ActivityDetailContent({ data, update, match, onClose, onDecision }) {
  const [showChangeActivity, setShowChangeActivity] = useState(false);
  const [selectedActivityId, setSelectedActivityId] = useState(match.scheduleActivityId ?? "");
  const [activityQuery, setActivityQuery] = useState("");
  const [showUnmatchedReason, setShowUnmatchedReason] = useState(false);
  const [unmatchedReason, setUnmatchedReason] = useState("No schedule activity found");
  const [feedback, setFeedback] = useState(update.pmFeedback ?? "");
  const schedule = getScheduleActivity(data, match.scheduleActivityId);
  const selectedSchedule = getScheduleActivity(data, selectedActivityId);
  const reviewItem = data.reviewItems.find((item) => item.fieldUpdateId === update.id);
  const project = data.projects.find((item) => item.id === update.projectId);
  const team = data.teams?.find((item) => item.id === update.teamId);
  const alternatives = data.scheduleActivities.filter((item) => item.projectId === update.projectId && `${item.activityName} ${item.activityId} ${item.level}`.toLowerCase().includes(activityQuery.toLowerCase()));
  const history = update.reviewHistory ?? [
    { actor: update.submittedBy, action: "Field update submitted", occurredAt: update.submittedAt },
    ...(match.scheduleActivityId ? [{ actor: "PRAVAHA demo matcher", action: `Suggested ${schedule?.level ?? "schedule"} match · ${match.confidence}% confidence`, occurredAt: update.submittedAt }] : []),
    ...(match.reviewedAt ? [{ actor: match.matchedBy ?? "Project Manager", action: match.reviewComment ?? "Review decision recorded", occurredAt: match.reviewedAt }] : []),
  ];
  const currentReviewStatus = reviewStatusFor(data, update);
  const completed = (update.progress ?? (update.actualEnd ? 100 : 0)) >= 100;
  const plannedStart = schedule ? `${formatDate(schedule.plannedStart)}${schedule.plannedStartTime ? ` · ${schedule.plannedStartTime}` : ""}` : "Not linked";
  const plannedEnd = schedule ? `${formatDate(schedule.plannedEnd)}${schedule.plannedEndTime ? ` · ${schedule.plannedEndTime}` : ""}` : "Not linked";

  const submitDecision = (decision, scheduleId, reason = "", note = feedback.trim()) => onDecision(update.id, decision, scheduleId, reason, note);

  return (
    <div className="pm-drawer-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <aside className="pm-activity-drawer" role="dialog" aria-modal="true" aria-labelledby="pm-activity-title">
        <div className="pm-drawer-header"><div><span className="pm-data-label"><UiText>FIELD UPDATE REVIEW · </UiText>{update.id}</span><h2 id="pm-activity-title">{update.extractedActivity?.activityName ?? update.activity ?? "Field activity"}</h2></div><button className="pm-icon-action" type="button" aria-label="Close activity details" onClick={onClose}><X size={17} /></button></div>
        <div className="pm-drawer-status"><StatusBadge status={currentReviewStatus} /><Confidence value={match.confidence ?? 0} /></div>

        <section className="pm-drawer-section"><h3><UiText>Field update</UiText></h3><blockquote>“{update.rawText}”</blockquote><dl>
          <div><dt><UiText>Project / team</UiText></dt><dd>{project?.name ?? "Project"} · {team?.name ?? "Team not recorded"}</dd></div>
          <div><dt><UiText>Submitted by</UiText></dt><dd>{update.submittedBy}</dd></div><div><dt><UiText>Submitted</UiText></dt><dd>{formatDateTime(update.submittedAt)}</dd></div><div><dt><UiText>Source</UiText></dt><dd>{update.source}</dd></div>
          <div><dt><UiText>Discipline</UiText></dt><dd>{update.discipline}</dd></div><div><dt><UiText>Location</UiText></dt><dd>{update.location}</dd></div>{update.observation && <div><dt><UiText>Observation / blocker</UiText></dt><dd>{update.observation}</dd></div>}
        </dl></section>

        <section className="pm-drawer-section"><h3><UiText>Extracted information</UiText></h3><dl>
          <div><dt><UiText>Activity</UiText></dt><dd>{update.extractedActivity?.activityName ?? update.activity ?? "Pending extraction"}</dd></div><div><dt><UiText>Progress</UiText></dt><dd>{update.progress ?? "Not reported"}{update.progress != null ? "%" : ""}</dd></div>
          <div><dt><UiText>Detected discipline</UiText></dt><dd>{update.extractedActivity?.discipline ?? "Not detected"}</dd></div><div><dt><UiText>Detected location</UiText></dt><dd>{update.extractedActivity?.location ?? "Not reported"}</dd></div>
          <div><dt><UiText>Identifiers</UiText></dt><dd>{update.extractedActivity?.identifiers?.join(", ") || "Not detected"}</dd></div><div><dt><UiText>Action</UiText></dt><dd>{update.extractedActivity?.action ?? "Not detected"}</dd></div>
          <div><dt><UiText>Date references</UiText></dt><dd>{update.extractedActivity?.dateReferences?.join(", ") || "None reported"}</dd></div>
          <div><dt><UiText>Actual start</UiText></dt><dd>{formatActual(update.actualStart)}</dd></div><div><dt><UiText>Actual end</UiText></dt><dd>{formatActual(update.actualEnd)}</dd></div>
        </dl></section>

        <section className="pm-drawer-section pm-match-panel"><div className="pm-match-panel-heading"><h3><UiText>Suggested schedule match</UiText></h3><span>{match.confidence ?? 0}<UiText>% confidence</UiText></span></div>
          {schedule ? <div className="pm-match-panel-activity"><span>{schedule.level} · {schedule.activityId}</span><strong>{schedule.activityName}</strong><small>{schedule.discipline} · {schedule.status}</small></div> : <div className="pm-no-suggestion"><Unlink size={15} /><UiText> No confident schedule match found</UiText></div>}
          <p><UiText>Compare the field description with the current schedule link. Recommendations are calculated from stored L5/L6 activities and need PM confirmation.</UiText></p>
          <div className="pm-planned-actual"><div className="pm-planned-actual-heading"><span></span><strong><UiText>Planned</UiText></strong><strong><UiText>Actual</UiText></strong></div>
            <div><span><UiText>Start</UiText></span><span>{plannedStart}</span><span>{formatActual(update.actualStart)}</span></div>
            <div><span><UiText>End</UiText></span><span>{plannedEnd}</span><span>{formatActual(update.actualEnd)}</span></div>
            <div><span><UiText>Progress</UiText></span><span><UiText>Baseline</UiText></span><span>{update.progress ?? (completed ? 100 : "Not reported")}{update.progress != null || completed ? "%" : ""}</span></div>
          </div>
          <div className="pm-variance-line"><span><UiText>Schedule variance</UiText></span><strong>{formatScheduleVariance(schedule, update)}</strong></div>
        </section>

        <FieldEvidence update={update} />
        <MatchEvidencePanel match={match} selectedActivityId={selectedActivityId} onSelectCandidate={(id) => { setSelectedActivityId(id); setShowChangeActivity(true); }} />

        <div className="pm-review-edit-control"><button type="button" className="pm-button-secondary" aria-expanded={showChangeActivity} onClick={() => setShowChangeActivity((value) => !value)}>{showChangeActivity ? "Close activity search" : schedule ? "Change activity" : "Find schedule activity"}</button>
          {showChangeActivity && <div className="pm-activity-search"><label><UiText>Search schedule activities</UiText><input value={activityQuery} onChange={(event) => setActivityQuery(event.target.value)} placeholder="Activity name or ID" /></label><label><UiText>Suggested activity</UiText><select value={selectedActivityId} onChange={(event) => setSelectedActivityId(event.target.value)}><option value=""><UiText>Select an L5/L6 activity</UiText></option>{alternatives.map((item) => <option value={item.id} key={item.id}>{item.level} · {item.activityName} · {item.activityId}</option>)}</select></label><button type="button" className="pm-button-secondary" disabled={!selectedSchedule || selectedActivityId === match.scheduleActivityId} onClick={() => submitDecision("change", selectedActivityId)}><UiText>Save changed match</UiText></button></div>}
        </div>

        <section className="pm-drawer-section pm-feedback-section"><h3><UiText>PM feedback to Team Leader</UiText></h3><textarea aria-label="PM feedback" value={feedback} onChange={(event) => setFeedback(event.target.value)} rows={3} placeholder="Add a concise note or request missing field information" /><div className="pm-feedback-actions"><button type="button" className="pm-button-secondary" disabled={!feedback.trim()} onClick={() => submitDecision("feedback", match.scheduleActivityId)}><UiText>Request information</UiText></button><small><UiText>Team Leader will see this note as Action Required.</UiText></small></div></section>

        {showUnmatchedReason && <section className="pm-unmatched-reason"><label><UiText>Reason</UiText><select value={unmatchedReason} onChange={(event) => setUnmatchedReason(event.target.value)}>{["No schedule activity found", "Insufficient information", "Incorrect activity description", "New/unplanned activity", "Other"].map((reason) => <option key={reason}>{reason}</option>)}</select></label><label><UiText>PM note (optional)</UiText><textarea value={feedback} onChange={(event) => setFeedback(event.target.value)} rows={2} placeholder="For example: Please confirm valve tag and location." /></label><div><button type="button" className="pm-button-secondary" onClick={() => setShowUnmatchedReason(false)}><UiText>Cancel</UiText></button><button type="button" className="pm-button-danger" onClick={() => submitDecision("unmatched", null, unmatchedReason)}><UiText>Confirm unmatched</UiText></button></div></section>}

        {reviewItem && <section className="pm-drawer-review"><span>{reviewItem.category} · {reviewItem.id}</span><p>{reviewItem.reason}</p>{reviewItem.reviewer && <small><UiText>Reviewed by </UiText>{reviewItem.reviewer} · {formatDateTime(reviewItem.reviewedAt)}</small>}</section>}
        {update.pmFeedback && <section className="pm-drawer-review is-feedback"><span><UiText>Last PM feedback</UiText></span><p>{update.pmFeedback}</p></section>}
        <section className="pm-drawer-audit"><h3><UiText>Review history</UiText></h3><ol>{history.map((event, index) => <li key={`${event.occurredAt}-${index}`}><span>{formatDateTime(event.occurredAt)}</span><div><strong>{event.actor}</strong><p>{event.action}</p></div></li>)}</ol></section>
        <div className="pm-drawer-actions"><button className="pm-button-secondary" type="button" onClick={onClose}><UiText>Close</UiText></button><button className="pm-button-danger" type="button" onClick={() => setShowUnmatchedReason((value) => !value)}><UiText>Mark unmatched</UiText></button>{selectedSchedule && currentReviewStatus !== "reviewed" && <button className="pm-button-primary" type="button" onClick={() => submitDecision("confirm", selectedActivityId)}><Check size={15} /><UiText> Confirm match</UiText></button>}</div>
      </aside>
    </div>
  );
}

export default function ProjectWorkflowWorkspace({ view, data, currentProjectId, onSelectProject, selectedUpdateId, detailUpdateId, onSelectUpdate, onOpenDetails, onCloseDetails, onDecision, onCreateReview, onNavigate, notice, clearNotice }) {
  const openReviews = () => onNavigate("Planner Review");
  const page = useMemo(() => {
    switch (view) {
      case "Field Updates": return <FieldUpdatesPage data={data} onOpenDetails={onOpenDetails} onNavigate={onNavigate} onSelectUpdate={onSelectUpdate} />;
      case "Activity Matching": return <MatchingPage data={data} selectedUpdateId={selectedUpdateId} onSelectUpdate={onSelectUpdate} onOpenDetails={onOpenDetails} onDecision={onDecision} onCreateReview={onCreateReview} />;
      case "Planner Review": return <ReviewQueuePage data={data} onOpenDetails={onOpenDetails} />;
      case "Schedule": return <SchedulePage data={data} currentProjectId={currentProjectId} onOpenDetails={onOpenDetails} />;
      case "Projects": return <ProjectsPage data={data} currentProjectId={currentProjectId} onSelectProject={onSelectProject} onNavigate={onNavigate} />;
      case "Settings": return <SettingsPage />;
      default: return <FieldUpdatesPage data={data} onOpenDetails={onOpenDetails} onNavigate={onNavigate} onSelectUpdate={onSelectUpdate} />;
    }
  }, [view, data, currentProjectId, onSelectProject, selectedUpdateId, onSelectUpdate, onOpenDetails, onDecision, onCreateReview, onNavigate]);

  return (
    <div className="pm-workflow-page">
      <WorkflowPageHeader view={view} data={data} currentProjectId={currentProjectId} openReviews={openReviews} notice={notice} clearNotice={clearNotice} />
      <WorkflowStepNav view={view} onNavigate={onNavigate} />
      {["Activity Matching", "Planner Review", "Analytics"].includes(view) && <MatchingHealth data={data} />}
      {page}
      <ActivityDetailDrawer data={data} updateId={detailUpdateId} onClose={onCloseDetails} onDecision={onDecision} />
    </div>
  );
}
