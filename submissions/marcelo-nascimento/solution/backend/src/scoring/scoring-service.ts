import { pool } from "../database/pool.js";
import { createScoringContext, calculateScore } from "./scoring.js";
import type { DealStage, ScoreResult, ScoredOpportunity, ScoringOpportunity } from "./types.js";

interface OpportunityRow {
  id: string;
  deal_stage: DealStage;
  product_id: number;
  product: string;
  series: string | null;
  sales_price: string | null;
  account_id: number | null;
  account_name: string | null;
  sector: string | null;
  employees: number | null;
  revenue: string | null;
  sales_agent_id: number;
  sales_agent: string;
  manager: string | null;
  regional_office: string | null;
  engage_date: string | null;
  close_date: string | null;
  close_value: string | null;
}

function optionalNumber(value: string | null): number | null {
  if (value === null || value === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function mapOpportunity(row: OpportunityRow): ScoringOpportunity {
  return {
    id: row.id,
    dealStage: row.deal_stage,
    productId: row.product_id,
    product: row.product,
    series: row.series,
    salesPrice: optionalNumber(row.sales_price),
    accountId: row.account_id,
    accountName: row.account_name,
    sector: row.sector,
    employees: row.employees,
    revenue: optionalNumber(row.revenue),
    salesAgentId: row.sales_agent_id,
    salesAgent: row.sales_agent,
    manager: row.manager,
    regionalOffice: row.regional_office,
    engageDate: row.engage_date,
    closeDate: row.close_date,
    closeValue: optionalNumber(row.close_value),
  };
}

export async function loadScoringOpportunities(): Promise<ScoringOpportunity[]> {
  const { rows } = await pool.query<OpportunityRow>(
    `SELECT
       o.id,
       o.deal_stage,
       o.product_id,
       p.name AS product,
       p.series,
       p.sales_price::text AS sales_price,
       a.id AS account_id,
       a.name AS account_name,
       a.sector,
       a.employees,
       a.revenue::text AS revenue,
       s.id AS sales_agent_id,
       s.name AS sales_agent,
       s.manager,
       s.regional_office,
       TO_CHAR(o.engage_date, 'YYYY-MM-DD') AS engage_date,
       TO_CHAR(o.close_date, 'YYYY-MM-DD') AS close_date,
       o.close_value::text AS close_value
     FROM opportunities o
     JOIN products p ON p.id = o.product_id
     JOIN sales_agents s ON s.id = o.sales_agent_id
     LEFT JOIN accounts a ON a.id = o.account_id
     ORDER BY o.id`,
  );
  return rows.map(mapOpportunity);
}

function defaultReferenceDate(opportunity: ScoringOpportunity): string {
  if ((opportunity.dealStage === "Won" || opportunity.dealStage === "Lost") && opportunity.closeDate) {
    return opportunity.closeDate;
  }
  return new Date().toISOString().slice(0, 10);
}

export function scoreOpportunities(
  opportunities: ScoringOpportunity[],
  calculatedAt = new Date().toISOString(),
  referenceDate?: string,
  history: ScoringOpportunity[] = opportunities,
): ScoredOpportunity[] {
  const context = createScoringContext(history);
  return opportunities.map((opportunity) => {
    const effectiveReferenceDate = referenceDate ?? defaultReferenceDate(opportunity);
    const scoreResult: ScoreResult = calculateScore(
      opportunity,
      opportunities,
      effectiveReferenceDate,
      calculatedAt,
      context,
    );
    return {
      ...opportunity,
      scoreResult,
      isHotLead: scoreResult.score >= 75,
    };
  });
}

export async function getScoredOpportunities(options: { ids?: string[]; referenceDate?: string } = {}): Promise<ScoredOpportunity[]> {
  const opportunities = await loadScoringOpportunities();
  const selected = options.ids
    ? opportunities.filter((opportunity) => options.ids?.includes(opportunity.id))
    : opportunities;
  return scoreOpportunities(selected, new Date().toISOString(), options.referenceDate, opportunities);
}
