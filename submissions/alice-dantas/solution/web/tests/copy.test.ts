// Catálogo de textos: cobre todos os códigos, só cita números recebidos e respeita o vocabulário.
import { describe, expect, test } from "vitest";

import {
  BRAND, DATA_WARNING, DIMENSION_LABELS, EVIDENCE, EVIDENCE_LANGUAGES, EVIDENCE_TEXT, GROUP_LABELS, INTELLIGENCE,
  METRIC_LABELS, NAV, OUTCOME_LABELS, PAGES, PEOPLE_DRIVERS_NOTE, RANKER_DESCRIPTIONS, RANKER_LABELS, RANKER_SHORT,
  RANKER_TECH_DESCRIPTIONS, ROLE_LABELS, RULES, TECH_COLUMNS, TEAM, UI, accountWarning, actionText, bandRange,
  bandCountText, bandTitle, chanceText, clientText, dataLabel, dealsEmptyText, diagnosticText, driversText, errorText, findingText,
  emptyGroupsText, groupDescription, groupOrderShort, groupRange, groupShort, groupZeroNote, groupEmptyText, historyEmptyText, legendText, metricText, missingShort, pipelineEmptyText,
  CHANCE_LABELS, DRIVER_SHORT, chanceSupport, diagnosticHeadline, diagnosticStepShort, findingHeadline, spreadText,
  ageContextText, reasonText, startAction, startReason, startReasonShort, segmentLabel, sizeLabel, summaryCounts, tieNote, tieText, suggestionText, suggestionsFor, valueLabel,
} from "@/copy/pt-BR";
import { GROUP_VISUAL } from "@/copy/visual";
import type { ChanceTest, Evidence, Intelligence, Meta, RevenueDrivers, Rules } from "@/lib/contract";
import type { Item } from "@/lib/contract";
import {
  formatCompact, formatDate, formatDecimal, formatInt, formatMonth, formatPct, formatPp, formatWhole,
} from "@/lib/format";
import { METRICS } from "@/lib/intelligence";

import { assistedTexts } from "./assisted-texts";
import {
  INTELLIGENCE_DEALS, INTELLIGENCE_PAGES, allPipelines, errors, intelligence, intelligenceDeals, load, readContract,
  sellerPipeline,
} from "./fixtures";

// A lista do núcleo (leadscorer/policy.py, FORBIDDEN_TERMS), exportada como fixture: uma lista só.
const CLOSED_LOST = /^perdidas?$|fechadas perdidas|nas perdidas|ganhas e perdidas/g;
const VOCABULARY = load("vocabulary") as { forbidden_terms: string[]; match: "word_start" };
/** Começo de palavra: "parad" pega "paradas", mas não "comparado" (o \b do JS só conhece ASCII). */
const startsAWord = (term: string) => new RegExp(`(?<![\\p{L}\\p{N}_])${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`, "u");
const BAND_WORD = /\b(alt[oa]|médi[oa]|baix[oa])\b/gi;
const NUMBER = /\d{2}\/\d{2}\/\d{4}|\d{1,3}(?:\.\d{3})+|\d+/g;

const schemas = readContract().components.schemas;
const codeOf = (name: string): string[] => {
  const code = schemas[name].properties.code;
  return code.enum ?? [code.const];
};
const refName = (ref: { $ref: string }) => ref.$ref.split("/").pop() as string;

const CONTRACT = {
  reasons: schemas.Item.properties.reasons.items.oneOf.flatMap((r: { $ref: string }) => codeOf(refName(r))),
  actions: [...codeOf("SimpleAction"), ...codeOf("AccountAction"), ...codeOf("FixFieldAction")],
  empty: [...codeOf("GroupEmpty"), ...codeOf("StartWithGroup"), ...codeOf("PipelineEmpty")],
  errors: schemas.ErrorBody.properties.code.enum as string[],
  groups: schemas.Group.properties.state.enum as string[],
  rankers: schemas.RankerResult.properties.code.enum as string[],
  diagnostics: schemas.Intelligence.properties.diagnostics.items.oneOf.flatMap((r: { $ref: string }) => codeOf(refName(r))),
  findings: schemas.Intelligence.properties.findings.items.oneOf.flatMap((r: { $ref: string }) => codeOf(refName(r))),
  verdicts: schemas.ChanceTest.properties.verdict.enum as string[],
  dimensions: schemas.Breakdown.properties.dimension.enum as string[],
  outcomes: schemas.IntelligenceDeals.properties.outcome.enum as string[],
};

const pages: Intelligence[] = INTELLIGENCE_PAGES.map(intelligence);

/** Os textos da Inteligência montados a partir dos códigos e params de uma resposta. */
const headlineTexts = (h: { metrics: { value: string; label: string }[]; chips?: string[] }): string[] =>
  [...h.metrics.flatMap((m) => [m.value, m.label]), ...(h.chips ?? [])];

