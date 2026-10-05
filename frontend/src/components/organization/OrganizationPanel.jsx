import UiText from "../../ui/UiText.jsx";
import { useEffect, useState } from 'react';
import { organizationApi as api } from '../../api/organization.js';
import StockPanel from "./StockPanel.jsx";
import ResourceTable from './ResourceTable.jsx';
import '../../styles/organization.css';

const GROUPS = { Departments:'organization', Business:'business', Materials:'materials', People:'people', Quality:'quality', HSE:'hse' };

function Overview() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { let active = true; api.overview().then((r) => { if (active) setData(r); }).catch((e) => { if (active) setError(e.message); }); return () => { active = false; }; }, []);
  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status"><UiText>Loading organization…</UiText></p>;
  return <section className="org-panel"><span className="org-kicker"><UiText>ORGANIZATION HEALTH · </UiText>{data.dataLabel}</span><h2><UiText>Portfolio and workforce allocation</UiText></h2><div className="org-metrics">{['projects','teams','departments','employees','workers','allocatedWorkers'].map((key) => <div key={key}><span><UiText>{key.replace(/([A-Z])/g, ' $1')}</UiText></span><strong>{data[key]}</strong></div>)}</div><h3><UiText>Attention required</UiText></h3>{data.attention.length ? <ul>{data.attention.map((item) => <li key={item.id}><strong>{item.id}</strong> · {item.reason}</li>)}</ul> : <p><UiText>No recorded attention items.</UiText></p>}<p className="org-muted"><UiText>Execution detail is available in each project. These counts come from persisted organization and assignment records.</UiText></p></section>;
}

export default function OrganizationPanel({ view = 'Support' }) {
  const [context, setContext] = useState(null);
  const [selected, setSelected] = useState('');
  const [error, setError] = useState('');
  useEffect(() => { let active = true; api.context().then((r) => { if (active) setContext(r); }).catch((e) => { if (active) setError(e.message); }); return () => { active = false; }; }, []);
  if (error) return <p role="alert">{error}</p>;
  if (!context) return <p role="status"><UiText>Loading permissions…</UiText></p>;
  if (view === 'Overview') return <Overview />;
  const resources = context.resources.filter((r) => !GROUPS[view] || r.capability === GROUPS[view] || (view === 'HSE' && r.key === 'corrective-actions'));
  if (view === 'Workers' || view === 'Roster') return <ResourceTable resource={context.resources.find((r) => r.key === 'employees') || { key:'employees', fields:[], canCreate:false }} context={context} roster />;
  const resource = resources.find((r) => r.key === selected) || resources[0];
  return <div className="org-console"><p className="org-muted">{context.dataLabel}<UiText> · Access is enforced by the API. </UiText>{context.confidentialAccess ? 'Explicit confidential HR responsibility granted.' : 'Confidential HR case records are excluded.'}</p><label className="org-resource-select"><UiText>Workflow</UiText><select value={resource?.key || ''} onChange={(e) => setSelected(e.target.value)}>{resources.map((r) => <option key={r.key} value={r.key}>{r.key.replaceAll('-', ' ')}</option>)}</select></label>{resource ? <><ResourceTable key={resource.key} resource={resource} context={context} />{resource.capability === "materials" && (context.role === "ADMIN" || context.capabilities.includes("materials")) && <StockPanel />}</> : <p><UiText>No departmental responsibilities have been granted. Contact your organization administrator.</UiText></p>}</div>;
}
