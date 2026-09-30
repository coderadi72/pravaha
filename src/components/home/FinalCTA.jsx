import { ArrowRight } from "lucide-react";

function FinalCTA() {
  return (
    <section
      id="about"
      className="
        relative
        overflow-hidden
        bg-[#071525]
        px-[5%]
        py-24
        text-white
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
          bg-[#3488ff]/10
          blur-[120px]
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
            text-[#4da0ff]
          "
        >
          BUILT FOR INFRASTRUCTURE PROJECT TEAMS
        </span>


        {/* Heading */}
        <h2
          className="
            mt-5
            text-[clamp(34px,5vw,58px)]
            font-bold
            leading-[1.08]
            tracking-[-1.5px]
            text-white
          "
        >
          Turn field progress into
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
            schedule intelligence.
          </span>
        </h2>


        {/* Description */}
        <p
          className="
            mx-auto
            mt-6
            max-w-[600px]
            text-[14px]
            leading-7
            text-slate-400
          "
        >
          Capture. Understand. Link. Update.
          <br className="hidden sm:block" />
          Build a smarter execution history with Pravaha.
        </p>


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
            className="
              group
              inline-flex
              h-11
              items-center
              gap-2
              rounded-md
              bg-[#3488ff]
              px-5
              text-[13px]
              font-semibold
              text-white
              shadow-[0_8px_30px_rgba(52,136,255,0.25)]
              transition-all
              duration-200
              hover:-translate-y-0.5
              hover:bg-[#4392ff]
              hover:shadow-[0_12px_35px_rgba(52,136,255,0.35)]
            "
          >
            <span>
              Try Pravaha Prototype
            </span>

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
            className="
              inline-flex
              h-11
              items-center
              justify-center
              rounded-md
              border
              border-white/15
              bg-white/[0.04]
              px-5
              text-[13px]
              font-medium
              text-slate-200
              backdrop-blur-sm
              transition-all
              duration-200
              hover:border-white/25
              hover:bg-white/[0.08]
              hover:text-white
            "
          >
            Explore Dashboard
          </button>

        </div>

      </div>
    </section>
  );
}

export default FinalCTA;