function intelligenceTexts(page: Intelligence): string[] {
  const texts: string[] = [INTELLIGENCE.dataLabel(page.meta)];
  for (const d of page.diagnostics) {
    texts.push(...Object.values(diagnosticText(d)), diagnosticStepShort(d), ...headlineTexts(diagnosticHeadline(d)));
  }
  for (const f of page.findings) {
    const { title, body } = findingText(f);
    texts.push(title, body, ...headlineTexts(findingHeadline(f)));
  }
  texts.push(...Object.values(CHANCE_LABELS), ...Object.values(DRIVER_SHORT));
  for (const b of page.breakdowns) {
    texts.push(chanceSupport(b.dimension, b.chance), ...(b.drivers ? [spreadText(b.dimension, b.drivers)] : []));
    texts.push(chanceText(b.dimension, b.chance), ...(b.drivers ? [driversText(b.dimension, b.drivers)] : []),
      ...b.segments.map((seg) => segmentLabel(b.dimension, seg.key, page.options.sizes)),
      ...METRICS.map((m) => metricText(m, null)));
  }
  texts.push(...page.options.sizes.map((band) => sizeLabel(band, page.options.sizes)));
  const { history, open } = page;
  texts.push(INTELLIGENCE.kpis.revenueShort(history.revenue),
    ...(history.median_lost_cycle_days === null ? [] : [INTELLIGENCE.kpis.lostCycleShort(history.median_lost_cycle_days)]),
    ...(history.win_rate ? [INTELLIGENCE.kpis.winRateChip(history.win_rate.low, history.win_rate.high)] : []),
    INTELLIGENCE.open.titleCount(open.summary.total));
  texts.push(INTELLIGENCE.kpis.revenueHelp(history.revenue), INTELLIGENCE.kpis.wonOf(history.closed),
    INTELLIGENCE.open.count(open.summary.total), INTELLIGENCE.open.listValue(open.list_value));
  if (history.win_rate) texts.push(INTELLIGENCE.kpis.winRateRange(history.win_rate.low, history.win_rate.high));
  if (history.median_won_cycle_days !== null) texts.push(INTELLIGENCE.kpis.days(history.median_won_cycle_days));
  if (history.median_lost_cycle_days !== null) texts.push(INTELLIGENCE.kpis.lostCycle(history.median_lost_cycle_days));
  if (open.excluded_without_account) texts.push(INTELLIGENCE.open.excluded(open.excluded_without_account));
  if (page.history_empty) texts.push(historyEmptyText(page.history_empty));
  texts.push(INTELLIGENCE.time.bandsHelp(page.meta), ...page.cycle_bands.map((b) => INTELLIGENCE.time.band(b.low, b.high)),
    ...page.monthly.map((m) => formatMonth(m.month)));
  for (const row of page.matrix.rows) {
    texts.push(...row.cells.map((c) => INTELLIGENCE.matrix.cell(c.closed, c.mix_share)),
      ...row.cells.map((c) => INTELLIGENCE.matrix.cellLabel(row.seller, c.product)));
  }
  for (const table of page.crosstabs) {
    for (const row of table.rows) {
      texts.push(...row.cells.map((c) => INTELLIGENCE.crosstab.cell(c.closed, c.share)),
        ...row.cells.map((c) => INTELLIGENCE.crosstab.cellLabel(row.key, c.key)));
    }
    texts.push(...table.columns.map((column) => INTELLIGENCE.crosstab.columnHelp(column)));
  }
  return texts;
}

const pipelines = allPipelines();
const items = (): Item[] => pipelines.flatMap((p) => p.groups.flatMap((g) => g.items));

/** Todos os textos fixos de um catálogo (objetos aninhados inclusive). */
const strings = (value: unknown): string[] =>
  typeof value === "string" ? [value] : value && typeof value === "object" ? Object.values(value).flatMap(strings) : [];

