import { useCallback, useEffect, useState } from 'react';
import { dataset } from '../data/dataset';
import { operationalDayKey } from '../domain/dates';
import { emptySeller, ensureDay, isSellerState, resolveMission, selectMission, undoMission, type SellerState } from '../domain/missions/queue';
import type { DayKey } from '../domain/types';
import { createStorage, storageKey } from './storage';

const storage = createStorage();
const selectionKey = `lead-scorer:selection:${dataset.datasetVersion}`;
const validSelection = (v: unknown): v is string => typeof v === 'string' && dataset.agents.some((a) => a.name === v);
// Carteira inicial variada, com prioridades altas e datas de engajamento no Top 10.
const defaultSeller = dataset.opportunities.find((o) => o.salesAgent === 'Zane Levy')?.salesAgent ?? dataset.opportunities[0]?.salesAgent ?? '';
function restore(seller: string, day: DayKey): SellerState {
  const knownIds = new Set(dataset.opportunities.filter((o) => o.salesAgent === seller).map((o) => o.opportunityId));
  const valid = (value: unknown): value is SellerState => isSellerState(value) && value.datasetVersion === dataset.datasetVersion && value.salesAgent === seller && Object.values(value.days).every((d) => d.ranking.every((id) => knownIds.has(id)));
  const saved = storage.read(storageKey(dataset.datasetVersion, seller), valid);
  const matching = saved?.datasetVersion === dataset.datasetVersion && saved.salesAgent === seller ? saved : emptySeller(dataset.datasetVersion, seller);
  return ensureDay(matching, dataset.opportunities, day);
}

export function useDailyQueue() {
  const [now, setNow] = useState(() => new Date());
  const dayKey = operationalDayKey(now);
  const [seller, setSeller] = useState(() => storage.read(selectionKey, validSelection) ?? defaultSeller);
  const [state, setState] = useState<SellerState | null>(() => seller ? restore(seller, dayKey) : null);
  const [persistenceWarning, setPersistenceWarning] = useState(!storage.persistent);
  useEffect(() => {
    const refresh = () => setNow(new Date());
    const onVisible = () => { if (document.visibilityState === 'visible') refresh(); };
    const timer = window.setInterval(refresh, 30_000);
    document.addEventListener('visibilitychange', onVisible);
    window.addEventListener('focus', refresh);
    return () => { window.clearInterval(timer); document.removeEventListener('visibilitychange', onVisible); window.removeEventListener('focus', refresh); };
  }, []);
  useEffect(() => { setState((s) => s ? ensureDay(s, dataset.opportunities, dayKey) : s); }, [dayKey]);
  useEffect(() => {
    if (state) storage.write(storageKey(dataset.datasetVersion, state.salesAgent), state);
    if (seller) storage.write(selectionKey, seller);
    setPersistenceWarning(!storage.persistent);
  }, [state, seller]);
  const chooseSeller = useCallback((name: string) => {
    if (!validSelection(name)) return;
    setSeller(name); setState(restore(name, operationalDayKey())); setNow(new Date());
  }, []);
  const select = (id: string) => setState((s) => s ? selectMission(ensureDay(s, dataset.opportunities, operationalDayKey()), operationalDayKey(), id) : s);
  const resolve = (id: string, status: 'completed' | 'deferred') => {
    const timestamp = new Date(), day = operationalDayKey(timestamp);
    if (day !== dayKey) {
      setState((s) => s ? ensureDay(s, dataset.opportunities, day) : s); setNow(timestamp); return false;
    }
    setState((s) => s ? resolveMission(ensureDay(s, dataset.opportunities, day), day, id, status, timestamp.toISOString()) : s);
    setNow(timestamp);
    return true;
  };
  const undo = (actionDay: DayKey, id: string) => {
    const today = operationalDayKey();
    setState((s) => s ? undoMission(ensureDay(s, dataset.opportunities, today), today, actionDay, id) : s);
    setNow(new Date());
  };
  return { now, dayKey, seller, state, day: state?.days[dayKey] ?? null, persistenceWarning, chooseSeller, select, resolve, undo };
}
