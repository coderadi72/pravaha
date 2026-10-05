import { resolveApiUrl } from "./config.js";

const UPLOAD_MAX_BYTES = Number(import.meta.env?.VITE_ATTACHMENT_MAX_BYTES || 5 * 1024 * 1024);

export class ApiError extends Error {
  constructor(status, code, message) { super(message); this.status = status; this.code = code; }
}

export async function apiRequest(path, options = {}, configuredBase) {
  let url;
  try { url = resolveApiUrl(path, configuredBase); }
  catch (error) { throw new ApiError(0, "CONFIGURATION_ERROR", error.message); }
  let response;
  try {
    response = await fetch(url, {
      ...options,
      credentials: "include",
      headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers },
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError(0, "NETWORK_ERROR", "Cannot reach PRAVAHA. Check that the local API server is running.");
  }
  let body;
  try { body = await response.json(); }
  catch { throw new ApiError(response.status, "INVALID_RESPONSE", "The server returned an unreadable response."); }
  if (!response.ok) throw new ApiError(response.status, body.error?.code ?? "REQUEST_FAILED", body.error?.message ?? "The request could not be completed.");
  return body;
}

export const authApi = {
  login: (credentials) => apiRequest("/api/auth/login", { method: "POST", body: JSON.stringify(credentials) }),
  signup: (registration, configuredBase) => apiRequest("/api/auth/signup", { method: "POST", body: JSON.stringify(registration) }, configuredBase),
  me: () => apiRequest("/api/auth/me"),
  logout: () => apiRequest("/api/auth/logout", { method: "POST", body: "{}" }),
};

export const registrationApi = {
  list: ({ status = "PENDING", offset = 0 } = {}) => apiRequest(`/api/admin/registrations?${new URLSearchParams({ ...(status ? { status } : {}), offset: String(offset) })}`),
  approve: (id, approvedRole, configuredBase) => apiRequest(`/api/admin/registrations/${encodeURIComponent(id)}/approve`, { method: "POST", body: JSON.stringify({ approvedRole }) }, configuredBase),
  reject: (id, rejectionReason, configuredBase) => apiRequest(`/api/admin/registrations/${encodeURIComponent(id)}/reject`, { method: "POST", body: JSON.stringify({ rejectionReason }) }, configuredBase),
};

export const workflowApi = {
  workspace: () => apiRequest("/api/workspace"),
  assignProjectManager: (projectId, projectManagerId) => apiRequest(`/api/admin/projects/${encodeURIComponent(projectId)}/manager`, { method: "PATCH", body: JSON.stringify({ projectManagerId }) }),
  assignTeam: (projectId, teamId, assigned = true) => apiRequest(`/api/admin/teams/${encodeURIComponent(teamId)}/assignment`, { method: "PATCH", body: JSON.stringify({ projectId, assigned }) }),
  assignTeamLeader: (teamId, teamLeaderId) => apiRequest(`/api/admin/teams/${encodeURIComponent(teamId)}/leader`, { method: "PATCH", body: JSON.stringify({ teamLeaderId }) }),
  createUser: (payload) => apiRequest("/api/admin/users", { method: "POST", body: JSON.stringify(payload) }),
  submitFieldUpdate: (payload) => apiRequest("/api/team-leader/field-updates", { method: "POST", body: JSON.stringify(payload) }),
  recordActivityAction: (activityId, action, details) => apiRequest(`/api/team-leader/activities/${encodeURIComponent(activityId)}/actions`, { method: "POST", body: JSON.stringify({ action, details }) }),
  requestPlannerReview: (updateId) => apiRequest(`/api/reviews/${encodeURIComponent(updateId)}/request-review`, { method: "POST", body: "{}" }),
  decideReview: (updateId, decision, scheduleActivityId, reason, feedback) => {
    const path = { confirm: "confirm", change: "change-match", unmatched: "unmatch", feedback: "request-info" }[decision];
    if (!path) throw new ApiError(400, "INVALID_REVIEW", "Review decision is invalid.");
    return apiRequest(`/api/reviews/${encodeURIComponent(updateId)}/${path}`, { method: "POST", body: JSON.stringify({ scheduleActivityId, reason, feedback }) });
  },
};


export const intelligenceApi = {
  portfolio: (offset = 0) => apiRequest(`/api/intelligence/portfolio?offset=${offset}`),
  project: (id, offset = 0) => apiRequest(`/api/intelligence/projects/${encodeURIComponent(id)}?offset=${offset}`),
  refresh: (id) => apiRequest(`/api/intelligence/projects/${encodeURIComponent(id)}/refresh`, { method: "POST", body: "{}" }),
  acknowledge: (id, warningId) => apiRequest(`/api/intelligence/projects/${encodeURIComponent(id)}/warnings/${encodeURIComponent(warningId)}/acknowledge`, { method: "PATCH", body: "{}" }),
  memory: (id, params) => apiRequest(`/api/intelligence/projects/${encodeURIComponent(id)}/memory?${new URLSearchParams(params)}`),
};


export const ingestionApi = {
  preview: (id, body) => apiRequest(`/api/projects/${encodeURIComponent(id)}/imports/preview`, { method: "POST", body: JSON.stringify(body) }),
  commit: (id, body) => apiRequest(`/api/projects/${encodeURIComponent(id)}/imports/commit`, { method: "POST", body: JSON.stringify(body) }),
  versions: (id, offset = 0) => apiRequest(`/api/projects/${encodeURIComponent(id)}/schedule-versions?offset=${offset}`),
  compare: (id, before, after) => apiRequest(`/api/projects/${encodeURIComponent(id)}/schedule-versions/compare?${new URLSearchParams({ before_id: before, after_id: after })}`, { method: "POST", body: "{}" }),
  upload: (id, body) => apiRequest(`/api/field-updates/${encodeURIComponent(id)}/attachments`, { method: "POST", body: JSON.stringify(body) }),
  attachments: (id) => apiRequest(`/api/field-updates/${encodeURIComponent(id)}/attachments`),
  process: (id, provider) => apiRequest(`/api/attachments/${encodeURIComponent(id)}/process`, { method: "POST", body: JSON.stringify({ provider }) }),
  search: (q, kind, offset = 0) => apiRequest(`/api/search?${new URLSearchParams({ q, kind, offset: String(offset) })}`),
  system: () => apiRequest("/api/admin/system"),
  createProject: (body) => apiRequest("/api/admin/projects", { method: "POST", body: JSON.stringify(body) }),
};

export function filePayload(file) {
  if (file.size > UPLOAD_MAX_BYTES) return Promise.reject(new Error(`Files must be at most ${Math.floor(UPLOAD_MAX_BYTES / (1024 * 1024))} MiB.`));
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("The selected file could not be read."));
    reader.onload = () => resolve({ filename: file.name, contentBase64: reader.result.split(",")[1] });
    reader.readAsDataURL(file);
  });
}
