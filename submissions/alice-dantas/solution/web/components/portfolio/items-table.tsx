"use client";

import { Info } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { HelpHead } from "@/components/app/help-head";
import { panelId } from "@/components/portfolio/reason-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  TEAM, UI, ageContextText, bandCountShort, bandCountText, bandTitle, missingShort, type AgeContextMeta,
} from "@/copy/pt-BR";
import { ASSISTED } from "@/copy/assisted";
import { CONCEPT_ICONS } from "@/copy/visual";
import type { Item } from "@/lib/contract";
import { formatDate, formatInt } from "@/lib/format";
import { MOBILE_QUERY, useMediaQuery } from "@/lib/use-media-query";
import { cn } from "@/lib/utils";

const {
  listPrice: ListPrice, product: Product, account: Account, seller: Seller, age: Age, assisted: Assisted,
} = CONCEPT_ICONS;

/** O ID da linha de uma oportunidade na lista: a lista rola até ela quando o cartão do topo a abre. */
export const itemRowId = (id: string) => `item-${id}`;

type Props = {
  items: Item[];
  /** As oportunidades com a análise aberta na própria linha, em qualquer número: dá para comparar com a de baixo. */
  expanded: readonly string[];
  onToggle: (id: string) => void;
  /** A análise de uma oportunidade (o "Por que está aqui"), que a linha mostra quando aberta. */
  renderPanel: (item: Item) => ReactNode;
  showSeller?: boolean;
  /** Os limites e a mediana do histórico: com eles, a idade abre o contexto histórico. */
  meta?: AgeContextMeta;
  /** A página a mostrar, como posições [início, fim) na lista; sem ela, todas. As contagens de faixa
   * continuam sendo da lista inteira. */
  range?: [number, number];
  /** O selo de cada oportunidade já avaliada na priorização assistida, por ID. Não muda a ordem da lista. */
  marks?: Record<string, string>;
  /** Com `onSelect`, a lista ganha uma caixa por oportunidade para escolher quais comparar na priorização assistida. */
  selected?: readonly string[];
  onSelect?: (id: string, on: boolean) => void;
  /** Quantas cabem na escolha: com o limite atingido, as não marcadas ficam desativadas. */
  maxSelected?: number;
};

type PickProps = Pick<Props, "selected" | "onSelect" | "maxSelected">;

/** A caixa de escolha de uma linha. Não abre a análise: o clique fica nela. */
function PickBox({ id, selected = [], onSelect, maxSelected = Infinity }: PickProps & { id: string }) {
  if (!onSelect) return null;
  const checked = selected.includes(id);
  return (
    <Checkbox checked={checked} disabled={!checked && selected.length >= maxSelected}
              aria-label={ASSISTED.selection.row(id)}
              onClick={(event) => event.stopPropagation()}
              onCheckedChange={(value) => onSelect(id, value === true)} />
  );
}

/** O título de uma faixa de valor: ícone, nome curto, a contagem num chip e o atalho para as faixas. */
function BandHeading({ band, onPage, total, linked }: { band: string; onPage: number; total: number; linked: boolean }) {
  return (
    <span className="flex items-center gap-1.5 text-xs font-semibold">
      <ListPrice aria-hidden className="size-3.5 text-muted-foreground" />
      {band}
      <Badge variant="secondary" className="tabular-nums">
        <span aria-hidden>{bandCountShort(onPage, total)}</span>
        <span className="sr-only">{bandCountText(onPage, total)}</span>
      </Badge>
      {linked && (
        <Button asChild variant="ghost" size="icon-xs" className="text-muted-foreground">
          <Link href="/como-funciona" aria-label={UI.bandRangesLink}>
            <Info aria-hidden />
          </Link>
        </Button>
      )}
    </span>
  );
}

/** Lista na ordem que veio da API, com uma linha de título para cada faixa de valor de tabela. */
export function ItemsTable(props: Props) {
  // Só uma versão no DOM (IDs não duplicam); no servidor e no jsdom, a tabela.
  const mobile = useMediaQuery(MOBILE_QUERY);
  return mobile ? <ItemsList {...props} /> : <ItemsGrid {...props} />;
}

function countBands(items: Item[], range?: [number, number]) {
  const total = new Map<string, number>();
  const page = new Map<string, number>();
  items.forEach((item) => {
    const band = bandTitle(item.value_band);
    total.set(band, (total.get(band) ?? 0) + 1);
  });
  items.slice(...(range ?? [0, items.length])).forEach((item) => {
    const band = bandTitle(item.value_band);
    page.set(band, (page.get(band) ?? 0) + 1);
  });
  return { total, page };
}

