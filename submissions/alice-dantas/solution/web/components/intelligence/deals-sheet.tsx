"use client";

import { X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { ErrorAlert } from "@/components/app/error-alert";
import { TablePagination } from "@/components/app/table-pagination";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DIMENSION_LABELS, GROUP_LABELS, INTELLIGENCE, NO_ACCOUNT, OUTCOME_LABELS, UI, dealsEmptyText, sizeLabel,
  type GroupKey,
} from "@/copy/pt-BR";
import { api } from "@/lib/api";
import type { Deal, IntelligenceFilter, SizeBand } from "@/lib/contract";
import { formatDate, formatInt } from "@/lib/format";
import { type DealOutcome, activeFilters, apiQuery } from "@/lib/intelligence";
import { PAGE_SIZE } from "@/lib/pagination";
import { useApi } from "@/lib/use-api";

export type DealsRequest = { filter: IntelligenceFilter; outcome: DealOutcome; group: GroupKey | null };

const text = INTELLIGENCE.deals;
const OUTCOMES = Object.keys(OUTCOME_LABELS) as DealOutcome[];

type Props = {
  request: DealsRequest | null;
  sizes: SizeBand[];
  onChange: (request: DealsRequest | null) => void;
};

function scopeText(request: DealsRequest, sizes: SizeBand[]): string {
  const parts = activeFilters(request.filter).map((key) => {
    const value = request.filter[key] as string;
    const band = key === "size" ? sizes.find((b) => b.key === value) : undefined;
    return text.filterPart(DIMENSION_LABELS[key], band ? sizeLabel(band, sizes) : value);
  });
  if (request.group) parts.push(text.groupPart(GROUP_LABELS[request.group]));
  return text.scope(parts);
}

function DealsTable({ deals, outcome }: { deals: Deal[]; outcome: DealOutcome }) {
  const isOpen = outcome === "open";
  return (
    <Table>
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          <TableHead className="pl-4">{text.columns.id}</TableHead>
          <TableHead>{text.columns.seller}</TableHead>
          <TableHead>{text.columns.product}</TableHead>
          <TableHead>{text.columns.client}</TableHead>
          <TableHead className="text-right" title={outcome === "lost" ? text.valueHelp : undefined}>
            {outcome === "won" ? text.columns.value : text.columns.price}
          </TableHead>
          <TableHead>{isOpen ? text.columns.group : text.columns.result}</TableHead>
          <TableHead>{isOpen ? text.columns.engaged : text.columns.closed}</TableHead>
          <TableHead className="pr-4 text-right">{isOpen ? text.columns.age : text.columns.cycle}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {deals.map((deal) => {
          const value = outcome === "won" ? deal.close_value : deal.sales_price;
          const date = isOpen ? deal.engage_date : deal.close_date;
          const days = isOpen ? deal.age_days : deal.cycle_days;
          return (
            <TableRow key={deal.opportunity_id}>
              <TableCell className="pl-4 font-mono text-xs">{deal.opportunity_id}</TableCell>
              <TableCell>
                {isOpen ? (
                  <Button asChild variant="link" size="sm" className="h-auto px-0 text-primary-strong">
                    <Link href={`/carteira?vendedor=${encodeURIComponent(deal.sales_agent)}`}
                          aria-label={text.seePortfolio(deal.sales_agent)}>
                      {deal.sales_agent}
                    </Link>
                  </Button>
                ) : deal.sales_agent}
              </TableCell>
              <TableCell>{deal.product ?? UI.noProduct}</TableCell>
              <TableCell className={deal.account ? undefined : "text-muted-foreground"}>{deal.account ?? NO_ACCOUNT}</TableCell>
              <TableCell className="text-right tabular-nums">{value === null ? UI.empty : formatInt(value)}</TableCell>
              <TableCell>
                {isOpen
                  ? deal.group && <Badge variant={deal.group}>{GROUP_LABELS[deal.group]}</Badge>
                  : <Badge variant={outcome}>{text.result[outcome]}</Badge>}
              </TableCell>
              <TableCell className="tabular-nums">{date ? formatDate(date) : UI.empty}</TableCell>
              <TableCell className="pr-4 text-right tabular-nums">{days === null ? UI.empty : UI.ageDays(days)}</TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

/** As negociações por trás de um número da página: o mesmo recorte (mais a linha ou a célula clicada), um
 * desfecho por aba. As abertas vêm na ordem da regra, com o grupo; as fechadas, da mais recente. */
export function DealsSheet({ request, sizes, onChange }: Props) {
  const key = request ? `deals:${apiQuery(request.filter)}:${request.outcome}:${request.group ?? ""}` : "deals:none";
  const deals = useApi(request ? () => api.intelligenceDeals(request.filter, request.outcome, request.group) : null, key);
  const [page, setPage] = useState(1);
  useEffect(() => setPage(1), [key]);
  const data = deals.data;
  const rows = data?.deals.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE) ?? [];

  return (
    <Sheet open={Boolean(request)} onOpenChange={(open) => !open && onChange(null)}>
      {/* A largura usa a mesma variante do primitivo (data-[side=right]), senão a dele vence. */}
      <SheetContent side="right" showCloseButton={false}
                    className="gap-0 data-[side=right]:w-full data-[side=right]:sm:max-w-3xl">
        {request && (
          <>
            <SheetHeader className="border-b">
              <div className="flex items-start justify-between gap-2">
                <div className="flex flex-col gap-1.5">
                  <SheetTitle className="text-lg font-semibold">{text.title}</SheetTitle>
                  <SheetDescription>{scopeText(request, sizes)}</SheetDescription>
                </div>
                <SheetClose asChild>
                  <Button variant="ghost" size="icon-sm" aria-label={UI.closePanel}>
                    <X aria-hidden />
                  </Button>
                </SheetClose>
              </div>
              <Tabs value={request.outcome}
                    onValueChange={(next) => onChange({ ...request, outcome: next as DealOutcome,
                      group: next === "open" ? request.group : null })}>
                <TabsList aria-label={text.outcomesLabel}>
                  {OUTCOMES.map((outcome) => (
                    <TabsTrigger key={outcome} value={outcome}>{OUTCOME_LABELS[outcome]}</TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </SheetHeader>
            <div className="flex flex-1 flex-col gap-3 overflow-y-auto py-4">
              {deals.error && <div className="px-4"><ErrorAlert message={deals.error} /></div>}
              {deals.loading && <Skeleton className="mx-4 h-64 rounded-xl" aria-label={UI.loading} />}
              {data && (data.empty ? (
                <p className="px-4 text-sm text-muted-foreground">{dealsEmptyText(data.empty)}</p>
              ) : (
                <>
                  <p className="px-4 text-sm text-muted-foreground">{text.total(data.total)}</p>
                  <DealsTable deals={rows} outcome={data.outcome} />
                  <TablePagination page={page} total={data.total} pageSize={PAGE_SIZE} onPage={setPage} />
                </>
              ))}
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
