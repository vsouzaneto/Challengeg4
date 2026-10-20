"use client";

import { Bar, BarChart, LabelList, XAxis, YAxis } from "recharts";

import { ChartTip, tipRow } from "@/components/app/chart-tip";
import { type ChartConfig, ChartContainer } from "@/components/ui/chart";
import { METRIC_LABELS, UI, metricText } from "@/copy/pt-BR";
import type { MetricKey } from "@/lib/intelligence";
import { cn } from "@/lib/utils";

type Row = { key: string | null; label: string; value: number | null };
type Props = {
  rows: Row[];
  metric: MetricKey;
  /** Clique numa barra: abre as negociações do recorte (a mesma ação da linha da tabela). */
  onSelect?: (key: string) => void;
  className?: string;
};

/** A métrica escolhida para as primeiras linhas da tabela, com tooltip e clique para abrir as negociações. O gráfico
 * é só para o mouse e o toque (escondido de leitores de tela e em telas estreitas): a tabela traz os mesmos números
 * e a mesma ação em botões. */
export function BreakdownChart({ rows, metric, onSelect, className }: Props) {
  const config = { value: { label: METRIC_LABELS[metric], color: "var(--chart-1)" } } satisfies ChartConfig;
  const data = rows.map((row) => ({ ...row, value: row.value ?? 0, empty: row.value === null }));
  return (
    <ChartContainer config={config} className={cn("aspect-auto w-full", className)} aria-hidden>
      <BarChart data={data} layout="vertical" margin={{ left: 0, right: 64, top: 4, bottom: 4 }}>
        <XAxis type="number" hide />
        <YAxis type="category" dataKey="label" width={180} tickLine={false} axisLine={false} fontSize={12} />
        <ChartTip render={(value, _name, item) => tipRow(
          "var(--chart-1)", METRIC_LABELS[metric], item.payload?.empty ? UI.empty : metricText(metric, value),
          onSelect ? UI.chartClickHint : undefined)} />
        <Bar dataKey="value" radius={4} isAnimationActive={false} fill="var(--color-value)"
             className={onSelect ? "cursor-pointer" : undefined}
             onClick={(bar) => {
               const key = (bar as { payload?: Row }).payload?.key;
               if (onSelect && key) onSelect(key);
             }}>
          <LabelList dataKey="value" position="right" className="fill-foreground"
                     formatter={(value: unknown) => metricText(metric, Number(value))} />
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}
