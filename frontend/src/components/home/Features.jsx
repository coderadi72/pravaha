import UiText from "../../ui/UiText.jsx";
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
        border-border
        bg-surface
        p-5
        shadow-[0_4px_18px_rgba(15,23,42,0.035)]
        transition-all
        duration-200

        hover:border-border
        hover:shadow-[0_14px_35px_rgba(15,23,42,0.08)]

        dark:border-border
        dark:bg-surface
        dark:shadow-[0_8px_28px_rgba(0,0,0,0.16)]
        dark:hover:border-border
        dark:hover:bg-surface
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
          duration-200


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
            text-foreground
            dark:text-foreground
          "
        >
          <UiText>{title}</UiText>
        </h3>

        <p
          className="
            m-0
            mt-1.5
            text-[11px]
            leading-[1.7]
            text-secondary
            dark:text-secondary
          "
        >
          <UiText>{text}</UiText>
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
        bg-background
        px-[5%]
        py-12

        dark:bg-background
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
          bg-surface-high/30
          hidden

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
          bg-primary/[0.07]
          hidden

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
            bg-primary/10
            text-primary

            dark:bg-primary/10
            dark:text-primary
          "
          title="Field Update Capture"
          text="Record field observations and progress details in a persistent project workflow."
        />

        {/* ==========================================================
            RULE-BASED ACTIVITY LINKING
        ========================================================== */}

        <FeatureCard
          icon={<Link2 size={21} strokeWidth={1.9} />}
          iconClass="
            bg-info/10
            text-info

            dark:bg-info/10
            dark:text-info
          "
          title="Deterministic Activity Linking"
          text="Fixed prototype rules suggest an L5/L6 schedule activity with a confidence score for Project Manager review."
        />

        {/* ==========================================================
            REAL-TIME UPDATES
        ========================================================== */}

        <FeatureCard
          icon={<Zap size={21} strokeWidth={1.9} />}
          iconClass="
            bg-warning/10
            text-warning

            dark:bg-warning/10
            dark:text-warning
          "
          title="Schedule Reconciliation"
          text="Project Manager confirmation links field dates and progress to the schedule with an audit trail."
        />

        {/* ==========================================================
            PROJECT INTELLIGENCE
        ========================================================== */}

        <FeatureCard
          icon={<Database size={21} strokeWidth={1.9} />}
          iconClass="
            bg-success/10
            text-success

            dark:bg-success/10
            dark:text-success
          "
          title="Review Execution Patterns"
          text="Explore illustrative patterns from demo records. Verify project sources and dates before reusing them."
        />

      </div>
    </section>
  );
}

export default Features;
