"use client";

import { CircleCheckBig, Coins, Percent } from "lucide-react";

import { GroupComposition } from "@/components/app/group-composition";
import { KpiCard } from "@/components/app/kpi-card";
import { InfoPopover } from "@/components/app/info-popover";
import { Badge } from "@/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { GROUP_LABELS, INTELLIGENCE, UI } from "@/copy/pt-BR";
import { CONCEPT_ICONS, GROUP_VISUAL } from "@/copy/visual";
import { cn } from "@/lib/utils";
import type { Intelligence } from "@/lib/contract";
import { formatCompact, formatInt, formatPct } from "@/lib/format";

const ListPrice = CONCEPT_ICONS.listPrice;

/** O histórico do recorte em quatro números e, à parte, a carteira aberta: valor de tabela nunca se
 * soma à receita realizada. Os grupos seguem a ordem da API. */
export function HistorySummary({ payload }: { payload: Pick<Intelligence, "history" | "open" | "ordering"> }) {
  const { history, open } = payload;
  const text = INTELLIGENCE.kpis;
  const order = payload.ordering.group_order;
  return (
    <div className="flex flex-col gap-4">
      <section aria-label={text.label} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard icon={Coins} label={text.revenue} value={formatCompact(history.revenue)} help={text.revenueShort(history.revenue)} />
        <KpiCard icon={CircleCheckBig} label={text.won} value={formatInt(history.won)} help={text.wonOf(history.closed)} />
        <KpiCard icon={Percent} label={text.winRate} value={history.win_rate ? formatPct(history.win_rate.value) : UI.empty}
             help={history.win_rate ? (
               <>
                 <Badge variant="outline" className="tabular-nums">{text.winRateChip(history.win_rate.low, history.win_rate.high)}</Badge>
                 <InfoPopover label={text.winRateRangeLabel}>
                   {text.winRateRange(history.win_rate.low, history.win_rate.high)}
                 </InfoPopover>
               </>
             ) : undefined} />
        <KpiCard icon={CONCEPT_ICONS.age} label={text.cycle}
             value={history.median_won_cycle_days === null ? UI.empty : text.days(history.median_won_cycle_days)}
             help={history.median_lost_cycle_days === null ? undefined : text.lostCycleShort(history.median_lost_cycle_days)} />
      </section>
      <Card size="sm" aria-label={INTELLIGENCE.open.title} role="region">
        <CardHeader>
          <CardTitle className="font-semibold tabular-nums">{INTELLIGENCE.open.titleCount(open.summary.total)}</CardTitle>
          <CardAction>
            <Badge variant="outline" className="tabular-nums">
              <ListPrice data-icon="inline-start" aria-hidden />
              {INTELLIGENCE.open.listValue(open.list_value)}
            </Badge>
          </CardAction>
          <CardDescription className="text-xs">{INTELLIGENCE.open.notRevenue}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <GroupComposition order={order} counts={open.summary} total={open.summary.total} className="h-2.5" />
          <ul aria-label={INTELLIGENCE.open.groupsLabel} className="flex flex-wrap gap-x-4 gap-y-1.5 text-sm">
            {order.map((state) => {
              const Icon = GROUP_VISUAL[state].icon;
              return (
                <li key={state} className="flex items-center gap-1.5">
                  <Icon aria-hidden className={cn("size-3.5", GROUP_VISUAL[state].text)} />
                  <span className={cn("font-medium", GROUP_VISUAL[state].text)}>{GROUP_LABELS[state]}</span>{" "}
                  <span className="font-semibold tabular-nums">{formatInt(open.summary[state])}</span>
                </li>
              );
            })}
          </ul>
          {open.excluded_without_account !== null && open.excluded_without_account > 0 && (
            <p className="text-xs text-muted-foreground">{INTELLIGENCE.open.excluded(open.excluded_without_account)}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
