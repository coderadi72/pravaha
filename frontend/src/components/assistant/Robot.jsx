import { useId } from "react";

export default function Robot({ state = "idle" }) {
  const id = useId().replace(/:/g, "");
  const concerned = state === "error" || state === "fallback";
  return <svg className={`pr-robot is-${state}`} viewBox="0 0 64 64" aria-hidden="true">
    <defs>
      <linearGradient id={`${id}-shell`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fff" /><stop offset=".55" stopColor="#edf2f6" /><stop offset="1" stopColor="#b9c8d5" /></linearGradient>
      <linearGradient id={`${id}-screen`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#36c2ff" /><stop offset="1" stopColor="#087ee4" /></linearGradient>
      <linearGradient id={`${id}-side`}><stop stopColor="#dce5ed" /><stop offset="1" stopColor="#8399ad" /></linearGradient>
    </defs>
    <ellipse className="pr-pet-shadow" cx="32" cy="61" rx="14" ry="2" fill="#2a6390" opacity=".13" />
    <g className="pr-pet-body">
      <path d="M31 14c0-7 4-10 12-10" stroke="#687e91" strokeWidth="2" strokeLinecap="round" fill="none" />
      <circle className="pr-pet-signal" cx="44" cy="4" r="3" fill="#2bb9ff" /><circle cx="43" cy="3" r="1" fill="#bfefff" />
      <rect x="25" y="45" width="17" height="13" rx="5" fill={`url(#${id}-shell)`} stroke="#a2b4c5" strokeWidth=".8" />
      <rect x="29" y="48" width="8" height="6" rx="1.5" fill={`url(#${id}-screen)`} />
      <rect x="24" y="56" width="7" height="4" rx="2" fill="#168fdf" /><rect x="35" y="56" width="7" height="4" rx="2" fill="#168fdf" />
      <rect x="8" y="16" width="49" height="34" rx="12" fill={`url(#${id}-side)`} />
      <rect x="6" y="14" width="48" height="34" rx="12" fill={`url(#${id}-shell)`} stroke="#a5b7c7" strokeWidth=".8" />
      <rect x="11" y="19" width="38" height="25" rx="8" fill={`url(#${id}-screen)`} stroke="#1383cb" strokeWidth=".8" />
      <path d="M17 17h20M14 24v9" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" opacity=".55" />
      <g className="pr-pet-eyes" fill="#123b65">
        <rect x="21" y="28" width="3.5" height="5" rx="1.7" /><rect x="36" y="28" width="3.5" height="5" rx="1.7" />
      </g>
      <ellipse cx="20" cy="36" rx="2.5" ry="1.3" fill="#f4a9bd" opacity=".9" /><ellipse cx="40" cy="36" rx="2.5" ry="1.3" fill="#f4a9bd" opacity=".9" />
      <path className="pr-pet-mouth" d={concerned ? "M28 36q2-2 4 0" : "M28 35q2 2.5 4 0"} fill="none" stroke="#164779" strokeWidth="1.3" strokeLinecap="round" />
    </g>
  </svg>;
}
