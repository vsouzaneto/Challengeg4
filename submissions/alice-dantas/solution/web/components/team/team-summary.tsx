"use client";

import { GroupComposition } from "@/components/app/group-composition";
import { InfoPopover } from "@/components/app/info-popover";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { GROUP_LABELS, TEAM, UI, groupRange, groupZeroNote } from "@/copy/pt-BR";
import { CONCEPT_ICONS, GROUP_VISUAL } from "@/copy/visual";
import type { Group, TeamPipeline } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import { cn } from "@/lib/utils";

type Props = {
  payload: Pick<TeamPipeline, "groups" | "summary" | "meta">;
  /** Abre a lista de oportunidades já no grupo escolhido. */
  onPick: (state: Group["state"]) => void;
};

/** A carteira aberta da equipe num cartão, como na Inteligência: o total, a barra por grupo (o comprimento codifica
 * as contagens da API) e a legenda com as contagens, cada uma levando à lista. Sem percentuais escritos: o front não
 * calcula valor de negócio (ADR-004). */
export function TeamSummary({ payload, onPick }: Props) {
  const { summary, meta } = payload;
  const order = payload.groups.map((group) => group.state);
  const NoAccount = CONCEPT_ICONS.noAccount;
  return (
    <section aria-label={UI.teamSummaryLabel}>
      <Card size="sm">
        <CardHeader>
          <CardTitle className="font-semibold">
            {TEAM.compositionTitle} · <span className="tabular-nums">{formatInt(summary.total)}</span>
          </CardTitle>
          <CardDescription className="text-xs">{TEAM.compositionNote}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <GroupComposition order={order} counts={summary} total={summary.total} onPick={onPick} className="h-2.5" />
          <ul className="flex flex-wrap gap-x-4 gap-y-1.5 text-sm">
            {payload.groups.map((group) => {
              const visual = GROUP_VISUAL[group.state];
              const zero = groupZeroNote(group.state, summary[group.state], meta);
              return (
                <li key={group.state} className="flex flex-col gap-0.5">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="ghost" size="sm" onClick={() => onPick(group.state)}
                              className="h-auto gap-1.5 px-1.5 py-1 font-normal">
                        <visual.icon aria-hidden className={cn("size-3.5", visual.text)} />
                        <span className={cn("font-medium", visual.text)}>{GROUP_LABELS[group.state]}</span>
                        <span className="font-semibold tabular-nums">{formatInt(summary[group.state])}</span>
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>{groupRange(group.state, meta)}</TooltipContent>
                  </Tooltip>
                  {zero && <span className="px-1.5 text-xs text-muted-foreground">{zero}</span>}
                </li>
              );
            })}
          </ul>
          {summary.without_account > 0 && (
            <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <NoAccount className="size-4 shrink-0" aria-hidden />
              <span className="tabular-nums">{TEAM.withoutAccountLine(summary.without_account)}</span>
              <InfoPopover label={TEAM.accountNoteLabel}>{UI.accountNote}</InfoPopover>
            </p>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
