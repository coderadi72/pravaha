import { useState } from "react";
import AuthModal from "../auth/AuthModal";

import {
  ChevronDown,
  Languages,
  Monitor,
  ShieldCheck,
  UserRound,
} from "lucide-react";

function Navbar() {
  const [authRole, setAuthRole] = useState(null);

  return (
    <>
      <header
        className="
          sticky
          top-0
          z-[1000]
          h-[64px]
          w-full
          border-b
          border-white/[0.07]
          bg-[#081827]/95
          text-white
          backdrop-blur-xl
        "
      >
        {/* subtle top light */}
        <div
          className="
            pointer-events-none
            absolute
            inset-x-0
            top-0
            h-px
            bg-gradient-to-r
            from-transparent
            via-[#3d9cff]/40
            to-transparent
          "
        />

        <div
          className="
            mx-auto
            flex
            h-full
            w-full
            items-center
            px-[3.2%]
          "
        >
          {/* ───────────────── LOGO ───────────────── */}

          <a
            href="#home"
            className="
              group
              flex
              h-full
              w-[155px]
              shrink-0
              items-center
              no-underline
            "
          >
            <div
              className="
                relative
                flex
                h-[42px]
                w-[142px]
                items-center
                rounded-xl
                px-2
                transition
                duration-300
                group-hover:bg-white/[0.035]
              "
            >
              <img
                src="/pravaha-logo-vector.svg"
                alt="Pravaha"
                className="
                  block
                  h-[38px]
                  w-[132px]
                  object-contain
                  object-left
                  transition
                  duration-300
                  group-hover:scale-[1.02]
                "
              />
            </div>
          </a>

          {/* ───────────────── NAVIGATION ───────────────── */}

          <nav
            className="
              ml-4
              flex
              h-full
              items-center
              gap-1
            "
          >
            <a
              href="#home"
              className="
                group
                relative
                flex
                h-[38px]
                items-center
                rounded-lg
                bg-[#17375d]/70
                px-4
                text-[12px]
                font-semibold
                text-[#65adff]
                no-underline
                shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]
                transition
                duration-200
              "
            >
              <span
                className="
                  absolute
                  bottom-0
                  left-3
                  right-3
                  h-[2px]
                  rounded-full
                  bg-gradient-to-r
                  from-[#2e91ff]
                  to-[#35d3c1]
                  opacity-100
                "
              />

              <span>Home</span>
            </a>

            <a
              href="#about"
              className="
                flex
                h-[38px]
                items-center
                rounded-lg
                px-4
                text-[12px]
                font-medium
                text-slate-300
                no-underline
                transition
                duration-200
                hover:bg-white/[0.055]
                hover:text-white
              "
            >
              About
            </a>

            <a
              href="#features"
              className="
                flex
                h-[38px]
                items-center
                rounded-lg
                px-4
                text-[12px]
                font-medium
                text-slate-300
                no-underline
                transition
                duration-200
                hover:bg-white/[0.055]
                hover:text-white
              "
            >
              Features
            </a>

            <a
              href="#how-it-works"
              className="
                flex
                h-[38px]
                items-center
                rounded-lg
                px-4
                text-[12px]
                font-medium
                text-slate-300
                no-underline
                transition
                duration-200
                hover:bg-white/[0.055]
                hover:text-white
              "
            >
              Use Cases
            </a>

            <a
              href="#about"
              className="
                flex
                h-[38px]
                items-center
                rounded-lg
                px-4
                text-[12px]
                font-medium
                text-slate-300
                no-underline
                transition
                duration-200
                hover:bg-white/[0.055]
                hover:text-white
              "
            >
              Contact
            </a>
          </nav>

          {/* ───────────────── RIGHT CONTROLS ───────────────── */}

          <div
            className="
              ml-auto
              flex
              items-center
              gap-2
            "
          >
            {/* Device */}

            <button
              type="button"
              className="
                group
                flex
                h-[36px]
                items-center
                gap-1.5
                rounded-lg
                border
                border-white/[0.08]
                bg-white/[0.025]
                px-2.5
                text-slate-300
                shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]
                transition
                duration-200
                hover:border-white/[0.14]
                hover:bg-white/[0.06]
                hover:text-white
              "
              aria-label="Display settings"
            >
              <Monitor
                size={15}
                strokeWidth={1.8}
                className="
                  text-slate-400
                  transition
                  group-hover:text-[#65adff]
                "
              />

              <ChevronDown
                size={11}
                className="text-slate-500"
              />
            </button>

            {/* Language */}

            <button
              type="button"
              className="
                group
                flex
                h-[36px]
                items-center
                gap-1.5
                rounded-lg
                border
                border-white/[0.08]
                bg-white/[0.025]
                px-3
                text-[11px]
                font-medium
                text-slate-300
                shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]
                transition
                duration-200
                hover:border-white/[0.14]
                hover:bg-white/[0.06]
                hover:text-white
              "
            >
              <Languages
                size={14}
                strokeWidth={1.8}
                className="
                  text-[#31d6b0]
                  transition
                  group-hover:scale-105
                "
              />

              <span>EN</span>

              <ChevronDown
                size={11}
                className="text-slate-500"
              />
            </button>

            {/* Divider */}

            <div
              className="
                mx-1
                h-6
                w-px
                bg-white/[0.08]
              "
            />

            {/* Employee */}

            <button
              type="button"
              onClick={() => setAuthRole("employee")}
              className="
                group
                flex
                h-[36px]
                items-center
                gap-1.5
                rounded-lg
                border
                border-[#31506f]/70
                bg-[#10263e]/80
                px-3
                text-[11px]
                font-semibold
                text-slate-200
                shadow-[0_4px_14px_rgba(0,0,0,0.12),inset_0_1px_0_rgba(255,255,255,0.04)]
                transition
                duration-200
                hover:border-[#3975a9]
                hover:bg-[#153250]
                hover:text-white
              "
            >
              <div
                className="
                  flex
                  h-5
                  w-5
                  items-center
                  justify-center
                  rounded-md
                  bg-[#123e55]
                "
              >
                <UserRound
                  size={12}
                  strokeWidth={2}
                  className="text-[#31d6b0]"
                />
              </div>

              <span>Employee</span>

              <ChevronDown
                size={11}
                className="
                  text-slate-500
                  transition
                  group-hover:text-slate-300
                "
              />
            </button>

            {/* Management */}

            <button
              type="button"
              onClick={() => setAuthRole("management")}
              className="
                group
                flex
                h-[36px]
                items-center
                gap-1.5
                rounded-lg
                border
                border-[#31506f]/70
                bg-[#10263e]/80
                px-3
                text-[11px]
                font-semibold
                text-slate-200
                shadow-[0_4px_14px_rgba(0,0,0,0.12),inset_0_1px_0_rgba(255,255,255,0.04)]
                transition
                duration-200
                hover:border-[#3975a9]
                hover:bg-[#153250]
                hover:text-white
              "
            >
              <div
                className="
                  flex
                  h-5
                  w-5
                  items-center
                  justify-center
                  rounded-md
                  bg-[#172f58]
                "
              >
                <ShieldCheck
                  size={12}
                  strokeWidth={2}
                  className="text-[#62aaff]"
                />
              </div>

              <span>Management</span>

              <ChevronDown
                size={11}
                className="
                  text-slate-500
                  transition
                  group-hover:text-slate-300
                "
              />
            </button>
          </div>
        </div>
      </header>

      {/* AUTH MODAL */}

      <AuthModal
        isOpen={authRole !== null}
        role={authRole}
        onClose={() => setAuthRole(null)}
      />
    </>
  );
}

export default Navbar;