/** Todo texto que a tela monta a partir das fixtures. */
function renderedTexts(): string[] {
  const texts: string[] = [...strings([GROUP_LABELS, BRAND, NAV, PAGES, ROLE_LABELS, UI, TEAM, RANKER_LABELS,
    RANKER_DESCRIPTIONS, RANKER_SHORT, RANKER_TECH_DESCRIPTIONS, EVIDENCE, EVIDENCE_LANGUAGES, EVIDENCE_TEXT, TECH_COLUMNS, RULES,
    INTELLIGENCE, DIMENSION_LABELS, METRIC_LABELS, OUTCOME_LABELS]), DATA_WARNING, PEOPLE_DRIVERS_NOTE,
    ...assistedTexts()];
  for (const page of pages) texts.push(...intelligenceTexts(page));
  for (const name of INTELLIGENCE_DEALS) {
    const deals = intelligenceDeals(name);
    texts.push(INTELLIGENCE.deals.total(deals.total), ...(deals.empty ? [dealsEmptyText(deals.empty)] : []));
  }
  texts.push(dealsEmptyText({ code: "no_deals_for_filter", params: {} }), INTELLIGENCE.deals.scope([]),
    INTELLIGENCE.deals.scope([INTELLIGENCE.deals.filterPart(DIMENSION_LABELS.product, "GTX Pro"),
      INTELLIGENCE.deals.groupPart(GROUP_LABELS.revisar)]), INTELLIGENCE.findings.seeBy("account"),
    INTELLIGENCE.explore.filterBy("GTX Pro"), INTELLIGENCE.explore.dealsOf("GTX Pro"),
    INTELLIGENCE.explore.rateRange(0.62, 0.643), INTELLIGENCE.explore.productsOf(6, 7),
    INTELLIGENCE.deals.seePortfolio("Ana Alfa"), INTELLIGENCE.filters.chip(DIMENSION_LABELS.sector, "retail"),
    INTELLIGENCE.filters.remove(DIMENSION_LABELS.sector, "retail"));
  const evidence = load("evidence") as Evidence;
  const rules = load("rules") as Rules;
  const { design } = evidence;
  for (const text of Object.values(EVIDENCE_TEXT)) {
    texts.push(text.question(design.top_k, design.horizon_days), text.headline(design.top_k),
      text.columns.value(design.top_k), text.columns.delta(design.top_k), text.how(design),
      text.method(design.cuts.length, design.cuts[0], design.cuts[design.cuts.length - 1], design.horizon_days),
      ...Object.values(text.methodStats(design)),
      ...[...evidence.rankers, ...evidence.without_no_outcome].flatMap((r) => (r.delta_val ? [text.delta(r.delta_val),
        text.deltaShort(r.delta_val), text.deltaRange(r.delta_val), text.rangeHelp(r.delta_val)] : [])));
  }
  for (const text of Object.values(EVIDENCE_TEXT)) {
    const verdicts = [evidence.without_no_outcome_verdict,
      { code: "reference_ahead", ranker: "list_price_only", delta: { value: -0.012, low: -0.02, high: -0.004 } },
      { code: "inconclusive", ranker: null, delta: null }] as Evidence["without_no_outcome_verdict"][];
    for (const verdict of verdicts) {
      texts.push(text.verdict(verdict), text.verdictTitle(verdict), ...(text.verdictBody(verdict) ? [text.verdictBody(verdict)!] : []));
    }
    texts.push(text.howHelp(design), ...text.howStats(design).flatMap((stat) => [stat.label, ...(stat.value ? [stat.value] : [])]));
  }
  texts.push(TECH_COLUMNS.hits(design.top_k), TECH_COLUMNS.lift(design.top_k), EVIDENCE.outOf(6, 7),
    RULES.wonLimit(rules.meta.won_cycle_limit_days, rules.meta.cycle_percentile),
    RULES.longestLimit(rules.meta.cycle_limit_days), ...rules.value_bands.map(bandRange),
    ...rules.value_bands.map((b) => bandTitle(b.band)));
  texts.push(groupZeroNote("focar", 0, rules.meta)!, UI.seeGroup(GROUP_LABELS.revisar), UI.moreInTab(3, GROUP_LABELS.focar), UI.whyHereFor("EPP"),
    UI.closeAnalysis, UI.chartClickHint, UI.sort.next(null), UI.sort.next("asc"), UI.sort.next("desc"),
    UI.ageDays(10), UI.ofTotal(2089), UI.pagination.page(2), UI.pagination.range(26, 50, 1291),
    UI.startWithTie(tieText(3, "GTX Plus Pro", 5482)), UI.tieChip(13, "GTX Plus Pro", 5482),
    ...Object.values(GROUP_LABELS).map(UI.startHeadline));
  for (const p of pipelines) {
    texts.push(legendText(p.ordering), dataLabel(p.meta), accountWarning(p.summary.without_account, p.summary.total));
    texts.push(...p.groups.map((g) => groupDescription(g.state, p.meta)), groupOrderShort(p.ordering),
      ...p.groups.flatMap((g) => [groupShort(g.state, p.meta), groupRange(g.state, p.meta)]));
    if (p.empty) texts.push(pipelineEmptyText(p.empty));
    for (const g of p.groups) {
      if (g.empty) texts.push(groupEmptyText(g.empty));
      if (g.empty?.code === "start_with_group") {
        texts.push(startReason(g.empty), startAction(g.empty), startReasonShort(g.empty, g.state));
      }
      if (g.next_action) texts.push(actionText(g.next_action));
    }
  }
  for (const p of pipelines) {
    for (const item of p.groups.flatMap((g) => g.items)) {
      texts.push(...item.reasons.map(reasonText), actionText(item.next_action, item.account), clientText(item),
        bandTitle(item.value_band));
      if (item.missing_field) texts.push(missingShort(item.missing_field));
      if (item.product && item.sales_price !== null) texts.push(tieText(item.tie_size, item.product, item.sales_price));
      texts.push(...suggestionsFor(item).map(suggestionText));
      const note = tieNote(item);
      if (note) texts.push(note);
      if (item.age_days !== null) texts.push(ageContextText(item.age_days, p.meta));
    }
  }
  texts.push(...Object.values(errors()).map(errorText));
  return texts;
}

describe("título de faixa", () => {
  test("o total da faixa; se a página mostra só parte dela, quantas mostra", () => {
    expect(bandCountText(9, 9)).toBe("9");
    expect(bandCountText(8, 9)).toBe("8 de 9 nesta página");
    expect(bandCountText(1, 1200)).toBe("1 de 1.200 nesta página");
  });
});

