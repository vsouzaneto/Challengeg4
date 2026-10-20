import { ArrowRight } from "lucide-react";

import { GroupBadge } from "@/components/app/group-badge";
import { InfoPopover } from "@/components/app/info-popover";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ASSISTED } from "@/copy/assisted";
import { rank, type Evaluation } from "@/lib/assisted/policy";
import {
  GROUP_LABELS, UI, actionText, startAction, startReasonShort,
} from "@/copy/pt-BR";
import { CONCEPT_ICONS } from "@/copy/visual";
import type { Group, Item, SellerPipeline } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import { firstBlock, startGroup } from "@/lib/portfolio";

const SHOWN = 5;
const { verify: Verify, tie: Tie, account: Account, age: Age, product: Product, listPrice: ListPrice, assisted: Assisted } =
  CONCEPT_ICONS;

type Props = {
  payload: Pick<SellerPipeline, "groups" | "empty">;
  onSelect: (id: string) => void;
  onShowGroup: (state: Group["state"]) => void;
  /** Abre a priorização assistida com as oportunidades empatadas do topo; sem ela, o botão não aparece. */
  onAssess?: (block: Item[]) => void;
  /** O selo de cada oportunidade já avaliada, por ID. */
  marks?: Record<string, string>;
  /** O resultado de cada oportunidade já avaliada: com duas ou mais completas, o cartão mostra a ordem delas. */
  scores?: Record<string, Evaluation>;
  /** A ordem que o vendedor escolheu para um conjunto avaliado, se houver. */
  orderFor?: (ids: string[]) => string[] | null;
};

/** Os atributos de uma oportunidade do bloco. No empate, produto e valor são iguais em todas e ficam no chip. */
function ItemAttributes({ item, tied }: { item: Item; tied: boolean }) {
  return (
    <span className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs font-normal text-muted-foreground">
      {!tied && (
        <span className="flex items-center gap-1">
          <Product aria-hidden className="size-3.5" />
          {item.product || UI.noProduct}
        </span>
      )}
      {!tied && (
        <span className="flex items-center gap-1 tabular-nums">
          <ListPrice aria-hidden className="size-3.5" />
          {item.sales_price === null ? UI.empty : formatInt(item.sales_price)}
        </span>
      )}
      {item.account ? (
        <span className="flex min-w-0 items-center gap-1">
          <Account aria-hidden className="size-3.5 shrink-0" />
          <span className="truncate">{item.account}</span>
        </span>
      ) : (
        <span className="italic">{UI.noAccountShort}</span>
      )}
      {item.age_days !== null && (
        <span className="flex items-center gap-1 tabular-nums">
          <Age aria-hidden className="size-3.5" />
          {UI.ageDays(item.age_days)}
        </span>
      )}
    </span>
  );
}

