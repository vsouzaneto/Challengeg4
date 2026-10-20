"use client";

import { X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ASSISTED } from "@/copy/assisted";
import { UI } from "@/copy/pt-BR";
import { MAX_SET, POLICY_VERSION, emptyAssessment, type Assessment } from "@/lib/assisted/model";
import { evaluate } from "@/lib/assisted/policy";
import type { Assessments } from "@/lib/assisted/use-assessments";
import type { Item } from "@/lib/contract";
import { cn } from "@/lib/utils";

import { QuestionStep } from "./question-step";
import { ResultStep } from "./result-step";
import { SelectStep } from "./select-step";

/** O que o vendedor pediu: comparar um conjunto de empatadas (escolhendo), as que marcou na lista (já escolhidas) ou
 * avaliar uma oportunidade só. */
export type AssessRequest = { mode: "set" | "picked" | "single"; pool: Item[] };

type Props = {
  request: AssessRequest | null;
  seller: string;
  /** A data dos dados (`meta.as_of`): é o "hoje" da avaliação. */
  asOf: string;
  store: Assessments;
  onClose: () => void;
};

type Step = "select" | "ask" | "result";

/** A janela da avaliação: escolher, responder e ver o resultado, com a etapa à vista no topo. Fecha e abre do zero, e
 * as respostas ficam guardadas. */
export function AssessmentDialog({ request, seller, asOf, store, onClose }: Props) {
  return (
    <Dialog open={Boolean(request)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent showCloseButton={false}
                     className="flex max-h-[min(92dvh,52rem)] w-full max-w-[calc(100%-1rem)] flex-col gap-0 overflow-hidden rounded-3xl p-0 sm:max-w-2xl">
        {request && <Flow request={request} seller={seller} asOf={asOf} store={store} onClose={onClose} />}
      </DialogContent>
    </Dialog>
  );
}

/** As etapas como traços: os já feitos e o atual em cor cheia (a cor nunca sozinha: o texto diz "Etapa 2 de 3"). */
function StepBar({ step, total }: { step: number; total: number }) {
  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs font-medium text-muted-foreground tabular-nums" aria-live="polite">
        {ASSISTED.dialog.step(step, total)}
      </p>
      <div aria-hidden className="flex gap-1.5">
        {Array.from({ length: total }, (_, index) => (
          <span key={index} className={cn("h-1.5 flex-1 rounded-full", index < step ? "bg-primary" : "bg-muted")} />
        ))}
      </div>
    </div>
  );
}

function Flow({ request, seller, asOf, store, onClose }: Omit<Props, "request"> & { request: AssessRequest }) {
  const single = request.mode === "single";
  const only = request.pool[0]?.opportunity_id;
  const [step, setStep] = useState<Step>(() => {
    if (request.mode === "set") return "select";
    return store.byId[only] && evaluate(store.byId[only], asOf).status === "complete" ? "result" : "ask";
  });
  const skipSelect = request.mode !== "set";
  const [chosen, setChosen] = useState<string[]>(
    single && only ? [only] : request.mode === "picked" ? request.pool.map((item) => item.opportunity_id) : []);
  const [index, setIndex] = useState(0);

  const items = Object.fromEntries(request.pool.map((item) => [item.opportunity_id, item]));
  const current = chosen[index];
  const assessmentOf = (id: string): Assessment => store.byId[id] ?? emptyAssessment(id);
  const assessed = new Set(
    request.pool.map((item) => item.opportunity_id).filter((id) => Object.keys(store.byId[id]?.answers ?? {}).length),
  );
  const edit = (id: string) => {
    setIndex(Math.max(0, chosen.indexOf(id)));
    setStep("ask");
  };
  const last = index >= chosen.length - 1;
  const advance = () => (last ? setStep("result") : setIndex(index + 1));
  const steps: Step[] = skipSelect ? ["ask", "result"] : ["select", "ask", "result"];

  return (
    <>
      <DialogHeader className="gap-4 border-b px-6 pt-6 pb-4 text-left">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <StepBar step={steps.indexOf(step) + 1} total={steps.length} />
          </div>
          <DialogClose asChild>
            <Button variant="ghost" size="icon-sm" aria-label={UI.closePanel} className="-mt-1 -mr-2">
              <X aria-hidden />
            </Button>
          </DialogClose>
        </div>
        <div className="flex flex-col gap-1.5">
          <DialogTitle className="text-2xl leading-tight font-semibold tracking-tight">{ASSISTED.title}</DialogTitle>
          <DialogDescription>{single ? ASSISTED.sheet.singleDescription : request.mode === "picked" ? ASSISTED.sheet.pickedDescription : ASSISTED.sheet.setDescription}</DialogDescription>
        </div>
      </DialogHeader>

      {step === "select" && (
        <SelectStep pool={request.pool} chosen={chosen.slice(0, MAX_SET)} assessed={assessed}
                    onChange={setChosen} onNext={() => {
                      // Na ordem da lista, não na ordem em que foram marcadas.
                      const order = request.pool.map((item) => item.opportunity_id);
                      setChosen((ids) => [...ids].sort((a, b) => order.indexOf(a) - order.indexOf(b)));
                      setIndex(0);
                      setStep("ask");
                    }} />
      )}
      {step === "ask" && current && (
        <QuestionStep
          key={current}
          item={items[current]}
          assessment={assessmentOf(current)}
          index={index + 1}
          total={chosen.length}
          last={last}
          onChange={(change) => store.update(current, (stored) => ({
            ...change(stored), assessedAt: new Date().toISOString(), policyVersion: POLICY_VERSION,
          }))}
          onBack={skipSelect ? null : () => (index === 0 ? setStep("select") : setIndex(index - 1))}
          onSkip={advance}
          onNext={advance}
        />
      )}
      {step === "result" && (
        <ResultStep ids={chosen} items={items} store={store} seller={seller} asOf={asOf} single={single}
                    onEdit={edit} onClose={onClose} />
      )}
    </>
  );
}
