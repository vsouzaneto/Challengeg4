"use client";

import { ArrowRight, FlaskConical, TriangleAlert } from "lucide-react";
import Link from "next/link";

import { DeltaValue } from "@/components/app/delta-value";
import { ErrorAlert } from "@/components/app/error-alert";
import { IconTile } from "@/components/app/icon-tile";
import { InfoPopover } from "@/components/app/info-popover";
import { MoreDetails } from "@/components/app/more-details";
import { PageHeader } from "@/components/app/page-header";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  EVIDENCE, EVIDENCE_LANGUAGES, EVIDENCE_TEXT, PAGES, RANKER_LABELS, TECH_COLUMNS, UI, type EvidenceLanguage,
  type EvidenceVerdict, type RankerCode,
} from "@/copy/pt-BR";
import { CONCEPT_ICONS } from "@/copy/visual";
import { api } from "@/lib/api";
import type { Delta, EvidenceDesign, RankerResult } from "@/lib/contract";
import { formatDecimal, formatPct, formatPp } from "@/lib/format";
import { useApi } from "@/lib/use-api";
import { MOBILE_QUERY, useMediaQuery } from "@/lib/use-media-query";
import { useQuery } from "@/lib/use-query";
import { cn } from "@/lib/utils";

import { EvidenceChart, WithoutChart, rankerRowId } from "./evidence-chart";

// As três que respondem à Head de RevOps: a regra servida (a referência que veio da API), a alternativa
// óbvia (só preço) e o acaso.
const headline = (reference: RankerCode): RankerCode[] => [reference, "list_price_only", "random"];
const TABLE_EDGES =
  "[&_td]:py-3.5 [&_th:first-child]:pl-6 [&_td:first-child]:pl-6 [&_th:last-child]:pr-6 [&_td:last-child]:pr-6";
const LANGUAGES = Object.keys(EVIDENCE_LANGUAGES) as EvidenceLanguage[];

function RankerName({ code, reference, description }: { code: RankerCode; reference: string; description?: string }) {
  return (
    <span className="flex flex-col gap-0.5 whitespace-normal">
      <span className="flex items-center gap-2 font-medium">
        {RANKER_LABELS[code]}
        {code === reference && <Badge variant="reference">{EVIDENCE.reference}</Badge>}
      </span>
      {description && <span className="text-xs text-muted-foreground">{description}</span>}
    </span>
  );
}

/** A diferença curta e a faixa embaixo; a frase completa fica para o leitor de tela. Na linguagem técnica os números
 * já são curtos e ficam como estavam. */
function DeltaText({ delta, language }: { delta: Delta; language: EvidenceLanguage }) {
  if (language === "tecnica") {
    return (
      <span className="flex flex-col items-end gap-0.5 tabular-nums">
        <span>{formatPp(delta.value)}</span>
        <span className="text-xs text-muted-foreground">
          {formatPp(delta.low)} a {formatPp(delta.high)}
        </span>
      </span>
    );
  }
  const text = EVIDENCE_TEXT.negocio;
  return <DeltaValue short={text.deltaShort(delta)} range={text.deltaRange(delta)} full={text.delta(delta)} />;
}

/** Valor capturado: o número da API e uma barra fina que só o codifica (decorativa). */
function ValueBar({ value, reference }: { value: number; reference: boolean }) {
  return (
    <span className="flex flex-col items-end gap-1">
      <span className="font-semibold tabular-nums">{formatPct(value)}</span>
      <Progress value={value * 100} tone={reference ? "default" : "neutral"} aria-hidden className="h-1.5 w-20" />
    </span>
  );
}

type TableProps = {
  rankers: RankerResult[];
  reference: string;
  design: EvidenceDesign;
  language: EvidenceLanguage;
  /** A tabela completa leva descrições e, na linguagem técnica, todas as métricas. */
  full: boolean;
  /** Qual das duas tabelas é esta: o gráfico acima rola até a linha certa. */
  scope: "all" | "without";
};

function DeltaHead({ language, k }: { language: EvidenceLanguage; k: number }) {
  const text = EVIDENCE_TEXT[language];
  return (
    <span className="inline-flex items-center gap-0.5">
      {text.columns.delta(k)}
      <InfoPopover label={text.pointsHelpLabel}>{text.pointsHelp}</InfoPopover>
    </span>
  );
}

