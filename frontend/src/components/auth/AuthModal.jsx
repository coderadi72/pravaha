import { useEffect, useRef, useState } from "react";
import { ArrowRight, Check, Circle, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, X } from "lucide-react";
import { authApi } from "../../api/client.js";
import Brand from "../layout/Brand.jsx";
import { useUiPreferences } from "../../ui/useUiPreferences.js";
import { signupDomain, signupEmailState, signupErrorMessage, validateSignup } from "./registration.js";

function SocialSignInButtons({ onSelect, activeProvider }) {
  const { t } = useUiPreferences();
  return <div className="pr-social-login">
    <button type="button" className={activeProvider === "Google" ? "is-active" : ""} onClick={() => onSelect("Google")} aria-label={t("Continue with Google")}><span className="pr-google-mark" aria-hidden="true">G</span><span>{t("Continue with Google")}</span></button>
    <button type="button" className={activeProvider === "GitHub" ? "is-active" : ""} onClick={() => onSelect("GitHub")} aria-label={t("Continue with GitHub")}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .9a11.1 11.1 0 0 0-3.5 21.6c.55.1.75-.24.75-.53v-2.08c-3.08.67-3.73-1.31-3.73-1.31-.5-1.28-1.23-1.62-1.23-1.62-1.01-.69.08-.68.08-.68 1.12.08 1.71 1.15 1.71 1.15 1 .1.79 1.97 3.34 1.41.1-.72.39-1.21.7-1.49-2.46-.28-5.05-1.23-5.05-5.47 0-1.21.43-2.2 1.14-2.98-.11-.28-.49-1.42.11-2.96 0 0 .93-.3 3.05 1.14a10.6 10.6 0 0 1 5.55 0c2.12-1.44 3.04-1.14 3.04-1.14.61 1.54.23 2.68.12 2.96.71.78 1.13 1.77 1.13 2.98 0 4.25-2.59 5.18-5.06 5.46.4.35.75 1.02.75 2.06v3.04c0 .29.2.63.76.52A11.1 11.1 0 0 0 12 .9Z" /></svg><span>{t("Continue with GitHub")}</span></button>
  </div>;
}

const passwordRequirements = [
  ["At least 12 characters", (value) => value.length >= 12],
  ["Uppercase letter", (value) => /[A-Z]/.test(value)],
  ["Lowercase letter", (value) => /[a-z]/.test(value)],
  ["Number", (value) => /[0-9]/.test(value)],
  ["Special character", (value) => /[^A-Za-z0-9]/.test(value)],
];

function PasswordFeedback({ password }) {
  const { t } = useUiPreferences();
  const checks = passwordRequirements.map(([, test]) => test(password));
  const score = checks.filter(Boolean).length;
  const level = score <= 1 ? "Weak" : score <= 3 ? "Fair" : score === 4 ? "Good" : "Strong";
  return <div className="pr-password-feedback" aria-live="polite">
    <div className="pr-password-strength-heading"><span>{t("Password strength")}</span><strong className={`is-${level.toLowerCase()}`}>{t(level)}</strong></div>
    <div className="pr-password-strength-meter" role="img" aria-label={`${t("Password strength")}: ${t(level)}`}>
      {checks.map((passed, index) => <span key={index} className={index < score ? `is-filled is-${level.toLowerCase()}` : ""} />)}
    </div>
    <div className="pr-password-requirements" aria-label={t("Password requirements")}>
      {passwordRequirements.map(([label], index) => <span key={label} className={checks[index] ? "is-met" : ""}>
        {checks[index] ? <Check size={13} aria-hidden="true" /> : <Circle size={11} aria-hidden="true" />}{t(label)}
      </span>)}
    </div>
  </div>;
}

export default function AuthModal({ isOpen, onClose, role = "management", signup = false, onOpenSignin, onAuthenticated }) {
  if (!isOpen) return null;
  return <AuthModalContent key={`${role}-${signup ? "signup" : "signin"}`} role={role} signup={signup} onClose={onClose} onOpenSignin={onOpenSignin} onAuthenticated={onAuthenticated} />;
}

