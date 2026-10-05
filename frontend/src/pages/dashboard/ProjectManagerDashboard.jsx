import UiText from "../../ui/UiText.jsx";
import OrganizationPanel from "../../components/organization/OrganizationPanel.jsx";
import ScheduleIngestion from "../../components/workflow/ScheduleIngestion.jsx";
import RecordSearch from "../../components/workflow/RecordSearch.jsx";
import {
  LayoutDashboard,
  FolderKanban,
  CalendarDays,
  ClipboardCheck,
  GitMerge,
  BarChart3,
  FileText,
  BookOpen,
  ClipboardList,
  Settings,
} from "lucide-react";
import { useState } from "react";
import ProjectWorkflowWorkspace from "../../components/workflow/ProjectWorkflowWorkspace";
import "../../styles/project-manager-dashboard.css";
import ExecutionIntelligence from "../../components/workflow/ExecutionIntelligence.jsx";
import ProjectManagerOverview from "../../components/workflow/ProjectManagerOverview.jsx";
import WorkspaceHeader from "../../components/layout/WorkspaceHeader.jsx";
import Footer from "../../components/layout/Footer.jsx";

function SidebarItem({ icon: Icon, label, active = false, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      aria-current={active ? "page" : undefined}
      className={`group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm transition-all duration-200 ${
        active
          ? "bg-blue-500/15 text-blue-400 shadow-[inset_3px_0_0_#3b82f6]"
          : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
      }`}
    >
      <Icon
        size={18}
        strokeWidth={1.8}
        className={
          active
            ? "text-blue-400"
            : "text-slate-500 group-hover:text-slate-100"
        }
      />

      <span><UiText>{label}</UiText></span>
    </button>
  );
}

