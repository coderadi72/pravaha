import UiText from "../../ui/UiText.jsx";
export default function MatchingHealth({ data }) {
  const matches = data.activityMatches.filter((match) => match.matcherVersion);
  const values = [
    ["Field updates", data.fieldUpdates.length],
    ["Processed", matches.length],
    ["High confidence", matches.filter((match) => match.confidence >= 80).length],
    ["Needs review", data.fieldUpdates.filter((update) => ["needs_review", "action_required", "submitted"].includes(update.reviewStatus)).length],
    ["Confirmed matches", data.activityMatches.filter((match) => match.matchStatus === "matched").length],
    ["Unmatched", data.activityMatches.filter((match) => match.matchStatus === "unmatched").length],
    ["Missing actuals", data.fieldUpdates.filter((update) => !update.actualStart || (update.progress >= 100 && !update.actualEnd)).length],
    ["Average confidence", matches.length ? `${Math.round(matches.reduce((sum, match) => sum + match.confidence, 0) / matches.length)}%` : "—"],
  ];
  return <section className="pm-matching-health" aria-label="Matching health"><div><h2><UiText>Matching health</UiText></h2><p><UiText>Calculated from persisted updates in your assigned scope. Confidence is a match score, not measured accuracy.</UiText></p></div><dl>{values.map(([label, value]) => <div key={label}><dt><UiText>{label}</UiText></dt><dd>{value}</dd></div>)}</dl></section>;
}
