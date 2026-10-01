import { BATCH_SIZE, DAILY_GOAL, STORAGE_SCHEMA_VERSION } from '../config';
import { nextCalendarDay } from '../dates';
import type { DayKey, MissionAction, RankedOpportunity } from '../types';

export interface DayState {
  dayKey: DayKey; goal: number; ranking: string[]; cursor: number;
  batchNumber: number; batch: string[]; active: string | null; returns: string[];
  actions: Record<string, MissionAction>;
}
export interface SellerState {
  schemaVersion: number; datasetVersion: string; salesAgent: string;
  days: Record<string, DayState>;
}
export function emptySeller(datasetVersion: string, salesAgent: string): SellerState {
  return { schemaVersion: STORAGE_SCHEMA_VERSION, datasetVersion, salesAgent, days: {} };
}
export const statusOf = (day: DayState, id: string) => day.actions[id]?.status ?? 'pending';
export const pendingIds = (day: DayState) => day.batch.filter((id) => statusOf(day, id) === 'pending');
export const completedCount = (day: DayState) => Object.values(day.actions).filter((a) => a.status === 'completed').length;
function latestAction(state: SellerState, id: string, dayKey: DayKey): MissionAction | undefined {
  return Object.keys(state.days).filter((d) => d < dayKey).sort().reverse().map((d) => state.days[d].actions[id]).find(Boolean);
}
function eligibleToday(state: SellerState, day: DayState, id: string): boolean {
  const current = day.actions[id];
  if (current && current.status !== 'pending') return false;
  const past = latestAction(state, id, day.dayKey);
  return !(past?.status === 'deferred' && past.deferredUntil > day.dayKey);
}
function loadBatch(state: SellerState, day: DayState) {
  const ids: string[] = [];
  while (day.returns.length && ids.length < BATCH_SIZE) {
    const id = day.returns.shift()!;
    if (day.ranking.includes(id) && eligibleToday(state, day, id) && !ids.includes(id)) ids.push(id);
  }
  while (day.cursor < day.ranking.length && ids.length < BATCH_SIZE) {
    const id = day.ranking[day.cursor++];
    if (eligibleToday(state, day, id) && !ids.includes(id)) ids.push(id);
  }
  day.batch = ids;
  if (ids.length) day.batchNumber++;
  day.active = ids[0] ?? null;
}
export function ensureDay(input: SellerState, opportunities: RankedOpportunity[], dayKey: DayKey): SellerState {
  if (input.days[dayKey]) return input;
  const state = structuredClone(input);
  const sellerOpportunities = opportunities.filter((o) => o.salesAgent === state.salesAgent && (o.stage === 'Engaging' || o.stage === 'Prospecting'));
  const available = sellerOpportunities.filter((o) => {
    const action = latestAction(state, o.opportunityId, dayKey);
    return !(action?.status === 'deferred' && action.deferredUntil > dayKey);
  });
  const isReturn = (id: string) => { const action = latestAction(state, id, dayKey); return action?.status === 'deferred' && action.deferredUntil <= dayKey; };
  const ranking = [...available].sort((a, b) => Number(isReturn(b.opportunityId)) - Number(isReturn(a.opportunityId)) || b.priorityScore - a.priorityScore || a.opportunityId.localeCompare(b.opportunityId)).map((o) => o.opportunityId);
  const day: DayState = { dayKey, goal: Math.min(DAILY_GOAL, ranking.length), ranking, cursor: 0, batchNumber: 0, batch: [], active: null, returns: [], actions: {} };
  state.days[dayKey] = day;
  loadBatch(state, day);
  return state;
}
export function selectMission(input: SellerState, dayKey: DayKey, id: string): SellerState {
  const day = input.days[dayKey];
  if (!day || !day.batch.includes(id) || statusOf(day, id) !== 'pending' || day.active === id) return input;
  const state = structuredClone(input); state.days[dayKey].active = id; return state;
}
export function resolveMission(input: SellerState, dayKey: DayKey, id: string, status: 'completed' | 'deferred', timestamp: string): SellerState {
  const oldDay = input.days[dayKey];
  if (!oldDay || !oldDay.batch.includes(id) || statusOf(oldDay, id) !== 'pending') return input;
  const state = structuredClone(input), day = state.days[dayKey];
  day.actions[id] = status === 'completed'
    ? { opportunityId: id, salesAgent: state.salesAgent, dayKey, status, completedAt: timestamp, deferredUntil: null }
    : { opportunityId: id, salesAgent: state.salesAgent, dayKey, status, completedAt: null, deferredUntil: nextCalendarDay(dayKey) };
  day.active = pendingIds(day)[0] ?? null;
  if (!day.active) loadBatch(state, day);
  return state;
}
export function undoMission(input: SellerState, currentDayKey: DayKey, actionDayKey: DayKey, id: string): SellerState {
  const actionDay = input.days[actionDayKey];
  if (!actionDay?.actions[id] || !input.days[currentDayKey]) return input;
  const state = structuredClone(input), day = state.days[currentDayKey];
  delete state.days[actionDayKey].actions[id];
  if (eligibleToday(state, day, id)) {
    if (!day.ranking.includes(id)) day.ranking.push(id);
    if (day.batch.includes(id)) day.active = id;
    else if (!day.returns.includes(id)) {
      day.returns.push(id);
      if (!pendingIds(day).length) loadBatch(state, day);
    }
  }
  return state;
}
export function currentStreak(state: SellerState, dayKey: DayKey): number {
  const achieved = (day: string) => !!state.days[day] && state.days[day].goal > 0 && completedCount(state.days[day]) >= state.days[day].goal;
  const previousDay = (day: string) => { const date = new Date(`${day}T12:00:00Z`); date.setUTCDate(date.getUTCDate() - 1); return date.toISOString().slice(0, 10); };
  let date: string = achieved(dayKey) ? dayKey : previousDay(dayKey), streak = 0;
  while (achieved(date)) { streak++; date = previousDay(date); }
  return streak;
}

