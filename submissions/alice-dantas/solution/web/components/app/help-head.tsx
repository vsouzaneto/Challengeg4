"use client";

import { Info } from "lucide-react";

import { InfoPopover } from "@/components/app/info-popover";
import { Button } from "@/components/ui/button";
import { TableHead } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

/** Cabeçalho de coluna (sem ordenação) com a ajuda ao lado: tooltip por padrão, ou popover quando é uma ressalva
 * (abre no toque). */
export function HelpHead({ label, help, popover, className }: {
  label: string; help: string; popover?: string; className?: string;
}) {
  return (
    <TableHead className={cn("whitespace-normal", className)}>
      <span className="inline-flex items-center gap-1">
        {label}
        {popover ? (
          // Ressalva (não só ajuda): abre no toque, ao contrário do Tooltip.
          <InfoPopover label={popover}>{help}</InfoPopover>
        ) : (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-xs" aria-label={help} className="text-muted-foreground">
                <Info aria-hidden />
              </Button>
            </TooltipTrigger>
            <TooltipContent>{help}</TooltipContent>
          </Tooltip>
        )}
      </span>
    </TableHead>
  );
}
