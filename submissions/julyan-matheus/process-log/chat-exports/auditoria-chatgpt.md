/**
 * Lead Scorer — pure scoring logic. No I/O here.
 *
 * Everything is derived from the closed history (Won / Lost) and from the
 * open pipeline at a reference date. close_date / close_value of an open
 * deal are never read (leakage guard).
 */
import type {
  Bucket,
  Deal,
  Factors,
  PipelineRow,
  Product,
  ScoredDeal,
  Tier,
  TriagedDeal,
  Tone,
  WhyLine,
} from "./types";

// ---------------------------------------------------------------------------
// Constants (docs/spec.md §4–§6, docs/decisoes.md)
// ---------------------------------------------------------------------------

/** No deal in the history closed after this many days open (H5). */
export const MAX_DAYS_OPEN = 138;

/** Shrinkage strength for agent × product affinity (§5.1). */
export const AFFINITY_K = 15;

/** Score weights, Decisão 3 without the value factor, renormalized (§5). */
export const SCORE_WEIGHTS = { affinity: 0.5, momentum: 0.31, capacity: 0.19 } as const;

/** Weights used only for the "chance" that feeds expected value (§6). */
export const CHANCE_WEIGHTS = { affinity: 0.5, momentum: 0.3, capacity: 0.2 } as const;

/** Momentum is computed in fixed steps instead of per day (approved adjustment). */
export const MOMENTUM_STEPS = [0, 14, 30, 60, 90, 120] as const;

/** Below this many closed deals a momentum step falls back to the global win rate. */
export const MOMENTUM_MIN_SAMPLE = 30;

const PRODUCT_ALIASES: Record<string, string> = { GTXPro: "GTX Pro" };

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

export function normalizeProduct(name: string): string {
  const trimmed = name.trim();
  return PRODUCT_ALIASES[trimmed] ?? trimmed;
}

const MS_PER_DAY = 86_400_000;

function toUtc(iso: string): number {
  const [y, m, d] = iso.split("-").map(Number);
  return Date.UTC(y, m - 1, d);
}

/** Whole days between two ISO dates (b − a). */
export function daysBetween(a: string, b: string): number {
  return Math.round((toUtc(b) - toUtc(a)) / MS_PER_DAY);
}

export const isOpen = (d: Deal) => d.deal_stage === "Prospecting" || d.deal_stage === "Engaging";
export const isClosed = (d: Deal) => d.deal_stage === "Won" || d.deal_stage === "Lost";

/** Reference date = max close_date of the CLOSED deals. Never "today". */
export function referenceDate(deals: Deal[]): string {
  let max = "";
  for (const d of deals) {
    if (isClosed(d) && d.close_date && d.close_date > max) max = d.close_date;
  }
  if (!max) throw new Error("referenceDate: no closed deal with close_date");
  return max;
}

export function daysOpen(deal: Deal, ref: string): number | null {
  return deal.engage_date ? daysBetween(deal.engage_date, ref) : null;
}

function minmax(value: number, min: number, max: number): number {
  if (max === min) return 0.5;
  return (value - min) / (max - min);
}

const pct = (x: number) => ${Math.round(x * 100)}%;

// ---------------------------------------------------------------------------
// Triage (§4, Decisão 1) — order matters
// ---------------------------------------------------------------------------

export function triage(deal: Deal, ref: string): Bucket {
  if (!isOpen(deal)) throw new Error(triage: deal ${deal.opportunity_id} is not open);
  const days = daysOpen(deal, ref);
  if (deal.deal_stage === "Engaging" && days !== null && days > MAX_DAYS_OPEN) return "Limpar";
  if (!deal.account) return "Requalificar";
  if (deal.deal_stage === "Prospecting") return "Iniciar";
  return "Focar";
}

export const BUCKET_ACTION: Record<Exclude<Bucket, "Focar">, string> = {
  Limpar: "Fechar como Lost ou reabrir do zero",
  Requalificar: "Vincular conta no CRM",
  Iniciar: "Fazer primeiro contato",
};

// ---------------------------------------------------------------------------
// Historical stats
// ---------------------------------------------------------------------------

interface WinCount {
  wins: number;
  total: number;
}

export interface Stats {
  ref: string;
  globalWinRate: number;
  byAgent: Map<string, WinCount>;
  byAgentProduct: Map<string, WinCount>;
  /** step → win rate of closed deals that took >= step days (or null if sample too small). */
  momentumCurve: Map<number, { winRate: number; sample: number }>;
  /** open deals per agent at the reference date. */
  loadByAgent: Map<string, number>;
  loadMin: number;
  loadMax: number;
  loadMean: number;
  priceByProduct: Map<string, number>;
}

