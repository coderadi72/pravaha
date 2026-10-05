import UiText from "../../ui/UiText.jsx";
import { ArrowRight } from "lucide-react";

function FinalCTA({ onDemoStart }) {
  return (
    <section
      id="about"
      className="
        relative
        overflow-hidden
        bg-surface
        px-[5%]
        py-24
        text-foreground
      "
    >
      {/* Background Glow */}
      <div
        className="
          pointer-events-none
          absolute
          left-1/2
          top-1/2
          h-[420px]
          w-[700px]
          -translate-x-1/2
          -translate-y-1/2
          rounded-full
          bg-primary/10
          hidden
        "
      />

      {/* Content */}
      <div
        className="
          relative
          z-10
          mx-auto
          max-w-[850px]
          text-center
        "
      >

        {/* Eyebrow */}
        <span
          className="
            inline-block
            text-[10px]
            font-bold
            tracking-[0.18em]
            text-primary
          "
        ><UiText>
          BUILT FOR INFRASTRUCTURE PROJECT TEAMS
        </UiText></span>


        {/* Heading */}
        <h2
          className="
            mt-5
            text-[clamp(34px,5vw,58px)]
            font-bold
            leading-[1.08]
            tracking-[-1.5px]
            text-foreground
          "
        ><UiText>
          Turn field progress into
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
            schedule intelligence.
          </UiText></span>
        </h2>


        {/* Description */}
        <p
          className="
            mx-auto
            mt-6
            max-w-[600px]
            text-[14px]
            leading-7
            text-secondary
          "
        ><UiText>
          Capture. Understand. Link. Update.
          </UiText><br className="hidden sm:block" /><UiText>
          Build a smarter execution history with Pravaha.
        </UiText></p>


        {/* Buttons */}
        <div
          className="
            mt-8
            flex
            flex-wrap
            items-center
            justify-center
            gap-3
          "
        >

          {/* Primary */}
          <button
            type="button"
            onClick={() => onDemoStart?.()}
            className="
              group
              inline-flex
              h-11
              items-center
              gap-2
              rounded-md
              bg-primary
              px-5
              text-[13px]
              font-semibold
              text-foreground
              shadow-[0_8px_30px_rgba(52,136,255,0.25)]
              transition-all
              duration-200
              hover:-translate-y-0.5
              hover:bg-primary
              hover:shadow-[0_12px_35px_rgba(52,136,255,0.35)]
            "
          >
            <span><UiText>
              Try Pravaha Prototype
            </UiText></span>

            <ArrowRight
              size={16}
              className="
                transition-transform
                duration-200
                group-hover:translate-x-1
              "
            />
          </button>


          {/* Secondary */}
          <button
            type="button"
            onClick={() => onDemoStart?.()}
            className="
              inline-flex
              h-11
              items-center
              justify-center
              rounded-md
              border
              border-border
              bg-surface/[0.04]
              px-5
              text-[13px]
              font-medium
              text-secondary
              backdrop-blur-sm
              transition-all
              duration-200
              hover:border-border
              hover:bg-surface/[0.08]
              hover:text-foreground
            "
          ><UiText>
            Explore Dashboard
          </UiText></button>

        </div>

      </div>
    </section>
  );
}

export default FinalCTA;
