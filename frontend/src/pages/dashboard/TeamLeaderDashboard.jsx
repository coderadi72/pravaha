import UiText from "../../ui/UiText.jsx";
import OrganizationPanel from "../../components/organization/OrganizationPanel.jsx";
import FieldEvidence from "../../components/workflow/FieldEvidence.jsx";
import { ingestionApi, filePayload } from "../../api/client.js";
import { useState } from "react";
import { Activity, ArrowRight, Bell, BookOpen, Check, CheckCircle2, ClipboardList, Clock3, FilePlus2, MapPin, Play, Users, X } from "lucide-react";
import "../../styles/project-manager-dashboard.css";
import { getTeamActivities } from "../../utils/workspace.js";
import { formatCurrentDate } from "../../utils/date.js";
import WorkspaceHeader from "../../components/layout/WorkspaceHeader.jsx";
import Footer from "../../components/layout/Footer.jsx";

const NAV_ITEMS = [
  { id: "Dashboard", icon: Activity },
  { id: "My Activities", icon: ClipboardList },
  { id: "Field Updates", icon: FilePlus2 },
  { id: "My Team", icon: Users },
  { id: "Notifications", icon: Bell },
];

const dateTime = (value) => value ? new Intl.DateTimeFormat("en-IN", { hour: "2-digit", minute: "2-digit" }).format(new Date(value)) : "Not recorded";
const initials = (name) => name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();

function TLStatus({ status }) {
  const tone = status.toLowerCase().replaceAll(" ", "-");
  return <span className={`tl-status is-${tone}`}><UiText>{status}</UiText></span>;
}

function TLNav({ active, onNavigate, teamLeaderName, teamName }) {
  return (
    <aside className="tl-sidebar">

      <p className="tl-nav-label"><UiText>SITE WORKSPACE</UiText></p>
      <nav aria-label="Team Leader navigation">
        {NAV_ITEMS.map(({ id, icon: Icon }) => <button key={id} type="button" className={active === id ? "is-active" : ""} aria-current={active === id ? "page" : undefined} onClick={() => onNavigate(id)}><Icon size={18} /><span><UiText>{id}</UiText></span>{id === "Notifications" && <i />}</button>)}
      </nav>
      <div className="tl-sidebar-profile"><span>{initials(teamLeaderName)}</span><div><strong>{teamLeaderName}</strong><small><UiText>Team Leader · </UiText>{teamName}</small></div></div>
    </aside>
  );
}

