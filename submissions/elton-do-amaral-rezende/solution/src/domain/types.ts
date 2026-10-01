export type DayKey = `${number}-${number}-${number}`;
export type OpenStage = 'Prospecting' | 'Engaging';
export type DealStage = OpenStage | 'Won' | 'Lost';
export type MissionStatus = 'pending' | 'completed' | 'deferred';

/** Contrato de scoring sem resultado, close_date ou close_value do candidato. */
export interface ScoringOpportunity {
  opportunityId: string;
  salesAgent: string;
  account: string | null;
  sector: string | null;
  product: string;
  originalProduct: string;
  stage: OpenStage;
  engageDate: DayKey | null;
  catalogPriceUsd: number | null;
}

export interface ScoreFactor {
  key: 'history' | 'engagementAge' | 'catalogValue';
  normalizedValue: number;
  contributionPoints: number;
  explanation: string;
  sampleSize: number | null;
  fallback: string | null;
}

export interface RankedOpportunity extends ScoringOpportunity {
  priorityScore: number;
  scoringVersion: string;
  asOfDate: DayKey;
  factors: ScoreFactor[];
  missingData: string[];
  nextAction: string;
}

export type MissionAction = {
  opportunityId: string;
  salesAgent: string;
  dayKey: DayKey;
} & (
  | { status: 'pending'; completedAt: null; deferredUntil: null }
  | { status: 'completed'; completedAt: string; deferredUntil: null }
  | { status: 'deferred'; completedAt: null; deferredUntil: DayKey }
);
