import UiText from "../../ui/UiText.jsx";
import { useCallback, useEffect, useState } from 'react';
import { organizationApi as api } from '../../api/organization.js';
import RecordForm from './RecordForm.jsx';
import { label } from '../../utils/organization.js';

export default function ResourceTable({ resource, context, roster = false }) {
  const [query, setQuery] = useState('');
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(null);
  const [detail, setDetail] = useState(null);
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => {
    setLoading(true); setError('');
    try { setData(await (roster ? api.roster(query, offset) : api.list(resource.key, query, offset))); }
    catch (e) { setError(e.message); setData(null); }
    finally { setLoading(false); }
  }, [resource.key, roster, query, offset]);
  useEffect(() => { let active = true; const timer = setTimeout(() => { if (active) load(); }, 200); return () => { active = false; clearTimeout(timer); }; }, [load]);
  const action = async (operation) => {
    setBusy(true); setError('');
    try { await operation(); setNotice('Saved to PostgreSQL.'); setDetail(null); await load(); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  const save = async (values) => { await (form?.id ? api.edit(resource.key, form.id, values) : api.create(resource.key, values)); setForm(null); setNotice('Record saved.'); await load(); };
  const showDetail = async (id) => {
    setBusy(true); setError('');
    try { setDetail(await api.detail(resource.key, id)); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  const columns = roster ? ['workforce_code','name','discipline','department_id','assignment','skills'] : ['id', ...resource.fields.map((f) => f.name).filter((f) => f !== 'narrative').slice(0,5), ...(resource.transitions && Object.keys(resource.transitions).length ? ['status'] : [])];
  return <section className="org-panel" aria-label={roster ? 'Workforce roster' : label(resource.key)}><div className="org-section-heading"><div><span className="org-kicker">{roster ? 'WORKFORCE' : resource.capability.toUpperCase()}</span><h2>{roster ? 'Employees and workforce' : label(resource.key)}</h2></div>{resource.canCreate && <button type="button" onClick={() => { setDetail(null); setForm({}); }}><UiText>Create record</UiText></button>}</div><div className="org-toolbar"><label><UiText>Search</UiText><input value={query} onChange={(e) => { setQuery(e.target.value); setOffset(0); }} placeholder="Name, title or identifier" /></label><span>{data?.total ?? '—'}<UiText> records · </UiText>{context.dataLabel}</span></div>{notice && <p role="status">{notice}</p>}{error && <div role="alert"><p>{error}</p><button type="button" onClick={load}><UiText>Retry</UiText></button></div>}{form && <RecordForm key={form.id || 'new'} resource={resource} initial={form.id ? form : null} role={context.role} confidentialAccess={context.confidentialAccess} onSave={save} onCancel={() => setForm(null)} />}{detail && <section className="org-detail"><h3><UiText>Record details</UiText></h3><dl>{Object.entries(detail).map(([key,value]) => <div key={key}><dt><UiText>{label(key)}</UiText></dt><dd>{typeof value === 'object' ? JSON.stringify(value) : String(value ?? 'Not available')}</dd></div>)}</dl><button type="button" onClick={() => setDetail(null)}><UiText>Close details</UiText></button></section>}{loading ? <p role="status"><UiText>Loading records…</UiText></p> : data?.items.length ? <div className="org-table-scroll" tabIndex={0} aria-label="Scrollable records"><table><thead><tr>{columns.map((column) => <th key={column}><UiText>{label(column)}</UiText></th>)}<th><UiText>Actions</UiText></th></tr></thead><tbody>{data.items.map((row) => <tr key={row.id}>{columns.map((column) => <td key={column}>{column === 'assignment' ? row.assignment ? `${row.assignment.project_id} · ${row.assignment.team_id}` : 'Unallocated' : column === 'skills' ? row.skills.join(', ') || 'Not recorded' : String(row[column] ?? 'Not available')}</td>)}<td><div className="org-row-actions">{!roster && <button type="button" disabled={busy} onClick={() => showDetail(row.id)}><UiText>Details</UiText></button>}{resource.canEdit && <button type="button" onClick={() => setForm(row)}><UiText>Edit</UiText></button>}{resource.canReview && (resource.transitions?.[row.status] || []).filter((state) => state !== 'HIRED' || row.kind === 'recruitment').map((state) => <button key={state} type="button" disabled={busy} onClick={() => action(() => api.transition(resource.key, row.id, state))}><UiText>{label(state)}</UiText></button>)}</div></td></tr>)}</tbody></table></div> : !error && <p><UiText>No records found. </UiText>{resource.canCreate ? 'Create a record to begin this workflow.' : 'Records will appear when authorized staff capture them.'}</p>}<div className="org-pagination"><button type="button" disabled={loading || offset === 0} onClick={() => setOffset(Math.max(0, offset-25))}><UiText>Previous</UiText></button><span>{offset+1}–{Math.min(offset+25, data?.total || 0)}<UiText> of </UiText>{data?.total || 0}</span><button type="button" disabled={loading || offset+25 >= (data?.total || 0)} onClick={() => setOffset(offset+25)}><UiText>Next</UiText></button></div></section>;
}
