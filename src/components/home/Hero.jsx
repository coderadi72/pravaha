import {
  ArrowRight,
  BarChart3,
  Database,
  FileText,
  Link2,
  Play,
  RefreshCw,
} from "lucide-react";

import DashboardPreview from "./DashboardPreview";

function Hero() {
  return (
    <section
      id="home"
      className="
        relative
        overflow-hidden
        bg-[#071525]
        text-white
      "
    >
      {/* ============================================================
          HERO BACKGROUND IMAGE
      ============================================================ */}

      <div
        className="
          absolute
          inset-0
          bg-cover
          bg-center
        "
        style={{
          backgroundImage: "url('/hero-bg.jpg')",
        }}
      />

      {/* ============================================================
          LIGHT MODE OVERLAY

          Left side stays soft/light so the heading remains readable.
      ============================================================ */}

      <div
        className="
          absolute
          inset-0
          bg-[linear-gradient(90deg,rgba(242,247,252,0.94)_0%,rgba(239,246,253,0.86)_34%,rgba(220,235,247,0.48)_55%,rgba(5,22,40,0.40)_78%,rgba(4,17,31,0.60)_100%)]
          dark:hidden
        "
      />

      {/* ============================================================
          DARK MODE OVERLAY

          In dark mode the hero becomes much more navy/cinematic.
      ============================================================ */}

      <div
        className="
          absolute
          inset-0
          hidden
          bg-[linear-gradient(90deg,rgba(3,20,38,0.94)_0%,rgba(5,25,45,0.88)_35%,rgba(6,28,48,0.72)_58%,rgba(3,18,33,0.78)_78%,rgba(2,13,25,0.90)_100%)]
          dark:block
        "
      />

      {/* ============================================================
          DARK MODE SOFT BLUE GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          left-[20%]
          top-[-100px]
          hidden
          h-[380px]
          w-[500px]
          rounded-full
          bg-[#1479ef]/10
          blur-[120px]
          dark:block
        "
      />

      {/* ============================================================
          BOTTOM DARK FADE

          Keeps the transition into the next section clean.
      ============================================================ */}

      <div
        className="
          absolute
          inset-x-0
          bottom-0
          h-24
          bg-gradient-to-t
          from-[#071525]
          to-transparent
        "
      />

      {/* ============================================================
          MAIN HERO CONTENT
      ============================================================ */}

      <div
        className="
          relative
          z-10
          mx-auto
          flex
          min-h-[455px]
          w-full
          max-w-[1500px]
          items-center
          gap-4
          px-[4.8%]
          pb-8
          pt-7
          lg:gap-5
        "
      >
        {/* ==========================================================
            LEFT CONTENT
        ========================================================== */}

        <div
          className="
            relative
            z-20
            w-full
            shrink-0
            lg:w-[48%]
            xl:w-[47%]
          "
        >
          {/* ========================================================
              PROJECT BADGE
          ======================================================== */}

          <div
            className="
              mb-4
              inline-flex
              items-center
              gap-2
              rounded-full
              border
              border-[#164c82]/15
              bg-white/75
              px-3
              py-1.5
              text-[10px]
              font-medium
              text-[#19335b]
              shadow-[0_4px_16px_rgba(20,50,90,0.07)]
              backdrop-blur-md
              dark:border-white/10
              dark:bg-[#102941]/80
              dark:text-slate-300
              dark:shadow-[0_8px_25px_rgba(0,0,0,0.20)]
            "
          >
            <BarChart3
              size={14}
              className="text-[#1674df] dark:text-[#55aaff]"
            />

            <strong
              className="
                font-bold
                text-[#102b54]
                dark:text-white
              "
            >
              SIH26122
            </strong>

            <span className="text-[#7990aa] dark:text-slate-600">
              |
            </span>

            <span>Oil India Limited</span>
          </div>

          {/* ========================================================
              HEADING
          ======================================================== */}

          <h1
            className="
              m-0
              max-w-[680px]
              text-[clamp(38px,4.2vw,62px)]
              font-bold
              leading-[1.01]
              tracking-[-2.4px]
              text-[#0b2448]
              dark:text-white
            "
          >
            From Field Updates
            <br />
            to{" "}
            <span
              className="
                bg-gradient-to-r
                from-[#1479ef]
                via-[#258ff5]
                to-[#19bca9]
                bg-clip-text
                text-transparent
              "
            >
              Smarter Schedules
            </span>
          </h1>

          {/* ========================================================
              DESCRIPTION
          ======================================================== */}

          <p
            className="
              mt-4
              max-w-[590px]
              text-[13px]
              font-medium
              leading-[1.55]
              text-[#233e62]
              xl:text-[14px]
              dark:text-slate-300
            "
          >
            AI-powered data capture and schedule linking layer for
            <br className="hidden xl:block" />
            real-time infrastructure project progress tracking.
          </p>

          {/* ========================================================
              FEATURE TAGS
          ======================================================== */}

          <div
            className="
              mt-5
              flex
              max-w-[680px]
              flex-wrap
              gap-1.5
            "
          >
            {/* Multi Format */}

            <div
              className="
                inline-flex
                items-center
                gap-1.5
                rounded-full
                border
                border-white/70
                bg-white/80
                px-2.5
                py-1.5
                text-[9px]
                font-semibold
                text-[#20395d]
                shadow-sm
                backdrop-blur-md
                dark:border-white/10
                dark:bg-[#102a43]/80
                dark:text-slate-200
              "
            >
              <FileText
                size={13}
                className="text-[#147cf0]"
              />

              Multi-Format Input
            </div>

            {/* AI Mapping */}

            <div
              className="
                inline-flex
                items-center
                gap-1.5
                rounded-full
                border
                border-white/70
                bg-white/80
                px-2.5
                py-1.5
                text-[9px]
                font-semibold
                text-[#20395d]
                shadow-sm
                backdrop-blur-md
                dark:border-white/10
                dark:bg-[#102a43]/80
                dark:text-slate-200
              "
            >
              <Link2
                size={13}
                className="text-[#754cff]"
              />

              AI Activity Mapping
            </div>

            {/* Real Time */}

            <div
              className="
                inline-flex
                items-center
                gap-1.5
                rounded-full
                border
                border-white/70
                bg-white/80
                px-2.5
                py-1.5
                text-[9px]
                font-semibold
                text-[#20395d]
                shadow-sm
                backdrop-blur-md
                dark:border-white/10
                dark:bg-[#102a43]/80
                dark:text-slate-200
              "
            >
              <RefreshCw
                size={13}
                className="text-[#147cf0]"
              />

              Real-Time Schedule Update
            </div>

            {/* Knowledge */}

            <div
              className="
                inline-flex
                items-center
                gap-1.5
                rounded-full
                border
                border-white/70
                bg-white/80
                px-2.5
                py-1.5
                text-[9px]
                font-semibold
                text-[#20395d]
                shadow-sm
                backdrop-blur-md
                dark:border-white/10
                dark:bg-[#102a43]/80
                dark:text-slate-200
              "
            >
              <Database
                size={13}
                className="text-[#079d9c]"
              />

              Institutional Knowledge
            </div>
          </div>

          {/* ========================================================
              CTA BUTTONS
          ======================================================== */}

          <div
            className="
              mt-5
              flex
              items-center
              gap-2.5
            "
          >
            {/* Primary CTA */}

            <button
              type="button"
              className="
                group
                inline-flex
                h-10
                items-center
                gap-2
                rounded-lg
                bg-[#0c315e]
                px-5
                text-[12px]
                font-semibold
                text-white
                shadow-[0_8px_22px_rgba(12,49,94,0.22)]
                transition
                duration-200
                hover:-translate-y-0.5
                hover:bg-[#104176]
                dark:bg-[#1678df]
                dark:shadow-[0_8px_25px_rgba(22,120,223,0.25)]
                dark:hover:bg-[#2587ed]
              "
            >
              Try Prototype

              <ArrowRight
                size={15}
                className="
                  transition
                  duration-200
                  group-hover:translate-x-1
                "
              />
            </button>

            {/* Demo */}

            <button
              type="button"
              className="
                inline-flex
                h-10
                items-center
                gap-2
                rounded-lg
                border
                border-[#1b5795]/25
                bg-white/75
                px-4
                text-[12px]
                font-semibold
                text-[#173b6b]
                shadow-sm
                backdrop-blur-md
                transition
                duration-200
                hover:bg-white
                dark:border-white/10
                dark:bg-[#102941]/80
                dark:text-slate-200
                dark:hover:bg-[#173653]
              "
            >
              <span
                className="
                  flex
                  h-5
                  w-5
                  items-center
                  justify-center
                  rounded-full
                  bg-white
                  text-[#176bd0]
                  shadow-sm
                  dark:bg-[#1a456d]
                  dark:text-[#65b1ff]
                "
              >
                <Play
                  size={9}
                  fill="currentColor"
                />
              </span>

              Watch Demo
            </button>
          </div>
        </div>

        {/* ==========================================================
            RIGHT — DASHBOARD PREVIEW
        ========================================================== */}

        <div
          className="
            relative
            hidden
            min-w-0
            flex-1
            lg:block
          "
        >
          {/* Glow */}

          <div
            className="
              absolute
              -inset-5
              rounded-[40px]
              bg-blue-300/10
              blur-3xl
              dark:bg-blue-500/10
            "
          />

          <div
            className="
              relative
              ml-auto
              w-[85%]
              max-w-[590px]
              xl:w-[85%]
              xl:max-w-[620px]
            "
          >
            <DashboardPreview />
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;