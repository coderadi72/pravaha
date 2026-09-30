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
        border-slate-200/80
        bg-white
        p-6
        shadow-[0_6px_24px_rgba(15,23,42,0.045)]
        transition-all
        duration-300

        hover:-translate-y-1
        hover:border-slate-300
        hover:shadow-[0_18px_45px_rgba(15,23,42,0.08)]

        dark:border-white/[0.07]
        dark:bg-[#0b243b]
        dark:shadow-[0_10px_30px_rgba(0,0,0,0.16)]

        dark:hover:border-white/[0.12]
        dark:hover:bg-[#0d2942]
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
          bg-[#3488ff]/[0.06]
          blur-3xl
          transition
          duration-500
          group-hover:bg-[#3488ff]/[0.10]

          dark:bg-[#3488ff]/[0.05]
          dark:group-hover:bg-[#3488ff]/[0.08]
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
          border-[#3488ff]/15
          bg-[#3488ff]/10
          text-[#3488ff]
          transition-all
          duration-300

          group-hover:scale-105
          group-hover:shadow-[0_8px_20px_rgba(52,136,255,0.10)]

          dark:border-[#3488ff]/15
          dark:bg-[#3488ff]/10
          dark:text-[#55aaff]

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
          text-[#142b4a]

          dark:text-white
        "
      >
        {title}
      </h3>

      {/* Description */}
      <p
        className="
          relative
          m-0
          mt-2.5
          text-[11px]
          leading-[1.75]
          text-slate-500

          dark:text-slate-400
        "
      >
        {text}
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
          border-slate-100
          pt-4

          dark:border-white/[0.07]
        "
      >
        <span
          className="
            text-[22px]
            font-bold
            leading-none
            tracking-[-0.5px]
            text-[#142b4a]

            dark:text-white
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
            text-slate-400

            dark:text-slate-500
          "
        >
          {note}
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
        bg-[#f7f9fb]
        px-[5%]
        py-20

        dark:bg-[#061a2c]
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
          bg-[#dceeff]/40
          blur-[120px]

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
          bg-[#28cdb0]/[0.045]
          blur-[130px]

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
          bg-[#1678e8]/[0.045]
          blur-[130px]

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
            text-[#3488ff]

            dark:text-[#5aa9ff]
          "
        >
          PROJECT KNOWLEDGE
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
          Every completed activity becomes

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
            reusable knowledge.
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
          Preserve actual execution patterns instead of losing
          valuable project knowledge when a project closes.
        </p>
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
            border-[#9b7aff]/15
            bg-[#9b7aff]/10
            text-[#8c6ee8]

            dark:border-[#9b7aff]/15
            dark:bg-[#9b7aff]/10
            dark:text-[#a891ff]
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
            border-[#28cdb0]/15
            bg-[#28cdb0]/10
            text-[#20b79e]

            dark:border-[#28cdb0]/15
            dark:bg-[#28cdb0]/10
            dark:text-[#35d8bc]
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