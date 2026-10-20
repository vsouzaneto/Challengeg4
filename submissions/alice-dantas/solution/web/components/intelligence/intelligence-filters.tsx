"use client";

import { SlidersHorizontal, X } from "lucide-react";

import { FilterSelect } from "@/components/app/filter-select";
import { SearchCombobox } from "@/components/app/search-combobox";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Popover, PopoverContent, PopoverDescription, PopoverHeader, PopoverTitle, PopoverTrigger,
} from "@/components/ui/popover";
import { DIMENSION_LABELS, INTELLIGENCE, UI, officeLabel, sectorLabel, sizeLabel } from "@/copy/pt-BR";
import type { Intelligence, IntelligenceFilter, Seller, SizeBand } from "@/lib/contract";
import { accountChoices, activeFilters, emptyFilter } from "@/lib/intelligence";
import { filterOptions } from "@/lib/team";

const text = INTELLIGENCE.filters;
const FULL = "w-full";

type Props = {
  filter: IntelligenceFilter;
  /** Nulo enquanto a primeira resposta não chega: os filtros aparecem só com o valor escolhido. */
  options: Intelligence["options"] | null;
  sellers: Seller[];
  onChange: (changes: Partial<IntelligenceFilter>) => void;
};

const withValue = (options: string[], value: string | null) =>
  value && !options.includes(value) ? [...options, value] : options;

const sizeText = (key: string, sizes: SizeBand[]) => {
  const band = sizes.find((b) => b.key === key);
  return band ? sizeLabel(band, sizes) : key;
};

/** O recorte da página num botão: os sete filtros num painel, cada mudança vai para a URL. Vendedor, gerente e
 * escritório vêm do cadastro e se estreitam entre si, como na Equipe; produto, setor, cliente e porte vêm da
 * própria resposta. */
export function IntelligenceFilters({ filter, options, sellers, onChange }: Props) {
  const active = activeFilters(filter);
  const team = filterOptions(sellers, filter.manager, filter.office);
  const sellerNames = sellers.filter((s) => (!filter.manager || s.manager === filter.manager)
    && (!filter.office || s.office === filter.office)).map((s) => s.name);
  const sizes = options?.sizes ?? [];
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" className="relative max-lg:size-9 max-lg:px-0">
          <SlidersHorizontal aria-hidden />
          <span className="max-lg:sr-only">{text.button}</span>
          {active.length > 0 && <Badge variant="secondary" className="tabular-nums max-lg:absolute max-lg:-top-2 max-lg:-right-2 max-lg:h-4 max-lg:min-w-4 max-lg:px-1 max-lg:text-[0.625rem]">{active.length}</Badge>}
        </Button>
      </PopoverTrigger>
      {/* No celular, o painel respeita a margem de 16 px e rola sozinho se passar da altura da tela. */}
      <PopoverContent align="end" collisionPadding={16} aria-label={INTELLIGENCE.filtersLabel}
                      className="max-h-(--radix-popover-content-available-height) w-[min(36rem,calc(100vw-2rem))] overflow-y-auto">
        <PopoverHeader>
          <PopoverTitle className="font-semibold">{text.title}</PopoverTitle>
          <PopoverDescription>{text.help}</PopoverDescription>
        </PopoverHeader>
        <div className="grid gap-3 sm:grid-cols-2">
          <FilterSelect label={DIMENSION_LABELS.product} options={withValue(options?.products ?? [], filter.product)}
                        value={filter.product} onChange={(product) => onChange({ product })} triggerClassName={FULL} />
          <SearchCombobox label={DIMENSION_LABELS.seller} options={withValue(sellerNames, filter.seller)}
                          value={filter.seller} onChange={(seller) => onChange({ seller })} triggerClassName={FULL}
                          searchPlaceholder={INTELLIGENCE.searchSeller} emptyText={INTELLIGENCE.noMatch} />
          <FilterSelect label={DIMENSION_LABELS.manager} options={team.managers} value={filter.manager}
                        onChange={(manager) => onChange({ manager })} triggerClassName={FULL} />
          <FilterSelect label={DIMENSION_LABELS.office} options={team.offices} value={filter.office}
                        onChange={(office) => onChange({ office })} triggerClassName={FULL} />
          <FilterSelect label={DIMENSION_LABELS.sector} options={withValue(options?.sectors ?? [], filter.sector)}
                        value={filter.sector} onChange={(sector) => onChange({ sector })} triggerClassName={FULL}
                        optionLabel={sectorLabel} />
          <SearchCombobox label={DIMENSION_LABELS.account}
                          options={withValue(options ? accountChoices(options, filter.sector) : [], filter.account)}
                          value={filter.account} onChange={(account) => onChange({ account })} triggerClassName={FULL}
                          searchPlaceholder={INTELLIGENCE.searchAccount} emptyText={INTELLIGENCE.noMatch} />
          <FilterSelect label={DIMENSION_LABELS.size} options={withValue(sizes.map((b) => b.key), filter.size)}
                        value={filter.size} onChange={(size) => onChange({ size })} triggerClassName={FULL}
                        optionLabel={(key) => sizeText(key, sizes)} />
        </div>
        {active.length > 0 && (
          <Button variant="ghost" className="w-fit" onClick={() => onChange(emptyFilter())}>
            <X aria-hidden />
            {UI.filters.clear}
          </Button>
        )}
      </PopoverContent>
    </Popover>
  );
}

/** O recorte ativo, sempre à vista: um chip por filtro, que tira só aquele filtro. */
export function ActiveFilters({ filter, sizes, onChange }: {
  filter: IntelligenceFilter; sizes: SizeBand[]; onChange: (changes: Partial<IntelligenceFilter>) => void;
}) {
  const active = activeFilters(filter);
  if (!active.length) return null;
  return (
    <div role="group" aria-label={text.activeLabel} className="flex flex-wrap items-center gap-2">
      {active.map((key) => {
        const raw = filter[key] as string;
        const value = key === "size" ? sizeText(raw, sizes) : key === "sector" ? sectorLabel(raw)
          : key === "office" ? officeLabel(raw) : raw;
        return (
          <Button key={key} variant="secondary" size="sm" aria-label={text.remove(DIMENSION_LABELS[key], value)}
                  onClick={() => onChange({ [key]: null })}>
            {text.chip(DIMENSION_LABELS[key], value)}
            <X aria-hidden />
          </Button>
        );
      })}
      <Button variant="ghost" size="sm" onClick={() => onChange(emptyFilter())}>{UI.filters.clear}</Button>
    </div>
  );
}
