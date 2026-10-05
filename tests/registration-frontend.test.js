import assert from "node:assert/strict";
import test from "node:test";
import { signupDomain, signupEmailState, signupErrorMessage, validateSignup } from "../frontend/src/components/auth/registration.js";
import { authApi, registrationApi } from "../frontend/src/api/client.js";
import { translate } from "../frontend/src/ui/translations.js";

const valid = { name: "Rahul Sharma", email: "rahul@pravaha.management.com", password: "ApprovedPass123!", confirmPassword: "ApprovedPass123!", roleCategory: "MANAGEMENT" };

test("registration domain eligibility is exact, category-specific and case-insensitive", () => {
  assert.equal(signupDomain("MANAGEMENT"), "pravaha.management.com");
  assert.equal(signupDomain("SUPERVISOR"), "pravaha.supervisor.com");
  assert.equal(signupEmailState(" RAHUL@PRAVAHA.MANAGEMENT.COM ", "MANAGEMENT").normalized, "rahul@pravaha.management.com");
  assert.equal(signupEmailState(valid.email, "MANAGEMENT").valid, true);
  assert.equal(signupEmailState("amit@pravaha.supervisor.com", "SUPERVISOR").valid, true);
  for (const email of ["rahul@gmail.com", "rahul@yahoo.com", "rahul@outlook.com", "rahul@pravaha.com", "rahul@pravaha.management.com.attacker.com", "rahul@pravaha.supervisor.com", "rahul@@pravaha.management.com", "rahul..sharma@pravaha.management.com", ".rahul@pravaha.management.com", "rahul sharma@pravaha.management.com"]) {
    assert.equal(signupEmailState(email, "MANAGEMENT").valid, false, email);
  }
  assert.equal(signupEmailState(valid.email, "SUPERVISOR").valid, false);
  assert.equal(signupEmailState(valid.email, "ADMIN").valid, false);
});

test("signup validation enforces all fields, the existing strong policy and matching passwords", () => {
  assert.equal(validateSignup(valid), "");
  for (const field of ["name", "email", "password", "confirmPassword"]) assert.notEqual(validateSignup({ ...valid, [field]: "" }), "");
  for (const password of ["Short9!", "lowercase123!", "UPPERCASE123!", "NoNumbersHere!", "NoSpecial12345", "A".repeat(129) + "a1!"]) {
    assert.notEqual(validateSignup({ ...valid, password, confirmPassword: password }), "");
  }
  assert.equal(validateSignup({ ...valid, confirmPassword: "DifferentPass123!" }), "Passwords do not match");
  const untouched = "  ApprovedPass123!  ";
  assert.equal(validateSignup({ ...valid, password: untouched, confirmPassword: untouched }), "");
});

test("registration errors hide implementation details and new copy uses the existing Hindi catalogue", () => {
  const internal = { code: "INTERNAL_ERROR", message: "postgresql secret internal traceback" };
  assert.equal(signupErrorMessage(internal), "Registration could not be completed. Please try again later.");
  assert.equal(signupErrorMessage({ code: "NETWORK_ERROR" }), "Unable to connect. Please try again.");
  assert.equal(signupErrorMessage({ code: "RATE_LIMITED" }), "Too many registration attempts. Try again later.");
  for (const label of ["Pending registration", "Registrations", "Authorized Management email", "At least 12 characters", "Submitting…", "Approve", "Rejection reason"]) assert.notEqual(translate(label, "hi"), label);
  assert.equal(translate("rahul@pravaha.management.com", "hi"), "rahul@pravaha.management.com");
});

test("signup and Admin review use the central cookie-aware API client with safe payloads", async () => {
  const originalFetch = globalThis.fetch;
  const requests = [];
  globalThis.fetch = async (url, options) => {
    requests.push({ url, options });
    return { ok: true, status: 202, json: async () => ({ status: "SUBMITTED", message: "Submitted" }) };
  };
  try {
    await authApi.signup(valid, "/api");
    assert.equal(requests[0].url, "/api/auth/signup");
    assert.equal(requests[0].options.credentials, "include");
    assert.deepEqual(JSON.parse(requests[0].options.body), valid);
    await registrationApi.approve("REG/1", "PROJECT_MANAGER", "/api");
    assert.equal(requests[1].url, "/api/admin/registrations/REG%2F1/approve");
    assert.deepEqual(JSON.parse(requests[1].options.body), { approvedRole: "PROJECT_MANAGER" });
    await registrationApi.reject("REG/2", "Unable to approve", "/api");
    assert.deepEqual(JSON.parse(requests[2].options.body), { rejectionReason: "Unable to approve" });
    assert.equal(requests[2].options.credentials, "include");
  } finally { globalThis.fetch = originalFetch; }
});
