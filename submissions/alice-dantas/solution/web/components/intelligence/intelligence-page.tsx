"use client";

import { BookOpen, Inbox, Lightbulb } from "lucide-react";
import { useEffect, useState } from "react";

import { DataWarning, ErrorAlert } from "@/components/app/error-alert";
import { PageHeader } from "@/components/app/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia } from "@/components/ui/empty";
import { Skeleton } from "@/components/ui/skeleton";
import { INTELLIGENCE, PAGES, UI, historyEmptyText, type GroupKey } from "@/copy/pt-BR";
import { api } from "@/lib/api";
import type { Intelligence, IntelligenceFilter } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import {
  METRICS, type DealOutcome, type Dimension, type MetricKey, apiQuery, filterFromQuery, queryChanges, withSegment,
} from "@/lib/intelligence";
import { useApi } from "@/lib/use-api";
import { useQuery } from "@/lib/use-query";

import { BreakdownExplorer } from "./breakdown-explorer";
import { DealsSheet, type DealsRequest } from "./deals-sheet";
import { HistorySummary } from "./history-summary";
import { ActiveFilters, IntelligenceFilters } from "./intelligence-filters";
import { CrosstabExplorer } from "./crosstab-explorer";
import { AnalysesPanel, GuidePanel, type Panel } from "./side-panels";
import { TimeResults } from "./time-results";

// O painel lateral fecha com uma animação; a rolagem até a seção espera ele sair.
const PANEL_CLOSE_MS = 250;

/** Inteligência comercial (ADR-007). No corpo, só números, gráficos e tabelas, com a leitura de cada um logo
 * abaixo; os diagnósticos e as descobertas ficam em "Ver análises", e as definições em "Como funciona". Descreve o
 * histórico; a lista de trabalho fica na Carteira. */
export function IntelligencePage() {
  const [query, setQuery] = useQuery();
  const filter = filterFromQuery(query);
  const key = `intelligence:${apiQuery(filter)}`;
  const sellers = useApi(() => api.sellers(), "sellers");
  const intelligence = useApi(() => api.intelligence(filter), key);
  const [deals, setDeals] = useState<DealsRequest | null>(null);
  const [panel, setPanel] = useState<Panel | null>(null);
  // As opções dos filtros ficam da última resposta enquanto a próxima carrega.
  const [options, setOptions] = useState<Intelligence["options"] | null>(null);
  const payload = intelligence.data;
  useEffect(() => {
    if (payload) setOptions(payload.options);
  }, [payload]);

  const dimensions = payload?.breakdowns.map((b) => b.dimension) ?? [];
  const asked = query.get("ver") as Dimension | null;
  const dimension = asked && dimensions.includes(asked) ? asked : dimensions[0];
  const askedMetric = query.get("metrica") as MetricKey | null;
  const metric: MetricKey = askedMetric && METRICS.includes(askedMetric) ? askedMetric : "revenue";
  const analyses = payload ? payload.diagnostics.length + payload.findings.length : 0;

  const change = (changes: Partial<IntelligenceFilter>) => {
    setDeals(null);
    setQuery(queryChanges(changes));
  };
  const openDeals = (outcome: DealOutcome, group: GroupKey | null = null, segment: Partial<IntelligenceFilter> = {}) => {
    setPanel(null);
    setDeals({ filter: withSegment(filter, segment), outcome, group });
  };
  const jump = (section: string) => {
    setPanel(null);
    window.setTimeout(() => document.getElementById(section)?.scrollIntoView?.({ behavior: "smooth" }), PANEL_CLOSE_MS);
  };
  const viewBy = (next: Dimension) => {
    setQuery({ ver: next });
    jump("explorar");
  };

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-4">
        <PageHeader
          title={PAGES.inteligencia.title}
          description={PAGES.inteligencia.description}
          actions={
            <div className="flex gap-2 lg:flex-wrap">
              <IntelligenceFilters filter={filter} options={options} sellers={sellers.data?.sellers ?? []}
                                   onChange={change} />
              <Button variant="outline" className="relative max-lg:size-9 max-lg:px-0" onClick={() => setPanel("analyses")} disabled={!payload}>
                <Lightbulb aria-hidden />
                <span className="max-lg:sr-only">{INTELLIGENCE.analyses.button}</span>
                {payload && <Badge variant="secondary" className="tabular-nums max-lg:absolute max-lg:-top-2 max-lg:-right-2 max-lg:h-4 max-lg:min-w-4 max-lg:px-1 max-lg:text-[0.625rem]">{formatInt(analyses)}</Badge>}
              </Button>
              <Button variant="outline" className="relative max-lg:size-9 max-lg:px-0" onClick={() => setPanel("guide")}>
                <BookOpen aria-hidden />
                <span className="max-lg:sr-only">{INTELLIGENCE.guide.button}</span>
              </Button>
            </div>
          }
        />
        <ActiveFilters filter={filter} sizes={options?.sizes ?? []} onChange={change} />
      </div>

      {(intelligence.error ?? sellers.error) && <ErrorAlert message={(intelligence.error ?? sellers.error) as string} />}

      {intelligence.loading && (
        <div className="flex flex-col gap-4" aria-busy="true" aria-label={UI.loading}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[0, 1, 2, 3].map((n) => <Skeleton key={n} className="h-28 rounded-xl" />)}
          </div>
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      )}

      {payload && dimension && (
        <>
          {!payload.meta.audited && <DataWarning />}
          {payload.history_empty && (
            <Empty className="border border-dashed">
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <Inbox aria-hidden />
                </EmptyMedia>
                <EmptyDescription>{historyEmptyText(payload.history_empty)}</EmptyDescription>
              </EmptyHeader>
            </Empty>
          )}
          <HistorySummary payload={payload} />
          <BreakdownExplorer key={dimension} breakdowns={payload.breakdowns} sizes={payload.options.sizes}
                             dimension={dimension} metric={metric}
                             onDimension={(next) => setQuery({ ver: next })}
                             onMetric={(next) => setQuery({ metrica: next === "revenue" ? null : next })}
                             onFilter={change} onDeals={(segment) => openDeals("won", null, segment)} />
          {payload.matrix.rows.length > 0 && (
            <CrosstabExplorer matrix={payload.matrix} crosstabs={payload.crosstabs} onDeals={(segment) => openDeals("won", null, segment)} />
          )}
          <TimeResults payload={payload} />
          <AnalysesPanel open={panel === "analyses"} onClose={() => setPanel(null)} diagnostics={payload.diagnostics}
                         findings={payload.findings} filter={filter} onViewBy={viewBy} onJump={jump}
                         onDeals={(outcome, group) => openDeals(outcome, group ?? null)} />
          <DealsSheet request={deals} sizes={payload.options.sizes} onChange={setDeals} />
        </>
      )}
      <GuidePanel open={panel === "guide"} onClose={() => setPanel(null)} />
    </div>
  );
}
