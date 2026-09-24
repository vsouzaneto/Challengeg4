import { addFactorReasons, buildJustification, classifyFactor, type FactorDraft } from "./explanation.js";
import type { ScoreResult, ScoringOpportunity } from "./types.js";

interface BuyerProfile {
  accountId: number;
  employees: number | null;
  revenue: number | null;
  wins: Array<{ id: string; closeDate: string }>;
}

export interface ScoringContext {
  exact: Map<string, ScoringOpportunity[]>;
  series: Map<string, ScoringOpportunity[]>;
  sector: Map<string, ScoringOpportunity[]>;
  buyersByProduct: Map<string, Map<number, BuyerProfile>>;
}

function isClosed(opportunity: ScoringOpportunity): boolean {
  return (opportunity.dealStage === "Won" || opportunity.dealStage === "Lost") && opportunity.closeDate !== null;
}

function key(...parts: Array<string | number | null>): string {
  return parts.map((part) => part ?? "∅").join("::");
}

function mergeBuyer(map: Map<number, BuyerProfile>, opportunity: ScoringOpportunity, closeDate: string): void {
  if (opportunity.accountId === null) {
    return;
  }
  const current = map.get(opportunity.accountId);
  map.set(opportunity.accountId, {
    accountId: opportunity.accountId,
    employees: opportunity.employees ?? current?.employees ?? null,
    revenue: opportunity.revenue ?? current?.revenue ?? null,
    wins: [...current?.wins ?? [], { id: opportunity.id, closeDate }],
  });
}

export function createScoringContext(opportunities: ScoringOpportunity[]): ScoringContext {
  const exact = new Map<string, ScoringOpportunity[]>();
  const series = new Map<string, ScoringOpportunity[]>();
  const sector = new Map<string, ScoringOpportunity[]>();
  const buyersByProduct = new Map<string, Map<number, BuyerProfile>>();

  for (const opportunity of opportunities) {
    if (!isClosed(opportunity) || !opportunity.closeDate) {
      continue;
    }

    const exactKey = key(opportunity.accountId, opportunity.product);
    const exactRows = exact.get(exactKey) ?? [];
    exactRows.push(opportunity);
    exact.set(exactKey, exactRows);

    if (opportunity.accountId !== null && opportunity.series) {
      const seriesKey = key(opportunity.accountId, opportunity.series);
      const seriesRows = series.get(seriesKey) ?? [];
      seriesRows.push(opportunity);
      series.set(seriesKey, seriesRows);
    }

    if (opportunity.sector) {
      const sectorKey = key(opportunity.product, opportunity.sector);
      const sectorRows = sector.get(sectorKey) ?? [];
      sectorRows.push(opportunity);
      sector.set(sectorKey, sectorRows);
    }

    if (opportunity.dealStage === "Won") {
      const buyers = buyersByProduct.get(opportunity.product) ?? new Map<number, BuyerProfile>();
      mergeBuyer(buyers, opportunity, opportunity.closeDate);
      buyersByProduct.set(opportunity.product, buyers);
    }
  }

  return { exact, series, sector, buyersByProduct };
}

function eligible(opportunities: ScoringOpportunity[], target: ScoringOpportunity, referenceDate: string): ScoringOpportunity[] {
  return opportunities.filter(
    (opportunity) => opportunity.id !== target.id && opportunity.closeDate !== null && opportunity.closeDate.slice(0, 10) < referenceDate,
  );
}

function historicalCounts(opportunities: ScoringOpportunity[]) {
  return opportunities.reduce(
    (counts, opportunity) => {
      if (opportunity.dealStage === "Won") {
        counts.won += 1;
      } else if (opportunity.dealStage === "Lost") {
        counts.lost += 1;
      }
      return counts;
    },
    { won: 0, lost: 0 },
  );
}

function similarity(value: number | null, reference: number | null): number {
  if (value === null || reference === null || value <= 0 || reference <= 0) {
    return 0;
  }
  return Math.min(value, reference) / Math.max(value, reference);
}

export function median(values: number[]): number {
  if (values.length === 0) {
    return 0;
  }
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 0) {
    return ((sorted[middle - 1] ?? 0) + (sorted[middle] ?? 0)) / 2;
  }
  return sorted[middle] ?? 0;
}

export function percentile(values: number[], fraction: number): number {
  if (values.length === 0) {
    return 0;
  }
  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * fraction;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  const lowerValue = sorted[lower] ?? 0;
  const upperValue = sorted[upper] ?? 0;
  if (lower === upper) {
    return lowerValue;
  }
  return lowerValue + (upperValue - lowerValue) * (position - lower);
}

function factor(id: FactorDraft["id"], label: string, points: number, maxPoints: number, evidence: FactorDraft["evidence"]): FactorDraft {
  const safePoints = Number.isFinite(points) ? Math.max(0, Math.min(maxPoints, points)) : 0;
  return {
    id,
    label,
    points: safePoints,
    maxPoints,
    strength: classifyFactor(safePoints, maxPoints),
    evidence,
  };
}

