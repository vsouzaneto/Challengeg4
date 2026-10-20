"use client";

import { Bar, BarChart, Cell, LabelList, ReferenceLine, XAxis, YAxis } from "recharts";

import { ChartTip, tipRow } from "@/components/app/chart-tip";
import { type ChartConfig, ChartContainer } from "@/components/ui/chart";
import {
  EVIDENCE_CHART, FAMILY_LABELS, RANKER_FAMILY, RANKER_LABELS, type RankerCode, type RankerFamily,
} from "@/copy/pt-BR";
import type { Evidence } from "@/lib/contract";
import { formatPct } from "@/lib/format";
import { cn } from "@/lib/utils";

const FAMILY_FILL: Record<RankerFamily, string> = {
  reference: "var(--chart-1)", alternative: "var(--chart-2)", baseline: "var(--chart-3)",
};
const FAMILY_SWATCH: Record<RankerFamily, string> = {
  reference: "bg-chart-1", alternative: "bg-chart-2", baseline: "bg-chart-3",
};
const FAMILIES: RankerFamily[] = ["reference", "alternative", "baseline"];

/** A família de uma estratégia: a regra atual é a que a API diz (`reference`), mesmo que o catálogo mude. */
export const familyOf = (code: RankerCode, reference: RankerCode): RankerFamily =>
  code === reference ? "reference" : RANKER_FAMILY[code] === "reference" ? "alternative" : RANKER_FAMILY[code];

/** Legenda das famílias (cor nunca sozinha). Decorativa: a tabela traz os nomes e os números. */
export function FamilyLegend({ families = FAMILIES, className }: { families?: RankerFamily[]; className?: string }) {
  return (
    <ul aria-hidden className={cn("flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground", className)}>
      {families.map((family) => (
        <li key={family} className="flex items-center gap-1.5">
          <span className={cn("size-2.5 rounded-sm", FAMILY_SWATCH[family])} />
          {FAMILY_LABELS[family]}
        </li>
      ))}
    </ul>
  );
}

/** O ID da linha de uma estratégia na tabela: o clique na barra rola até ela. */
export const rankerRowId = (code: RankerCode, scope: "all" | "without") => `estrategia-${scope}-${code}`;

/** Rola até a linha da tabela da estratégia e a deixa em foco (a linha leva `tabIndex={-1}`). */
export function goToRanker(code: RankerCode, scope: "all" | "without") {
  const row = document.getElementById(rankerRowId(code, scope));
  row?.scrollIntoView({ behavior: "smooth", block: "center" });
  row?.focus({ preventScroll: true });
}

type Props = {
  evidence: Pick<Evidence, "rankers" | "reference">;
  label: string;
  className?: string;
};

/** Valor capturado por estratégia, na ordem da API, colorido por família e com uma linha tracejada no valor da
 * regra atual. É decorativo para leitores de tela e some em telas estreitas: a tabela traz os mesmos números. */
export function EvidenceChart({ evidence, label, className }: Props) {
  const config = { value: { label } } satisfies ChartConfig;
  const data = evidence.rankers.map((ranker) => ({
    code: ranker.code, label: RANKER_LABELS[ranker.code], value: ranker.val_at_k, delta: ranker.delta_val,
    text: EVIDENCE_CHART.barLabel(ranker.val_at_k, ranker.delta_val),
  }));
  const reference = evidence.rankers.find((ranker) => ranker.code === evidence.reference);
  return (
    <div className={cn("flex-col gap-2", className)} aria-hidden>
      <FamilyLegend />
      <ChartContainer config={config} className="aspect-auto min-h-72 w-full flex-1">
        <BarChart data={data} layout="vertical" margin={{ left: 0, right: 96, top: 4, bottom: 4 }}>
          <XAxis type="number" domain={[0, 1]} hide />
          <YAxis type="category" dataKey="label" width={210} tickLine={false} axisLine={false} fontSize={12} />
          {reference && (
            <ReferenceLine x={reference.val_at_k} stroke="var(--chart-1)" strokeDasharray="4 4" ifOverflow="extendDomain" />
          )}
          <ChartTip render={(value, _name, item) => {
            const entry = item.payload as unknown as (typeof data)[number];
            const family = familyOf(entry.code, evidence.reference);
            return tipRow(FAMILY_FILL[family], FAMILY_LABELS[family], formatPct(value),
              [EVIDENCE_CHART.tipDelta(entry.delta), EVIDENCE_CHART.tipClick].filter(Boolean).join(". "));
          }} />
          <Bar dataKey="value" radius={4} isAnimationActive={false} className="cursor-pointer"
               onClick={(bar) => goToRanker((bar as unknown as { payload: { code: RankerCode } }).payload.code, "all")}>
            {data.map((entry) => (
              <Cell key={entry.code} fill={FAMILY_FILL[familyOf(entry.code, evidence.reference)]} />
            ))}
            <LabelList dataKey="text" position="right" className="fill-foreground tabular-nums" fontSize={12} />
          </Bar>
        </BarChart>
      </ChartContainer>
    </div>
  );
}

