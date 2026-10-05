// Keep the supplied artwork intact. Replace this source when official variants arrive.
export default function Brand({ compact = false }) {
  return <img className={`pr-brand-image${compact ? " is-compact" : ""}`} src="/pravaha-logo-vector.svg" alt="PRAVAHA" width="720" height="220" />;
}
