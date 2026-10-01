/** Dois relógios: referência histórica do score e calendário real das ações. */
export const SCORING_AS_OF_DATE = '2017-12-31';
export const OPERATIONAL_TIME_ZONE = 'America/Sao_Paulo';
export const DAILY_GOAL = 10;
export const BATCH_SIZE = 10;
export const STORAGE_SCHEMA_VERSION = 1;

/** Hipótese inicial; congelar antes da avaliação final. */
export const SCORING_RULE = {
  version: 'candidate-v1',
  weights: { history: 0.65, engagementAge: 0.25, catalogValue: 0.10 },
  historicalWeights: { product: 0.50, sector: 0.30, account: 0.20 },
  smoothing: 20,
} as const;
