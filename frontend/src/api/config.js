export function resolveApiUrl(path, configuredBase = import.meta.env?.VITE_API_BASE_URL) {
  if (typeof configuredBase !== "string" || !configuredBase.trim()) throw new Error("Set VITE_API_BASE_URL in the frontend environment before starting or building PRAVAHA.");
  const base = configuredBase.trim().replace(/\/+$/, "");
  if (!base.startsWith("/") && !/^https?:\/\//i.test(base)) throw new Error("VITE_API_BASE_URL must be an HTTP(S) URL or a relative API path.");
  if (base.startsWith("//")) throw new Error("VITE_API_BASE_URL must not be a protocol-relative URL.");
  if (!path.startsWith("/api/")) throw new Error("API request paths must start with /api/.");
  return `${base}${path.slice(4)}`;
}
