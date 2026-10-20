"use client";

import { Bar, BarChart, XAxis, YAxis } from "recharts";

import { ChartTip, tipRow } from "@/components/app/chart-tip";
import { Badge } from "@/components/ui/badge";
import { type ChartConfig, ChartContainer } from "@/components/ui/chart";
import { DRIVER_SHORT, driverShareText, driverShares } from "@/copy/pt-BR";
import type { RevenueDrivers } from "@/lib/contract";

const COLORS = { volume: "var(--chart-1)", ticket: "var(--chart-2)", conversion: "var(--chart-3)" } as const;
const SWATCH = { volume: "bg-chart-1", ticket: "bg-chart-2", conversion: "bg-chart-3" } as const;

/** A decomposição da receita em três fatores: barra 100% empilhada (decorativa) e a legenda com as porcentagens da
 * API. Quando os fatores se compensam (fatia fora de [0, 1]), não desenha nada e quem usa fica com a frase. */
export function DriverBar({ drivers }: { drivers: RevenueDrivers }) {
  const shares = driverShares(drivers);
  if (!shares) return null;
  const drawn = shares.filter((d) => !d.negligible && d.share > 0);
  const config = Object.fromEntries(drawn.map((d) => [d.driver, { label: DRIVER_SHORT[d.driver], color: COLORS[d.driver] }])) satisfies ChartConfig;
  const row = Object.fromEntries(drawn.map((d) => [d.driver, d.share]));
  return (
    <div className="flex flex-col gap-2">
      <ChartContainer config={config} aria-hidden className="aspect-auto h-3 w-full rounded-full bg-muted">
        <BarChart data={[row]} layout="vertical" margin={{ top: 0, right: 0, bottom: 0, left: 0 }} barCategoryGap={0}>
          <XAxis type="number" hide domain={[0, "dataMax"]} />
          <YAxis type="category" hide />
          <ChartTip cursor={false} hideLabel
                    render={(_value, name) => tipRow(COLORS[name as keyof typeof COLORS], DRIVER_SHORT[name as keyof typeof COLORS],
                      driverShareText(drivers, name as keyof typeof COLORS))} />
          {drawn.map((d) => (
            <Bar key={d.driver} dataKey={d.driver} stackId="d" fill={`var(--color-${d.driver})`} stroke="var(--card)"
                 strokeWidth={2} radius={4} isAnimationActive={false} />
          ))}
        </BarChart>
      </ChartContainer>
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs">
        {shares.map((d) => (
          <li key={d.driver} className="flex items-center gap-1.5">
            <span aria-hidden className={`size-2 shrink-0 rounded-sm ${SWATCH[d.driver]}`} />
            <span className="text-muted-foreground">{DRIVER_SHORT[d.driver]}</span>
            {d.negligible ? (
              <Badge variant="outline">{driverShareText(drivers, d.driver)}</Badge>
            ) : (
              <span className="font-semibold tabular-nums">{driverShareText(drivers, d.driver)}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
