import UiText from "../../ui/UiText.jsx";
import { useState } from 'react';
import { organizationApi as api } from '../../api/organization.js';
import { workflowApi } from '../../api/client.js';
import { ReferenceField } from './RecordForm.jsx';

function ActionForm({ title, fields, submit, checkbox, options }) {
  const [values, setValues] = useState({});
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const set = (name, value) => setValues((old) => ({ ...old, [name]:value }));
  const save = async (event) => {
    event.preventDefault();
    const submitted = { ...values, ...Object.fromEntries(new FormData(event.currentTarget)) };
    setValues(submitted); setBusy(true); setMessage('');
    try { await submit(submitted); setMessage('Saved. The change is recorded in the audit history.'); }
    catch (e) { setMessage(e.message); } finally { setBusy(false); }
  };
  return <details><summary><UiText>{title}</UiText></summary><form onSubmit={save}><div className="org-form-grid">{fields.map((name) => name.endsWith('_id') && name !== 'allocation_id' ? <ReferenceField key={name} name={name} value={values[name]} onChange={(value) => set(name, value)} required /> : <label key={name}>{name.replaceAll('_', ' ')}<input name={name} type={name.startsWith('effective_') ? 'date' : 'text'} required value={values[name] || ''} onChange={(e) => set(name, e.target.value)} /></label>)}{options && <label><UiText>Capability</UiText><select required value={values.capability || ''} onChange={(e) => set('capability', e.target.value)}><option value=""><UiText>Choose capability</UiText></option>{options.map((o) => <option key={o}>{o}</option>)}</select></label>}{checkbox && <label>{checkbox}<select value={String(values[checkbox] || false)} onChange={(e) => set(checkbox, e.target.value === 'true')}><option value="false"><UiText>No</UiText></option><option value="true"><UiText>Yes</UiText></option></select></label>}</div><div className="org-actions"><button type="submit" disabled={busy}>{busy ? 'Saving…' : 'Save assignment'}</button></div>{message && <p role="status">{message}</p>}</form></details>;
}

function History() {
  const [employee, setEmployee] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  return <details><summary><UiText>Workforce assignment history</UiText></summary><ReferenceField name="employee_id" value={employee} onChange={setEmployee} /><button type="button" onClick={async () => { try { setData(await api.history(employee)); setError(''); } catch (e) { setError(e.message); } }}><UiText>Load history</UiText></button>{error && <p role="alert">{error}</p>}{data && <div className="org-table-scroll"><table><thead><tr><th>ID</th><th><UiText>Project</UiText></th><th><UiText>Team</UiText></th><th><UiText>Start</UiText></th><th><UiText>End</UiText></th><th><UiText>Status</UiText></th></tr></thead><tbody>{data.items.map((row) => <tr key={row.id}>{['id','project_id','team_id','effective_start','effective_end','status'].map((key) => <td key={key}>{row[key] || 'Open'}</td>)}</tr>)}</tbody></table></div>}</details>;
}

export default function AssignmentControls({ onReload }) {
  const reload = async (promise) => { await promise; if (onReload) await onReload(); };
  return <section className="org-controls"><h2><UiText>Explicit organization assignments</UiText></h2><p className="org-muted"><UiText>Select records, then save. Transfers close the prior allocation and preserve its history. Teams with execution history retain their project.</UiText></p><ActionForm title="Assign or replace a Project Manager" fields={['project_id','account_id']} submit={(v) => reload(workflowApi.assignProjectManager(v.project_id, v.account_id))} /><ActionForm title="Assign or replace a Team Leader" fields={['team_id','account_id']} submit={(v) => reload(workflowApi.assignTeamLeader(v.team_id, v.account_id))} /><ActionForm title="Assign a team to a project" fields={['project_id','team_id']} submit={(v) => reload(workflowApi.assignTeam(v.project_id, v.team_id))} /><ActionForm title="Allocate or transfer workforce" fields={['employee_id','project_id','team_id','effective_start']} checkbox="transfer" submit={(v) => api.allocate({ ...v, transfer:v.transfer || false })} /><ActionForm title="End a workforce allocation" fields={['allocation_id','effective_end']} submit={(v) => api.end(v.allocation_id, v.effective_end)} /><History /><ActionForm title="Add project member" fields={['project_id','employee_id','responsibility']} submit={api.membership} /><ActionForm title="Add participating department" fields={['project_id','department_id']} submit={api.membership} /><ActionForm title="Assign employee skill" fields={['employee_id','skill_id']} submit={api.skill} /></section>;
}

export function CapabilityControls() {
  const [grants, setGrants] = useState(null);
  const [error, setError] = useState('');
  return <section className="org-controls"><h2><UiText>Department responsibilities</UiText></h2><p className="org-muted"><UiText>Designation and department membership do not grant application access. Confidential HR access is a separate, explicit responsibility.</UiText></p><ActionForm title="Grant or revoke department capability" fields={['account_id']} options={['business','materials','people','quality','hse','hr-confidential']} checkbox="revoke" submit={(v) => api.grant({ user_id:v.account_id, capability:v.capability, granted:!v.revoke })} /><button type="button" onClick={async () => { try { setGrants(await api.grants()); } catch (e) { setError(e.message); } }}><UiText>View explicit grants</UiText></button>{error && <p role="alert">{error}</p>}{grants && <ul>{grants.items.map((g) => <li key={g.user_id+g.capability}>{g.user_id} · {g.capability}</li>)}</ul>}</section>;
}