/** "O que verificar agora": a ação do grupo por onde começar e o primeiro bloco da ordem que veio da API. */
export function NextStepCard({ payload, onSelect, onShowGroup, onAssess, marks, scores, orderFor }: Props) {
  const group = startGroup(payload);
  if (!group || !group.next_action) return null;
  const head = payload.groups[0];
  // Focar vazio: o título diz por onde começar; a ação e o motivo vêm embaixo, em linhas próprias.
  const start = !head.items.length && head.empty?.code === "start_with_group" ? head.empty : null;
  const block = firstBlock(group);
  const first = block[0];
  // Pela avaliação do vendedor: as completas vêm primeiro, na ordem dos pontos; as demais seguem a ordem da regra.
  const evaluated = block.map((item) => scores?.[item.opportunity_id]).filter((e): e is Evaluation => Boolean(e));
  const complete = evaluated.filter((e) => e.status === "complete" && !e.aside);
  const ranking = complete.length >= 2 ? rank(evaluated, orderFor?.(complete.map((e) => e.opportunityId)) ?? null) : null;
  const places = new Map(ranking?.ordered.map((r) => [r.evaluation.opportunityId, r]));
  const ordered = ranking
    ? [...ranking.ordered.map((r) => block.find((i) => i.opportunity_id === r.evaluation.opportunityId)!),
       ...block.filter((i) => !places.has(i.opportunity_id))]
    : block;
  const shown = ordered.slice(0, SHOWN);
  const tied = block.length > 1 && Boolean(first.product) && first.sales_price !== null;

  return (
    <Card className="ring-primary/40">
      <CardHeader>
        <CardDescription className="flex items-center gap-2 font-medium text-primary-strong">
          <Verify className="size-4" aria-hidden />
          {UI.nextStepTitle}
        </CardDescription>
        <CardTitle className="text-lg leading-7 font-semibold text-pretty">
          {start ? UI.startHeadline(GROUP_LABELS[group.state]) : actionText(group.next_action)}
        </CardTitle>
        {start && (
          <div className="flex flex-col gap-0.5">
            <p className="text-sm text-pretty">{startAction(start)}</p>
            <p className="text-xs text-muted-foreground">{startReasonShort(start, head.state)}</p>
          </div>
        )}
        <CardAction>
          <GroupBadge state={group.state} />
        </CardAction>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {tied ? (
          <div className="flex items-center gap-1">
            <Badge variant="outline" className="tabular-nums">
              <Tie data-icon="inline-start" aria-hidden />
              {UI.tieChip(block.length, first.product!, first.sales_price!)}
            </Badge>
            <InfoPopover label={UI.tieHelpLabel}>{UI.tieHelp}</InfoPopover>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">{UI.startWithOne}</p>
        )}
        {ranking && (
          <p className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <Assisted aria-hidden className="size-3.5" />
            {ASSISTED.card.orderedBy}
          </p>
        )}
        <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {shown.map((item) => (
            <li key={item.opportunity_id}>
              <Button
                variant="outline"
                className="h-full w-full flex-col items-start justify-start gap-1 px-3 py-2 text-left whitespace-normal"
                onClick={() => onSelect(item.opportunity_id)}
              >
                <span className="flex w-full items-center gap-2">
                  {places.get(item.opportunity_id) && (
                    <Badge variant="default" className="tabular-nums">
                      {ASSISTED.result.position(places.get(item.opportunity_id)!.position, places.get(item.opportunity_id)!.tied)}
                    </Badge>
                  )}
                  <span className="font-semibold">{item.opportunity_id}</span>
                  {places.get(item.opportunity_id) && (
                    <span className="ml-auto text-sm font-semibold tabular-nums">
                      {ASSISTED.points(places.get(item.opportunity_id)!.evaluation.confirmed)}
                    </span>
                  )}
                </span>
                <ItemAttributes item={item} tied={tied} />
                {marks?.[item.opportunity_id] && (
                  <Badge variant="reference" className="mt-1 h-auto whitespace-normal"><Assisted data-icon="inline-start" aria-hidden />{marks[item.opportunity_id]}</Badge>
                )}
              </Button>
            </li>
          ))}
        </ul>
        {onAssess && tied && (
          <div className="flex flex-col gap-2 rounded-lg border border-dashed p-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="flex items-start gap-2 text-sm">
              <Assisted className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden />
              <span>
                {ASSISTED.card.hint}
                <span className="block text-xs text-muted-foreground">{ASSISTED.card.note}</span>
              </span>
            </p>
            <Button variant="outline" className="shrink-0" onClick={() => onAssess(block)}>
              {ASSISTED.card.button}
            </Button>
          </div>
        )}
        <Button variant="link" className="w-fit px-0 text-primary-strong" onClick={() => onShowGroup(group.state)}>
          {block.length > shown.length
            ? UI.moreInTab(block.length - shown.length, GROUP_LABELS[group.state])
            : UI.seeGroup(GROUP_LABELS[group.state])}
          <ArrowRight aria-hidden />
        </Button>
      </CardContent>
    </Card>
  );
}
