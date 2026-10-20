"use client";

import { Filter, List, type LucideIcon } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { InfoPopover } from "@/components/app/info-popover";
import { SortableHead } from "@/components/app/sortable-head";
import { TablePagination } from "@/components/app/table-pagination";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import {
  CHANCE_LABELS, DIMENSION_LABELS, DIMENSION_PLURALS, INTELLIGENCE, METRIC_LABELS, UI, chanceShort, chanceSupport, chanceText,
  countryLabel, driversText, sectorLabel, spreadText,
  segmentLabel, sizeLabel,
} from "@/copy/pt-BR";
import { CONCEPT_ICONS } from "@/copy/visual";
import type { Breakdown, IntelligenceFilter, Segment, SizeBand } from "@/lib/contract";
import { formatCompact, formatInt, formatPct, formatWhole } from "@/lib/format";
import { METRICS, type Dimension, type MetricKey, metricValue } from "@/lib/intelligence";
import { PAGE_SIZE } from "@/lib/pagination";
import { useSort } from "@/lib/sort";
import { cn } from "@/lib/utils";

import { BreakdownChart } from "./breakdown-chart";
import { DriverBar } from "./driver-bar";

const Compare = CONCEPT_ICONS.compare;

const text = INTELLIGENCE.explore;
type Column = "name" | "sector" | "location" | "size" | "products" | "sellers" | "closed" | "won" | "lost" | "winRate" | "ticket" |
  "revenue" | "share" | "open";
const CHART_ROWS = 10;

type Props = {
  breakdowns: Breakdown[];
  sizes: SizeBand[];
  dimension: Dimension;
  metric: MetricKey;
  onDimension: (dimension: Dimension) => void;
  onMetric: (metric: MetricKey) => void;
  onFilter: (changes: Partial<IntelligenceFilter>) => void;
  onDeals: (segment: Partial<IntelligenceFilter>) => void;
};

function Choice<T extends string>({ label, value, options, labels, onChange }: {
  label: string; value: T; options: readonly T[]; labels: Record<T, string>; onChange: (value: T) => void;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <Select value={value} onValueChange={(next) => onChange(next as T)}>
        <SelectTrigger aria-label={label} className="w-full sm:w-52">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => <SelectItem key={option} value={option}>{labels[option]}</SelectItem>)}
        </SelectContent>
      </Select>
    </div>
  );
}

const number = (value: number | null, format: (v: number) => string) => (value === null ? UI.empty : format(value));

/** Ação da linha só com ícone: o tooltip diz o que ela faz, e o mesmo texto é o nome para leitores de tela. */
function RowAction({ label, icon: Icon, onClick }: { label: string; icon: LucideIcon; onClick: () => void }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label={label} onClick={onClick}>
          <Icon aria-hidden />
        </Button>
      </TooltipTrigger>
      <TooltipContent>{label}</TooltipContent>
    </Tooltip>
  );
}

/** Um recorte por vez, com a tabela sempre visível. Pessoas em ordem alfabética e sem gráfico (a API manda a
 * ordem); os demais recortes por receita, com o gráfico da métrica escolhida a partir de telas médias. */