function FieldUpdateComposer({ activities, onClose, onSubmit, teamLeaderName }) {
  const [description, setDescription] = useState("");
  const [activityId, setActivityId] = useState("");
  const [showDetails, setShowDetails] = useState(false);
  const [progress, setProgress] = useState("");
  const [observation, setObservation] = useState("");
  const [discipline, setDiscipline] = useState("");
  const [location, setLocation] = useState("");
  const [attachmentName, setAttachmentName] = useState("");
  const [attachment, setAttachment] = useState(null);
  const [structured, setStructured] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const selectedActivity = activities.find((item) => item.id === activityId);

  async function submit(event) {
    event.preventDefault();
    const value = description.trim();
    if (!value || submitting) return;
    setSubmitting(true);
    try { await onSubmit({ description: value, activity: selectedActivity, progress: progress === "" ? null : Number(progress), observation: observation.trim(), discipline: discipline || selectedActivity?.discipline || "", location: location.trim() || selectedActivity?.location || "", attachmentName, attachment, ...structured, ...(structured.quantity ? { quantity: Number(structured.quantity) } : { quantity: null }) }); }
    finally { setSubmitting(false); }
  }

  return <section className="tl-composer" aria-labelledby="tl-composer-title">
    <div className="tl-composer-heading"><div><span className="tl-section-kicker"><UiText>FIELD CAPTURE</UiText></span><h2 id="tl-composer-title"><UiText>What happened at site?</UiText></h2><p><UiText>Describe the work in your own words. Activity linking can be reviewed later.</UiText></p></div><button type="button" aria-label="Close field update" className="tl-close" onClick={onClose}><X size={18} /></button></div>
    <form onSubmit={submit}>
      <label className="tl-description-label" htmlFor="tl-description"><UiText>Field observation </UiText><span><UiText>Required</UiText></span></label>
      <textarea id="tl-description" autoFocus rows={3} maxLength={500} value={description} onChange={(event) => setDescription(event.target.value)} placeholder={'Describe what happened at site…\ne.g. “Spool erected for Line 247-XX”'} required />
      <button className="tl-disclosure" type="button" aria-expanded={showDetails} onClick={() => setShowDetails((value) => !value)}>{showDetails ? "Hide" : "Add"}<UiText> activity details </UiText><span><UiText>Optional</UiText></span></button>
      {showDetails && <div className="tl-optional-fields">
        <label><UiText>Activity (optional)</UiText><select value={activityId} onChange={(event) => setActivityId(event.target.value)}><option value=""><UiText>Let the planner link this update</UiText></option>{activities.map((item) => <option value={item.id} key={item.id}>{item.activityName}</option>)}</select></label>
        <label><UiText>Discipline (optional)</UiText><select value={discipline || selectedActivity?.discipline || ""} onChange={(event) => setDiscipline(event.target.value)}><option value=""><UiText>Select discipline</UiText></option>{["Piping", "Civil", "Mechanical", "Static Equipment", "Rotating Equipment", "Electrical", "Instrumentation", "HSE"].map((item) => <option key={item}>{item}</option>)}</select></label>
        <label><UiText>Location (optional)</UiText><input value={location || selectedActivity?.location || ""} onChange={(event) => setLocation(event.target.value)} placeholder="Area, unit, or package" /></label>
        <label><UiText>Progress </UiText>{selectedActivity ? `(current ${selectedActivity.progress}%)` : "(optional)"}<div className="tl-range-control"><input type="range" min="0" max="100" step="5" value={progress === "" ? (selectedActivity?.progress ?? 0) : progress} onChange={(event) => setProgress(event.target.value)} /><span>{progress === "" ? (selectedActivity?.progress ?? 0) : progress}%</span></div></label>
        <label><UiText>Observation </UiText><input value={observation} onChange={(event) => setObservation(event.target.value)} placeholder="Delay, access issue, or work note" /></label>
        {["quantity", "unit", "remarks", "blocker", "crew", "equipment"].map(key => <label key={key}>{key}<input aria-label={`Field ${key}`} type={key === "quantity" ? "number" : "text"} min={key === "quantity" ? "0" : undefined} step={key === "quantity" ? "any" : undefined} maxLength={120} value={structured[key] ?? ""} onChange={e => setStructured({ ...structured, [key]: e.target.value })} /></label>)}
        <p><UiText>Voice transcription and OCR are not configured. WAV recordings may be attached as evidence; enter the observation text for matching.</UiText></p>
        <label><UiText>Source / attachment </UiText><span className="tl-file-input"><input type="file" accept="image/png,image/jpeg,.pdf,.xlsx,.csv,.txt,.wav" onChange={(event) => { setAttachment(event.target.files?.[0] ?? null); setAttachmentName(event.target.files?.[0]?.name ?? ""); }} />{attachmentName || "Choose a site photo, diary, or document"}</span></label>
      </div>}
      <div className="tl-composer-footer"><span><UiText>Submitted as </UiText>{teamLeaderName}<UiText> · Team Leader / Supervisor</UiText></span><button type="submit" className="tl-primary-button" disabled={!description.trim() || submitting}><Check size={16} /> <UiText>{submitting ? "Processing…" : "Submit field update"}</UiText></button></div>
    </form>
  </section>;
}

