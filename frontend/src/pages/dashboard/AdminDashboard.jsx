import UiText from "../../ui/UiText.jsx";
import { useUiPreferences } from "../../ui/useUiPreferences.js";
import { useSearchParams } from "react-router-dom";
import OrganizationPanel from "../../components/organization/OrganizationPanel.jsx";
import ProjectTeamForms from "../../components/organization/ProjectTeamForms.jsx";
import AssignmentControls, { CapabilityControls } from "../../components/organization/AssignmentControls.jsx";
import ScheduleIngestion from "../../components/workflow/ScheduleIngestion.jsx";
import SystemHealth from "../../components/workflow/SystemHealth.jsx";
import RecordSearch from "../../components/workflow/RecordSearch.jsx";
import { useState } from "react";
import {
  Activity, BarChart3, Building2, CheckCircle2,
  ChevronRight, FolderKanban, LayoutDashboard, LogOut,
  MapPin, Network, Settings, ShieldCheck, Users, UserRound,
} from "lucide-react";
import "../../styles/admin-dashboard.css";
import ExecutionIntelligence from "../../components/workflow/ExecutionIntelligence.jsx";
import { formatCurrentDate } from "../../utils/date.js";
import WorkspaceHeader from "../../components/layout/WorkspaceHeader.jsx";
import Footer from "../../components/layout/Footer.jsx";
import RegistrationRequests from "../../components/auth/RegistrationRequests.jsx";
import OrganizationAnalytics from "../../components/organization/OrganizationAnalytics.jsx";

const NAV = [
  { group: "PRIMARY", items: [["Dashboard", LayoutDashboard], ["Projects", FolderKanban], ["Project Managers", UserRound], ["Teams", Users], ["Organization Activity", Activity]] },
  { group: "MANAGEMENT", items: [["Registrations", ShieldCheck], ["Workers", Users], ["Assignments", Network], ["Departments", Building2], ["Business", Building2], ["Materials", Building2], ["People", Users], ["Quality", ShieldCheck], ["HSE", ShieldCheck], ["Data & Imports", FolderKanban], ["Reports", BarChart3], ["Audit", Activity]] },
  { group: "SYSTEM", items: [["Settings", Settings]] },
];

function Status({ value }) {
  const key = value?.toLowerCase().replaceAll(" ", "-") ?? "active";
  return <span className={`ad-status is-${key}`}>{value}</span>;
}

function ProjectRow({ project, data, onOpen }) {
  const manager = data.projectManagers.find((item) => item.id === project.projectManagerId);
  const teamCount = (project.teamIds ?? []).length;
  return <tr>
    <td><button className="ad-row-link" type="button" onClick={() => onOpen(project.id)}><strong>{project.name}</strong><small>{project.id} · {project.location}</small></button></td>
    <td><Status value={project.status} /></td><td><UiText>Open intelligence for confirmed activity actuals</UiText></td>
    <td>{manager?.name ?? "Unassigned"}</td><td>{teamCount}</td><td><button className="ad-open-button" type="button" aria-label={`Open ${project.name}`} onClick={() => onOpen(project.id)}><ChevronRight size={16} /></button></td>
  </tr>;
}

function ProjectDetails({ data, project, onBack }) {
  const manager = data.projectManagers.find((item) => item.id === project.projectManagerId);
  const teams = data.teams.filter((team) => (project.teamIds ?? []).includes(team.id));
  return <>
    <button className="ad-back" type="button" onClick={onBack}><UiText>‹ All projects</UiText></button>
    <section className="ad-project-hero"><div><span className="ad-eyebrow">{project.id}<UiText> · PROJECT DETAIL</UiText></span><h2>{project.name}</h2><p><MapPin size={14} /> {project.location} <Status value={project.status} /></p></div><span><UiText>Overall weighted progress unavailable</UiText></span></section>
    <div className="ad-detail-grid">
      <section className="ad-panel"><PanelHeading kicker="OWNERSHIP" title="Project organization" /><div className="ad-owner-row"><span className="ad-person-mark"><UserRound size={16} /></span><div><small><UiText>PROJECT MANAGER</UiText></small><strong>{manager?.name ?? "Unassigned"}</strong><span>{manager?.id ?? "No manager assigned"}</span></div></div><div className="ad-panel-subhead"><UiText>Assigned teams </UiText><span>{teams.length}<UiText> teams · </UiText>{teams.filter((team) => team.teamLeaderId).length}<UiText> Team Leaders</UiText></span></div>{teams.length ? teams.map((team) => <div className="ad-team-row" key={team.id}><div><strong>{team.name}</strong><small>{team.id} · {team.site}</small></div><span>{data.teamLeaders.find((leader) => leader.id === team.teamLeaderId)?.name ?? "Team Leader unassigned"}</span></div>) : <p className="ad-empty"><UiText>No teams assigned.</UiText></p>}</section>
      <ExecutionIntelligence projects={[project]} currentProjectId={project.id} onSelectProject={() => {}} workflowData={data} />
    </div>
  </>;
}