/** Celular: um item por oportunidade, com o valor de tabela à direita do ID; sem numeração (empate não tem ordem). */
function ItemsList({ items, expanded, onToggle, renderPanel, showSeller = false, meta, range, marks, selected, onSelect, maxSelected }: Props) {
  const { total, page } = countBands(items, range);
  const sections: { band: string; linked: boolean; items: Item[] }[] = [];
  items.slice(...(range ?? [0, items.length])).forEach((item) => {
    const band = bandTitle(item.value_band);
    const last = sections[sections.length - 1];
    if (last?.band === band) last.items.push(item);
    else sections.push({ band, linked: Boolean(item.value_band), items: [item] });
  });
  return (
    <div className="flex flex-col">
      {sections.map((section) => (
        <section key={section.band} aria-label={section.band}>
          <div className="border-b bg-muted/50 px-4 py-2">
            <BandHeading band={section.band} onPage={page.get(section.band) ?? 0} total={total.get(section.band) ?? 0}
                         linked={section.linked} />
          </div>
          <ul className="divide-y border-b">
            {section.items.map((item) => {
              const active = expanded.includes(item.opportunity_id);
              const mark = marks?.[item.opportunity_id];
              return (
                <li key={item.opportunity_id} id={itemRowId(item.opportunity_id)} data-state={active ? "selected" : undefined}
                    className="flex scroll-mt-24 flex-col gap-1 py-3 data-[state=selected]:bg-accent/60">
                  <div className="flex flex-col gap-1 px-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="flex items-center gap-3">
                    <PickBox id={item.opportunity_id} selected={selected} onSelect={onSelect} maxSelected={maxSelected} />
                    <Button variant="link" size="sm" className="h-auto gap-1 px-0 font-semibold text-primary-strong"
                            aria-expanded={active} aria-controls={active ? panelId(item.opportunity_id) : undefined}
                            aria-label={UI.whyHereFor(item.opportunity_id)}
                            onClick={() => onToggle(item.opportunity_id)}>
                      {item.opportunity_id}
                    </Button>
                    </span>
                    <span className="text-base font-semibold tabular-nums">
                      <span className="sr-only">{UI.columns.price}:</span>
                      {item.sales_price === null ? UI.empty : formatInt(item.sales_price)}
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Product aria-hidden className="size-3.5" />
                      {item.product || UI.noProduct}
                    </span>
                    {item.account ? (
                      <span className="flex min-w-0 items-center gap-1">
                        <Account aria-hidden className="size-3.5 shrink-0" />
                        <span className="truncate">{item.account}</span>
                      </span>
                    ) : (
                      <span className="italic">{UI.noAccountShort}</span>
                    )}
                    {showSeller && (
                      <span className="flex items-center gap-1">
                        <Seller aria-hidden className="size-3.5" />
                        {item.sales_agent}
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    {item.age_days !== null && (
                      <span className="flex items-center gap-1">
                        <Age aria-hidden className="size-3.5" />
                        {meta ? <AgeContext age={item.age_days} meta={meta} /> : UI.ageDays(item.age_days)}
                      </span>
                    )}
                    {item.missing_field && <Badge variant="missing">{missingShort(item.missing_field)}</Badge>}
                    {mark && <Badge variant="reference" className="h-auto whitespace-normal"><Assisted data-icon="inline-start" aria-hidden />{mark}</Badge>}
                  </div>
                  </div>
                  {active && <div className="mt-2">{renderPanel(item)}</div>}
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}

function ItemsGrid({ items, expanded, onToggle, renderPanel, showSeller = false, meta, range, marks, selected, onSelect, maxSelected }: Props) {
  const columns = (showSeller ? 7 : 6) + (onSelect ? 1 : 0);
  const { total: bandCounts, page: pageCounts } = countBands(items, range);

  const rows: ReactNode[] = [];
  let band: string | null = null;
  items.slice(...(range ?? [0, items.length])).forEach((item) => {
    const title = bandTitle(item.value_band);
    if (title !== band) {
      band = title;
      rows.push(
        <TableRow key={`band-${band}`} className="hover:bg-transparent">
          <TableHead colSpan={columns} scope="colgroup" className="h-9 bg-muted/50">
            <BandHeading band={band} onPage={pageCounts.get(band) ?? 0} total={bandCounts.get(band) ?? 0}
                         linked={Boolean(item.value_band)} />
          </TableHead>
        </TableRow>,
      );
    }
    const active = expanded.includes(item.opportunity_id);
    rows.push(
      <Row key={item.opportunity_id} item={item} showSeller={showSeller} meta={meta} mark={marks?.[item.opportunity_id]}
           active={active} onToggle={onToggle} selected={selected} onSelect={onSelect} maxSelected={maxSelected} />,
    );
    if (active) {
      rows.push(
        <TableRow key={`${item.opportunity_id}-analise`} className="hover:bg-transparent">
          <TableCell colSpan={columns} className="p-0 whitespace-normal">{renderPanel(item)}</TableCell>
        </TableRow>,
      );
    }
  });

  return (
    <Table>
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          {onSelect && <TableHead className="w-10 pl-4"><span className="sr-only">{ASSISTED.selection.head}</span></TableHead>}
          <TableHead className={cn(!onSelect && "pl-4")}>{UI.columns.id}</TableHead>
          {showSeller && <TableHead className="whitespace-normal">{UI.columns.seller}</TableHead>}
          <TableHead>{UI.columns.product}</TableHead>
          <HelpHead label={UI.columns.client} help={UI.accountNote} popover={TEAM.accountNoteLabel} />
          <HelpHead label={UI.columns.price} help={UI.columnHelp.price} className="text-right" />
          <TableHead className="whitespace-normal">{UI.columns.engaged}</TableHead>
          <HelpHead label={UI.columns.age} help={UI.columnHelp.age} className="pr-4 text-right" />
        </TableRow>
      </TableHeader>
      <TableBody>{rows}</TableBody>
    </Table>
  );
}

type RowProps = {
  item: Item;
  showSeller: boolean;
  meta?: AgeContextMeta;
  mark?: string;
  active: boolean;
  onToggle: (id: string) => void;
} & PickProps;

function Row({ item, showSeller, meta, mark, active, onToggle, selected, onSelect, maxSelected }: RowProps) {
  return (
    <TableRow
      id={itemRowId(item.opportunity_id)}
      data-state={active ? "selected" : undefined}
      className="scroll-mt-24 cursor-pointer data-[state=selected]:bg-accent/60"
      onClick={() => onToggle(item.opportunity_id)}
    >
      {onSelect && (
        <TableCell className="w-10 pl-4">
          <PickBox id={item.opportunity_id} selected={selected} onSelect={onSelect} maxSelected={maxSelected} />
        </TableCell>
      )}
      <TableCell className={cn("whitespace-normal", !onSelect && "pl-4")}>
        <div className="flex flex-col items-start gap-1">
        <Button
          variant="link"
          size="sm"
          className="h-auto gap-1 px-0 font-semibold text-primary-strong"
          aria-expanded={active}
          aria-controls={active ? panelId(item.opportunity_id) : undefined}
          aria-label={UI.whyHereFor(item.opportunity_id)}
          onClick={(event) => {
            event.stopPropagation();
            onToggle(item.opportunity_id);
          }}
        >
          {item.opportunity_id}
        </Button>
        {mark && <Badge variant="reference" className="h-auto max-w-56 whitespace-normal"><Assisted data-icon="inline-start" aria-hidden />{mark}</Badge>}
        </div>
      </TableCell>
      {showSeller && <TableCell className="whitespace-normal">{item.sales_agent}</TableCell>}
      <TableCell>
        <span className="inline-flex items-center gap-2">
          {item.product || UI.empty}
          {item.missing_field && <Badge variant="missing">{missingShort(item.missing_field)}</Badge>}
        </span>
      </TableCell>
      <TableCell className={cn("whitespace-normal", !item.account && "text-muted-foreground italic")}>
        {item.account ?? UI.noAccountShort}
      </TableCell>
      <TableCell className="text-right tabular-nums">
        {item.sales_price === null ? UI.empty : formatInt(item.sales_price)}
      </TableCell>
      <TableCell className="tabular-nums">{item.engage_date ? formatDate(item.engage_date) : UI.empty}</TableCell>
      <TableCell className="pr-4 text-right tabular-nums">
        {item.age_days === null ? UI.empty : meta ? <AgeContext age={item.age_days} meta={meta} /> : UI.ageDays(item.age_days)}
      </TableCell>
    </TableRow>
  );
}

/** A idade como botão discreto: abre o contexto histórico (fatos das vendas ganhas), sem cor nem contagem. */
function AgeContext({ age, meta }: { age: number; meta: AgeContextMeta }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="h-auto px-1.5 py-0.5 font-normal tabular-nums underline decoration-dotted underline-offset-4"
          aria-label={`${UI.ageDays(age)}. ${UI.ageContextHelp}`}
          onClick={(event) => event.stopPropagation()}
        >
          {UI.ageDays(age)}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="gap-2 text-left" onClick={(event) => event.stopPropagation()}>
        <p className="text-xs font-medium text-muted-foreground">{UI.ageContextTitle}</p>
        <p>{ageContextText(age, meta)}</p>
        <p className="text-xs text-muted-foreground">{UI.ageContextNote}</p>
      </PopoverContent>
    </Popover>
  );
}