function ActivityRow({ activity, onAction }) {
  const [editing, setEditing] = useState(false);
  const [progress, setProgress] = useState(activity.progress ?? 0);
  const [observation, setObservation] = useState(activity.observation || "");
  const [blockedReason, setBlockedReason] = useState("");
  const [blocking, setBlocking] = useState(false);
  const isStarted = Boolean(activity.actualStart);
  const isComplete = activity.status === "Completed" || activity.status === "Complete";

  return <article className="tl-activity-row">
    <div className="tl-activity-main"><div className="tl-activity-title-row"><h3>{activity.activityName}</h3><TLStatus status={activity.status} /></div><p>{activity.discipline} <span>·</span> <MapPin size={13} /> {activity.location}</p><div className="tl-activity-planned"><Clock3 size={13} /><UiText> Planned </UiText>{activity.plannedStart}–{activity.plannedEnd}{activity.actualStart && <> <span>·</span><UiText> Started </UiText>{dateTime(activity.actualStart)}</>}{activity.actualEnd && <> <span>·</span><UiText> Ended </UiText>{dateTime(activity.actualEnd)}</>}</div></div>
    <div className="tl-activity-progress"><div><span><UiText>Progress</UiText></span><strong>{activity.progress == null ? "Not reported" : `${activity.progress}%`}</strong></div><div className="tl-progress-track"><i style={{ width: `${activity.progress ?? 0}%` }} /></div></div>
    <div className="tl-activity-actions">
      {!isStarted && !isComplete && <button type="button" className="tl-button-secondary" onClick={() => onAction(activity.id, "start")}><Play size={14} /><UiText> Start</UiText></button>}
      {isStarted && !isComplete && <button type="button" className="tl-button-secondary" onClick={() => setEditing((value) => !value)}><UiText>Update</UiText></button>}
      {!isComplete && <button type="button" className="tl-button-primary" onClick={() => onAction(activity.id, "complete", { progress: 100, observation })}><Check size={14} /><UiText> Complete</UiText></button>}
      {!isComplete && activity.status !== "Blocked" && <button type="button" className="tl-text-button" onClick={() => setBlocking((value) => !value)}><UiText>Mark blocked</UiText></button>}
    </div>
    {editing && <form className="tl-inline-editor" onSubmit={(event) => { event.preventDefault(); onAction(activity.id, "update", { progress: Number(progress), observation }); setEditing(false); }}><label><UiText>Progress </UiText><strong>{progress}%</strong><input type="range" min="0" max="100" step="5" value={progress} onChange={(event) => setProgress(event.target.value)} /></label><label><UiText>Observation (optional)</UiText><input value={observation} onChange={(event) => setObservation(event.target.value)} placeholder="What changed at site?" /></label><button type="submit" className="tl-primary-button"><UiText>Save field update</UiText></button></form>}
    {blocking && <form className="tl-inline-editor is-blocked" onSubmit={(event) => { event.preventDefault(); if (!blockedReason.trim()) return; onAction(activity.id, "block", { blockedReason, observation }); setBlocking(false); }}><label><UiText>Reason this work is blocked</UiText><input autoFocus value={blockedReason} onChange={(event) => setBlockedReason(event.target.value)} placeholder="e.g. Material not available" required /></label><button type="submit" className="tl-warning-button"><UiText>Record blocked activity</UiText></button></form>}
  </article>;
}

