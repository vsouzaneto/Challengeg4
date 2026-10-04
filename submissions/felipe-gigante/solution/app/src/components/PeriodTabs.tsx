import Link from "next/link";
import { PERIODS } from "@/lib/analytics";

export function PeriodTabs({ current, base }: { current: number; base: string }) {
  return (
    <div className="inline-flex rounded-lg border border-line bg-offwhite p-1">
      {PERIODS.map((p) => (
        <Link key={p} href={`${base}?p=${p}`} className={`rounded-md px-3 py-1.5 text-xs font-semibold ${p === current ? "bg-navy text-white shadow" : "text-muted hover:text-navy"}`}>
          {p === 1 ? "24h" : `${p}d`}
        </Link>
      ))}
    </div>
  );
}
