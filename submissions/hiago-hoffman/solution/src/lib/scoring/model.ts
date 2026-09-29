import { type Dataset, type Deal, monthOfQuarter } from "./dataset.ts"

/*
 * Modelo de score v1 (docs/analise-lead-scorer.md, seção 6).
 * Estrutura fixa; todos os números são reaprendidos da base a cada treino.
 * Nenhum nome de vendedor/produto/região aparece aqui: são só chaves de agrupamento.
 */

// Políticas: decisões de negócio, não aprendidas.
export const POLICY = {
  weekDays: 7,
  // percentis do ciclo dos ganhos que delimitam as situações (os dias são aprendidos)
  statePercentiles: { andamento: 0.75, esfriando: 0.95, tardio: 0.99 },
  minSeriesWon: 100, // ganhos mínimos para uma série ter curva/limiares próprios
  // Candidatos que o backtest testa; a escolha é feita pelos dados (backtest.ts).
  candidates: {
    halfLife: [90, 180, 365, null] as (number | null)[], // null = sem ponderação por recência
    seriesPrior: [null, 200] as (number | null)[], // null = só curva global
    urgencyLambda: [0.5, 1, 2, 3], // força da urgência (0 = desligada, sempre testada)
    urgencyHorizonDays: [7, 14, 21, 28], // janela da queda de chance
  },
  topShare: 0.2, // "topo da lista" avaliado no backtest
  followUpDays: 120, // acompanhamento mínimo após cada corte do backtest
  minClosedToTrain: 300,
}

export interface Config {
  halfLife: number | null
  seriesPrior: number | null
  levels: string[] // grupos que entram na fórmula (cada um aprovado separadamente no backtest)
  urgency: { lambda: number; horizonDays: number } // lambda 0 = urgência desligada
}

// Fator da fórmula ao qual cada grupo pertence.
export type FactorKind = "afinidade" | "relacionamento" | "produto" | "time" | "calendario"

export const FACTOR_LABEL: Record<FactorKind, string> = {
  afinidade: "Afinidade (produto × região/vendedor)",
  relacionamento: "Relacionamento (histórico do cliente)",
  produto: "Produto",
  time: "Time (região, manager, vendedor)",
  calendario: "Calendário",
}

// Contexto para chaves que dependem do tempo: primeira compra (Won) de cada conta.
export interface KeyCtx {
  firstWin: Map<string, number>
  at: number
}

interface LevelDef {
  id: string
  label: string
  kind: FactorKind
  key: (d: Deal, ctx: KeyCtx) => string | null
}

// Cliente com histórico = a conta já tinha uma compra fechada antes de o deal entrar em Engaging
// (ou antes da data do cálculo, se não tem data de entrada). Conta não informada = sem ajuste.
export const hasHistory = (d: Deal, ctx: KeyCtx) =>
  d.account ? (ctx.firstWin.get(d.account) ?? Infinity) < (d.engage ?? ctx.at) : null

export const LEVELS: LevelDef[] = [
  { id: "serie", label: "Série do produto", kind: "produto", key: (d) => d.series },
  { id: "produto", label: "Produto", kind: "produto", key: (d) => d.product },
  { id: "regiao", label: "Região", kind: "time", key: (d) => d.region },
  { id: "manager", label: "Manager", kind: "time", key: (d) => d.manager },
  { id: "vendedor", label: "Vendedor", kind: "time", key: (d) => d.agent },
  { id: "regiao_produto", label: "Região × produto", kind: "afinidade", key: (d) => (d.region ? `${d.region} · ${d.product}` : null) },
  { id: "vendedor_produto", label: "Vendedor × produto", kind: "afinidade", key: (d) => `${d.agent} · ${d.product}` },
  {
    id: "cliente_historico",
    label: "Cliente com histórico de compras",
    kind: "relacionamento",
    key: (d, ctx) => {
      const h = hasHistory(d, ctx)
      return h === null ? null : h ? "com histórico" : "sem histórico"
    },
  },
  {
    id: "mes_trimestre",
    label: "Mês do trimestre de entrada",
    kind: "calendario",
    key: (d) => (d.engage === null ? null : `${monthOfQuarter(d.engage)}º mês`),
  },
]

