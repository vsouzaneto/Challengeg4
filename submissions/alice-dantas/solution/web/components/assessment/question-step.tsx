"use client";

import { cn } from "cn";
import { Check, TriangleAlert } from "lucide-react";
import { useId } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { ASSISTED, CONFLICT_TEXTS, CRITERIA_LABELS, QUESTIONS, answerLabel } from "@/copy/assisted";
import { UI, clientText } from "@/copy/pt-BR";
import { DIMENSIONS, OPTIONS, type Assessment, type Dimension } from "@/lib/assisted/model";
import { conflictsOf } from "@/lib/assisted/policy";
import type { Item } from "@/lib/contract";

import { AssessmentFooter, FOOTER_BUTTON } from "./assessment-footer";
import { ASSESSMENT_CTA } from "./cta";

type Props = {
  item: Item;
  assessment: Assessment;
  /** Posição desta oportunidade na avaliação (1 a total); sem `total`, é uma avaliação só. */
  index: number;
  total: number;
  onChange: (change: (current: Assessment) => Assessment) => void;
  onBack: (() => void) | null;
  onSkip: () => void;
  onNext: () => void;
  last: boolean;
};

/** Etapa 2: as sete perguntas de uma oportunidade numa tela só. Cada resposta é guardada na hora. */
export function QuestionStep({ item, assessment, index, total, onChange, onBack, onSkip, onNext, last }: Props) {
  const prefix = useId();
  const answered = DIMENSIONS.filter((d) => assessment.answers[d] !== undefined).length;
  const conflicts = conflictsOf(assessment);

  const answer = (dimension: Dimension, value: string) =>
    onChange((current) => ({
      ...current,
      answers: { ...current.answers, [dimension]: value },
      // Mudou uma resposta: o que já tinha sido confirmado como correto volta a ser conferido.
      confirmedConflicts: [],
    }));

  return (
    <>
      <div className="relative flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-6 pb-5 [&>*]:shrink-0">
        {/* Fica no topo ao rolar: a oportunidade e o avanço sempre à vista. */}
        <div className="sticky top-0 z-10 -mx-6 flex flex-col gap-2 border-b bg-popover px-6 pt-5 pb-3">
          {total > 1 && <p className="text-xs font-medium text-muted-foreground">{ASSISTED.ask.progress(index, total)}</p>}
          <h3 className="text-lg font-semibold">
            {item.opportunity_id}
            <span className="font-normal text-muted-foreground">
              {" · "}{[item.product || UI.noProduct, clientText(item)].join(" · ")}
            </span>
          </h3>
          <div role="progressbar" aria-label={ASSISTED.ask.form(item.opportunity_id)} aria-valuemin={0}
               aria-valuemax={DIMENSIONS.length} aria-valuenow={answered}
               className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div className={cn("h-full rounded-full bg-primary transition-all", WIDTHS[answered])} />
          </div>
          <p className="text-xs text-muted-foreground" aria-live="polite">{ASSISTED.ask.answered(answered)}</p>
        </div>

        {DIMENSIONS.map((dimension, position) => {
          const labelId = `${prefix}-${dimension}`;
          return (
            <section key={dimension} className="flex flex-col gap-3 rounded-2xl border bg-card/50 p-4">
              <div className="flex flex-col gap-1">
                <span aria-hidden className="font-mono text-[0.6875rem] tracking-wider text-muted-foreground uppercase tabular-nums">
                  {ASSISTED.ask.questionTag(position + 1)}
                </span>
                <h4 id={labelId} className="text-base font-medium">
                  <span className="sr-only tabular-nums">{position + 1}. </span>
                  {QUESTIONS[dimension]}
                  <span className="sr-only"> ({CRITERIA_LABELS[dimension]})</span>
                </h4>
                <span className="text-xs text-muted-foreground">{ASSISTED.ask.chooseOne}</span>
              </div>
              <RadioGroup aria-labelledby={labelId} value={assessment.answers[dimension] ?? ""}
                          onValueChange={(value) => answer(dimension, value)}>
                {OPTIONS[dimension].map((option) => {
                  const id = `${prefix}-${dimension}-${option}`;
                  return (
                    <Label key={option} htmlFor={id}
                           className="group relative flex cursor-pointer items-center gap-3 rounded-xl border bg-card px-4 py-3 font-normal transition-colors hover:bg-muted/50 has-[[data-state=checked]]:border-primary has-[[data-state=checked]]:bg-accent has-[:focus-visible]:ring-3 has-[:focus-visible]:ring-ring/50">
                      <RadioGroupItem id={id} value={option} className="sr-only" />
                      <span aria-hidden
                            className="flex size-5 shrink-0 items-center justify-center rounded-full border border-input text-white group-has-[[data-state=checked]]:border-primary-strong group-has-[[data-state=checked]]:bg-primary-strong dark:group-has-[[data-state=checked]]:border-primary dark:group-has-[[data-state=checked]]:bg-primary">
                        <Check className="size-3 opacity-0 group-has-[[data-state=checked]]:opacity-100" />
                      </span>
                      {answerLabel(dimension, option)}
                    </Label>
                  );
                })}
              </RadioGroup>
            </section>
          );
        })}

        {conflicts.map((code) => (
          <Alert key={code} variant="warning">
            <TriangleAlert aria-hidden />
            <AlertTitle>{ASSISTED.conflict.title}</AlertTitle>
            <AlertDescription className="flex flex-col items-start gap-2">
              <span>{CONFLICT_TEXTS[code]} {ASSISTED.conflict.question}</span>
              <span className="text-xs">{ASSISTED.conflict.hint}</span>
              <Button size="sm" variant="outline"
                      onClick={() => onChange((current) => ({
                        ...current, confirmedConflicts: [...current.confirmedConflicts, code],
                      }))}>
                {ASSISTED.conflict.keep}
              </Button>
            </AlertDescription>
          </Alert>
        ))}
      </div>
      <AssessmentFooter>
        {onBack ? <Button variant="secondary" className={FOOTER_BUTTON} onClick={onBack}>{ASSISTED.ask.back}</Button> : <span />}
        <div className="flex items-center gap-2">
          <Button variant="ghost" className={FOOTER_BUTTON} onClick={onSkip}>{ASSISTED.ask.skip}</Button>
          <Button className={cn(ASSESSMENT_CTA, FOOTER_BUTTON)} onClick={onNext}>
            {last ? ASSISTED.ask.finish : ASSISTED.ask.next}
          </Button>
        </div>
      </AssessmentFooter>
    </>
  );
}

// A barra de progresso usa classes prontas (o teste de design system proíbe estilo inline).
const WIDTHS = ["w-0", "w-1/7", "w-2/7", "w-3/7", "w-4/7", "w-5/7", "w-6/7", "w-full"];
