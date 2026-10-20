"use client";

import { ArrowRight, CircleHelp, FileSearch, Inbox, ListOrdered } from "lucide-react";
import { useEffect, useRef, useState, type ReactNode } from "react";

import { IconTile } from "@/components/app/icon-tile";
import { TablePagination } from "@/components/app/table-pagination";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia } from "@/components/ui/empty";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  GROUP_LABELS, UI, actionText, groupEmptyText, groupOrderShort, groupRange, groupShort,
  type AgeContextMeta, type AgeLimits,
} from "@/copy/pt-BR";
import { GROUP_VISUAL } from "@/copy/visual";
import type { Group, Item, Ordering } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import { PAGE_SIZE, pageOf } from "@/lib/pagination";
import { cn } from "@/lib/utils";

import { ItemsTable, itemRowId } from "./items-table";

type State = Group["state"];

type Props = {
  groups: Group[];
  tab: State;
  onTab: (state: State) => void;
  /** As oportunidades com a análise aberta na linha. */
  expanded: readonly string[];
  onToggle: (id: string) => void;
  /** A análise de uma oportunidade, mostrada dentro da linha aberta. */
  renderPanel: (item: Item) => ReactNode;
  /** Uma oportunidade que acabou de ser aberta de fora da lista (o cartão do topo): a lista vai até ela. */
  reveal?: { id: string } | null;
  limits: AgeLimits & AgeContextMeta;
  showSeller?: boolean;
  /** Busca ou filtro já aplicado aos grupos: um grupo que fica sem itens por causa dele diz isso. */
  filtered?: boolean;
  /** Linhas por página em cada aba. */
  pageSize?: number;
  /** Grupo cujo próximo passo já está no cartão "Seu próximo passo" (não repete a frase). */
  actionShownFor?: State;
  /** O selo de cada oportunidade avaliada na priorização assistida, por ID. */
  marks?: Record<string, string>;
  /** A ordem que veio da API, para o rodapé do popover dos grupos. */
  ordering?: Ordering;
  /** Escolha de oportunidades para a priorização assistida (só na Carteira). */
  selected?: readonly string[];
  onSelect?: (id: string, on: boolean) => void;
  maxSelected?: number;
};

/** O que cada grupo significa, na ordem das abas: ícone, nome na cor do grupo, chip do limite e a frase curta.
 * A definição inteira, com as ressalvas, fica em Como funciona. */
