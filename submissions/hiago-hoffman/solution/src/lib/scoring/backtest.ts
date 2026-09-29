import type { Dataset, Deal } from "./dataset.ts"
import {
  type Calibrator,
  type Config,
  LEVELS,
  POLICY,
  type Model,
  calibrate,
  fitCalibrator,
  fitModel,
  isOpenAt,
  scoreDeal,
} from "./model.ts"

/*
 * Backtest com cortes mensais: em cada corte o modelo só enxerga o que se sabia naquela data e é
 * avaliado pelo que aconteceu depois. Objetivo definido pelo negócio: colocar no topo da lista os
 * deals que geram receita, de preferência as maiores (receita ganha capturada no topo).
 * Etapas, todas decididas pelos dados:
 *   1. recência e curva (sem grupos);
 *   2. cada grupo testado sozinho: entra na fórmula se capturar pelo menos a mesma receita;
 *   3. urgência (força × janela): entra só se aumentar a receita capturada;
 *   4. a candidata só substitui a versão vigente se não for pior.
 */

export interface ConfigResult {
  key: string
  config: Config
  brier: number // erro das probabilidades (menor é melhor)
  capture: number // receita ganha capturada no topo da lista (maior é melhor)
  n: number
}

export interface Backtest {
  cutoffs: number[]
  baseline: { brier: number; capture: number } // sem modelo: taxa histórica e ordenação por preço
  bases: ConfigResult[]
  levelTests: (ConfigResult & { id: string; label: string; included: boolean })[]
  urgencyTests: ConfigResult[]
  chosen: ConfigResult
  current: ConfigResult | null
  promoted: boolean
  reason: string
  calibration: { from: number; to: number; predicted: number; observed: number; n: number }[]
  calibrator: Calibrator
  calibratedBrier: number // calibrador treinado sem o corte avaliado
}

const EPS = 1e-9

export const configKey = (c: Config) => {
  const groups = c.levels.length ? LEVELS.filter((l) => c.levels.includes(l.id)).map((l) => l.label.toLowerCase()).join(", ") : "nenhum"
  const urg = c.urgency.lambda > 0 ? `urgência ${c.urgency.lambda} em ${c.urgency.horizonDays}d` : "sem urgência"
  return `recência ${c.halfLife ? `${c.halfLife}d` : "∞"} · curva ${c.seriesPrior === null ? "global" : `por série (m=${c.seriesPrior})`} · grupos: ${groups} · ${urg}`
}

// Melhor = mais receita capturada; empate → menor erro de probabilidade.
const better = (a: ConfigResult, b: ConfigResult) => a.capture > b.capture + EPS || (Math.abs(a.capture - b.capture) <= EPS && a.brier < b.brier - EPS)

function monthEnds(from: number, to: number): number[] {
  const out: number[] = []
  const d = new Date(from * 86_400_000)
  for (let y = d.getUTCFullYear(), m = d.getUTCMonth(); ; m++) {
    const end = Date.UTC(y, m + 1, 0) / 86_400_000
    if (end > to) break
    if (end >= from) out.push(end)
  }
  return out
}

function captureTop(items: { rankBy: number; revenue: number }[]): number {
  const total = items.reduce((s, x) => s + x.revenue, 0)
  if (total === 0) return 0
  const top = [...items].sort((a, b) => b.rankBy - a.rankBy).slice(0, Math.ceil(items.length * POLICY.topShare))
  return top.reduce((s, x) => s + x.revenue, 0) / total
}

