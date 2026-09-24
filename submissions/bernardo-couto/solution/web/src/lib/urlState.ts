import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

export type SortKey = 'score' | 'value' | 'days';
export const SORT_TO_API: Record<SortKey, string> = {
  score: '-priority_score',
  value: '-expected_value,-priority_score',
  days: '-days_in_engaging,-priority_score',
};
export const TOP_N_OPTIONS = [10, 25, 50, 0] as const; // 0 = all (API max 500)
export const ALL_LIMIT = 500;

export interface UrlState {
  asOf?: string;
  region?: string;
  manager?: string;
  agent?: string;
  n: number;
  sort: SortKey;
  offset: number;
  deal?: string;
  queue: 'work' | 'confirm';
}

function parseSort(v: string | null): SortKey {
  return v === 'value' || v === 'days' ? v : 'score';
}

export function readState(sp: URLSearchParams): UrlState {
  const n = Number(sp.get('n') ?? 10);
  const offset = Number(sp.get('offset') ?? 0);
  return {
    asOf: sp.get('as_of') ?? undefined,
    region: sp.get('region') ?? undefined,
    manager: sp.get('manager') ?? undefined,
    agent: sp.get('agent') ?? undefined,
    n: Number.isFinite(n) && n >= 0 ? n : 10,
    sort: parseSort(sp.get('sort')),
    offset: Number.isFinite(offset) && offset > 0 ? offset : 0,
    deal: sp.get('deal') ?? undefined,
    queue: sp.get('queue') === 'confirm' ? 'confirm' : 'work',
  };
}

export function writeState(state: UrlState): URLSearchParams {
  const sp = new URLSearchParams();
  if (state.asOf) sp.set('as_of', state.asOf);
  if (state.region) sp.set('region', state.region);
  if (state.manager) sp.set('manager', state.manager);
  if (state.agent) sp.set('agent', state.agent);
  if (state.n !== 10) sp.set('n', String(state.n));
  if (state.sort !== 'score') sp.set('sort', state.sort);
  if (state.offset > 0) sp.set('offset', String(state.offset));
  if (state.deal) sp.set('deal', state.deal);
  if (state.queue === 'confirm') sp.set('queue', 'confirm');
  return sp;
}

/** Hierarchical filters: region clears manager+agent; manager clears agent. Filters reset paging. */
export function applyPatch(prev: UrlState, patch: Partial<UrlState>): UrlState {
  const next = { ...prev, ...patch };
  if ('region' in patch && patch.region !== prev.region) {
    next.manager = undefined;
    next.agent = undefined;
  }
  if ('manager' in patch && patch.manager !== prev.manager) next.agent = undefined;
  const pagingReset = ['region', 'manager', 'agent', 'asOf', 'n', 'sort', 'queue'].some(
    (k) => k in patch,
  );
  if (pagingReset && !('offset' in patch)) next.offset = 0;
  return next;
}

export function useUrlState() {
  const [sp, setSp] = useSearchParams();
  const state = useMemo(() => readState(sp), [sp]);
  const update = useCallback(
    (patch: Partial<UrlState>, opts?: { replace?: boolean }) =>
      setSp((current) => writeState(applyPatch(readState(current), patch)), {
        replace: opts?.replace,
      }),
    [setSp],
  );
  const clearFilters = useCallback(
    () => update({ region: undefined, manager: undefined, agent: undefined }),
    [update],
  );
  return { state, update, clearFilters, search: sp.toString() };
}

export function activeFilterCount(s: UrlState) {
  return [s.region, s.manager, s.agent].filter(Boolean).length;
}
