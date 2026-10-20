"use client";

import {
  ArrowDownWideNarrow, CircleSlash, Layers, PenOff, RefreshCwOff, UsersRound, type LucideIcon,
} from "lucide-react";

import { ErrorAlert } from "@/components/app/error-alert";
import { IconTile } from "@/components/app/icon-tile";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/app/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  AGE_GROUPS, GROUP_LABELS, OUTSIDE_RULER, PAGES, RULES, UI, bandRange, bandTitle, dataLabel,
  groupRange, groupShort,
} from "@/copy/pt-BR";
import { CONCEPT_ICONS, GROUP_VISUAL } from "@/copy/visual";
import { api } from "@/lib/api";
import { useApi } from "@/lib/use-api";
import { cn } from "@/lib/utils";

const FLOW_ICONS: LucideIcon[] = [Layers, CONCEPT_ICONS.listPrice, ArrowDownWideNarrow];
const NOT_USED_ICONS = [CONCEPT_ICONS.seller, CONCEPT_ICONS.account];
const LIMIT_ICONS: LucideIcon[] = [CircleSlash, PenOff, UsersRound, RefreshCwOff];

/** Como a lista é montada: a política que veio de /api/rules, em linguagem de vendedor. */
export function RulesPage() {
  const { data, error, loading } = useApi(() => api.rules(), "rules");
  const meta = data?.meta;
  const ruler = data ? data.ordering.group_order.filter((state) => AGE_GROUPS.includes(state)) : [];

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title={PAGES.comoFunciona.title} description={PAGES.comoFunciona.description} />
      {error && <ErrorAlert message={error} />}
      {loading && <Skeleton className="h-96 w-full rounded-xl" aria-label={UI.loading} />}

      {data && meta && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-semibold">{RULES.groupsTitle}</CardTitle>
              <CardDescription>{RULES.groupsHelp}</CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                {data.ordering.group_order.map((state) => {
                  const visual = GROUP_VISUAL[state];
                  return (
                    <li key={state} className="flex flex-col gap-2 rounded-lg border p-4">
                      <IconTile icon={visual.icon} tone={visual.tile} size="lg" />
                      <h3 className={cn("font-semibold", visual.text)}>{GROUP_LABELS[state]}</h3>
                      <Badge variant="outline" className="tabular-nums">{groupRange(state, meta)}</Badge>
                      <p className="text-sm text-pretty">{groupShort(state, meta)}</p>
                    </li>
                  );
                })}
              </ol>
            </CardContent>
          </Card>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold">{RULES.orderTitle}</CardTitle>
                <CardDescription>{RULES.orderHelp}</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                <ol aria-label={RULES.flowLabel} className="flex flex-col gap-4">
                  {RULES.orderSteps(data.ordering.group_order.map((state) => GROUP_LABELS[state]).join(" → ")).map((step, index) => {
                    const Icon = FLOW_ICONS[index] ?? CONCEPT_ICONS.order;
                    return (
                      <li key={step.title} className="flex items-start gap-3">
                        <IconTile icon={Icon} size="sm" />
                        <div className="flex flex-col gap-0.5">
                          <span className="text-xs font-medium text-muted-foreground">{RULES.stepLabel(index + 1)}</span>
                          <span className="font-medium">{step.title}</span>
                          <span className="text-sm text-pretty text-muted-foreground">{step.body}</span>
                        </div>
                      </li>
                    );
                  })}
                </ol>
              </CardContent>
            </Card>

            <Card className="gap-4 pb-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">{RULES.ageTitle}</CardTitle>
                <CardDescription>{RULES.ageHelpShort}</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                {/* Régua de grupo (só aqui, nunca por oportunidade): três partes iguais, sem largura proporcional. */}
                <div className="flex flex-col gap-1">
                  <ol aria-label={RULES.ageRulerLabel} className="grid grid-cols-3 overflow-hidden rounded-lg">
                    {ruler.map((state) => {
                      const visual = GROUP_VISUAL[state];
                      const Icon = visual.icon;
                      return (
                        <li key={state} className={cn("flex items-center justify-center gap-1.5 px-2 py-2.5 text-sm font-medium",
                          visual.tile)}>
                          <Icon aria-hidden className="size-4 shrink-0" />
                          {GROUP_LABELS[state]}
                        </li>
                      );
                    })}
                  </ol>
                  <div aria-hidden className="grid grid-cols-3 text-xs font-medium text-muted-foreground tabular-nums">
                    <span className="col-start-1 text-right"><span className="inline-block translate-x-1/2">{RULES.ageMark(meta.won_cycle_limit_days)}</span></span>
                    <span className="col-start-2 text-right"><span className="inline-block translate-x-1/2">{RULES.ageMark(meta.cycle_limit_days)}</span></span>
                  </div>
                </div>
                <ul className="flex flex-col gap-2 text-sm">
                  <li>{RULES.wonLimit(meta.won_cycle_limit_days, meta.cycle_percentile)}</li>
                  <li>{RULES.longestLimit(meta.cycle_limit_days)}</li>
                </ul>
                <ul className="flex flex-wrap gap-2">
                  {OUTSIDE_RULER.map(({ state, text }) => {
                    const Icon = GROUP_VISUAL[state].icon;
                    return (
                      <li key={state}>
                        <Badge variant="outline">
                          <Icon data-icon="inline-start" aria-hidden className={GROUP_VISUAL[state].text} />
                          {text}
                        </Badge>
                      </li>
                    );
                  })}
                </ul>
                <h3 className="text-sm font-semibold">{RULES.bandsTitle}</h3>
                <div className="-mx-6">
                  <Table>
                    <TableHeader>
                      <TableRow className="hover:bg-transparent">
                        <TableHead className="pl-6">{RULES.bandsColumns.band}</TableHead>
                        <TableHead className="pr-6 text-right">{RULES.bandsColumns.range}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {data.value_bands.map((rule) => (
                        <TableRow key={rule.band}>
                          <TableCell className="pl-6">
                            <span className="flex items-center gap-2">
                              <CONCEPT_ICONS.listPrice aria-hidden className="size-4 text-muted-foreground" />
                              {bandTitle(rule.band)}
                            </span>
                          </TableCell>
                          <TableCell className="pr-6 text-right tabular-nums">{bandRange(rule)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card id="nao-usa" className="scroll-mt-24">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">{RULES.notUsedTitle}</CardTitle>
              <CardDescription>{RULES.notUsedHelp}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="grid gap-4 md:grid-cols-2">
                {RULES.notUsed.map((item, index) => (
                  <li key={item.title} className="flex items-start gap-3 rounded-xl border bg-muted/40 p-4">
                    <IconTile icon={NOT_USED_ICONS[index] ?? CONCEPT_ICONS.info} size="sm" />
                    <div className="flex flex-col gap-1">
                      <span className="font-medium">{item.title}</span>
                      <span className="text-sm text-pretty text-muted-foreground">{item.body}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-semibold">{RULES.limitsTitle}</CardTitle>
              <CardDescription>{dataLabel(meta)}</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="grid gap-3 text-sm sm:grid-cols-2">
                {RULES.limits.map((limit, index) => (
                  <li key={limit} className="flex items-center gap-3">
                    <IconTile icon={LIMIT_ICONS[index] ?? CONCEPT_ICONS.info} size="sm" />
                    <span className="text-pretty">{limit}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
