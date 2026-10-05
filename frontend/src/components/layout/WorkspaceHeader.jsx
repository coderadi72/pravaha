import Brand from "./Brand.jsx";
import PreferenceControls from "./PreferenceControls.jsx";
import ProfileMenu from "./ProfileMenu.jsx";
import { useUiPreferences } from "../../ui/useUiPreferences.js";

export default function WorkspaceHeader({ name, role, onSignOut, onSettings }) {
  const { t } = useUiPreferences();
  return <header className="pr-navbar is-workspace"><div className="pr-navbar-row">
    <div className="pr-workspace-brand"><Brand compact /><span>{t(role)}</span></div>
    <div className="pr-navbar-actions"><PreferenceControls compact /><ProfileMenu name={name} role={role} onSettings={onSettings} onSignOut={onSignOut} /></div>
  </div></header>;
}
