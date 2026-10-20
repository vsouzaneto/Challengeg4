"use client";

import { Bar, BarChart, XAxis, YAxis } from "recharts";

import { ChartTip, tipRow } from "@/components/app/chart-tip";
import { type ChartConfig, ChartContainer } from "@/components/ui/chart";
import { GROUP_LABELS, type GroupKey } from "@/copy/pt-BR";
import { GROUP_VISUAL } from "@/copy/visual";
import { formatInt } from "@/lib/format";
import { cn } from "@/lib/utils";

type Props = {
  /** Os grupos na ordem da API. */
  order: GroupKey[];
  /** Contagens da API (`summary`), por grupo. */
  counts: Record<GroupKey, number>;
  total: number;
  /** Clique num segmento: abre o grupo. Sem ela, o segmento só mostra o tooltip. */
  onPick?: (state: GroupKey) => void;
  className?: string;
};

/** Barra segmentada da carteira por grupo. O comprimento codifica as contagens da API e nada é escrito nela
 * (nenhum %); o tooltip traz o nome e a contagem de cada grupo. É escondida de leitores de tela, e quem a usa põe ao
 * lado a legenda com as contagens (e os botões que fazem o mesmo que o clique). */
export function GroupComposition({ order, counts, total, onPick, className }: Props) {
  const shown = order.filter((state) => counts[state] > 0);
  const config = Object.fromEntries(shown.map((state) => [state, { label: GROUP_LABELS[state], color: GROUP_VISUAL[state].fill }])) satisfies ChartConfig;
  const row = Object.fromEntries(shown.map((state) => [state, counts[state]]));
  return (
    <ChartContainer config={config} aria-hidden
                    className={cn("aspect-auto h-3 w-full rounded-full bg-muted", className)}>
      <BarChart data={[row]} layout="vertical" margin={{ top: 0, right: 0, bottom: 0, left: 0 }} barCategoryGap={0}>
        <XAxis type="number" hide domain={[0, Math.max(total, 1)]} />
        <YAxis type="category" hide />
        <ChartTip cursor={false} hideLabel
                  render={(value, name) => tipRow(GROUP_VISUAL[name as GroupKey].fill, GROUP_LABELS[name as GroupKey], formatInt(value))} />
        {shown.map((state) => (
          <Bar key={state} dataKey={state} stackId="g" fill={`var(--color-${state})`} stroke="var(--card)" strokeWidth={2} radius={4}
               isAnimationActive={false} className={onPick ? "cursor-pointer" : undefined}
               onClick={onPick ? () => onPick(state) : undefined} />
        ))}
      </BarChart>
    </ChartContainer>
  );
}
