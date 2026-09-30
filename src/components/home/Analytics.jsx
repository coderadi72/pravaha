import {
  CheckCircle2,
  Database,
  Gauge,
  Target,
} from "lucide-react";

export function AnalyticsStat({
  icon,
  value,
  label,
  note,
}) {
  return (
    <div
      className="
        group
        relative
        overflow-hidden
        rounded-2xl
        border
        border-white/[0.09]
        bg-white/[0.045]
        p-5
        backdrop-blur-xl
        transition-all
        duration-300
        hover:-translate-y-1
        hover:border-white/[0.15]
        hover:bg-white/[0.07]
        hover:shadow-[0_18px_45px_rgba(0,0,0,0.18)]

        dark:border-white/[0.08]
        dark:bg-[#0a2137]/80
        dark:hover:bg-[#0d2942]
      "
    >
      {/* ============================================================
          CARD TOP GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          -right-10
          -top-10
          h-24
          w-24
          rounded-full
          bg-[#3488ff]/10
          blur-2xl
          opacity-0
          transition
          duration-300
          group-hover:opacity-100
        "
      />

      {/* ============================================================
          ICON
      ============================================================ */}

      <div
        className="
          relative
          mb-5
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-xl
          border
          border-[#3488ff]/10
          bg-[#3488ff]/10
          text-[#4da0ff]
          transition
          duration-300
          group-hover:scale-105
          group-hover:bg-[#3488ff]/15
        "
      >
        {icon}
      </div>

      {/* ============================================================
          VALUE
      ============================================================ */}

      <strong
        className="
          relative
          block
          text-[30px]
          font-bold
          leading-none
          tracking-[-1px]
          text-white
        "
      >
        {value}
      </strong>

      {/* ============================================================
          LABEL
      ============================================================ */}

      <span
        className="
          relative
          mt-2
          block
          text-[11px]
          font-medium
          text-slate-300
        "
      >
        {label}
      </span>

      {/* ============================================================
          NOTE
      ============================================================ */}

      <small
        className="
          relative
          mt-2
          block
          text-[10px]
          font-semibold
          text-[#35c9a7]
        "
      >
        {note}
      </small>
    </div>
  );
}

function Analytics() {
  return (
    <section
      className="
        relative
        overflow-hidden
        bg-[#071525]
        py-20
        text-white

        dark:bg-[#061827]
      "
    >
      {/* ============================================================
          AMBIENT BACKGROUND
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          inset-0
          bg-[radial-gradient(circle_at_18%_50%,rgba(52,136,255,0.11),transparent_34%),radial-gradient(circle_at_82%_40%,rgba(40,214,180,0.075),transparent_30%)]
        "
      />

      {/* ============================================================
          DARK MODE DEEP GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          left-1/2
          top-[-180px]
          hidden
          h-[400px]
          w-[700px]
          -translate-x-1/2
          rounded-full
          bg-[#1678e8]/[0.055]
          blur-[130px]

          dark:block
        "
      />

      {/* ============================================================
          SUBTLE GRID
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          inset-0
          opacity-[0.035]
          [background-image:linear-gradient(rgba(255,255,255,0.8)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.8)_1px,transparent_1px)]
          [background-size:50px_50px]
        "
      />

      {/* ============================================================
          CONTENT
      ============================================================ */}

      <div
        className="
          relative
          z-10
          mx-auto
          grid
          w-full
          max-w-[1250px]
          grid-cols-1
          items-center
          gap-12
          px-[5%]
          lg:grid-cols-[1fr_1fr]
          lg:gap-20
        "
      >

        {/* ==========================================================
            LEFT
        ========================================================== */}

        <div>

          {/* Eyebrow */}

          <div
            className="
              mb-5
              flex
              items-center
              gap-2
              text-[10px]
              font-bold
              tracking-[0.18em]
              text-[#4da0ff]
            "
          >
            <span
              className="
                h-1.5
                w-1.5
                rounded-full
                bg-[#4da0ff]
                shadow-[0_0_10px_rgba(77,160,255,0.7)]
              "
            />

            BRIDGING PLANNING AND EXECUTION
          </div>

          {/* Heading */}

          <h2
            className="
              m-0
              text-[clamp(34px,4vw,52px)]
              font-bold
              leading-[1.08]
              tracking-[-1.5px]
              text-white
            "
          >
            Transforming Infrastructure
            <br />
            Project Management

            <span
              className="
                block
                bg-gradient-to-r
                from-[#4da0ff]
                to-[#28d6b4]
                bg-clip-text
                text-transparent
              "
            >
              with AI
            </span>
          </h2>

          {/* Description */}

          <p
            className="
              mt-6
              max-w-[510px]
              text-[14px]
              leading-7
              text-slate-400
            "
          >
            From disconnected field data to a unified,
            real-time, and intelligent view of project
            progress.
          </p>

          {/* ========================================================
              BUILT FOR
          ======================================================== */}

          <div
            className="
              mt-7
              flex
              flex-wrap
              items-center
              gap-2
            "
          >

            {/* Avatars */}

            <div className="flex items-center">

              <div
                className="
                  flex
                  h-8
                  w-8
                  items-center
                  justify-center
                  rounded-full
                  border-2
                  border-[#071525]
                  bg-[#2869a8]
                  text-[10px]
                  font-bold
                  text-white
                "
              >
                A
              </div>

              <div
                className="
                  -ml-2
                  flex
                  h-8
                  w-8
                  items-center
                  justify-center
                  rounded-full
                  border-2
                  border-[#071525]
                  bg-[#7456a8]
                  text-[10px]
                  font-bold
                  text-white
                "
              >
                R
              </div>

              <div
                className="
                  -ml-2
                  flex
                  h-8
                  w-8
                  items-center
                  justify-center
                  rounded-full
                  border-2
                  border-[#071525]
                  bg-[#287f75]
                  text-[10px]
                  font-bold
                  text-white
                "
              >
                S
              </div>

              <div
                className="
                  -ml-2
                  flex
                  h-8
                  w-8
                  items-center
                  justify-center
                  rounded-full
                  border-2
                  border-[#071525]
                  bg-[#9a6636]
                  text-[10px]
                  font-bold
                  text-white
                "
              >
                K
              </div>

            </div>

            <span
              className="
                ml-1
                text-[11px]
                font-medium
                text-slate-400
              "
            >
              Built for Site Teams, Planners &
              Project Stakeholders
            </span>

          </div>
        </div>

        {/* ==========================================================
            RIGHT — STATS
        ========================================================== */}

        <div
          className="
            grid
            grid-cols-1
            gap-3
            sm:grid-cols-2
          "
        >

          <AnalyticsStat
            icon={<Gauge size={20} strokeWidth={1.8} />}
            value="42%"
            label="Overall Progress"
            note="↗ 12% this month"
          />

          <AnalyticsStat
            icon={
              <CheckCircle2
                size={20}
                strokeWidth={1.8}
              />
            }
            value="1,245"
            label="Activities Tracked"
            note="↗ 230 this week"
          />

          <AnalyticsStat
            icon={
              <Target
                size={20}
                strokeWidth={1.8}
              />
            }
            value="92%"
            label="Matching Accuracy"
            note="↗ 8% improvement"
          />

          <AnalyticsStat
            icon={
              <Database
                size={20}
                strokeWidth={1.8}
              />
            }
            value="15+"
            label="Input Formats"
            note="Text, Excel, PDF, Voice..."
          />

        </div>
      </div>
    </section>
  );
}

export default Analytics;