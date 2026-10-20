"use client";

import { CircleCheck, Info } from "lucide-react";
import { useState } from "react";

import { IconTile } from "@/components/app/icon-tile";
import { InfoPopover } from "@/components/app/info-popover";
import { Button } from "@/components/ui/button";
import { ASSISTED, summaryText } from "@/copy/assisted";
import type { Assessments } from "@/lib/assisted/use-assessments";
import { emptyAssessment } from "@/lib/assisted/model";
import { evaluate, move, rank } from "@/lib/assisted/policy";
import type { Item } from "@/lib/contract";
import { cn } from "@/lib/utils";

import { ASSESSMENT_CTA } from "./cta";

import { AssessmentFooter, FOOTER_BUTTON } from "./assessment-footer";
import { ComparisonTable } from "./comparison-table";
import { ResultCard } from "./result-card";

type Props = {
  ids: string[];
  items: Record<string, Item>;
  store: Assessments;
  seller: string;
  asOf: string;
  /** Uma avaliação só: sem ordem, só o resultado. */
  single: boolean;
  onEdit: (id: string) => void;
  onClose: () => void;
};

/** Etapa 3: a ordem sugerida por pontos, o bloco à parte, o que ainda está incompleto e o comparativo. */
export function ResultStep({ ids, items, store, seller, asOf, single, onEdit, onClose }: Props) {
  const [compare, setCompare] = useState(false);
  const [copied, setCopied] = useState(false);

  const assessmentOf = (id: string) => store.byId[id] ?? emptyAssessment(id);
  const evaluations = ids.map((id) => evaluate(assessmentOf(id), asOf));
  const ranking = rank(evaluations, store.orderFor(ids));
  const order = ranking.ordered.map((r) => r.evaluation.opportunityId);

  const copy = () => {
    const text = summaryText({ seller, asOf, items, ranked: ranking.ordered, aside: ranking.aside, pending: ranking.pending });
    navigator.clipboard?.writeText(text).then(() => setCopied(true), () => setCopied(false));
  };
  const card = (evaluation: (typeof evaluations)[number], extra: Partial<React.ComponentProps<typeof ResultCard>> = {}) => {
    const assessment = assessmentOf(evaluation.opportunityId);
    return (
      <ResultCard key={evaluation.opportunityId} evaluation={evaluation} item={items[evaluation.opportunityId]}
                  assessedAt={assessment.assessedAt} policyVersion={assessment.policyVersion}
                  onEdit={() => onEdit(evaluation.opportunityId)}
                  onRemove={() => {
                    store.remove(evaluation.opportunityId);
                    if (single) onClose();
                  }} {...extra} />
    );
  };

  return (
    <>
      <div className="relative flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-6 py-5 [&>*]:shrink-0">
        <div className="flex items-start gap-3">
          <IconTile icon={CircleCheck} tone="bg-accent text-primary-strong" size="lg" className="rounded-full" />
          <div className="flex flex-col gap-1">
            <h3 className="text-lg font-semibold">{single ? ASSISTED.result.single : ASSISTED.result.title}</h3>
            <p className="text-sm text-muted-foreground">{ASSISTED.result.intro}</p>
          </div>
        </div>

        {ranking.pending.length > 0 && (
          <section aria-label={single ? ASSISTED.result.incompleteTitle : ASSISTED.result.partialTitle}
                   className="flex flex-col gap-2 rounded-lg border border-dashed p-3">
            <h4 className="text-sm font-semibold">
              {single ? ASSISTED.result.incompleteTitle : ASSISTED.result.partialTitle}
            </h4>
            <p className="text-sm text-muted-foreground">
              {single ? ASSISTED.result.incompleteBody : ASSISTED.result.partialBody(ranking.pending.map((e) => e.opportunityId))}
            </p>
            <div className="flex flex-wrap gap-2">
              {ranking.pending.map((e) => (
                <Button key={e.opportunityId} size="sm" variant="outline" onClick={() => onEdit(e.opportunityId)}>
                  {ASSISTED.result.answer} {e.opportunityId}
                </Button>
              ))}
            </div>
          </section>
        )}

        {single
          ? evaluations.map((evaluation) => (evaluation.status === "complete" ? card(evaluation) : null))
          : (
            <ol aria-label={ASSISTED.result.title} className="flex flex-col gap-3">
              {ranking.ordered.map(({ evaluation, position, tied, manual }, index) => (
                <li key={evaluation.opportunityId}>
                  {card(evaluation, {
                    position: { value: position, tied, manual },
                    onMove: (delta) => store.saveOrder(ids, move(order, evaluation.opportunityId, delta)),
                    canUp: index > 0,
                    canDown: index < order.length - 1,
                  })}
                </li>
              ))}
            </ol>
          )}

        {ranking.aside.length > 0 && (
          <section aria-label={ASSISTED.result.asideTitle} className="flex flex-col gap-3">
            <div>
              <h4 className="text-sm font-semibold">{ASSISTED.result.asideTitle}</h4>
              <p className="text-xs text-muted-foreground">{ASSISTED.result.asideNote}</p>
            </div>
            {ranking.aside.map((evaluation) => card(evaluation))}
          </section>
        )}

        {!single && evaluations.length > 1 && (
          <section className="flex flex-col gap-2">
            <Button variant="outline" size="sm" className="w-fit" aria-expanded={compare} onClick={() => setCompare(!compare)}>
              {compare ? ASSISTED.result.hideCompare : ASSISTED.result.compare}
            </Button>
            {compare && <ComparisonTable evaluations={evaluations} />}
          </section>
        )}

        <p className="flex items-center gap-1.5 text-xs leading-relaxed text-muted-foreground">
          <Info aria-hidden className="size-3.5 shrink-0" />
          <span>{ASSISTED.disclaimer}</span>
          <InfoPopover label={ASSISTED.result.localNoteLabel}>{ASSISTED.localNote}</InfoPopover>
        </p>
        {store.unsaved && <p className="text-xs text-destructive">{ASSISTED.unsaved}</p>}
      </div>
      <AssessmentFooter>
        <Button variant="secondary" className={FOOTER_BUTTON} onClick={copy}>
          {copied ? ASSISTED.result.copied : ASSISTED.result.copy}
        </Button>
        <Button className={cn(ASSESSMENT_CTA, FOOTER_BUTTON)} onClick={onClose}>{ASSISTED.close}</Button>
      </AssessmentFooter>
    </>
  );
}