function SubmissionRow({ update, match, reviewItem, onOpen }) {
  const status = update.reviewStatus === "action_required" ? "Action Required" : update.reviewStatus === "reviewed" ? "Reviewed" : match?.matchStatus === "matched" ? "Matched" : match?.matchStatus === "rejected" ? "Reviewed" : match?.matchStatus === "unmatched" ? "Unmatched" : match?.matchStatus === "processing" ? "Processing" : match?.matchStatus === "low_confidence" || match?.matchStatus === "review_required" ? "Needs Review" : "Submitted";
  const linkedActivity = update.pmFeedback || (match?.matchStatus === "matched" ? match.reviewComment : reviewItem?.reason);
  const recommendation = match?.candidates?.find((item) => item.scheduleActivityId === match.recommendedMatchId);
  return <article className="tl-submission-row"><span className="tl-submission-icon"><FilePlus2 size={16} /></span><div className="tl-submission-copy"><strong>{update.rawText}</strong><small>{update.extractedActivity?.activityName ?? update.activity ?? "Field observation"} · {dateTime(update.submittedAt)}</small>
    {match?.matcherVersion && <div className="tl-extraction-summary"><span><UiText>Detected: </UiText>{update.extractedActivity?.discipline ?? "Unclassified"}{update.extractedActivity?.identifiers?.length ? ` · ${update.extractedActivity.identifiers.join(", ")}` : ""}</span><span>{recommendation ? `Suggested: ${recommendation.activityName}` : match.recommendationRestricted ? "Recommendation details sent to your PM" : match.recommendationStatus === "ambiguous" ? "Multiple plausible activities" : "No confident recommendation"}</span>{update.reviewStatus !== "reviewed" && <span><UiText>Waiting for PM review</UiText></span>}</div>}
    {linkedActivity && <p className={match?.matchStatus === "matched" ? "is-confirmed" : "is-feedback"}><span>{match?.matchStatus === "matched" ? "PM feedback" : "Review note"}</span>{linkedActivity}</p>}<FieldEvidence update={update} /></div><div className="tl-submission-status"><TLStatus status={status} />{typeof match?.confidence === "number" && <small>{match?.matchStatus === "matched" ? "PM-confirmed schedule link" : match.confidence > 0 ? `${match.confidence}% confidence` : "No schedule link"}</small>}</div><button type="button" aria-label={`Open ${update.rawText}`} className="tl-row-action" onClick={() => onOpen(update.id)}><ArrowRight size={16} /></button></article>;
}

function SupervisorMain({ activeView, data, team, activities, updates, onAction, onReview, setComposerOpen }) {
  const open = (title, detail) => <div className="tl-placeholder"><BookOpen size={19} /><div><strong><UiText>{title}</UiText></strong><p>{detail}</p></div></div>;
  if (activeView === "My Team") return <section className="tl-panel"><div className="tl-section-heading"><div><span className="tl-section-kicker"><UiText>TEAM ON SITE</UiText></span><h2>{team.name}</h2><p><UiText>Execution coverage for the current shift.</UiText></p></div></div><div className="tl-team-summary"><div><span><UiText>Team members</UiText></span><strong>{team.members}</strong></div><div><span><UiText>Active on site</UiText></span><strong>{team.active}</strong></div><div><span><UiText>On leave</UiText></span><strong>{team.onLeave}</strong></div><div><span><UiText>Other assignment</UiText></span><strong>{team.other}</strong></div></div><div className="tl-team-note"><Users size={17} /><p><UiText>Team staffing is provided for site context. Organization and user administration are managed by authorized roles.</UiText></p></div></section>;
  if (activeView === "Notifications") return <section className="tl-panel"><div className="tl-section-heading"><div><span className="tl-section-kicker"><UiText>SITE NOTIFICATIONS</UiText></span><h2><UiText>Updates that need your attention</UiText></h2></div></div>{updates.some((update) => update.pmFeedback) ? updates.filter((update) => update.pmFeedback).map((update) => <SubmissionRow key={update.id} update={update} match={data.activityMatches.find((item) => item.fieldUpdateId === update.id)} reviewItem={data.reviewItems.find((item) => item.fieldUpdateId === update.id)} onOpen={onReview} />) : open("No new PM feedback", "Your submitted updates will appear here when a Project Manager reviews them.")}</section>;

  return <>
    {(activeView === "Dashboard" || activeView === "My Activities") && <section className="tl-panel tl-today-panel"><div className="tl-section-heading"><div><span className="tl-section-kicker"><UiText>TODAY'S WORK</UiText></span><h2>{activeView === "My Activities" ? "Assigned activities" : "Your assigned activities"}</h2><p><UiText>Work assigned to </UiText>{team.name}<UiText> · select a quick action to report site progress.</UiText></p></div><span className="tl-count-label">{activities.length}<UiText> activities</UiText></span></div>
      {activities.length ? <div className="tl-activity-list">{activities.map((activity) => <ActivityRow key={activity.id} activity={activity} onAction={onAction} />)}</div> : open("No activities assigned today", "There are no activities assigned to your team for this shift. Contact your Project Manager if this looks incorrect.")}
    </section>}
    {(activeView === "Dashboard" || activeView === "Field Updates") && <section className="tl-panel tl-submissions-panel"><div className="tl-section-heading"><div><span className="tl-section-kicker"><UiText>FIELD REPORTING</UiText></span><h2>{activeView === "Field Updates" ? "Your submitted updates" : "Recently submitted"}</h2><p><UiText>Field observations are sent for schedule linking and Project Manager review.</UiText></p></div>{activeView === "Dashboard" && <button className="tl-link-button" type="button" onClick={() => setComposerOpen(true)}><UiText>View all </UiText><ArrowRight size={14} /></button>}</div>
      {updates.length ? <div className="tl-submission-list">{(activeView === "Dashboard" ? updates.slice(0, 4) : updates).map((update) => <SubmissionRow key={update.id} update={update} match={data.activityMatches.find((item) => item.fieldUpdateId === update.id)} reviewItem={data.reviewItems.find((item) => item.fieldUpdateId === update.id)} onOpen={onReview} />)}</div> : open("No field updates submitted today", "Use Add field update to record work as it happens. Your description is enough to start.")}
    </section>}
    {activeView === "Dashboard" && <div className="tl-bottom-grid"><section className="tl-panel"><div className="tl-section-heading"><div><span className="tl-section-kicker"><UiText>SHIFT SUMMARY</UiText></span><h2><UiText>Today's execution</UiText></h2></div></div><div className="tl-shift-summary"><div><strong>{activities.length}</strong><span><UiText>Assigned</UiText></span></div><div><strong>{activities.filter((item) => item.status === "Completed" || item.status === "Complete").length}</strong><span><UiText>Completed</UiText></span></div><div><strong>{activities.filter((item) => item.status === "In Progress").length}</strong><span><UiText>In progress</UiText></span></div><div className="is-blocked"><strong>{activities.filter((item) => item.status === "Blocked").length}</strong><span><UiText>Blocked</UiText></span></div><div><strong>{updates.filter((item) => item.submittedAt?.slice(0, 10) === new Date().toISOString().slice(0, 10)).length}</strong><span><UiText>Updates submitted</UiText></span></div></div></section>
      <section className="tl-panel tl-team-context"><div className="tl-section-heading"><div><span className="tl-section-kicker"><UiText>TEAM ON SITE</UiText></span><h2>{team.name}</h2></div><Users size={17} /></div><div className="tl-team-context-count"><strong>{team.active}</strong><span><UiText>of </UiText>{team.members}<UiText> members active</UiText></span></div><p><MapPin size={14} /> {team.site}</p></section></div>}
  </>;
}

