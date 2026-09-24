import type { ScoredOpportunity } from "./scoring/types.js";

export interface OpportunityFilters {
  search?: string;
  stage?: string;
  product?: string;
  sector?: string;
  seller?: string;
  scoreBand?: string;
}

export type OpportunitySort = "score" | "account" | "product" | "stage";
export type SortOrder = "asc" | "desc";

export const scoreBands = [
  { id: "0-24", label: "0–24", min: 0, max: 24 },
  { id: "25-49", label: "25–49", min: 25, max: 49 },
  { id: "50-74", label: "50–74", min: 50, max: 74 },
  { id: "75-100", label: "75–100", min: 75, max: 100 },
] as const;

export function roundOne(value: number): number {
  return Math.round(value * 10) / 10;
}

export function opportunityBand(score: number): string {
  return scoreBands.find((band) => score >= band.min && score <= band.max)?.id ?? "0-24";
}

export function applyOpportunityFilters(items: ScoredOpportunity[], filters: OpportunityFilters): ScoredOpportunity[] {
  const search = filters.search?.trim().toLocaleLowerCase("pt-BR");
  return items.filter((item) => {
    if (search) {
      const searchable = `${item.accountName ?? ""} ${item.product}`.toLocaleLowerCase("pt-BR");
      if (!searchable.includes(search)) {
        return false;
      }
    }
    if (filters.stage && item.dealStage !== filters.stage) {
      return false;
    }
    if (filters.product && item.product !== filters.product) {
      return false;
    }
    if (filters.sector && (filters.sector === "unknown" ? item.sector !== null : item.sector !== filters.sector)) {
      return false;
    }
    if (filters.seller && item.salesAgent !== filters.seller) {
      return false;
    }
    if (filters.scoreBand && opportunityBand(item.scoreResult.score) !== filters.scoreBand) {
      return false;
    }
    return true;
  });
}

export function sortOpportunities(
  items: ScoredOpportunity[],
  sort: OpportunitySort,
  order: SortOrder,
): ScoredOpportunity[] {
  const direction = order === "asc" ? 1 : -1;
  return [...items].sort((left, right) => {
    let comparison = 0;
    if (sort === "score") {
      comparison = left.scoreResult.score - right.scoreResult.score;
    } else if (sort === "account") {
      comparison = (left.accountName ?? "").localeCompare(right.accountName ?? "", "pt-BR");
    } else if (sort === "product") {
      comparison = left.product.localeCompare(right.product, "pt-BR");
    } else {
      comparison = left.dealStage.localeCompare(right.dealStage, "pt-BR");
    }
    return comparison === 0 ? left.id.localeCompare(right.id) : comparison * direction;
  });
}

export function scoreDistribution(items: ScoredOpportunity[]) {
  return scoreBands.map((band) => ({
    id: band.id,
    label: band.label,
    count: items.filter((item) => opportunityBand(item.scoreResult.score) === band.id).length,
  }));
}

export function average(items: ScoredOpportunity[]): number | null {
  if (items.length === 0) {
    return null;
  }
  return roundOne(items.reduce((total, item) => total + item.scoreResult.score, 0) / items.length);
}

export function groupAverages(items: ScoredOpportunity[], keySelector: (item: ScoredOpportunity) => string) {
  const groups = new Map<string, ScoredOpportunity[]>();
  for (const item of items) {
    const key = keySelector(item);
    const group = groups.get(key) ?? [];
    group.push(item);
    groups.set(key, group);
  }
  return [...groups.entries()]
    .map(([name, group]) => ({ name, count: group.length, averageScore: average(group) }))
    .sort((left, right) => (right.averageScore ?? 0) - (left.averageScore ?? 0) || left.name.localeCompare(right.name, "pt-BR"));
}
