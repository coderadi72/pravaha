import UiText from "../../ui/UiText.jsx";
import { useEffect, useState } from "react";
import { intelligenceApi } from "../../api/client.js";
import MatchEvidencePanel from "./MatchEvidencePanel.jsx";
import "../../styles/execution-intelligence.css";

const display = (value) => value == null ? "N/A" : value;
const words = (value) => value.replace(/([a-z0-9])([A-Z])/g, "$1 $2").replaceAll("_", " ");

export default function ExecutionIntelligence({ projects, currentProjectId, onSelectProject, workflowData, title = "Execution intelligence" }) {
  const [result, setResult] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [portfolioOffset, setPortfolioOffset] = useState(0);
  const [history, setHistory] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  const [offset, setOffset] = useState(0);
  const [memoryOffset, setMemoryOffset] = useState(0);
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState("");
  const [activityId, setActivityId] = useState("");
  const [evidenceId, setEvidenceId] = useState(null);
  const projectId = projects.some((p) => p.id === currentProjectId) ? currentProjectId : projects[0]?.id;

  useEffect(() => {
    let cancelled = false;
    if (!projectId) return;
    async function load() {
      setBusy(true); setError("");
      try {
        const params = { limit: "50", offset: String(memoryOffset), q: query, ...(kind ? { kind } : {}), ...(activityId ? { activity_id: activityId } : {}) };
        const [intelligence, memory, overview] = await Promise.all([intelligenceApi.project(projectId, offset), intelligenceApi.memory(projectId, params), intelligenceApi.portfolio(portfolioOffset)]);
        if (!cancelled) { setResult(intelligence); setHistory(memory); setPortfolio(overview); }
      } catch (failure) { if (!cancelled) { setError(failure.message); setResult(null); setHistory(null); } }
      finally { if (!cancelled) setBusy(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [projectId, offset, memoryOffset, query, kind, activityId, revision, workflowData, portfolioOffset]);

  async function refresh() {
    setBusy(true); setError("");
    try { await intelligenceApi.refresh(projectId); setRevision((v) => v + 1); }
    catch (failure) { setError(failure.message); setBusy(false); }
  }
  async function acknowledge(id) {
    setBusy(true); setError("");
    try { await intelligenceApi.refresh(projectId); await intelligenceApi.acknowledge(projectId, id); setRevision((v) => v + 1); }
    catch (failure) { setError(failure.message); setBusy(false); }
  }
  const match = workflowData?.activityMatches.find((m) => m.fieldUpdateId === evidenceId);
  const activityOptions = workflowData?.scheduleActivities.filter((a) => a.projectId === projectId) ?? [];
  return <section className="execution-intelligence" aria-label="Execution intelligence">
    <header className="ei-heading"><div><h2><UiText>{title}</UiText></h2><p><UiText>Persisted evidence · PM-confirmed actuals · Calendar-day variance</UiText></p></div><label><UiText>Project</UiText><select aria-label="Intelligence project" value={projectId ?? ""} onChange={(e) => { onSelectProject(e.target.value); setOffset(0); setMemoryOffset(0); setActivityId(""); setEvidenceId(null); }}><option value="" disabled><UiText>Select project</UiText></option>{projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label><button type="button" disabled={!projectId || busy} onClick={refresh}><UiText>Refresh intelligence</UiText></button></header>
    {!projectId && <p><UiText>No permitted projects are assigned.</UiText></p>}
    {busy && <p role="status"><UiText>Loading execution evidence…</UiText></p>}
    {error && <p role="alert">{error}</p>}
    {result?.projectId === projectId && <>
      <small><UiText>Evaluated </UiText>{new Date(result.evaluatedAt).toLocaleString()} · {result.version}<UiText>. Read views calculate current signals; refresh records warning changes.</UiText></small>
      <div className="ei-metrics">{Object.entries(result.summary).map(([key, value]) => <article key={key}><span>{words(key)}</span><strong>{value}</strong></article>)}</div>
      <h3><UiText>Portfolio execution overview</UiText></h3>
      {portfolio && <><div className="ei-health">{portfolio.items.map((p) => <article key={p.id}><h4>{p.name}</h4><strong>{words(p.health.schedule.status)}</strong><p>{p.health.schedule.reason}</p><p>{p.summary.completedActivities}<UiText> complete · </UiText>{p.summary.pendingReviewActivities}<UiText> activities awaiting review · Linkage </UiText>{display(p.dataHealth.linkageCoverage)}{p.dataHealth.linkageCoverage == null ? "" : "%"}</p><button type="button" onClick={() => { onSelectProject(p.id); setOffset(0); setMemoryOffset(0); setActivityId(""); }}><UiText>Inspect project</UiText></button></article>)}</div><nav aria-label="Portfolio pages"><button type="button" disabled={portfolioOffset === 0 || busy} onClick={() => setPortfolioOffset(Math.max(0, portfolioOffset - 20))}><UiText>Previous projects</UiText></button><button type="button" disabled={portfolioOffset + 20 >= portfolio.total || busy} onClick={() => setPortfolioOffset(portfolioOffset + 20)}><UiText>Next projects</UiText></button></nav></>}
      <h3><UiText>Project health — contributing signals</UiText></h3><div className="ei-health">{Object.entries(result.health).map(([key, value]) => <article key={key}><h4>{words(key)}</h4><strong>{words(value.status)}</strong><p>{value.reason}</p></article>)}</div>
      {result.dependencyImpact && <><h3><UiText>Dependency impact</UiText></h3><p>{result.dependencyImpact.status} · {result.dependencyImpact.reason}</p>{result.dependencyImpact.items.slice(0, 50).map((i, n) => <details key={n}><summary>{i.status}<UiText> · depth </UiText>{i.depth} · {i.sourceActivityId} → {i.activityId}<UiText> · potential </UiText>{display(i.potentialExposureDays)}<UiText> days</UiText></summary><p>{i.reason}</p><pre>{JSON.stringify(i.evidence, null, 2)}</pre></details>)}{result.dependencyImpact.items.length > 50 && <p><UiText>Showing the first 50 impacts. Narrow project scope for detailed inspection.</UiText></p>}</>}
      <h3><UiText>Attention and early warnings</UiText></h3><p><UiText>Warnings describe evidence and potential exposure; they do not prove a cause.</UiText></p>
      {!result.warningTotal && <p><UiText>No current warning conditions were found.</UiText></p>}
      <div className="ei-warnings">{result.warnings.map((w) => <article className={`ei-warning is-${w.severity.toLowerCase()}`} key={w.id}><small>{w.severity} · {w.status} · {words(w.type)}</small><h4>{w.reason}</h4><p>{w.activityId ?? "Project update"} {w.fieldUpdateId ?? ""}</p><details><summary><UiText>Why this warning?</UiText></summary><pre>{JSON.stringify(w.evidence, null, 2)}</pre><p>{w.attention}</p><small><UiText>First generated </UiText>{new Date(w.generatedAt).toLocaleString()}</small></details>{w.fieldUpdateId && <button type="button" onClick={() => setEvidenceId(w.fieldUpdateId)}><UiText>Why not matched?</UiText></button>}{w.status === "OPEN" && <button type="button" disabled={busy} onClick={() => acknowledge(w.id)}><UiText>Acknowledge</UiText></button>}</article>)}</div>
      {match && <div><button type="button" onClick={() => setEvidenceId(null)}><UiText>Close match evidence</UiText></button><MatchEvidencePanel match={match} selectedActivityId={match.recommendedMatchId} /></div>}
      <h3><UiText>Schedule variance and confirmed execution</UiText></h3><p><UiText>Positive days indicate adverse variance. N/A means dates or confirmation are missing. Completion alone does not establish an actual finish date.</UiText></p>
      <div className="ei-table"><table><thead><tr><th><UiText>Activity</UiText></th><th><UiText>State / timing</UiText></th><th><UiText>Confirmed progress</UiText></th><th><UiText>Start variance</UiText></th><th><UiText>Finish variance</UiText></th><th><UiText>Duration variance</UiText></th><th><UiText>Potential downstream impact</UiText></th></tr></thead><tbody>{result.activities.map((a) => <tr key={a.activityId}><td><button type="button" onClick={() => { setActivityId(a.activityId); setMemoryOffset(0); }}>{a.name}</button><small>{a.activityId}</small></td><td>{words(a.status)} / {words(a.timing)}</td><td>{a.confirmedProgress == null ? "N/A" : `${a.confirmedProgress}%`}</td><td>{display(a.startVarianceDays)}<UiText> days</UiText></td><td>{display(a.finishVarianceDays)}<UiText> days</UiText></td><td>{display(a.durationVarianceDays)}<UiText> days</UiText></td><td>{a.potentialDownstream.length ? a.potentialDownstream.map((d) => <p key={d.activityId}>{d.activityId}: may be exposed to {d.potentialExposureDays}<UiText> days</UiText></p>) : result.dependencyRelationships ? "No exposure signal" : "Unavailable: no persisted dependencies"}</td></tr>)}</tbody></table></div>
      <nav aria-label="Intelligence pages"><button type="button" disabled={offset === 0 || busy} onClick={() => setOffset(Math.max(0, offset - 50))}><UiText>Previous activities / warnings</UiText></button><span>{offset + 1}–{offset + 50} · {result.activityTotal}<UiText> activities, </UiText>{result.warningTotal}<UiText> warnings</UiText></span><button type="button" disabled={offset + 50 >= Math.max(result.activityTotal, result.warningTotal) || busy} onClick={() => setOffset(offset + 50)}><UiText>Next activities / warnings</UiText></button></nav>
      <h3><UiText>Execution data health</UiText></h3><div className="ei-metrics">{Object.entries(result.dataHealth).filter(([key]) => !key.endsWith("Formula")).map(([key, value]) => <article key={key}><span>{words(key)}</span><strong>{display(value)}{key.endsWith("Coverage") && value != null ? "%" : ""}</strong></article>)}</div><p>{result.dataHealth.linkageFormula}</p><p>{result.dataHealth.dataFormula}<UiText>. Empty denominator = N/A.</UiText></p>
      <h3><UiText>Institutional memory / what changed?</UiText></h3><form className="ei-filters" onSubmit={(e) => { e.preventDefault(); setQuery(search); setMemoryOffset(0); }}><label><UiText>Search persisted records</UiText><input aria-label="Search execution memory" value={search} maxLength={200} onChange={(e) => setSearch(e.target.value)} /></label><label><UiText>Record type</UiText><select value={kind} onChange={(e) => { setKind(e.target.value); setMemoryOffset(0); }}><option value=""><UiText>All records</UiText></option>{["field_update", "review_history", "review", "confirmed_actual", "audit"].map((k) => <option key={k} value={k}>{words(k)}</option>)}</select></label><label><UiText>Activity timeline</UiText><select aria-label="Activity timeline" value={activityId} onChange={(e) => { setActivityId(e.target.value); setMemoryOffset(0); }}><option value=""><UiText>Project timeline</UiText></option>{activityOptions.map((a) => <option key={a.id} value={a.id}>{a.activityName}</option>)}</select></label><button type="submit" disabled={busy}><UiText>Search memory</UiText></button></form>
      {history && <><p>{history.total}<UiText> persisted records found. Provisional reports and PM confirmations remain distinct.</UiText></p><ol className="ei-timeline">{history.items.map((event) => <li key={event.id}><time>{event.occurredAt ? new Date(event.occurredAt).toLocaleString() : "Timestamp unavailable"}</time><strong>{event.action ?? words(event.kind)}</strong><small>{event.actor ?? "Actor unavailable"} · {words(event.kind)}</small><details><summary><UiText>Recorded details</UiText></summary><pre>{JSON.stringify(event.details, null, 2)}</pre></details></li>)}</ol><nav aria-label="Memory pages"><button type="button" disabled={memoryOffset === 0 || busy} onClick={() => setMemoryOffset(Math.max(0, memoryOffset - 50))}><UiText>Previous records</UiText></button><button type="button" disabled={memoryOffset + 50 >= history.total || busy} onClick={() => setMemoryOffset(memoryOffset + 50)}><UiText>Next records</UiText></button></nav></>}
    </>}
  </section>;
}