const comboKey = (agent: string, product: string) => ${agent}|${normalizeProduct(product)};

function bump(map: Map<string, WinCount>, key: string, won: boolean) {
  const cur = map.get(key) ?? { wins: 0, total: 0 };
  cur.total += 1;
  if (won) cur.wins += 1;
  map.set(key, cur);
}

export function buildStats(deals: Deal[], products: Product[], ref = referenceDate(deals)): Stats {
  const byAgent = new Map<string, WinCount>();
  const byAgentProduct = new Map<string, WinCount>();
  const loadByAgent = new Map<string, number>();
  let wins = 0;
  let closed = 0;
  const durations: { days: number; won: boolean }[] = [];

  for (const d of deals) {
    if (isClosed(d)) {
      const won = d.deal_stage === "Won";
      closed += 1;
      if (won) wins += 1;
      bump(byAgent, d.sales_agent, won);
      bump(byAgentProduct, comboKey(d.sales_agent, d.product), won);
      if (d.engage_date && d.close_date) {
        durations.push({ days: daysBetween(d.engage_date, d.close_date), won });
      }
    } else if (isOpen(d)) {
      loadByAgent.set(d.sales_agent, (loadByAgent.get(d.sales_agent) ?? 0) + 1);
    }
  }

  const globalWinRate = closed ? wins / closed : 0;

  const momentumCurve = new Map<number, { winRate: number; sample: number }>();
  for (const step of MOMENTUM_STEPS) {
    const slice = durations.filter((x) => x.days >= step);
    const sample = slice.length;
    const winRate =
      sample >= MOMENTUM_MIN_SAMPLE ? slice.filter((x) => x.won).length / sample : globalWinRate;
    momentumCurve.set(step, { winRate, sample });
  }

  const loads = [...loadByAgent.values()];
  const loadMin = loads.length ? Math.min(...loads) : 0;
  const loadMax = loads.length ? Math.max(...loads) : 0;
  const loadMean = loads.length ? loads.reduce((a, b) => a + b, 0) / loads.length : 0;

  const priceByProduct = new Map(products.map((p) => [normalizeProduct(p.product), p.sales_price]));

  return {
    ref,
    globalWinRate,
    byAgent,
    byAgentProduct,
    momentumCurve,
    loadByAgent,
    loadMin,
    loadMax,
    loadMean,
    priceByProduct,
  };
}

// ---------------------------------------------------------------------------
// Factors (§5.1–§5.3)
// ---------------------------------------------------------------------------

export interface AffinityDetail {
  value: number;
  comboWins: number;
  comboTotal: number;
  agentWinRate: number;
  agentTotal: number;
}

export function affinity(stats: Stats, agent: string, product: string): AffinityDetail {
  const agentStat = stats.byAgent.get(agent);
  const agentWinRate = agentStat && agentStat.total > 0 ? agentStat.wins / agentStat.total : stats.globalWinRate;
  const combo = stats.byAgentProduct.get(comboKey(agent, product));
  if (!combo || combo.total === 0) {
    return { value: agentWinRate, comboWins: 0, comboTotal: 0, agentWinRate, agentTotal: agentStat?.total ?? 0 };
  }
  const value = (combo.wins + AFFINITY_K * agentWinRate) / (combo.total + AFFINITY_K);
  return { value, comboWins: combo.wins, comboTotal: combo.total, agentWinRate, agentTotal: agentStat?.total ?? 0 };
}

export interface MomentumDetail {
  value: number;
  step: number;
  sample: number;
}

export function momentum(stats: Stats, days: number): MomentumDetail {
  let step: number = MOMENTUM_STEPS[0];
  for (const s of MOMENTUM_STEPS) if (days >= s) step = s;
  const point = stats.momentumCurve.get(step);
  if (!point) return { value: stats.globalWinRate, step, sample: 0 };
  return { value: point.winRate, step, sample: point.sample };
}

export interface CapacityDetail {
  /** 1 − minmax(load) */
  value: number;
  load: number;
  loadNorm: number;
}

export function capacity(stats: Stats, agent: string): CapacityDetail {
  const load = stats.loadByAgent.get(agent) ?? 0;
  const loadNorm = minmax(load, stats.loadMin, stats.loadMax);
  return { value: 1 - loadNorm, load, loadNorm };
}