function GroupGuide({ groups, limits, ordering }: { groups: Group[]; limits: AgeLimits; ordering?: Ordering }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" className="text-muted-foreground">
          <CircleHelp aria-hidden />
          {UI.groupGuide.button}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start"
                      className="max-h-[min(32rem,70vh)] w-[min(24rem,calc(100vw-2rem))] gap-3 overflow-y-auto text-left">
        <p className="text-xs font-medium text-muted-foreground">{UI.groupGuide.title}</p>
        <dl className="flex flex-col gap-3">
          {groups.map((group) => {
            const visual = GROUP_VISUAL[group.state];
            return (
              <div key={group.state} className="grid grid-cols-[auto_1fr] items-start gap-x-3 gap-y-0.5">
                <IconTile icon={visual.icon} tone={visual.tile} size="sm" className="row-span-2" />
                <div className="flex flex-wrap items-center gap-2">
                  <dt className={cn("font-semibold", visual.text)}>{GROUP_LABELS[group.state]}</dt>
                  <Badge variant="outline" className="tabular-nums">{groupRange(group.state, limits)}</Badge>
                </div>
                <dd className="text-muted-foreground">{groupShort(group.state, limits)}</dd>
              </div>
            );
          })}
        </dl>
        <div className="flex flex-col gap-2 border-t pt-3 text-xs text-muted-foreground">
          {ordering && (
            <p className="flex items-start gap-1.5">
              <ListOrdered className="mt-0.5 size-3.5 shrink-0" aria-hidden />
              {groupOrderShort(ordering)}
            </p>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

function GroupIcon({ state }: { state: State }) {
  const Icon = GROUP_VISUAL[state].icon;
  return <Icon aria-hidden className={GROUP_VISUAL[state].text} />;
}

/** Faixa compacta acima da tabela: o limite do grupo, a frase curta e, quando o cartão do topo não a mostra, a
 * verificação do grupo. A definição inteira fica no botão ao lado das abas e em Como funciona. */
function GroupStrip({ group, limits, showAction }: { group: Group; limits: AgeLimits; showAction: boolean }) {
  const visual = GROUP_VISUAL[group.state];
  return (
    <div className={cn("flex flex-col gap-1.5 rounded-lg px-3 py-2 text-sm", visual.soft)}>
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <IconTile icon={visual.icon} tone={visual.tile} size="sm" className="bg-card/70" />
        <Badge variant="outline" className="bg-card tabular-nums">{groupRange(group.state, limits)}</Badge>
        <p className="order-last min-w-0 basis-full text-foreground sm:order-none sm:basis-0 sm:flex-1">
          {groupShort(group.state, limits)}
        </p>
      </div>
      {showAction && group.next_action && (
        <p className="flex items-start gap-1.5">
          <FileSearch className="mt-0.5 size-4 shrink-0 text-primary-strong" aria-hidden />
          <span>
            <span className="font-medium">{UI.verifyLabel}:</span> {actionText(group.next_action)}
          </span>
        </p>
      )}
    </div>
  );
}

/** Um grupo por aba, na ordem da API, com a contagem no rótulo. */
export function GroupTabs({
  groups, tab, onTab, expanded, onToggle, renderPanel, reveal, limits, showSeller, filtered = false, pageSize = PAGE_SIZE, actionShownFor,
  marks, ordering, selected, onSelect, maxSelected,
}: Props) {
  const [pages, setPages] = useState<Partial<Record<State, number>>>({});
  const tables = useRef<Partial<Record<State, HTMLDivElement | null>>>({});

  // Uma oportunidade aberta de fora da lista (o cartão do topo) pode estar em outra página: a tabela vai até ela
  // e, quando a linha está na tela, rola até ela.
  const pending = useRef<string | null>(null);
  useEffect(() => {
    if (!reveal) return;
    pending.current = reveal.id;
    for (const group of groups) {
      const index = group.items.findIndex((item) => item.opportunity_id === reveal.id);
      if (index >= 0) setPages((current) => ({ ...current, [group.state]: pageOf(index, pageSize) }));
    }
  }, [reveal, groups, pageSize]);
  useEffect(() => {
    if (!pending.current) return;
    const row = document.getElementById(itemRowId(pending.current));
    if (!row) return;
    pending.current = null;
    row.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  const goTo = (state: State, page: number) => {
    setPages((current) => ({ ...current, [state]: page }));
    tables.current[state]?.scrollIntoView({ block: "start", behavior: "smooth" });
  };

  return (
    <Tabs id="grupos" value={tab} onValueChange={(value) => onTab(value as State)} className="scroll-mt-20 gap-4">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <TabsList aria-label={UI.groupsLabel}
                  className="grid w-full grid-cols-2 group-data-horizontal/tabs:h-auto sm:inline-flex sm:w-fit sm:group-data-horizontal/tabs:h-9">
          {groups.map((group) => (
            <TabsTrigger key={group.state} value={group.state} className="h-8 px-3 sm:h-[calc(100%-1px)]">
              <GroupIcon state={group.state} />
              {GROUP_LABELS[group.state]}
              <Badge variant={group.count ? group.state : "secondary"} className="tabular-nums">
                {formatInt(group.count)}
              </Badge>
            </TabsTrigger>
          ))}
        </TabsList>
        <GroupGuide groups={groups} limits={limits} ordering={ordering} />
      </div>

      {groups.map((group) => {
        const page = pages[group.state] ?? 1;
        const range: [number, number] = [(page - 1) * pageSize, page * pageSize];
        return (
          <TabsContent key={group.state} value={group.state} className="flex flex-col gap-3">
            <GroupStrip group={group} limits={limits}
                        showAction={group.items.length > 0 && group.state !== actionShownFor} />

            {group.items.length ? (
              <Card className="scroll-mt-24 gap-0 py-0" ref={(node) => { tables.current[group.state] = node; }}>
                <ItemsTable items={group.items} expanded={expanded} onToggle={onToggle} renderPanel={renderPanel}
                            showSeller={showSeller}
                            meta={limits} range={range} marks={marks}
                            selected={selected} onSelect={onSelect} maxSelected={maxSelected} />
                <TablePagination page={page} total={group.items.length} pageSize={pageSize}
                                 onPage={(next) => goTo(group.state, next)} />
              </Card>
            ) : (
              <Empty className="border border-dashed">
                <EmptyHeader>
                  <EmptyMedia variant="icon">
                    <Inbox aria-hidden />
                  </EmptyMedia>
                  <EmptyDescription>
                    {group.empty ? groupEmptyText(group.empty) : filtered ? UI.listFilters.noneHere : null}
                  </EmptyDescription>
                </EmptyHeader>
                {group.empty?.code === "start_with_group" && (
                  <EmptyContent>
                    <Button variant="outline" onClick={() => onTab(group.empty!.params.group as State)}>
                      {UI.seeGroup(GROUP_LABELS[group.empty.params.group])}
                      <ArrowRight aria-hidden />
                    </Button>
                  </EmptyContent>
                )}
              </Empty>
            )}

          </TabsContent>
        );
      })}
    </Tabs>
  );
}
