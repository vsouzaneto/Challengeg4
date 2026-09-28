import { FLAG_LABEL, STATE_META, fmtChance, fmtDays, fmtInt, fmtMoney, fmtPct } from "@/lib/explain"
import { LOST_STAGE, WON_STAGE, formatDay, type Deal } from "@/lib/scoring/dataset"
import { LEVELS, type AgeState, type ScoredDeal } from "@/lib/scoring/model"
import type { AppState } from "@/lib/server/store"

// DTOs enviados à interface. Tudo aqui é derivado do estado calculado no servidor.

export interface Filters {
  regiao?: string
  manager?: string
  vendedor?: string
}

export interface CardDTO {
  id: string
  stage: string
  account: string | null
  product: string
  agent: string
  score: number | null
  rank: number | null // posição dentro da visão filtrada
  p: number | null
  value: number | null
  expected: number | null
  age: number | null
  state: AgeState | null
  flags: string[]
  tooltip: string[]
  closeDate: string | null
  closeValue: number | null
}

export interface LaneDTO {
  stage: string
  kind: "aberta" | "ganha" | "perdida"
  count: number
  cards: CardDTO[]
  expectedTotal: number
  closedTotal: number
  revalidar: { count: number; value: number; cards: CardDTO[] }
}

export interface BoardDTO {
  lanes: LaneDTO[]
  startStage: string | null
  options: {
    regions: string[]
    managers: { name: string; region: string | null }[]
    agents: { name: string; manager: string | null; region: string | null }[]
  }
  filters: Filters
  summary: { vivos: number; esfriando: number; revalidar: number; pendencias: number }
  refDay: string
  version: number
}

const CLOSED_LIMIT = 30
const REVALIDAR_LIMIT = 30

// Mesma ordem no ranking e nas raias: receita esperada desc, desempate estável pelo ID.
const byExpected = (a: ScoredDeal, b: ScoredDeal) => (b.expected ?? -1) - (a.expected ?? -1) || a.deal.id.localeCompare(b.deal.id)

const matches = (d: Deal, f: Filters) =>
  (!f.regiao || d.region === f.regiao) && (!f.manager || d.manager === f.manager) && (!f.vendedor || d.agent === f.vendedor)

function median(xs: number[]) {
  if (!xs.length) return 0
  const s = [...xs].sort((a, b) => a - b)
  return s[Math.floor(s.length / 2)]
}

function tooltipFor(s: ScoredDeal, rank: number | null, med: { p: number; v: number }): string[] {
  const meta = STATE_META[s.state]
  if (s.expected === null) return ["Sem score", "Produto fora do catálogo: sem preço para estimar o valor"]
  const head = `Score ${s.score}${rank ? ` · #${rank} nesta visão` : ""}`
  const revenue = `Receita esperada ${fmtMoney(s.expected)} = ${fmtChance(s.p)} de chance × ${fmtMoney(s.value)}`
  if (s.state === "fora") {
    return [
      head,
      revenue,
      `${fmtDays(s.age)} aberto: além de 99% dos ganhos (${fmtDays(s.thresholds.tardio)})`,
      `Na base, ${fmtInt(s.tail!.wins)} de ${fmtInt(s.tail!.atRisk)} deals abertos há ${s.tail!.fromDays}+ dias foram ganhos`,
    ]
  }
  const driver =
    s.value! >= med.v && s.p! >= med.p
      ? "Valor e chance acima da mediana do pipeline"
      : s.value! >= med.v
        ? "Puxado pelo valor: ticket alto, chance abaixo da mediana"
        : s.p! >= med.p
          ? "Puxado pela chance: ticket menor, boa chance para a idade"
          : "Valor e chance abaixo da mediana do pipeline"
  return [
    head,
    revenue,
    s.conversion !== null
      ? `Sem data de entrada: chance inclui ${fmtPct(s.conversion)} de conversão para Engaging`
      : `${fmtDays(s.age)} · ${meta.label}`,
    driver,
  ]
}

function closedCard(d: Deal): CardDTO {
  return {
    id: d.id,
    stage: d.stage,
    account: d.account,
    product: d.product,
    agent: d.agent,
    score: null,
    rank: null,
    p: null,
    value: null,
    expected: null,
    age: null,
    state: null,
    flags: [],
    tooltip: [],
    closeDate: d.close === null ? null : formatDay(d.close),
    closeValue: d.closeValue,
  }
}

