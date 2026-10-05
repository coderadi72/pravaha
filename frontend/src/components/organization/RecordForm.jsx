import UiText from "../../ui/UiText.jsx";
import { useEffect, useId, useState } from 'react';
import { organizationApi as api } from '../../api/organization.js';

import { label } from '../../utils/organization.js';
const REFERENCES = { department_id:'departments', unit_id:'units', location_id:'locations', designation_id:'designations', manager_id:'employees', account_id:'accounts', employee_id:'employees', assigned_employee_id:'employees', client_id:'clients', opportunity_id:'opportunities', tender_id:'tenders', proposal_id:'proposals', project_id:'projects', team_id:'teams', material_id:'materials', vendor_id:'vendors', store_id:'stores', request_id:'material-requests', order_id:'purchase-orders', inspection_id:'inspections', quality_issue_id:'quality-issues', safety_event_id:'safety', skill_id:'skills' };

export function ReferenceField({ name, value, onChange, required = false }) {
  const resource = REFERENCES[name];
  const [query, setQuery] = useState('');
  const [rows, setRows] = useState([]);
  const [error, setError] = useState('');
  const listId = useId();
  useEffect(() => {
    let active = true;
    const timer = setTimeout(() => {
      const request = ['accounts','projects','teams'].includes(resource) ? api.lookup(resource, query) : resource === 'employees' ? api.roster(query) : api.list(resource, query);
      request.then((result) => { if (active) { setRows(result.items); setError(''); } }).catch((e) => { if (active) setError(e.message); });
    }, 200);
    return () => { active = false; clearTimeout(timer); };
  }, [resource, query]);
  return <fieldset className="org-reference"><legend><UiText>{label(name)}</UiText>{required ? ' *' : ''}</legend><input aria-label={`Search ${label(name)}`} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search names or identifiers" /><input name={name} aria-label={label(name)} list={listId} value={value || ''} onChange={(e) => onChange(e.target.value)} required={required} placeholder="Select or enter a valid ID" /><datalist id={listId}>{rows.map((r) => <option key={r.id} value={r.id}>{r.name || r.title || r.workforce_code || r.id}</option>)}</datalist>{error && <small role="status">{error}</small>}</fieldset>;
}

export default function RecordForm({ resource, initial, onSave, onCancel, role, confidentialAccess }) {
  const [values, setValues] = useState(() => Object.fromEntries(resource.fields.filter((f) => initial?.[f.name] !== undefined || f.type === 'Boolean').map((f) => [f.name, initial?.[f.name] ?? (f.type === 'Boolean' ? true : null)])));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const set = (name, value) => setValues((old) => ({ ...old, [name]: value }));
  const submit = async (event) => {
    event.preventDefault();
    const submitted = { ...values };
    const native = new FormData(event.currentTarget);
    resource.fields.filter((field) => field.type === 'Date').forEach((field) => { submitted[field.name] = native.get(field.name) || null; });
    setValues(submitted); setBusy(true); setError('');
    try { await onSave(submitted); } catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  return <form className="org-form" onSubmit={submit}><h3><UiText>{initial ? 'Edit' : 'Create'}</UiText> <UiText>{label(resource.key)}</UiText></h3><div className="org-form-grid">{resource.fields.map((field) => {
    const { name, type, required } = field;
    if (REFERENCES[name]) return <ReferenceField key={name} name={name} value={values[name]} onChange={(value) => set(name, value)} required={required} />;
    let choices = null;
    if (name === 'kind') choices = resource.key === 'people' ? (role === 'TEAM_LEADER' ? ['attendance'] : ['recruitment','attendance','leave','training', ...(confidentialAccess ? ['performance','employee-relations','grievance','wellbeing'] : [])]) : resource.key === 'safety' ? ['OBSERVATION','INCIDENT'] : ['ISSUE','NCR'];
    return <label key={name}><UiText>{label(name)}</UiText>{required ? ' *' : ''}{choices ? <select value={values[name] || ''} onChange={(e) => set(name, e.target.value)} required={required}><option value=""><UiText>Choose</UiText></option>{choices.map((choice) => <option key={choice}>{choice}</option>)}</select> : type === 'Boolean' ? <select value={String(values[name] ?? true)} onChange={(e) => set(name, e.target.value === 'true')}><option value="true"><UiText>Active</UiText></option><option value="false"><UiText>Inactive</UiText></option></select> : name === 'narrative' ? <textarea maxLength={2000} value={values[name] || ''} onChange={(e) => set(name, e.target.value)} /> : <input name={name} type={type === 'Date' ? 'date' : type === 'Numeric' ? 'number' : 'text'} step={type === 'Numeric' ? '0.001' : undefined} min={type === 'Numeric' ? 0 : undefined} value={values[name] ?? ''} maxLength={500} onChange={(e) => set(name, e.target.value)} required={required} />}</label>;
  })}</div>{resource.key === 'people' && <p className="org-muted"><UiText>Confidential cases require explicitly granted HR access. Enter only the information needed for this workflow.</UiText></p>}{error && <p role="alert">{error}</p>}<div className="org-actions"><button type="submit" disabled={busy}><UiText>{busy ? 'Saving…' : 'Save record'}</UiText></button><button type="button" onClick={onCancel} disabled={busy}><UiText>Cancel</UiText></button></div></form>;
}
