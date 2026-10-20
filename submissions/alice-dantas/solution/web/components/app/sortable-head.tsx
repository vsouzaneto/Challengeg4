"use client";

import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { TableHead } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { UI } from "@/copy/pt-BR";
import type { SortState } from "@/lib/sort";
import { cn } from "@/lib/utils";

type Props<K extends string> = {
  column: K;
  state: SortState<K>;
  onSort: (column: K) => void;
  children: ReactNode;
  /** Alinha o rótulo à direita, como os números da coluna. */
  numeric?: boolean;
  className?: string;
  /** O que a coluna mostra: aparece no tooltip ao passar o mouse ou focar o título (e é a descrição para leitores de tela). */
  help?: string;
};

/** Cabeçalho de coluna que ordena a tabela. O estado vai em `aria-sort`; o botão diz o que o próximo clique faz. */
export function SortableHead<K extends string>({ column, state, onSort, children, numeric, className, help }: Props<K>) {
  const dir = state?.key === column ? state.dir : null;
  const Icon = dir === "asc" ? ArrowUp : dir === "desc" ? ArrowDown : ChevronsUpDown;
  return (
    <TableHead aria-sort={dir === "asc" ? "ascending" : dir === "desc" ? "descending" : "none"}
               className={cn(numeric && "text-right", className)}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="ghost" size="sm" onClick={() => onSort(column)}
                  className={cn("-mx-2 h-8 gap-1 px-2 font-medium whitespace-nowrap", numeric && "flex-row-reverse")}>
            {children}
            <Icon aria-hidden className={cn("size-3.5", dir ? "text-foreground" : "text-muted-foreground")} />
            <span className="sr-only">{UI.sort.next(dir)}</span>
          </Button>
        </TooltipTrigger>
        {help && <TooltipContent className="max-w-64 text-pretty">{help}</TooltipContent>}
      </Tooltip>
    </TableHead>
  );
}
