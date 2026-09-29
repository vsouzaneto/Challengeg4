import { STATE_META, fmtChance, fmtDays, fmtDec, fmtInt, fmtMoney, fmtPct } from "@/lib/explain"
import { LOST_STAGE, WON_STAGE, formatDay, type Deal } from "@/lib/scoring/dataset"
import type { AgeState, ScoredDeal } from "@/lib/scoring/model"
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
  priority: number | null
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
  priorityTotal: number
  closedTotal: number
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

// Mesma ordem no ranking, nas raias e no bloco Revalidar: prioridade desc, desempate pelo ID.
const byPriority = (a: ScoredDeal, b: ScoredDeal) => (b.priority ?? -1) - (a.priority ?? -1) || a.deal.id.localeCompare(b.deal.id)

const matches = (d: Deal, f: Filters) =>
  (!f.regiao || d.region === f.regiao) && (!f.manager || d.manager === f.manager) && (!f.vendedor || d.agent === f.vendedor)

// Tooltip em linguagem de vendedor: a nota, a conta que a gera e só o que mexeu nela.
function situationPhrase(s: ScoredDeal) {
  const days = fmtDays(s.age)
  switch (s.state) {
    case "entrada":
      return `Prospecting: ainda não entrou em Engaging. A chance já desconta os ${fmtPct(1 - (s.situation.conversion ?? 1))} que costumam não avançar`
    case "inicio":
      return `Início: aberto há ${days}`
    case "andamento":
      return `Em andamento: aberto há ${days}, dentro do prazo normal de fechamento`
    case "esfriando":
      return `Esfriando: aberto há ${days}, já passou do prazo em que a maioria dos ganhos fecha`
    case "tardio":
      return `Tardio: aberto há ${days}, quase todos os ganhos já teriam fechado`
    case "fora":
      return `Revalidar: aberto há ${days}, além do prazo de 99% dos ganhos. Chance quase nula`
  }
}

function factorPhrase(f: ScoredDeal["factors"][number]) {
  const pct = Math.round((f.factor - 1) * 100)
  const effect = `chance ${Math.abs(pct)}% ${pct > 0 ? "maior" : "menor"}`
  switch (f.kind) {
    case "calendario":
      return `Entrou no ${f.group} do trimestre: ${effect}`
    case "relacionamento":
      return `Cliente ${f.group} de compras: ${effect}`
    case "afinidade":
      return `${f.group} costuma converter ${pct > 0 ? "mais" : "menos"}: ${effect}`
    default:
      return `${f.label} ${f.group}: ${effect}`
  }
}

function tooltipFor(s: ScoredDeal, rank: number | null, K: number | null): string[] {
  if (s.priority === null) return ["Sem nota", "Produto fora do catálogo: sem preço para calcular"]
  const ratio = K ? s.priority / K : null
  const vsTypical =
    ratio === null ? "" : ratio >= 1.05 ? `, ${fmtDec(ratio, ratio < 10 ? 1 : 0)}× um deal típico` : ratio <= 0.95 ? ", abaixo de um deal típico" : ", igual a um deal típico"
  return [
    `Nota ${s.score} de 100${rank ? ` · ${rank}º da lista` : ""}`,
    `Vale ${fmtMoney(s.value)} e tem ${fmtChance(s.p)} de chance de fechar: ${fmtMoney(s.priority)} esperados${vsTypical}`,
    situationPhrase(s),
    ...s.factors.filter((f) => Math.abs(f.factor - 1) >= 0.005).map(factorPhrase),
    ...(s.urgency.factor - 1 >= 0.005 ? [`Urgência: a chance cai ${fmtPct(s.urgency.drop)} em ${s.urgency.horizonDays} dias se nada for feito`] : []),
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
    priority: null,
    age: null,
    state: null,
    flags: [],
    tooltip: [],
    closeDate: d.close === null ? null : formatDay(d.close),
    closeValue: d.closeValue,
  }
}

// Os filtros ficam coerentes com o que foi escolhido: vendedor preenche o manager e a região dele;
// manager preenche a região. Vale também para links compartilhados só com ?vendedor=.
function normalize(state: AppState, f: Filters): Filters {
  const agent = f.vendedor ? state.ds.agents.get(f.vendedor) : undefined
  const manager = f.manager ?? agent?.manager ?? undefined
  const managerRegion = manager ? [...state.ds.agents.values()].find((a) => a.manager === manager)?.region : undefined
  return { regiao: f.regiao ?? agent?.region ?? managerRegion ?? undefined, manager, vendedor: f.vendedor }
}

