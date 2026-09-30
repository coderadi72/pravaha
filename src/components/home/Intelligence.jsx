import {
  Check,
  CircleAlert,
  HardHat,
  Wrench,
  Zap,
} from "lucide-react";

export function MatchRow({
  icon,
  iconClass = "",
  title,
  subtitle,
  score,
}) {
  return (
    <div
      className="
        group
        flex
        items-center
        gap-3
        border-b
        border-slate-700/50
        py-3.5
        transition-colors
        duration-200
        last:border-b-0
        hover:bg-white/[0.015]
      "
    >
      {/* ============================================================
          ICON
      ============================================================ */}

      <div
        className={`
          flex
          h-8
          w-8
          shrink-0
          items-center
          justify-center
          rounded-lg
          bg-[#3488ff]/10
          text-[#4da0ff]
          transition
          duration-200
          group-hover:scale-105

          ${iconClass}
        `}
      >
        {icon}
      </div>

      {/* ============================================================
          INFORMATION
      ============================================================ */}

      <div className="min-w-0 flex-1">
        <strong
          className="
            block
            truncate
            text-[11px]
            font-semibold
            text-white
          "
        >
          {title}
        </strong>

        <span
          className="
            mt-1
            block
            truncate
            text-[9px]
            text-slate-500
          "
        >
          {subtitle}
        </span>
      </div>

      {/* ============================================================
          CONFIDENCE
      ============================================================ */}

      <div
        className="
          shrink-0
          text-right
          text-[13px]
          font-bold
          text-[#28cdb0]
        "
      >
        {score}

        <small
          className="
            mt-0.5
            block
            text-[8px]
            font-medium
            text-slate-500
          "
        >
          Match
        </small>
      </div>
    </div>
  );
}

function Intelligence() {
  const disciplines = [
    "Civil & Structural",
    "Piping & Mechanical",
    "Electrical",
    "Instrumentation",
    "HSE & Site Operations",
    "Static / Rotating Equipment",
  ];

  return (
    <section
      className="
        relative
        overflow-hidden
        bg-[#071525]
        px-[5%]
        py-20
        text-white

        dark:bg-[#061827]
      "
    >
      {/* ============================================================
          LEFT AMBIENT GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          left-[-120px]
          top-1/2
          h-[400px]
          w-[400px]
          -translate-y-1/2
          rounded-full
          bg-[#3488ff]/[0.08]
          blur-[110px]
        "
      />

      {/* ============================================================
          RIGHT AMBIENT GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          bottom-[-150px]
          right-[-80px]
          h-[400px]
          w-[400px]
          rounded-full
          bg-[#28cdb0]/[0.06]
          blur-[120px]
        "
      />

      {/* ============================================================
          DARK MODE CENTER GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          left-1/2
          top-[-160px]
          hidden
          h-[300px]
          w-[600px]
          -translate-x-1/2
          rounded-full
          bg-[#1678e8]/[0.045]
          blur-[120px]

          dark:block
        "
      />

      {/* ============================================================
          MAIN CONTENT
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
          lg:grid-cols-[0.9fr_1.1fr]
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
                shadow-[0_0_9px_rgba(77,160,255,0.7)]
              "
            />

            ONE PLATFORM. MULTIPLE DISCIPLINES.
          </div>

          {/* Heading */}

          <h2
            className="
              mt-5
              text-[clamp(34px,4vw,52px)]
              font-bold
              leading-[1.08]
              tracking-[-1.5px]
              text-white
            "
          >
            Connect every part of

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
              project execution.
            </span>
          </h2>

          {/* Description */}

          <p
            className="
              mt-6
              max-w-[500px]
              text-[14px]
              leading-7
              text-slate-400
            "
          >
            Different engineering teams describe progress
            in different ways. Pravaha creates a common
            layer between field language and structured
            project schedules.
          </p>

          {/* ========================================================
              DISCIPLINES
          ======================================================== */}

          <div
            className="
              mt-7
              grid
              grid-cols-1
              gap-3
              sm:grid-cols-2
            "
          >
            {disciplines.map((item) => (
              <div
                key={item}
                className="
                  group/item
                  flex
                  items-center
                  gap-2.5
                  text-[11px]
                  font-medium
                  text-slate-300
                "
              >
                <span
                  className="
                    flex
                    h-5
                    w-5
                    shrink-0
                    items-center
                    justify-center
                    rounded-full
                    bg-[#28cdb0]/10
                    text-[#28cdb0]
                    transition
                    duration-200
                    group-hover/item:bg-[#28cdb0]/15
                  "
                >
                  <Check size={12} strokeWidth={2.5} />
                </span>

                {item}
              </div>
            ))}
          </div>
        </div>

        {/* ==========================================================
            RIGHT — INTELLIGENCE PANEL
        ========================================================== */}

        <div
          className="
            relative
          "
        >

          {/* Panel glow */}

          <div
            className="
              pointer-events-none
              absolute
              -inset-5
              rounded-[32px]
              bg-[#1678e8]/[0.05]
              blur-2xl
            "
          />

          <div
            className="
              relative
              overflow-hidden
              rounded-2xl
              border
              border-white/[0.09]
              bg-[#0c1b2d]/95
              p-5
              shadow-[0_25px_70px_rgba(0,0,0,0.25)]
              backdrop-blur-xl

              dark:border-white/[0.08]
              dark:bg-[#0a2137]/95
              dark:shadow-[0_30px_80px_rgba(0,0,0,0.30)]
            "
          >

            {/* ======================================================
                PANEL TOP LINE
            ====================================================== */}

            <div
              className="
                absolute
                inset-x-8
                top-0
                h-px
                bg-gradient-to-r
                from-transparent
                via-[#3488ff]/50
                to-transparent
              "
            />

            {/* ======================================================
                PANEL HEADER
            ====================================================== */}

            <div
              className="
                flex
                items-center
                justify-between
                border-b
                border-slate-700/50
                pb-4
              "
            >
              <div>
                <strong
                  className="
                    block
                    text-[13px]
                    font-semibold
                    text-white
                  "
                >
                  Activity Intelligence
                </strong>

                <small
                  className="
                    mt-1
                    block
                    text-[9px]
                    text-slate-500
                  "
                >
                  Live matching overview
                </small>
              </div>

              {/* Live status */}

              <span
                className="
                  inline-flex
                  items-center
                  gap-1.5
                  rounded-full
                  border
                  border-[#28cdb0]/20
                  bg-[#28cdb0]/10
                  px-2.5
                  py-1
                  text-[8px]
                  font-bold
                  tracking-wide
                  text-[#28cdb0]
                "
              >
                <i
                  className="
                    h-1.5
                    w-1.5
                    rounded-full
                    bg-[#28cdb0]
                    shadow-[0_0_8px_#28cdb0]
                  "
                />

                LIVE
              </span>
            </div>

            {/* ======================================================
                MATCH 1
            ====================================================== */}

            <MatchRow
              icon={<Wrench size={14} strokeWidth={1.8} />}
              title="Erected spool for Line 247-XX"
              subtitle="Field update → Piping"
              score="92%"
            />

            {/* ======================================================
                MATCH 2
            ====================================================== */}

            <MatchRow
              icon={
                <HardHat
                  size={14}
                  strokeWidth={1.8}
                />
              }
              iconClass="
                bg-[#28cdb0]/10
                text-[#28cdb0]
              "
              title="Foundation F-12 concreting"
              subtitle="Field update → Civil"
              score="87%"
            />

            {/* ======================================================
                MATCH 3
            ====================================================== */}

            <MatchRow
              icon={
                <Zap
                  size={14}
                  strokeWidth={1.8}
                />
              }
              iconClass="
                bg-[#f4a340]/10
                text-[#f4a340]
              "
              title="Cable tray installation"
              subtitle="Field update → Electrical"
              score="90%"
            />

            {/* ======================================================
                UNMATCHED BOX
            ====================================================== */}

            <div
              className="
                mt-4
                flex
                items-center
                gap-3
                rounded-xl
                border
                border-orange-400/15
                bg-orange-400/[0.06]
                p-3
                transition
                duration-200
                hover:bg-orange-400/[0.08]
              "
            >

              {/* Alert */}

              <div
                className="
                  flex
                  h-8
                  w-8
                  shrink-0
                  items-center
                  justify-center
                  rounded-lg
                  bg-orange-400/10
                  text-orange-400
                "
              >
                <CircleAlert
                  size={14}
                  strokeWidth={1.9}
                />
              </div>

              {/* Text */}

              <div className="min-w-0 flex-1">
                <strong
                  className="
                    block
                    text-[10px]
                    font-semibold
                    text-slate-200
                  "
                >
                  15 activities require review
                </strong>

                <span
                  className="
                    mt-1
                    block
                    text-[8px]
                    text-slate-500
                  "
                >
                  New or unmatched field descriptions
                </span>
              </div>

              {/* Review */}

              <button
                type="button"
                className="
                  shrink-0
                  rounded-lg
                  border
                  border-orange-400/20
                  bg-orange-400/10
                  px-2.5
                  py-1.5
                  text-[9px]
                  font-semibold
                  text-orange-400
                  transition
                  duration-200
                  hover:border-orange-400/30
                  hover:bg-orange-400/15
                "
              >
                Review →
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Intelligence;