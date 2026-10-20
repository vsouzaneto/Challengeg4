"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { UI } from "@/copy/pt-BR";

// O Select do Radix não aceita valor vazio: "todos" é uma chave interna dos filtros.
const ALL = "__todos__";

type Props = {
  label: string;
  options: string[];
  value: string | null;
  onChange: (value: string | null) => void;
  /** Texto de cada opção, quando não é o próprio valor (ex.: o porte do cliente). */
  optionLabel?: (value: string) => string;
  /** Largura do campo; dentro de um painel de filtros, a coluna inteira. */
  triggerClassName?: string;
};

/** Filtro de uma lista curta, com "Todos" no topo. Usado na Equipe e na Inteligência. */
export function FilterSelect({
  label, options, value, onChange, optionLabel = (option) => option, triggerClassName = "w-full sm:w-52",
}: Props) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <Select value={value ?? ALL} onValueChange={(next) => onChange(next === ALL ? null : next)}>
        <SelectTrigger aria-label={label} className={triggerClassName}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ALL}>{UI.filters.all}</SelectItem>
          {options.map((option) => (
            <SelectItem key={option} value={option}>
              {optionLabel(option)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