export function calculateScore(
  target: ScoringOpportunity,
  opportunities: ScoringOpportunity[],
  referenceDate: string,
  calculatedAt: string,
  context = createScoringContext(opportunities),
): ScoreResult {
  const exactHistory = eligible(context.exact.get(key(target.accountId, target.product)) ?? [], target, referenceDate);
  const exactCounts = historicalCounts(exactHistory);
  const exactTotal = exactCounts.won + exactCounts.lost;
  const exactFit = exactCounts.won / (exactTotal + 3);

  const relatedSeries = target.accountId !== null && target.series
    ? eligible(context.series.get(key(target.accountId, target.series)) ?? [], target, referenceDate)
      .filter((opportunity) => opportunity.product !== target.product)
    : [];
  const seriesCounts = historicalCounts(relatedSeries);
  const seriesTotal = seriesCounts.won + seriesCounts.lost;
  const seriesFit = seriesCounts.won / (seriesTotal + 5);
  const accountProductPoints = target.accountId === null ? 0 : 35 * (0.7 * exactFit + 0.3 * seriesFit);

  const sectorHistory = target.sector
    ? eligible(context.sector.get(key(target.product, target.sector)) ?? [], target, referenceDate)
    : [];
  const sectorCounts = historicalCounts(sectorHistory);
  const sectorTotal = sectorCounts.won + sectorCounts.lost;
  const sectorProductPoints = target.sector ? 30 * (sectorCounts.won / (sectorTotal + 10)) : 0;

  const buyers = [...(context.buyersByProduct.get(target.product)?.values() ?? [])].filter((buyer) =>
    buyer.wins.some((win) => win.id !== target.id && win.closeDate < referenceDate),
  );
  const employeeValues = buyers.flatMap((buyer) => buyer.employees === null ? [] : [buyer.employees]);
  const revenueValues = buyers.flatMap((buyer) => buyer.revenue === null ? [] : [buyer.revenue]);
  const medianEmployees = median(employeeValues);
  const medianRevenue = median(revenueValues);
  const employeeSimilarity = similarity(target.employees, medianEmployees || null);
  const revenueSimilarity = similarity(target.revenue, medianRevenue || null);
  const companyProfilePoints = 10 * employeeSimilarity + 10 * revenueSimilarity;

  const revenueBuyers = revenueValues.filter((value) => value > 0);
  const q1 = percentile(revenueBuyers, 0.25);
  const q3 = percentile(revenueBuyers, 0.75);
  const financialFit = target.revenue === null || target.revenue <= 0 || revenueBuyers.length < 4
    ? 0
    : target.revenue < q1
      ? q1 > 0 ? target.revenue / q1 : 0
      : target.revenue > q3
        ? q3 > 0 ? q3 / target.revenue : 0
        : 1;
  const financialPoints = 15 * financialFit;

  const factors = addFactorReasons([
    factor("account_product_fit", "Produto × cliente", accountProductPoints, 35, {
      account: target.accountName,
      evidenceState: target.accountId === null
        ? "missing_account"
        : exactTotal + seriesTotal === 0 ? "no_historical_evidence" : "calculated",
      exactWon: exactCounts.won,
      exactLost: exactCounts.lost,
      exactTotal,
      exactFit,
      series: target.series,
      seriesWon: seriesCounts.won,
      seriesLost: seriesCounts.lost,
      seriesTotal,
      seriesFit,
    }),
    factor("sector_product_fit", "Produto × setor", sectorProductPoints, 30, {
      sector: target.sector,
      evidenceState: !target.sector ? "missing_sector" : sectorTotal === 0 ? "no_historical_evidence" : "calculated",
      won: sectorCounts.won,
      lost: sectorCounts.lost,
      sampleSize: sectorTotal,
      fit: sectorCounts.won / (sectorTotal + 10),
    }),
    factor("company_profile_fit", "Perfil da empresa", companyProfilePoints, 20, {
      evidenceState: target.employees === null && target.revenue === null
        ? "missing_target_data"
        : employeeValues.length + revenueValues.length === 0 ? "no_historical_evidence" : "calculated",
      employeeEvidenceState: target.employees === null
        ? "missing_target_data"
        : employeeValues.length === 0 ? "no_historical_evidence" : "calculated",
      revenueEvidenceState: target.revenue === null
        ? "missing_target_data"
        : revenueValues.length === 0 ? "no_historical_evidence" : "calculated",
      targetEmployees: target.employees,
      targetRevenue: target.revenue,
      medianEmployees: medianEmployees || null,
      medianRevenue: medianRevenue || null,
      employeeSimilarity,
      revenueSimilarity,
      employeeContribution: 10 * employeeSimilarity,
      revenueContribution: 10 * revenueSimilarity,
    }),
    factor("financial_fit", "Compatibilidade financeira", financialPoints, 15, {
      evidenceState: target.revenue === null
        ? "missing_target_data"
        : revenueBuyers.length < 4 ? "insufficient_history" : "calculated",
      targetRevenue: target.revenue,
      q1: revenueBuyers.length >= 4 ? q1 : null,
      q3: revenueBuyers.length >= 4 ? q3 : null,
      sampleSize: revenueBuyers.length,
      financialFit,
    }),
  ]);

  const rawScore = factors.reduce((total, current) => total + current.points, 0);
  const boundedScore = Math.min(100, Math.max(0, rawScore));
  const score = Math.round(boundedScore);
  return {
    opportunityId: target.id,
    score,
    rawScore,
    factors,
    justification: buildJustification(score, factors),
    calculatedAt,
  };
}
