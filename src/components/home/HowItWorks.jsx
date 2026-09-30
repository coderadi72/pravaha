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
          text-slate-400
          dark:text-slate-500
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
          bg-white
          shadow-[0_8px_25px_rgba(15,23,42,0.06)]
          transition-all
          duration-300
          group-hover:-translate-y-1
          group-hover:shadow-[0_14px_32px_rgba(15,23,42,0.10)]

          dark:bg-[#0b243b]
          dark:shadow-[0_10px_28px_rgba(0,0,0,0.18)]
          dark:group-hover:bg-[#0e2b45]
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
          text-[#142b4a]
          dark:text-white
        "
      >
        {title}
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
          text-slate-500
          dark:text-slate-400
        "
      >
        {description}
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
              border-slate-200
              bg-white
              px-2
              py-1
              text-[8px]
              font-medium
              text-slate-500

              dark:border-white/[0.08]
              dark:bg-[#0b243b]
              dark:text-slate-400
            "
          >
            {tag}
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
        bg-[#f4f7fa]
        px-[5%]
        py-20

        dark:bg-[#061a2c]
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
          bg-[#dceeff]/35
          blur-[110px]

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
          bg-[#1678e8]/[0.06]
          blur-[120px]

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
            text-[#3488ff]
            dark:text-[#5aa9ff]
          "
        >
          HOW PRAVAHA WORKS
        </div>

        {/* Heading */}

        <h2
          className="
            mt-4
            text-[clamp(32px,4vw,48px)]
            font-bold
            leading-[1.1]
            tracking-[-1.2px]
            text-[#142b4a]
            dark:text-white
          "
        >
          From Site Data to

          <span
            className="
              block
              bg-gradient-to-r
              from-[#3488ff]
              to-[#28cdb0]
              bg-clip-text
              text-transparent
            "
          >
            Schedule Intelligence
          </span>
        </h2>

        {/* Description */}

        <p
          className="
            mx-auto
            mt-5
            max-w-[600px]
            text-[13px]
            leading-6
            text-slate-500
            dark:text-slate-400
          "
        >
          Pravaha connects fragmented field updates with
          the project schedule through a simple intelligent
          workflow.
        </p>
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
            bg-gradient-to-r
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
            border-[#3488ff]/20
            bg-[#3488ff]/10
            text-[#3488ff]

            dark:border-[#3488ff]/20
            dark:bg-[#3488ff]/10
            dark:text-[#55aaff]
          "
          title="Capture"
          description="Collect daily reports, spreadsheets, site diaries and supervisor updates from multiple disciplines."
          tags={[
            "Reports",
            "Excel",
            "Site Diary",
          ]}
        />

        {/* ==========================================================
            UNDERSTAND
        ========================================================== */}

        <WorkflowStep
          number="02"
          icon={<Sparkles size={21} strokeWidth={1.9} />}
          iconClass="
            border-[#9b7aff]/20
            bg-[#9b7aff]/10
            text-[#8c6ee8]

            dark:border-[#9b7aff]/20
            dark:bg-[#9b7aff]/10
            dark:text-[#a891ff]
          "
          title="Understand"
          description="AI extracts activity names, dates, discipline information and execution details from unstructured updates."
          tags={[
            "AI Extraction",
            "Dates",
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
            border-[#f4a340]/20
            bg-[#f4a340]/10
            text-[#e89427]

            dark:border-[#f4a340]/20
            dark:bg-[#f4a340]/10
            dark:text-[#ffb45b]
          "
          title="Link"
          description="Fuzzy matching connects field descriptions to the correct L5/L6 schedule activity with a confidence score."
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
            border-[#28cdb0]/20
            bg-[#28cdb0]/10
            text-[#20b79e]

            dark:border-[#28cdb0]/20
            dark:bg-[#28cdb0]/10
            dark:text-[#35d8bc]
          "
          title="Update"
          description="Actual progress is reflected back into the schedule while maintaining an audit trail for every update."
          tags={[
            "Schedule",
            "Audit Trail",
            "Live Data",
          ]}
        />
      </div>
    </section>
  );
}

export default HowItWorks;