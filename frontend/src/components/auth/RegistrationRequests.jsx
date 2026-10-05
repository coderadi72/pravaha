import { useEffect, useRef, useState } from "react";
import { registrationApi } from "../../api/client.js";
import { useUiPreferences } from "../../ui/useUiPreferences.js";

const STATUS_LABELS = { PENDING: "Pending registration", APPROVED: "Approved", REJECTED: "Rejected" };
const STATUS_CLASSES = { PENDING: "is-at-risk", APPROVED: "is-active", REJECTED: "is-unmatched" };
const ROLE_LABELS = { PROJECT_MANAGER: "Project Manager", DEPARTMENT: "Department account", TEAM_LEADER: "Team Leader / Supervisor" };

export default function RegistrationRequests({ organization, onReload }) {
  const { t, locale } = useUiPreferences();
  const [status, setStatus] = useState("PENDING");
  const [offset, setOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const [page, setPage] = useState({ registrations: [], total: 0, limit: 25 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busyId, setBusyId] = useState(null);
  const [selectedRoles, setSelectedRoles] = useState({});
  const [rejectingId, setRejectingId] = useState(null);
  const [rejectionReason, setRejectionReason] = useState("");
  const busyLock = useRef(false);

  useEffect(() => {
    let active = true;
    registrationApi.list({ status, offset })
      .then((result) => { if (active) setPage(result); })
      .catch(() => { if (active) setError("Registration requests could not be loaded. Please try again."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [status, offset, revision]);

  const refresh = () => {
    if (busyLock.current) return;
    setError("");
    setLoading(true);
    setOffset(0);
    setRevision((value) => value + 1);
  };

  const changePage = (nextOffset) => {
    setError("");
    setLoading(true);
    setOffset(nextOffset);
  };

  const review = async (registration, decision) => {
    if (busyLock.current) return;
    busyLock.current = true;
    setBusyId(registration.id);
    setError("");
    setMessage("");
    try {
      if (decision === "approve") {
        const approvedRole = registration.requestedRoleCategory === "SUPERVISOR" ? "TEAM_LEADER" : selectedRoles[registration.id] || "PROJECT_MANAGER";
        await registrationApi.approve(registration.id, approvedRole);
        setMessage("Registration approved. The account can now sign in.");
      } else {
        await registrationApi.reject(registration.id, rejectionReason);
        setMessage("Registration rejected. No account was activated.");
      }
      setRejectingId(null);
      setRejectionReason("");
      setLoading(true);
      setOffset(0);
      setRevision((value) => value + 1);
      try { await onReload?.(); }
      catch { setMessage("Registration review saved. Refresh the workspace if the account is not visible yet."); }
    } catch (failure) {
      setError(failure.status === 403
        ? "You do not have access to review registration requests."
        : failure.code === "DUPLICATE_EMAIL"
          ? "If an account or registration already exists for this email, please contact your organization administrator."
          : failure.code === "REGISTRATION_REVIEWED"
            ? "This registration has already been reviewed. Refresh the list."
            : "The registration could not be reviewed. Please try again.");
    } finally {
      busyLock.current = false;
      setBusyId(null);
    }
  };

  return <section className="org-panel" aria-busy={loading || busyId !== null}>
    <div className="org-section-heading">
      <div><span className="org-kicker">{t("Administrator approval")}</span><h2>{t("Registration requests")}</h2></div>
      <button type="button" onClick={refresh} disabled={loading || busyId !== null}>{t("Refresh")}</button>
    </div>
    <p className="org-muted">{t("Approval assigns this account to your organization.")} {organization?.name}</p>
    <div className="org-toolbar">
      <label>{t("Status")}<select aria-label={t("Status")} value={status} disabled={busyId !== null} onChange={(event) => { setStatus(event.target.value); setOffset(0); setLoading(true); setError(""); }}>
        <option value="PENDING">{t("Pending registration")}</option><option value="APPROVED">{t("Approved")}</option><option value="REJECTED">{t("Rejected")}</option><option value="">{t("All statuses")}</option>
      </select></label>
      <span>{t("Total requests")}: {page.total}</span>
    </div>
    {message && <p role="status">{t(message)}</p>}
    {error && <p role="alert">{t(error)}</p>}
    {loading ? <p className="org-muted" role="status">{t("Loading registration requests…")}</p> : !error && (page.registrations.length ? <>
      <div className="org-table-scroll"><table><thead><tr>
        {["Name", "Work email", "Requested category", "Email domain", "Status", "Created date", "Actions"].map((label) => <th key={label} scope="col">{t(label)}</th>)}
      </tr></thead><tbody>{page.registrations.map((registration) => <tr key={registration.id}>
        <td>{registration.name}</td><td>{registration.email}</td><td>{t(registration.requestedRoleCategory === "MANAGEMENT" ? "Management" : "Team Leader / Supervisor")}</td><td>{registration.emailDomain}</td>
        <td><span className={`ad-status ${STATUS_CLASSES[registration.status] || ""}`}>{t(STATUS_LABELS[registration.status] || registration.status)}</span></td>
        <td><time dateTime={registration.createdAt}>{new Date(registration.createdAt).toLocaleString(locale)}</time></td>
        <td>{registration.status === "PENDING" ? <div>
          <label>{t("Final role")}<select aria-label={`${t("Final role")}: ${registration.name}`} value={registration.requestedRoleCategory === "SUPERVISOR" ? "TEAM_LEADER" : selectedRoles[registration.id] || "PROJECT_MANAGER"} disabled={busyId !== null} onChange={(event) => setSelectedRoles((roles) => ({ ...roles, [registration.id]: event.target.value }))}>
            {registration.requestedRoleCategory === "SUPERVISOR" ? <option value="TEAM_LEADER">{t("Team Leader / Supervisor")}</option> : <><option value="PROJECT_MANAGER">{t("Project Manager")}</option><option value="DEPARTMENT">{t("Department account")}</option></>}
          </select></label>
          <div className="org-row-actions"><button type="button" disabled={busyId !== null || loading} onClick={() => review(registration, "approve")}>{t(busyId === registration.id ? "Reviewing…" : "Approve")}</button><button type="button" disabled={busyId !== null || loading} onClick={() => { setRejectingId(registration.id); setRejectionReason(""); }}>{t("Reject")}</button></div>
          {rejectingId === registration.id && <form onSubmit={(event) => { event.preventDefault(); if (rejectionReason.trim()) review(registration, "reject"); }}>
            <label>{t("Rejection reason")}<input value={rejectionReason} onChange={(event) => setRejectionReason(event.target.value)} required maxLength={500} placeholder={t("Give a short reason for the decision.")} disabled={busyId !== null} /></label>
            <div className="org-row-actions"><button type="submit" disabled={busyId !== null || !rejectionReason.trim()}>{t("Confirm rejection")}</button><button type="button" disabled={busyId !== null} onClick={() => { setRejectingId(null); setRejectionReason(""); }}>{t("Cancel")}</button></div>
          </form>}
        </div> : <><span>{t(ROLE_LABELS[registration.approvedRole] || STATUS_LABELS[registration.status] || registration.status)}</span>{registration.rejectionReason && <p className="org-muted">{registration.rejectionReason}</p>}</>}</td>
      </tr>)}</tbody></table></div>
      <div className="org-pagination"><button type="button" disabled={offset === 0 || busyId !== null} onClick={() => changePage(Math.max(0, offset - page.limit))}>{t("Previous")}</button><span>{offset + 1}–{offset + page.registrations.length} / {page.total}</span><button type="button" disabled={offset + page.limit >= page.total || busyId !== null} onClick={() => changePage(offset + page.limit)}>{t("Next")}</button></div>
    </> : <p className="org-muted">{t("No registration requests match this status.")}</p>)}
  </section>;
}
