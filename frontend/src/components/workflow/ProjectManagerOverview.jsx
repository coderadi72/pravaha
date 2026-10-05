import { useMemo, useState } from "react";
import { AlertTriangle, ArrowRight, BarChart3, CalendarDays, CheckCircle2, ClipboardCheck, Clock3, FolderKanban, RefreshCw } from "lucide-react";
import UiText from "../../ui/UiText.jsx";
import "../../styles/project-manager-overview.css";

const day = (value) => value ? new Date(value.length > 10 ? value : `${value}T12:00:00`) : null;
const valid = (value) => value && !Number.isNaN(value.getTime());

function BarGroup({ items, label, onSelect }) {
  const max = Math.max(1, ...items.flatMap((item) => [item.planned ?? 0, item.confirmed ?? 0]));
  return <div className="pmo-bar-chart" role="img" aria-label={label}>
    {items.map((item) => <button type="button" className="pmo-bar-group" key={item.label} onClick={() => onSelect?.(item)} aria-label={`${item.label}: planned ${item.planned ?? "not available"}, confirmed ${item.confirmed ?? "not available"}`}>
      <span className="pmo-bar-pair"><i className="pmo-bar is-planned" style={{ height: `${Math.max(3, ((item.planned ?? 0) / max) * 100)}%` }} /><i className="pmo-bar is-confirmed" style={{ height: `${item.confirmed == null ? 0 : Math.max(3, (item.confirmed / max) * 100)}%` }} /></span>
      <strong>{item.label}</strong>
    </button>)}
  </div>;
}

