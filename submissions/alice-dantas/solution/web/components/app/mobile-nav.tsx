"use client";

import { Check, Menu } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { NAV, UI } from "@/copy/pt-BR";
import { NAV_ITEMS, isActive } from "@/lib/nav";
import { cn } from "@/lib/utils";

/** Menu das páginas em telas estreitas: um botão que abre a lista, no lugar de uma segunda linha no cabeçalho. */
export function MobileNav({ className }: { className?: string }) {
  const pathname = usePathname();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" aria-label={UI.menu} className={className}>
          <Menu aria-hidden />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-52">
        {NAV_ITEMS.map((item) => {
          const active = isActive(pathname, item.href);
          return (
            <DropdownMenuItem key={item.key} asChild className={cn("justify-between", active && "bg-muted font-medium")}>
              <Link href={item.href} aria-current={active ? "page" : undefined}>
                {NAV[item.key]}
                {active && <Check aria-hidden className="size-4" />}
              </Link>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
