import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type Props = {
  value: string;
  unit?: ReactNode;
  label?: ReactNode;
  /** `hero`: um por página, no máximo. */
  size?: "hero" | "kpi" | "row";
  className?: string;
};

const SIZES = {
  hero: "text-4xl font-semibold tracking-tight",
  kpi: "text-3xl font-semibold",
  row: "text-base font-semibold",
} as const;

/** Número da API com a unidade colada e o rótulo acima. */
export function StatNumber({ value, unit, label, size = "kpi", className }: Props) {
  return (
    <div className={cn("flex flex-col gap-0.5", className)}>
      {label && <span className="text-xs font-medium text-muted-foreground">{label}</span>}
      <span className="flex items-baseline gap-1.5">
        <span className={cn("tabular-nums", SIZES[size])}>{value}</span>
        {unit && <span className="text-sm font-normal text-muted-foreground">{unit}</span>}
      </span>
    </div>
  );
}