// ---------------------------------------------------------------------------
// Score, chance, expected value (§5, §6)
// ---------------------------------------------------------------------------

export function computeScore(f: Factors): number {
  const raw =
    SCORE_WEIGHTS.affinity * f.affinity +
    SCORE_WEIGHTS.momentum * f.momentum +
    SCORE_WEIGHTS.capacity * f.capacity;
  return Math.min(100, Math.max(0, Math.round(raw * 100)));
}

/** §6: chance = 0.5·afinidade + 0.3·momentum + 0.2·(wr_global + (0.5 − minmax(carga)) × 0.1) */
export function computeChance(stats: Stats, aff: number, mom: number, loadNorm: number): number {
  const capTerm = stats.globalWinRate + (0.5 - loadNorm) * 0.1;
  const c = CHANCE_WEIGHTS.affinity * aff + CHANCE_WEIGHTS.momentum * mom + CHANCE_WEIGHTS.capacity * capTerm;
  return Math.min(1, Math.max(0, c));
}

// ---------------------------------------------------------------------------
// Explainability (§7)
// ---------------------------------------------------------------------------

const AFFINITY_TOLERANCE = 0.05;

export function explain(
  deal: Deal,
  days: number,
  aff: AffinityDetail,
  mom: MomentumDetail,
  cap: CapacityDetail,
  stats: Stats,
): WhyLine[] {
  const product = normalizeProduct(deal.product);

  // Afinidade
  let affText: string;
  let affTone: Tone;
  if (aff.comboTotal === 0) {
    affText = Sem histórico de ${product} — usando sua média de ${pct(aff.agentWinRate)};
    affTone = "neutro";
  } else {
    const diff = aff.value - aff.agentWinRate;
    const base = Você fecha ${pct(aff.value)} de ${product} (${aff.comboTotal} deals);
    if (diff >= AFFINITY_TOLERANCE) {
      affText = ${base} — acima da sua média de ${pct(aff.agentWinRate)};
      affTone = "positivo";
    } else if (diff <= -AFFINITY_TOLERANCE) {
      affText = ${base} — abaixo da sua média de ${pct(aff.agentWinRate)};
      affTone = "alerta";
    } else {
      affText = base;
      affTone = "neutro";
    }
  }

  // Momentum
  let momText: string;
  let momTone: Tone;
  if (days >= 120) {
    momText = Aberto há ${days} dias — perto do limite de ${MAX_DAYS_OPEN};
    momTone = "alerta";
  } else if (mom.value > stats.globalWinRate + 0.01) {
    momText = Aberto há ${days} dias — deals que chegam aqui fecham ${pct(mom.value)};
    momTone = "positivo";
  } else {
    momText = Aberto há ${days} dias — chance histórica de ${pct(mom.value)};
    momTone = "neutro";
  }

  // Capacidade
  const mean = Math.round(stats.loadMean);
  let capText: string;
  let capTone: Tone;
  if (cap.load < stats.loadMean) {
    capText = Você tem ${cap.load} deals abertos — abaixo da média (${mean});
    capTone = "positivo";
  } else if (cap.load > stats.loadMean * 1.25) {
    capText = Você tem ${cap.load} abertos — priorize;
    capTone = "alerta";
  } else {
    capText = Você tem ${cap.load} deals abertos — na média (${mean});
    capTone = "neutro";
  }

  return [
    { factor: "afinidade", text: affText, tone: affTone },
    { factor: "momentum", text: momText, tone: momTone },
    { factor: "capacidade", text: capText, tone: capTone },
  ];
}

// ---------------------------------------------------------------------------
// Public entry points
// ---------------------------------------------------------------------------

export function scoreDeal(deal: Deal, stats: Stats): ScoredDeal {
  const days = daysOpen(deal, stats.ref);
  if (days === null) throw new Error(scoreDeal: deal ${deal.opportunity_id} has no engage_date);
  const aff = affinity(stats, deal.sales_agent, deal.product);
  const mom = momentum(stats, days);
  const cap = capacity(stats, deal.sales_agent);
  const factors: Factors = { affinity: aff.value, momentum: mom.value, capacity: cap.value };
  const chance = computeChance(stats, aff.value, mom.value, cap.loadNorm);
  const price = stats.priceByProduct.get(normalizeProduct(deal.product)) ?? 0;
  return {
    deal,
    bucket: "Focar",
    daysOpen: days,
    score: computeScore(factors),
    tier: "Top", // overwritten by assignTiers once the agent's Focar is known
    chance,
    expectedValue: Math.round(chance * price),
    factors,
    why: explain(deal, days, aff, mom, cap, stats),
  };
}

