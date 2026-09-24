// Presentation split of reason codes (docs/revops-review.md §1): context codes are informative
// (weight zero, direction `i`) and are shown apart from the factors that build the score.
// No weights are computed here; the API's numbers are only grouped and formatted.
import type { Reason, ScoredDeal } from '../api/client';

export const SCORE_CODES = new Set<Reason['code']>([
  'PRODUCT_BASE_RATE',
  'HIGH_TICKET',
  'LOW_TICKET',
  'ZOMBIE_RISK',
]);

export const CONTEXT_CODES = new Set<Reason['code']>([
  'AGENT_TRACK_RECORD',
  'AGENT_PRODUCT_FIT',
  'SECTOR_FIT',
  'ACCOUNT_SIZE',
  'ACCOUNT_HISTORY',
  'ACCOUNT_UNKNOWN',
  'SURVIVAL_POSITIVE',
  'PROSPECTING_NO_TIMELINE',
  'AGENT_OVERLOAD',
]);

/** Context codes are always rendered as informative, whatever direction the payload carries. */
export function asContext(r: Reason): Reason {
  return CONTEXT_CODES.has(r.code) ? { ...r, direction: 'i', weight: 0 } : r;
}

export function splitReasons(reasons: Reason[], showModel: boolean) {
  const score: Reason[] = [];
  const context: Reason[] = [];
  for (const r of reasons) {
    if (r.code === 'MODEL_CONTRIBUTION') {
      if (showModel) score.push(r);
      continue;
    }
    if (CONTEXT_CODES.has(r.code)) context.push(asContext(r));
    else score.push(r);
  }
  return { score, context };
}

/** Main reason for the row: the strongest score factor, else the first context line. */
export function mainReason(deal: ScoredDeal): Reason | undefined {
  const { score, context } = splitReasons(deal.reasons, false);
  return score[0] ?? context[0];
}

/** Zombie threshold: the longest cycle ever closed (scoring-spec §4); the API also exposes it as
 * `PipelineSummary.zombie_threshold_days`. */
export const ZOMBIE_DAYS = 138;
/** Cooling window start (p90 of the Won cycle). */
export const COOLING_DAYS = 100;

export type QueueKind = 'work' | 'confirm';

export function isStale(deal: ScoredDeal): boolean {
  return (deal.days_in_engaging ?? 0) > ZOMBIE_DAYS;
}
export function isCooling(deal: ScoredDeal): boolean {
  const d = deal.days_in_engaging ?? 0;
  return d > COOLING_DAYS && d <= ZOMBIE_DAYS;
}

export const AGE_BANDS: { label: string; min: number; max: number }[] = [
  { label: '139–180 dias', min: 139, max: 180 },
  { label: '181–240 dias', min: 181, max: 240 },
  { label: '241–300 dias', min: 241, max: 300 },
  { label: 'acima de 300 dias', min: 301, max: Infinity },
];

export function ageBand(days: number) {
  return AGE_BANDS.find((b) => days >= b.min && days <= b.max) ?? AGE_BANDS[AGE_BANDS.length - 1]!;
}
