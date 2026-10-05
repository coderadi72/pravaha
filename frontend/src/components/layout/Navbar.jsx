import { useEffect, useRef, useState } from "react";
import { Menu, X } from "lucide-react";
import Brand from "./Brand.jsx";
import PreferenceControls from "./PreferenceControls.jsx";
import { useUiPreferences } from "../../ui/useUiPreferences.js";

const links = [["Home", "#home"], ["About", "#about"], ["Features", "#features"], ["Use Cases", "#how-it-works"], ["Contact", "#contact"]];

export default function Navbar({ onOpenAuth, onOpenSignup }) {
  const { t } = useUiPreferences();
  const [open, setOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const trigger = useRef(null);
  const root = useRef(null);
  useEffect(() => {
    if (!open) return;
    const dismiss = (event) => {
      if (event.key === "Escape") { setOpen(false); trigger.current?.focus(); }
      else if (event.type === "pointerdown" && !root.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener("keydown", dismiss);
    document.addEventListener("pointerdown", dismiss);
    return () => { document.removeEventListener("keydown", dismiss); document.removeEventListener("pointerdown", dismiss); };
  }, [open]);

  useEffect(() => {
    const update = () => setIsScrolled(window.scrollY > 14);
    update();
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);

  return <header className={`pr-navbar${isScrolled ? " is-scrolled" : ""}`} ref={root}>
    <div className="pr-navbar-row">
      <a href="#home" className="pr-brand-link" aria-label="PRAVAHA"><Brand /></a>
      <nav id="pr-public-navigation" className={`pr-public-navigation${open ? " is-open" : ""}`} aria-label={t("Main navigation")}>
        {links.map(([label, href]) => <a key={href} href={href} onClick={() => setOpen(false)}>{t(label)}</a>)}
        <div className="pr-mobile-auth"><button type="button" className="pr-button" onClick={() => { setOpen(false); onOpenAuth("management"); }}>{t("Sign in")}</button><button type="button" className="pr-button is-primary" onClick={() => { setOpen(false); onOpenSignup(); }}>{t("Sign up")}</button></div>
      </nav>
      <div className="pr-navbar-actions">
        <PreferenceControls compact />
        <div className="pr-desktop-auth"><button type="button" className="pr-button" onClick={() => onOpenAuth("management")}>{t("Sign in")}</button><button type="button" className="pr-button is-primary" onClick={onOpenSignup}>{t("Sign up")}</button></div>
        <button ref={trigger} type="button" className="pr-icon-button pr-menu-toggle" aria-label={t(open ? "Close navigation" : "Open navigation")} aria-expanded={open} aria-controls="pr-public-navigation" onClick={() => setOpen(!open)}>{open ? <X size={19} /> : <Menu size={19} />}</button>
      </div>
    </div>
  </header>;
}
