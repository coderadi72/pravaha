import { useEffect, useState } from "react";

import {
  ArrowRight,
  Building2,
  Check,
  CheckCircle2,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
  User,
  X,
} from "lucide-react";

function AuthModal({
  isOpen,
  onClose,
  role = "employee",
}) {
  const [mode, setMode] = useState("login");

  const [managementRole, setManagementRole] = useState(
    "administrator"
  );

  const [showPassword, setShowPassword] = useState(false);

  const isManagement = role === "management";

  const roleTitle = isManagement
    ? managementRole === "administrator"
      ? "Administrator"
      : "Project Manager"
    : "Employee";

  useEffect(() => {
    if (!isOpen) return;

    setMode("login");
    setManagementRole("administrator");
    setShowPassword(false);

    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen, role]);

  if (!isOpen) return null;

  const accentGradient = isManagement
    ? "from-[#286cff] via-[#685cff] to-[#8a5cf6]"
    : "from-[#1478ee] via-[#2aa8e9] to-[#20c7ad]";

  const accentText = isManagement
    ? "text-[#6357dc]"
    : "text-[#1478ee]";

  const buttonGradient = isManagement
    ? "bg-gradient-to-r from-[#315ed7] to-[#6257d9] hover:from-[#2852c5] hover:to-[#554acb]"
    : "bg-gradient-to-r from-[#146fd0] to-[#167edc] hover:from-[#1263bd] hover:to-[#126fc9]";

  const portalIcon = isManagement ? (
    <ShieldCheck
      size={21}
      strokeWidth={2}
      className="text-white"
    />
  ) : (
    <Building2
      size={21}
      strokeWidth={2}
      className="text-white"
    />
  );

  return (
    <div
      className="
        fixed
        inset-0
        z-[9999]
        flex
        items-center
        justify-center
        overflow-y-auto
        bg-[#061426]/75
        px-4
        py-8
        backdrop-blur-[12px]
      "
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      {/* Ambient glow */}

      <div
        className="
          pointer-events-none
          absolute
          left-1/2
          top-1/2
          h-[500px]
          w-[500px]
          -translate-x-1/2
          -translate-y-1/2
          rounded-full
          bg-[#1678e8]/10
          blur-[100px]
        "
      />

      {/* MODAL */}

      <div
        className="
          relative
          w-full
          max-w-[470px]
          overflow-hidden
          rounded-[24px]
          border
          border-white/80
          bg-white
          shadow-[0_35px_100px_rgba(0,20,45,0.38)]
          animate-[authModalIn_0.24s_cubic-bezier(.2,.8,.2,1)]
        "
      >
        {/* Top gradient */}

        <div
          className={`
            h-[3px]
            w-full
            bg-gradient-to-r
            ${accentGradient}
          `}
        />

        {/* Header */}

        <div
          className="
            flex
            items-center
            justify-between
            border-b
            border-slate-100
            px-7
            py-5
          "
        >
          <div className="flex items-center gap-3">
            {/* Logo */}

            <div
              className={`
                flex
                h-[42px]
                w-[42px]
                items-center
                justify-center
                rounded-[13px]
                bg-gradient-to-br
                ${accentGradient}
                shadow-[0_8px_22px_rgba(25,115,220,0.20)]
              `}
            >
              {portalIcon}
            </div>

            <div>
              <div
                className="
                  text-[15px]
                  font-bold
                  tracking-[-0.02em]
                  text-[#102b54]
                "
              >
                Pravaha
              </div>

              <div
                className="
                  mt-0.5
                  text-[9px]
                  font-medium
                  tracking-[0.01em]
                  text-slate-400
                "
              >
                Project Progress Monitoring System
              </div>
            </div>
          </div>

          {/* Close */}

          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="
              flex
              h-9
              w-9
              items-center
              justify-center
              rounded-full
              border
              border-transparent
              bg-slate-100
              text-slate-500
              transition
              duration-200
              hover:border-slate-200
              hover:bg-slate-200
              hover:text-slate-800
            "
          >
            <X size={17} strokeWidth={2} />
          </button>
        </div>

        {/* Main */}

        <div className="px-7 pb-7 pt-6">
          {/* Portal label */}

          <div
            className={`
              mb-2
              flex
              items-center
              gap-2
              text-[10px]
              font-bold
              uppercase
              tracking-[0.16em]
              ${accentText}
            `}
          >
            <span
              className={`
                h-1.5
                w-1.5
                rounded-full
                bg-current
              `}
            />

            {isManagement
              ? "Management Portal"
              : "Employee Portal"}
          </div>

          {/* Heading */}

          <h2
            className="
              m-0
              text-[27px]
              font-bold
              leading-tight
              tracking-[-0.035em]
              text-[#102b54]
            "
          >
            {mode === "login"
              ? "Welcome back"
              : `Create your ${roleTitle.toLowerCase()} account`}
          </h2>

          <p
            className="
              mt-2
              max-w-[390px]
              text-[12px]
              leading-5
              text-slate-500
            "
          >
            {mode === "login"
              ? `Sign in to continue to the Pravaha ${roleTitle.toLowerCase()} portal.`
              : `Register your ${roleTitle.toLowerCase()} account to access Pravaha.`}
          </p>

          {/* MANAGEMENT ROLE */}

          {isManagement && (
            <div className="mt-5">
              <div
                className="
                  mb-2
                  text-[10px]
                  font-bold
                  uppercase
                  tracking-[0.08em]
                  text-slate-500
                "
              >
                Access as
              </div>

              <div
                className="
                  grid
                  grid-cols-2
                  gap-1
                  rounded-xl
                  border
                  border-slate-200
                  bg-slate-100
                  p-1
                "
              >
                <button
                  type="button"
                  onClick={() =>
                    setManagementRole("administrator")
                  }
                  className={`
                    flex
                    h-[42px]
                    items-center
                    justify-center
                    gap-2
                    rounded-lg
                    text-[10px]
                    font-semibold
                    transition
                    duration-200
                    ${
                      managementRole === "administrator"
                        ? "bg-white text-[#183962] shadow-[0_2px_8px_rgba(15,35,65,0.10)]"
                        : "text-slate-500 hover:text-slate-700"
                    }
                  `}
                >
                  <ShieldCheck
                    size={14}
                    className={
                      managementRole === "administrator"
                        ? "text-[#5d61dc]"
                        : ""
                    }
                  />

                  Administrator
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setManagementRole("project-manager")
                  }
                  className={`
                    flex
                    h-[42px]
                    items-center
                    justify-center
                    gap-2
                    rounded-lg
                    text-[10px]
                    font-semibold
                    transition
                    duration-200
                    ${
                      managementRole === "project-manager"
                        ? "bg-white text-[#183962] shadow-[0_2px_8px_rgba(15,35,65,0.10)]"
                        : "text-slate-500 hover:text-slate-700"
                    }
                  `}
                >
                  <Building2
                    size={14}
                    className={
                      managementRole === "project-manager"
                        ? "text-[#5d61dc]"
                        : ""
                    }
                  />

                  Project Manager
                </button>
              </div>
            </div>
          )}

          {/* LOGIN / SIGNUP */}

          <div
            className={`
              ${
                isManagement ? "mt-4" : "mt-6"
              }
              flex
              rounded-xl
              border
              border-slate-200
              bg-slate-100
              p-1
            `}
          >
            <button
              type="button"
              onClick={() => setMode("login")}
              className={`
                flex
                h-[40px]
                flex-1
                items-center
                justify-center
                rounded-lg
                text-[11px]
                font-semibold
                transition
                duration-200
                ${
                  mode === "login"
                    ? "bg-white text-[#17375f] shadow-[0_2px_8px_rgba(15,35,65,0.10)]"
                    : "text-slate-500 hover:text-slate-700"
                }
              `}
            >
              Login
            </button>

            <button
              type="button"
              onClick={() => setMode("signup")}
              className={`
                flex
                h-[40px]
                flex-1
                items-center
                justify-center
                rounded-lg
                text-[11px]
                font-semibold
                transition
                duration-200
                ${
                  mode === "signup"
                    ? "bg-white text-[#17375f] shadow-[0_2px_8px_rgba(15,35,65,0.10)]"
                    : "text-slate-500 hover:text-slate-700"
                }
              `}
            >
              Sign Up
            </button>
          </div>

          {/* FORM */}

          <form
            className="mt-5 space-y-3.5"
            onSubmit={(e) => {
              e.preventDefault();

              // Backend authentication yahan connect hoga.
            }}
          >
            {/* FULL NAME */}

            {mode === "signup" && (
              <div>
                <label
                  className="
                    mb-1.5
                    block
                    text-[10px]
                    font-bold
                    text-[#41536d]
                  "
                >
                  Full Name
                </label>

                <div className="relative">
                  <User
                    size={15}
                    strokeWidth={1.8}
                    className="
                      absolute
                      left-3.5
                      top-1/2
                      -translate-y-1/2
                      text-slate-400
                    "
                  />

                  <input
                    type="text"
                    placeholder="Enter your full name"
                    className="
                      h-[43px]
                      w-full
                      rounded-xl
                      border
                      border-slate-200
                      bg-[#f8fafc]
                      pl-10
                      pr-3
                      text-[12px]
                      text-slate-700
                      outline-none
                      transition
                      duration-200
                      placeholder:text-slate-400
                      hover:border-slate-300
                      focus:border-[#4799ec]
                      focus:bg-white
                      focus:ring-4
                      focus:ring-[#4799ec]/10
                    "
                  />
                </div>
              </div>
            )}

            {/* EMAIL */}

            <div>
              <label
                className="
                  mb-1.5
                  block
                  text-[10px]
                  font-bold
                  text-[#41536d]
                "
              >
                {isManagement
                  ? `${roleTitle} Email`
                  : "Work Email"}
              </label>

              <div className="relative">
                <Mail
                  size={15}
                  strokeWidth={1.8}
                  className="
                    absolute
                    left-3.5
                    top-1/2
                    -translate-y-1/2
                    text-slate-400
                  "
                />

                <input
                  type="email"
                  placeholder={
                    isManagement
                      ? "name@organization.gov.in"
                      : "name@organization.com"
                  }
                  className="
                    h-[43px]
                    w-full
                    rounded-xl
                    border
                    border-slate-200
                    bg-[#f8fafc]
                    pl-10
                    pr-3
                    text-[12px]
                    text-slate-700
                    outline-none
                    transition
                    duration-200
                    placeholder:text-slate-400
                    hover:border-slate-300
                    focus:border-[#4799ec]
                    focus:bg-white
                    focus:ring-4
                    focus:ring-[#4799ec]/10
                  "
                />
              </div>
            </div>

            {/* ID */}

            {mode === "signup" && (
              <div>
                <label
                  className="
                    mb-1.5
                    block
                    text-[10px]
                    font-bold
                    text-[#41536d]
                  "
                >
                  {isManagement
                    ? `${roleTitle} ID`
                    : "Employee ID"}
                </label>

                <div className="relative">
                  <Building2
                    size={15}
                    strokeWidth={1.8}
                    className="
                      absolute
                      left-3.5
                      top-1/2
                      -translate-y-1/2
                      text-slate-400
                    "
                  />

                  <input
                    type="text"
                    placeholder={
                      isManagement
                        ? `Enter ${roleTitle.toLowerCase()} ID`
                        : "Enter employee ID"
                    }
                    className="
                      h-[43px]
                      w-full
                      rounded-xl
                      border
                      border-slate-200
                      bg-[#f8fafc]
                      pl-10
                      pr-3
                      text-[12px]
                      text-slate-700
                      outline-none
                      transition
                      duration-200
                      placeholder:text-slate-400
                      hover:border-slate-300
                      focus:border-[#4799ec]
                      focus:bg-white
                      focus:ring-4
                      focus:ring-[#4799ec]/10
                    "
                  />
                </div>
              </div>
            )}

            {/* PASSWORD */}

            <div>
              <div className="mb-1.5 flex items-center justify-between">
                <label
                  className="
                    text-[10px]
                    font-bold
                    text-[#41536d]
                  "
                >
                  Password
                </label>

                {mode === "login" && (
                  <button
                    type="button"
                    className="
                      text-[10px]
                      font-semibold
                      text-[#277fe4]
                      transition
                      hover:text-[#125eb5]
                    "
                  >
                    Forgot password?
                  </button>
                )}
              </div>

              <div className="relative">
                <LockKeyhole
                  size={15}
                  strokeWidth={1.8}
                  className="
                    absolute
                    left-3.5
                    top-1/2
                    -translate-y-1/2
                    text-slate-400
                  "
                />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter your password"
                  className="
                    h-[43px]
                    w-full
                    rounded-xl
                    border
                    border-slate-200
                    bg-[#f8fafc]
                    pl-10
                    pr-11
                    text-[12px]
                    text-slate-700
                    outline-none
                    transition
                    duration-200
                    placeholder:text-slate-400
                    hover:border-slate-300
                    focus:border-[#4799ec]
                    focus:bg-white
                    focus:ring-4
                    focus:ring-[#4799ec]/10
                  "
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowPassword(
                      (value) => !value
                    )
                  }
                  className="
                    absolute
                    right-3
                    top-1/2
                    flex
                    -translate-y-1/2
                    items-center
                    justify-center
                    text-slate-400
                    transition
                    hover:text-slate-700
                  "
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? (
                    <EyeOff size={16} />
                  ) : (
                    <Eye size={16} />
                  )}
                </button>
              </div>
            </div>

            {/* MANAGEMENT SECURITY */}

            {isManagement && (
              <div
                className="
                  flex
                  items-start
                  gap-2.5
                  rounded-xl
                  border
                  border-indigo-100
                  bg-gradient-to-r
                  from-indigo-50
                  to-blue-50
                  p-3
                "
              >
                <div
                  className="
                    flex
                    h-6
                    w-6
                    shrink-0
                    items-center
                    justify-center
                    rounded-lg
                    bg-white
                    shadow-sm
                  "
                >
                  <ShieldCheck
                    size={14}
                    className="text-indigo-500"
                  />
                </div>

                <div>
                  <div
                    className="
                      text-[9px]
                      font-bold
                      text-indigo-800
                    "
                  >
                    Restricted access
                  </div>

                  <p
                    className="
                      mt-0.5
                      text-[9px]
                      leading-4
                      text-indigo-600
                    "
                  >
                    Management access is limited to
                    authorized personnel and protected
                    by additional security controls.
                  </p>
                </div>
              </div>
            )}

            {/* REMEMBER */}

            {mode === "login" && (
              <label
                className="
                  flex
                  cursor-pointer
                  items-center
                  gap-2
                  pt-0.5
                "
              >
                <input
                  type="checkbox"
                  className="
                    h-3.5
                    w-3.5
                    cursor-pointer
                    rounded
                    border-slate-300
                    accent-[#1875d1]
                  "
                />

                <span
                  className="
                    text-[10px]
                    font-medium
                    text-slate-500
                  "
                >
                  Keep me signed in
                </span>
              </label>
            )}

            {/* SUBMIT */}

            <button
              type="submit"
              className={`
                group
                relative
                flex
                h-[45px]
                w-full
                items-center
                justify-center
                gap-2
                overflow-hidden
                rounded-xl
                text-[12px]
                font-bold
                text-white
                shadow-[0_10px_25px_rgba(20,110,210,0.22)]
                transition
                duration-200
                hover:-translate-y-[1px]
                hover:shadow-[0_14px_30px_rgba(20,110,210,0.27)]
                active:translate-y-0
                ${buttonGradient}
              `}
            >
              {/* shine */}

              <span
                className="
                  pointer-events-none
                  absolute
                  inset-y-0
                  -left-20
                  w-16
                  rotate-[20deg]
                  bg-white/15
                  blur-md
                  transition
                  duration-700
                  group-hover:left-[110%]
                "
              />

              <span className="relative">
                {mode === "login"
                  ? "Sign In"
                  : "Create Account"}
              </span>

              <ArrowRight
                size={15}
                className="
                  relative
                  transition
                  duration-200
                  group-hover:translate-x-1
                "
              />
            </button>
          </form>

          {/* FOOTER */}

          <div
            className="
              mt-6
              flex
              items-center
              justify-center
              gap-2
            "
          >
            <div
              className="
                flex
                h-5
                w-5
                items-center
                justify-center
                rounded-full
                bg-emerald-50
              "
            >
              <Check
                size={11}
                strokeWidth={2.5}
                className="text-emerald-500"
              />
            </div>

            <span
              className="
                text-[9px]
                font-medium
                text-slate-400
              "
            >
              Secure access to Pravaha
            </span>
          </div>

          {/* Tiny privacy text */}

          <div
            className="
              mt-2
              text-center
              text-[8px]
              text-slate-300
            "
          >
            Your credentials are protected with
            enterprise-grade security.
          </div>
        </div>
      </div>

      <style>
        {`
          @keyframes authModalIn {
            from {
              opacity: 0;
              transform: translateY(16px) scale(0.975);
            }

            to {
              opacity: 1;
              transform: translateY(0) scale(1);
            }
          }
        `}
      </style>
    </div>
  );
}

export default AuthModal;