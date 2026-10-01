// @vitest-environment node
import { beforeAll, describe, expect, it } from 'vitest';
import { loadRaw } from '../scripts/load-raw';
import { ingest, parseCsv, validDate } from '../src/domain/ingestion';
import { historicalStats, scoreOpportunity, scoringCandidate } from '../src/domain/scoring/engine';
import { evaluate, historicalCandidates, outcome } from '../src/domain/evaluation';

let data: Awaited<ReturnType<typeof loadRaw>>;
beforeAll(async () => { data = await loadRaw(); });
describe('CSV e integridade dos dados reais', () => {
  it('recusa datas inexistentes e preserva ausência de data', () => {
    expect(validDate('', 'engage_date')).toBeNull();
    expect(validDate('2024-02-29', 'engage_date')).toBe('2024-02-29');
    expect(() => validDate('2023-02-29', 'engage_date')).toThrow('Data inválida');
    expect(() => validDate('2017-13-01', 'engage_date')).toThrow('Data inválida');
  });
  it('lê aspas escapadas, vírgulas, BOM e linhas dentro de campos', () => {
    expect(parseCsv('\uFEFFid,text\r\n1,"a,b"\r\n2,"aspas ""ok""\nlinha"\r\n')).toEqual([{ id: '1', text: 'a,b' }, { id: '2', text: 'aspas "ok"\nlinha' }]);
    expect(() => parseCsv('id,text\n1,"aberto')).toThrow();
    expect(() => parseCsv('id,id\n1,2')).toThrow();
    expect(() => parseCsv('id,text\n1')).toThrow();
  });
  it('preserva cardinalidade, conta ausente e todos os aliases', () => {
    expect(data.opportunities).toHaveLength(8800);
    expect(new Set(data.opportunities.map((o) => o.opportunityId)).size).toBe(8800);
    expect(data.quality.aliases).toBe(1480);
    expect(data.quality.missingAccounts).toBe(1425);
    expect(data.quality.stages).toEqual({ Prospecting: 500, Engaging: 1589, Won: 4238, Lost: 2473 });
    expect(data.quality.unknownProducts).toEqual([]);
    expect(data.quality.unknownAccounts).toEqual([]);
    expect(data.quality.unknownSalesAgents).toEqual([]);
    expect(data.opportunities.filter((o) => o.originalProduct === 'GTXPro').every((o) => o.product === 'GTX Pro' && o.catalogPriceUsd === 4821)).toBe(true);
  });
  it('preserva vínculos desconhecidos e acusa chave duplicada', () => {
    const files = { pipeline: 'opportunity_id,sales_agent,product,account,deal_stage,engage_date,close_date,close_value\nx,A,Unknown,,Prospecting,,,', accounts: 'account,sector,revenue\nB,tech,1', products: 'product,sales_price\nP,10', teams: 'sales_agent,manager,regional_office\nA,M,R' };
    const result = ingest(files);
    expect(result.opportunities).toHaveLength(1);
    expect(result.quality.unknownProducts).toEqual(['Unknown']);
    expect(result.opportunities[0].catalogPriceUsd).toBeNull();
    expect(() => ingest({ ...files, pipeline: files.pipeline + '\nx,A,P,,Prospecting,,,' })).toThrow('duplicada');
  });
});
describe('scoring e avaliação sem vazamento', () => {
  it('nomes especiais sem histórico usam e explicam a referência global', () => {
    const stats = historicalStats([], '2017-12-31');
    const input = scoringCandidate(data.opportunities[0], 'Prospecting');
    for (const name of ['constructor', 'toString', '__proto__']) {
      const score = scoreOpportunity({ ...input, product: name, sector: name, account: name, engageDate: null, catalogPriceUsd: null }, stats, []);
      expect(score.priorityScore).toBe(50);
      expect(score.factors.every((f) => Number.isFinite(f.contributionPoints))).toBe(true);
      expect(score.factors.find((f) => f.key === 'history')?.fallback).toContain('base inteira');
    }
  });
  it('catálogo sem variação e ciclo zero usam valores intermediários seguros', () => {
    const input = scoringCandidate(data.opportunities[0], 'Engaging');
    const score = scoreOpportunity({ ...input, engageDate: '2017-12-01', catalogPriceUsd: 10 }, historicalStats([], '2017-12-31'), [10, 10]);
    expect(score.priorityScore).toBe(50);
    expect(score.factors.find((f) => f.key === 'catalogValue')?.normalizedValue).toBe(0.5);
    expect(score.factors.find((f) => f.key === 'engagementAge')?.normalizedValue).toBe(0.5);
  });
  it('avaliação vazia e vendedor com menos de K mantêm os denominadores corretos', () => {
    const empty = evaluate([], []);
    expect(empty.summary.every((r) => r.selected === 0 && r.resolvedWinRate === null && r.lift === null && r.winCapture === null)).toBe(true);
    const candidate = { ...data.opportunities[0], engageDate: '2017-09-01' as const, closeDate: null, stage: 'Engaging' as const };
    const small = evaluate([candidate], data.prices);
    expect(small.bySeller.every((r) => r.selected === 1 && r.smallerThanK && r.censored === 1 && r.losses === 0 && r.resolvedWinRate === null)).toBe(true);
  });
  it('gera scores finitos, limitados e explicações consistentes em todas as abertas', () => {
    const stats = historicalStats(data.opportunities, '2017-12-31');
    for (const o of data.opportunities.filter((o) => o.stage === 'Prospecting' || o.stage === 'Engaging')) {
      const input = scoringCandidate(o, o.stage as 'Prospecting' | 'Engaging'), scored = scoreOpportunity(input, stats, data.prices);
      expect(scored.priorityScore).toBeGreaterThanOrEqual(0);
      expect(scored.priorityScore).toBeLessThanOrEqual(100);
      expect(scored.priorityScore).toBe(Math.round(scored.factors.reduce((s, f) => s + f.contributionPoints, 0)));
      expect(scored).toEqual(scoreOpportunity(input, stats, data.prices));
    }
  });
  it('ignora receita e resultado futuros do candidato; exclui futuro do histórico', () => {
    const cut = '2017-09-30', candidates = historicalCandidates(data.opportunities, cut), o = candidates.find((o) => o.closeDate)!;
    const changed = data.opportunities.map((item) => item.opportunityId === o.opportunityId ? { ...item, closeValue: 999999, stage: item.stage === 'Won' ? 'Lost' as const : 'Won' as const } : item);
    const stats = historicalStats(data.opportunities, cut);
    expect(historicalStats(changed, cut)).toEqual(stats);
    expect(scoreOpportunity(scoringCandidate(changed.find((i) => i.opportunityId === o.opportunityId)!, 'Engaging'), stats, data.prices)).toEqual(scoreOpportunity(scoringCandidate(o, 'Engaging'), stats, data.prices));
    expect(stats.global.count).toBe(4726);
  });
  it('usa fallbacks seguros sem histórico, preço ou datas', () => {
    const input = scoringCandidate(data.opportunities[0], 'Prospecting');
    const score = scoreOpportunity({ ...input, product: 'Unknown', engageDate: null, catalogPriceUsd: null, account: null, sector: null }, historicalStats([], '2017-12-31'), []);
    expect(score.priorityScore).toBe(50);
    expect(score.factors.every((f) => f.fallback !== null)).toBe(true);
    expect(score.nextAction).toContain('tempo em prospecção é desconhecido');
  });
  it('reconstrói o corte e separa censura, com resultados reproduzíveis', () => {
    const report = evaluate(data.opportunities, data.prices);
    expect(report.eligible).toBe(2409);
    expect(report.outcomes).toEqual({ wins: 559, losses: 376, censored: 1474 });
    const candidate = historicalCandidates(data.opportunities, '2017-09-30').find((o) => !o.closeDate)!;
    expect(outcome(candidate, '2017-12-31')).toBe('Censored');
    expect(report).toEqual(evaluate(data.opportunities, data.prices));
    expect(report.bySeller.every((r) => r.ids.length <= r.k && new Set(r.ids).size === r.ids.length)).toBe(true);
  });
});
