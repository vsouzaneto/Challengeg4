import { type Dataset, type Deal, monthOfQuarter } from "./dataset.ts"

/*
 * Modelo de score v1 (docs/analise-lead-scorer.md, seção 6).
 * Estrutura fixa; todos os números são reaprendidos da base a cada treino.
 * Nenhum nome de vendedor/produto/região aparece aqui: são só chaves de agrupamento.
 */

// Políticas: decisões de negócio, não aprendidas.
export const POLICY = {
  weekDays: 7,
  // percentis do ciclo dos ganhos que delimitam os estados (os dias são aprendidos)
  statePercentiles: { andamento: 0.75, esfriando: 0.95, tardio: 0.99 },
  minSeriesWon: 100, // ganhos mínimos para uma série ter curva/limiares próprios
  minImpactToExplain: 0.01, // ajuste só é citado na explicação se mover p em ≥ 1 p.p.
  candidates: {
    halfLife: [90, 180, 365, null] as (number | null)[], // null = sem ponderação por recência
    seriesPrior: [null, 200] as (number | null)[], // null = só curva global
    levels: ["tempo", "completo"] as const,
  },
  topShare: 0.2, // "topo da lista" avaliado no backtest
  followUpDays: 120, // acompanhamento mínimo após cada corte do backtest
  minClosedToTrain: 300,
}

export interface Config {
  halfLife: number | null
  seriesPrior: number | null
  levels: "tempo" | "completo"
}

interface LevelDef {
  id: string
  label: string
  key: (d: Deal) => string | null
}

