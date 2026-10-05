import UiText from "./ui/UiText.jsx";
import "./styles/global.css";
import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import OrganizationPanel from "./components/organization/OrganizationPanel.jsx";
import HomePage from "./pages/HomePage.jsx";
import ProjectManagerDashboard from "./pages/dashboard/ProjectManagerDashboard.jsx";
import TeamLeaderDashboard from "./pages/dashboard/TeamLeaderDashboard.jsx";
import AdminDashboard from "./pages/dashboard/AdminDashboard.jsx";
import { ApiError, authApi, workflowApi } from "./api/client.js";
import PreferenceControls from "./components/layout/PreferenceControls.jsx";
import ProfileMenu from "./components/layout/ProfileMenu.jsx";
const AssistantWidget = lazy(() => import("./components/assistant/AssistantWidget.jsx"));

function AccessState({ title, message, onRetry, onSignOut }) {
  return <main className="pr-role-screen"><section role="alert"><div className="pr-role-brand"><span>P</span><div><strong>PRAVAHA</strong><small>FIELD EXECUTION &amp; PROJECT CONTROL</small></div></div><h1><UiText>{title}</UiText></h1><p className="pr-role-copy">{message}</p>{onRetry && <button type="button" onClick={onRetry}><UiText>Retry</UiText></button>}{onSignOut && <button type="button" className="pr-role-home" onClick={onSignOut}><UiText>Sign out</UiText></button>}</section></main>;
}

function App() {
  const [user, setUser] = useState(null);
  const [workflowData, setWorkflowData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshWorkspace = useCallback(async () => {
    const result = await workflowApi.workspace();
    setWorkflowData(result.data);
    setUser(result.user);
    setError(null);
    return result;
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const result = await authApi.me();
        if (!active) return;
        setUser(result.user);
        if (["WORKFORCE", "DEPARTMENT"].includes(result.user.role)) return;
        const workspace = await workflowApi.workspace();
        if (active) setWorkflowData(workspace.data);
      } catch (requestError) {
        if (active && !(requestError instanceof ApiError && requestError.status === 401)) setError(requestError);
      } finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, []);

  const handleAuthenticated = async (authenticatedUser) => {
    setUser(authenticatedUser);
    setLoading(true);
    try { if (!["WORKFORCE", "DEPARTMENT"].includes(authenticatedUser.role)) await refreshWorkspace(); }
    catch (requestError) { setError(requestError); }
    finally { setLoading(false); }
  };

  const signOut = async () => {
    try { await authApi.logout(); }
    finally { setUser(null); setWorkflowData(null); setError(null); }
  };

  const applyMutation = async (promise) => {
    const result = await promise;
    if (result.data) setWorkflowData(result.data);
    return result;
  };

  const retry = async () => {
    setLoading(true);
    try {
      if (user) await refreshWorkspace();
      else {
        const result = await authApi.me(); setUser(result.user); await refreshWorkspace();
      }
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { setUser(null); setWorkflowData(null); }
      else setError(requestError);
    } finally { setLoading(false); }
  };

  if (loading) return <AccessState title="Loading PRAVAHA" message="Checking your session and loading your assigned workspace." />;
  if (!user) return <HomePage onAuthenticated={handleAuthenticated} />;
  if (user.role === "WORKFORCE") return <AccessState title="Access restricted" message="You are signed in. Workforce accounts have no management workspace permissions; work is managed through your Team Leader." onSignOut={signOut} />;
  if (user.role === "DEPARTMENT") return <main className="department-workspace"><header><div><h1>PRAVAHA · Department workspace</h1><p>{user.name}</p></div><div className="pr-department-actions"><PreferenceControls compact /><ProfileMenu name={user.name} role="Department account" onSignOut={signOut} /></div></header><OrganizationPanel /></main>;
  if (error) return <AccessState title={error.status === 403 ? "Access restricted" : "Workspace unavailable"} message={error.message ?? "The workspace could not be loaded."} onRetry={retry} onSignOut={signOut} />;
  if (!workflowData) return <AccessState title="Workspace unavailable" message="No workspace data was returned by the server." onRetry={retry} onSignOut={signOut} />;

  const assistant = <Suspense fallback={null}><AssistantWidget key={`${user.id}:${user.organizationId}:${user.role}`} user={user} activities={workflowData.scheduleActivities} /></Suspense>;
  if (user.role === "ADMIN") return <><AdminDashboard onReload={refreshWorkspace} workflowData={workflowData} user={user} onCreateUser={async (payload) => { const result = await workflowApi.createUser(payload); await refreshWorkspace(); return result; }} onUpdateAssignment={async (assignment) => {
    if (assignment.type === "project-manager") await applyMutation(workflowApi.assignProjectManager(assignment.projectId, assignment.projectManagerId));
    else if (assignment.type === "team-leader") await applyMutation(workflowApi.assignTeamLeader(assignment.teamId, assignment.teamLeaderId));
    else if (assignment.type === "team") await applyMutation(workflowApi.assignTeam(assignment.projectId, assignment.teamId, assignment.assigned !== false));
  }} onSignOut={signOut} />{assistant}</>;

  if (user.role === "PROJECT_MANAGER") return <><ProjectManagerDashboard onReload={refreshWorkspace} workflowData={workflowData} projectManagerId={user.id} onRequestReview={async (updateId) => applyMutation(workflowApi.requestPlannerReview(updateId))} onReviewAction={async (updateId, decision, scheduleActivityId, reason, feedback) => applyMutation(workflowApi.decideReview(updateId, decision, scheduleActivityId, reason, feedback))} onSignOut={signOut} />{assistant}</>;

  if (user.role === "TEAM_LEADER") return <><TeamLeaderDashboard workflowData={workflowData} teamLeaderId={user.id} onSubmitFieldUpdate={async (payload) => applyMutation(workflowApi.submitFieldUpdate(payload))} onRecordActivity={async (activityId, action, details) => applyMutation(workflowApi.recordActivityAction(activityId, action, details))} onSignOut={signOut} />{assistant}</>;

  return <AccessState title="Access restricted" message="This account does not have a supported PRAVAHA workspace role." onSignOut={signOut} />;
}

export default App;
