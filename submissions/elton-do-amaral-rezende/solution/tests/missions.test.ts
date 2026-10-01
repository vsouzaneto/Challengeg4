import { describe, expect, it } from 'vitest';
import { emptySeller, ensureDay, resolveMission, selectMission, undoMission, completedCount, currentStreak, isSellerState, pendingIds } from '../src/domain/missions/queue';
import type { RankedOpportunity, DayKey } from '../src/domain/types';

const date: DayKey = '2026-09-30';
const opportunities = (count = 25): RankedOpportunity[] => Array.from({ length: count }, (_, i) => ({ opportunityId: `id-${i.toString().padStart(2, '0')}`, salesAgent: 'A', priorityScore: 100 - i, product: 'P', originalProduct: 'P', account: null, sector: null, stage: 'Engaging', engageDate: '2017-12-01', catalogPriceUsd: 10, scoringVersion: 'test', asOfDate: '2017-12-31', factors: [], missingData: [], nextAction: 'Confirmar situação' }));
const start = (count = 25) => ensureDay(emptySeller('v1', 'A'), opportunities(count), date);
describe('fila diária', () => {
  it('isola vendedor, mantém lote estável e seleção não conclui', () => {
    const state = start();
    const selected = selectMission(state, date, 'id-06');
    expect(selected.days[date].batch).toEqual(state.days[date].batch);
    expect(selected.days[date].active).toBe('id-06');
    expect(completedCount(selected.days[date])).toBe(0);
    expect(ensureDay(emptySeller('v1', 'B'), opportunities(), date).days[date].batch).toEqual([]);
  });
  it('feito é idempotente e desfazer restaura posição', () => {
    const state = start(), done = resolveMission(state, date, 'id-00', 'completed', '2026-09-30T12:00:00Z');
    expect(resolveMission(done, date, 'id-00', 'completed', '2026-09-30T12:01:00Z')).toBe(done);
    expect(done.days[date].active).toBe('id-01');
    expect(completedCount(done.days[date])).toBe(1);
    const undone = undoMission(done, date, date, 'id-00');
    expect(undone.days[date].batch).toEqual(state.days[date].batch);
    expect(undone.days[date].active).toBe('id-00');
    expect(completedCount(undone.days[date])).toBe(0);
  });
  it('esgota lotes sem repetir e devolve desfazer antigo pela fila explícita', () => {
    let state = start();
    for (const id of [...state.days[date].batch]) state = resolveMission(state, date, id, 'completed', '2026-09-30T12:00:00Z');
    expect(state.days[date].batchNumber).toBe(2);
    expect(state.days[date].batch).toHaveLength(10);
    state = undoMission(state, date, date, 'id-00');
    expect(state.days[date].returns).toEqual(['id-00']);
    for (const id of [...state.days[date].batch]) state = resolveMission(state, date, id, 'deferred', '2026-09-30T12:00:00Z');
    expect(state.days[date].batch).toEqual(['id-00', 'id-20', 'id-21', 'id-22', 'id-23', 'id-24']);
    expect(completedCount(state.days[date])).toBe(9);
  });
  it('todos adiados não cumprem meta e retornam primeiro amanhã', () => {
    let state = start(12);
    for (const id of [...state.days[date].batch]) state = resolveMission(state, date, id, 'deferred', '2026-09-30T12:00:00Z');
    expect(state.days[date].goal).toBe(10);
    expect(completedCount(state.days[date])).toBe(0);
    expect(currentStreak(state, date)).toBe(0);
    const next = ensureDay(state, opportunities(12), '2026-10-01');
    expect(next.days['2026-10-01'].batch).toEqual(Array.from({ length: 10 }, (_, i) => `id-${i.toString().padStart(2, '0')}`));
  });
  it('lote pequeno e desfazer depois do esgotamento permitem retomar', () => {
    let state = start(6);
    expect(state.days[date].goal).toBe(6);
    for (const id of [...state.days[date].batch]) state = resolveMission(state, date, id, 'completed', '2026-09-30T12:00:00Z');
    expect(state.days[date].batch).toEqual([]);
    expect(currentStreak(state, date)).toBe(1);
    state = undoMission(state, date, date, 'id-05');
    expect(state.days[date].batch).toEqual(['id-05']);
    expect(currentStreak(state, date)).toBe(0);
    expect(isSellerState(state)).toBe(true);
  });
  it('preserva o mesmo dia, evita dias extras e recalcula sequência ao desfazer', () => {
    let state = start(1);
    state = resolveMission(state, date, 'id-00', 'completed', '2026-09-30T12:00:00Z');
    expect(ensureDay(state, opportunities(1), date)).toBe(state);
    state = ensureDay(state, opportunities(1), '2026-10-01');
    state = resolveMission(state, '2026-10-01', 'id-00', 'completed', '2026-10-01T12:00:00Z');
    expect(currentStreak(state, '2026-10-01')).toBe(2);
    state = undoMission(state, '2026-10-01', date, 'id-00');
    expect(currentStreak(state, '2026-10-01')).toBe(1);
    expect(pendingIds(state.days['2026-10-01'])).toEqual([]);
  });
  it('rejeita estado corrompido e referência ativa fora do lote', () => {
    expect(isSellerState(start())).toBe(true);
    expect(isSellerState({ ...start(), schemaVersion: 999 })).toBe(false);
    const corrupt = start(); corrupt.days[date].active = 'inexistente';
    expect(isSellerState(corrupt)).toBe(false);
  });
  it('mantém adiamento futuro fora da fila e não inventa conquista em dia vazio', () => {
    let state = start(1);
    state = resolveMission(state, date, 'id-00', 'deferred', '2026-09-30T12:00:00Z');
    const action = state.days[date].actions['id-00'];
    if (action.status === 'deferred') action.deferredUntil = '2026-10-03';
    state = ensureDay(state, opportunities(1), '2026-10-01');
    expect(state.days['2026-10-01'].goal).toBe(0);
    expect(state.days['2026-10-01'].batch).toEqual([]);
    expect(currentStreak(state, '2026-10-01')).toBe(0);
    const returned = undoMission(state, '2026-10-01', date, 'id-00');
    expect(returned.days['2026-10-01'].batch).toEqual(['id-00']);
    expect(returned.days['2026-10-01'].goal).toBe(0);
    state = ensureDay(state, opportunities(1), '2026-10-03');
    expect(state.days['2026-10-03'].batch).toEqual(['id-00']);
  });
});
