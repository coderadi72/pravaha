import UiText from "../../ui/UiText.jsx";
export default function MatchEvidencePanel({ match, selectedActivityId, onSelectCandidate }) {
  if (!match.matcherVersion) return <section className="pm-intelligence-evidence"><h3><UiText>Match evidence</UiText></h3><p><UiText>This historical recommendation predates stored evidence.</UiText></p></section>;
  const candidates = match.candidates ?? [];
  const candidate = candidates.find((item) => item.scheduleActivityId === selectedActivityId) ?? candidates[0];
  const evidence = candidate?.evidence ?? match.evidence ?? [];
  return <section className="pm-intelligence-evidence" aria-label="Match evidence">
    <div className="pm-evidence-heading"><h3><UiText>PRAVAHA recommendation</UiText></h3><span>{match.recommendationStatus === "ambiguous" ? "Multiple plausible activities" : match.recommendedMatchId ? "Suggested match" : "No confident recommendation"}</span></div>
    <p className="pm-evidence-version">{match.matcherVersion}<UiText> · Generated </UiText>{new Date(match.generatedAt).toLocaleString("en-IN")}</p>
    <p><UiText>Confidence describes available match evidence. PM confirmation is required.</UiText></p>
    <h4><UiText>Candidate activities</UiText></h4>
    {candidates.length ? <ol className="pm-candidate-list">{candidates.map((item) => <li key={item.scheduleActivityId}>
      <button type="button" disabled={!onSelectCandidate} aria-pressed={selectedActivityId === item.scheduleActivityId} aria-label={`Select ${item.activityName} · ${item.activityId}`} onClick={() => onSelectCandidate?.(item.scheduleActivityId)}>
        <span><strong>{item.activityName}</strong><small>{item.level} · {item.activityId} · {item.discipline}{item.location ? ` · ${item.location}` : ""}</small></span>
        <span className={`pm-candidate-score is-${item.confidenceLevel}`}>{item.score}%<small>{item.confidenceLevel}</small></span>
      </button>
    </li>)}</ol> : <p><UiText>No relevant candidates were found in this project's L5/L6 schedule.</UiText></p>}
    <h4><UiText>Why did PRAVAHA suggest this?</UiText></h4>
    {candidate && <p className="pm-evidence-target"><UiText>Evidence for </UiText>{candidate.activityName} · {candidate.score}%</p>}
    <ul className="pm-evidence-list">{evidence.map((item, index) => <li className={`is-${item.outcome}`} key={`${item.signal}-${index}`}><span aria-hidden="true">{item.outcome === "support" ? "✓" : item.outcome === "conflict" ? "!" : "·"}</span><span>{item.text}</span></li>)}</ul>
    {!evidence.length && <p>{match.matchReason}</p>}
    <h4><UiText>Why not automatically matched?</UiText></h4><p>{match.unmatchReason}</p>
  </section>;
}
