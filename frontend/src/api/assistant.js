import { apiRequest } from "./client.js";
export const assistantApi = {
  contexts: (offset = 0, signal) => apiRequest(`/api/assistant/contexts?offset=${offset}`, { signal }),
  ask: (body, signal) => apiRequest("/api/assistant/ask", { method: "POST", body: JSON.stringify(body), signal }),
  source: (path, signal) => {
    if (!path.startsWith("/api/assistant/source?reference=")) throw new Error("Invalid assistant source route.");
    return apiRequest(path, { signal });
  },
};
