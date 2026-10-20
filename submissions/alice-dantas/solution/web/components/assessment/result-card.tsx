"use client";

import { ArrowDown, ArrowUp, CircleHelp, Pencil } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ANSWER_SHORT, ASSISTED, CATEGORY_ACTIONS, CATEGORY_LABELS, CRITERIA_LABELS, noteText, unknownText, whyText,
} from "@/copy/assisted";
import { UI } from "@/copy/pt-BR";
import { CATEGORY_ICONS, CONCEPT_ICONS } from "@/copy/visual";
import type { CategoryCode } from "@/lib/assisted/model";
import { POLICY_VERSION } from "@/lib/assisted/model";
import type { Evaluation } from "@/lib/assisted/policy";
import type { Item } from "@/lib/contract";
import { formatDate } from "@/lib/format";

import { RemoveAssessment } from "./remove-assessment";

const { product: Product, account: Account, verify: Verify } = CONCEPT_ICONS;
// "Não sei" é a mesma resposta em todas as perguntas.
const ANSWER_UNKNOWN = ANSWER_SHORT.interest.unknown;

function CategoryIcon({ category }: { category: CategoryCode }) {
  const Icon = CATEGORY_ICONS[category];
  return <Icon data-icon="inline-start" aria-hidden />;
}

type Props = {
  evaluation: Evaluation;
  item: Item | undefined;
  /** Posição na ordem; sem ela (bloco à parte ou avaliação única), o cartão não mostra número. */
  position?: { value: number; tied: boolean; manual: boolean };
  assessedAt: string;
  policyVersion: string;
  onEdit: () => void;
  onRemove: () => void;
  onMove?: (delta: -1 | 1) => void;
  canUp?: boolean;
  canDown?: boolean;
};

/** Um resultado: pontos e faixa, categoria, por que, o que ainda não se sabe e o que fazer agora. */
export function ResultCard({
  evaluation, item, position, assessedAt, policyVersion, onEdit, onRemove, onMove, canUp, canDown,
}: Props) {
  const id = evaluation.opportunityId;
  const category = evaluation.category;
  const unknown = unknownText(evaluation);
  return (
    <Card size="sm" data-opportunity={id}>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          {position && (
            <Badge variant="secondary" className="tabular-nums">
              {ASSISTED.result.position(position.value, position.tied)}
            </Badge>
          )}
          {category && (
            <Badge variant="reference">
              <CategoryIcon category={category} />
              {CATEGORY_LABELS[category]}
            </Badge>
          )}
          {position?.manual && <Badge variant="outline">{ASSISTED.result.manual}</Badge>}
        </div>
        <CardTitle className="text-base">{id}</CardTitle>
        {item && (
          <p className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Product aria-hidden className="size-3.5" />
              {item.product || UI.noProduct}
            </span>
            {item.account ? (
              <span className="flex items-center gap-1">
                <Account aria-hidden className="size-3.5" />
                {item.account}
              </span>
            ) : (
              <span className="italic">{UI.noAccountShort}</span>
            )}
          </p>
        )}
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <p>
          <span className="text-2xl font-semibold tabular-nums">{ASSISTED.points(evaluation.confirmed)}</span>
          {evaluation.potential > evaluation.confirmed && (
            <span className="text-muted-foreground"> · {ASSISTED.potential(evaluation.potential)}</span>
          )}
        </p>
        {position?.tied && <p className="text-xs text-muted-foreground">{ASSISTED.result.tied}</p>}
        <dl className="flex flex-col gap-2">
          <div>
            <dt className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{ASSISTED.result.why}</dt>
            <dd className="leading-relaxed">
              {whyText(evaluation)}
              {evaluation.notes.map((note) => <span key={note.code} className="block">{noteText(note)}</span>)}
            </dd>
          </div>
          {unknown && (
            <div>
              <dt className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{ASSISTED.result.unknown}</dt>
              <dd>{ASSISTED.result.unknownBody(unknown)}</dd>
            </div>
          )}
          {category && (
            <div className="flex gap-2 rounded-lg bg-accent p-3 text-accent-foreground">
              <Verify aria-hidden className="mt-0.5 size-4 shrink-0 text-primary-strong" />
              <div>
                <dt className="text-xs font-medium text-primary-strong">{ASSISTED.result.todo}</dt>
                <dd className="leading-relaxed">{CATEGORY_ACTIONS[category]}</dd>
              </div>
            </div>
          )}
        </dl>
        <section aria-label={ASSISTED.result.breakdown} className="flex flex-col gap-1.5">
          <h4 className="text-xs font-medium text-muted-foreground">{ASSISTED.result.breakdown}</h4>
          <dl className="grid grid-cols-[1fr_auto] gap-x-4 gap-y-1 text-sm">
            {evaluation.breakdown.map((row) => (
              <div key={row.dimension} className="contents">
                <dt className="text-muted-foreground">{CRITERIA_LABELS[row.dimension]}</dt>
                <dd className="text-right tabular-nums">
                  {row.answer === "unknown" ? (
                    <span className="inline-flex items-center gap-1 text-muted-foreground">
                      <CircleHelp aria-hidden className="size-3.5" />
                      {ANSWER_UNKNOWN}
                    </span>
                  ) : (
                    ASSISTED.result.pointsOf(row.points, row.weight)
                  )}
                </dd>
              </div>
            ))}
          </dl>
        </section>
        <p className="text-xs text-muted-foreground">
          {ASSISTED.result.assessedOn(formatDate(assessedAt.slice(0, 10)))}
          {policyVersion !== POLICY_VERSION && ` · ${ASSISTED.result.recalculated}`}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" variant="outline" onClick={onEdit}>
            <Pencil aria-hidden />
            {ASSISTED.result.edit}
          </Button>
          <RemoveAssessment id={id} onRemove={onRemove} />
          {onMove && (
            <>
              <Button size="icon-sm" variant="outline" aria-label={ASSISTED.result.up(id)} disabled={!canUp}
                      onClick={() => onMove(-1)}>
                <ArrowUp aria-hidden />
              </Button>
              <Button size="icon-sm" variant="outline" aria-label={ASSISTED.result.down(id)} disabled={!canDown}
                      onClick={() => onMove(1)}>
                <ArrowDown aria-hidden />
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
