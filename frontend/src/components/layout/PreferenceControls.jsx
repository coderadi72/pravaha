import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Globe, Moon, Sun } from "lucide-react";
import { useUiPreferences } from "../../ui/useUiPreferences.js";

const languages = [
  { value: "en", label: "English" },
  { value: "hi", label: "हिन्दी" },
];

export default function PreferenceControls({ compact = false }) {
  const { theme, setTheme, language, setLanguage, t } = useUiPreferences();
  const [languageOpen, setLanguageOpen] = useState(false);
  const root = useRef(null);
  const trigger = useRef(null);

  useEffect(() => {
    if (!languageOpen) return undefined;
    const dismiss = (event) => {
      if (event.key === "Escape") { setLanguageOpen(false); trigger.current?.focus(); }
      else if (event.type === "pointerdown" && !root.current?.contains(event.target)) setLanguageOpen(false);
    };
    document.addEventListener("keydown", dismiss);
    document.addEventListener("pointerdown", dismiss);
    return () => { document.removeEventListener("keydown", dismiss); document.removeEventListener("pointerdown", dismiss); };
  }, [languageOpen]);

  const selected = languages.find((item) => item.value === language) ?? languages[0];
  return <div className={`pr-preference-controls${compact ? " is-compact" : ""}`}>
    <div className="pr-language-control" ref={root}>
      <button ref={trigger} type="button" className="pr-language-trigger" aria-label={t("Language")} aria-haspopup="menu" aria-expanded={languageOpen} onClick={() => setLanguageOpen((value) => !value)}>
        <Globe size={15} aria-hidden="true" /><span>{selected.label}</span><ChevronDown size={13} aria-hidden="true" />
      </button>
      {languageOpen && <div className="pr-language-menu" role="menu" aria-label={t("Language")}>
        {languages.map((item) => <button key={item.value} type="button" role="menuitemradio" aria-checked={selected.value === item.value} className={selected.value === item.value ? "is-selected" : ""} onClick={() => { setLanguage(item.value); setLanguageOpen(false); trigger.current?.focus(); }}>
          <span>{item.label}</span>{selected.value === item.value && <Check size={15} aria-hidden="true" />}
        </button>)}
      </div>}
    </div>
    <button type="button" className="pr-theme-toggle" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={t(`Switch to ${theme === "dark" ? "light" : "dark"} mode`)} title={t(`Switch to ${theme === "dark" ? "light" : "dark"} mode`)}>
      {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
      {!compact && <span>{t(theme === "dark" ? "Light" : "Dark")}</span>}
    </button>
  </div>;
}