export interface Curve {
  hw: number[] // hazard de ganho por semana
  hl: number[] // hazard de perda por semana
  pFrom: number[] // P(ganhar em algum momento | aberto no início da semana k)
  support: number[] // deals (sem peso) ainda abertos no início da semana k
  winsFrom: number[] // ganhos (sem peso) com ciclo a partir da semana k
  // Chance para quem passou do histórico: (ganhos + 1) / (em risco + 2) a partir da semana k,
  // sem nunca subir com a idade (mínimo acumulado). Hoje: 0 ganhos em 1.273 deals → 0,08%.
  tailP: number[]
  tailWeek: number[] // semana cuja evidência define tailP[k] (onde o mínimo foi atingido)
  lastEventWeek: number
}

export interface LevelFit {
  id: string
  label: string
  kind: FactorKind
  k: number | null // força da priori; null = ∞ (sem sinal → peso 0)
  groups: Record<string, { n: number; rate: number; expected: number; w: number; delta: number }>
}

export interface RhoFit {
  mean: number
  levels: { id: string; label: string; k: number | null; groups: Record<string, { n: number; shift: number; w: number }> }[]
}

export interface Thresholds {
  inicio: number
  andamento: number
  esfriando: number
  tardio: number
  nWon: number
}

export type Situation = "inicio" | "andamento" | "esfriando" | "tardio" | "fora"

// Fator da situação: chance de ganho de um deal que está nessa situação (média das semanas da
// faixa, ponderada pelos deals que passaram por elas). Mesmo método para todas as situações.
export type SituationTable = Record<Situation, { p: number; reached: number; fromDays: number; toDays: number | null }>

export interface Model {
  cutoff: number
  config: Config
  base: number
  curves: { global: Curve; bySeries: Record<string, Curve> }
  situations: { global: SituationTable; bySeries: Record<string, SituationTable> }
  ctx: KeyCtx
  accountWins: Map<string, number[]> // dias das compras (Won) de cada conta até o corte
  levels: LevelFit[]
  rho: RhoFit
  thresholds: { global: Thresholds; bySeries: Record<string, Thresholds> }
  counts: { closed: number; won: number; lost: number; censored: number }
}

const logit = (p: number) => Math.log(p / (1 - p))
const sigmoid = (x: number) => 1 / (1 + Math.exp(-x))
const clampP = (p: number) => Math.min(1 - 1e-6, Math.max(1e-6, p))
const recency = (cutoff: number, end: number, halfLife: number | null) =>
  halfLife ? 2 ** (-(cutoff - end) / halfLife) : 1

// Como o deal era visto na data de corte: encerrado (com desfecho) ou aberto (censurado).
function observe(d: Deal, cutoff: number): { end: number; outcome: "won" | "lost" | null } | null {
  if (d.engage === null || d.engage > cutoff) return null
  if (d.outcome && d.close === null) return null
  if (d.outcome && d.close !== null && d.close <= cutoff) return { end: d.close, outcome: d.outcome }
  return { end: cutoff, outcome: null }
}

export function isOpenAt(d: Deal, at: number): boolean {
  if (d.outcome === null) return d.engage === null || d.engage <= at
  return d.engage !== null && d.engage <= at && d.close !== null && d.close > at
}

// ---------- Passo 1: curva de riscos competitivos ----------

interface Obs {
  week: number
  outcome: "won" | "lost" | null
  w: number
}