function ProjectManagerDashboard({ onReload, workflowData: sharedWorkflowData, projectManagerId, onRequestReview, onReviewAction, onSignOut }) {
  const [activeView, setActiveView] = useState("Dashboard");
  const [focusedUpdateId, setFocusedUpdateId] = useState("FU-1043");
  const [detailUpdateId, setDetailUpdateId] = useState(null);
  const [notice, setNotice] = useState("");
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  const navigate = (view) => {
    setActiveView(view);
    setDetailUpdateId(null);
  };

  const openDetails = (updateId) => {
    setFocusedUpdateId(updateId);
    setDetailUpdateId(updateId);
  };

  const createReviewItem = async (updateId) => {
    try {
      await onRequestReview(updateId);
      setFocusedUpdateId(updateId);
      navigate("Planner Review");
    } catch (error) { setNotice(error.message ?? "Review could not be created."); }
  };

  const decideMatch = async (updateId, decision, scheduleActivityId, reason = "", feedback = "") => {
    try {
      const result = await onReviewAction(updateId, decision, scheduleActivityId, reason, feedback);
      setNotice(result.message);
      if (result.shouldClose) setDetailUpdateId(null);
    } catch (error) { setNotice(error.message ?? "Review decision could not be saved."); }
  };

  const assignedProjectManagerRecord = sharedWorkflowData.projectManagers.find((manager) => manager.id === projectManagerId);
  const assignedProjects = Array.isArray(assignedProjectManagerRecord?.assignedProjectIds)
    ? sharedWorkflowData.projects.filter((item) => assignedProjectManagerRecord.assignedProjectIds.includes(item.id))
    : sharedWorkflowData.projects.filter((item) => item.projectManagerId === projectManagerId);
  const project = assignedProjects.find((item) => item.id === selectedProjectId) ?? assignedProjects[0] ?? null;
  const assignedProjectManager = assignedProjectManagerRecord?.name ?? "Unassigned Project Manager";
  const assignedProjectIds = new Set(assignedProjects.map((item) => item.id));
  const assignedUpdateIds = new Set(sharedWorkflowData.fieldUpdates.filter((item) => assignedProjectIds.has(item.projectId)).map((item) => item.id));
  const workflowData = {
    ...sharedWorkflowData,
    projects: assignedProjects,
    teams: sharedWorkflowData.teams.filter((item) => assignedProjectIds.has(item.projectId)),
    scheduleActivities: sharedWorkflowData.scheduleActivities.filter((item) => assignedProjectIds.has(item.projectId)),
    fieldUpdates: sharedWorkflowData.fieldUpdates.filter((item) => assignedProjectIds.has(item.projectId)),
    activityMatches: sharedWorkflowData.activityMatches.filter((item) => assignedUpdateIds.has(item.fieldUpdateId)),
    reviewItems: sharedWorkflowData.reviewItems.filter((item) => assignedUpdateIds.has(item.fieldUpdateId)),
  };

  return (
<div className="pm-dashboard min-h-screen bg-[#061525] text-white">
<WorkspaceHeader name={assignedProjectManager} role="Project Manager" onSettings={() => navigate("Settings")} onSignOut={onSignOut} />
<aside className="pm-sidebar fixed inset-y-0 left-0 z-40 flex w-[245px] flex-col border-r border-white/[0.06] bg-[#07192b]">
        {/* The shared header owns branding and account controls. */}

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto px-3 py-5">
          <p className="mb-3 px-4 text-[13px] font-semibold uppercase tracking-[0.2em] text-slate-600"><UiText>
            Workspace
          </UiText></p>

          <nav className="space-y-1">
            <SidebarItem
              icon={LayoutDashboard}
              label="Dashboard"
              active={activeView === "Dashboard"}
              onClick={() => navigate("Dashboard")}
            />

            <SidebarItem icon={FolderKanban} label="Projects" active={activeView === "Projects"} onClick={() => navigate("Projects")} />
            <SidebarItem icon={CalendarDays} label="Schedule" active={activeView === "Schedule"} onClick={() => navigate("Schedule")} />
            <SidebarItem icon={ClipboardCheck} label="Field Updates" active={activeView === "Field Updates"} onClick={() => navigate("Field Updates")} />
            <SidebarItem icon={GitMerge} label="Activity Matching" active={activeView === "Activity Matching"} onClick={() => navigate("Activity Matching")} />
            <SidebarItem icon={ClipboardList} label="Planner Review" active={activeView === "Planner Review"} onClick={() => navigate("Planner Review")} />
            <SidebarItem icon={BarChart3} label="Analytics" active={activeView === "Analytics"} onClick={() => navigate("Analytics")} />
            <SidebarItem icon={FileText} label="Reports" active={activeView === "Reports"} onClick={() => navigate("Reports")} />
          </nav>

          <p className="mb-3 mt-8 px-4 text-[13px] font-semibold uppercase tracking-[0.2em] text-slate-600"><UiText>
            Resources
          </UiText></p>

          <nav className="space-y-1">
            <SidebarItem icon={BookOpen} label="Knowledge Base" active={activeView === "Knowledge Base"} onClick={() => navigate("Knowledge Base")} />
            <SidebarItem icon={Settings} label="Settings" active={activeView === "Settings"} onClick={() => navigate("Settings")} />
          </nav>
        </div>

        {/* User */}
        <div className="border-t border-white/[0.06] p-4">
          <div className="flex items-center gap-3 rounded-xl bg-white/[0.025] p-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#25476b] text-xs font-semibold">
              PM
            </div>

            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium text-white">
                {assignedProjectManager}
              </p>

              <p className="truncate text-[11px] text-slate-500"><UiText>
                Project Manager
              </UiText></p>
            </div>

            <span className="text-slate-600">•••</span>
          </div>
        </div>
      </aside>
      {/* TOP HEADER */}
<header className="pm-header fixed left-[245px] right-0 top-0 z-30 flex h-20 items-center justify-between border-b border-white/[0.06] bg-[#061525]/90 px-8 backdrop-blur-xl">
  {/* Search */}
  <div className="relative w-[340px]">
    <svg
      className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" />
    </svg>

    <input
      type="text"
      placeholder="Search projects, activities"
      className="h-10 w-full rounded-xl border border-white/[0.06] bg-white/[0.025] pl-10 pr-4 text-xs text-white outline-none placeholder:text-slate-600 focus:border-blue-500/30"
    />
  </div>

  {/* Right side */}
  <div className="flex items-center gap-4">

    {/* Notification */}
    <button className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.06] bg-white/[0.025] text-slate-400 transition hover:text-white">
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M10 21h4" />
      </svg>

      <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-red-400" />
    </button>

    <div className="h-7 w-px bg-white/[0.06]" />

  </div>
</header>{/* DASHBOARD CONTENT */}
<main className="pm-main ml-[245px] min-w-0 pt-20">
  {["Dashboard", "Analytics", "Reports", "Knowledge Base"].includes(activeView) ? (
    <div className="w-full px-8 py-7">
      {activeView !== "Dashboard" && <h1 className="mb-4 text-2xl">{activeView}</h1>}
      {activeView === "Dashboard" && <><ProjectManagerOverview data={workflowData} currentProjectId={project?.id} onSelectProject={setSelectedProjectId} onNavigate={navigate} onSelectUpdate={setFocusedUpdateId} onRefresh={onReload} /><ExecutionIntelligence projects={assignedProjects} currentProjectId={project?.id} onSelectProject={setSelectedProjectId} workflowData={sharedWorkflowData} /><details className="pmo-tools"><summary><UiText>Schedule import and record search</UiText></summary><ScheduleIngestion key={project?.id} projectId={project?.id} onReload={onReload} /><RecordSearch /></details></>}
      {activeView !== "Dashboard" && <><ScheduleIngestion key={project?.id} projectId={project?.id} onReload={onReload} /><RecordSearch /><ExecutionIntelligence projects={assignedProjects} currentProjectId={project?.id} onSelectProject={setSelectedProjectId} workflowData={sharedWorkflowData} /></>}
    </div>
  ) : (
    <div className="w-full px-8 py-7">
      <ProjectWorkflowWorkspace
        view={activeView}
        data={workflowData}
        currentProjectId={project?.id}
        onSelectProject={setSelectedProjectId}
        selectedUpdateId={focusedUpdateId}
        detailUpdateId={detailUpdateId}
        onSelectUpdate={setFocusedUpdateId}
        onOpenDetails={openDetails}
        onCloseDetails={() => setDetailUpdateId(null)}
        onDecision={decideMatch}
        onCreateReview={createReviewItem}
        onNavigate={navigate}
        notice={notice}
        clearNotice={() => setNotice("")}
      />
    </div>
  )}
<details className="org-support mx-8"><summary><UiText>Project workforce and support workflows</UiText></summary><OrganizationPanel view="Roster" /><OrganizationPanel /></details>
<Footer compact />
</main>
    </div>
  );
}

export default ProjectManagerDashboard;