function ProjectManagerOverview({ data, currentProjectId, onSelectProject, onNavigate, onSelectUpdate, onRefresh }) {
  const [period, setPeriod] = useState("30");
  const project = data.projects.find((item) => item.id === currentProjectId) ?? data.projects[0];
  const projectId = project?.id;
  const [from, to] = useMemo(() => {
    const end = new Date();
    const start = new Date(end);
    start.setDate(end.getDate() - (period === "7" ? 7 : period === "90" ? 90 : 30));
    return [start, end];
  }, [period]);
  const updates = data.fieldUpdates.filter((item) => item.projectId === projectId);
  const activities = data.scheduleActivities.filter((item) => item.projectId === projectId);
  const matches = data.activityMatches.filter((item) => updates.some((update) => update.id === item.fieldUpdateId));
  const periodUpdates = updates.filter((item) => { const submitted = day(item.submittedAt); return valid(submitted) && submitted >= from && submitted <= to; });
  const reviewed = updates.filter((item) => item.reviewStatus === "reviewed" || matches.some((match) => match.fieldUpdateId === item.id && match.matchStatus === "matched"));
  const progressValues = reviewed.map((item) => item.progress).filter((value) => typeof value === "number");
  const confirmedProgress = progressValues.length ? Math.round(progressValues.reduce((sum, value) => sum + value, 0) / progressValues.length) : null;
  const planned = activities.length ? Math.round(activities.filter((item) => valid(day(item.plannedEnd)) && day(item.plannedEnd) <= to).length / activities.length * 100) : null;
  const delayed = activities.filter((item) => String(item.status).toLowerCase().includes("delay") || (valid(day(item.actualEnd)) && valid(day(item.plannedEnd)) && day(item.actualEnd) > day(item.plannedEnd))).length;
  const pending = updates.filter((item) => item.reviewStatus !== "reviewed" && !matches.some((match) => match.fieldUpdateId === item.id && match.matchStatus === "matched")).length;
  const warnings = (data.executionWarnings ?? []).filter((item) => item.projectId === projectId && item.status !== "ACKNOWLEDGED").length;
  const disciplines = [...new Set(activities.map((item) => item.discipline).filter(Boolean))].map((name) => {
    const values = reviewed.filter((item) => item.discipline === name).map((item) => item.progress).filter((value) => typeof value === "number");
    return { name, value: values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : null };
  });
  const reviewRows = periodUpdates.filter((item) => item.reviewStatus !== "reviewed").slice(0, 5);
  const activityBars = Object.values(periodUpdates.reduce((result, item) => { const submitted = day(item.submittedAt); if (!valid(submitted)) return result; const key = submitted.toISOString().slice(0, 10); result[key] ??= { label: submitted.toLocaleDateString("en-IN", { day: "2-digit", month: "short" }), planned: 0, confirmed: 0 }; result[key].planned += 1; if (item.reviewStatus === "reviewed") result[key].confirmed += 1; return result; }, {})).slice(-7);
  const cards = [
    ["Confirmed progress", confirmedProgress == null ? "—" : `${confirmedProgress}%`, `${reviewed.length}/${activities.length} activities with confirmed evidence`, CheckCircle2, "Reports"],
    ["Delayed activities", delayed, "Current project schedule signals", AlertTriangle, "Schedule"],
    ["Pending PM reviews", pending, "Human decision required", ClipboardCheck, "Planner Review"],
    ["Open warnings", warnings, "Execution intelligence warnings", AlertTriangle, "Analytics"],
  ];
  return <div className="pmo-overview">
    <header className="pmo-heading"><div><span className="pmo-eyebrow"><UiText>PROJECT EXECUTION</UiText></span><h1><UiText>Project execution</UiText></h1><p><UiText>Plan, review and confirm actual progress.</UiText></p></div><div className="pmo-filters"><label><UiText>Project</UiText><select value={projectId ?? ""} onChange={(event) => onSelectProject(event.target.value)}>{data.projects.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label><UiText>Reporting period</UiText><select value={period} onChange={(event) => setPeriod(event.target.value)}><option value="7"><UiText>Last 7 days</UiText></option><option value="30"><UiText>Last 30 days</UiText></option><option value="90"><UiText>Last 90 days</UiText></option></select></label><button type="button" className="pmo-icon-button" aria-label="Refresh project dashboard" onClick={onRefresh}><RefreshCw size={15} /></button></div></header>
    {!project && <section className="pmo-empty"><FolderKanban size={20} /><UiText>No assigned project. Ask an administrator to assign a project.</UiText></section>}
    {project && <>
      <div className="pmo-context"><span>{project.name} · {project.location}</span><span><CalendarDays size={14} /> {period === "7" ? "Last 7 days" : period === "90" ? "Last 90 days" : "Last 30 days"}</span></div>
      <div className="pmo-kpis">{cards.map(([label, value, note, Icon, destination]) => <button type="button" className="pmo-card pmo-kpi" key={label} onClick={() => onNavigate(destination)}><span>{label}<Icon size={16} /></span><strong>{value}</strong><small>{note}<ArrowRight size={12} /></small></button>)}</div>
      <div className="pmo-main-grid"><section className="pmo-card pmo-chart-panel"><div className="pmo-panel-heading"><div><h2><UiText>Planned vs confirmed progress</UiText></h2><p><UiText>Current schedule snapshot; no historical progress is inferred.</UiText></p></div><div className="pmo-legend"><span><i className="is-planned" /><UiText>Planned</UiText></span><span><i className="is-confirmed" /><UiText>PM-confirmed actual</UiText></span></div></div><BarGroup items={[{ label: "Current", planned: planned ?? 0, confirmed: confirmedProgress }]} label="Planned and PM-confirmed progress" onSelect={() => onNavigate("Reports")} /><p className="pmo-note">{planned == null ? "No dated schedule baseline is available." : `${activities.length} scheduled activities · ${reviewed.length} records with confirmed evidence.`}</p></section><section className="pmo-card pmo-discipline-panel"><div className="pmo-panel-heading"><div><h2><UiText>Discipline progress</UiText></h2><p><UiText>Known confirmed progress only</UiText></p></div><BarChart3 size={17} /></div>{disciplines.length ? disciplines.map((item) => <button type="button" className="pmo-discipline" key={item.name} onClick={() => onNavigate("Analytics")}><span>{item.name}</span><strong>{item.value == null ? "—" : `${item.value}%`}</strong><i><b style={{ width: `${item.value ?? 0}%` }} /></i></button>) : <div className="pmo-empty"><UiText>No discipline evidence in this project.</UiText></div>}</section></div>
      <div className="pmo-secondary-grid"><section className="pmo-card"><div className="pmo-panel-heading"><div><h2><UiText>Field-update activity</UiText></h2><p><UiText>Submission cohorts in the selected reporting period</UiText></p></div><Clock3 size={17} /></div>{activityBars.length ? <BarGroup items={activityBars} label="Field updates submitted and confirmed by day" onSelect={() => onNavigate("Field Updates")} /> : <div className="pmo-empty"><UiText>No field updates in this period.</UiText></div>}</section><section className="pmo-card pmo-review-panel"><div className="pmo-panel-heading"><div><h2><UiText>Schedule matching / PM review</UiText></h2><p><UiText>Recommendations require PM confirmation.</UiText></p></div><button type="button" className="pmo-link" onClick={() => onNavigate("Planner Review")}><UiText>View all</UiText><ArrowRight size={13} /></button></div>{reviewRows.length ? <div className="pmo-review-list">{reviewRows.map((item) => <button type="button" key={item.id} onClick={() => { onSelectUpdate(item.id); onNavigate("Planner Review"); }}><span><strong>{item.rawText}</strong><small>{item.discipline} · {item.location}</small></span><b>{matches.find((match) => match.fieldUpdateId === item.id)?.confidence ?? 0}%</b></button>)}</div> : <div className="pmo-empty"><CheckCircle2 size={18} /><UiText>No updates require review in this period.</UiText></div>}</section></div>
    </>}
  </div>;
}

export default ProjectManagerOverview;
