import { apiRequest } from './client.js';
const json = (body) => JSON.stringify(body);
export const organizationApi = {
  context: () => apiRequest('/api/organization/context'),
  overview: () => apiRequest('/api/organization/overview'),
  analytics: () => apiRequest('/api/organization/analytics'),
  list: (resource, q = '', offset = 0) => apiRequest(`/api/modules/${encodeURIComponent(resource)}?${new URLSearchParams({ q, offset, limit: 25 })}`),
  lookup: (resource, q = '') => apiRequest(`/api/organization/lookups/${resource}?${new URLSearchParams({ q, limit: 25 })}`),
  roster: (q = '', offset = 0) => apiRequest(`/api/organization/roster?${new URLSearchParams({ q, offset, limit: 25 })}`),
  detail: (resource, id) => apiRequest(`/api/modules/${resource}/${encodeURIComponent(id)}`),
  create: (resource, values) => apiRequest(`/api/modules/${resource}`, { method: 'POST', body: json({ values }) }),
  edit: (resource, id, values) => apiRequest(`/api/modules/${resource}/${encodeURIComponent(id)}`, { method: 'PATCH', body: json({ values }) }),
  transition: (resource, id, status) => apiRequest(`/api/modules/${resource}/${encodeURIComponent(id)}/transition`, { method: 'POST', body: json({ status }) }),
  allocate: (body) => apiRequest('/api/organization/allocations', { method: 'POST', body: json(body) }),
  history: (id) => apiRequest(`/api/organization/allocations/${encodeURIComponent(id)}`),
  end: (id, effective_end) => apiRequest(`/api/organization/allocations/${encodeURIComponent(id)}/end`, { method: 'POST', body: json({ effective_end }) }),
  grant: (body) => apiRequest('/api/organization/grants', { method: 'POST', body: json(body) }),
  grants: () => apiRequest('/api/organization/grants'),
  membership: (body) => apiRequest('/api/organization/memberships', { method: 'POST', body: json(body) }),
  members: (id) => apiRequest(`/api/organization/memberships/${encodeURIComponent(id)}`),
  skill: (body) => apiRequest('/api/organization/skills', { method: 'POST', body: json(body) }),
  createTeam: (body) => apiRequest('/api/organization/teams', { method:'POST', body:json(body) }),
  stock: (q = '', offset = 0) => apiRequest(`/api/organization/stock?${new URLSearchParams({ q, offset, limit:25 })}`),
};