export default function TeamLeaderDashboard({ workflowData, teamLeaderId, onSubmitFieldUpdate, onRecordActivity, onSignOut }) {
  const [activeView, setActiveView] = useState("Dashboard");
  const [composerOpen, setComposerOpen] = useState(false);
  const [notice, setNotice] = useState("");
  const assignedLeader = workflowData.teamLeaders.find((item) => item.id === teamLeaderId);
  const team = workflowData.teams.find((item) => item.id === assignedLeader?.teamId)
    ?? (assignedLeader?.teamId === undefined ? workflowData.teams.find((item) => item.teamLeaderId === teamLeaderId) : null)
    ?? { id: null, name: "No team assigned", projectId: assignedLeader?.projectId, site: "Assignment pending", members: 0, active: 0, onLeave: 0, other: 0 };
  const teamLeaderName = assignedLeader?.name ?? "Unassigned Team Leader";
  const activities = team.id ? getTeamActivities(workflowData, team.id) : [];
  const updates = workflowData.fieldUpdates.filter((item) => item.submitterUserId === teamLeaderId || (team.id && item.teamId === team.id)).sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));

  const submitObservation = async (payload) => {
    if (!team.id) return;
    setNotice("Submitted. Processing activity and schedule evidence…");
    try {
      const file = payload.attachment ? await filePayload(payload.attachment) : null;
      const result = await onSubmitFieldUpdate({ ...payload, attachment: undefined, activityId: payload.activity?.id });
      if (file) {
        try { await ingestionApi.upload(result.fieldUpdate.id, file); }
        catch (failure) { setComposerOpen(false); setNotice(`Update saved. Attachment failed: ${failure.message}`); return; }
      }
      setComposerOpen(false);
      setActiveView("Dashboard");
      setNotice("Field update submitted. Your Project Manager can now review the observation and schedule link.");
    } catch (error) { setNotice(error.message ?? "Field update could not be submitted."); }
  };

  const recordActivityAction = async (activityId, action, details = {}) => {
    try {
      await onRecordActivity(activityId, action, details);
      setNotice(action === "block" ? "Blocked activity recorded and sent to your Project Manager." : action === "start" ? "Activity started. Actual start time recorded and submitted for review." : action === "complete" ? "Activity completed. Actual end time recorded and submitted for review." : "Progress update submitted to your Project Manager.");
    } catch (error) { setNotice(error.message ?? "Activity update could not be saved."); }
  };

  const openReview = (updateId) => {
    const update = workflowData.fieldUpdates.find((item) => item.id === updateId);
    const match = workflowData.activityMatches.find((item) => item.fieldUpdateId === updateId);
    const review = workflowData.reviewItems.find((item) => item.fieldUpdateId === updateId);
    if (update?.reviewStatus === "action_required") setNotice(`Action required: ${update.pmFeedback}`);
    else if (match?.matchStatus === "matched" || review?.status === "accepted") setNotice(`Matched: ${match?.reviewComment ?? "Your Project Manager confirmed this schedule link."}`);
    else if (match?.matchStatus === "rejected" || review?.status === "rejected") setNotice("Your Project Manager reviewed this update. Check the review note for requested follow-up.");
    else if (match?.matchStatus === "unmatched") setNotice(update?.pmFeedback ? `No schedule match found. ${update.pmFeedback}` : "No schedule match found. Your update remains available in Project Manager review.");
    else setNotice("This update is with your Project Manager for schedule review. You do not need to approve the match.");
  };

  return <div className="tl-app">
    <WorkspaceHeader name={teamLeaderName} role="Team Leader / Supervisor" onSignOut={onSignOut} />
    <TLNav active={activeView} onNavigate={setActiveView} teamLeaderName={teamLeaderName} teamName={team.name} />
    <main className="tl-main">
      <header className="tl-header"><div><span className="tl-section-kicker">{formatCurrentDate().toUpperCase()}<UiText> · TODAY</UiText></span><h1><UiText>Good morning, </UiText>{teamLeaderName.split(" ")[0]}</h1><p><UiText>Field execution · </UiText>{workflowData.projects.find((project) => project.id === team.projectId)?.name ?? "Unassigned project"}</p></div><div className="tl-header-side"><div className="tl-site-context"><span><Users size={14} /> {team.name}</span><span><MapPin size={14} /> {team.site}</span></div></div></header>
      <div className="tl-titlebar"><div><h2><UiText>{activeView === "Dashboard" ? "Today's site work" : activeView}</UiText></h2><p><UiText>{activeView === "Dashboard" ? "Assigned work, quick reporting, and updates from your Project Manager." : `${workflowData.projects.find((project) => project.id === team.projectId)?.name ?? "Unassigned project"} · ${team.name}`}</UiText></p></div><button type="button" className="tl-primary-button tl-add-update" disabled={!team.id} onClick={() => setComposerOpen(true)}><FilePlus2 size={17} /><UiText> Add field update</UiText></button></div>
      {notice && <div className="tl-notice" role="status"><CheckCircle2 size={17} /><span>{notice}</span><button type="button" aria-label="Dismiss message" onClick={() => setNotice("")}><X size={16} /></button></div>}
      {composerOpen && <FieldUpdateComposer activities={activities} onClose={() => setComposerOpen(false)} onSubmit={submitObservation} teamLeaderName={teamLeaderName} />}
      <SupervisorMain activeView={activeView} data={workflowData} team={team} activities={activities} updates={updates} onAction={recordActivityAction} onReview={openReview} setComposerOpen={setComposerOpen} />
      <details className="org-support"><summary><UiText>Team workforce and support workflows</UiText></summary><OrganizationPanel view="Roster" /><OrganizationPanel /></details>
      <Footer compact />
    </main>
  </div>;
}