function buildCurve(obs: Obs[], prior: Curve | null, m: number): Curve {
  let len = prior?.hw.length ?? 0
  for (const o of obs) len = Math.max(len, o.week + 1)
  const W = new Array(len).fill(0)
  const L = new Array(len).fill(0)
  const ends = new Array(len).fill(0)
  const endsRaw = new Array(len).fill(0)
  const WRaw = new Array(len).fill(0)
  for (const o of obs) {
    ends[o.week] += o.w
    endsRaw[o.week] += 1
    if (o.outcome === "won") WRaw[o.week] += 1
    if (o.outcome === "won") W[o.week] += o.w
    else if (o.outcome === "lost") L[o.week] += o.w
  }
  const hw = new Array(len).fill(0)
  const hl = new Array(len).fill(0)
  const support = new Array(len).fill(0)
  const winsFrom = new Array(len).fill(0)
  let risk = 0
  let riskRaw = 0
  let winsRaw = 0
  let lastEventWeek = -1
  for (let k = len - 1; k >= 0; k--) {
    risk += ends[k]
    riskRaw += endsRaw[k]
    support[k] = riskRaw
    winsRaw += WRaw[k]
    winsFrom[k] = winsRaw
    if (lastEventWeek < 0 && W[k] + L[k] > 0) lastEventWeek = k
    const pw = prior ? prior.hw[k] ?? 0 : 0
    const pl = prior ? prior.hl[k] ?? 0 : 0
    const denom = risk + (prior ? m : 0)
    hw[k] = denom > 0 ? (W[k] + (prior ? m * pw : 0)) / denom : pw
    hl[k] = denom > 0 ? (L[k] + (prior ? m * pl : 0)) / denom : pl
    const total = hw[k] + hl[k]
    if (total > 1) {
      hw[k] /= total
      hl[k] /= total
    }
  }
  const pFrom = new Array(len + 1).fill(0)
  for (let k = len - 1; k >= 0; k--) pFrom[k] = hw[k] + (1 - hw[k] - hl[k]) * pFrom[k + 1]
  const tailP = new Array(len).fill(0)
  const tailWeek = new Array(len).fill(0)
  for (let k = 0; k < len; k++) {
    const laplace = (winsFrom[k] + 1) / (support[k] + 2)
    const keep = k > 0 && tailP[k - 1] <= laplace
    tailP[k] = keep ? tailP[k - 1] : laplace
    tailWeek[k] = keep ? tailWeek[k - 1] : k
  }
  return { hw, hl, pFrom, support, winsFrom, tailP, tailWeek, lastEventWeek: prior ? prior.lastEventWeek : lastEventWeek }
}

// ---------- Passo 2: ajustes hierárquicos com encolhimento aprendido ----------

function fitLevels(rows: { d: Deal; y: number; w: number }[], levelIds: string[], ctx: KeyCtx) {
  let sw = 0
  let sy = 0
  for (const r of rows) {
    sw += r.w
    sy += r.w * r.y
  }
  const base = sw > 0 ? clampP(sy / sw) : 0.5
  const pred = rows.map(() => base)
  const levels: LevelFit[] = []

  for (const level of LEVELS.filter((l) => levelIds.includes(l.id))) {
    const agg = new Map<string, { n: number; won: number; exp: number }>()
    const keys = rows.map((r) => level.key(r.d, ctx))
    rows.forEach((r, i) => {
      const key = keys[i]
      if (!key) return
      const a = agg.get(key) ?? { n: 0, won: 0, exp: 0 }
      a.n += r.w
      a.won += r.w * r.y
      a.exp += r.w * pred[i]
      agg.set(key, a)
    })
    let N = 0
    let won = 0
    let varObs = 0
    let varNoise = 0
    for (const a of agg.values()) {
      const rate = a.won / a.n
      const e = a.exp / a.n
      N += a.n
      won += a.won
      varObs += a.n * (rate - e) ** 2
      varNoise += e * (1 - e)
    }
    if (N === 0) continue
    varObs /= N
    varNoise /= N
    const pbar = won / N
    const tau2 = Math.max(0, varObs - varNoise)
    const k = tau2 > 0 ? Math.max(0, (pbar * (1 - pbar)) / tau2 - 1) : null

    const groups: LevelFit["groups"] = {}
    for (const [key, a] of agg) {
      const e = clampP(a.exp / a.n)
      const w = k === null ? 0 : a.n / (a.n + k)
      const delta = logit((a.won + 0.5) / (a.n + 1)) - logit(e)
      groups[key] = { n: a.n, rate: a.won / a.n, expected: e, w, delta }
    }
    rows.forEach((_, i) => {
      const g = keys[i] ? groups[keys[i]!] : undefined
      if (g && g.w > 0) pred[i] = clampP(sigmoid(logit(pred[i]) + g.w * g.delta))
    })
    levels.push({ id: level.id, label: level.label, kind: level.kind, k, groups })
  }
  return { base, levels }
}

// ---------- Passo 3: razão valor realizado / preço ----------

const RHO_LEVELS = LEVELS.filter((l) => l.id === "serie" || l.id === "produto")
const NO_CTX: KeyCtx = { firstWin: new Map(), at: 0 } // série e produto não dependem do tempo

