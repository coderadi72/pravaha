import UiText from "../../ui/UiText.jsx";
import {
  ArrowRight,
  Link2,
  Sparkles,
  Upload,
} from "lucide-react";

export function WorkflowStep({
  number,
  icon,
  iconClass,
  title,
  description,
  tags,
}) {
  return (
    <div
      className="
        group
        relative
        z-10
        flex
        flex-col
        items-center
        text-center
      "
    >
      {/* ============================================================
          NUMBER
      ============================================================ */}

      <div
        className="
          mb-4
          text-[10px]
          font-bold
          tracking-[0.15em]
          text-secondary
          dark:text-secondary
        "
      >
        {number}
      </div>

      {/* ============================================================
          ICON
      ============================================================ */}

      <div
        className={`
          flex
          h-14
          w-14
          items-center
          justify-center
          rounded-2xl
          border
          bg-surface
          shadow-[0_8px_25px_rgba(15,23,42,0.06)]
          transition-all
          duration-200

          group-hover:shadow-[0_14px_32px_rgba(15,23,42,0.10)]

          dark:bg-surface
          dark:shadow-[0_10px_28px_rgba(0,0,0,0.18)]
          dark:group-hover:bg-surface
          dark:group-hover:shadow-[0_16px_38px_rgba(0,0,0,0.25)]

          ${iconClass}
        `}
      >
        {icon}
      </div>

      {/* ============================================================
          TITLE
      ============================================================ */}

      <h3
        className="
          mt-5
          text-[16px]
          font-semibold
          text-foreground
          dark:text-foreground
        "
      >
        <UiText>{title}</UiText>
      </h3>

      {/* ============================================================
          DESCRIPTION
      ============================================================ */}

      <p
        className="
          mt-2
          max-w-[235px]
          text-[11px]
          leading-[1.7]
          text-secondary
          dark:text-secondary
        "
      >
        <UiText>{description}</UiText>
      </p>

      {/* ============================================================
          TAGS
      ============================================================ */}

      <div
        className="
          mt-4
          flex
          flex-wrap
          justify-center
          gap-1.5
        "
      >
        {tags.map((tag) => (
          <span
            key={tag}
            className="
              rounded-md
              border
              border-border
              bg-surface
              px-2
              py-1
              text-[8px]
              font-medium
              text-secondary

              dark:border-border
              dark:bg-surface
              dark:text-secondary
            "
          >
            <UiText>{tag}</UiText>
          </span>
        ))}
      </div>
    </div>
  );
}

function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="
        relative
        overflow-hidden
        bg-background
        px-[5%]
        py-20

        dark:bg-background
      "
    >
      {/* ============================================================
          LIGHT MODE AMBIENT GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          left-[8%]
          top-[-160px]
          h-[330px]
          w-[500px]
          rounded-full
          bg-surface-high/35
          hidden

          dark:hidden
        "
      />

      {/* ============================================================
          DARK MODE AMBIENT GLOW
      ============================================================ */}

      <div
        className="
          pointer-events-none
          absolute
          right-[5%]
          top-[-150px]
          hidden
          h-[350px]
          w-[500px]
          rounded-full
          bg-primary/[0.06]
          hidden

          dark:block
        "
      />

      {/* ============================================================
          HEADING
      ============================================================ */}

      <div
        className="
          relative
          z-10
          mx-auto
          max-w-[700px]
          text-center
        "
      >
        {/* Eyebrow */}

        <div
          className="
            text-[10px]
            font-bold
            tracking-[0.18em]
            text-primary
            dark:text-primary
          "
        ><UiText>
          HOW PRAVAHA WORKS
        </UiText></div>

        {/* Heading */}

        <h2
          className="
            mt-4
            text-[clamp(32px,4vw,48px)]
            font-bold
            leading-[1.1]
            tracking-[-1.2px]
            text-foreground
            dark:text-foreground
          "
        ><UiText>
          From Site Data to

          </UiText><span
            className="
              block
              bg-none
              from-[#3488ff]
              to-[#28cdb0]
              bg-clip-text
              text-transparent
            "
          ><UiText>
            Schedule Intelligence
          </UiText></span>
        </h2>

        {/* Description */}

        <p
          className="
            mx-auto
            mt-5
            max-w-[600px]
            text-[13px]
            leading-6
            text-secondary
            dark:text-secondary
          "
        ><UiText>
          Pravaha connects fragmented field updates with
          the project schedule through a simple intelligent
          workflow.
        </UiText></p>
      </div>

      {/* ============================================================
          WORKFLOW
      ============================================================ */}

      <div
        className="
          relative
          z-10
          mx-auto
          mt-16
          grid
          w-full
          max-w-[1200px]
          grid-cols-1
          gap-14
          md:grid-cols-2
          lg:grid-cols-4
          lg:gap-8
        "
      >
        {/* ==========================================================
            CONNECTING LINE
        ========================================================== */}

        <div
          className="
            absolute
            left-[12.5%]
            right-[12.5%]
            top-[57px]
            hidden
            h-px
            bg-none
            from-[#3488ff]/20
            via-[#9b7aff]/30
            to-[#28cdb0]/20
            lg:block
          "
        />

        {/* ==========================================================
            CAPTURE
        ========================================================== */}

        <WorkflowStep
          number="01"
          icon={<Upload size={21} strokeWidth={1.9} />}
          iconClass="
            border-primary/20
            bg-primary/10
            text-primary

            dark:border-primary/20
            dark:bg-primary/10
            dark:text-primary
          "
          title="Capture"
          description="Record supervisor observations and progress as text updates in the project workspace."
          tags={[
            "Reports",
            "Text Updates",
            "Observations",
          ]}
        />

        {/* ==========================================================
            UNDERSTAND
        ========================================================== */}

        <WorkflowStep
          number="02"
          icon={<Sparkles size={21} strokeWidth={1.9} />}
          iconClass="
            border-info/20
            bg-info/10
            text-info

            dark:border-info/20
            dark:bg-info/10
            dark:text-info
          "
          title="Understand"
          description="Prototype rules suggest activity, discipline and location for supported field descriptions."
          tags={[
            "Demo Rules",
            "Discipline",
            "Activities",
          ]}
        />

        {/* ==========================================================
            LINK
        ========================================================== */}

        <WorkflowStep
          number="03"
          icon={<Link2 size={21} strokeWidth={1.9} />}
          iconClass="
            border-warning/20
            bg-warning/10
            text-warning

            dark:border-warning/20
            dark:bg-warning/10
            dark:text-warning
          "
          title="Link"
          description="Deterministic suggestions connect field descriptions to L5/L6 schedule activities for Project Manager confirmation."
          tags={[
            "L5 / L6",
            "Matching",
            "Confidence",
          ]}
        />

        {/* ==========================================================
            UPDATE
        ========================================================== */}

        <WorkflowStep
          number="04"
          icon={<ArrowRight size={21} strokeWidth={1.9} />}
          iconClass="
            border-success/20
            bg-success/10
            text-success

            dark:border-success/20
            dark:bg-success/10
            dark:text-success
          "
          title="Update"
          description="Actual progress is reflected back into the schedule while maintaining an audit trail for every update."
          tags={[
            "Schedule",
            "Audit Trail",
            "Demo Data",
          ]}
        />
      </div>
    </section>
  );
}

export default HowItWorks;
