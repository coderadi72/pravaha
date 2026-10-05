import { useContext } from "react";
import { PreferenceContext } from "./preferenceContext.js";

export function useUiPreferences() {
  const value = useContext(PreferenceContext);
  if (!value) throw new Error("useUiPreferences must be used within UiPreferencesProvider");
  return value;
}