export function runBacktest(ds: Dataset, current: Config | null): Backtest {
  const closes = ds.deals.filter((d) => d.close !== null).map((d) => d.close!)
  const firstClose = closes.reduce((a, b) => Math.min(a, b), Infinity)
  const cutoffs = monthEnds(firstClose, ds.refDay - POLICY.followUpDays).filter(
    (c) => closes.filter((x) => x <= c).length >= POLICY.minClosedToTrain,
  )
  if (!cutoffs.length) throw new Error("Histórico curto demais para backtest.")

  // Deals abertos em cada corte e o que aconteceu depois (ganho até a data de referência = 1).
  const evalSets: { d: Deal; y: number }[][] = cutoffs.map((c) =>
    ds.deals.filter((d) => d.engage !== null && d.price !== null && isOpenAt(d, c)).map((d) => ({ d, y: d.outcome === "won" ? 1 : 0 })),
  )

  // O ajuste não depende da urgência: reaproveita os modelos entre configurações.
  const fits = new Map<string, Model>()
  const fitAt = (i: number, config: Config) => {
    const k = `${i}|${config.halfLife}|${config.seriesPrior}|${config.levels.join(",")}`
    let m = fits.get(k)
    if (!m) fits.set(k, (m = fitModel(ds, cutoffs[i], { ...config, urgency: { lambda: 0, horizonDays: 7 } })))
    return m
  }

  const points = new Map<string, { p: number; y: number }[][]>()
  const evaluate = (config: Config): ConfigResult => {
    const key = configKey(config)
    let se = 0
    let n = 0
    let capture = 0
    const perCutoff: { p: number; y: number }[][] = []
    cutoffs.forEach((c, i) => {
      const model = { ...fitAt(i, config), config }
      const items: { rankBy: number; revenue: number }[] = []
      const pts: { p: number; y: number }[] = []
      for (const { d, y } of evalSets[i]) {
        const s = scoreDeal(d, model, c)
        se += (s.p - y) ** 2
        n++
        pts.push({ p: s.p, y })
        items.push({ rankBy: s.priority ?? 0, revenue: y * d.price! })
      }
      perCutoff.push(pts)
      capture += captureTop(items)
    })
    points.set(key, perCutoff)
    return { key, config, brier: se / n, capture: capture / cutoffs.length, n }
  }
  const pick = (rs: ConfigResult[]) => rs.reduce((best, r) => (better(r, best) ? r : best))

  // 1. recência e curva
  const off = { lambda: 0, horizonDays: POLICY.candidates.urgencyHorizonDays[0] }
  const bases: ConfigResult[] = []
  for (const halfLife of POLICY.candidates.halfLife)
    for (const seriesPrior of POLICY.candidates.seriesPrior) bases.push(evaluate({ halfLife, seriesPrior, levels: [], urgency: off }))
  const base = pick(bases)

  // 2. cada grupo, isoladamente, contra a base
  const levelTests = LEVELS.map((l) => {
    const r = evaluate({ ...base.config, levels: [l.id] })
    return { ...r, id: l.id, label: l.label, included: !better(base, r) }
  })
  const withGroups = evaluate({ ...base.config, levels: levelTests.filter((t) => t.included).map((t) => t.id) })
  const grouped = better(base, withGroups) ? base : withGroups
  if (grouped === base) for (const t of levelTests) t.included = false // juntos pioraram: nenhum entra

  // 3. urgência
  const urgencyTests: ConfigResult[] = []
  for (const lambda of POLICY.candidates.urgencyLambda)
    for (const horizonDays of POLICY.candidates.urgencyHorizonDays)
      urgencyTests.push(evaluate({ ...grouped.config, urgency: { lambda, horizonDays } }))
  const bestUrgency = pick(urgencyTests)
  const candidate = better(bestUrgency, grouped) ? bestUrgency : grouped

  // 4. promoção
  const cur = current && Array.isArray(current.levels) && current.urgency ? evaluate(current) : null
  let chosen = candidate
  let promoted = true
  let reason = "Primeira versão: configuração que mais captura receita no teste em datas passadas."
  if (cur && cur.key !== candidate.key) {
    if (!better(cur, candidate)) reason = "Candidata capturou pelo menos a mesma receita que a vigente: promovida."
    else {
      chosen = cur
      promoted = false
      reason = "Candidata não superou a vigente: configuração mantida, parâmetros reaprendidos com a base nova."
    }
  } else if (cur) {
    promoted = false
    reason = "A configuração vigente continua a melhor; parâmetros reaprendidos com a base nova."
  }

  // Calibração: avaliada deixando um corte de fora; o calibrador final usa todos os cortes.
  const perCutoff = points.get(chosen.key)!
  let cse = 0
  let cn = 0
  const heldOut: { p: number; y: number }[] = []
  perCutoff.forEach((pts, i) => {
    const cal = fitCalibrator(perCutoff.filter((_, j) => j !== i).flat())
    for (const { p, y } of pts) {
      const pc = calibrate(p, cal)
      cse += (pc - y) ** 2
      cn++
      heldOut.push({ p: pc, y })
    }
  })
  const bins = Array.from({ length: 10 }, (_, i) => ({ from: i / 10, to: (i + 1) / 10, ps: 0, ys: 0, n: 0 }))
  for (const { p, y } of heldOut) {
    const b = bins[Math.min(9, Math.floor(p * 10))]
    b.ps += p
    b.ys += y
    b.n++
  }

  // Referência sem modelo: taxa histórica constante + ordenação só por preço.
  let bse = 0
  let bn = 0
  let bcap = 0
  cutoffs.forEach((c, i) => {
    const closed = ds.deals.filter((d) => d.close !== null && d.close <= c)
    const rate = closed.filter((d) => d.outcome === "won").length / closed.length
    for (const { y } of evalSets[i]) {
      bse += (rate - y) ** 2
      bn++
    }
    bcap += captureTop(evalSets[i].map(({ d, y }) => ({ rankBy: d.price!, revenue: y * d.price! })))
  })

  return {
    cutoffs,
    baseline: { brier: bse / bn, capture: bcap / cutoffs.length },
    bases,
    levelTests,
    urgencyTests,
    chosen,
    current: cur,
    promoted,
    reason,
    calibration: bins.filter((b) => b.n > 0).map((b) => ({ from: b.from, to: b.to, predicted: b.ps / b.n, observed: b.ys / b.n, n: b.n })),
    calibrator: fitCalibrator(perCutoff.flat()),
    calibratedBrier: cse / cn,
  }
}