export function buildBoard(state: AppState, rawFilters: Filters): BoardDTO {
  const { ds } = state
  const filters = normalize(state, rawFilters)
  const open = state.scored.filter((s) => matches(s.deal, filters))
  const ranked = open.filter((s) => s.priority !== null).sort(byPriority)
  const viewRank = new Map(ranked.map((s, i) => [s.deal.id, i + 1]))

  const toCard = (s: ScoredDeal): CardDTO => {
    const rank = viewRank.get(s.deal.id) ?? null
    return {
      ...closedCard(s.deal),
      score: s.score,
      rank,
      p: s.p,
      value: s.value,
      priority: s.priority,
      age: s.age,
      state: s.state,
      flags: s.flags,
      tooltip: tooltipFor(s, rank, state.K),
    }
  }

  const lanes: LaneDTO[] = ds.lanes.map((stage) => {
    if (stage === WON_STAGE || stage === LOST_STAGE) {
      const closed = ds.deals.filter((d) => d.stage === stage && matches(d, filters)).sort((a, b) => (b.close ?? 0) - (a.close ?? 0))
      return {
        stage,
        kind: stage === WON_STAGE ? "ganha" : "perdida",
        count: closed.length,
        cards: closed.slice(0, CLOSED_LIMIT).map(closedCard),
        priorityTotal: 0,
        closedTotal: closed.reduce((sum, d) => sum + (d.closeValue ?? 0), 0),
      }
    }
    // Um score só: todas as oportunidades da raia numa lista, na ordem do score (Revalidar inclusive).
    const inLane = open.filter((s) => s.deal.stage === stage).sort(byPriority)
    return {
      stage,
      kind: "aberta",
      count: inLane.length,
      cards: inLane.map(toCard),
      priorityTotal: inLane.reduce((sum, s) => sum + (s.priority ?? 0), 0),
      closedTotal: 0,
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
// Só o que justifica a posição: valor, situação, fatores que mudaram a chance, urgência ativa, score.

const ALWAYS = 0.005 // abaixo disso o fator é ×1,00 e não aparece

export interface DetailDTO {
  id: string
  stage: string
  product: string
  agent: string
  region: string | null
  account: string | null
  score: number | null
  rank: number | null
  nScored: number
  state: AgeState
  age: number | null
  thresholds: { inicio: number; andamento: number; esfriando: number; tardio: number; source: string }
  situation: {
    label: string
    meaning: string
    chance: number // chance da situação (calibrada, antes da conversão)
    factor: number // fator final da situação na fórmula
    reached: number
    conversion: { c: number; converted: number; failed: number } | null
  }
  factors: { label: string; factor: number; reason: string }[] // só os diferentes de ×1,00
  urgency: { factor: number; drop: number; horizonDays: number } | null // só se ativa
  value: { price: number | null; rho: number; value: number | null }
  p: number
  priority: number | null
  K: number | null
}

function meaningOf(state: AgeState, t: { inicio: number; andamento: number; esfriando: number; tardio: number }) {
  switch (state) {
    case "entrada":
      return "Sem data de entrada em Engaging."
    case "inicio":
      return `Até ${t.inicio} dias desde a entrada: ainda antes do prazo em que metade das perdas acontece.`
    case "andamento":
      return `${t.inicio} a ${t.andamento} dias desde a entrada: dentro do prazo em que 75% dos ganhos fecham.`
    case "esfriando":
      return `${t.andamento} a ${t.esfriando} dias desde a entrada: passou do prazo em que 75% dos ganhos já tinham fechado.`
    case "tardio":
      return `${t.esfriando} a ${t.tardio} dias desde a entrada: 95% dos ganhos já tinham fechado.`
    case "fora":
      return `Mais de ${t.tardio} dias desde a entrada: 99% dos ganhos já tinham fechado.`
  }
}

export function buildDetail(state: AppState, id: string): DetailDTO | null {
  const s = state.byId.get(id)
  if (!s) return null
  const d = s.deal
  return {
    id: d.id,
    stage: d.stage,
    product: d.product,
    agent: d.agent,
    region: d.region,
    account: d.account,
    score: s.score,
    rank: s.rank,
    nScored: state.scored.filter((x) => x.score !== null).length,
    state: s.state,
    age: s.age,
    thresholds: { ...s.thresholds, source: s.thresholdSource === "série" ? `série ${d.series}` : "base inteira" },
    situation: {
      label: STATE_META[s.state].label,
      meaning: meaningOf(s.state, s.thresholds),
      chance: s.situation.conversion ? s.situation.factor / s.situation.conversion : s.situation.factor,
      factor: s.situation.factor,
      reached: s.situation.reached,
      conversion:
        s.situation.conversion === null
          ? null
          : { c: s.situation.conversion, converted: state.conversion.converted, failed: state.conversion.failed },
    },
    factors: s.factors
      .filter((f) => Math.abs(f.factor - 1) >= ALWAYS)
      .map((f) => ({
        label: `${f.label} (${f.group})`,
        factor: f.factor,
        reason: `Na base, deals deste grupo ganharam ${fmtPct(f.rate)}, contra ${fmtPct(f.expected)} esperados; o ajuste pesa ${fmtPct(f.weight)} por ter ${fmtInt(f.n)} deals de histórico.`,
      })),
    urgency: s.urgency.factor - 1 >= ALWAYS ? { factor: s.urgency.factor, drop: s.urgency.drop, horizonDays: s.urgency.horizonDays } : null,
    value: { price: d.price, rho: s.rho, value: s.value },
    p: s.p,
    priority: s.priority,
    K: state.K,
  }
}
