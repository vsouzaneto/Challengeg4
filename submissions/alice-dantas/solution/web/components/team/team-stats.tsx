"use client";

import { CircleCheckBig, Percent, Users } from "lucide-react";

import { KpiCard } from "@/components/app/kpi-card";
import { InfoPopover } from "@/components/app/info-popover";
import { Badge } from "@/components/ui/badge";
import { INTELLIGENCE, TEAM, UI } from "@/copy/pt-BR";
import { CONCEPT_ICONS } from "@/copy/visual";
import type { Intelligence } from "@/lib/contract";
import { formatCompact, formatInt, formatPct } from "@/lib/format";

type Props = {
  /** Vendedores com carteira aberta no filtro (vem do pipeline). */
  sellers: number;
  /** Histórico e valor de tabela do mesmo filtro (vem da Inteligência): `undefined` carregando, `null` se falhou. */
  intelligence: Pick<Intelligence, "history" | "open"> | null | undefined;
};

/** Quatro números no topo da equipe, no mesmo formato da Inteligência: valor de tabela aberto, vendedores,
 * vendas ganhas e taxa de ganho. Se a Inteligência falhar, só os que dependem dela mostram o vazio. */
export function TeamStats({ sellers, intelligence }: Props) {
  const text = INTELLIGENCE.kpis;
  const loading = intelligence === undefined;
  const history = intelligence?.history;
  return (
    <section aria-label={TEAM.stats.label} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <KpiCard icon={CONCEPT_ICONS.listPrice} label={TEAM.openValue.label} loading={loading}
               value={intelligence ? formatCompact(intelligence.open.list_value) : UI.empty}
               help={intelligence ? INTELLIGENCE.open.notRevenue : undefined} />
      <KpiCard icon={Users} label={TEAM.stats.sellers} value={formatInt(sellers)} help={TEAM.stats.sellersHelp} />
      <KpiCard icon={CircleCheckBig} label={text.won} loading={loading}
               value={history ? formatInt(history.won) : UI.empty}
               help={history ? text.wonOf(history.closed) : undefined} />
      <KpiCard icon={Percent} label={text.winRate} loading={loading}
               value={history?.win_rate ? formatPct(history.win_rate.value) : UI.empty}
               help={history?.win_rate ? (
                 <>
                   <Badge variant="outline" className="tabular-nums">{text.winRateChip(history.win_rate.low, history.win_rate.high)}</Badge>
                   <InfoPopover label={text.winRateRangeLabel}>
                     {text.winRateRange(history.win_rate.low, history.win_rate.high)}
                   </InfoPopover>
                 </>
               ) : undefined} />
    </section>
  );
}