function fitRho(rows: { d: Deal; r: number; w: number }[]): RhoFit {
  let sw = 0
  let sr = 0
  for (const x of rows) {
    sw += x.w
    sr += x.w * x.r
  }
  if (sw === 0) return { mean: 1, levels: [] }
  const mean = sr / sw
  let sigma2 = 0
  for (const x of rows) sigma2 += x.w * (x.r - mean) ** 2
  sigma2 /= sw
  const pred = rows.map(() => mean)
  const levels: RhoFit["levels"] = []
  for (const level of RHO_LEVELS) {
    const agg = new Map<string, { n: number; s: number }>()
    const keys = rows.map((x) => level.key(x.d, NO_CTX))
    rows.forEach((x, i) => {
      const key = keys[i]
      if (!key) return
      const a = agg.get(key) ?? { n: 0, s: 0 }
      a.n += x.w
      a.s += x.w * (x.r - pred[i])
      agg.set(key, a)
    })
    let N = 0
    let varObs = 0
    for (const a of agg.values()) {
      N += a.n
      varObs += a.n * (a.s / a.n) ** 2
    }
    if (N === 0) continue
    varObs /= N
    const varNoise = (sigma2 * agg.size) / N
    const tau2 = Math.max(0, varObs - varNoise)
    const k = tau2 > 0 ? sigma2 / tau2 : null
    const groups: RhoFit["levels"][number]["groups"] = {}
    for (const [key, a] of agg) groups[key] = { n: a.n, shift: a.s / a.n, w: k === null ? 0 : a.n / (a.n + k) }
    rows.forEach((_, i) => {
      const g = keys[i] ? groups[keys[i]!] : undefined
      if (g) pred[i] += g.w * g.shift
    })
    levels.push({ id: level.id, label: level.label, k, groups })
  }
  return { mean, levels }
}

// ---------- Passo 5: limiares de idade ----------

function weightedQuantile(items: { v: number; w: number }[], q: number): number {
  if (!items.length) return NaN
  const sorted = [...items].sort((a, b) => a.v - b.v)
  const total = sorted.reduce((s, x) => s + x.w, 0)
  let acc = 0
  for (const x of sorted) {
    acc += x.w
    if (acc >= q * total) return x.v
  }
  return sorted[sorted.length - 1].v
}

function thresholdsFrom(won: { v: number; w: number }[], lost: { v: number; w: number }[]): Thresholds {
  const p = POLICY.statePercentiles
  return {
    inicio: weightedQuantile(lost.length ? lost : won, 0.5),
    andamento: weightedQuantile(won, p.andamento),
    esfriando: weightedQuantile(won, p.esfriando),
    tardio: weightedQuantile(won, p.tardio),
    nWon: won.length,
  }
}

// ---------- Passo 1b: fator da situação ----------

// Chance de ganhar em algum momento para um deal aberto no início da semana w: curva enquanto
// há eventos; depois dela, a cauda (ganhos + 1) / (em risco + 2) da curva global.
export function weekChance(curve: Curve, global: Curve, w: number): number {
  if (w <= curve.lastEventWeek) return curve.pFrom[w] ?? 0
  return global.tailP[Math.min(w, global.tailP.length - 1)]
}

function situationTable(curve: Curve, global: Curve, t: Thresholds): SituationTable {
  const wk = (days: number) => Math.floor(days / POLICY.weekDays)
  const last = Math.max(curve.support.length, global.support.length) - 1
  const band = (fromDays: number, toDays: number | null, from: number, to: number) => {
    let num = 0
    let den = 0
    for (let w = from; w <= to; w++) {
      const n = curve.support[w] ?? global.support[w] ?? 0
      num += n * weekChance(curve, global, w)
      den += n
    }
    return { p: den > 0 ? num / den : weekChance(curve, global, from), reached: curve.support[from] ?? global.support[from] ?? 0, fromDays, toDays }
  }
  return {
    inicio: band(0, t.inicio, 0, Math.max(0, wk(t.inicio) - 1)),
    andamento: band(t.inicio, t.andamento, wk(t.inicio), wk(t.andamento)),
    esfriando: band(t.andamento, t.esfriando, wk(t.andamento) + 1, wk(t.esfriando)),
    tardio: band(t.esfriando, t.tardio, wk(t.esfriando) + 1, wk(t.tardio)),
    fora: band(t.tardio, null, wk(t.tardio) + 1, Math.max(last, wk(t.tardio) + 1)),
  }
}

