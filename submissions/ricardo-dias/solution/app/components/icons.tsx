import type { SVGProps } from "react";

const paths = {
  grid: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  chart: "M4 3v17h17 M8 15v-4 M13 15V7 M18 15V4",
  ticket: "M4 5h16v5a2 2 0 0 0 0 4v5H4v-5a2 2 0 0 0 0-4z M9 9h6 M9 15h6",
  model: "M12 3v4 M12 17v4 M3 12h4 M17 12h4 M7 7h10v10H7z M10 10h4v4h-4z",
  flow: "M8 3h8v5H8z M12 8v5 M5 13h14 M5 13v3 M19 13v3 M2 16h6v5H2z M16 16h6v5h-6z",
  arrow: "M5 12h14 M13 6l6 6-6 6",
  chevron: "m9 5 7 7-7 7",
  check: "m5 12 4 4L19 6",
  shield: "M12 3 3 7v5c0 5 9 9 9 9s9-4 9-9V7z m-4 9 3 3 5-6",
  alert: "m12 3 10 18H2z M12 9v5 M12 17v.5",
  info: "M12 11v6 M12 7v.5 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0",
  refresh:
    "M20 7v5h-5 M4 17v-5h5 M5.1 8a8 8 0 0 1 13.2-3L20 7 M4 17l1.7 2A8 8 0 0 0 19 16",
  sparkle: "m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z",
  copy: "M9 9h12v12H9z M5 15H3V3h12v2",
  search: "M16 16l5 5 M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0",
  clock: "M12 6v6l4 2 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0",
  people:
    "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8 M2 21v-3a7 7 0 0 1 14 0v3 M17 4a4 4 0 0 1 0 7 M19 15a6 6 0 0 1 3 6",
  book: "M12 5c-3-2-6-2-10-1v15c4-1 7-1 10 1 3-2 6-2 10-1V4c-4-1-7-1-10 1z M12 5v15",
  external: "M14 3h7v7 M10 14 21 3 M10 3H3v18h18v-7",
} as const;

export type IconName = keyof typeof paths;
export function Icon({
  name,
  ...props
}: SVGProps<SVGSVGElement> & { name: IconName }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      <path d={paths[name]} />
    </svg>
  );
}
