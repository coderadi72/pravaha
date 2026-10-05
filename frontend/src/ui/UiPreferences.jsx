import { useEffect, useMemo, useState } from "react";
import { PreferenceContext } from "./preferenceContext.js";
import { resolveLocale, translate } from "./translations.js";

const THEME_KEY = "pravaha.ui.theme.v1";
const LANGUAGE_KEY = "pravaha.ui.language.v1";
const languages = new Set(["en", "hi"]);

function readPreference(key, fallback, allowed) {
  try {
    const value = window.localStorage.getItem(key);
    return allowed.has(value) ? value : fallback;
  } catch {
    return fallback;
  }
}

export function UiPreferencesProvider({ children }) {
  const [theme, setTheme] = useState(() => readPreference(THEME_KEY, "light", new Set(["light", "dark"])));
  const [language, setLanguage] = useState(() => readPreference(LANGUAGE_KEY, "en", languages));
  const locale = resolveLocale(language, navigator.language);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.documentElement.dataset.language = language;
    document.documentElement.lang = locale;
    try {
      window.localStorage.setItem(THEME_KEY, theme);
      window.localStorage.setItem(LANGUAGE_KEY, language);
    } catch {
      // The preferences remain usable for this session when storage is unavailable.
    }
  }, [theme, language, locale]);

  const value = useMemo(() => ({ theme, setTheme, language, setLanguage, locale, t: (text) => translate(text, locale) }), [theme, language, locale]);
  return <PreferenceContext.Provider value={value}>{children}</PreferenceContext.Provider>;
}