// ---------- Treino ----------

export function fitModel(ds: Dataset, cutoff: number, config: Config): Model {
  const obs: (Obs & { d: Deal })[] = []
  const closed: { d: Deal; y: number; w: number }[] = []
  const ratios: { d: Deal; r: number; w: number }[] = []
  const cycles = new Map<string, { won: { v: number; w: number }[]; lost: { v: number; w: number }[] }>()
  const cyclesAll = { won: [] as { v: number; w: number }[], lost: [] as { v: number; w: number }[] }
  let censored = 0

  for (const d of ds.deals) {
    const o = observe(d, cutoff)
    if (!o) continue
    const w = recency(cutoff, o.end, config.halfLife)
    const duration = o.end - d.engage!
    obs.push({ d, week: Math.floor(duration / POLICY.weekDays), outcome: o.outcome, w })
    if (o.outcome === null) {
      censored++
      continue
    }
    closed.push({ d, y: o.outcome === "won" ? 1 : 0, w })
    if (o.outcome === "won" && d.price && d.closeValue !== null && d.closeValue > 0) {
      ratios.push({ d, r: d.closeValue / d.price, w })
    }
    const bucket = cyclesAll[o.outcome]
    bucket.push({ v: duration, w })
    if (d.series) {
      const c = cycles.get(d.series) ?? { won: [], lost: [] }
      c[o.outcome].push({ v: duration, w })
      cycles.set(d.series, c)
    }
  }
  if (!closed.length) throw new Error("Sem oportunidades encerradas até a data de corte: não há do que aprender.")

  const global = buildCurve(obs, null, 0)
  const bySeries: Record<string, Curve> = {}
  if (config.seriesPrior !== null) {
    const perSeries = new Map<string, Obs[]>()
    for (const o of obs) {
      if (!o.d.series) continue
      const list = perSeries.get(o.d.series) ?? []
      list.push(o)
      perSeries.set(o.d.series, list)
    }
    for (const [series, list] of perSeries) bySeries[series] = buildCurve(list, global, config.seriesPrior)
  }

  const firstWin = new Map<string, number>()
  const accountWins = new Map<string, number[]>()
  for (const d of ds.deals) {
    if (d.outcome !== "won" || !d.account || d.close === null || d.close > cutoff) continue
    firstWin.set(d.account, Math.min(firstWin.get(d.account) ?? Infinity, d.close))
    accountWins.set(d.account, [...(accountWins.get(d.account) ?? []), d.close])
  }
  const ctx: KeyCtx = { firstWin, at: cutoff }

  const { base, levels } = fitLevels(closed, config.levels, ctx)
  const globalT = thresholdsFrom(cyclesAll.won, cyclesAll.lost)
  const seriesT: Record<string, Thresholds> = {}
  for (const [series, c] of cycles) {
    if (c.won.length >= POLICY.minSeriesWon) seriesT[series] = thresholdsFrom(c.won, c.lost.length ? c.lost : cyclesAll.lost)
  }
  const sitSeries: Record<string, SituationTable> = {}
  for (const [series, curve] of Object.entries(bySeries)) sitSeries[series] = situationTable(curve, global, seriesT[series] ?? globalT)
  for (const series of Object.keys(seriesT)) sitSeries[series] ??= situationTable(global, global, seriesT[series])

  return {
    cutoff,
    config,
    base,
    curves: { global, bySeries },
    situations: { global: situationTable(global, global, globalT), bySeries: sitSeries },
    ctx,
    accountWins,
    levels,
    rho: fitRho(ratios),
    thresholds: { global: globalT, bySeries: seriesT },
    counts: {
      closed: closed.length,
      won: cyclesAll.won.length,
      lost: cyclesAll.lost.length,
      censored,
    },
  }
}

// ---------- Pontuação ----------
//
// Um score só, a mesma fórmula para todo deal aberto:
//   Prioridade = Valor × Situação × Afinidade × Relacionamento × (outros grupos) × Urgência
//   Score      = 100 × Prioridade / (Prioridade + K)
// Cada fator é aprendido; o que não tem sinal na base fica ×1,00.

