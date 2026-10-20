"use client";

import { ChevronsUpDown, UserRound } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { UI } from "@/copy/pt-BR";
import type { Seller } from "@/lib/contract";

type Props = {
  sellers: Seller[];
  value: string;
  onChange: (name: string) => void;
};

/** Escolha do vendedor (35 nomes): combobox do shadcn, com busca. A lista vem em ordem alfabética da API. */
export function SellerCombobox({ sellers, value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-label={UI.seller}
          disabled={!sellers.length}
          className="w-full justify-between sm:w-64"
        >
          <span className="flex min-w-0 items-center gap-2">
            <UserRound className="text-muted-foreground" aria-hidden />
            <span className={value ? "truncate" : "truncate text-muted-foreground"}>{value || UI.pickSeller}</span>
          </span>
          <ChevronsUpDown className="text-muted-foreground" aria-hidden />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-(--radix-popover-trigger-width) p-0 sm:w-64">
        <Command>
          <CommandInput placeholder={UI.searchSeller} />
          <CommandList>
            <CommandEmpty>{UI.noSellerFound}</CommandEmpty>
            <CommandGroup>
              {sellers.map((seller) => (
                <CommandItem
                  key={seller.name}
                  value={seller.name}
                  data-checked={seller.name === value}
                  onSelect={() => {
                    onChange(seller.name);
                    setOpen(false);
                  }}
                >
                  {seller.name}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
