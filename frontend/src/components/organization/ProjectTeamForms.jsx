import UiText from "../../ui/UiText.jsx";
import { useState } from 'react';
import { organizationApi } from '../../api/organization.js';
import { ingestionApi } from '../../api/client.js';
import { ReferenceField } from './RecordForm.jsx';

export default function ProjectTeamForms({ kind, onReload }) {
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [project, setProject] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const save = async (event) => {
    event.preventDefault(); setBusy(true); setMessage('');
    try {
      const result = await (kind === 'team' ? organizationApi.createTeam({ name, site:location, project_id:project }) : ingestionApi.createProject({ name, location }));
      setMessage(`Created ${result.id || result.project.id}. Assign enabled management accounts before allocating workforce.`);
      setName(''); setLocation(''); if (onReload) await onReload();
    } catch (e) { setMessage(e.message); } finally { setBusy(false); }
  };
  return <details className="org-controls"><summary><UiText>Create </UiText>{kind}</summary><form className="org-form" onSubmit={save}><div className="org-form-grid"><label><UiText>Name</UiText><input required maxLength={120} value={name} onChange={(e) => setName(e.target.value)} /></label><label><UiText>Site / location</UiText><input maxLength={120} value={location} onChange={(e) => setLocation(e.target.value)} /></label>{kind === 'team' && <ReferenceField name="project_id" value={project} onChange={setProject} required />}</div><div className="org-actions"><button disabled={busy} type="submit">{busy ? 'Creating…' : 'Create '+kind}</button></div>{message && <p role="status">{message}</p>}</form></details>;
}