export type AgeState = "entrada" | Situation

// Calibração isotônica, aprendida no backtest: "30% previsto" passa a valer 30% observado.
// Blocos monotônicos (PAV) com taxa suavizada (acertos + 1) / (deals + 2), interpolados entre si.
// Diferente de uma reta em logit, não infla chances muito pequenas (ex.: deals em Revalidar).
export interface Calibrator {
  xs: number[] // chance prevista média de cada bloco (crescente)
  ys: number[] // taxa observada suavizada do bloco (não decrescente)
}

export function fitCalibrator(points: { p: number; y: number }[]): Calibrator {
  const sorted = [...points].sort((a, b) => a.p - b.p)
  const blocks: { sp: number; sy: number; n: number }[] = []
  const rate = (b: { sy: number; n: number }) => (b.sy + 1) / (b.n + 2)
  for (const { p, y } of sorted) {
    blocks.push({ sp: p, sy: y, n: 1 })
    while (blocks.length > 1 && rate(blocks[blocks.length - 2]) >= rate(blocks[blocks.length - 1])) {
      const last = blocks.pop()!
      const prev = blocks[blocks.length - 1]
      prev.sp += last.sp
      prev.sy += last.sy
      prev.n += last.n
    }
  }
  return { xs: blocks.map((b) => b.sp / b.n), ys: blocks.map(rate) }
}

export function calibrate(p: number, c: Calibrator | null): number {
  if (!c || !c.xs.length) return p
  const { xs, ys } = c
  if (p <= xs[0]) return xs[0] > 0 ? (ys[0] * p) / xs[0] : ys[0]
  if (p >= xs[xs.length - 1]) return ys[ys.length - 1]
  let i = 1
  while (xs[i] < p) i++
  const t = (p - xs[i - 1]) / (xs[i] - xs[i - 1])
  return ys[i - 1] + t * (ys[i] - ys[i - 1])
}

export interface ScoreOptions {
  calibrator?: Calibrator | null
  conversion?: number // c = conversão Prospecting → Engaging, aprendida entre bases (conversion.ts)
}

// Um fator multiplicativo da fórmula, já na escala final (depois da calibração).
export interface GroupFactor {
  level: string
  label: string
  kind: FactorKind
  group: string
  n: number // deals (com peso de recência) que sustentam o ajuste
  rate: number // taxa de ganho observada no grupo
  expected: number // taxa que o modelo esperava para o grupo antes deste ajuste
  weight: number // peso aprendido do grupo (0 = sem sinal)
  factor: number // multiplicador aplicado à chance
}

export interface ScoredDeal {
  deal: Deal
  age: number | null
  state: AgeState
  thresholds: Thresholds
  thresholdSource: "série" | "geral"
  situation: { p: number; reached: number; conversion: number | null; factor: number } // factor = fator final da situação
  factors: GroupFactor[]
  p: number // chance final
  urgency: { factor: number; drop: number; horizonDays: number; lambda: number }
  rho: number
  value: number | null
  expected: number | null // valor × chance
  priority: number | null // expected × urgência
  history: { purchases: number } | null // compras anteriores da conta (para a explicação)
  flags: string[]
  score: number | null
  rank: number | null
}

export function situationOf(age: number | null, t: Thresholds): AgeState {
  if (age === null) return "entrada"
  if (age > t.tardio) return "fora"
  if (age < t.inicio) return "inicio"
  if (age <= t.andamento) return "andamento"
  if (age <= t.esfriando) return "esfriando"
  return "tardio"
}

