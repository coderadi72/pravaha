import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { label } from '../frontend/src/utils/organization.js';

const source = (path) => readFileSync(new URL('../frontend/src/'+path, import.meta.url), 'utf8');

test('organization labels remain readable for references and workflow states', () => {
  assert.equal(label('project_id'), 'project ID');
  assert.equal(label('material-requests'), 'material requests');
});

test('organization controls persist assignments only after explicit form submission', () => {
  const control = source('components/organization/AssignmentControls.jsx');
  assert.match(control, /onSubmit=\{save\}/);
  assert.match(control, /Save assignment/);
  assert.doesNotMatch(source('pages/dashboard/AdminDashboard.jsx'), /onChange=.*updateAssignment/);
});

test('workforce and departmental roles are handled before legacy workspace rendering', () => {
  const app = source('App.jsx');
  assert.ok(app.indexOf('user.role === "WORKFORCE"') < app.indexOf('if (!workflowData)'));
  assert.match(app, /\["WORKFORCE", "DEPARTMENT"\]\.includes\(authenticatedUser.role\)/);
  assert.match(source('components/auth/AuthModal.jsx'), /Work email or login ID/);
});

test('organization edit form sends allowed fields and excludes record IDs and roster metadata', () => {
  const form = source('components/organization/RecordForm.jsx');
  assert.match(form, /Object\.fromEntries\(resource\.fields/);
  assert.doesNotMatch(form, /useState\(initial \|\| \{\}\)/);
  assert.match(source('components/organization/ResourceTable.jsx'), /offset\+25/);
  assert.match(source('components/organization/RecordForm.jsx'), /Search names or identifiers/);
});

test('TL shows an accepted schedule link independently of matcher confidence', () => {
  assert.match(source('pages/dashboard/TeamLeaderDashboard.jsx'), /match\?\.matchStatus === "matched" \? "PM-confirmed schedule link"/);
});