function PanelHeading({ kicker, title, action }) {
  return <div className="ad-panel-heading"><div><span className="ad-eyebrow">{kicker}</span><h3><UiText>{title}</UiText></h3></div>{action}</div>;
}

function UserProvisionForm({ onCreate }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("PROJECT_MANAGER");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const submit = async (event) => {
    event.preventDefault(); setBusy(true); setMessage("");
    try { const result = await onCreate({ name, email, role, password }); setMessage(`${result.user.name} account created.`); setName(""); setEmail(""); setPassword(""); }
    catch (error) { setMessage(error.message ?? "Account could not be created."); }
    finally { setBusy(false); }
  };
  return <form className="ad-user-provision" onSubmit={submit}>
    <div><label><UiText>Name</UiText><input value={name} onChange={(event) => setName(event.target.value)} maxLength={120} required /></label><label><UiText>Work email</UiText><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} maxLength={254} required /></label><label><UiText>Role</UiText><select value={role} onChange={(event) => setRole(event.target.value)}><option value="PROJECT_MANAGER"><UiText>Project Manager</UiText></option><option value="TEAM_LEADER"><UiText>Team Leader / Supervisor</UiText></option><option value="DEPARTMENT"><UiText>Department account</UiText></option></select></label><label><UiText>Initial password</UiText><input type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={12} maxLength={128} required /></label><button type="submit" disabled={busy}><UiText>{busy ? "Creating…" : "Create account"}</UiText></button></div>
    <small><UiText>At least 12 characters with uppercase, lowercase, number and special character. Assign the account to a project or team after creating it.</UiText></small>
    {message && <p role="status">{message}</p>}
  </form>;
}

