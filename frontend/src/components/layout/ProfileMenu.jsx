import { ChevronDown, LogOut, Settings } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useUiPreferences } from "../../ui/useUiPreferences.js";

export default function ProfileMenu({ name, role, onSignOut, onSettings }) {
  const { t } = useUiPreferences();
  const [open, setOpen] = useState(false);
  const root = useRef(null);
  const trigger = useRef(null);
  useEffect(() => {
    if (!open) return undefined;
    const dismiss = (event) => { if (!root.current?.contains(event.target)) setOpen(false); };
    const onKey = (event) => {
      if (event.key === "Escape") { setOpen(false); trigger.current?.focus(); }
      if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key) && root.current?.contains(event.target)) {
        event.preventDefault();
        const items = [...root.current.querySelectorAll('[role="menuitem"]')];
        const current = items.indexOf(document.activeElement);
        const next = event.key === "Home" ? 0 : event.key === "End" ? items.length - 1 : (current + (event.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items[next]?.focus();
      }
    };
    root.current?.querySelector('[role="menuitem"]')?.focus();
    document.addEventListener("pointerdown", dismiss);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("pointerdown", dismiss); document.removeEventListener("keydown", onKey); };
  }, [open]);
  const initials = (name || "P").split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
  return <div className="pr-profile-menu" ref={root}>
    <button ref={trigger} type="button" className="pr-profile-trigger" aria-haspopup="menu" aria-expanded={open} aria-label={`${t("Profile menu")} · ${name}`} onClick={() => setOpen((value) => !value)} onKeyDown={(event) => { if (event.key === "ArrowDown") { event.preventDefault(); setOpen(true); } }}><span>{initials}</span><ChevronDown size={13} /></button>
    {open && <div className="pr-profile-popover" role="menu">
      <div className="pr-profile-identity"><strong>{name}</strong><span>{t(role)}</span></div>
      {onSettings && <button type="button" role="menuitem" onClick={() => { setOpen(false); onSettings(); trigger.current?.focus(); }}><Settings size={15} />{t("Settings")}</button>}
      <button type="button" role="menuitem" className="is-sign-out" onClick={() => { setOpen(false); onSignOut(); }}><LogOut size={15} />{t("Sign out")}</button>
    </div>}
  </div>;
}
