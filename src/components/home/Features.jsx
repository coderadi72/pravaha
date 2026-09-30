import {
  Database,
  Link2,
  Upload,
  Zap,
} from "lucide-react";

export function FeatureCard({
  icon,
  iconClass,
  title,
  text,
}) {
  return (
    <div
      className="
        group
        flex
        items-start
        gap-4
        rounded-2xl
        border
        border-slate-200/80
        bg-white
        p-5
        shadow-[0_4px_18px_rgba(15,23,42,0.035)]
        transition-all
        duration-300
        hover:-translate-y-1
        hover:border-slate-300
        hover:shadow-[0_14px_35px_rgba(15,23,42,0.08)]

        dark:border-white/[0.07]
        dark:bg-[#0b243b]
        dark:shadow-[0_8px_28px_rgba(0,0,0,0.16)]
        dark:hover:border-white/[0.12]
        dark:hover:bg-[#0d2942]
        dark:hover:shadow-[0_16px_40px_rgba(0,0,0,0.22)]
      "
    >
      {/* ============================================================
          ICON
      ============================================================ */}

      <div
        className={`
          flex
          h-11
          w-11
          shrink-0
          items-center
          justify-center
          rounded-xl
          transition-all
          duration-300
          group-hover:scale-105
          group-hover:rotate-[2deg]
          ${iconClass}
        `}
      >
        {icon}
      </div>

      {/* ============================================================
          CONTENT
      ============================================================ */}

      <div className="min-w-0">

        <h3
          className="
            m-0
            text-[14px]
            font-semibold
            leading-5
            text-[#142b4a]
            dark:text-white
          "
        >
          {title}
        </h3>

        <p
          className="
            m-0
            mt-1.5
            text-[11px]
            leading-[1.7]
            text-slate-500
            dark:text-slate-400
          "
        >
          {text}
        </p>

      </div>
    </div>
  );
}

function Features() {
  return (
    <section
      id="features"
      className="
        relative
        w-full
        overflow-hidden
        bg-[#f4f7fa]
        px-[5%]
        py-12

        dark:bg-[#061a2c]
      "
    >
      {/* ============================================================
          SUBTLE LIGHT MODE DEPTH
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          left-[10%]
          top-[-120px]
          h-[260px]
          w-[420px]
          rounded-full
          bg-[#dbeeff]/30
          blur-[100px]

          dark:hidden
        "
      />

      {/* ============================================================
          DARK MODE GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          right-[8%]
          top-[-120px]
          hidden
          h-[280px]
          w-[420px]
          rounded-full
          bg-[#1678e8]/[0.07]
          blur-[110px]

          dark:block
        "
      />

      {/* ============================================================
          CARDS
      ============================================================ */}

      <div
        className="
          relative
          z-10
          mx-auto
          grid
          w-full
          max-w-[1280px]
          grid-cols-1
          gap-4
          sm:grid-cols-2
          lg:grid-cols-4
        "
      >

        {/* ==========================================================
            INGEST ANY FORMAT
        ========================================================== */}

        <FeatureCard
          icon={<Upload size={21} strokeWidth={1.9} />}
          iconClass="
            bg-[#3488ff]/10
            text-[#3488ff]

            dark:bg-[#3488ff]/10
            dark:text-[#55aaff]
          "
          title="Ingest Any Format"
          text="Free-text reports, spreadsheets, scanned diaries, Primavera/MS Project exports and more."
        />

        {/* ==========================================================
            AI ACTIVITY LINKING
        ========================================================== */}

        <FeatureCard
          icon={<Link2 size={21} strokeWidth={1.9} />}
          iconClass="
            bg-[#9b7aff]/10
            text-[#8b6bea]

            dark:bg-[#9b7aff]/10
            dark:text-[#a891ff]
          "
          title="AI Activity Linking"
          text="Fuzzy match discipline-specific updates to correct L5/L6 plan nodes with confidence score."
        />

        {/* ==========================================================
            REAL-TIME UPDATES
        ========================================================== */}

        <FeatureCard
          icon={<Zap size={21} strokeWidth={1.9} />}
          iconClass="
            bg-[#f4a340]/10
            text-[#e89225]

            dark:bg-[#f4a340]/10
            dark:text-[#ffb75a]
          "
          title="Real-Time Updates"
          text="Auto-update actual start/end dates in the schedule with full audit trail."
        />

        {/* ==========================================================
            PROJECT INTELLIGENCE
        ========================================================== */}

        <FeatureCard
          icon={<Database size={21} strokeWidth={1.9} />}
          iconClass="
            bg-[#28cdb0]/10
            text-[#20b79e]

            dark:bg-[#28cdb0]/10
            dark:text-[#35d8bc]
          "
          title="Build Project Intelligence"
          text="Create a queryable repository of actual execution patterns for future projects."
        />

      </div>
    </section>
  );
}

export default Features;