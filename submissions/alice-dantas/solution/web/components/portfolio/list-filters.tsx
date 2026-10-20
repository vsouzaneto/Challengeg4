"use client";

import { Search, SlidersHorizontal, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { FilterSelect } from "@/components/app/filter-select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { UI, bandTitle } from "@/copy/pt-BR";
import { NO_FILTERS, activeFilterCount, hasFilters, type ListFilters } from "@/lib/portfolio";
import { cn } from "@/lib/utils";

type Props = {
  filters: ListFilters;
  onChange: (filters: ListFilters) => void;
  products: string[];
  className?: string;
};

const SEARCH_DELAY_MS = 250;
const BANDS = ["alto", "médio", "baixo"] as const;
const L = UI.listFilters;

/** Busca por ID, produto ou cliente e filtros da lista, numa linha só. Nada aqui muda a ordem nem o grupo da
 * oportunidade. */
export function ListFiltersBar({ filters, onChange, products, className }: Props) {
  // A busca digita na hora e vai para a URL com um respiro, para não refazer a lista a cada letra.
  const [text, setText] = useState(filters.q);
  const latest = useRef(filters);
  latest.current = filters;
  useEffect(() => setText(filters.q), [filters.q]);
  useEffect(() => {
    if (text === latest.current.q) return;
    const timer = setTimeout(() => onChange({ ...latest.current, q: text }), SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [text, onChange]);

  const count = activeFilterCount(filters);
  const set = (changes: Partial<ListFilters>) => onChange({ ...filters, ...changes });
  const number = (value: string): number | null => (value === "" ? null : Math.max(0, Math.trunc(Number(value))));

  return (
    <section aria-label={L.title} className={cn("flex flex-col gap-2 sm:flex-row sm:items-center", className)}>
      <div className="relative sm:min-w-0 sm:max-w-80 sm:flex-1">
        <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
        <Input
          type="search"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder={L.searchPlaceholder}
          aria-label={L.searchLabel}
          className="pl-9"
        />
      </div>

      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline" className="w-fit">
            <SlidersHorizontal aria-hidden />
            {L.button}
            {count > 0 && <Badge variant="secondary" className="tabular-nums">{count}</Badge>}
          </Button>
        </PopoverTrigger>
        <PopoverContent align="end" className="w-[min(22rem,calc(100vw-2rem))] gap-3">
          <p className="text-sm font-semibold">{L.title}</p>
          <FilterSelect label={L.account} options={["com", "sem"]} value={filters.account}
                        onChange={(value) => set({ account: value as ListFilters["account"] })}
                        optionLabel={(option) => (option === "com" ? L.accountWith : L.accountWithout)}
                        triggerClassName="w-full" />
          <FilterSelect label={L.product} options={products} value={filters.product}
                        onChange={(value) => set({ product: value })} triggerClassName="w-full" />
          <FilterSelect label={L.band} options={[...BANDS]} value={filters.band}
                        onChange={(value) => set({ band: value as ListFilters["band"] })}
                        optionLabel={(option) => bandTitle(option as (typeof BANDS)[number])}
                        triggerClassName="w-full" />
          <fieldset className="flex flex-col gap-1.5">
            <legend className="text-xs font-medium text-muted-foreground">{L.age}</legend>
            <div className="grid grid-cols-2 gap-2">
              <Input type="number" min={0} inputMode="numeric" placeholder={L.from} aria-label={L.ageFrom}
                     value={filters.ageMin ?? ""} onChange={(event) => set({ ageMin: number(event.target.value) })} />
              <Input type="number" min={0} inputMode="numeric" placeholder={L.to} aria-label={L.ageTo}
                     value={filters.ageMax ?? ""} onChange={(event) => set({ ageMax: number(event.target.value) })} />
            </div>
          </fieldset>
          <fieldset className="flex flex-col gap-1.5">
            <legend className="text-xs font-medium text-muted-foreground">{L.engaged}</legend>
            <div className="grid grid-cols-2 gap-2">
              <Input type="date" aria-label={L.engagedFrom} value={filters.from ?? ""}
                     onChange={(event) => set({ from: event.target.value || null })} />
              <Input type="date" aria-label={L.engagedTo} value={filters.to ?? ""}
                     onChange={(event) => set({ to: event.target.value || null })} />
            </div>
          </fieldset>
          <p className="text-xs text-muted-foreground">{L.undated}</p>
        </PopoverContent>
      </Popover>

      {hasFilters(filters) && (
        <Button variant="ghost" className="w-fit" onClick={() => onChange(NO_FILTERS)}>
          <X aria-hidden />
          {L.clear}
        </Button>
      )}
    </section>
  );
}

/** Quantas oportunidades a lista mostra com a busca e os filtros, contra o total; só aparece quando há algum. */
export function ListFiltersStatus({ filters, shown, total }: { filters: ListFilters; shown: number; total: number }) {
  if (!hasFilters(filters)) return null;
  return <p className="text-xs text-muted-foreground" role="status">{L.result(shown, total)}</p>;
}
