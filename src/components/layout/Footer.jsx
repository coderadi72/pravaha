import {
  ArrowUpRight,
  Building2,
  CheckCircle2,
  ExternalLink,
  Globe2,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from "lucide-react";

function Footer() {
  return (
    <footer className="relative overflow-hidden bg-[#031b33] text-white">

      {/* ================================================================
          BACKGROUND
      ================================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          inset-0
          opacity-60
        "
      >
        <div
          className="
            absolute
            -right-32
            -top-40
            h-[420px]
            w-[420px]
            rounded-full
            bg-[#126fd0]/10
            blur-[100px]
          "
        />

        <div
          className="
            absolute
            -bottom-40
            left-[-100px]
            h-[350px]
            w-[350px]
            rounded-full
            bg-[#20c7ad]/[0.07]
            blur-[100px]
          "
        />
      </div>

      {/* subtle top line */}

      <div
        className="
          relative
          h-px
          w-full
          bg-gradient-to-r
          from-transparent
          via-[#2d8fff]/40
          to-transparent
        "
      />

      {/* ================================================================
          MAIN FOOTER
      ================================================================ */}

      <div
        className="
          relative
          mx-auto
          max-w-[1400px]
          px-5
          py-10
          sm:px-8
          lg:px-10
          lg:py-12
        "
      >

        <div
          className="
            grid
            grid-cols-1
            gap-9
            sm:grid-cols-2
            lg:grid-cols-[1.35fr_0.8fr_0.8fr_1fr]
            lg:gap-10
          "
        >

          {/* ============================================================
              BRAND / ORGANIZATION
          ============================================================ */}

          <div>

            <div className="flex items-center gap-3">

              {/* Pravaha logo */}

              <div
                className="
                  flex
                  h-[44px]
                  w-[44px]
                  items-center
                  justify-center
                  rounded-xl
                  border
                  border-white/10
                  bg-white/[0.04]
                "
              >
                <img
                  src="/pravaha-logo-vector.svg"
                  alt="Pravaha"
                  className="
                    h-[30px]
                    w-[34px]
                    object-contain
                  "
                />
              </div>

              <div>

                <div
                  className="
                    text-[17px]
                    font-bold
                    tracking-[-0.02em]
                  "
                >
                  Pravaha
                </div>

                <div
                  className="
                    mt-0.5
                    text-[9px]
                    font-medium
                    uppercase
                    tracking-[0.12em]
                    text-slate-500
                  "
                >
                  Project Intelligence Platform
                </div>

              </div>

            </div>

            <p
              className="
                mt-5
                max-w-[360px]
                text-[12px]
                leading-6
                text-slate-400
              "
            >
              AI-powered project progress monitoring for
              real-time field updates, schedule intelligence,
              activity mapping and institutional knowledge.
            </p>

            {/* Organization */}

            <div
              className="
                mt-5
                flex
                items-center
                gap-2.5
                rounded-xl
                border
                border-white/[0.07]
                bg-white/[0.025]
                px-3
                py-2.5
              "
            >

              <div
                className="
                  flex
                  h-7
                  w-7
                  items-center
                  justify-center
                  rounded-lg
                  bg-[#12375a]
                "
              >
                <Building2
                  size={14}
                  className="text-[#55aaff]"
                />
              </div>

              <div>

                <div
                  className="
                    text-[9px]
                    font-semibold
                    uppercase
                    tracking-[0.08em]
                    text-slate-500
                  "
                >
                  Project Organization
                </div>

                <div
                  className="
                    mt-0.5
                    text-[11px]
                    font-semibold
                    text-slate-200
                  "
                >
                  Oil India Limited
                </div>

              </div>

            </div>

          </div>

          {/* ============================================================
              PLATFORM
          ============================================================ */}

          <div>

            <h3
              className="
                mb-4
                text-[11px]
                font-bold
                uppercase
                tracking-[0.12em]
                text-white
              "
            >
              Platform
            </h3>

            <div className="space-y-2.5">

              <a
                href="#home"
                className="
                  block
                  text-[11px]
                  text-slate-400
                  no-underline
                  transition
                  hover:translate-x-0.5
                  hover:text-white
                "
              >
                Overview
              </a>

              <a
                href="#features"
                className="
                  block
                  text-[11px]
                  text-slate-400
                  no-underline
                  transition
                  hover:translate-x-0.5
                  hover:text-white
                "
              >
                Features
              </a>

              <a
                href="#how-it-works"
                className="
                  block
                  text-[11px]
                  text-slate-400
                  no-underline
                  transition
                  hover:translate-x-0.5
                  hover:text-white
                "
              >
                How It Works
              </a>

              <a
                href="#about"
                className="
                  block
                  text-[11px]
                  text-slate-400
                  no-underline
                  transition
                  hover:translate-x-0.5
                  hover:text-white
                "
              >
                About Pravaha
              </a>

              <a
                href="#knowledge"
                className="
                  block
                  text-[11px]
                  text-slate-400
                  no-underline
                  transition
                  hover:translate-x-0.5
                  hover:text-white
                "
              >
                Knowledge Base
              </a>

            </div>

          </div>

          {/* ============================================================
              QUICK LINKS
          ============================================================ */}

          <div>

            <h3
              className="
                mb-4
                text-[11px]
                font-bold
                uppercase
                tracking-[0.12em]
                text-white
              "
            >
              Quick Access
            </h3>

            <div className="space-y-2.5">

              <button
                type="button"
                className="
                  flex
                  items-center
                  gap-1.5
                  text-[11px]
                  text-slate-400
                  transition
                  hover:text-white
                "
              >
                Employee Portal

                <ArrowUpRight
                  size={11}
                  className="text-slate-600"
                />
              </button>

              <button
                type="button"
                className="
                  flex
                  items-center
                  gap-1.5
                  text-[11px]
                  text-slate-400
                  transition
                  hover:text-white
                "
              >
                Management Portal

                <ArrowUpRight
                  size={11}
                  className="text-slate-600"
                />
              </button>

              <button
                type="button"
                className="
                  flex
                  items-center
                  gap-1.5
                  text-[11px]
                  text-slate-400
                  transition
                  hover:text-white
                "
              >
                Project Dashboard

                <ArrowUpRight
                  size={11}
                  className="text-slate-600"
                />
              </button>

              <button
                type="button"
                className="
                  flex
                  items-center
                  gap-1.5
                  text-[11px]
                  text-slate-400
                  transition
                  hover:text-white
                "
              >
                Help & Support

                <ArrowUpRight
                  size={11}
                  className="text-slate-600"
                />
              </button>

              <button
                type="button"
                className="
                  flex
                  items-center
                  gap-1.5
                  text-[11px]
                  text-slate-400
                  transition
                  hover:text-white
                "
              >
                Documentation

                <ExternalLink
                  size={10}
                  className="text-slate-600"
                />
              </button>

            </div>

          </div>

          {/* ============================================================
              CONNECT / SYSTEM STATUS
          ============================================================ */}

          <div>

            <h3
              className="
                mb-4
                text-[11px]
                font-bold
                uppercase
                tracking-[0.12em]
                text-white
              "
            >
              System & Security
            </h3>

            {/* Status */}

            <div
              className="
                flex
                items-center
                gap-2.5
                rounded-xl
                border
                border-emerald-400/10
                bg-emerald-400/[0.04]
                px-3
                py-2.5
              "
            >

              <div
                className="
                  flex
                  h-7
                  w-7
                  items-center
                  justify-center
                  rounded-lg
                  bg-emerald-400/10
                "
              >
                <CheckCircle2
                  size={14}
                  className="text-emerald-400"
                />
              </div>

              <div>

                <div
                  className="
                    text-[9px]
                    font-semibold
                    uppercase
                    tracking-[0.08em]
                    text-slate-500
                  "
                >
                  Platform Status
                </div>

                <div
                  className="
                    mt-0.5
                    flex
                    items-center
                    gap-1.5
                    text-[11px]
                    font-semibold
                    text-emerald-400
                  "
                >
                  <span
                    className="
                      h-1.5
                      w-1.5
                      rounded-full
                      bg-emerald-400
                    "
                  />

                  All systems operational
                </div>

              </div>

            </div>

            {/* Security */}

            <div
              className="
                mt-3
                grid
                grid-cols-2
                gap-2
              "
            >

              <div
                className="
                  flex
                  items-center
                  gap-2
                  rounded-lg
                  border
                  border-white/[0.07]
                  bg-white/[0.025]
                  px-2.5
                  py-2
                "
              >
                <LockKeyhole
                  size={13}
                  className="text-[#53a7ff]"
                />

                <span
                  className="
                    text-[9px]
                    font-medium
                    text-slate-400
                  "
                >
                  Secure Access
                </span>
              </div>

              <div
                className="
                  flex
                  items-center
                  gap-2
                  rounded-lg
                  border
                  border-white/[0.07]
                  bg-white/[0.025]
                  px-2.5
                  py-2
                "
              >
                <ShieldCheck
                  size={13}
                  className="text-[#38d1b1]"
                />

                <span
                  className="
                    text-[9px]
                    font-medium
                    text-slate-400
                  "
                >
                  Role Based
                </span>
              </div>

            </div>

            {/* Contact */}

            <div
              className="
                mt-4
                flex
                items-center
                gap-2
                text-[10px]
                text-slate-500
              "
            >
              <Mail
                size={12}
                className="text-slate-600"
              />

              <span>
                Support through authorized channels
              </span>
            </div>

          </div>

        </div>

        {/* ================================================================
            BOTTOM BAR
        ================================================================ */}

        <div
          className="
            mt-9
            border-t
            border-white/[0.08]
            pt-5
          "
        >

          <div
            className="
              flex
              flex-col
              gap-4
              md:flex-row
              md:items-center
              md:justify-between
            "
          >

            {/* Copyright */}

            <div
              className="
                flex
                flex-wrap
                items-center
                gap-x-3
                gap-y-1.5
                text-[9px]
                text-slate-500
              "
            >

              <span>
                © 2026 Pravaha
              </span>

              <span className="text-slate-700">
                •
              </span>

              <span>
                SIH 2026
              </span>

              <span className="text-slate-700">
                •
              </span>

              <span>
                Project Progress Monitoring System
              </span>

            </div>

            {/* Right side */}

            <div
              className="
                flex
                flex-wrap
                items-center
                gap-4
                text-[9px]
                text-slate-500
              "
            >

              <button
                type="button"
                className="
                  transition
                  hover:text-white
                "
              >
                Privacy
              </button>

              <button
                type="button"
                className="
                  transition
                  hover:text-white
                "
              >
                Terms
              </button>

              <button
                type="button"
                className="
                  transition
                  hover:text-white
                "
              >
                Accessibility
              </button>

              <div
                className="
                  flex
                  items-center
                  gap-1.5
                  rounded-md
                  border
                  border-white/[0.07]
                  bg-white/[0.025]
                  px-2
                  py-1
                "
              >
                <Globe2
                  size={10}
                  className="text-slate-500"
                />

                <span>
                  India
                </span>
              </div>

            </div>

          </div>

          {/* Prototype disclaimer */}

          <div
            className="
              mt-4
              rounded-lg
              border
              border-amber-400/10
              bg-amber-400/[0.025]
              px-3
              py-2.5
              text-[8.5px]
              leading-4
              text-slate-500
            "
          >
            <span className="font-semibold text-slate-400">
              Prototype Notice:
            </span>{" "}
            Pravaha is an SIH 2026 prototype for project
            progress monitoring and demonstration purposes.
            It does not represent an official government
            production service or system of record.
          </div>

        </div>

      </div>
    </footer>
  );
}

export default Footer;