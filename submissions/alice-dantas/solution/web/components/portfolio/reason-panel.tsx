"use client";

import { ChevronUp, Copy } from "lucide-react";
import { useEffect, useState } from "react";

import { RemoveAssessment } from "@/components/assessment/remove-assessment";
import { IconTile } from "@/components/app/icon-tile";
import { InfoPopover } from "@/components/app/info-popover";
import { MoreDetails } from "@/components/app/more-details";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ASSISTED } from "@/copy/assisted";
import {
  ROLE_LABELS, UI, actionText, ageContextText, reasonText, smallSampleNote, suggestionText, suggestionsFor, tieNote,
  type AgeContextMeta, type ReasonRole,
} from "@/copy/pt-BR";
import { CONCEPT_ICONS, GROUP_VISUAL } from "@/copy/visual";
import type { Evaluation } from "@/lib/assisted/policy";
import type { Item } from "@/lib/contract";
import { useSmallProductSample } from "@/lib/product-sample";
import { cn } from "@/lib/utils";

const { verify: Verify, tie: Tie, listPrice: ListPrice, assisted: Assisted, blindSpot: BlindSpot } = CONCEPT_ICONS;

// Ordem das seções: o que decidiu o grupo e o que decidiu a posição. Só entra motivo que decide.
const ROLES: ReasonRole[] = ["group", "order"];

/** O ID do painel de uma oportunidade: a linha da tabela aponta para ele com `aria-controls`. */
export const panelId = (id: string) => `analise-${id}`;

type Props = {
  item: Item;
  /** Limites e mediana do histórico, para o contexto da idade. */
  meta: AgeContextMeta;
  /** Fecha a análise (recolhe a linha). */
  onClose: () => void;
  /** Abre a priorização assistida desta oportunidade; sem ela, a seção não aparece (ex.: visão da equipe). */
  onAssess?: (item: Item) => void;
  /** Remove a avaliação de uma oportunidade (só com o selo). */
  onRemoveAssessment?: (id: string) => void;
  /** O selo de cada oportunidade já avaliada, por ID. */
  marks?: Record<string, string>;
  /** O resultado da avaliação desta oportunidade, quando já foi feita: os pontos ficam à vista. */
  evaluation?: Evaluation;
};

/** "Por que está aqui", dentro da própria linha: o próximo passo, os motivos separados pelo papel que o contrato dá a
 * cada um e as ferramentas de apoio. Fica entre as linhas da lista para o vendedor comparar com a de baixo. */
