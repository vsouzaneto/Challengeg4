import type { Opportunity } from './ingestion';
import type { DayKey } from './types';
import { historicalStats, scoreOpportunity, scoringCandidate } from './scoring/engine';

export const EVALUATION_CUTOFF: DayKey = '2017-09-30';
export const EVALUATION_HORIZON: DayKey = '2017-12-31';
export const RANDOM_SEED = 20260930;
export const METHODS = ['priority', 'without-value', 'without-age', 'catalog-price', 'recent-engagement', 'random'] as const;
export type EvaluationMethod = typeof METHODS[number];
export function historicalCandidates(opportunities: Opportunity[], cutoff: DayKey) {
  return opportunities.filter((o) => o.engageDate !== null && o.engageDate <= cutoff && (o.closeDate === null || o.closeDate > cutoff));
}
export function outcome(o: Opportunity, horizon: DayKey): 'Won' | 'Lost' | 'Censored' {
  return o.closeDate && o.closeDate <= horizon && (o.stage === 'Won' || o.stage === 'Lost') ? o.stage : 'Censored';
}
export function evaluate(opportunities: Opportunity[], prices: number[], cutoff = EVALUATION_CUTOFF, horizon = EVALUATION_HORIZON) {
  const candidates = historicalCandidates(opportunities, cutoff), stats = historicalStats(opportunities, cutoff);
  const agents = [...new Set(candidates.map((o) => o.salesAgent))].sort();
  let randomState = RANDOM_SEED;
  const random = () => { randomState += 0x6D2B79F5; let t = randomState; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const randomValues = new Map([...candidates].sort((a, b) => a.opportunityId.localeCompare(b.opportunityId)).map((o) => [o.opportunityId, random()]));
  const value = (o: Opportunity, method: EvaluationMethod) => {
    if (method === 'catalog-price') return o.catalogPriceUsd ?? 0;
    if (method === 'recent-engagement') return Date.parse(o.engageDate!);
    if (method === 'random') return randomValues.get(o.opportunityId)!;
    return scoreOpportunity(scoringCandidate(o, 'Engaging'), stats, prices, method === 'priority' ? 'full' : method).priorityScore;
  };
  const metrics = (selected: Opportunity[], eligible: Opportunity[]) => {
    const wins = selected.filter((o) => outcome(o, horizon) === 'Won').length;
    const losses = selected.filter((o) => outcome(o, horizon) === 'Lost').length;
    const eligibleWins = eligible.filter((o) => outcome(o, horizon) === 'Won').length;
    const eligibleResolved = eligible.filter((o) => outcome(o, horizon) !== 'Censored').length;
    const resolvedWinRate = wins + losses ? wins / (wins + losses) : null;
    const baselineResolvedWinRate = eligibleResolved ? eligibleWins / eligibleResolved : null;
    return { selected: selected.length, wins, losses, censored: selected.length - wins - losses, resolvedWinRate, baselineResolvedWinRate, observedWinShare: selected.length ? wins / selected.length : null, lift: resolvedWinRate !== null && baselineResolvedWinRate ? resolvedWinRate / baselineResolvedWinRate : null, winCapture: eligibleWins ? wins / eligibleWins : null };
  };
  const bySeller = METHODS.flatMap((method) => agents.flatMap((salesAgent) => {
    const eligible = candidates.filter((o) => o.salesAgent === salesAgent);
    const ranked = [...eligible].sort((a, b) => value(b, method) - value(a, method) || a.opportunityId.localeCompare(b.opportunityId));
    return [10, 20, 50].map((k) => ({ method, salesAgent, k, eligible: eligible.length, smallerThanK: eligible.length < k, ...metrics(ranked.slice(0, k), eligible), ids: ranked.slice(0, k).map((o) => o.opportunityId) }));
  }));
  const summary = METHODS.flatMap((method) => [10, 20, 50].map((k) => {
    const rows = bySeller.filter((r) => r.method === method && r.k === k), ids = new Set(rows.flatMap((r) => r.ids));
    return { method, k, sellers: rows.length, sellersWithLessThanK: rows.filter((r) => r.smallerThanK).length, ...metrics(candidates.filter((o) => ids.has(o.opportunityId)), candidates) };
  }));
  return {
    cutoff, horizon, seed: RANDOM_SEED, ruleVersion: 'candidate-v1', protocol: 'Pesos fixados antes da avaliação final; nenhuma otimização no horizonte final.',
    historicalClosed: stats.global.count, eligible: candidates.length,
    outcomes: { wins: candidates.filter((o) => outcome(o, horizon) === 'Won').length, losses: candidates.filter((o) => outcome(o, horizon) === 'Lost').length, censored: candidates.filter((o) => outcome(o, horizon) === 'Censored').length },
    summary, bySeller,
    limitations: ['Resultados resolvidos têm viés de seleção.', 'Cadastros atuais são proxies sem snapshots históricos.', 'Não é possível reconstruir Prospecting sem data de criação.', 'Política de adiamento não é validada pelo backtest.', 'Score não é probabilidade; ações locais não são vendas.'],
  };
}
