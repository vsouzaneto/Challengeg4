// Leitura da ordem que veio da API, sem regra nova: por onde começar e o primeiro bloco da lista.
import type { Group, Item, SellerPipeline, TeamPipeline } from "@/lib/contract";

type Pipeline = Pick<SellerPipeline | TeamPipeline, "groups" | "empty">;

/** O grupo por onde começar: o primeiro da ordem ou, se ele vier vazio, o que o back indicou em `start_with_group`. */
export function startGroup(pipeline: Pipeline): Group | null {
  if (pipeline.empty) return null;
  const first = pipeline.groups[0];
  if (!first) return null;
  if (first.items.length) return first;
  if (first.empty?.code !== "start_with_group") return null;
  const target = first.empty.params.group;
  return pipeline.groups.find((group) => group.state === target) ?? null;
}

/** O primeiro bloco da lista: o empate inteiro (mesmo produto e valor de tabela). Dentro dele a ordem
 * por ID é só estabilidade, então nenhum item é destacado sozinho. */
export function firstBlock(group: Group): Item[] {
  const first = group.items[0];
  if (!first) return [];
  return group.items.slice(0, first.sales_price !== null ? first.tie_size : 1);
}

/** Busca e filtros da lista. Descrevem o que a lista mostra (cadastro, produto, faixa, idade, início): nenhum muda a
 * ordem nem o grupo de uma oportunidade. Vivem na URL, e a conta ausente é só lacuna de cadastro. */
export type ListFilters = {
  q: string;
  account: "com" | "sem" | null;
  product: string | null;
  band: NonNullable<Item["value_band"]> | null;
  ageMin: number | null;
  ageMax: number | null;
  from: string | null;
  to: string | null;
};

export const NO_FILTERS: ListFilters = {
  q: "", account: null, product: null, band: null, ageMin: null, ageMax: null, from: null, to: null,
};

const BANDS = ["alto", "médio", "baixo"] as const;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const days = (value: string | null): number | null => {
  const n = value === null || value.trim() === "" ? NaN : Number(value);
  return Number.isInteger(n) && n >= 0 ? n : null;
};

export function parseFilters(params: URLSearchParams): ListFilters {
  const account = params.get("cliente");
  const band = params.get("faixa");
  const from = params.get("de");
  const to = params.get("ate");
  return {
    q: params.get("q") ?? "",
    account: account === "com" || account === "sem" ? account : null,
    product: params.get("produto") || null,
    band: BANDS.find((b) => b === band) ?? null,
    ageMin: days(params.get("idade_min")),
    ageMax: days(params.get("idade_max")),
    from: from && DATE.test(from) ? from : null,
    to: to && DATE.test(to) ? to : null,
  };
}

/** As chaves da URL de cada filtro; o valor vazio sai da URL. */
export function filtersToQuery(filters: ListFilters): Record<string, string | null> {
  return {
    q: filters.q.trim() || null,
    cliente: filters.account,
    produto: filters.product,
    faixa: filters.band,
    idade_min: filters.ageMin === null ? null : String(filters.ageMin),
    idade_max: filters.ageMax === null ? null : String(filters.ageMax),
    de: filters.from,
    ate: filters.to,
  };
}

/** Quantos filtros além da busca estão ativos. */
export const activeFilterCount = (filters: ListFilters): number =>
  [filters.account, filters.product, filters.band, filters.ageMin, filters.ageMax, filters.from, filters.to]
    .filter((value) => value !== null).length;

export const hasFilters = (filters: ListFilters): boolean => filters.q.trim() !== "" || activeFilterCount(filters) > 0;

/** Sem acento e sem maiúsculas, para a busca achar "Açaí" digitando "acai". */
const plain = (text: string): string => text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

export function matches(item: Item, filters: ListFilters): boolean {
  const query = plain(filters.q.trim());
  if (query && !plain([item.opportunity_id, item.product, item.account, item.sales_agent].filter(Boolean).join(" ")).includes(query)) {
    return false;
  }
  if (filters.account && (item.account !== null) !== (filters.account === "com")) return false;
  if (filters.product && item.product !== filters.product) return false;
  if (filters.band && item.value_band !== filters.band) return false;
  if (filters.ageMin !== null && (item.age_days === null || item.age_days < filters.ageMin)) return false;
  if (filters.ageMax !== null && (item.age_days === null || item.age_days > filters.ageMax)) return false;
  if (filters.from && (item.engage_date === null || item.engage_date < filters.from)) return false;
  if (filters.to && (item.engage_date === null || item.engage_date > filters.to)) return false;
  return true;
}

/** Mantém só as oportunidades que passam na busca e nos filtros; grupos e ordem seguem os da API. */
export function filterGroups(groups: Group[], filters: ListFilters): Group[] {
  if (!hasFilters(filters)) return groups;
  return groups.map((group) => {
    const items = group.items.filter((item) => matches(item, filters));
    return { ...group, items, count: items.length };
  });
}

/** Os produtos que aparecem na lista, em ordem alfabética, para o filtro de produto. */
export const productsIn = (groups: Group[]): string[] =>
  [...new Set(groups.flatMap((group) => group.items.map((item) => item.product).filter((p): p is string => Boolean(p))))]
    .sort((a, b) => a.localeCompare(b, "pt-BR"));

/** Aba inicial: o grupo por onde começar; sem ele, o primeiro da ordem. */
export const defaultTab = (pipeline: Pipeline): Group["state"] | undefined =>
  startGroup(pipeline)?.state ?? pipeline.groups[0]?.state;