describe("cobertura: todo código do contrato tem texto", () => {
  const seen = {
    reasons: new Set(items().flatMap((i) => i.reasons.map((r) => r.code))),
    actions: new Set([...items().map((i) => i.next_action.code),
      ...pipelines.flatMap((p) => p.groups.flatMap((g) => (g.next_action ? [g.next_action.code] : [])))]),
    empty: new Set(pipelines.flatMap((p) => [
      ...(p.empty ? [p.empty.code] : []), ...p.groups.flatMap((g) => (g.empty ? [g.empty.code] : []))])),
  };

  test.each(["reasons", "actions", "empty"] as const)("%s: as fixtures exercitam todos os códigos", (kind) => {
    expect([...seen[kind]].sort()).toEqual([...CONTRACT[kind]].sort());
  });
  test("grupos", () => {
    expect(Object.keys(GROUP_LABELS).sort()).toEqual([...CONTRACT.groups].sort());
    // Ícone e cor de apresentação para todo grupo do contrato; a cor de gráfico é sempre um token de preenchimento.
    expect(Object.keys(GROUP_VISUAL).sort()).toEqual([...CONTRACT.groups].sort());
    for (const [state, visual] of Object.entries(GROUP_VISUAL)) {
      expect(visual.fill).toBe(`var(--status-${state.replace("_", "-")}-fill)`);
      expect(new Set(Object.values(GROUP_VISUAL).map((v) => v.icon)).size).toBe(CONTRACT.groups.length);
    }
  });
  test("estratégias do backtest: rótulo e descrição para cada código", () => {
    expect(Object.keys(RANKER_LABELS).sort()).toEqual([...CONTRACT.rankers].sort());
    expect(Object.keys(RANKER_DESCRIPTIONS).sort()).toEqual([...CONTRACT.rankers].sort());
    expect(Object.keys(RANKER_SHORT).sort()).toEqual([...CONTRACT.rankers].sort());
    // A descrição curta cabe na coluna: até 8 palavras.
    for (const text of Object.values(RANKER_SHORT)) expect(text.split(/\s+/).length, text).toBeLessThanOrEqual(8);
    expect(Object.keys(RANKER_TECH_DESCRIPTIONS).sort()).toEqual([...CONTRACT.rankers].sort());
    expect((load("evidence") as Evidence).rankers.map((r) => r.code).sort()).toEqual([...CONTRACT.rankers].sort());
  });
  test("inteligência: a base rica dispara todo diagnóstico e descoberta, e todos têm texto", () => {
    const rich = intelligence("intelligence-rich");
    expect([...new Set(rich.diagnostics.map((d) => d.code))].sort()).toEqual([...CONTRACT.diagnostics].sort());
    expect([...new Set(rich.findings.map((f) => f.code))].sort()).toEqual([...CONTRACT.findings].sort());
    expect(Object.keys(DIMENSION_LABELS).sort()).toEqual([...CONTRACT.dimensions].sort());
    expect(Object.keys(OUTCOME_LABELS).sort()).toEqual([...CONTRACT.outcomes].sort());
    const chance = rich.breakdowns[0].chance;
    for (const verdict of CONTRACT.verdicts) {
      expect(chanceText("product", { ...chance, verdict: verdict as ChanceTest["verdict"] })).not.toBe("");
    }
  });
  test.each(CONTRACT.errors)("erro %s", (code) => {
    expect(errorText({ detail: "", code: code as never, params: {} })).not.toBe("");
  });
  test("nenhum texto sai com valor faltando", () => {
    for (const text of renderedTexts()) expect(text).not.toMatch(/undefined|null|NaN|\[object/);
  });
  test("nenhum texto usa ponto e vírgula: a frase termina em ponto, ou usa \"mas\" para a condição", () => {
    for (const text of renderedTexts()) expect(text, text).not.toContain(";");
  });
});

test("vocabulário: nenhum termo proibido; faixa sempre como valor de tabela", () => {
  expect(VOCABULARY.match).toBe("word_start");
  for (const text of renderedTexts()) {
    const lowered = text.toLowerCase();
    // "Perdida" só como o resultado factual de uma negociação já fechada sem venda (nunca para uma aberta): o rótulo
    // sozinho, "fechadas perdidas", "nas perdidas" ou "ganhas e perdidas". Fora dessas formas, a palavra segue proibida.
    const checked = lowered.replace(CLOSED_LOST, "");
    for (const term of VOCABULARY.forbidden_terms) expect(checked, `${term} em "${text}"`).not.toMatch(startsAWord(term));
    for (const match of text.matchAll(BAND_WORD)) {
      expect(lowered.slice(0, match.index).endsWith("de tabela "), text).toBe(true);
    }
  }
});

test("vocabulário por começo de palavra, como no núcleo", () => {
  const hits = (text: string) => VOCABULARY.forbidden_terms.some((term) => startsAWord(term).test(text.toLowerCase()));
  expect(hits("Comparado à regra atual, separadas por grupo.")).toBe(false);
  expect(hits("A negociação aberta está perdida".replace(CLOSED_LOST, ""))).toBe(true);
  expect(hits("As fechadas perdidas".replace(CLOSED_LOST, ""))).toBe(false);
  for (const text of ["Negociação parada", "prazo de 106 dias", "Venceu ontem", "Atrasadas", "chance zero", "inativa"]) {
    expect(hits(text), text).toBe(true);
  }
});

test("todo número de uma frase de grupo vem do meta", () => {
  for (const p of pipelines) {
    const allowed = new Set([p.meta.won_cycle_limit_days, p.meta.cycle_limit_days, p.meta.cycle_percentile].map(String));
    for (const g of p.groups) {
      for (const text of [groupDescription(g.state, p.meta), groupShort(g.state, p.meta), groupRange(g.state, p.meta)]) {
        for (const number of text.match(NUMBER) ?? []) expect(allowed, text).toContain(number);
      }
    }
  }
});

test("todo número de um motivo vem dos parâmetros do código", () => {
  for (const item of items()) {
    for (const reason of item.reasons) {
      let text = reasonText(reason);
      const allowed = new Set<string>();
      for (const value of Object.values(reason.params as Record<string, unknown>)) {
        if (typeof value === "number") allowed.add(String(value)).add(formatInt(value));
        if (typeof value === "string") {
          if (/^\d{4}-\d{2}-\d{2}$/.test(value)) allowed.add(formatDate(value));
          else text = text.replaceAll(value, " "); // números dentro de um nome (ex.: "GTK 500")
        }
      }
      for (const number of text.match(NUMBER) ?? []) expect(allowed, `${number} em "${text}"`).toContain(number);
    }
  }
});

/** Toda forma escrita de um valor dos params (números, meses, nomes), da maior para a menor. */
function writtenForms(params: unknown): string[] {
  const forms = new Set<string>();
  const visit = (value: unknown) => {
    if (typeof value === "number") {
      for (const form of [String(value), formatInt(value), formatPct(value), formatDecimal(value, 1),
        formatWhole(value), formatCompact(value)]) forms.add(form);
    } else if (typeof value === "string") {
      forms.add(/^\d{4}-\d{2}$/.test(value) ? formatMonth(value) : value);
    } else if (value && typeof value === "object") {
      Object.values(value).forEach(visit);
    }
  };
  visit(params);
  return [...forms].sort((a, b) => b.length - a.length);
}

const withoutForms = (text: string, params: unknown) =>
  writtenForms(params).reduce((rest, form) => rest.replaceAll(form, " "), text);

test("inteligência: todo número de diagnóstico, descoberta, acaso e decomposição vem dos params", () => {
  for (const page of pages) {
    for (const d of page.diagnostics) {
      for (const line of [...Object.values(diagnosticText(d)), diagnosticStepShort(d), ...headlineTexts(diagnosticHeadline(d))]) {
        expect(withoutForms(line, d.params), line).not.toMatch(/\d/);
      }
    }
    for (const f of page.findings) {
      const { title, body } = findingText(f);
      expect(withoutForms(`${title} ${body}`, f.params), body).not.toMatch(/\d/);
      for (const line of headlineTexts(findingHeadline(f))) expect(withoutForms(line, f.params), line).not.toMatch(/\d/);
    }
    for (const b of page.breakdowns) {
      expect(withoutForms(chanceText(b.dimension, b.chance), b.chance)).not.toMatch(/\d/);
      expect(withoutForms(chanceSupport(b.dimension, b.chance), b.chance)).not.toMatch(/\d/);
      if (b.drivers) expect(withoutForms(driversText(b.dimension, b.drivers), b.drivers)).not.toMatch(/\d/);
      if (b.drivers) expect(withoutForms(spreadText(b.dimension, b.drivers), b.drivers)).not.toMatch(/\d/);
    }
  }
});

test("inteligência sem jargão estatístico nem promessa de chance", () => {
  const texts = [...pages.flatMap(intelligenceTexts), ...strings(INTELLIGENCE)];
  for (const text of texts) {
    expect(text, text).not.toMatch(/\bpp\b|IC95%|\bIC\b|qui-quadrado|Bonferroni|Wilson|p-valor|\bp =|AUC|score/i);
    expect(text, text).not.toMatch(/margem de erro|faixa provável|dentro do acaso|ticket|\bmix\b/i);
  }
});

// Textos de referência: a redação é desta camada; mudar uma frase é uma decisão
// explícita, que aparece aqui. Valores das fixtures sintéticas.
function itemOf(fixture: string, id: string): Item {
  const item = sellerPipeline(fixture).groups.flatMap((g) => g.items).find((i) => i.opportunity_id === id);
  if (!item) throw new Error(`${id} não está em ${fixture}`);
  return item;
}

describe("textos de referência", () => {
  test("motivos e próximo passo dos três grupos de idade", () => {
    const epp = itemOf("pipeline-ana-alfa", "EPP");
    expect(epp.reasons.map(reasonText)).toEqual([
      "Focar porque está aberta há 10 dias. Entre as vendas ganhas, 90% fecharam em até 100 dias.",
      "Valor de tabela 5.482 (valor de tabela alto): preço de catálogo do GTX Plus Pro, não valor negociado.",
    ]);
    // Sem conta registrada: a verificação cita o andamento e a conta, não uma ação comercial.
    expect(actionText(epp.next_action, epp.account)).toBe("Consulte no CRM o andamento e a conta desta negociação.");
    expect(actionText({ code: "check_status", params: { has_account: true } }, "Initech")).toBe(
      "Consulte no CRM o andamento da negociação com Initech.");
    expect(actionText({ code: "check_status", params: { has_account: null } })).toBe(
      "Consulte no CRM o andamento de cada negociação.");
    const e138 = itemOf("pipeline-ana-alfa", "E138");
    expect(reasonText(e138.reasons[0])).toBe("Acompanhar porque está aberta há 138 dias: mais do que 90% das " +
      "vendas ganhas levaram (100 d), sem passar da venda mais longa já fechada (138 d).");
    expect(actionText(e138.next_action, e138.account)).toBe(
      "Consulte no CRM o último registro e a conta desta negociação.");
    const e139 = itemOf("pipeline-ana-alfa", "E139");
    expect(reasonText(e139.reasons[0])).toBe(
      "Confirmar porque está aberta há 139 dias, mais do que qualquer venda já fechada aqui (138 d).");
    expect(actionText(e139.next_action, e139.account)).toBe(
      "Verifique no CRM se a negociação com Acme continua: o tempo aberta não prova que ela terminou.");
    expect(UI.limitsNote).toBe(
      "Como o pipeline só apresenta datas, produto e preço de tabela: não apresenta último contato, ligações, " +
        "reuniões nem e-mails. A base não registra atividades, estágio nem contatos. Por isso o Rankio indica " +
        "possibilidades para diferentes cenários de negociação, mas não uma certeza de próximo passo.");
  });

  test("Qualificar e Completar", () => {
    const p1 = itemOf("pipeline-edges-bruno-beta", "P1");
    expect(p1.reasons.map(reasonText)).toEqual([
      "Qualificar porque ainda está em prospecção.", "Valor de tabela 4.821 (valor de tabela alto): preço de " +
        "catálogo do GTX Pro, não valor negociado."]);
    const n1 = itemOf("pipeline-edges-bruno-beta", "N1");
    expect([reasonText(n1.reasons[0]), actionText(n1.next_action), missingShort(n1.missing_field!)]).toEqual([
      "Completar porque falta a data de engajamento.", "Corrija a data de engajamento no CRM.",
      "sem data de engajamento"]);
    const n2 = itemOf("pipeline-edges-bruno-beta", "N2");
    expect(reasonText(n2.reasons[1])).toBe("Sem valor de tabela: a oportunidade não tem produto.");
    expect(reasonText(itemOf("pipeline-edges-bruno-beta", "U1").reasons[1])).toBe(
      "Sem valor de tabela: o GTX Ultra não tem preço no catálogo.");
  });

  test("carteira, grupos vazios e avisos", () => {
    const ana = sellerPipeline("pipeline-ana-alfa");
    expect(legendText(ana.ordering)).toBe("Ordem: Focar → Qualificar → Acompanhar → Confirmar → Completar. Em cada " +
      "grupo, maior valor de tabela primeiro. A idade aparece, mas não muda a ordem.");
    expect(dataLabel(ana.meta)).toBe("Dados até 31/12/2017");
    expect(accountWarning(ana.summary.without_account, ana.summary.total)).toBe("5 de 8 sem cliente registrado");
    expect(summaryCounts(ana)).toBe("5 Focar + 2 Acompanhar + 1 Confirmar");
    expect(emptyGroupsText(ana)).toBe("Sem oportunidades em Qualificar e Completar.");
    // Focar vazio: o texto cita só o limite que importa para o grupo indicado.
    expect(groupEmptyText(sellerPipeline("pipeline-bruno-beta").groups[0].empty!)).toBe(
      "Nenhuma negociação em andamento. Comece por Qualificar: verifique no CRM se já houve engajamento e registre a " +
        "data.");
    const davi = sellerPipeline("pipeline-edges-davi-delta").groups[0];
    if (davi.empty?.code === "start_with_group") {
      expect([startReasonShort(davi.empty, davi.state), startAction(davi.empty)]).toEqual([
        "Focar vazio: nenhuma aberta há até 100 dias.", "Consulte no CRM o último registro de cada uma."]);
    }
    expect(groupEmptyText(sellerPipeline("pipeline-edges-davi-delta").groups[0].empty!)).toBe(
      "Nenhuma aberta há até 100 dias. Comece por Acompanhar: consulte no CRM o último registro de cada uma.");
    expect(groupEmptyText(sellerPipeline("pipeline-edges-eva-epsilon").groups[0].empty!)).toBe(
      "Todas as negociações em andamento estão abertas há mais de 138 dias. Comece por Confirmar: verifique no CRM " +
        "quais seguem ativas.");
    expect(pipelineEmptyText(sellerPipeline("pipeline-carla-gama").empty!)).toBe(
      "Nenhuma oportunidade aberta para este vendedor. A base não registra nenhuma aberta no nome dele. Se isso não era " +
        "esperado, confira o cadastro no CRM.");
    expect(clientText(itemOf("pipeline-ana-alfa", "E138"))).toBe("sem cliente registrado");
    expect(valueLabel("médio")).toBe("valor de tabela médio");
  });

  test("definição dos grupos, papéis dos motivos e cartão de próximo passo", () => {
    const meta: Meta = sellerPipeline("pipeline-ana-alfa").meta;
    expect((["focar", "acompanhar", "revisar", "qualificar", "nao_pontuavel"] as const)
      .map((g) => groupDescription(g, meta))).toEqual([
      "Abertas há até 100 dias. No histórico, 90% das vendas ganhas fecharam dentro desse tempo. É sobre o tempo " +
        "aberta, não sobre a chance de fechar.",
      "Abertas há mais de 100 e até 138 dias: mais do que 90% das vendas ganhas levaram, sem passar da venda mais " +
        "longa já fechada.",
      "Para verificar se a negociação continua: abertas há mais de 138 dias, mais do que qualquer venda já fechada " +
        "aqui. Confirmar é limpar a carteira, não prever venda: o sistema não vê ligações nem reuniões.",
      "Ainda em prospecção, sem data de início da negociação.",
      "Falta produto, preço de tabela ou data de engajamento no CRM.",
    ]);
    expect(ROLE_LABELS).toEqual({ group: "Por que está neste grupo", order: "Por que nesta posição" });
    expect(UI.tieChip(13, "GTX Plus Pro", 5482)).toBe("13 empatadas · GTX Plus Pro · 5.482");
    expect(UI.startWithTie(tieText(3, "GTX Plus Pro", 5482))).toBe(
      "Comece por qualquer uma destas 3 oportunidades empatadas (GTX Plus Pro, 5.482):");
    expect([UI.ofTotal(2089), UI.pagination.range(26, 50, 1291)]).toEqual(["de 2.089 abertas", "26–50 de 1.291"]);
    expect([RULES.wonLimit(106, 90), RULES.longestLimit(138)]).toEqual([
      "90% das vendas ganhas fecharam em até 106 dias. Até esse tempo, a negociação fica em Focar.",
      "A venda mais longa já fechada levou 138 dias. Entre os dois limites, a negociação fica em Acompanhar. Acima, " +
        "em Confirmar."]);
  });

  test("evidência e regras: frações em porcentagem, diferenças em pontos e faixas em palavras", () => {
    expect([formatPct(0.569), formatPct(0.14), formatPct(1)]).toEqual(["56,9%", "14,0%", "100,0%"]);
    expect([formatPp(-0.031), formatPp(0.015), formatPp(0), formatPp(-0.0004)]).toEqual(
      ["−3,1 pp", "+1,5 pp", "0,0 pp", "0,0 pp"]);
    const bands = (load("rules") as Rules).value_bands;
    expect(bands.map((b) => `${bandTitle(b.band)}: ${bandRange(b)}`)).toEqual([
      "Valor de tabela alto: a partir de 3.000", "Valor de tabela médio: 500 a 2.999", "Valor de tabela baixo: até 499"]);
  });

  test("evidência em linguagem de negócio: pontos em palavras, sem jargão", () => {
    const { negocio, tecnica } = EVIDENCE_TEXT;
    expect(negocio.question(10, 90)).toBe("Quanto do valor vendido em 90 dias estava nas 10 primeiras?");
    // Número primeiro, palavra depois: a diferença curta com sinal, a faixa curta e a faixa em frase (popover).
    const behindRef = { value: -0.327, low: -0.368, high: -0.287 };
    expect([negocio.deltaShort(behindRef), negocio.deltaRange(behindRef)]).toEqual(["−32,7 pontos", "entre −36,8 e −28,7"]);
    expect(negocio.deltaShort({ value: 0.01, low: 0.003, high: 0.019 })).toBe("+1,0 ponto");
    expect(negocio.deltaShort({ value: 0, low: -0.001, high: 0.002 })).toBe("Igual");
    expect(negocio.rangeHelp({ value: -0.046, low: -0.068, high: -0.025 })).toBe(
      "A diferença real deve ficar entre 2,5 e 6,8 pontos a menos.");
    expect([tecnica.deltaShort(behindRef), tecnica.deltaRange(behindRef)]).toEqual(["−32,7 pp", "−36,8 pp a −28,7 pp"]);
    expect(negocio.delta({ value: -0.046, low: -0.068, high: -0.025 })).toBe(
      "4,6 pontos a menos que a regra atual (a diferença real deve ficar entre 2,5 e 6,8 pontos a menos)");
    expect(negocio.delta({ value: 0.015, low: 0.002, high: 0.027 })).toBe(
      "1,5 ponto a mais que a regra atual (a diferença real deve ficar entre 0,2 e 2,7 pontos a mais)");
    expect(negocio.delta({ value: 0.004, low: -0.008, high: 0.016 })).toBe(
      "0,4 ponto a mais que a regra atual (a diferença real deve ficar entre 0,8 a menos e 1,6 a mais)");
    expect(negocio.delta({ value: 0, low: 0, high: 0 })).toBe("Igual à regra atual");
    expect(tecnica.delta({ value: -0.046, low: -0.068, high: -0.025 })).toBe(
      "Δ −4,6 pp contra a regra atual (IC95%: −6,8 pp a −2,5 pp)");
    // A limitação principal, dita a partir do veredito que o back calculou (os números reais de hoje).
    const behind = { code: "reference_behind", ranker: "list_price_only",
      delta: { value: 0.01, low: 0.003, high: 0.019 } } as const;
    expect(negocio.verdict(behind)).toBe("Sem elas, \"Só valor de tabela\" rende 1,0 ponto a mais que a regra atual " +
      "(a diferença real deve ficar entre 0,3 e 1,9 pontos a mais). A vantagem da regra atual vem dessas negociações, e elas podem " +
      "ser um efeito de como a base foi montada.");
    expect(tecnica.verdict(behind)).toBe("\"Só valor de tabela\": Δ +1,0 pp (IC95%: +0,3 pp a +1,9 pp) contra a regra " +
      "servida. A vantagem da regra servida depende das negociações sem desfecho.");
    // O veredito curto do alerta, para os três códigos; a frase inteira continua no detalhe.
    expect([negocio.verdictTitle(behind), negocio.verdictBody(behind)]).toEqual([
      "Sem as que nunca fecharam, \"Só valor de tabela\" fica 1,0 ponto à frente.",
      "A vantagem da regra atual vem dessas negociações."]);
    const ahead = { code: "reference_ahead", ranker: "list_price_only", delta: { value: -0.012, low: -0.02, high: -0.004 } } as const;
    expect([negocio.verdictTitle(ahead), negocio.verdictBody(ahead)]).toEqual([
      "Mesmo sem as que nunca fecharam, a regra atual fica à frente.", "A mais próxima é \"Só valor de tabela\": −1,2 ponto."]);
    const inconclusive = { code: "inconclusive", ranker: null, delta: null } as const;
    expect([negocio.verdictTitle(inconclusive), negocio.verdictBody(inconclusive)]).toEqual([
      "Sem as que nunca fecharam, a diferença é pequena demais para ser confiável.", null]);
    expect(negocio.limitsShort).toHaveLength(negocio.limits.length);
    expect(tecnica.limitsShort).toHaveLength(tecnica.limits.length);
    expect(negocio.verdict({ code: "inconclusive", ranker: null, delta: null })).toBe(
      "Sem elas, a diferença entre a regra atual e as outras é pequena demais para ser confiável.");
    // A linguagem de negócio não usa siglas nem jargão estatístico.
    const business = [...strings(negocio), ...Object.values(RANKER_DESCRIPTIONS), ...Object.values(RANKER_SHORT),
      negocio.deltaShort(behindRef), negocio.deltaRange(behindRef), negocio.rangeHelp(behindRef), negocio.question(10, 90),
      negocio.verdictTitle(behind), negocio.verdictBody(behind)!, negocio.verdictTitle(ahead), negocio.verdictBody(ahead)!,
      negocio.headline(10), negocio.columns.value(10), negocio.columns.delta(10), negocio.verdict(behind)];
    for (const line of business) expect(line, line).not.toMatch(/\bpp\b|IC95%|AUC|Val@|P@|Lift|bootstrap|oráculo|margem de erro|acaso|ticket|\bmix\b/i);
  });
});

describe("textos de referência da inteligência", () => {
  test("números grandes, meses e métricas", () => {
    expect(formatCompact(10005534).replace(/\s/g, " ")).toBe("10,01 mi");
    expect(formatCompact(950000).replace(/\s/g, " ")).toBe("950 mil");
    expect([formatMonth("2017-11"), formatWhole(2360.91)]).toEqual(["nov/2017", "2.361"]);
    expect([metricText("win_rate", 0.631501), metricText("median_won_cycle_days", 57), metricText("revenue", null)])
      .toEqual(["63,2%", "57 d", "—"]);
  });

  test("diagnósticos da base rica", () => {
    const rich = intelligence("intelligence-rich");
    const byCode = Object.fromEntries(rich.diagnostics.map((d) => [d.code, diagnosticText(d)]));
    expect(byCode.engaging_beyond_longest_cycle).toEqual({
      title: "2 negociações abertas há mais de 93 dias",
      body: "2 de 4 negociações em andamento (50,0%) estão abertas há mais tempo do que qualquer venda já fechada. " +
        "Na lista, elas ficam em Confirmar. O sistema não vê ligações nem reuniões: o tempo aberta não prova que a " +
        "negociação terminou.",
      step: "Rotina de confirmação: cada vendedor confirma no CRM quais seguem e registra o desfecho das demais. A " +
        "carteira fica menor e o que sobra é real.",
    });
    expect(byCode.open_without_account.body).toBe("3 de 6 abertas (50,0%) não têm cliente. Nas 121 fechadas, todas " +
      "têm cliente. Por isso a base não permite saber se a ausência do cliente diz algo sobre o desfecho.");
    expect(byCode.sellers_without_opportunities.body).toBe(
      "Fabio Zeta está no cadastro da equipe, mas sem nenhuma oportunidade no CRM.");
    expect(byCode.quarter_end_outcome_mix.body).toBe("No último mês de cada trimestre, 100,0% das 64 fechadas são " +
      "ganhas. Nos outros meses, 0,0% das 57.");
    expect(byCode.engagement_inflow_drop.body).toBe(
      "0 em nov/2017 e 1 em dez/2017, contra o ritmo de 9,4 por mês de jun/2017 a out/2017.");
  });

  test("decomposição e acaso com os números reais", () => {
    const sellers: RevenueDrivers = { segments_used: 30, spread_ratio: 9.34, volume_share: 0.614719,
      conversion_share: -0.013776, ticket_share: 0.399058, main: ["volume", "ticket"], negligible: ["conversion"] };
    expect(driversText("seller", sellers)).toBe("A receita varia 9,3 vezes entre 30 vendedores. Quanto da diferença " +
      "cada fator explica: volume de fechadas, 61,5%. Receita por venda (depende dos produtos vendidos), 39,9%. Taxa de ganho, quase " +
      "nada. A diferença vem sobretudo do volume de fechadas e da receita por venda (depende dos produtos vendidos).");
    const offsetting: RevenueDrivers = { segments_used: 5, spread_ratio: 3.2, volume_share: -0.303, conversion_share: -0.084,
      ticket_share: 1.387, main: ["ticket"], negligible: [] };
    const text = driversText("seller", offsetting);
    expect(text).toBe("A receita varia 3,2 vezes entre 5 vendedores. Neste recorte os fatores se compensam, então a " +
      "diferença não se divide em porcentagens. A diferença vem sobretudo da receita por venda (depende dos produtos vendidos).");
    expect(text).not.toMatch(/%/);
    const chance: ChanceTest = { verdict: "within_chance", segments_tested: 30, segments_small: 0, closed_tested: 6711,
      min_win_rate: 0.549784, max_win_rate: 0.703947, p_value: 0.2639, alpha: 0.007143 };
    expect(chanceText("seller", chance)).toBe(
      "Entre 30 vendedores, a taxa de ganho vai de 55,0% a 70,4%: diferença pequena demais para ser confiável com 6.711 fechadas: " +
        "poderia aparecer mesmo que os recortes fossem iguais.");
  });

  test("descobertas: concentração e cobertura do catálogo", () => {
    const concentrated = findingText({ code: "revenue_concentrated", params: { dimension: "product", top: 3, of: 7,
      share: 0.835199, keys: ["GTX Pro", "GTX Plus Pro", "MG Advanced"] } });
    expect(concentrated.title).toBe("3 de 7 produtos somam 83,5% da receita");
    const coverage = findingText({ code: "account_product_coverage", params: { accounts: 85, products: 7,
      distribution: [{ bought: 6, accounts: 73 }, { bought: 7, accounts: 12 }], most_missing: "GTK 500",
      most_missing_accounts: 73 } });
    expect(coverage.body).toBe("Dos 85 clientes com venda ganha, 73 compraram 6 e 12 compraram 7 dos 7 produtos. O " +
      "que mais falta é o GTK 500, em 73 clientes. Não há lacuna de produto visível para venda cruzada, e isso não " +
      "diz se um cliente compraria de novo.");
  });
});