/** Não confiar em JSON de armazenamento: valida estrutura e relações usadas pela fila. */
export function isSellerState(value: unknown): value is SellerState {
  if (!value || typeof value !== 'object') return false;
  const s = value as SellerState;
  if (s.schemaVersion !== STORAGE_SCHEMA_VERSION || typeof s.datasetVersion !== 'string' || typeof s.salesAgent !== 'string' || !s.days || typeof s.days !== 'object' || Array.isArray(s.days)) return false;
  const date = (v: unknown) => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v) && Number.isFinite(Date.parse(v)) && new Date(v).toISOString().slice(0, 10) === v;
  const ids = (v: unknown): v is string[] => Array.isArray(v) && v.every((x) => typeof x === 'string') && new Set(v).size === v.length;
  return Object.entries(s.days).every(([key, day]) => {
    if (!day || !date(key) || day.dayKey !== key || !Number.isInteger(day.goal) || day.goal < 0 || day.goal > DAILY_GOAL || !ids(day.ranking) || !ids(day.batch) || day.batch.length > BATCH_SIZE || !ids(day.returns) || !Number.isInteger(day.cursor) || day.cursor < 0 || day.cursor > day.ranking.length || !Number.isInteger(day.batchNumber) || day.batchNumber < 0 || !day.actions || typeof day.actions !== 'object' || Array.isArray(day.actions)) return false;
    if ([...day.batch, ...day.returns].some((id) => !day.ranking.includes(id))) return false;
    if (day.active !== null && (!day.batch.includes(day.active) || statusOf(day, day.active) !== 'pending')) return false;
    if (day.active === null && day.batch.some((id) => statusOf(day, id) === 'pending')) return false;
    return Object.entries(day.actions).every(([id, a]) => a && day.ranking.includes(id) && a.opportunityId === id && a.salesAgent === s.salesAgent && a.dayKey === key && (
      (a.status === 'completed' && typeof a.completedAt === 'string' && Number.isFinite(Date.parse(a.completedAt)) && a.deferredUntil === null) ||
      (a.status === 'deferred' && a.completedAt === null && date(a.deferredUntil) && a.deferredUntil > key)
    ));
  });
}