type GroupedProps = {
  evidence: Pick<Evidence, "rankers" | "without_no_outcome" | "reference">;
  className?: string;
};

/** "Sem as que nunca fecharam": para cada estratégia do recorte, a barra com todas as negociações (linha de base,
 * cinza) e a sem elas (a cor da família). A inversão aparece sem frase; todos os números vêm da API. */
export function WithoutChart({ evidence, className }: GroupedProps) {
  const config = {
    all: { label: EVIDENCE_CHART.all, color: "var(--chart-3)" },
    without: { label: EVIDENCE_CHART.without, color: "var(--chart-1)" },
  } satisfies ChartConfig;
  const data = evidence.without_no_outcome.flatMap((ranker) => {
    const all = evidence.rankers.find((r) => r.code === ranker.code);
    return all ? [{
      code: ranker.code, label: RANKER_LABELS[ranker.code], all: all.val_at_k, without: ranker.val_at_k,
    }] : [];
  });
  if (!data.length) return null;
  return (
    <div className={cn("flex-col gap-2", className)} aria-hidden>
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
        <li className="flex items-center gap-1.5"><span className="size-2.5 rounded-sm bg-chart-3" />{EVIDENCE_CHART.all}</li>
        <li className="flex items-center gap-1.5">
          <span className="flex gap-0.5">
            <span className="size-2.5 rounded-sm bg-chart-1" />
            <span className="size-2.5 rounded-sm bg-chart-2" />
          </span>
          {EVIDENCE_CHART.without}
        </li>
      </ul>
      <ChartContainer config={config} className="aspect-auto h-56 w-full">
        <BarChart data={data} layout="vertical" margin={{ left: 0, right: 56, top: 4, bottom: 4 }} barGap={2}>
          <XAxis type="number" domain={[0, 1]} hide />
          <YAxis type="category" dataKey="label" width={210} tickLine={false} axisLine={false} fontSize={12} />
          <ChartTip render={(value, name, item) => {
            const entry = item.payload as unknown as (typeof data)[number];
            const color = name === "all" ? "var(--color-all)" : FAMILY_FILL[familyOf(entry.code, evidence.reference)];
            return tipRow(color, name === "all" ? EVIDENCE_CHART.all : EVIDENCE_CHART.without, formatPct(value),
              EVIDENCE_CHART.tipClick);
          }} />
          <Bar dataKey="all" fill="var(--color-all)" radius={3} isAnimationActive={false} className="cursor-pointer"
               onClick={(bar) => goToRanker((bar as unknown as { payload: { code: RankerCode } }).payload.code, "without")}>
            <LabelList dataKey="all" position="right" className="fill-foreground tabular-nums" fontSize={12}
                       formatter={(value: unknown) => formatPct(Number(value))} />
          </Bar>
          <Bar dataKey="without" radius={3} isAnimationActive={false} className="cursor-pointer"
               onClick={(bar) => goToRanker((bar as unknown as { payload: { code: RankerCode } }).payload.code, "without")}>
            {data.map((entry) => (
              <Cell key={entry.code} fill={FAMILY_FILL[familyOf(entry.code, evidence.reference)]} />
            ))}
            <LabelList dataKey="without" position="right" className="fill-foreground tabular-nums" fontSize={12}
                       formatter={(value: unknown) => formatPct(Number(value))} />
          </Bar>
        </BarChart>
      </ChartContainer>
    </div>
  );
}