function RankerTable({ rankers, reference, design, language, full, scope }: TableProps) {
  const text = EVIDENCE_TEXT[language];
  const k = design.top_k;
  const tech = language === "tecnica";
  const cuts = design.cuts.length;
  const count = (value: number | null) => (value === null ? UI.empty : EVIDENCE.outOf(value, cuts));
  return (
    // A primeira e a última coluna têm o mesmo respiro das bordas do cartão, na linguagem de negócio e na técnica.
    <Table className={TABLE_EDGES}>
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          <TableHead className="pl-6">{text.columns.strategy}</TableHead>
          <TableHead className="text-right">{text.columns.value(k)}</TableHead>
          <TableHead className="text-right"><DeltaHead language={language} k={k} /></TableHead>
          {tech && <TableHead className="text-right">{TECH_COLUMNS.hits(k)}</TableHead>}
          {tech && full && <TableHead className="text-right">{TECH_COLUMNS.lift(k)}</TableHead>}
          {tech && full && <TableHead className="text-right">{TECH_COLUMNS.auc}</TableHead>}
          {tech && full && (
            <TableHead className="w-28 text-right whitespace-normal">{TECH_COLUMNS.aucCuts}</TableHead>
          )}
          {tech && full && (
            <TableHead className="w-28 pr-6 text-right whitespace-normal">{TECH_COLUMNS.aboveReference}</TableHead>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rankers.map((ranker) => (
          <TableRow key={ranker.code} id={rankerRowId(ranker.code, scope)} tabIndex={-1}
                    data-state={ranker.code === reference ? "selected" : undefined}
                    className="outline-none focus-visible:bg-accent data-[state=selected]:bg-accent">
            <TableCell className="min-w-56 pl-6">
              <RankerName code={ranker.code} reference={reference}
                          description={full ? text.shortDescriptions[ranker.code] : undefined} />
            </TableCell>
            <TableCell className="text-right">
              <ValueBar value={ranker.val_at_k} reference={ranker.code === reference} />
            </TableCell>
            <TableCell className="text-right">
              {ranker.delta_val ? <DeltaText delta={ranker.delta_val} language={language} />
                : <span className="text-muted-foreground">{UI.empty}</span>}
            </TableCell>
            {tech && <TableCell className="text-right tabular-nums">{formatPct(ranker.p_at_k)}</TableCell>}
            {tech && full && <TableCell className="text-right tabular-nums">{formatDecimal(ranker.lift_at_k)}</TableCell>}
            {tech && full && (
              <TableCell className="text-right tabular-nums">
                {formatDecimal(ranker.auc_mean)}{" "}
                <span className="text-xs text-muted-foreground">
                  ({formatDecimal(ranker.auc_min)}–{formatDecimal(ranker.auc_max)})
                </span>
              </TableCell>
            )}
            {tech && full && <TableCell className="text-right tabular-nums">{count(ranker.cuts_auc_above_chance)}</TableCell>}
            {tech && full && (
              <TableCell className="pr-6 text-right tabular-nums">{count(ranker.cuts_val_above_reference)}</TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/** No celular, a mesma comparação como lista: nome, número e diferença ficam à vista sem rolar para o lado. */
function RankerList({ rankers, reference, design, language, full }: TableProps) {
  const text = EVIDENCE_TEXT[language];
  return (
    <div className="flex flex-col">
      <div className="flex justify-between gap-4 border-b px-4 pb-2 text-xs font-medium text-muted-foreground">
        <span>{text.columns.value(design.top_k)}</span>
        <span className="flex items-center gap-0.5 text-right">
          {text.columns.delta(design.top_k)}
          <InfoPopover label={text.pointsHelpLabel}>{text.pointsHelp}</InfoPopover>
        </span>
      </div>
      <ul className="flex flex-col divide-y">
        {rankers.map((ranker) => (
          <li key={ranker.code} className={cn("flex flex-col gap-1.5 px-4 py-3", ranker.code === reference && "bg-accent")}>
            <RankerName code={ranker.code} reference={reference}
                        description={full ? text.shortDescriptions[ranker.code] : undefined} />
            <div className="flex items-start justify-between gap-4">
              <span className="flex flex-col items-start gap-1">
                <span className="font-semibold tabular-nums">{formatPct(ranker.val_at_k)}</span>
                <Progress value={ranker.val_at_k * 100} tone={ranker.code === reference ? "default" : "neutral"}
                          aria-hidden className="h-1.5 w-20" />
              </span>
              {ranker.delta_val && <DeltaText delta={ranker.delta_val} language={language} />}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Tabela na mesa, lista no celular: só uma das duas fica no DOM. */
function RankerComparison(props: TableProps) {
  const mobile = useMediaQuery(MOBILE_QUERY);
  return mobile ? <RankerList {...props} /> : <RankerTable {...props} />;
}

/** O método em três números do `design`; a frase inteira fica a um clique. */
function MethodLine({ design, language }: { design: EvidenceDesign; language: EvidenceLanguage }) {
  const text = EVIDENCE_TEXT[language];
  const stats = text.methodStats(design);
  const chips = [
    { icon: CONCEPT_ICONS.engaged, label: stats.dates },
    { icon: CONCEPT_ICONS.data, label: stats.opportunities },
    { icon: CONCEPT_ICONS.age, label: stats.horizon },
  ];
  return (
    <div className="flex flex-col gap-1 pt-1">
      <ul className="flex flex-wrap gap-2">
        {chips.map(({ icon: Icon, label }) => (
          <li key={label}>
            <Badge variant="secondary" className="tabular-nums">
              <Icon data-icon="inline-start" aria-hidden />
              {label}
            </Badge>
          </li>
        ))}
      </ul>
      <MoreDetails label={text.methodLabel}>
        <p className="text-sm text-pretty text-muted-foreground">
          {text.method(design.cuts.length, design.cuts[0], design.cuts[design.cuts.length - 1], design.horizon_days)}
        </p>
      </MoreDetails>
    </div>
  );
}

/** A ressalva que muda a leitura, logo abaixo dos números: o veredito curto do back e o atalho para o recorte. */
function VerdictAlert({ verdict, language }: { verdict: EvidenceVerdict; language: EvidenceLanguage }) {
  const text = EVIDENCE_TEXT[language];
  const body = text.verdictBody(verdict);
  return (
    <Alert variant={verdict.code === "reference_behind" ? "warning" : "default"}>
      <TriangleAlert aria-hidden />
      <AlertTitle className="text-pretty">{text.verdictTitle(verdict)}</AlertTitle>
      <AlertDescription className="flex flex-wrap items-baseline gap-x-2">
        {body && <span>{body}</span>}
        <a href="#sem-desfecho" className="font-medium underline underline-offset-3">{text.seeWithout}</a>
      </AlertDescription>
    </Alert>
  );
}

/** Os limites em títulos curtos, junto do número; o texto inteiro está no cartão do fim da página. */
function LimitsStrip({ language }: { language: EvidenceLanguage }) {
  const text = EVIDENCE_TEXT[language];
  return (
    <div className="flex flex-col gap-2 rounded-lg bg-muted/60 px-4 py-3 text-sm">
      <ul className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
        {text.limitsShort.map(({ concept, title }) => {
          const Icon = CONCEPT_ICONS[concept];
          return (
            <li key={title} className="flex items-start gap-2 text-muted-foreground">
              <Icon className="mt-0.5 size-4 shrink-0" aria-hidden />
              {title}
            </li>
          );
        })}
      </ul>
      <a href="#limites" className="w-fit text-xs font-medium text-primary-strong hover:underline">{text.seeLimits}</a>
    </div>
  );
}

/** Um cartão só: de onde vêm os números (com ícone e número) e o que a evidência não mostra (em acordeão). */
function LimitsCard({ design, language }: { design: EvidenceDesign; language: EvidenceLanguage }) {
  const text = EVIDENCE_TEXT[language];
  return (
    <Card id="limites" className="scroll-mt-24">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{text.limitsCardTitle}</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        <section className="flex flex-col gap-3" aria-label={text.howTitle}>
          <h3 className="text-sm font-semibold">{text.howTitle}</h3>
          <ul className="flex flex-col gap-3">
            {text.howStats(design).map(({ concept, value, label }) => (
              <li key={label} className="flex items-center gap-3">
                <IconTile icon={CONCEPT_ICONS[concept]} />
                <span className="flex items-baseline gap-1.5">
                  {value && <span className="text-base font-semibold tabular-nums">{value}</span>}
                  <span className={value ? "text-sm text-muted-foreground" : "text-sm"}>{label}</span>
                </span>
                {value === null && <InfoPopover label={text.howHelpLabel}>{text.howHelp(design)}</InfoPopover>}
              </li>
            ))}
          </ul>
          {language === "tecnica" && (
            <InfoPopover label={text.howHelpLabel} text={text.howHelpLabel} className="w-fit">{text.howHelp(design)}</InfoPopover>
          )}
        </section>
        <section className="flex flex-col gap-1" aria-label={text.limitsTitle}>
          <h3 className="text-sm font-semibold">{text.limitsTitle}</h3>
          <Accordion type="multiple">
            {text.limitsShort.map(({ concept, title }, index) => {
              const Icon = CONCEPT_ICONS[concept];
              return (
                <AccordionItem key={title} value={String(index)}>
                  <AccordionTrigger className="items-center py-3 font-normal">
                    <span className="flex items-center gap-2">
                      <Icon className="size-4 shrink-0 text-muted-foreground" aria-hidden />
                      {title}
                    </span>
                  </AccordionTrigger>
                  <AccordionContent className="pl-6 text-muted-foreground">{text.limits[index]}</AccordionContent>
                </AccordionItem>
              );
            })}
          </Accordion>
        </section>
      </CardContent>
    </Card>
  );
}

export function EvidencePage() {
  const [query, setQuery] = useQuery();
  const language: EvidenceLanguage = query.get("linguagem") === "tecnica" ? "tecnica" : "negocio";
  const text = EVIDENCE_TEXT[language];
  const { data, error, loading } = useApi(() => api.evidence(), "evidence");
  const byCode = new Map(data?.rankers.map((ranker) => [ranker.code, ranker]));
  const design = data?.design;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={PAGES.evidencia.title}
        description={PAGES.evidencia.description}
        actions={
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex flex-col gap-1.5">
              <span className="text-xs font-medium text-muted-foreground">{EVIDENCE.languageLabel}</span>
              <Select value={language}
                      onValueChange={(next) => setQuery({ linguagem: next === "tecnica" ? "tecnica" : null })}>
                <SelectTrigger aria-label={EVIDENCE.languageLabel} className="w-full sm:w-56">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LANGUAGES.map((key) => (
                    <SelectItem key={key} value={key}>{EVIDENCE_LANGUAGES[key]}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button asChild variant="link" className="w-fit px-0 text-primary-strong">
              <Link href="/equipe">
                {EVIDENCE.seeTeam}
                <ArrowRight aria-hidden />
              </Link>
            </Button>
          </div>
        }
      />

      {error && <ErrorAlert message={error} />}
      {loading && <Skeleton className="h-96 w-full rounded-xl" aria-label={UI.loading} />}

      {data && design && (
        <>
          {!design.audited_data && (
            <Alert variant="warning">
              <TriangleAlert aria-hidden />
              <AlertDescription>{EVIDENCE.notAudited}</AlertDescription>
            </Alert>
          )}

          <Card>
            <CardHeader>
              <CardDescription className="flex items-center gap-2 font-medium text-primary-strong">
                <FlaskConical className="size-4" aria-hidden />
                {EVIDENCE.questionLabel}
              </CardDescription>
              <CardTitle className="text-lg leading-7 font-semibold text-pretty">
                {text.question(design.top_k, design.horizon_days)}
              </CardTitle>
              <MethodLine design={design} language={language} />
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-[minmax(0,18rem)_minmax(0,1fr)]">
              <dl className="flex flex-col gap-3">
                {headline(data.reference).map((code) => byCode.get(code)).filter((r): r is RankerResult => Boolean(r)).map((ranker) => {
                  const isReference = ranker.code === data.reference;
                  return (
                    <div key={ranker.code} className={cn("flex flex-col gap-1 rounded-lg border p-4",
                      isReference && "border-transparent bg-accent ring-1 ring-primary/50")}>
                      <dt className="flex items-center gap-2 text-sm text-muted-foreground">
                        {RANKER_LABELS[ranker.code]}
                        {isReference && <Badge variant="reference">{EVIDENCE.reference}</Badge>}
                      </dt>
                      <dd className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                        <span className={cn("font-semibold tabular-nums", isReference ? "text-4xl tracking-tight" : "text-3xl")}>
                          {formatPct(ranker.val_at_k)}
                        </span>
                        <span className="text-xs text-muted-foreground">{text.headline(design.top_k)}</span>
                      </dd>
                      {ranker.delta_val && (
                        <dd>
                          <DeltaValue variant="chip" short={text.deltaShort(ranker.delta_val)} full={text.delta(ranker.delta_val)}
                                      extra={<InfoPopover label={text.rangeLabel}>{text.rangeHelp(ranker.delta_val)}</InfoPopover>} />
                        </dd>
                      )}
                    </div>
                  );
                })}
              </dl>
              <EvidenceChart evidence={data} label={text.chartLabel} className="hidden h-full md:flex" />
            </CardContent>
          </Card>

          <VerdictAlert verdict={data.without_no_outcome_verdict} language={language} />
          <LimitsStrip language={language} />

          <Card className="gap-4 pb-0">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">{text.detailTitle}</CardTitle>
              <CardDescription>{text.detailShort}</CardDescription>
            </CardHeader>
            <CardContent className="px-0">
              <RankerComparison rankers={data.rankers} reference={data.reference} design={design} language={language} full
                                scope="all" />
            </CardContent>
          </Card>

          <Card id="sem-desfecho" className="scroll-mt-24 gap-4 pb-0">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">{text.withoutTitle}</CardTitle>
              <CardDescription>{text.withoutHelp}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4 px-0">
              <WithoutChart evidence={data} className="hidden px-4 sm:px-6 md:flex" />
              <RankerComparison rankers={data.without_no_outcome} reference={data.reference} design={design}
                                language={language} full={false} scope="without" />
              <MoreDetails label={text.whyItMatters} className="px-4 pb-4 sm:px-6">
                <p className="text-sm text-pretty text-muted-foreground">{text.verdict(data.without_no_outcome_verdict)}</p>
              </MoreDetails>
            </CardContent>
          </Card>

          <LimitsCard design={design} language={language} />
        </>
      )}
    </div>
  );
}
