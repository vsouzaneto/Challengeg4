"use client";

import { ArrowRight, CalendarDays, List, MoveDown, TrendingDown, UsersRound, type LucideIcon } from "lucide-react";
import Link from "next/link";

import { IconTile } from "@/components/app/icon-tile";
import { MoreDetails } from "@/components/app/more-details";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
  INTELLIGENCE, diagnosticHeadline, diagnosticStepShort, diagnosticText, type Diagnostic, type GroupKey,
} from "@/copy/pt-BR";
import { CONCEPT_ICONS, GROUP_VISUAL } from "@/copy/visual";
import type { IntelligenceFilter } from "@/lib/contract";
import { type DealOutcome, type Dimension, teamHref, teamScopeOnly } from "@/lib/intelligence";

import { HeadlineMetrics } from "./headline-metrics";

type Props = {
  diagnostics: Diagnostic[];
  filter: IntelligenceFilter;
  onDeals: (outcome: DealOutcome, group?: GroupKey) => void;
  onViewBy: (dimension: Dimension) => void;
  /** Leva a uma seção da página (fecha o painel antes). */
  onJump: (section: string) => void;
};

const text = INTELLIGENCE.process;

/** Ícone e tom de cada diagnóstico; o grupo, quando há, vem dos params (nunca escrito à mão). Neutro no resto:
 * nenhum vermelho para queda. */
function visualOf(diagnostic: Diagnostic): { icon: LucideIcon; tone?: string; group?: GroupKey } {
  switch (diagnostic.code) {
    case "engaging_beyond_longest_cycle":
    case "prospecting_without_engage_date": {
      const group = diagnostic.params.group;
      return { icon: GROUP_VISUAL[group].icon, tone: GROUP_VISUAL[group].tile, group };
    }
    case "open_without_account":
      return { icon: CONCEPT_ICONS.noAccount };
    case "sellers_without_opportunities":
    case "accounts_shared_by_sellers":
      return { icon: UsersRound };
    case "quarter_end_outcome_mix":
      return { icon: CalendarDays };
    case "engagement_inflow_drop":
      return { icon: TrendingDown };
    default:
      return { icon: CONCEPT_ICONS.info };
  }
}

/** As ações de cada diagnóstico: as negociações por trás do número, ou onde ver o padrão. */
function Actions({ diagnostic, filter, onDeals, onViewBy, onJump }: Omit<Props, "diagnostics"> & { diagnostic: Diagnostic }) {
  const deals = (group?: GroupKey) => (
    <Button variant="outline" size="sm" onClick={() => onDeals("open", group)}>
      <List aria-hidden />
      {text.seeDeals}
    </Button>
  );
  const link = (href: string, label: string) => (
    <Button asChild variant="link" size="sm" className="px-0 text-primary-strong">
      <Link href={href}>
        {label}
        <ArrowRight aria-hidden />
      </Link>
    </Button>
  );
  switch (diagnostic.code) {
    case "engaging_beyond_longest_cycle":
      return (
        <>
          {deals(diagnostic.params.group)}
          {teamScopeOnly(filter) && link(teamHref(filter, diagnostic.params.group), text.seeTeam)}
        </>
      );
    case "open_without_account":
      return deals();
    case "prospecting_without_engage_date":
      return deals(diagnostic.params.group);
    case "quarter_end_outcome_mix":
    case "engagement_inflow_drop":
      return (
        <Button variant="outline" size="sm" onClick={() => onJump("tempo")}>
          <MoveDown aria-hidden />
          {text.seeMonths}
        </Button>
      );
    case "accounts_shared_by_sellers":
      return (
        <Button variant="outline" size="sm" onClick={() => onViewBy("account")}>{text.seeAccounts}</Button>
      );
    default:
      return null;
  }
}

/** Onde o processo pode melhorar: número + barra (só com `share` da API) + próximo passo em uma linha; o texto
 * inteiro fica em "Ver detalhe". Fica no painel "Ver análises". */
export function DiagnosticsList({ diagnostics, filter, onDeals, onViewBy, onJump }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">{text.help}</p>
      {diagnostics.length === 0 && <p className="text-sm text-muted-foreground">{text.none}</p>}
      {diagnostics.map((diagnostic) => {
        const { title, body, step } = diagnosticText(diagnostic);
        const visual = visualOf(diagnostic);
        return (
          <Card key={diagnostic.code} size="sm">
            <CardHeader className="flex flex-row items-start gap-3">
              <IconTile icon={visual.icon} tone={visual.tone} />
              <CardTitle className="font-semibold text-pretty">{title}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <HeadlineMetrics headline={diagnosticHeadline(diagnostic)} tone={visual.group} />
              <p className="flex items-start gap-2 text-sm font-medium">
                <ArrowRight aria-hidden className="mt-0.5 size-4 shrink-0 text-primary-strong" />
                <span><span className="sr-only">{text.nextStep}: </span>{diagnosticStepShort(diagnostic)}</span>
              </p>
              <MoreDetails label={text.detail} contentClassName="flex flex-col gap-2 text-sm text-muted-foreground">
                <p className="text-pretty">{body}</p>
                <div className="flex flex-col gap-1 rounded-lg bg-accent p-3 text-accent-foreground">
                  <h3 className="text-sm font-semibold">{text.nextStep}</h3>
                  <p className="text-sm leading-relaxed">{step}</p>
                </div>
              </MoreDetails>
            </CardContent>
            <CardFooter className="flex flex-wrap gap-2">
              <Actions diagnostic={diagnostic} filter={filter} onDeals={onDeals} onViewBy={onViewBy} onJump={onJump} />
            </CardFooter>
          </Card>
        );
      })}
    </div>
  );
}