export function scoreDeal(d: Deal, m: Model, at: number, opts: ScoreOptions = {}): ScoredDeal {
  const g = m.curves.global
  const curve = (d.series && m.curves.bySeries[d.series]) || g
  const seriesT = d.series ? m.thresholds.bySeries[d.series] : undefined
  const t = seriesT ?? m.thresholds.global
  const table = (d.series && m.situations.bySeries[d.series]) || m.situations.global
  const age = d.engage === null ? null : at - d.engage
  const state = situationOf(age, t)
  const cal = opts.calibrator ?? null

  // Situação: chance da faixa (Prospecting usa a de Início × conversão aprendida).
  const band = table[state === "entrada" ? "inicio" : state]
  const conversion = state === "entrada" ? (opts.conversion ?? 1) : null
  const conv = conversion ?? 1
  let x = logit(clampP(band.p))
  const situationFactor = calibrate(band.p, cal) * conv

  // Grupos aprovados no backtest: cada um vira um multiplicador explícito.
  const ctx: KeyCtx = { firstWin: m.ctx.firstWin, at }
  const factors: GroupFactor[] = []
  for (const level of m.levels) {
    const def = LEVELS.find((l) => l.id === level.id)!
    const key = def.key(d, ctx)
    if (!key) continue
    const gr = level.groups[key]
    const before = calibrate(sigmoid(x), cal)
    if (gr && gr.w > 0) x += gr.w * gr.delta
    factors.push({
      level: level.id,
      label: level.label,
      kind: level.kind,
      group: key,
      n: gr?.n ?? 0,
      rate: gr?.rate ?? 0,
      expected: gr?.expected ?? 0,
      weight: gr?.w ?? 0,
      factor: calibrate(sigmoid(x), cal) / before,
    })
  }
  const p = calibrate(sigmoid(x), cal) * conv

  // Urgência: queda prevista da chance na janela, se nada for feito (0 para Prospecting).
  const { lambda, horizonDays } = m.config.urgency
  let drop = 0
  if (age !== null) {
    const w = Math.floor(age / POLICY.weekDays)
    const now = weekChance(curve, g, w)
    const later = weekChance(curve, g, w + Math.round(horizonDays / POLICY.weekDays))
    drop = now > 0 ? Math.max(0, (now - later) / now) : 0
  }
  const urgency = { factor: 1 + lambda * drop, drop, horizonDays, lambda }

  let rho = m.rho.mean
  for (const level of m.rho.levels) {
    const key = RHO_LEVELS.find((l) => l.id === level.id)!.key(d, NO_CTX)
    const gr = key ? level.groups[key] : undefined
    if (gr) rho += gr.w * gr.shift
  }
  const value = d.price === null ? null : d.price * rho
  const expected = value === null ? null : p * value

  let history: ScoredDeal["history"] = null
  if (d.account) {
    let purchases = 0
    for (const day of m.accountWins.get(d.account) ?? []) if (day < (d.engage ?? at)) purchases++
    history = { purchases }
  }

  const flags: string[] = []
  if (!d.account) flags.push("sem_conta")
  if (d.price === null) flags.push("produto_fora_catalogo")
  if (d.region === null) flags.push("vendedor_sem_cadastro")
  if (age === null) flags.push("estimativa_entrada")

  return {
    deal: d,
    age,
    state,
    thresholds: t,
    thresholdSource: seriesT ? "série" : "geral",
    situation: { p: band.p, reached: band.reached, conversion, factor: situationFactor },
    factors,
    p,
    urgency,
    rho,
    value,
    expected,
    priority: expected === null ? null : expected * urgency.factor,
    history,
    flags,
    score: null,
    rank: null,
  }
}

// Pontua o pipeline aberto na data de referência. Score = 100 × P / (P + K), escala absoluta:
// K = prioridade mediana dos deals vivos com data de entrada (50 = mediana; 75 = o triplo).
// K é fixo por versão e não muda com filtros.
export function scorePipeline(ds: Dataset, m: Model, opts: ScoreOptions = {}): { deals: ScoredDeal[]; K: number | null } {
  const deals = ds.deals.filter((d) => d.outcome === null).map((d) => scoreDeal(d, m, ds.refDay, opts))
  const median = (xs: number[]) => (xs.length ? [...xs].sort((a, b) => a - b)[Math.floor(xs.length / 2)] : null)
  const live = deals.filter((s) => s.priority !== null && s.state !== "fora" && s.state !== "entrada")
  const K = median(live.map((s) => s.priority!)) ?? median(deals.filter((s) => s.priority! > 0).map((s) => s.priority!))
  if (!K) return { deals, K: null }

  const ranked = deals.filter((s) => s.priority !== null).sort((a, b) => b.priority! - a.priority!)
  ranked.forEach((s, i) => {
    s.score = Math.round((100 * s.priority!) / (s.priority! + K))
    s.rank = i > 0 && ranked[i - 1].priority === s.priority ? ranked[i - 1].rank : i + 1
  })
  return { deals, K }
}
