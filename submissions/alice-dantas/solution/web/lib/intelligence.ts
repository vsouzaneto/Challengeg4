// Inteligência comercial: o recorte na URL e na chamada, e apoios de apresentação. Nenhum número é
// calculado aqui: taxas, fatias e decomposições chegam prontas da API (ADR-004).
import type { ClosedMetrics, Intelligence, IntelligenceDeals, IntelligenceFilter } from "@/lib/contract";

export type Dimension = Intelligence["breakdowns"][number]["dimension"];
export type DealOutcome = IntelligenceDeals["outcome"];
export type FilterKey = keyof IntelligenceFilter;

/** Nome de cada filtro na URL, em português como na Equipe. As dimensões têm os mesmos nomes dos filtros. */
export const QUERY_KEYS: Record<FilterKey, string> = {
  product: "produto", seller: "vendedor", manager: "gerente", office: "escritorio", sector: "setor",
  account: "cliente", size: "porte",
};
export const FILTER_KEYS = Object.keys(QUERY_KEYS) as FilterKey[];

export const emptyFilter = (): IntelligenceFilter =>
  Object.fromEntries(FILTER_KEYS.map((key) => [key, null])) as IntelligenceFilter;

export const filterFromQuery = (query: URLSearchParams): IntelligenceFilter =>
  Object.fromEntries(FILTER_KEYS.map((key) => [key, query.get(QUERY_KEYS[key]) || null])) as IntelligenceFilter;

/** Mudanças de filtro como parâmetros da URL (nulo apaga). */
export const queryChanges = (changes: Partial<IntelligenceFilter>): Record<string, string | null> =>
  Object.fromEntries(Object.entries(changes).map(([key, value]) => [QUERY_KEYS[key as FilterKey], value ?? null]));

export function apiQuery(filter: IntelligenceFilter): URLSearchParams {
  const query = new URLSearchParams();
  for (const key of FILTER_KEYS) if (filter[key]) query.set(key, filter[key] as string);
  return query;
}

export const activeFilters = (filter: IntelligenceFilter): FilterKey[] => FILTER_KEYS.filter((key) => filter[key]);

/** O recorte da página mais um segmento clicado (linha da tabela ou célula da matriz). */
export const withSegment = (filter: IntelligenceFilter, segment: Partial<IntelligenceFilter>): IntelligenceFilter =>
  ({ ...filter, ...segment });

/** A Equipe só filtra por gerente e escritório: o atalho para ela só vale nesse recorte. */
export const teamScopeOnly = (filter: IntelligenceFilter): boolean =>
  activeFilters(filter).every((key) => key === "manager" || key === "office");

export function teamHref(filter: IntelligenceFilter, group: string): string {
  const query = new URLSearchParams({ visao: "oportunidades", grupo: group });
  if (filter.manager) query.set("gerente", filter.manager);
  if (filter.office) query.set("escritorio", filter.office);
  return `/equipe?${query}`;
}

/** Os clientes que o filtro de setor deixa escolher. */
export const accountChoices = (options: Intelligence["options"], sector: string | null): string[] =>
  options.accounts.filter((account) => !sector || account.sector === sector).map((account) => account.name);

/** Intensidade da célula da matriz pela fatia que veio da API (0 = vazia). A cor só acompanha o número. */
export function heatLevel(share: number | null): 0 | 1 | 2 | 3 | 4 {
  if (!share) return 0;
  if (share < 0.1) return 1;
  if (share < 0.2) return 2;
  if (share < 0.35) return 3;
  return 4;
}

/** Métricas do histórico que o gráfico do Explore mostra. */
export const METRICS = ["revenue", "won", "win_rate", "ticket", "revenue_per_closed", "median_won_cycle_days"] as const;
export type MetricKey = (typeof METRICS)[number];

/** O valor da métrica como veio da API (a taxa de ganho é o `value` da faixa). */
export const metricValue = (history: ClosedMetrics, metric: MetricKey): number | null =>
  metric === "win_rate" ? history.win_rate?.value ?? null : history[metric];
