"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { ASSISTED } from "@/copy/assisted";
import { UI } from "@/copy/pt-BR";
import { CONCEPT_ICONS } from "@/copy/visual";
import { MAX_SET, MIN_SET } from "@/lib/assisted/model";
import type { Item } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import { cn } from "@/lib/utils";

import { AssessmentFooter, FOOTER_BUTTON } from "./assessment-footer";
import { ASSESSMENT_CTA } from "./cta";

const { tie: Tie, product: Product, account: Account, listPrice: ListPrice } = CONCEPT_ICONS;

type Props = {
  pool: Item[];
  chosen: string[];
  onChange: (ids: string[]) => void;
  onNext: () => void;
  /** IDs que já têm alguma resposta guardada. */
  assessed: Set<string>;
};

/** Etapa 1: o vendedor marca de 2 a 5 oportunidades do empate. Nada vem marcado. */
export function SelectStep({ pool, chosen, onChange, onNext, assessed }: Props) {
  const full = chosen.length >= MAX_SET;
  // Empate (mesmo produto e valor em todas): os dois ficam no chip, e cada linha só diz o que muda.
  const first = pool[0];
  const tied = pool.length > 1 && Boolean(first?.product) && first?.sales_price !== null &&
    pool.every((item) => item.product === first.product && item.sales_price === first.sales_price);
  const toggle = (id: string, on: boolean) =>
    onChange(on ? [...chosen, id] : chosen.filter((other) => other !== id));

  return (
    <>
      <div className="relative flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-6 py-5 [&>*]:shrink-0">
        <div className="flex flex-col gap-1">
          <h3 className="text-lg font-semibold">{ASSISTED.select.title}</h3>
          <p className="text-sm text-muted-foreground" aria-live="polite">
            {ASSISTED.select.counter(chosen.length)}
            {" · "}
            {chosen.length < MIN_SET ? ASSISTED.select.needMore : full ? ASSISTED.select.full : ASSISTED.card.note}
          </p>
        </div>
        {tied && (
          <Badge variant="outline" className="tabular-nums">
            <Tie data-icon="inline-start" aria-hidden />
            {UI.tieChip(pool.length, first.product!, first.sales_price!)}
          </Badge>
        )}
        <ul aria-label={ASSISTED.select.listLabel} className="flex flex-col gap-2">
          {pool.map((item) => {
            const checked = chosen.includes(item.opportunity_id);
            const inputId = `assess-${item.opportunity_id}`;
            return (
              <li key={item.opportunity_id}
                  className="flex items-start gap-3 rounded-2xl border bg-card p-4 transition-colors hover:bg-muted/40 has-[[data-state=checked]]:border-primary has-[[data-state=checked]]:bg-accent">
                <Checkbox id={inputId} checked={checked} disabled={!checked && full} className="mt-0.5"
                          onCheckedChange={(value) => toggle(item.opportunity_id, value === true)} />
                <Label htmlFor={inputId} className="flex flex-1 flex-col items-start gap-0.5 font-normal">
                  <span className="flex flex-wrap items-center gap-2 font-semibold">
                    {item.opportunity_id}
                    {assessed.has(item.opportunity_id) && <Badge variant="secondary">{ASSISTED.select.assessed}</Badge>}
                  </span>
                  <span className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
                    {!tied && (
                      <span className="flex items-center gap-1">
                        <Product aria-hidden className="size-3.5" />
                        {item.product || UI.noProduct}
                      </span>
                    )}
                    {item.account ? (
                      <span className="flex items-center gap-1">
                        <Account aria-hidden className="size-3.5" />
                        {item.account}
                      </span>
                    ) : (
                      <span className="italic">{UI.noAccountShort}</span>
                    )}
                    {!tied && item.sales_price !== null && (
                      <span className="flex items-center gap-1 tabular-nums">
                        <ListPrice aria-hidden className="size-3.5" />
                        {formatInt(item.sales_price)}
                      </span>
                    )}
                  </span>
                </Label>
              </li>
            );
          })}
        </ul>
      </div>
      <AssessmentFooter className="justify-end">
        <Button className={cn(ASSESSMENT_CTA, FOOTER_BUTTON)} disabled={chosen.length < MIN_SET} onClick={onNext}>
          {ASSISTED.select.next}
        </Button>
      </AssessmentFooter>
    </>
  );
}
