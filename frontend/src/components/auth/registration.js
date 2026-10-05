const domains = {
  MANAGEMENT: "pravaha.management.com",
  SUPERVISOR: "pravaha.supervisor.com",
};

export function signupDomain(category) {
  return domains[category] ?? "";
}

export function signupEmailState(email, category) {
  const normalized = email.trim().toLowerCase();
  const parts = normalized.split("@");
  const local = parts[0];
  const domain = parts[1];
  const wellFormed = normalized.length <= 254 && parts.length === 2 && local.length > 0 && local.length <= 64
    && /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+$/i.test(local)
    && !local.startsWith(".") && !local.endsWith(".") && !local.includes("..");
  const valid = Boolean(wellFormed && domains[category] && domain === domains[category]);
  return {
    valid,
    normalized,
    message: valid
      ? category === "MANAGEMENT" ? "Authorized Management email" : "Authorized Supervisor email"
      : category === "MANAGEMENT" ? "Please use your authorized PRAVAHA Management email." : "Please use your authorized PRAVAHA Supervisor email.",
  };
}

export function validateSignup({ name, email, password, confirmPassword, roleCategory }) {
  if (!name.trim()) return "Full name is required.";
  if (!email.trim()) return "Work email is required.";
  if (!signupEmailState(email, roleCategory).valid) return "This email domain is not valid for the selected role.";
  if (!password) return "Password is required.";
  if (password.length < 12 || password.length > 128 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password) || !/[^A-Za-z0-9]/.test(password)) {
    return "Password must be 12-128 characters and include uppercase, lowercase, number, and special character.";
  }
  if (password !== confirmPassword) return "Passwords do not match";
  return "";
}

export function signupErrorMessage(error) {
  const messages = {
    UNAUTHORIZED_EMAIL: "Please use your authorized PRAVAHA work email.",
    INVALID_EMAIL_DOMAIN: "This email domain is not valid for the selected role.",
    INVALID_EMAIL: "Email address is invalid.",
    WEAK_PASSWORD: "Password must be 12-128 characters and include uppercase, lowercase, number, and special character.",
    PASSWORD_MISMATCH: "Passwords do not match",
    RATE_LIMITED: "Too many registration attempts. Try again later.",
    DUPLICATE_EMAIL: "If an account or registration already exists for this email, please contact your organization administrator.",
    REGISTRATION_UNAVAILABLE: "Registration could not be completed. Please try again later.",
    NETWORK_ERROR: "Unable to connect. Please try again.",
    INVALID_INPUT: "Please check the registration details.",
  };
  return messages[error?.code] ?? "Registration could not be completed. Please try again later.";
}
