"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { SortableHead } from "@/components/app/sortable-head";
import { TablePagination } from "@/components/app/table-pagination";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/ui/table";
import { INTELLIGENCE, countryLabel, officeLabel, sectorLabel } from "@/copy/pt-BR";
import type { Crosstab, IntelligenceFilter, SellerProductMatrix } from "@/lib/contract";
import { formatInt } from "@/lib/format";
import { heatLevel } from "@/lib/intelligence";
import { PAGE_SIZE } from "@/lib/pagination";
import { useSort } from "@/lib/sort";
import { cn } from "@/lib/utils";

const text = INTELLIGENCE.crosstab;
// A cor só acompanha a fatia que está escrita na célula (cor nunca sozinha).
const HEAT = ["", "bg-heat-1", "bg-heat-2", "bg-heat-3", "bg-heat-4"] as const;

type TableId = keyof typeof text.tables;
type Row = Crosstab["rows"][number];

/** O vendedor × produto que já existia vira o mesmo formato dos demais cruzamentos. */
function fromMatrix(matrix: SellerProductMatrix): Crosstab & { id: "seller_product" } {
  return {
    id: "seller_product", row_dimension: "seller", column_dimension: "product", columns: matrix.products,
    rows: matrix.rows.map((row) => ({
      key: row.seller, closed: row.closed,
      cells: row.cells.map((cell) => ({ key: cell.product, closed: cell.closed, share: cell.mix_share })),
    })),
  } as Crosstab & { id: "seller_product" };
}

const rowLabel = (dimension: Crosstab["row_dimension"], key: string) =>
  dimension === "sector" ? sectorLabel(key) : dimension === "location" ? countryLabel(key) : key;
const columnLabel = (dimension: Crosstab["column_dimension"], key: string) =>
  dimension === "sector" ? sectorLabel(key) : dimension === "office" ? officeLabel(key) : key;

/** Os filtros que levam às negociações de uma célula. O país da sede não é filtro da página: sem ele, a célula só informa. */
function segmentOf(table: Crosstab, row: Row, column: string): Partial<IntelligenceFilter> | null {
  if (table.row_dimension === "location") return null;
  return { [table.row_dimension]: row.key, [table.column_dimension]: column };
}

/** Um cruzamento por vez, escolhido no seletor: o que cada cliente, setor ou vendedor compra ou atende e a relação
 * entre setor, país e escritório. Contagens de fechadas e a fatia de cada coluna; sem taxa de ganho por célula. */
export function CrosstabExplorer({ matrix, crosstabs, onDeals }: {
  matrix: SellerProductMatrix; crosstabs: Crosstab[]; onDeals: (segment: Partial<IntelligenceFilter>) => void;
}) {
  const tables = useMemo(() => [fromMatrix(matrix), ...crosstabs] as (Crosstab & { id: TableId })[], [matrix, crosstabs]);
  const [id, setId] = useState<TableId>("seller_product");
  const table = tables.find((t) => t.id === id) ?? tables[0];
  return (
    <section aria-labelledby="cruzamento" className="flex scroll-mt-24 flex-col gap-4" id="cruzamentos">
      <div className="flex flex-col gap-1.5">
        <span className="text-xs font-medium text-muted-foreground">{text.viewBy}</span>
        <Select value={table.id} onValueChange={(next) => setId(next as TableId)}>
          <SelectTrigger aria-label={text.viewBy} className="w-full sm:w-72">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {tables.map((t) => <SelectItem key={t.id} value={t.id}>{text.tables[t.id].option}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      <CrosstabCard key={table.id} table={table} onDeals={onDeals} />
    </section>
  );
}

/** O cartão de um cruzamento; remonta ao trocar de cruzamento para a ordenação e a página recomeçarem. */
function CrosstabCard({ table, onDeals }: { table: Crosstab & { id: TableId }; onDeals: (segment: Partial<IntelligenceFilter>) => void }) {
  const copy = text.tables[table.id];
  const [page, setPage] = useState(1);
  const accessors = useMemo<Record<string, (row: Row) => string | number | null>>(() => ({
    name: (row) => rowLabel(table.row_dimension, row.key),
    total: (row) => row.closed,
    ...Object.fromEntries(table.columns.map((column) => [
      column, (row: Row) => row.cells.find((cell) => cell.key === column)?.closed ?? null,
    ])),
  }), [table]);
  const { sorted, state, toggle } = useSort(table.rows, accessors, () => setPage(1));
  const rows = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  return (
    <Card className="gap-4 pb-0">
      <CardHeader>
        <CardTitle id="cruzamento" className="text-lg font-semibold">{copy.title}</CardTitle>
      </CardHeader>
      <CardContent className="px-0">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <SortableHead column="name" state={state} onSort={toggle} className="pl-6" help={text.firstHelp}>
                {copy.first}
              </SortableHead>
              {table.columns.map((column) => (
                <SortableHead key={column} column={column} state={state} onSort={toggle} numeric
                              help={text.columnHelp(columnLabel(table.column_dimension, column))}>
                  {columnLabel(table.column_dimension, column)}
                </SortableHead>
              ))}
              <SortableHead column="total" state={state} onSort={toggle} numeric className="pr-6" help={text.totalHelp}>
                {INTELLIGENCE.matrix.total}
              </SortableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => {
              const name = rowLabel(table.row_dimension, row.key);
              return (
                <TableRow key={row.key} className="hover:bg-transparent">
                  <TableCell className="pl-6 font-medium">{name}</TableCell>
                  {row.cells.map((cell) => {
                    const segment = segmentOf(table, row, cell.key);
                    const label = columnLabel(table.column_dimension, cell.key);
                    return (
                      <TableCell key={cell.key} className="p-1 text-right">
                        {cell.closed && segment ? (
                          <Button variant="ghost" size="sm" aria-label={text.cellLabel(name, label)}
                                  className={cn("w-full justify-end tabular-nums", HEAT[heatLevel(cell.share)])}
                                  onClick={() => onDeals(segment)}>
                            {text.cell(cell.closed, cell.share)}
                          </Button>
                        ) : cell.closed ? (
                          <span className={cn("block rounded-md px-3 py-1 tabular-nums", HEAT[heatLevel(cell.share)])}>
                            {text.cell(cell.closed, cell.share)}
                          </span>
                        ) : (
                          <span className="px-3 text-muted-foreground tabular-nums">{formatInt(0)}</span>
                        )}
                      </TableCell>
                    );
                  })}
                  <TableCell className="pr-6 text-right tabular-nums">{formatInt(row.closed)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        <TablePagination page={page} total={table.rows.length} pageSize={PAGE_SIZE} onPage={setPage} />
      </CardContent>
      <CardFooter className="flex-col items-start gap-1 border-t pb-6 text-sm text-pretty text-muted-foreground">
        <p>{copy.help}</p>
        <p>
          {text.noRate}{" "}
          <Link href="/como-funciona#nao-usa" className="font-medium text-primary-strong underline underline-offset-4">
            {INTELLIGENCE.matrix.noRateSee}
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}
