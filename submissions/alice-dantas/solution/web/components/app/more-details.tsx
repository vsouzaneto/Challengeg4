"use client";

import { ChevronDown } from "lucide-react";
import { useState, type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { UI } from "@/copy/pt-BR";
import { cn } from "@/lib/utils";

type Props = {
  children: ReactNode;
  /** Rótulo do gatilho; o padrão é "Ver detalhe". */
  label?: string;
  /** Nome da região (para testes e leitores de tela). */
  regionLabel?: string;
  className?: string;
  contentClassName?: string;
};

/** "Ver detalhe": o texto sai do nível 1 mas fica no DOM (forceMount) e a um clique, com gatilho visível. Um padrão só:
 * o rótulo não muda, a seta aponta para baixo fechado e gira para cima aberto, e o conteúdo vem num bloco com fundo
 * próprio. */
export function MoreDetails({ children, label = UI.details.show, regionLabel, className, contentClassName }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <Collapsible open={open} onOpenChange={setOpen} className={cn("flex flex-col gap-2", className)}>
      <CollapsibleTrigger asChild>
        <Button variant="link" size="sm" className="h-auto w-fit gap-1 px-0 text-primary-strong">
          {label}
          <ChevronDown aria-hidden className={cn("transition-transform", open && "rotate-180")} />
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent forceMount role={regionLabel ? "region" : undefined} aria-label={regionLabel}
                          className={cn("rounded-lg border bg-background/60 p-3 data-[state=closed]:hidden", contentClassName)}>
        {children}
      </CollapsibleContent>
    </Collapsible>
  );
}
