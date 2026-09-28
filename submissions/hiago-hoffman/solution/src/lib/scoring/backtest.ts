import type { Dataset } from "./dataset.ts"
import { type Calibrator, type Config, POLICY, calibrate, fitCalibrator, fitModel, isOpenAt, scoreDeal } from "./model.ts"

/*
 * Backtest com cortes mensais: em cada corte o modelo só enxerga o que se sabia naquela data
 * e é avaliado pelo que aconteceu depois. Seleciona a configuração e decide a promoção.
 */

export interface ConfigResult {
  key: string
  config: Config
  brier: number
  capture: number // receita ganha capturada no topo da lista
  n: number
}

export interface Backtest {
  cutoffs: number[]
  results: ConfigResult[]
  baseline: { brier: number; capture: number } // sem modelo: taxa histórica constante e ordenação por preço
  calibration: { from: number; to: number; predicted: number; observed: number; n: number }[]
  calibrator: Calibrator
  calibratedBrier: number // validação cruzada por corte (calibrador treinado sem o corte avaliado)
  chosen: ConfigResult
  current: ConfigResult | null
  promoted: boolean
  reason: string
}

export const configKey = (c: Config) =>
  `recência ${c.halfLife ? `${c.halfLife}d` : "∞"} · curva ${c.seriesPrior === null ? "global" : `por série (m=${c.seriesPrior})`} · ${c.levels === "completo" ? "tempo + grupos" : "só tempo"}`

export function candidateConfigs(): Config[] {
  const out: Config[] = []
  for (const halfLife of POLICY.candidates.halfLife)
    for (const seriesPrior of POLICY.candidates.seriesPrior)
      for (const levels of POLICY.candidates.levels) out.push({ halfLife, seriesPrior, levels })
  return out
}

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
  const firstClose = Math.min(...closes)
  const cutoffs = monthEnds(firstClose, ds.refDay - POLICY.followUpDays).filter(
    (c) => closes.filter((x) => x <= c).length >= POLICY.minClosedToTrain,
  )
  if (!cutoffs.length) throw new Error("Histórico curto demais para backtest.")

  // Deals abertos em cada corte e o que aconteceu depois (ganho até a data de referência = 1).
  const evalSets = cutoffs.map((c) =>
    ds.deals
      .filter((d) => d.engage !== null && d.price !== null && isOpenAt(d, c))
      .map((d) => ({ d, y: d.outcome === "won" ? 1 : 0 })),
  )

  const configs = candidateConfigs()
  const allCalib = new Map<string, { p: number; y: number }[][]>()
  const results: ConfigResult[] = configs.map((config) => {
    let se = 0
    let n = 0
    let capture = 0
    const calib: { p: number; y: number }[][] = []
    cutoffs.forEach((c, i) => {
      calib.push([])
      const model = fitModel(ds, c, config)
      const items: { rankBy: number; revenue: number }[] = []
      for (const { d, y } of evalSets[i]) {
        const s = scoreDeal(d, model, c)
        const p = s.p ?? 0 // "fora do histórico" conta como sem chance no ranking
        se += (p - y) ** 2
        n++
        calib[i].push({ p, y })
        items.push({ rankBy: s.expected ?? 0, revenue: y * d.price! })
      }
      capture += captureTop(items)
    })
    const key = configKey(config)
    allCalib.set(key, calib)
    return { key, config, brier: se / n, capture: capture / cutoffs.length, n }
  })

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
  const baseline = { brier: bse / bn, capture: bcap / cutoffs.length }

  const best = [...results].sort((a, b) => a.brier - b.brier || b.capture - a.capture)[0]
  const cur = current ? results.find((r) => r.key === configKey(current)) ?? null : null
  let chosen = best
  let promoted = true
  let reason = "Primeira versão: configuração com menor erro no backtest."
  if (cur && cur.key !== best.key) {
    if (best.brier <= cur.brier && best.capture >= cur.capture) {
      reason = "Candidata superou a vigente em erro de probabilidade e em receita capturada."
    } else {
      chosen = cur
      promoted = false
      reason = "Candidata não superou a vigente nos dois critérios: configuração mantida, parâmetros reaprendidos."
    }
  } else if (cur) {
    promoted = false
    reason = "A configuração vigente continua a melhor; parâmetros reaprendidos com a base nova."
  }

  // Calibração: avaliada deixando um corte de fora; o calibrador final usa todos os cortes.
  const perCutoff = allCalib.get(chosen.key)!
  let cse = 0
  let cn = 0
  const heldOut: { p: number; y: number }[] = []
  perCutoff.forEach((points, i) => {
    const cal = fitCalibrator(perCutoff.filter((_, j) => j !== i).flat())
    for (const { p, y } of points) {
      const pc = p > 0 ? calibrate(p, cal) : 0
      cse += (pc - y) ** 2
      cn++
      heldOut.push({ p: pc, y })
    }
  })
  const calibrator = fitCalibrator(perCutoff.flat())

  const bins = Array.from({ length: 10 }, (_, i) => ({ from: i / 10, to: (i + 1) / 10, ps: 0, ys: 0, n: 0 }))
  for (const { p, y } of heldOut) {
    const b = bins[Math.min(9, Math.floor(p * 10))]
    b.ps += p
    b.ys += y
    b.n++
  }
  const calibration = bins
    .filter((b) => b.n > 0)
    .map((b) => ({ from: b.from, to: b.to, predicted: b.ps / b.n, observed: b.ys / b.n, n: b.n }))

  return { cutoffs, results, baseline, calibration, calibrator, calibratedBrier: cse / cn, chosen, current: cur, promoted, reason }
}
