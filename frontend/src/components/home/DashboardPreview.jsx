import UiText from "../../ui/UiText.jsx";
import {
  BookOpen,
  CalendarDays,
  Check,
  ChevronDown,
  CircleAlert,
  FileText,
  LayoutDashboard,
  Menu,
  Settings,
  Wrench,
  Zap,
} from "lucide-react";

function DashboardPreview() {
  const navItems = [
    {
      label: "Dashboard",
      icon: LayoutDashboard,
      active: true,
    },
    {
      label: "Activities",
      icon: Wrench,
    },
    {
      label: "Schedule",
      icon: CalendarDays,
    },
    {
      label: "Reports",
      icon: FileText,
    },
    {
      label: "Knowledge Base",
      icon: BookOpen,
    },
    {
      label: "Settings",
      icon: Settings,
    },
  ];

  const stats = [
    {
      number: "42%",
      label: "Overall Progress",
      change: "↗ 12%",
    },
    {
      number: "1,245",
      label: "Activities Tracked",
      change: "↗ 8%",
    },
    {
      number: "92%",
      label: "Demo Matching Score",
      change: "Illustrative value",
    },
    {
      number: "15",
      label: "Unmatched Items",
      change: "↓ 3%",
      warning: true,
    },
  ];

  const schedule = [
    {
      name: "Civil Works",
      width: "78%",
      bar: "bg-primary",
    },
    {
      name: "Piping",
      width: "88%",
      bar: "bg-success",
    },
    {
      name: "Electrical",
      width: "65%",
      bar: "bg-warning",
    },
    {
      name: "Instrumentation",
      width: "72%",
      bar: "bg-info",
    },
    {
      name: "Equipment Erection",
      width: "54%",
      bar: "bg-danger",
    },
  ];

  const activities = [
    {
      title: "Erected spool for Line 247-XX",
      subtitle: "Piping | 8:00 AM",
      score: "92%",
      icon: Wrench,
      iconBg: "bg-primary/15",
      iconColor: "text-primary",
    },
    {
      title: "Concreting of foundation F-12",
      subtitle: "Civil | 10:20 AM",
      score: "87%",
      icon: Check,
      iconBg: "bg-success/15",
      iconColor: "text-success",
    },
    {
      title: "Cable tray installation",
      subtitle: "Electrical | 12:15 PM",
      score: "90%",
      icon: Zap,
      iconBg: "bg-warning/15",
      iconColor: "text-warning",
    },
  ];

  return (
    <div
      id="dashboard"
      className="
        relative
        w-full
        overflow-hidden
        rounded-[16px]
        border
        border-border
        bg-background
        shadow-[0_30px_80px_rgba(7,32,65,0.28)]
      "
    >
      <div className="flex min-h-[440px]">

        {/* =====================================================
            SIDEBAR
        ====================================================== */}
        <aside
          className="
            hidden
            w-[150px]
            shrink-0
            flex-col
            border-r
            border-border
            bg-surface
            sm:flex
            lg:w-[165px]
          "
        >
          {/* Brand */}
          <div
            className="
              flex
              h-[52px]
              items-center
              justify-between
              border-b
              border-border
              px-3.5
            "
          >
            <img
              src="/pravaha-logo-vector.svg"
              alt="Pravaha"
              className="
                block
                h-[28px]
                w-[92px]
                object-contain
                object-left
              "
            />

            <Menu
              size={13}
              className="text-secondary"
            />
          </div>

          {/* Navigation */}
          <div className="flex flex-col gap-1 px-2 py-3">
            {navItems.map((item) => {
              const Icon = item.icon;

              return (
                <div
                  key={item.label}
                  className={`
                    flex
                    h-8
                    items-center
                    gap-2
                    rounded-md
                    px-2
                    text-[9px]
                    font-medium
                    transition
                    ${
                      item.active
                        ? "bg-primary/15 text-primary"
                        : "text-secondary hover:bg-surface/5 hover:text-secondary"
                    }
                  `}
                >
                  <Icon size={12} />

                  <span><UiText>{item.label}</UiText></span>
                </div>
              );
            })}
          </div>
        </aside>

        {/* =====================================================
            MAIN DASHBOARD
        ====================================================== */}
        <main className="min-w-0 flex-1 bg-background">

          {/* Top Header */}
          <div
            className="
              flex
              min-h-[52px]
              flex-wrap
              items-center
              justify-between
              gap-2
              border-b
              border-border
              bg-surface
              px-4
              py-2
            "
          >
            <div
              className="
                text-[13px]
                font-semibold
                text-foreground
              "
            ><UiText>
              Demo Project Overview
            </UiText></div>

            <div className="flex items-center gap-1.5">

              {/* Discipline */}
              <button
                type="button"
                className="
                  hidden
                  h-6
                  items-center
                  gap-1.5
                  rounded
                  border
                  border-border
                  bg-surface
                  px-2
                  text-[8px]
                  font-medium
                  text-secondary
                  sm:flex
                "
              >
                <span><UiText>All Disciplines</UiText></span>

                <ChevronDown
                  size={9}
                  className="text-secondary"
                />
              </button>

              {/* Date */}
              <button
                type="button"
                className="
                  hidden
                  h-6
                  items-center
                  gap-1.5
                  rounded
                  border
                  border-border
                  bg-surface
                  px-2
                  text-[8px]
                  font-medium
                  text-secondary
                  sm:flex
                "
              >
                <span><UiText>Last 30 Days</UiText></span>

                <ChevronDown
                  size={9}
                  className="text-secondary"
                />
              </button>
            </div>
          </div>

          {/* =================================================
              STATS
          ================================================== */}
          <div
            className="
              grid
              grid-cols-2
              gap-2
              p-3
              lg:grid-cols-4
            "
          >
            {stats.map((stat) => (
              <div
                key={stat.label}
                className={`
                  rounded-lg
                  border
                  bg-surface
                  px-3
                  py-2.5
                  shadow-[0_2px_8px_rgba(15,23,42,0.03)]
                  ${
                    stat.warning
                      ? "border-orange-200"
                      : "border-border"
                  }
                `}
              >
                <div
                  className="
                    text-[20px]
                    font-bold
                    leading-none
                    tracking-tight
                    text-foreground
                  "
                >
                  {stat.number}
                </div>

                <div
                  className="
                    mt-1
                    text-[8px]
                    font-medium
                    text-secondary
                  "
                >
                  <UiText>{stat.label}</UiText>
                </div>

                <div
                  className={`
                    mt-1.5
                    text-[8px]
                    font-semibold
                    ${
                      stat.warning
                        ? "text-orange-500"
                        : "text-success"
                    }
                  `}
                >
                  {stat.change}
                </div>
              </div>
            ))}
          </div>

          {/* =================================================
              LOWER CONTENT
          ================================================== */}
          <div
            className="
              grid
              grid-cols-1
              gap-2.5
              px-3
              pb-3
              lg:grid-cols-[1.12fr_0.88fr]
            "
          >

            {/* =================================================
                SCHEDULE
            ================================================== */}
            <div
              className="
                rounded-lg
                border
                border-border
                bg-surface
                p-3
                shadow-[0_2px_8px_rgba(15,23,42,0.03)]
              "
            >
              <div
                className="
                  mb-3
                  text-[10px]
                  font-semibold
                  text-foreground
                "
              ><UiText>
                Schedule Progress (L5/L6)
              </UiText></div>

              {/* Header */}
              <div
                className="
                  mb-2.5
                  grid
                  grid-cols-[105px_1fr]
                  items-center
                  text-[7px]
                  font-semibold
                  uppercase
                  tracking-wide
                  text-secondary
                  lg:grid-cols-[115px_1fr]
                "
              >
                <span><UiText>Discipline</UiText></span>
                <span><UiText>Today</UiText></span>
              </div>

              {/* Rows */}
              <div className="space-y-2.5">
                {schedule.map((item) => (
                  <div
                    key={item.name}
                    className="
                      grid
                      grid-cols-[105px_1fr]
                      items-center
                      gap-2
                      lg:grid-cols-[115px_1fr]
                    "
                  >
                    <span
                      className="
                        truncate
                        text-[8px]
                        font-medium
                        text-secondary
                      "
                    >
                      {item.name}
                    </span>

                    <div
                      className="
                        h-1.5
                        overflow-hidden
                        rounded-full
                        bg-surface
                      "
                    >
                      <div
                        className={`
                          h-full
                          rounded-full
                          ${item.bar}
                        `}
                        style={{
                          width: item.width,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Months */}
              <div
                className="
                  ml-[105px]
                  mt-4
                  grid
                  grid-cols-4
                  text-[7px]
                  font-medium
                  text-secondary
                  lg:ml-[115px]
                "
              >
                <span>Aug</span>
                <span className="text-center">Sep</span>
                <span className="text-center">Oct</span>
                <span className="text-right">Nov</span>
              </div>
            </div>

            {/* =================================================
                RECENT ACTIVITIES
            ================================================== */}
            <div
              className="
                rounded-lg
                border
                border-border
                bg-surface
                p-3
                shadow-[0_2px_8px_rgba(15,23,42,0.03)]
              "
            >
              {/* Heading */}
              <div
                className="
                  mb-2
                  flex
                  items-center
                  justify-between
                  gap-2
                "
              >
                <span
                  className="
                    text-[10px]
                    font-semibold
                    text-foreground
                  "
                ><UiText>
                  Recent Activity Updates
                </UiText></span>

                <button
                  type="button"
                  className="
                    text-[7px]
                    font-semibold
                    text-primary
                  "
                ><UiText>
                  View All →
                </UiText></button>
              </div>

              {/* Activities */}
              <div className="divide-y divide-slate-100">

                {activities.map((activity) => {
                  const Icon = activity.icon;

                  return (
                    <div
                      key={activity.title}
                      className="
                        flex
                        items-center
                        gap-2
                        py-2.5
                      "
                    >
                      <div
                        className={`
                          flex
                          h-6
                          w-6
                          shrink-0
                          items-center
                          justify-center
                          rounded-full
                          ${activity.iconBg}
                          ${activity.iconColor}
                        `}
                      >
                        <Icon size={10} />
                      </div>

                      <div
                        className="
                          min-w-0
                          flex-1
                        "
                      >
                        <strong
                          className="
                            block
                            truncate
                            text-[8px]
                            font-semibold
                            text-foreground
                          "
                        >
                          <UiText>{activity.title}</UiText>
                        </strong>

                        <small
                          className="
                            mt-0.5
                            block
                            text-[7px]
                            text-secondary
                          "
                        >
                          <UiText>{activity.subtitle}</UiText>
                        </small>
                      </div>

                      <span
                        className="
                          shrink-0
                          text-right
                          text-[7px]
                          font-semibold
                          leading-3
                          text-success
                        "
                      ><UiText>
                        Matched
                        </UiText><br />
                        {activity.score}
                      </span>
                    </div>
                  );
                })}

                {/* Review Activity */}
                <div
                  className="
                    flex
                    items-center
                    gap-2
                    py-2.5
                  "
                >
                  <div
                    className="
                      flex
                      h-6
                      w-6
                      shrink-0
                      items-center
                      justify-center
                      rounded-full
                      bg-red-500/10
                      text-red-500
                    "
                  >
                    <CircleAlert size={10} />
                  </div>

                  <div
                    className="
                      min-w-0
                      flex-1
                    "
                  >
                    <strong
                      className="
                        block
                        truncate
                        text-[8px]
                        font-semibold
                        text-foreground
                      "
                    ><UiText>
                      Unmatched activity - Review required
                    </UiText></strong>

                    <small
                      className="
                        mt-0.5
                        block
                        text-[7px]
                        text-secondary
                      "
                    >
                      Instrumentation | 2:40 PM
                    </small>
                  </div>

                  <span
                    className="
                      shrink-0
                      rounded
                      bg-red-50
                      px-1.5
                      py-1
                      text-[7px]
                      font-semibold
                      text-red-500
                    "
                  ><UiText>
                    Review
                  </UiText></span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default DashboardPreview;