function AuthModalContent({ role, signup, onClose, onOpenSignin, onAuthenticated }) {
  const { t } = useUiPreferences();
  const dialog = useRef(null);
  const submitting = useRef(false);
  const [portal, setPortal] = useState(role);
  const [signupCategory, setSignupCategory] = useState(role === "field" ? "SUPERVISOR" : "MANAGEMENT");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [socialPulse, setSocialPulse] = useState("");

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    const previousFocus = document.activeElement;
    document.body.style.overflow = "hidden";
    dialog.current?.querySelector("#pravaha-login-title")?.focus({ preventScroll: true });
    return () => { document.body.style.overflow = previousOverflow; previousFocus?.focus(); };
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    if (submitting.current || submitted) return;
    if (signup) {
      const payload = { name: fullName, email, password, confirmPassword, roleCategory: signupCategory };
      const validationError = validateSignup(payload);
      if (validationError) { setError(validationError); return; }
      submitting.current = true;
      setBusy(true); setError(""); setNotice("");
      try {
        const result = await authApi.signup({ ...payload, name: fullName.trim(), email: signupEmailState(email, signupCategory).normalized });
        setSubmitted(true);
        setNotice(result.message);
        setPassword(""); setConfirmPassword(""); setShowPassword(false); setShowConfirmPassword(false);
      } catch (requestError) { setError(signupErrorMessage(requestError)); }
      finally { submitting.current = false; setBusy(false); }
      return;
    }
    submitting.current = true;
    setBusy(true); setError("");
    try {
      const result = await authApi.login({ email, password });
      onClose();
      await onAuthenticated(result.user);
    } catch (requestError) { setError(requestError.message ?? "Sign in could not be completed."); }
    finally { submitting.current = false; setBusy(false); }
  };
  const signupValid = !validateSignup({ name: fullName, email, password, confirmPassword, roleCategory: signupCategory });
  const emailState = signupEmailState(email, signupCategory);
  const handleSocialSelect = (provider) => {
    setSocialPulse(provider);
    window.setTimeout(() => setSocialPulse(""), 220);
  };

  return <div className="pr-auth-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section ref={dialog} className="pr-auth-dialog" role="dialog" aria-modal="true" aria-labelledby="pravaha-login-title" onKeyDown={(event) => {
      if (event.key === "Escape") { event.stopPropagation(); onClose(); }
      if (event.key === "Tab") {
        const items = [...dialog.current.querySelectorAll('button:not(:disabled), input, select, a[href]')];
        const first = items[0], last = items[items.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    }}>
      <header className="pr-auth-header"><Brand /><button type="button" onClick={onClose} aria-label={t("Close sign in")} className="pr-icon-button"><X size={18} /></button></header>
      <aside className="pr-auth-context-panel">
        <span className="pr-auth-context-kicker">SIH26122 · Oil India Limited</span>
        <h2><UiAuthText text="Project Progress Monitoring System" /></h2>
        <p><UiAuthText text="Connect field execution with project schedules and actual progress." /></p>
        <div className="pr-auth-process" aria-hidden="true"><span><UiAuthText text="Field execution" /></span><i /><span><UiAuthText text="Schedule links" /></span><i /><span><UiAuthText text="Actual progress" /></span></div>
      </aside>
      <div className="pr-auth-body">
        {!signup && <div className="pr-auth-context"><label><ShieldCheck size={15} /><span className="sr-only">{t("Workspace")}</span><select value={portal} onChange={(event) => setPortal(event.target.value)} aria-label={t("Workspace")}><option value="management">{t("Management")}</option><option value="field">{t("Team Leader / Supervisor")}</option></select></label></div>}
        <h2 id="pravaha-login-title" tabIndex={-1}>{t(signup ? "Create your PRAVAHA account" : "Secure account access")}</h2>
        <p className="pr-auth-description">{t(signup ? "Registration requires administrator approval before sign in." : "Your server-assigned role and project access determine the workspace you can open.")}</p>
        <SocialSignInButtons onSelect={handleSocialSelect} activeProvider={socialPulse} />
        <div className="pr-auth-divider"><span><UiAuthText text="Or continue with email" /></span></div>
        {signup ? <form className="pr-auth-form" onSubmit={submit} noValidate>
          <fieldset className="pr-auth-role-options" disabled={busy || submitted}><legend className="sr-only">{t("Signup category")}</legend>{[["MANAGEMENT", "Management"], ["SUPERVISOR", "Team Leader / Supervisor"]].map(([category, label]) => <button key={category} type="button" aria-pressed={signupCategory === category} className={signupCategory === category ? "is-selected" : ""} onClick={() => { setSignupCategory(category); setError(""); }}>{t(label)}</button>)}</fieldset>
          <label htmlFor="pravaha-full-name">{t("Full name")}<span className="pr-input-with-icon"><input id="pravaha-full-name" name="name" type="text" autoComplete="name" required disabled={busy || submitted} maxLength={120} value={fullName} onChange={(event) => { setFullName(event.target.value); setError(""); }} placeholder={t("Enter your full name")} /></span></label>
          <label htmlFor="pravaha-email">{t("Work email")}<span className="pr-input-with-icon"><Mail size={16} aria-hidden="true" /><input id="pravaha-email" name="email" type="email" autoComplete="email" required disabled={busy || submitted} maxLength={254} value={email} onChange={(event) => { setEmail(event.target.value); setError(""); }} placeholder={`name@${signupDomain(signupCategory)}`} aria-describedby="pravaha-email-domain" aria-invalid={Boolean(email && !emailState.valid)} /></span><span id="pravaha-email-domain" className={`pr-password-match ${email ? emailState.valid ? "is-match" : "is-mismatch" : ""}`} aria-live="polite">{email ? emailState.valid ? <><Check size={12} aria-hidden="true" /> {t(emailState.message)}</> : t(emailState.message) : null}</span></label>
          <label htmlFor="pravaha-password">{t("Password")}<span className="pr-input-with-icon"><LockKeyhole size={16} aria-hidden="true" /><input id="pravaha-password" name="password" type={showPassword ? "text" : "password"} autoComplete="new-password" required disabled={busy || submitted} maxLength={128} value={password} onChange={(event) => { setPassword(event.target.value); setError(""); }} placeholder={t("Enter your password")} /><button type="button" disabled={submitted} onClick={() => setShowPassword((value) => !value)} aria-label={t(showPassword ? "Hide password" : "Show password")} className="pr-password-toggle">{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></span><PasswordFeedback password={password} /></label>
          <label htmlFor="pravaha-confirm-password">{t("Confirm password")}<span className="pr-input-with-icon"><LockKeyhole size={16} aria-hidden="true" /><input id="pravaha-confirm-password" name="confirmPassword" type={showConfirmPassword ? "text" : "password"} autoComplete="new-password" required disabled={busy || submitted} maxLength={128} value={confirmPassword} onChange={(event) => { setConfirmPassword(event.target.value); setError(""); }} placeholder={t("Re-enter your password")} /><button type="button" disabled={submitted} onClick={() => setShowConfirmPassword((value) => !value)} aria-label={t(showConfirmPassword ? "Hide password" : "Show password")} className="pr-password-toggle">{showConfirmPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></span>{confirmPassword && <span className={`pr-password-match ${confirmPassword === password ? "is-match" : "is-mismatch"}`}>{confirmPassword === password ? t("Passwords match") : t("Passwords do not match")}</span>}</label>
          {notice && <p role="status" className="pr-auth-provisioning">{t(notice)}</p>}
          {error && <p role="alert" className="pr-auth-error">{t(error)}</p>}
          <button type="submit" disabled={!signupValid || busy || submitted} className={`pr-button is-primary pr-auth-submit ${signupValid ? "is-ready" : "is-subdued"}`}>{t(busy ? "Submitting…" : submitted ? "Pending registration" : "Create account")}{!busy && !submitted && <ArrowRight size={16} />}</button>
          <button type="button" onClick={onOpenSignin} className="pr-auth-text-button">{t("Back to sign in")}</button>
        </form> : <form className="pr-auth-form" onSubmit={submit}>
          <label htmlFor="pravaha-email">{t("Work email or login ID")}<span className="pr-input-with-icon"><Mail size={16} aria-hidden="true" /><input id="pravaha-email" name="email" type="text" autoComplete="username" required maxLength={254} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@organization.com" /></span></label>
          <label htmlFor="pravaha-password">{t("Password")}<span className="pr-input-with-icon"><LockKeyhole size={16} aria-hidden="true" /><input id="pravaha-password" name="password" type={showPassword ? "text" : "password"} autoComplete="current-password" required maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={t("Enter your password")} /><button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={t(showPassword ? "Hide password" : "Show password")} className="pr-password-toggle">{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></span><PasswordFeedback password={password} /></label>
          <button type="button" onClick={() => setNotice("Contact your organization administrator to reset your password.")} className="pr-auth-forgot">{t("Forgot password?")}</button>
          {notice && <p role="status" className="pr-auth-provisioning">{t(notice)}</p>}
          {error && <p role="alert" className="pr-auth-error">{t(error)}</p>}
          <button type="submit" disabled={busy} className="pr-button is-primary pr-auth-submit"><span>{t(busy ? "Signing in…" : "Sign in")}</span>{!busy && <ArrowRight size={16} />}</button>
        </form>}
        {!signup && <p className="pr-auth-note">{t("Accounts are provisioned by your organization administrator.")}</p>}
      </div>
      <footer className="pr-auth-footer"><span>PRAVAHA · SIH26122</span><span aria-live="polite" className="sr-only">{socialPulse ? `Continue with ${socialPulse}` : ""}</span></footer>
    </section>
  </div>;
}

function UiAuthText({ text }) {
  const { t } = useUiPreferences();
  return t(text);
}
