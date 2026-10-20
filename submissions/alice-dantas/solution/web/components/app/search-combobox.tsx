"use client";

import { ChevronsUpDown } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { UI } from "@/copy/pt-BR";
import { cn } from "@/lib/utils";

type Props = {
  label: string;
  options: string[];
  value: string | null;
  onChange: (value: string | null) => void;
  searchPlaceholder: string;
  emptyText: string;
  triggerClassName?: string;
};

/** Filtro de uma lista longa (35 vendedores, 85 clientes): combobox do shadcn com busca e "Todos" no topo. A borda
 * e o fundo são os do Select, para os filtros lado a lado parecerem iguais. */
export function SearchCombobox({
  label, options, value, onChange, searchPlaceholder, emptyText, triggerClassName = "w-full sm:w-52",
}: Props) {
  const [open, setOpen] = useState(false);
  const pick = (next: string | null) => {
    onChange(next);
    setOpen(false);
  };
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" role="combobox" aria-expanded={open} aria-label={label}
                  className={cn("justify-between border-input bg-transparent font-normal", triggerClassName)}>
            <span className="truncate">{value ?? UI.filters.all}</span>
            <ChevronsUpDown className="text-muted-foreground" aria-hidden />
          </Button>
        </PopoverTrigger>
        <PopoverContent align="start" className="w-(--radix-popover-trigger-width) p-0 sm:w-64">
          <Command>
            <CommandInput placeholder={searchPlaceholder} />
            <CommandList>
              <CommandEmpty>{emptyText}</CommandEmpty>
              <CommandGroup>
                <CommandItem value={UI.filters.all} data-checked={value === null} onSelect={() => pick(null)}>
                  {UI.filters.all}
                </CommandItem>
                {options.map((option) => (
                  <CommandItem key={option} value={option} data-checked={option === value} onSelect={() => pick(option)}>
                    {option}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
