import { SCORING_RULE } from '../config';
import type { Opportunity } from '../ingestion';
import type { DayKey, RankedOpportunity, ScoringOpportunity, ScoreFactor } from '../types';
export interface Segment { wins: number; count: number; rate: number }
export interface HistoricalStats {
  asOfDate: DayKey; global: Segment;
  product: Record<string, Segment>; sector: Record<string, Segment>; account: Record<string, Segment>;
  medianCycleDays: number; productMedianCycleDays: Record<string, number>;
}
export const daysBetween = (from: DayKey, to: DayKey) => (Date.parse(to) - Date.parse(from)) / 86_400_000;
const median = (values: number[]) => {
  const sorted = [...values].sort((a, b) => a - b), m = Math.floor(sorted.length / 2);
  return sorted.length ? sorted.length % 2 ? sorted[m] : (sorted[m - 1] + sorted[m]) / 2 : 0;
};
export function historicalStats(opportunities: Opportunity[], asOfDate: DayKey): HistoricalStats {
  const closed = opportunities.filter((o) => (o.stage === 'Won' || o.stage === 'Lost') && o.closeDate !== null && o.closeDate <= asOfDate);
  const wins = closed.filter((o) => o.stage === 'Won').length, rate = closed.length ? wins / closed.length : 0.5;
  const global = { wins, count: closed.length, rate };
  const group = (key: 'product' | 'sector' | 'account') => {
    const counts = new Map<string, { wins: number; count: number }>();
    for (const o of closed) { const value = o[key]; if (!value) continue; const s = counts.get(value) ?? { wins: 0, count: 0 }; s.count++; s.wins += Number(o.stage === 'Won'); counts.set(value, s); }
    return Object.fromEntries([...counts].sort(([a], [b]) => a.localeCompare(b)).map(([key, s]) => [key, { ...s, rate: (s.wins + SCORING_RULE.smoothing * rate) / (s.count + SCORING_RULE.smoothing) }]));
  };
  const cycles = closed.filter((o) => o.engageDate && o.closeDate).map((o) => daysBetween(o.engageDate!, o.closeDate!));
  const productCycles = new Map<string, number[]>();
  for (const o of closed) if (o.engageDate && o.closeDate) { const values = productCycles.get(o.product) ?? []; values.push(daysBetween(o.engageDate, o.closeDate)); productCycles.set(o.product, values); }
  return { asOfDate, global, product: group('product'), sector: group('sector'), account: group('account'), medianCycleDays: median(cycles), productMedianCycleDays: Object.fromEntries([...productCycles].map(([p, v]) => [p, median(v)])) };
}
export function scoringCandidate(o: Opportunity, stage: 'Prospecting' | 'Engaging'): ScoringOpportunity {
  return { opportunityId: o.opportunityId, salesAgent: o.salesAgent, product: o.product, originalProduct: o.originalProduct, account: o.account, sector: o.sector, stage, engageDate: o.engageDate, catalogPriceUsd: o.catalogPriceUsd };
}
export type ScoringVariant = 'full' | 'without-value' | 'without-age';
export function scoreOpportunity(o: ScoringOpportunity, stats: HistoricalStats, prices: number[], variant: ScoringVariant = 'full'): RankedOpportunity {
  const pct = (value: number) => `${(value * 100).toFixed(1).replace('.', ',')}%`;
  const segments = ([['product', o.product, SCORING_RULE.historicalWeights.product, 'produto'], ['sector', o.sector, SCORING_RULE.historicalWeights.sector, 'setor'], ['account', o.account, SCORING_RULE.historicalWeights.account, 'conta']] as const).map(([kind, key, weight, label]) => {
    const segment = key && Object.hasOwn(stats[kind], key) ? stats[kind][key] : undefined; return { label, weight, segment, rate: segment?.rate ?? stats.global.rate };
  });
  const history = segments.reduce((sum, s) => sum + s.weight * s.rate, 0);
  const age = o.engageDate ? Math.max(0, daysBetween(o.engageDate, stats.asOfDate)) : null;
  const productCycle = stats.productMedianCycleDays[o.product], cycle = productCycle > 0 ? productCycle : stats.medianCycleDays;
  const ageValue = age === null || cycle <= 0 ? 0.5 : Math.exp(-age / (2 * cycle));
  const positivePrices = prices.filter((p) => Number.isFinite(p) && p > 0), logs = positivePrices.map(Math.log1p);
  const min = Math.min(...logs), max = Math.max(...logs), hasPrice = o.catalogPriceUsd !== null && o.catalogPriceUsd > 0;
  const value = !hasPrice || !logs.length || max === min ? 0.5 : Math.max(0, Math.min(1, (Math.log1p(o.catalogPriceUsd!) - min) / (max - min)));
  const weights = variant === 'without-value' ? { history: 0.65 / 0.9, engagementAge: 0.25 / 0.9, catalogValue: 0 } : variant === 'without-age' ? { history: 0.65 / 0.75, engagementAge: 0, catalogValue: 0.10 / 0.75 } : SCORING_RULE.weights;
  const historyText = segments.map((s) => `${s.label}: ${pct(s.rate)} de sucesso, com base em ${s.segment?.count ?? stats.global.count} negociações anteriores${s.segment ? '' : ' da base inteira'}`).join('; ');
  const historyFallback = segments.filter((s) => !s.segment).map((s) => s.label).join(', ');
  const factors: ScoreFactor[] = [
    { key: 'history', normalizedValue: history, contributionPoints: 100 * weights.history * history, explanation: `O resultado de negociações anteriores ajuda a definir a prioridade. ${historyText}. Ajustamos esses percentuais com a média geral para que poucas negociações não pesem demais na comparação. Eles não são a chance de fechar esta oportunidade.`, sampleSize: stats.global.count, fallback: historyFallback ? `Sem histórico específico de ${historyFallback}, usamos os resultados da base inteira.` : null },
    { key: 'engagementAge', normalizedValue: ageValue, contributionPoints: 100 * weights.engagementAge * ageValue, explanation: age === null ? 'Não sabemos quando esta oportunidade entrou em engajamento. Por isso, não a tratamos como recente nem antiga.' : `Na data dos dados analisados, esta oportunidade estava em engajamento há ${age} dias.${cycle > 0 ? ` Comparamos esse tempo com o prazo típico de ${cycle} dias até encerrar uma negociação. Quanto mais recente, mais pontos neste critério.` : ' Não há dados suficientes para comparar com o prazo de outras negociações.'} Esse tempo começa na entrada em engajamento, não no último contato com o cliente.`, sampleSize: stats.product[o.product]?.count ?? stats.global.count, fallback: age === null || cycle <= 0 ? 'Usamos um valor intermediário neste critério por falta de informação.' : productCycle > 0 ? null : 'Como não temos um prazo típico para este produto, usamos o prazo das negociações da base inteira.' },
    { key: 'catalogValue', normalizedValue: value, contributionPoints: 100 * weights.catalogValue * value, explanation: hasPrice ? 'Comparamos o preço de uma unidade deste produto com os outros preços do catálogo. Produtos mais caros ganham mais pontos neste critério, mas a diferença de preço tem peso limitado. É o preço de tabela, não o valor combinado com o cliente nem uma previsão de quanto você vai vender.' : 'O preço de tabela deste produto não foi informado.', sampleSize: positivePrices.length, fallback: !hasPrice || !logs.length || max === min ? 'Sem preços suficientes ou diferentes para comparar, usamos um valor intermediário neste critério.' : null },
  ];
  const missingData = [!o.account && 'Conta não informada', !o.sector && 'Setor não informado', !o.engageDate && 'Data de engajamento desconhecida', !hasPrice && 'Preço de catálogo desconhecido'].filter((s): s is string => typeof s === 'string');
  const nextAction = o.stage === 'Prospecting' ? 'Qualifique a necessidade e identifique quem decide a compra. O tempo em prospecção é desconhecido.' : age !== null && cycle > 0 && age > cycle * 2 ? 'Confirme se a oportunidade continua ativa e revise a estratégia antes de atualizar o pipeline.' : 'Confirme a situação atual, a necessidade e o próximo passo com quem decide a compra.';
  return { ...o, priorityScore: Math.round(factors.reduce((sum, f) => sum + f.contributionPoints, 0)), scoringVersion: `${SCORING_RULE.version}:${variant}`, asOfDate: stats.asOfDate, factors, missingData, nextAction };
}
export function rank(opportunities: RankedOpportunity[]) { return [...opportunities].sort((a, b) => b.priorityScore - a.priorityScore || a.opportunityId.localeCompare(b.opportunityId)); }

