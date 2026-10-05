import { useUiPreferences } from "./useUiPreferences.js";

// Returns a text node, preserving existing form, table and flex layouts.
export default function UiText({ children }) {
  const { t } = useUiPreferences();
  return t(children);
}
