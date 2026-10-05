import UiText from "../../ui/UiText.jsx";
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
        border-border
        bg-surface/[0.045]
        p-5
        backdrop-blur-xl
        transition-all
        duration-200

        hover:border-border
        hover:bg-surface/[0.07]
        hover:shadow-[0_18px_45px_rgba(0,0,0,0.18)]

        dark:border-border
        dark:bg-surface/80
        dark:hover:bg-surface
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
          bg-primary/10
          blur-2xl
          opacity-0
          transition
          duration-200
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
          border-primary/10
          bg-primary/10
          text-primary
          transition
          duration-200

          group-hover:bg-primary/15
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
          text-foreground
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
          text-secondary
        "
      >
        <UiText>{label}</UiText>
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
          text-success
        "
      >
        <UiText>{note}</UiText>
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
        bg-surface
        py-20
        text-foreground

        dark:bg-surface
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
          bg-primary/[0.055]
          hidden

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
              text-primary
            "
          >
            <span
              className="
                h-1.5
                w-1.5
                rounded-full
                bg-primary
                shadow-[0_0_10px_rgba(77,160,255,0.7)]
              "
            /><UiText>

            BRIDGING PLANNING AND EXECUTION
          </UiText></div>

          {/* Heading */}

          <h2
            className="
              m-0
              text-[clamp(34px,4vw,52px)]
              font-bold
              leading-[1.08]
              tracking-[-1.5px]
              text-foreground
            "
          ><UiText>
            Transforming Infrastructure
            </UiText><br /><UiText>
            Project Management

            </UiText><span
              className="
                block
                bg-none
                from-[#4da0ff]
                to-[#28d6b4]
                bg-clip-text
                text-transparent
              "
            ><UiText>
              with Field Data
            </UiText></span>
          </h2>

          {/* Description */}

          <p
            className="
              mt-6
              max-w-[510px]
              text-[14px]
              leading-7
              text-secondary
            "
          ><UiText>
            A prototype view of field updates and schedule links.
            The figures shown here are illustrative demo values.
          </UiText></p>

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
                  border-border
                  bg-info
                  text-[10px]
                  font-bold
                  text-foreground
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
                  border-border
                  bg-info
                  text-[10px]
                  font-bold
                  text-foreground
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
                  border-border
                  bg-success
                  text-[10px]
                  font-bold
                  text-foreground
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
                  border-border
                  bg-warning
                  text-[10px]
                  font-bold
                  text-foreground
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
                text-secondary
              "
            ><UiText>
              Built for Site Teams, Planners &
              Project Stakeholders
            </UiText></span>

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
            note="Illustrative demo progress"
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
            note="Illustrative demo count"
          />

          <AnalyticsStat
            icon={
              <Target
                size={20}
                strokeWidth={1.8}
              />
            }
            value="92%"
            label="Demo Matching Score"
            note="Illustrative value, not measured accuracy"
          />

          <AnalyticsStat
            icon={
              <Database
                size={20}
                strokeWidth={1.8}
              />
            }
            value="Text"
            label="Field Update Input"
            note="Supervisor descriptions and progress"
          />

        </div>
      </div>
    </section>
  );
}

export default Analytics;