function AdminDashboard({ onReload, workflowData, user, onCreateUser, onSignOut }) {
  const { t } = useUiPreferences();
  const [params, setParams] = useSearchParams();
  const requestedView = params.get("view") || "Dashboard";
  const activeView = NAV.some((group) => group.items.some(([label]) => label === requestedView)) ? requestedView : "Dashboard";
  const setActiveView = (view) => setParams({ view });
  const [intelligenceProjectId, setIntelligenceProjectId] = useState(null);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [notice, setNotice] = useState("");
  const data = workflowData;
  const selectedProject = data.projects.find((project) => project.id === selectedProjectId);

  const openProject = (projectId) => { setSelectedProjectId(projectId); setActiveView("Projects"); };

  const renderProjects = () => selectedProject ? <ProjectDetails data={data} project={selectedProject} onBack={() => setSelectedProjectId(null)} /> : <section className="ad-panel"><PanelHeading kicker="PORTFOLIO" title="Projects" action={<span className="ad-count">{data.projects.length}<UiText> sample projects</UiText></span>} /><ProjectTeamForms kind="project" onReload={onReload} /><div className="ad-table-wrap"><table className="ad-table"><thead><tr><th><UiText>Project</UiText></th><th><UiText>Recorded project status</UiText></th><th><UiText>Actual progress</UiText></th><th><UiText>Project Manager</UiText></th><th><UiText>Teams</UiText></th><th aria-label="Open project" /></tr></thead><tbody>{data.projects.map((project) => <ProjectRow key={project.id} project={project} data={data} onOpen={openProject} />)}</tbody></table></div></section>;

  const renderManagers = () => <section className="ad-panel"><PanelHeading kicker="ORGANIZATION" title="Project Managers and accounts" action={<span className="ad-count">{data.projectManagers.length}<UiText> PM profiles</UiText></span>} /><UserProvisionForm onCreate={onCreateUser} /><div className="ad-table-wrap"><table className="ad-table"><thead><tr><th><UiText>Manager</UiText></th><th><UiText>Assigned projects</UiText></th><th><UiText>Active teams</UiText></th><th><UiText>Status</UiText></th><th><UiText>Last activity</UiText></th></tr></thead><tbody>{data.projectManagers.map((manager) => { const projects = data.projects.filter((project) => manager.assignedProjectIds.includes(project.id)); const teamCount = projects.reduce((total, project) => total + (project.teamIds ?? []).length, 0); return <tr key={manager.id}><td><span className="ad-name-cell"><span className="ad-person-mark"><UserRound size={15} /></span><span><strong>{manager.name}</strong><small>{manager.id}</small></span></span></td><td><UiText>{projects.length ? projects.map((project) => <button key={project.id} className="ad-inline-link" type="button" onClick={() => openProject(project.id)}>{project.name}</button>) : "Unassigned"}</UiText></td><td>{teamCount}</td><td><Status value={manager.status} /></td><td>{manager.lastActivity}</td></tr>; })}</tbody></table></div></section>;

  const renderTeams = () => <section className="ad-panel"><PanelHeading kicker="FIELD ORGANIZATION" title="Teams and supervisors" action={<span className="ad-count">{data.teams.length}<UiText> demo teams</UiText></span>} /><ProjectTeamForms kind="team" onReload={onReload} /><div className="ad-table-wrap"><table className="ad-table"><thead><tr><th><UiText>Team</UiText></th><th><UiText>Project / site</UiText></th><th><UiText>Team Leader / Supervisor</UiText></th><th><UiText>Members</UiText></th><th><UiText>Status</UiText></th></tr></thead><tbody>{data.teams.map((team) => { const project = data.projects.find((item) => item.id === team.projectId); const leader = data.teamLeaders.find((item) => item.id === team.teamLeaderId); return <tr key={team.id}><td><strong>{team.name}</strong><small className="ad-cell-sub">{team.id}</small></td><td><strong>{project?.name ?? "Unassigned"}</strong><small className="ad-cell-sub">{team.site}</small></td><td>{leader?.name ?? "Unassigned"}<small className="ad-cell-sub">{leader?.id ?? "No supervisor"}</small></td><td><strong>{team.active}</strong> / {team.members}<small className="ad-cell-sub">{team.onLeave}<UiText> on leave</UiText></small></td><td><Status value={team.status} /></td></tr>; })}</tbody></table></div></section>;


  const renderActivity = () => <section className="ad-panel"><PanelHeading kicker="ORGANIZATION RECORD" title="Organization activity" action={<span className="ad-count"><UiText>Persistent audit events</UiText></span>} /><div className="ad-activity-list">{(data.organizationActivity ?? []).slice(0, 100).map((item) => <div className="ad-activity-row" key={item.id}><span className={`ad-activity-icon is-${item.type}`}><Activity size={15} /></span><div><strong>{item.action}</strong><small>{item.actor}</small></div><time>{new Date(item.occurredAt).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</time></div>)}</div>{!data.organizationActivity?.length && <p className="ad-empty"><UiText>No organization activity has been recorded.</UiText></p>}</section>;

  const renderExecutionReport = () => <ExecutionIntelligence projects={data.projects} currentProjectId={intelligenceProjectId} onSelectProject={setIntelligenceProjectId} workflowData={data} title="Organization execution intelligence" />;
  const renderOverview = () => <><OrganizationAnalytics workflowData={data} onNavigate={setActiveView} onOpenProject={openProject} onOpenReport={(id) => { setIntelligenceProjectId(id); setActiveView("Reports"); }} />{renderActivity()}</>;
  const renderReports = renderExecutionReport;

  const organizationViews = ["Workers", "Departments", "Business", "Materials", "People", "Quality", "HSE"];
  const content = organizationViews.includes(activeView) ? <OrganizationPanel key={activeView} view={activeView} /> : activeView === "Data & Imports" ? <section className="org-panel"><h2><UiText>Schedule data and imports</UiText></h2><label><UiText>Project</UiText><select value={selectedProjectId || ""} onChange={(e) => setSelectedProjectId(e.target.value)}><option value=""><UiText>Choose a project</UiText></option>{data.projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label><ScheduleIngestion key={selectedProjectId} projectId={selectedProjectId} onReload={onReload} /></section> : activeView === "Audit" ? renderActivity() : activeView === "Dashboard" ? renderOverview()
    : activeView === "Projects" ? renderProjects()
      : activeView === "Project Managers" ? renderManagers()
        : activeView === "Teams" ? renderTeams()
          : activeView === "Organization Activity" ? renderActivity()
            : activeView === "Assignments" ? <AssignmentControls onReload={onReload} />
              : activeView === "Registrations" ? <RegistrationRequests organization={data.organization} onReload={onReload} />
              : activeView === "Reports" ? renderReports()
              : <section className="ad-panel"><PanelHeading kicker="SYSTEM" title="Settings" /><p className="ad-muted-note"><UiText>Organization configuration is managed by the backend environment.</UiText></p><div className="ad-setting-row"><span><UiText>Organization</UiText></span><strong>{data.organization.name}</strong></div><div className="ad-setting-row"><span><UiText>Data source</UiText></span><strong>PostgreSQL-backed workflow data</strong></div><div className="ad-setting-row"><span><UiText>Access model</UiText></span><strong>Server-authenticated roles</strong></div></section>;

  return <div className="admin-dashboard">
    <WorkspaceHeader name={user.name} role="Administrator" onSettings={() => setActiveView("Settings")} onSignOut={onSignOut} />
    <aside className="ad-sidebar"><div className="ad-org-switch"><span className="ad-org-mark"><Building2 size={16} /></span><div><small><UiText>WORKSPACE</UiText></small><strong>{data.organization.name}</strong></div><ChevronRight size={14} /></div><nav aria-label="Administrator navigation">{NAV.map((group) => <div className="ad-nav-group" key={group.group}><small>{group.group}</small>{group.items.map(([label, Icon]) => <button className={activeView === label ? "is-active" : ""} key={label} type="button" aria-label={t(label)} title={t(label)} onClick={() => { setActiveView(label); setSelectedProjectId(null); }}><Icon size={17} /><span><UiText>{label}</UiText></span></button>)}</div>)}</nav><div className="ad-sidebar-footer"><div className="ad-admin-profile"><span>{user.name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase()}</span><div><strong>{user.name}</strong><small><UiText>Authenticated administrator</UiText></small></div><ShieldCheck size={15} /></div><button type="button" aria-label="Sign out" title="Sign out" onClick={onSignOut}><LogOut size={15} /><UiText> Sign out</UiText></button></div></aside>
    <div className="pr-workspace-context"><span>{data.organization.name}</span><span><UiText>Demo organization data</UiText></span></div>
    <main className="ad-main"><div className="ad-main-inner"><div className="ad-page-heading"><div><span className="ad-eyebrow">{formatCurrentDate().toUpperCase()}<UiText> · ORGANIZATION VIEW</UiText></span><h1><UiText>{selectedProject ? "Project detail" : activeView === "Dashboard" ? "Organization overview" : activeView}</UiText></h1><p>{selectedProject ? `${selectedProject.id} · Ownership, teams and execution status` : activeView === "Dashboard" ? "Portfolio execution, project health, and field activity across the organization." : `Organization-level visibility and assignment management · ${data.organization?.dataLabel ?? "Prototype data"}.`}</p></div><span className="ad-readonly-tag"><ShieldCheck size={14} /><UiText> Organization access</UiText></span></div>{notice && <div className="ad-notice" role="status"><CheckCircle2 size={16} />{notice}<button type="button" aria-label="Dismiss message" onClick={() => setNotice("")}>×</button></div>}<RecordSearch />{content}{activeView === "Settings" && <><CapabilityControls /><SystemHealth onReload={onReload} /></>}<Footer compact /></div></main>
  </div>;
}

export default AdminDashboard;
