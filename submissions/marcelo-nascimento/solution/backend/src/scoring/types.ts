export type DealStage = "Prospecting" | "Engaging" | "Won" | "Lost";

export interface ScoringOpportunity {
  id: string;
  dealStage: DealStage;
  productId: number;
  product: string;
  series: string | null;
  salesPrice: number | null;
  accountId: number | null;
  accountName: string | null;
  sector: string | null;
  employees: number | null;
  revenue: number | null;
  salesAgentId: number;
  salesAgent: string;
  manager: string | null;
  regionalOffice: string | null;
  engageDate: string | null;
  closeDate: string | null;
  closeValue: number | null;
}

export type EvidenceValue = string | number | boolean | null;
export type ScoreEvidence = Record<string, EvidenceValue>;

export type FactorId =
  | "account_product_fit"
  | "sector_product_fit"
  | "company_profile_fit"
  | "financial_fit";

export type EvidenceStrength = "forte" | "moderada" | "fraca" | "sem evidência";

export interface ScoreFactor {
  id: FactorId;
  label: string;
  points: number;
  maxPoints: number;
  strength: EvidenceStrength;
  reason: string;
  evidence: ScoreEvidence;
}

export interface ScoreResult {
  opportunityId: string;
  score: number;
  rawScore: number;
  factors: ScoreFactor[];
  justification: string;
  calculatedAt: string;
}

export interface ScoredOpportunity extends ScoringOpportunity {
  scoreResult: ScoreResult;
  isHotLead: boolean;
}
