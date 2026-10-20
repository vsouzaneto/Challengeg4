"use client";

import { ArrowRight, Inbox } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef } from "react";

import { DataWarning, ErrorAlert } from "@/components/app/error-alert";
import { PageHeader } from "@/components/app/page-header";
import { GroupTabs } from "@/components/portfolio/group-tabs";
import { ListFiltersBar, ListFiltersStatus } from "@/components/portfolio/list-filters";
import { ReasonPanel } from "@/components/portfolio/reason-panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia } from "@/components/ui/empty";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PAGES, TEAM, UI, pipelineEmptyText } from "@/copy/pt-BR";
import { api } from "@/lib/api";
import type { Group } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import { defaultTab, filterGroups, filtersToQuery, hasFilters, parseFilters, productsIn, type ListFilters } from "@/lib/portfolio";
import { emptyFilter } from "@/lib/intelligence";
import { filterOptions } from "@/lib/team";
import { useApi } from "@/lib/use-api";
import { useExpanded } from "@/lib/use-expanded";
import { useQuery } from "@/lib/use-query";

import { BySellerTable } from "./by-seller-table";
import { TeamFilters } from "./team-filters";
import { TeamStats } from "./team-stats";
import { TeamSummary } from "./team-summary";

export function TeamPage() {
  const [query, setQuery] = useQuery();
  const manager = query.get("gerente");
  const office = query.get("escritorio");
  const sellers = useApi(() => api.sellers(), "sellers");
  const key = `team:${manager ?? ""}:${office ?? ""}`;
  const pipeline = useApi(() => api.teamPipeline({ manager, office }), key);
  // Valor de tabela, vendas e taxa de ganho do mesmo filtro vêm da Inteligência; se falhar, esses cartões ficam vazios.
  const value = useApi(() => api.intelligence({ ...emptyFilter(), manager, office }), `team-value:${manager ?? ""}:${office ?? ""}`);
  const rows = useExpanded();

  const options = filterOptions(sellers.data?.sellers ?? [], manager, office);
  const payload = pipeline.data;
  const fromQuery = query.get("grupo");
  const tab = payload?.groups.some((g) => g.state === fromQuery) ? (fromQuery as Group["state"]) : payload && defaultTab(payload);
  const filters = parseFilters(query);
  const groups = payload ? filterGroups(payload.groups, filters) : [];
  const changeFilters = useCallback((next: ListFilters) => setQuery(filtersToQuery(next)), [setQuery]);
  const error = sellers.error ?? pipeline.error;
  // Duas análises sob os números, em abas, para a página não virar uma rolagem longa. Fica na URL.
  const view = query.get("visao") === "oportunidades" ? "oportunidades" : "vendedores";
  // Da legenda da composição para a lista: rola só depois que a URL mudou e a aba montou.
  const scrollToList = useRef(false);
  useEffect(() => {
    if (!scrollToList.current || view !== "oportunidades") return;
    scrollToList.current = false;
    // Um quadro depois do commit: a troca de aba ainda ajusta o layout no mesmo quadro.
    window.requestAnimationFrame(() =>
      document.getElementById("grupos")?.scrollIntoView({ behavior: "smooth", block: "start" }));
  }, [view, tab]);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={PAGES.equipe.title}
        description={PAGES.equipe.description}
        actions={
          <Button asChild variant="link" className="w-fit px-0 text-primary-strong">
            <Link href="/evidencia">
              {TEAM.seeEvidence}
              <ArrowRight aria-hidden />
            </Link>
          </Button>
        }
      />

      <TeamFilters
        managers={options.managers}
        offices={options.offices}
        manager={manager}
        office={office}
        onChange={(changes) => {
          rows.reset();
          setQuery({ ...changes, grupo: null });
        }}
      />

      {error && <ErrorAlert message={error} />}

      {pipeline.loading && (
        <div className="flex flex-col gap-4" aria-busy="true" aria-label={UI.loading}>
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      )}

      {payload && tab && (
        <>
          {!payload.meta.audited && <DataWarning />}
          <TeamStats sellers={payload.by_seller.filter((seller) => seller.total > 0).length}
                     intelligence={value.error ? null : value.data} />
          <TeamSummary payload={payload} onPick={(state) => {
            scrollToList.current = true;
            setQuery({ visao: "oportunidades", grupo: state });
          }} />
          <Tabs value={view} onValueChange={(next) => setQuery({ visao: next === "oportunidades" ? next : null })}
                className="gap-6">
            <TabsList variant="line" aria-label={TEAM.views.label} className="w-full self-center sm:w-fit">
              <TabsTrigger value="vendedores" className="px-2 after:bg-primary sm:px-4">
                {TEAM.views.sellers}
                <Badge variant="secondary" className="tabular-nums">{formatInt(payload.by_seller.length)}</Badge>
              </TabsTrigger>
              <TabsTrigger value="oportunidades" className="px-2 after:bg-primary sm:px-4">
                {TEAM.views.opportunities}
                <Badge variant="secondary" className="tabular-nums">{formatInt(payload.summary.total)}</Badge>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="vendedores">
              {payload.by_seller.length ? (
                <BySellerTable key={key} rows={payload.by_seller} groups={payload.ordering.group_order} />
              ) : (
                <EmptyState text={TEAM.noSellers} />
              )}
            </TabsContent>

            <TabsContent value="oportunidades" className="flex flex-col gap-6">
              {payload.empty ? (
                <EmptyState text={pipelineEmptyText(payload.empty)} />
              ) : (
                <>
                  <ListFiltersBar filters={filters} onChange={changeFilters} products={productsIn(payload.groups)} />
                  <ListFiltersStatus filters={filters} shown={groups.reduce((sum, g) => sum + g.items.length, 0)}
                                     total={payload.summary.total} />
                  <GroupTabs
                    key={`${key}:${JSON.stringify(filters)}`}
                    groups={groups}
                    tab={tab}
                    onTab={(state) => setQuery({ grupo: state })}
                    expanded={rows.expanded}
                    onToggle={rows.toggle}
                    renderPanel={(item) => (
                      <ReasonPanel item={item} meta={payload.meta} onClose={() => rows.close(item.opportunity_id)} />
                    )}
                    limits={payload.meta}
                    ordering={payload.ordering}
                    filtered={hasFilters(filters)}
                    showSeller
                  />
                </>
              )}
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <Empty className="border border-dashed">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Inbox aria-hidden />
        </EmptyMedia>
        <EmptyDescription>{text}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}
