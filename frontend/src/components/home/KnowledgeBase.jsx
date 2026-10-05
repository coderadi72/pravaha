import UiText from "../../ui/UiText.jsx";
import {
  BarChart3,
  CircleAlert,
  Clock3,
} from "lucide-react";

export function MemoryCard({
  icon,
  iconClass = "",
  title,
  text,
  value,
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
        border-border
        bg-surface
        p-6
        shadow-[0_6px_24px_rgba(15,23,42,0.045)]
        transition-all
        duration-200


        hover:border-border
        hover:shadow-[0_18px_45px_rgba(15,23,42,0.08)]

        dark:border-border
        dark:bg-surface
        dark:shadow-[0_10px_30px_rgba(0,0,0,0.16)]

        dark:hover:border-border
        dark:hover:bg-surface
        dark:hover:shadow-[0_18px_45px_rgba(0,0,0,0.24)]
      "
    >
      {/* Top ambient glow */}
      <div
        className="
          pointer-events-none
          absolute
          -right-16
          -top-16
          h-32
          w-32
          rounded-full
          bg-primary/[0.06]
          hidden
          transition
          duration-200
          group-hover:bg-primary/[0.10]

          dark:bg-primary/[0.05]
          dark:group-hover:bg-primary/[0.08]
        "
      />

      {/* Icon */}
      <div
        className={`
          relative
          mb-5
          flex
          h-11
          w-11
          items-center
          justify-center
          rounded-xl
          border
          border-primary/15
          bg-primary/10
          text-primary
          transition-all
          duration-200


          group-hover:shadow-[0_8px_20px_rgba(52,136,255,0.10)]

          dark:border-primary/15
          dark:bg-primary/10
          dark:text-primary

          ${iconClass}
        `}
      >
        {icon}
      </div>

      {/* Title */}
      <h3
        className="
          relative
          m-0
          text-[15px]
          font-semibold
          tracking-[-0.2px]
          text-foreground

          dark:text-foreground
        "
      >
        <UiText>{title}</UiText>
      </h3>

      {/* Description */}
      <p
        className="
          relative
          m-0
          mt-2.5
          text-[11px]
          leading-[1.75]
          text-secondary

          dark:text-secondary
        "
      >
        <UiText>{text}</UiText>
      </p>

      {/* Value */}
      <div
        className="
          relative
          mt-6
          flex
          items-end
          justify-between
          gap-3
          border-t
          border-border
          pt-4

          dark:border-border
        "
      >
        <span
          className="
            text-[22px]
            font-bold
            leading-none
            tracking-[-0.5px]
            text-foreground

            dark:text-foreground
          "
        >
          {value}
        </span>

        <small
          className="
            max-w-[120px]
            text-right
            text-[9px]
            font-medium
            leading-4
            text-secondary

            dark:text-secondary
          "
        >
          <UiText>{note}</UiText>
        </small>
      </div>
    </div>
  );
}

function KnowledgeBase() {
  return (
    <section
      id="knowledge"
      className="
        relative
        w-full
        overflow-hidden
        bg-background
        px-[5%]
        py-20

        dark:bg-background
      "
    >
      {/* ================= AMBIENT BACKGROUND ================= */}

      <div
        className="
          pointer-events-none
          absolute
          left-[-120px]
          top-[-140px]
          h-[360px]
          w-[500px]
          rounded-full
          bg-surface-high/40
          hidden

          dark:hidden
        "
      />

      <div
        className="
          pointer-events-none
          absolute
          bottom-[-180px]
          right-[-120px]
          h-[400px]
          w-[500px]
          rounded-full
          bg-success/[0.045]
          hidden

          dark:hidden
        "
      />

      <div
        className="
          pointer-events-none
          absolute
          left-1/2
          top-[-180px]
          hidden
          h-[350px]
          w-[650px]
          -translate-x-1/2
          rounded-full
          bg-primary/[0.045]
          hidden

          dark:block
        "
      />

      {/* ================= HEADER ================= */}

      <div
        className="
          relative
          z-10
          mx-auto
          max-w-[720px]
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
          PROJECT KNOWLEDGE
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
          Every completed activity becomes

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
            reusable knowledge.
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
          Explore illustrative execution patterns from demo data.
          These example figures are not measured project results.
        </UiText></p>
      </div>

      {/* ================= CARDS ================= */}

      <div
        className="
          relative
          z-10
          mx-auto
          mt-12
          grid
          w-full
          max-w-[1150px]
          grid-cols-1
          gap-5

          md:grid-cols-2
          lg:grid-cols-3
        "
      >
        {/* Actual Durations */}
        <MemoryCard
          icon={<Clock3 size={21} strokeWidth={1.9} />}
          title="Actual Durations"
          text="Understand how long activities actually took compared with the baseline schedule."
          value="18.4 days"
          note="Average actual duration"
        />

        {/* Delay Causes */}
        <MemoryCard
          icon={
            <CircleAlert
              size={21}
              strokeWidth={1.9}
            />
          }
          iconClass="
            border-info/15
            bg-info/10
            text-info

            dark:border-info/15
            dark:bg-info/10
            dark:text-info
          "
          title="Recurring Delay Causes"
          text="Build a structured record of recurring execution bottlenecks and delay patterns."
          value="24"
          note="Patterns identified"
        />

        {/* Productivity */}
        <MemoryCard
          icon={
            <BarChart3
              size={21}
              strokeWidth={1.9}
            />
          }
          iconClass="
            border-success/15
            bg-success/10
            text-success

            dark:border-success/15
            dark:bg-success/10
            dark:text-success
          "
          title="Discipline Productivity"
          text="Compare execution patterns across disciplines, contractors and project phases."
          value="+14%"
          note="Productivity insight"
        />
      </div>
    </section>
  );
}

export default KnowledgeBase;
