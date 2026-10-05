const CURRENT_DATE_FORMAT = new Intl.DateTimeFormat("en-IN", {
  weekday: "long",
  day: "2-digit",
  month: "long",
  year: "numeric",
});

export const formatCurrentDate = () => CURRENT_DATE_FORMAT.format(new Date());