export function buildBoard(state: AppState, filters: Filters): BoardDTO {
  const { ds } = state
  const open = state.scored.filter((s) => matches(s.deal, filters))
  const ranked = open.filter((s) => s.expected !== null).sort(byExpected)
  const viewRank = new Map(ranked.map((s, i) => [s.deal.id, i + 1]))
  const withScore = state.scored.filter((s) => s.expected !== null && s.state !== "fora")
  const med = { p: median(withScore.map((s) => s.p!)), v: median(withScore.map((s) => s.value!)) }

  const toCard = (s: ScoredDeal): CardDTO => {
    const rank = viewRank.get(s.deal.id) ?? null
    return {
      ...closedCard(s.deal),
      score: s.score,
      rank,
      p: s.p,
      value: s.value,
      expected: s.expected,
      age: s.age,
      state: s.state,
      flags: s.flags,
      tooltip: tooltipFor(s, rank, med),
    }
  }

  const lanes: LaneDTO[] = ds.lanes.map((stage) => {
    if (stage === WON_STAGE || stage === LOST_STAGE) {
      const closed = ds.deals
        .filter((d) => d.stage === stage && matches(d, filters))
        .sort((a, b) => (b.close ?? 0) - (a.close ?? 0))
      return {
        stage,
        kind: stage === WON_STAGE ? "ganha" : "perdida",
        count: closed.length,
        cards: closed.slice(0, CLOSED_LIMIT).map(closedCard),
        expectedTotal: 0,
        closedTotal: closed.reduce((sum, d) => sum + (d.closeValue ?? 0), 0),
        revalidar: { count: 0, value: 0, cards: [] },
      }
    }
    const inLane = open.filter((s) => s.deal.stage === stage)
    const active = inLane
      .filter((s) => s.state !== "fora")
      .sort(byExpected)
    const stale = inLane.filter((s) => s.state === "fora").sort(byExpected)
    return {
      stage,
      kind: "aberta",
      count: inLane.length,
      cards: active.map(toCard),
      expectedTotal: active.reduce((sum, s) => sum + (s.expected ?? 0), 0),
      closedTotal: 0,
      revalidar: {
        count: stale.length,
        value: stale.reduce((sum, s) => sum + (s.value ?? 0), 0),
        cards: stale.slice(0, REVALIDAR_LIMIT).map(toCard),
      },
    }
  })

  const agents = [...ds.agents.values()].filter((a) => ds.deals.some((d) => d.agent === a.name))
  return {
    lanes,
    startStage: ranked[0]?.deal.stage ?? null,
    options: {
      regions: [...new Set(agents.map((a) => a.region).filter((r): r is string => !!r))].sort(),
      managers: [...new Map(agents.filter((a) => a.manager).map((a) => [a.manager!, { name: a.manager!, region: a.region }])).values()].sort(
        (a, b) => a.name.localeCompare(b.name),
      ),
      agents: agents.map((a) => ({ name: a.name, manager: a.manager, region: a.region })).sort((a, b) => a.name.localeCompare(b.name)),
    },
    filters,
    summary: {
      vivos: ranked.filter((s) => s.state !== "fora").length,
      esfriando: open.filter((s) => s.state === "esfriando" || s.state === "tardio").length,
      revalidar: open.filter((s) => s.state === "fora").length,
      pendencias: open.filter((s) => s.flags.length > 0).length,
    },
    refDay: formatDay(ds.refDay),
    version: state.version.version,
  }
}

// ---------- Detalhe de uma oportunidade ----------

export interface DetailDTO {
  id: string
  stage: string
  product: string
  series: string | null
  agent: string
  manager: string | null
  region: string | null
  account: { name: string; sector: string | null; employees: number | null; location: string | null } | null
  score: number | null
  rankGlobal: number | null
  nScored: number
  state: AgeState
  age: number | null
  action: string
  thresholds: { inicio: number; andamento: number; esfriando: number; tardio: number; source: string }
  base: { p: number | null; support: number; curve: string }
  tail: { wins: number; atRisk: number; fromDays: number } | null
  conversion: { c: number; converted: number; failed: number } | null
  K: number | null
  adjustments: { label: string; group: string; n: number; weight: number; impact: number }[]
  groupsNote: string
  calibration: { before: number | null; after: number | null }
  p: number | null // chance final usada na receita esperada
  value: { price: number | null; rho: number; value: number | null }
  expected: number | null
  tasks: string[]
  model: { version: number; refDay: string; configKey: string }
}

export function buildDetail(state: AppState, id: string): DetailDTO | null {
  const s = state.byId.get(id)
  if (!s) return null
  const d = s.deal
  const acc = d.account ? state.ds.accounts.get(d.account) : undefined
  const zeroWeight = state.groupDiagnostics.filter((l) => l.k === null).map((l) => l.label)
  const groupsNote =
    state.model.config.levels === "tempo"
      ? `Grupos (${LEVELS.map((l) => l.label.toLowerCase()).join(", ")}) foram testados no backtest e não melhoraram a previsão; nesta versão a chance depende só da idade.`
      : zeroWeight.length
        ? `Sem diferença no histórico, peso zero: ${zeroWeight.join(", ")}.`
        : ""
  return {
    id: d.id,
    stage: d.stage,
    product: d.product,
    series: d.series,
    agent: d.agent,
    manager: d.manager,
    region: d.region,
    account: acc
      ? { name: acc.name, sector: acc.sector, employees: acc.employees, location: acc.location }
      : d.account
        ? { name: d.account, sector: null, employees: null, location: null }
        : null,
    score: s.score,
    rankGlobal: s.rank,
    nScored: state.scored.filter((x) => x.score !== null).length,
    state: s.state,
    age: s.age,
    action: STATE_META[s.state].action(s.thresholds),
    thresholds: { ...s.thresholds, source: s.thresholdSource === "série" ? `série ${d.series}` : "base inteira" },
    base: {
      p: s.pBase,
      support: s.support,
      curve: d.series && state.model.curves.bySeries[d.series] ? `curva da série ${d.series}` : "curva geral",
    },
    tail: s.tail,
    conversion:
      s.conversion === null
        ? null
        : { c: s.conversion, converted: state.conversion.converted, failed: state.conversion.failed },
    K: state.K,
    adjustments: s.adjustments.map((a) => ({ label: a.label, group: a.group, n: a.n, weight: a.weight, impact: a.impact })),
    groupsNote,
    // calibração vem antes da conversão de Prospecting
    calibration: { before: s.pModel, after: s.p === null || s.conversion === null ? s.p : s.p / s.conversion },
    p: s.p,
    value: { price: d.price, rho: s.rho, value: s.value },
    expected: s.expected,
    tasks: s.flags.map((f) => FLAG_LABEL[f] ?? f),
    model: { version: state.version.version, refDay: formatDay(state.ds.refDay), configKey: state.version.configKey },
  }
}
