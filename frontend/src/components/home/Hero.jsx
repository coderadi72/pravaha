import UiText from "../../ui/UiText.jsx";
import { ArrowRight, BarChart3, Database, FileText, Link2, Play, RefreshCw } from "lucide-react";
import DashboardPreview from "./DashboardPreview";

const featureTags = [
  [FileText, "Field Update Capture"],
  [Link2, "Rule-Based Activity Matching"],
  [RefreshCw, "Persistent Schedule Updates"],
  [Database, "Institutional Knowledge"],
];

export default function Hero({ onDemoStart }) {
  return <section id="home" className="pr-hero">
    <div className="pr-hero-background" aria-hidden="true" style={{ backgroundImage: "url('/pravaha-hero-refinery.png')" }} />
    <div className="pr-hero-overlay" aria-hidden="true" />
    <div className="pr-hero-bottom-fade" aria-hidden="true" />
    <div className="pr-hero-content">
      <div className="pr-hero-badge">
        <BarChart3 size={15} aria-hidden="true" />
        <strong>SIH26122</strong>
        <span aria-hidden="true">·</span>
        <span>Oil India Limited</span>
      </div>
      <h1 className="pr-hero-title">
        <UiText>From Field Updates</UiText>
        <br />
        <UiText>to</UiText>{" "}<span className="pr-hero-title-accent"><UiText>Smarter Schedules</UiText></span>
      </h1>
      <p className="pr-hero-description"><UiText>Field data capture and deterministic schedule linking for real-time infrastructure project progress tracking.</UiText></p>
      <div className="pr-hero-actions">
        <button type="button" onClick={() => onDemoStart?.()} className="pr-hero-primary">
          <UiText>Try Prototype</UiText><ArrowRight size={16} aria-hidden="true" />
        </button>
        <button type="button" onClick={() => document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" })} className="pr-hero-secondary">
          <Play size={13} fill="currentColor" aria-hidden="true" /><UiText>Watch Demo</UiText>
        </button>
      </div>
      <ul className="pr-hero-tags" aria-label="PRAVAHA capabilities">
        {featureTags.map(([Icon, label]) => <li key={label}><Icon size={14} aria-hidden="true" /><UiText>{label}</UiText></li>)}
      </ul>
      <div className="pr-hero-preview">
        <p className="pr-hero-preview-note"><UiText>A prototype view of field updates and schedule links. The figures shown here are illustrative demo values.</UiText></p>
        <DashboardPreview />
      </div>
      <ol className="pr-hero-flow" aria-label="Project execution flow">
        {["Field execution", "Data capture", "Activity extraction", "L5/L6 schedule matching", "Actual progress", "Project intelligence"].map((step, index) => <li key={step}><UiText>{step}</UiText>{index < 5 && <ArrowRight size={13} aria-hidden="true" />}</li>)}
      </ol>
    </div>
  </section>;
}
