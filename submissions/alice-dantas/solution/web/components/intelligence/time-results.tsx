"use client";

import { Bar, BarChart, XAxis, YAxis } from "recharts";

import { HelpHead } from "@/components/app/help-head";
import { ChartTip, tipRow } from "@/components/app/chart-tip";
import { type ChartConfig, ChartContainer, ChartLegend, ChartLegendContent } from "@/components/ui/chart";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/ui/table";
import { INTELLIGENCE, UI } from "@/copy/pt-BR";
import type { Intelligence } from "@/lib/contract";
import { formatInt, formatMonth, formatPct } from "@/lib/format";

const text = INTELLIGENCE.time;
// A nota de leitura fica abaixo da tabela, depois dos números, no pé do cartão: as dos dois cartões se alinham.
const NOTE = "mt-auto border-t pb-6 text-sm text-pretty text-muted-foreground";
const CHART = "hidden aspect-auto w-full px-6 md:flex";

/** Tempo e resultado: fechadas por faixa de ciclo (as duas últimas terminam nos limites da regra) e o ritmo
 * mensal de entrada e de fechamentos. Os gráficos são decorativos; as tabelas trazem os mesmos números. */
export function TimeResults({ payload }: { payload: Pick<Intelligence, "cycle_bands" | "monthly" | "meta"> }) {
  const config = { engaged: { label: text.chartLabel } } satisfies ChartConfig;
  // Ganhas e perdidas empilhadas por faixa: mostra onde as fechadas perdidas se concentram.
  const bandsConfig = {
    won: { label: text.columns.won, color: "var(--chart-1)" },
    lost: { label: text.columns.lost, color: "var(--chart-2)" },
  } satisfies ChartConfig;
  const bands = payload.cycle_bands.map((b) => ({ ...b, label: text.band(b.low, b.high) }));
  const months = payload.monthly.map((m) => ({ ...m, label: formatMonth(m.month) }));
  return (
    <section aria-labelledby="tempo-titulo" id="tempo" className="flex scroll-mt-24 flex-col gap-4">
      <h2 id="tempo-titulo" className="text-lg font-semibold">{text.title}</h2>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="gap-4 pb-0">
          <CardHeader>
            <CardTitle className="font-semibold">{text.bandsTitle}</CardTitle>
          </CardHeader>
          {/* Lado a lado com o ritmo mensal (mais alto), o gráfico cresce para ocupar a altura que sobra. */}
          <CardContent className="flex flex-1 flex-col gap-4 px-0">
            <ChartContainer config={bandsConfig} className={`${CHART} min-h-72 flex-1`} aria-hidden>
              <BarChart data={bands} margin={{ left: 0, right: 8, top: 4, bottom: 4 }}>
                <XAxis dataKey="label" tickLine={false} axisLine={false} fontSize={11} />
                <YAxis hide />
                <ChartTip render={(value, name) => tipRow(name === "won" ? "var(--chart-1)" : "var(--chart-2)",
                  name === "won" ? text.columns.won : text.columns.lost, formatInt(value))} />
                <Bar dataKey="won" stackId="desfecho" fill="var(--color-won)" isAnimationActive={false} />
                <Bar dataKey="lost" stackId="desfecho" fill="var(--color-lost)" fillOpacity={0.45} radius={[3, 3, 0, 0]}
                     isAnimationActive={false} />
                <ChartLegend content={<ChartLegendContent />} />
              </BarChart>
            </ChartContainer>
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <HelpHead label={text.columns.band} help={text.columnHelp.band} className="pl-6" />
                  <HelpHead label={text.columns.won} help={text.columnHelp.won} className="text-right" />
                  <HelpHead label={text.columns.lost} help={text.columnHelp.lost} className="text-right" />
                  <HelpHead label={text.columns.rate} help={text.columnHelp.rate} className="pr-6 text-right" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {payload.cycle_bands.map((band) => (
                  <TableRow key={band.low}>
                    <TableCell className="pl-6 tabular-nums">{text.band(band.low, band.high)}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatInt(band.won)}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatInt(band.lost)}</TableCell>
                    <TableCell className="pr-6 text-right tabular-nums">
                      {band.win_rate === null ? UI.empty : formatPct(band.win_rate)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
          <CardFooter className={NOTE}>{text.bandsHelp(payload.meta)}</CardFooter>
        </Card>
        <Card className="gap-4 pb-0">
          <CardHeader>
            <CardTitle className="font-semibold">{text.monthlyTitle}</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4 px-0">
            <ChartContainer config={config} className={`${CHART} h-48`} aria-hidden>
              <BarChart data={months} margin={{ left: 0, right: 8, top: 4, bottom: 4 }}>
                <XAxis dataKey="label" tickLine={false} axisLine={false} fontSize={11} interval="preserveStartEnd" />
                <YAxis hide />
                <ChartTip render={(value) => tipRow("var(--chart-1)", text.monthColumns.engaged, formatInt(value))} />
                <Bar dataKey="engaged" fill="var(--chart-1)" radius={3} isAnimationActive={false} />
              </BarChart>
            </ChartContainer>
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <HelpHead label={text.monthColumns.month} help={text.monthHelp.month} className="pl-6" />
                  <HelpHead label={text.monthColumns.engaged} help={text.monthHelp.engaged} className="text-right" />
                  <HelpHead label={text.monthColumns.won} help={text.monthHelp.won} className="text-right" />
                  <HelpHead label={text.monthColumns.lost} help={text.monthHelp.lost} className="pr-6 text-right" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {months.map((m) => (
                  <TableRow key={m.month}>
                    <TableCell className="pl-6">{m.label}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatInt(m.engaged)}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatInt(m.won)}</TableCell>
                    <TableCell className="pr-6 text-right tabular-nums">{formatInt(m.lost)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
          <CardFooter className={NOTE}>{text.monthlyHelp}</CardFooter>
        </Card>
      </div>
    </section>
  );
}
