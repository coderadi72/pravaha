import test from "node:test";
import assert from "node:assert/strict";
import { resolveApiUrl } from "../frontend/src/api/config.js";
import { apiRequest, ApiError } from "../frontend/src/api/client.js";
import { getTeamActivities } from "../frontend/src/utils/workspace.js";

test("API host changes require configuration only, with no duplicate /api prefix", () => {
  for (const base of ["https://api.example.invalid/api", "http://192.0.2.1:8000/api/", "/api"]) {
    assert.equal(resolveApiUrl("/api/auth/me", base), `${base.replace(/\/+$/, "")}/auth/me`);
  }
});

test("missing or unsafe frontend API configuration fails clearly", () => {
  for (const value of [undefined, "", "ftp://api.example.invalid/api", "//api.example.invalid/api"]) assert.throws(() => resolveApiUrl("/api/auth/me", value));
  assert.throws(() => resolveApiUrl("https://external.invalid/", "/api"));
});

test("central client sends cookies and JSON and handles structured errors", async () => {
  const originalFetch = globalThis.fetch;
  try {
    globalThis.fetch = async (url, options) => {
      assert.equal(url, "https://api.example.invalid/api/auth/login");
      assert.equal(options.credentials, "include");
      assert.equal(options.headers["Content-Type"], "application/json");
      return { ok: false, status: 401, json: async () => ({ error: { code: "INVALID_CREDENTIALS", message: "Email or password is incorrect." } }) };
    };
    await assert.rejects(apiRequest("/api/auth/login", { method: "POST", body: "{}" }, "https://api.example.invalid/api"), (error) => error instanceof ApiError && error.status === 401 && error.code === "INVALID_CREDENTIALS");
  } finally { globalThis.fetch = originalFetch; }
});

test("client reports configuration, connection, and unreadable response errors", async () => {
  const originalFetch = globalThis.fetch;
  try {
    await assert.rejects(apiRequest("/api/auth/me", {}, ""), (error) => error.code === "CONFIGURATION_ERROR");
    globalThis.fetch = async () => { throw new Error("offline"); };
    await assert.rejects(apiRequest("/api/auth/me", {}, "/api"), (error) => error.code === "NETWORK_ERROR");
    globalThis.fetch = async () => ({ status: 502, json: async () => { throw new Error("html"); } });
    await assert.rejects(apiRequest("/api/auth/me", {}, "/api"), (error) => error.code === "INVALID_RESPONSE");
  } finally { globalThis.fetch = originalFetch; }
});

test("frontend selector preserves assigned scope and planned time display", () => {
  const data = { teams: [{ id: "T1", projectId: "P1" }, { id: "T2", projectId: null }], scheduleActivities: [
    { id: "A1", teamId: "T1", projectId: "P1", plannedStartTime: "08:00", plannedEndTime: "14:00" },
    { id: "A2", teamId: "T1", projectId: "P2" },
  ] };
  assert.deepEqual(getTeamActivities(data, "T1"), [{ ...data.scheduleActivities[0], plannedStart: "08:00", plannedEnd: "14:00" }]);
  assert.deepEqual(getTeamActivities(data, "T2"), []);
  assert.deepEqual(getTeamActivities(data, "missing"), []);
});