/** Sort used for ranking inside an agent's Focar: score desc, then expected value desc, then id. */
export function byScoreDesc(a: ScoredDeal, b: ScoredDeal): number {
  return b.score - a.score || b.expectedValue - a.expectedValue || a.deal.opportunity_id.localeCompare(b.deal.opportunity_id);
}

/** Tier = third of the ranking among the same agent's Focar deals. Mutates tier in place. */
export function assignTiers(scored: ScoredDeal[]): void {
  const byAgent = new Map<string, ScoredDeal[]>();
  for (const s of scored) {
    const list = byAgent.get(s.deal.sales_agent) ?? [];
    list.push(s);
    byAgent.set(s.deal.sales_agent, list);
  }
  for (const list of byAgent.values()) {
    list.sort(byScoreDesc);
    const n = list.length;
    list.forEach((s, i) => {
      const pos = i / n;
      const tier: Tier = pos < 1 / 3 ? "Top" : pos < 2 / 3 ? "Meio" : "Fundo";
      s.tier = tier;
    });
  }
}

/** Triage every open deal; score only the Focar bucket. */
export function scorePipeline(deals: Deal[], products: Product[], ref?: string): PipelineRow[] {
  const stats = buildStats(deals, products, ref);
  const rows: PipelineRow[] = [];
  for (const deal of deals) {
    if (!isOpen(deal)) continue;
    const bucket = triage(deal, stats.ref);
    if (bucket === "Focar") {
      rows.push(scoreDeal(deal, stats));
    } else {
      const row: TriagedDeal = { deal, bucket, daysOpen: daysOpen(deal, stats.ref), action: BUCKET_ACTION[bucket] };
      rows.push(row);
    }
  }
  assignTiers(rows.filter(isScored));
  return rows;
}

export const isScored = (r: PipelineRow): r is ScoredDeal => r.bucket === "Focar";

export function countBuckets(rows: PipelineRow[]): Record<Bucket, number> {
  const c: Record<Bucket, number> = { Focar: 0, Requalificar: 0, Iniciar: 0, Limpar: 0 };
  for (const r of rows) c[r.bucket] += 1;
  return c;
}

/** Bloco "Hoje": top N of Focar by expected value (approved adjustment to §8). */
export function todayPicks(rows: PipelineRow[], n = 3): ScoredDeal[] {
  return rows
    .filter(isScored)
    .sort((a, b) => b.expectedValue - a.expectedValue || b.score - a.score)
    .slice(0, n);
}






Você é um revisor técnico cético. Abaixo está o código de um lead scorer para um CRM de vendas (dataset: pipeline com deal_stage, engage_date, close_date, close_value; produtos com preço; vendedores). Não te dei as conclusões do autor de propósito.

Encontre problemas reais: bugs de lógica, leakage (uso de informação que só existe depois do fechamento), divisão por zero, casos de borda mal tratados, pesos que não fazem sentido, ou qualquer coisa que faria o score enganar um vendedor. Seja específico: função, o que está errado, e como corrigir. Se algo está certo, não elogie — só liste problemas. No máximo 8 pontos, ordenados por gravidade.
[Crítico] buildStats() tem leakage temporal quando ref é informado
Função: buildStats
O ref pode ser, por exemplo, 2026-06-30, mas o loop inclui todos os deals fechados do dataset, inclusive os com close_date > ref.
Isso contamina globalWinRate, byAgent, byAgentProduct e momentumCurve com informação do futuro.
Pior: o comentário diz que o pipeline é calculado “at a reference date”, mas isso só é verdade quando ref coincide com a data máxima do dataset.

Correção: ao construir as estatísticas, considerar apenas:

if (isClosed(d) && d.close_date && d.close_date <= ref) {
  // usar no histórico
}

E, para o pipeline, considerar apenas deals que já existiam em ref.

[Crítico] loadByAgent também não é realmente “at the reference date”
Função: buildStats
Todo deal aberto no dataset entra na carga, independentemente de quando ele entrou no pipeline.
Se você fizer backtest em uma data passada, um deal aberto depois dessa data aumenta a carga do vendedor retroativamente.
Isso afeta diretamente capacity, computeScore() e computeChance().

Correção: filtrar os abertos para os que já existiam em ref, usando o timestamp disponível de criação/entrada no pipeline. Se engage_date for a melhor aproximação disponível:

if (isOpen(d) && d.engage_date && d.engage_date <= ref)
[Crítico] chance não é uma probabilidade calibrada, embora seja apresentada como “chance”
Função: computeChance

