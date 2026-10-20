"use client";

import type { MouseEvent } from "react";

import {
  Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { UI } from "@/copy/pt-BR";
import { pageCount, pageWindow } from "@/lib/pagination";
import { cn } from "@/lib/utils";

type Props = {
  page: number;
  total: number;
  pageSize: number;
  onPage: (page: number) => void;
};

/** Paginação de tabela (sem rolagem infinita): faixa de linhas, anterior, páginas e próxima.
 * No celular ficam só anterior, a página atual e próxima. */
export function TablePagination({ page, total, pageSize, onPage }: Props) {
  const count = pageCount(total, pageSize);
  if (count <= 1) return null;
  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  const go = (target: number) => (event: MouseEvent) => {
    event.preventDefault();
    if (target >= 1 && target <= count && target !== page) onPage(target);
  };
  const edge = (disabled: boolean) => ({
    "aria-disabled": disabled || undefined,
    tabIndex: disabled ? -1 : undefined,
    className: cn(disabled && "pointer-events-none opacity-50"),
  });

  return (
    <div className="flex flex-col items-center gap-2 border-t px-4 py-3 sm:flex-row sm:justify-between">
      <p className="text-xs text-muted-foreground tabular-nums">{UI.pagination.range(from, to, total)}</p>
      <Pagination aria-label={UI.pagination.label} className="mx-0 w-auto">
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious href="#" text={UI.pagination.previous} aria-label={UI.pagination.previous}
                                onClick={go(page - 1)} {...edge(page === 1)} />
          </PaginationItem>
          {pageWindow(page, count).map((n, i) =>
            n === null ? (
              <PaginationItem key={`salto-${i}`} className="hidden sm:block">
                <PaginationEllipsis />
              </PaginationItem>
            ) : (
              <PaginationItem key={n} className={n === page ? undefined : "hidden sm:block"}>
                <PaginationLink href="#" isActive={n === page} aria-label={UI.pagination.page(n)} onClick={go(n)}
                                className="tabular-nums">
                  {n}
                </PaginationLink>
              </PaginationItem>
            ),
          )}
          <PaginationItem>
            <PaginationNext href="#" text={UI.pagination.next} aria-label={UI.pagination.next}
                            onClick={go(page + 1)} {...edge(page === count)} />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
}