export function BreakdownExplorer({ breakdowns, sizes, dimension, metric, onDimension, onMetric, onFilter, onDeals }: Props) {
  const breakdown = breakdowns.find((b) => b.dimension === dimension) ?? breakdowns[0];
  const [page, setPage] = useState(1);
  const people = breakdown.order === "alphabetical";
  const isAccount = breakdown.dimension === "account";
  const label = (segment: Segment) => segmentLabel(breakdown.dimension, segment.key, sizes);
  const accessors = useMemo<Record<Column, (segment: Segment) => string | number | null>>(() => ({
    name: (s) => segmentLabel(breakdown.dimension, s.key, sizes),
    sector: (s) => (s.profile?.sector ? sectorLabel(s.profile.sector) : null),
    location: (s) => (s.profile?.location ? countryLabel(s.profile.location) : null),
    size: (s) => s.profile?.size ?? null,
    products: (s) => s.profile?.products_bought ?? null,
    sellers: (s) => s.profile?.sellers ?? null,
    closed: (s) => s.history.closed,
    won: (s) => s.history.won,
    lost: (s) => s.history.lost,
    winRate: (s) => s.history.win_rate?.value ?? null,
    ticket: (s) => s.history.ticket,
    revenue: (s) => s.history.revenue,
    share: (s) => s.revenue_share,
    open: (s) => s.open,
  }), [breakdown.dimension, sizes]);
  const { sorted, state, toggle } = useSort(breakdown.segments, accessors, () => setPage(1));
  const rows = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const chartRows = breakdown.segments.filter((s) => s.key !== null).slice(0, CHART_ROWS)
    .map((s) => ({ key: s.key, label: label(s), value: metricValue(s.history, metric) }));
  const dimensions = breakdowns.map((b) => b.dimension);
  const sizeOf = (key: string | null) => {
    const band = sizes.find((b) => b.key === key);
    return band ? sizeLabel(band, sizes) : UI.empty;
  };

  return (
    <section aria-labelledby="explore" className="flex scroll-mt-24 flex-col gap-4" id="explorar">
      <h2 id="explore" className="text-lg font-semibold">{text.title}</h2>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <Choice label={text.viewBy} value={breakdown.dimension} options={dimensions} labels={DIMENSION_LABELS}
                onChange={(next) => { setPage(1); onDimension(next); }} />
        {!people && <Choice label={text.metric} value={metric} options={METRICS} labels={METRIC_LABELS} onChange={onMetric} />}
      </div>

      <Card className="gap-4 pb-0">
        <CardHeader>
          <CardTitle className="font-semibold">{DIMENSION_LABELS[breakdown.dimension]}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 px-0">
          {!people && chartRows.length > 1 && (
            <div className="hidden flex-col gap-1 px-6 md:flex">
              <BreakdownChart rows={chartRows} metric={metric} className="h-72"
                              onSelect={(key) => onDeals({ [breakdown.dimension]: key })} />
              <p className="text-xs text-muted-foreground">{text.chartNote}</p>
            </div>
          )}
          {breakdown.segments.length === 0 ? (
            <p className="px-6 pb-6 text-sm text-muted-foreground">{text.empty}</p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <SortableHead column="name" state={state} onSort={toggle} className="pl-6"
                                  help={text.columnHelp.name(DIMENSION_LABELS[breakdown.dimension])}>
                      {DIMENSION_LABELS[breakdown.dimension]}
                    </SortableHead>
                    {isAccount && <SortableHead column="sector" state={state} onSort={toggle} help={text.columnHelp.sector}>{text.columns.sector}</SortableHead>}
                    {isAccount && <SortableHead column="location" state={state} onSort={toggle} help={text.columnHelp.location}>{text.columns.location}</SortableHead>}
                    {isAccount && <SortableHead column="size" state={state} onSort={toggle} help={text.columnHelp.size}>{text.columns.size}</SortableHead>}
                    {isAccount && <SortableHead column="products" state={state} onSort={toggle} help={text.columnHelp.products} numeric>{text.columns.products}</SortableHead>}
                    {isAccount && <SortableHead column="sellers" state={state} onSort={toggle} help={text.columnHelp.sellers} numeric>{text.columns.sellers}</SortableHead>}
                    <SortableHead column="closed" state={state} onSort={toggle} help={text.columnHelp.closed} numeric>{text.columns.closed}</SortableHead>
                    <SortableHead column="won" state={state} onSort={toggle} help={text.columnHelp.won} numeric>{text.columns.won}</SortableHead>
                    <SortableHead column="lost" state={state} onSort={toggle} help={text.columnHelp.lost} numeric>{text.columns.lost}</SortableHead>
                    <SortableHead column="winRate" state={state} onSort={toggle} help={text.columnHelp.winRate} numeric>{text.columns.winRate}</SortableHead>
                    <SortableHead column="ticket" state={state} onSort={toggle} help={text.columnHelp.ticket} numeric>{text.columns.ticket}</SortableHead>
                    <SortableHead column="revenue" state={state} onSort={toggle} help={text.columnHelp.revenue} numeric>{text.columns.revenue}</SortableHead>
                    <SortableHead column="share" state={state} onSort={toggle} help={text.columnHelp.share} numeric>{text.columns.share}</SortableHead>
                    <SortableHead column="open" state={state} onSort={toggle} help={text.columnHelp.open} numeric>{text.columns.open}</SortableHead>
                    <TableHead className="pr-6 text-right">{text.columns.actions}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.map((segment) => {
                    const { history, profile } = segment;
                    const name = label(segment);
                    return (
                      <TableRow key={segment.key ?? "sem-dado"}>
                        <TableCell className={cn("pl-6 font-medium", segment.key === null && "text-muted-foreground")}>
                          {name}
                        </TableCell>
                        {isAccount && <TableCell>{profile?.sector ? sectorLabel(profile.sector) : UI.empty}</TableCell>}
                        {isAccount && <TableCell>{profile?.location ? countryLabel(profile.location) : UI.empty}</TableCell>}
                        {isAccount && <TableCell className="whitespace-nowrap">{sizeOf(profile?.size ?? null)}</TableCell>}
                        {isAccount && (
                          <TableCell className="text-right tabular-nums">
                            {profile ? text.productsOf(profile.products_bought, profile.products_total) : UI.empty}
                          </TableCell>
                        )}
                        {isAccount && <TableCell className="text-right tabular-nums">{profile ? profile.sellers : UI.empty}</TableCell>}
                        <TableCell className="text-right tabular-nums">{formatInt(history.closed)}</TableCell>
                        <TableCell className="text-right tabular-nums">{formatInt(history.won)}</TableCell>
                        <TableCell className="text-right tabular-nums">{formatInt(history.lost)}</TableCell>
                        <TableCell className="text-right tabular-nums">
                          {history.win_rate ? (
                            <span className="flex flex-col items-end">
                              <span>{formatPct(history.win_rate.value)}</span>
                              <span className="text-xs text-muted-foreground">
                                {text.rateRange(history.win_rate.low, history.win_rate.high)}
                              </span>
                            </span>
                          ) : UI.empty}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">{number(history.ticket, formatWhole)}</TableCell>
                        <TableCell className="text-right tabular-nums">{formatCompact(history.revenue)}</TableCell>
                        <TableCell className="text-right tabular-nums">{number(segment.revenue_share, formatPct)}</TableCell>
                        <TableCell className="text-right tabular-nums">{formatInt(segment.open)}</TableCell>
                        <TableCell className="pr-6 text-right">
                          {segment.key !== null && (
                            <span className="flex justify-end gap-1">
                              <RowAction label={text.filterBy(name)} icon={Filter}
                                         onClick={() => onFilter({ [breakdown.dimension]: segment.key })} />
                              <RowAction label={text.dealsOf(name)} icon={List}
                                         onClick={() => onDeals({ [breakdown.dimension]: segment.key })} />
                            </span>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
              <TablePagination page={page} total={breakdown.segments.length} pageSize={PAGE_SIZE} onPage={setPage} />
            </>
          )}
        </CardContent>
        {/* As leituras vêm depois dos números, em dois blocos: a diferença é real? e de onde vem a receita. */}
        <CardFooter className="flex-col items-stretch gap-3 border-t pb-6 text-sm">
          <div className={cn("grid gap-3", breakdown.drivers && "lg:grid-cols-2")}>
            <div className="flex flex-col gap-2 rounded-xl border bg-muted/40 p-4">
              <p className="flex items-center gap-1 font-medium">
                {text.reality.title(DIMENSION_PLURALS[breakdown.dimension])}
                <InfoPopover label={text.reality.label}>{chanceText(breakdown.dimension, breakdown.chance)}</InfoPopover>
              </p>
              <Badge variant={breakdown.chance.verdict === "beyond_chance" ? "secondary" : "outline"} className="w-fit">
                <Compare data-icon="inline-start" aria-hidden />
                {CHANCE_LABELS[breakdown.chance.verdict]}
              </Badge>
              <p className="text-muted-foreground">{chanceShort(breakdown.chance)}</p>
              <p className="text-xs text-muted-foreground tabular-nums">{chanceSupport(breakdown.dimension, breakdown.chance)}</p>
            </div>
            {breakdown.drivers && (
              <div className="flex flex-col gap-2 rounded-xl border bg-muted/40 p-4">
                <p className="flex items-center gap-1 font-medium">
                  {text.sources.title}
                  <InfoPopover label={text.sources.label}>{driversText(breakdown.dimension, breakdown.drivers)}</InfoPopover>
                </p>
                <p className="tabular-nums">{spreadText(breakdown.dimension, breakdown.drivers)}</p>
                <p className="text-xs text-muted-foreground">{text.sources.caption}</p>
                <DriverBar drivers={breakdown.drivers} />
              </div>
            )}
          </div>
          {people && <p className="text-xs text-pretty text-muted-foreground">{text.peopleNote}</p>}
          {isAccount && (
            <p className="text-xs text-pretty text-muted-foreground">
              {text.accountNote}{" "}
              <Link href="/como-funciona#nao-usa" className="font-medium text-primary-strong underline underline-offset-4">
                {text.accountNoteSee}
              </Link>
            </p>
          )}
        </CardFooter>
      </Card>
    </section>
  );
}