export const LEVELS: LevelDef[] = [
  { id: "serie", label: "Série do produto", key: (d) => d.series },
  { id: "produto", label: "Produto", key: (d) => d.product },
  { id: "regiao", label: "Região", key: (d) => d.region },
  { id: "manager", label: "Manager", key: (d) => d.manager },
  { id: "vendedor", label: "Vendedor", key: (d) => d.agent },
  { id: "regiao_produto", label: "Região × produto", key: (d) => (d.region ? `${d.region} · ${d.product}` : null) },
  { id: "vendedor_produto", label: "Vendedor × produto", key: (d) => `${d.agent} · ${d.product}` },
  {
    id: "mes_trimestre",
    label: "Mês do trimestre de entrada",
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

export interface Model {
  cutoff: number
  config: Config
  base: number
  curves: { global: Curve; bySeries: Record<string, Curve> }
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

function fitLevels(rows: { d: Deal; y: number; w: number }[], useLevels: boolean) {
  let sw = 0
  let sy = 0
  for (const r of rows) {
    sw += r.w
    sy += r.w * r.y
  }
  const base = sw > 0 ? clampP(sy / sw) : 0.5
  const pred = rows.map(() => base)
  const levels: LevelFit[] = []
  if (!useLevels) return { base, levels }

  for (const level of LEVELS) {
    const agg = new Map<string, { n: number; won: number; exp: number }>()
    const keys = rows.map((r) => level.key(r.d))
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
    levels.push({ id: level.id, label: level.label, k, groups })
  }
  return { base, levels }
}

// ---------- Passo 3: razão valor realizado / preço ----------

const RHO_LEVELS = LEVELS.filter((l) => l.id === "serie" || l.id === "produto")

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
    const keys = rows.map((x) => level.key(x.d))
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

  const { base, levels } = fitLevels(closed, config.levels === "completo")
  const globalT = thresholdsFrom(cyclesAll.won, cyclesAll.lost)
  const seriesT: Record<string, Thresholds> = {}
  for (const [series, c] of cycles) {
    if (c.won.length >= POLICY.minSeriesWon) seriesT[series] = thresholdsFrom(c.won, c.lost.length ? c.lost : cyclesAll.lost)
  }

  return {
    cutoff,
    config,
    base,
    curves: { global, bySeries },
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

export type AgeState = "entrada" | "inicio" | "andamento" | "esfriando" | "tardio" | "fora"

export interface Adjustment {
  level: string
  label: string
  group: string
  n: number
  weight: number
  delta: number
  impact: number // variação de p causada por este ajuste
}

export interface ScoredDeal {
  deal: Deal
  age: number | null
  state: AgeState
  thresholds: Thresholds
  thresholdSource: "série" | "geral"
  pBase: number | null
  pModel: number | null
  p: number | null
  adjustments: Adjustment[]
  rho: number
  value: number | null
  expected: number | null
  support: number
  tail: { wins: number; atRisk: number; fromDays: number } | null // evidência usada além do histórico
  conversion: number | null // c aplicado a deals sem data de entrada
  flags: string[]
  score: number | null
  rank: number | null
}

export interface ScoreOptions {
  calibrator?: Calibrator | null
  conversion?: number // c = conversão Prospecting → Engaging, aprendida entre bases (conversion.ts)
}

// Calibração (Platt): p_cal = sigmoid(a + b·logit(p)), aprendida no backtest. Monotônica em p.
export interface Calibrator {
  a: number
  b: number
}

export function fitCalibrator(points: { p: number; y: number }[]): Calibrator {
  const xs = points.filter((q) => q.p > 0 && q.p < 1).map((q) => ({ x: logit(q.p), y: q.y }))
  let a = 0
  let b = 1
  for (let it = 0; it < 50 && xs.length; it++) {
    let ga = 0, gb = 0, haa = 0, hab = 0, hbb = 0
    for (const { x, y } of xs) {
      const p = sigmoid(a + b * x)
      const r = y - p
      const v = p * (1 - p)
      ga += r
      gb += r * x
      haa += v
      hab += v * x
      hbb += v * x * x
    }
    const det = haa * hbb - hab * hab
    if (Math.abs(det) < 1e-12) break
    const da = (hbb * ga - hab * gb) / det
    const db = (haa * gb - hab * ga) / det
    a += da
    b += db
    if (Math.abs(da) + Math.abs(db) < 1e-9) break
  }
  return { a, b }
}

export const calibrate = (p: number, c: Calibrator | null) => (c ? sigmoid(c.a + c.b * logit(clampP(p))) : p)

export function scoreDeal(d: Deal, m: Model, at: number, opts: ScoreOptions = {}): ScoredDeal {
  const curve = (d.series && m.curves.bySeries[d.series]) || m.curves.global
  const seriesT = d.series ? m.thresholds.bySeries[d.series] : undefined
  const t = seriesT ?? m.thresholds.global
  const age = d.engage === null ? null : at - d.engage
  const week = age === null ? 0 : Math.floor(age / POLICY.weekDays)

  let state: AgeState
  if (age === null) state = "entrada"
  else if (age > t.tardio || week > curve.lastEventWeek) state = "fora"
  else if (age < t.inicio) state = "inicio"
  else if (age <= t.andamento) state = "andamento"
  else if (age <= t.esfriando) state = "esfriando"
  else state = "tardio"

  const flags: string[] = []
  if (!d.account) flags.push("sem_conta")
  if (d.price === null) flags.push("produto_fora_catalogo")
  if (d.region === null) flags.push("vendedor_sem_cadastro")
  if (age === null) flags.push("estimativa_entrada")

  let pBase: number | null = null
  let pModel: number | null = null // antes da calibração
  let p: number | null = null
  const adjustments: Adjustment[] = []
  let tail: ScoredDeal["tail"] = null
  let conversion: number | null = null
  if (state === "fora") {
    // Além do histórico: sem curva, usa a evidência direta da cauda (curva global, mais deals).
    const g = m.curves.global
    const w = Math.min(week, g.tailP.length - 1)
    const src = g.tailWeek[w]
    tail = { wins: g.winsFrom[src], atRisk: g.support[src], fromDays: src * POLICY.weekDays }
    pBase = pModel = p = g.tailP[w]
  } else {
    pBase = curve.pFrom[week] ?? 0
    let x = logit(clampP(pBase))
    for (const level of m.levels) {
      const key = LEVELS.find((l) => l.id === level.id)!.key(d)
      const g = key ? level.groups[key] : undefined
      if (!g || g.w === 0) continue
      const before = sigmoid(x)
      x += g.w * g.delta
      adjustments.push({
        level: level.id,
        label: level.label,
        group: key!,
        n: g.n,
        weight: g.w,
        delta: g.delta,
        impact: sigmoid(x) - before,
      })
    }
    pModel = sigmoid(x)
    p = calibrate(pModel, opts.calibrator ?? null)
    if (age === null) {
      conversion = opts.conversion ?? 1
      p *= conversion
    }
  }

  let rho = m.rho.mean
  for (const level of m.rho.levels) {
    const key = RHO_LEVELS.find((l) => l.id === level.id)!.key(d)
    const g = key ? level.groups[key] : undefined
    if (g) rho += g.w * g.shift
  }
  const value = d.price === null ? null : d.price * rho
  const expected = p === null || value === null ? null : p * value

  return {
    deal: d,
    age,
    state,
    thresholds: t,
    thresholdSource: seriesT ? "série" : "geral",
    pBase,
    pModel,
    p,
    adjustments,
    rho,
    value,
    expected,
    support: curve.support[week] ?? 0,
    tail,
    conversion,
    flags,
    score: null,
    rank: null,
  }
}

// Pontua o pipeline aberto na data de referência.
// Score = 100 × R / (R + K): escala absoluta. K = receita esperada mediana dos deals vivos com data
// de entrada (score 50 = mediana; 75 = o triplo). K é fixo por versão e não muda com filtros.
export function scorePipeline(ds: Dataset, m: Model, opts: ScoreOptions = {}): { deals: ScoredDeal[]; K: number | null } {
  const deals = ds.deals.filter((d) => d.outcome === null).map((d) => scoreDeal(d, m, ds.refDay, opts))
  const median = (xs: number[]) => (xs.length ? [...xs].sort((a, b) => a - b)[Math.floor(xs.length / 2)] : null)
  const live = deals.filter((s) => s.expected !== null && s.state !== "fora" && s.state !== "entrada")
  const K = median(live.map((s) => s.expected!)) ?? median(deals.filter((s) => s.expected! > 0).map((s) => s.expected!))
  if (!K) return { deals, K: null }

  const ranked = deals.filter((s) => s.expected !== null).sort((a, b) => b.expected! - a.expected!)
  ranked.forEach((s, i) => {
    s.score = Math.round((100 * s.expected!) / (s.expected! + K))
    s.rank = i > 0 && ranked[i - 1].expected === s.expected ? ranked[i - 1].rank : i + 1
  })
  return { deals, K }
}
