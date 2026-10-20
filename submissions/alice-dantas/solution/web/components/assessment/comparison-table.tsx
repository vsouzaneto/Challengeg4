"use client";

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ASSISTED, CRITERIA_LABELS, answerLabel } from "@/copy/assisted";
import { DIMENSIONS } from "@/lib/assisted/model";
import type { Evaluation } from "@/lib/assisted/policy";

/** As respostas de cada oportunidade lado a lado, uma coluna por oportunidade. */
export function ComparisonTable({ evaluations }: { evaluations: Evaluation[] }) {
  return (
    <Table aria-label={ASSISTED.result.compareLabel}>
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          <TableHead />
          {evaluations.map((e) => <TableHead key={e.opportunityId}>{e.opportunityId}</TableHead>)}
        </TableRow>
      </TableHeader>
      <TableBody>
        {DIMENSIONS.map((dimension) => (
          <TableRow key={dimension}>
            <TableHead scope="row" className="font-medium">{CRITERIA_LABELS[dimension]}</TableHead>
            {evaluations.map((e) => {
              const row = e.breakdown.find((b) => b.dimension === dimension)!;
              return (
                <TableCell key={e.opportunityId} className={row.answer === "unknown" ? "text-muted-foreground" : undefined}>
                  {answerLabel(dimension, row.answer, true)}
                  {row.answer !== null && (
                    <span className="block text-xs text-muted-foreground tabular-nums">{row.points}/{row.weight}</span>
                  )}
                </TableCell>
              );
            })}
          </TableRow>
        ))}
        <TableRow className="hover:bg-transparent">
          <TableHead scope="row" className="font-semibold">{ASSISTED.pointsLabel}</TableHead>
          {evaluations.map((e) => (
            <TableCell key={e.opportunityId} className="font-semibold tabular-nums">{e.confirmed}</TableCell>
          ))}
        </TableRow>
      </TableBody>
    </Table>
  );
}
