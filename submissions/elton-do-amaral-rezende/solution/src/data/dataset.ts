import prepared from './opportunities.generated.json';
import evaluation from './evaluation.generated.json';
import type { RankedOpportunity } from '../domain/types';
import type { SalesAgent, QualityReport } from '../domain/ingestion';

export const dataset = {
  datasetVersion: prepared.datasetVersion,
  asOfDate: prepared.asOfDate,
  opportunities: prepared.opportunities as RankedOpportunity[],
  agents: prepared.agents as SalesAgent[],
  quality: prepared.quality as QualityReport,
};
export const evaluationSummary = evaluation;
export const opportunityById = new Map(dataset.opportunities.map((o) => [o.opportunityId, o]));
