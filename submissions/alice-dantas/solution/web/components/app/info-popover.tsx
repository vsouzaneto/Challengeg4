"use client";

import { Info, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

type Props = {
  /** Nome acessível do botão (e o título do popover). */
  label: string;
  children: ReactNode;
  /** Texto visível ao lado do ícone; sem ele, o botão é só o ícone. */
  text?: string;
  icon?: LucideIcon;
  className?: string;
};

/** Ajuda curta que abre no toque (ao contrário do Tooltip): ícone + Popover de até ~40 palavras. */
export function InfoPopover({ label, children, text, icon: Icon = Info, className }: Props) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size={text ? "xs" : "icon-xs"} aria-label={text ? undefined : label}
                className={cn("text-muted-foreground", className)}>
          <Icon aria-hidden />
          {text}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-[min(20rem,calc(100vw-2rem))] gap-1.5 text-left">
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        <div className="text-sm text-pretty">{children}</div>
      </PopoverContent>
    </Popover>
  );
}