A fórmula mistura três scores arbitrários e chama o resultado de chance:

0.5 * affinity + 0.3 * momentum + 0.2 * capTerm

Isso não significa que um deal com chance = 0.70 tenha 70% de probabilidade de ganhar.

Não há nenhuma etapa que compare as chances previstas com os resultados reais para calibrá-las.
Isso é especialmente perigoso porque expectedValue = chance * price transforma uma métrica não calibrada em dinheiro.
Correção: ou chamar isso de priorityProbability/propensityScore, ou calibrar a saída contra histórico separado de treino/validação e só então tratá-la como probabilidade. Modelos de scoring precisam ser avaliados por calibração, não apenas ranking.
[Alto] capacity() pode dar capacidade artificialmente alta/baixa por causa da população usada no min-max
Função: capacity

loadMin e loadMax são calculados somente entre vendedores que possuem pelo menos um deal aberto:

const loads = [...loadByAgent.values()];
Um vendedor com zero deals simplesmente desaparece da distribuição.
Isso faz o significado de capacity = 1 - minmax(load) depender de quem atualmente tem pipeline, e não da capacidade real do time.
Além disso, se no futuro capacity() for chamado para um vendedor fora do mapa, ele recebe load = 0, que pode ficar abaixo de loadMin, produzindo loadNorm < 0 e portanto capacity > 1.

Correção: construir a carga usando uma lista explícita de vendedores do CRM, incluindo zeros, e limitar:

const loadNorm = Math.min(1, Math.max(0, minmax(...)));
[Alto] O expectedValue usa preço de catálogo, não valor econômico do deal
Função: scoreDeal

Você recebe close_value no dataset, mas para deals abertos ele não é usado — o que é correto para evitar leakage. O problema é o substituto:

const price = stats.priceByProduct.get(product) ?? 0;
Isso assume que todo deal de um produto vale exatamente sales_price.
Se houver quantidade, desconto, negociação, mix ou ticket diferente, dois deals com a mesma probabilidade terão o mesmo EV, mesmo podendo valer valores completamente diferentes.
E quando o produto não está em products, o EV vira zero, potencialmente mandando um deal importante para baixo.
Correção: ter um deal_value/open_value disponível no momento do scoring ou estimar ticket histórico por produto/segmento, com fallback explícito — nunca simplesmente 0.
[Alto] O score ignora o próprio deal_stage depois da triagem
Funções: triage, scoreDeal
Prospecting vira Iniciar; Engaging vira Focar. Depois disso, todo Focar é tratado pelo mesmo modelo.
O estágio é provavelmente um dos sinais mais fortes de probabilidade de fechamento, mas desaparece do score.
Mais problemático: momentum usa apenas idade do deal, então dois deals Engaging com mesma idade são equivalentes mesmo que o CRM tenha outros estados relevantes dentro do processo.
Correção: se deal_stage contém informação real de avanço, incorporá-la ao modelo ou construir modelos separados por estágio. A validação deve verificar se os tiers realmente apresentam lift histórico.
[Médio] O tratamento de cold start pode produzir scores absurdamente baixos
Funções: referenceDate, buildStats, affinity

Se não houver nenhum closed deal:

referenceDate(deals)

simplesmente lança erro.

Mesmo passando ref manualmente, globalWinRate = 0. Um vendedor sem histórico também recebe afinidade 0; momentum vira 0; e o score praticamente colapsa.
Isso significa que um CRM novo ou um vendedor novo não é apenas “incerto”: o sistema interpreta ausência de informação como probabilidade de fracasso.
Correção: definir um prior/base rate inicial, por exemplo uma taxa global configurável, e usar shrinkage também no nível global quando a amostra for pequena.
[Médio] assignTiers() força exatamente três faixas mesmo quando há pouquíssimos deals
Função: assignTiers
Com 1 deal → Top.
Com 2 → Top, Meio; nunca existe Fundo.
Com 3 → um em cada.
Com 4 → 2 Top, 1 Meio, 1 Fundo.
Ou seja, “Top / Meio / Fundo” não representa níveis estatisticamente diferentes; representa apenas posição relativa dentro de uma amostra que pode ser minúscula.
Um vendedor com 2 oportunidades terá uma “Top” mesmo que o score seja ruim.
Correção: exigir mínimo de deals para tiers, ou usar thresholds absolutos/percentis globais. E validar se os tiers realmente possuem taxas de fechamento crescentes antes de apresentá-los como prioridade.