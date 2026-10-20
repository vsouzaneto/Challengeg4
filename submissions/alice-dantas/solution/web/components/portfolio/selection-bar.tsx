"use client";

import { ASSESSMENT_CTA } from "@/components/assessment/cta";
import { Button } from "@/components/ui/button";
import { ASSISTED } from "@/copy/assisted";
import { CONCEPT_ICONS } from "@/copy/visual";
import { MAX_SET, MIN_SET } from "@/lib/assisted/model";
import { cn } from "@/lib/utils";

const { assisted: Assisted } = CONCEPT_ICONS;

type Props = {
  count: number;
  onAssess: () => void;
  onClear: () => void;
};

/** A barra fixa no pé da tela com as oportunidades escolhidas na lista: diz quantas são e leva à priorização assistida. */
export function SelectionBar({ count, onAssess, onClear }: Props) {
  if (count === 0) return null;
  const text = ASSISTED.selection;
  const hint = count < MIN_SET ? text.needMore : count >= MAX_SET ? text.full : text.ready;
  return (
    <div role="region" aria-label={text.barLabel}
         className="sticky bottom-4 z-20 mx-auto flex w-full max-w-2xl flex-wrap items-center justify-between gap-x-4 gap-y-2 rounded-2xl border bg-popover px-4 py-3 shadow-lg">
      <p className="flex min-w-0 flex-col text-sm" aria-live="polite">
        <span className="font-semibold tabular-nums">{text.counter(count)}</span>
        <span className="text-xs text-muted-foreground">{hint}</span>
      </p>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={onClear}>{text.clear}</Button>
        <Button size="sm" className={cn(ASSESSMENT_CTA)} disabled={count < MIN_SET} onClick={onAssess}>
          <Assisted data-icon="inline-start" aria-hidden />
          {text.action}
        </Button>
      </div>
    </div>
  );
}
