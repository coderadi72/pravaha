import { ExternalLink } from "lucide-react";
import Brand from "./Brand.jsx";
import { useUiPreferences } from "../../ui/useUiPreferences.js";

const socialLinks = [
  ["GitHub", import.meta.env.VITE_GITHUB_URL],
  ["LinkedIn", import.meta.env.VITE_LINKEDIN_URL],
  ["X", import.meta.env.VITE_X_URL],
  ["YouTube", import.meta.env.VITE_YOUTUBE_URL],
];
const socialMarks = {
  GitHub: <path d="M12 .9a11.1 11.1 0 0 0-3.5 21.6c.55.1.75-.24.75-.53v-2.08c-3.08.67-3.73-1.31-3.73-1.31-.5-1.28-1.23-1.62-1.23-1.62-1.01-.69.08-.68.08-.68 1.12.08 1.71 1.15 1.71 1.15 1 .1.79 1.97 3.34 1.41.1-.72.39-1.21.7-1.49-2.46-.28-5.05-1.23-5.05-5.47 0-1.21.43-2.2 1.14-2.98-.11-.28-.49-1.42.11-2.96 0 0 .93-.3 3.05 1.14a10.6 10.6 0 0 1 5.55 0c2.12-1.44 3.04-1.14 3.04-1.14.61 1.54.23 2.68.12 2.96.71.78 1.13 1.77 1.13 2.98 0 4.25-2.59 5.18-5.06 5.46.4.35.75 1.02.75 2.06v3.04c0 .29.2.63.76.52A11.1 11.1 0 0 0 12 .9Z" />,
  LinkedIn: <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14ZM8.3 10H5.7v8h2.6v-8Zm-.1-2.6a1.5 1.5 0 1 0-3 0 1.5 1.5 0 0 0 3 0ZM18.3 13.4c0-2.4-1.3-3.5-3.1-3.5-1.4 0-2 .8-2.4 1.3V10h-2.6v8h2.6v-4.2c0-1.1.2-2.2 1.6-2.2s1.4 1.3 1.4 2.3V18h2.5v-4.6Z" />,
  X: <path d="M18.9 2H22l-6.8 7.8L23.2 22h-6.3L12 14.9 5.8 22H2.6l7.3-8.4L2 2h6.5l4.4 6.5L18.9 2Zm-1.1 18h1.7L7.4 3.9H5.6L17.8 20Z" />,
  YouTube: <><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.6 3.6 12 3.6 12 3.6s-7.6 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.8.5 9.4.5 9.4.5s7.6 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8Z"/><path fill="var(--surface)" d="m9.6 15.8 6.3-3.8-6.3-3.8v7.6Z"/></>,
};
const safePublicUrl = (value) => {
  try { const url = new URL(value); return url.protocol === "https:" && !url.username && !url.password ? url.href : null; }
  catch { return null; }
};

export default function Footer({ onOpenAuth, compact = false }) {
  const { t } = useUiPreferences();
  return <footer id={compact ? undefined : "contact"} className={`pr-footer${compact ? " is-compact" : ""}`}>
    {!compact && <div className="pr-footer-grid">
      <div className="pr-footer-intro"><Brand /><p>{t("Project intelligence for infrastructure execution.")}</p><small>SIH26122 · Oil India Limited</small></div>
      <nav aria-label={t("Platform")}><strong>{t("Platform")}</strong>{[["Features", "#features"], ["Use Cases", "#how-it-works"], ["About", "#about"], ["Knowledge Base", "#knowledge"]].map(([label, href]) => <a key={href} href={href}>{t(label)}</a>)}</nav>
      <div><strong>{t("Help & Support")}</strong><p>{t("Accounts are provisioned by your organization administrator.")}</p>{onOpenAuth && <><button type="button" onClick={() => onOpenAuth("field")}>{t("Team Leader / Supervisor")}</button><button type="button" onClick={() => onOpenAuth("management")}>{t("Management")}</button></>}</div>
      <div><strong>{t("Resources")}</strong><span title={t("Not published yet")}>{t("Privacy")} <small>— {t("Not published yet")}</small></span><span title={t("Not published yet")}>{t("Terms")} <small>— {t("Not published yet")}</small></span></div>
    </div>}
    <div className="pr-footer-bottom"><span>© 2026 PRAVAHA</span><small>{t("SIH 2026 prototype · Synthetic demonstration data")}</small><nav aria-label={t("Connect")}>{socialLinks.map(([label, value]) => {
      const url = safePublicUrl(value);
      return url ? <a key={label} href={url} target="_blank" rel="noopener noreferrer"><svg className="pr-social-mark" viewBox="0 0 24 24" aria-hidden="true">{socialMarks[label]}</svg><span>{label}</span><ExternalLink size={12} aria-hidden="true" /></a> : !compact && <span key={label} className="pr-link-unavailable"><svg className="pr-social-mark" viewBox="0 0 24 24" aria-hidden="true">{socialMarks[label]}</svg><span>{label}</span><small> · {t("Not configured")}</small></span>;
    })}</nav></div>
  </footer>;
}
