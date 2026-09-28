import { parseCsv } from "./csv.ts"

// Nomes de estágio que têm significado para o modelo. Os demais são tratados como "aberto".
export const WON_STAGE = "Won"
export const LOST_STAGE = "Lost"
// Ordem do funil nas raias; estágios desconhecidos entram antes de Won, na ordem em que aparecem.
export const FUNNEL = ["Prospecting", "Engaging", WON_STAGE, LOST_STAGE]

export interface ProductInfo {
  name: string
  series: string | null
  price: number
}

export interface AgentInfo {
  name: string
  manager: string | null
  region: string | null
}

export interface AccountInfo {
  name: string
  sector: string | null
  employees: number | null
  revenue: number | null
  location: string | null
}

export interface Deal {
  id: string
  stage: string
  agent: string
  manager: string | null
  region: string | null
  product: string // nome canônico do catálogo quando reconhecido; senão o nome bruto
  series: string | null
  price: number | null
  account: string | null
  engage: number | null // dia (epoch) de entrada em Engaging
  close: number | null // dia (epoch) de fechamento
  closeValue: number | null
  outcome: "won" | "lost" | null
}

export interface DataIssue {
  id: string
  label: string
  count: number
  examples: string[]
  // "bloqueia" = impede o score do deal; "tarefa" = vira pendência de cadastro
  impact: "bloqueia" | "tarefa" | "info"
}

export interface Dataset {
  deals: Deal[]
  products: Map<string, ProductInfo>
  agents: Map<string, AgentInfo>
  accounts: Map<string, AccountInfo>
  refDay: number // data de referência = data mais recente da base
  issues: DataIssue[]
  lanes: string[]
}

export interface RawFiles {
  accounts: string
  products: string
  sales_teams: string
  sales_pipeline: string
}

export const REQUIRED_COLUMNS: Record<keyof RawFiles, string[]> = {
  accounts: ["account"],
  products: ["product", "sales_price"],
  sales_teams: ["sales_agent"],
  sales_pipeline: ["opportunity_id", "sales_agent", "product", "deal_stage"],
}

export class DataError extends Error {}

const DAY_MS = 86_400_000

export function parseDay(s: string | undefined): number | null {
  const m = s?.match(/^(\d{4})-(\d{2})-(\d{2})/)
  return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) / DAY_MS : null
}

export function formatDay(day: number): string {
  return new Date(day * DAY_MS).toISOString().slice(0, 10)
}

export function monthOfQuarter(day: number): number {
  return (new Date(day * DAY_MS).getUTCMonth() % 3) + 1
}

// Chave de comparação tolerante a grafia: "GTXPro" e "GTX Pro" viram "gtxpro".
export const canonical = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "")

const num = (s: string | undefined) => {
  if (s === undefined || s.trim() === "") return null
  const n = Number(s)
  return Number.isFinite(n) ? n : null
}
const text = (s: string | undefined) => (s && s.trim() !== "" ? s.trim() : null)

export function prepareDataset(files: RawFiles): Dataset {
  const tables = Object.fromEntries(
    (Object.keys(REQUIRED_COLUMNS) as (keyof RawFiles)[]).map((name) => {
      const rows = parseCsv(files[name])
      const missing = REQUIRED_COLUMNS[name].filter((c) => rows.length && !(c in rows[0]))
      if (!rows.length) throw new DataError(`${name}.csv está vazio ou sem cabeçalho.`)
      if (missing.length) throw new DataError(`${name}.csv sem as colunas: ${missing.join(", ")}.`)
      return [name, rows]
    }),
  ) as Record<keyof RawFiles, Record<string, string>[]>

  const products = new Map<string, ProductInfo>()
  for (const r of tables.products) {
    const price = num(r.sales_price)
    if (price === null) continue
    products.set(canonical(r.product), { name: r.product, series: text(r.series), price })
  }
  const agents = new Map<string, AgentInfo>()
  for (const r of tables.sales_teams) {
    agents.set(r.sales_agent, { name: r.sales_agent, manager: text(r.manager), region: text(r.regional_office) })
  }
  const accounts = new Map<string, AccountInfo>()
  for (const r of tables.accounts) {
    accounts.set(r.account, {
      name: r.account,
      sector: text(r.sector),
      employees: num(r.employees),
      revenue: num(r.revenue),
      location: text(r.office_location),
    })
  }

  const issues = new Map<string, DataIssue>()
  const note = (id: string, label: string, impact: DataIssue["impact"], example: string) => {
    const it = issues.get(id) ?? { id, label, impact, count: 0, examples: [] }
    it.count++
    if (it.examples.length < 3) it.examples.push(example)
    issues.set(id, it)
  }

  const seen = new Set<string>()
  const deals: Deal[] = []
  for (const r of tables.sales_pipeline) {
    const id = r.opportunity_id
    if (!id || seen.has(id)) {
      note("duplicado", "Oportunidade sem ID ou duplicada (ignorada)", "bloqueia", id || "(vazio)")
      continue
    }
    seen.add(id)
    const stage = r.deal_stage || "(sem estágio)"
    const product = products.get(canonical(r.product))
    const agent = agents.get(r.sales_agent)
    const engage = parseDay(r.engage_date)
    let close = parseDay(r.close_date)
    const outcome = stage === WON_STAGE ? "won" : stage === LOST_STAGE ? "lost" : null

    if (!product) note("produto", "Produto fora do catálogo (sem preço, sem score)", "bloqueia", `${id}: ${r.product}`)
    else if (product.name !== r.product) note("grafia_produto", "Produto com grafia diferente do catálogo (corrigido)", "info", `${r.product} → ${product.name}`)
    if (!agent) note("vendedor", "Vendedor sem cadastro no time (sem região/manager)", "tarefa", `${id}: ${r.sales_agent}`)
    if (!text(r.account)) note("conta", "Oportunidade sem conta vinculada", "tarefa", id)
    if (outcome && close === null) note("sem_fechamento", "Encerrada sem data de fechamento (fora do aprendizado)", "info", id)
    if (!outcome && engage === null) note("sem_entrada", "Aberta sem data de entrada (idade desconhecida)", "tarefa", id)
    if (engage !== null && close !== null && close < engage) {
      note("datas", "Fechamento antes da entrada (datas ignoradas)", "info", id)
      close = null
    }

    deals.push({
      id,
      stage,
      agent: r.sales_agent,
      manager: agent?.manager ?? null,
      region: agent?.region ?? null,
      product: product?.name ?? r.product,
      series: product?.series ?? null,
      price: product?.price ?? null,
      account: text(r.account),
      engage,
      close: outcome ? close : null,
      closeValue: num(r.close_value),
      outcome,
    })
  }
  if (!deals.length) throw new DataError("sales_pipeline.csv não tem oportunidades válidas.")

  let refDay = -Infinity
  for (const d of deals) refDay = Math.max(refDay, d.engage ?? -Infinity, d.close ?? -Infinity)
  if (!Number.isFinite(refDay)) throw new DataError("Nenhuma data válida em sales_pipeline.csv.")

  const extra = [...new Set(deals.map((d) => d.stage))].filter((s) => !FUNNEL.includes(s))
  const present = new Set(deals.map((d) => d.stage))
  const lanes = [
    ...FUNNEL.slice(0, 2).filter((s) => present.has(s)),
    ...extra,
    ...FUNNEL.slice(2).filter((s) => present.has(s)),
  ]

  return { deals, products, agents, accounts, refDay, issues: [...issues.values()], lanes }
}