export function ReasonPanel({ item, meta, onClose, onAssess, onRemoveAssessment, marks, evaluation }: Props) {
  const [copied, setCopied] = useState(false);
  const tie = tieNote(item);
  const suggestions = suggestionsFor(item);
  const mark = marks?.[item.opportunity_id];
  const smallSample = useSmallProductSample(item.product);

  useEffect(() => setCopied(false), [item.opportunity_id]);

  const copy = () => {
    navigator.clipboard?.writeText(item.opportunity_id).then(() => setCopied(true), () => setCopied(false));
  };

  return (
    <section id={panelId(item.opportunity_id)} aria-label={UI.whyHereFor(item.opportunity_id)}
             className="flex flex-col gap-4 border-l-2 border-primary/50 bg-muted/30 px-4 py-4 text-left whitespace-normal sm:px-6">
      <div className="grid gap-x-8 gap-y-4 lg:grid-cols-2">
        <div className="flex flex-col gap-4">
          <div className="flex gap-3 rounded-lg bg-accent p-3 text-accent-foreground">
            <IconTile icon={Verify} tone="bg-background text-primary-strong" size="sm" />
            <div className="flex flex-col gap-0.5">
              <h4 className="text-xs font-medium text-primary-strong">{UI.nextStep}</h4>
              <p className="text-sm leading-relaxed font-medium">{actionText(item.next_action, item.account)}</p>
            </div>
          </div>
          {ROLES.map((role) => {
            const reasons = item.reasons.filter((reason) => reason.role === role);
            if (!reasons.length) return null;
            const Icon = role === "group" ? GROUP_VISUAL[item.group].icon : ListPrice;
            const tone = role === "group" ? GROUP_VISUAL[item.group].text : "text-muted-foreground";
            return (
              <section key={role} className="flex flex-col gap-2">
                <h4 className="text-xs font-medium text-muted-foreground">{ROLE_LABELS[role]}</h4>
                <ul className="flex flex-col gap-2 text-sm leading-relaxed">
                  {reasons.map((reason) => (
                    <li key={reason.code} className="flex items-start gap-2">
                      <Icon aria-hidden className={cn("mt-0.5 size-4 shrink-0", tone)} />
                      <span>{reasonText(reason)}</span>
                    </li>
                  ))}
                  {role === "order" && tie && (
                    <li className="flex items-start gap-2">
                      <Tie aria-hidden className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                      <span>{tie}</span>
                    </li>
                  )}
                  {role === "order" && smallSample && item.product && (
                    <li className="flex items-start gap-2">
                      <BlindSpot aria-hidden className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                      <span>{smallSampleNote(item.product, smallSample.closed, smallSample.won)}</span>
                    </li>
                  )}
                </ul>
              </section>
            );
          })}
        </div>

        <div className="flex flex-col gap-4">
          {onAssess && (
            <section aria-label={ASSISTED.single.title} className="flex flex-col gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <Assisted aria-hidden className="size-4 text-muted-foreground" />
                <Button size="sm" variant="outline" onClick={() => onAssess(item)}>
                  {mark ? ASSISTED.single.edit : ASSISTED.single.button}
                </Button>
                <InfoPopover label={ASSISTED.single.title}>{ASSISTED.single.hint}</InfoPopover>
                {onRemoveAssessment && mark && (
                  <RemoveAssessment id={item.opportunity_id} onRemove={() => onRemoveAssessment(item.opportunity_id)} />
                )}
                {mark && (
                  <Badge variant="reference" className="ml-auto h-auto whitespace-normal">
                    <Assisted data-icon="inline-start" aria-hidden />{mark}
                  </Badge>
                )}
              </div>
              {evaluation?.status === "complete" && (
                <p className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                  <span className="text-2xl font-semibold tabular-nums">{ASSISTED.points(evaluation.confirmed)}</span>
                  {evaluation.potential > evaluation.confirmed && (
                    <span className="text-xs text-muted-foreground">{ASSISTED.potential(evaluation.potential)}</span>
                  )}
                </p>
              )}
            </section>
          )}
          <MoreDetails label={UI.suggestionsCount(suggestions.length)} regionLabel={UI.suggestionsTitle}
                       contentClassName="flex flex-col gap-2">
            <p className="text-xs leading-relaxed text-muted-foreground">{UI.suggestionsIntro}</p>
            <ul className="flex list-disc flex-col gap-1.5 pl-4 text-sm leading-relaxed">
              {suggestions.map((suggestion) => (
                <li key={suggestion.when}>{suggestionText(suggestion)}</li>
              ))}
            </ul>
          </MoreDetails>
          <MoreDetails label={UI.blindSpotButton} contentClassName="flex flex-col gap-2">
            <p className="flex items-start gap-2 text-xs font-medium">
              <BlindSpot aria-hidden className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
              {UI.limitsShort}
            </p>
            <p className="text-xs leading-relaxed text-muted-foreground">{UI.limitsNote}</p>
          </MoreDetails>
          {item.age_days !== null && (
            <MoreDetails label={UI.ageContextShort} contentClassName="flex flex-col gap-1">
              <h4 className="sr-only">{UI.ageContextTitle}</h4>
              <p className="text-sm leading-relaxed">{ageContextText(item.age_days, meta)}</p>
              <p className="text-xs leading-relaxed text-muted-foreground">{UI.ageContextNote}</p>
            </MoreDetails>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between gap-2 border-t pt-3">
        <Button variant="outline" size="sm" onClick={copy}>
          <Copy aria-hidden />
          {copied ? UI.copied : UI.copyId}
        </Button>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <ChevronUp aria-hidden />
          {UI.closeAnalysis}
        </Button>
      </div>
    </section>
  );
}
