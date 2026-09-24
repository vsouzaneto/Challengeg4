import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ScoredDeal } from '../api/client';
import { useDeals, useMeta, usePipelineSummary } from '../api/queries';
import { DealDrawer } from '../components/DealDrawer';
import { DealRow } from '../components/DealRow';
import { QueueSkeleton } from '../components/Skeleton';
import { ApiErrorBanner, EmptyState, QueryError } from '../components/States';
import { Tile } from '../components/Tile';
import { FirstOpenNotice } from '../components/WhatItDoesNotDo';
import { useFeedback, type UiAction } from '../features/feedback/feedbackStore';
import { t } from '../i18n/pt-BR';
import { dealsToCsv, downloadCsv } from '../lib/csv';
import { fmtBRL, fmtInt } from '../lib/format';
import { ageBand, COOLING_DAYS, isCooling, ZOMBIE_DAYS, type QueueKind } from '../lib/reasons';
import { ALL_LIMIT, SORT_TO_API, TOP_N_OPTIONS, useUrlState, type SortKey } from '../lib/urlState';

const EMPTY: ScoredDeal[] = [];
const DAILY_QUOTA = 5;
/** "Confirm" queue order: value desc, then newest first (scoring-spec §4). `sales_price` is not
 * sortable in the API, so expected value is the proxy for nominal value. */
const CONFIRM_SORT = '-sales_price,days_in_engaging';

/**
 * Home: two queues with two verbs (revops-review §3c), both paginated by the API
 * (`queue=work|confirm`). Counts for the other tab and the cooling tile come from
 * `limit=1` requests (`total`); the nominal value of the stale queue comes from
 * `/pipeline/summary` — nothing is computed from scores here.
 */
export function QueuePage() {
  const { state, update, clearFilters } = useUrlState();
  const meta = useMeta();
  const queue: QueueKind = state.queue;
  const ready = !!state.asOf || meta.isFetched;
  const scopeParams = {
    as_of: state.asOf,
    regional_office: state.region,
    manager: state.manager,
    sales_agent: state.agent,
  };
  const limit = state.n === 0 ? ALL_LIMIT : state.n;
  const query = useDeals(
    {
      ...scopeParams,
      queue,
      sort: queue === 'work' ? SORT_TO_API[state.sort] : CONFIRM_SORT,
      limit,
      offset: state.offset,
    },
    ready,
  );
  const other: QueueKind = queue === 'work' ? 'confirm' : 'work';
  const otherCount = useDeals({ ...scopeParams, queue: other, limit: 1 }, ready);
  const coolingCount = useDeals(
    {
      ...scopeParams,
      queue: 'work',
      min_days_in_engaging: COOLING_DAYS + 1,
      max_days_in_engaging: ZOMBIE_DAYS,
      limit: 1,
    },
    ready && queue === 'work',
  );
  const summary = usePipelineSummary(
    { ...scopeParams, group_by: 'regional_office' },
    ready && queue === 'confirm',
  );
  const { state: fb } = useFeedback();
  const [focusAction, setFocusAction] = useState<UiAction | undefined>();
  const titleRefs = useRef(new Map<string, HTMLButtonElement>());
  const h1Ref = useRef<HTMLHeadingElement>(null);

  const page = query.data;
  const items = useMemo(() => page?.items ?? EMPTY, [page]);
  const visible = useMemo(
    () => items.filter((d) => !fb.discarded[d.opportunity_id]),
    [items, fb.discarded],
  );
  const total = page?.total ?? 0;
  const counts = {
    [queue]: total,
    [other]: otherCount.data?.total,
  } as Record<QueueKind, number | undefined>;
  const hasNext = page ? page.offset + page.limit < page.total : false;
  const hasPrev = state.offset > 0;
  const remaining = total - state.offset - limit;

  const selected = state.deal;
  const initialDeal = items.find((d) => d.opportunity_id === selected);

  // Tiles: counts/sums over the loaded page or API totals (ux-spec §3.3, revops-review §5.4).
  const hot = visible.filter((d) => d.tier === 'A').length;
  const expected = visible.reduce((s, d) => s + d.expected_value, 0);
  const cooling = coolingCount.data?.total ?? visible.filter(isCooling).length;
  const staleTotal = summary.data?.total;
  const staleNominal = staleTotal?.nominal_zombie_value;
  const handled = items.filter((d) => {
    const f = fb.byDeal[d.opportunity_id];
    return f !== undefined && f.status !== 'error';
  }).length;

  const openDeal = useCallback(
    (deal: ScoredDeal, opts?: { focusAction?: 'accountFixed' }) => {
      setFocusAction(opts?.focusAction);
      update({ deal: deal.opportunity_id });
    },
    [update],
  );
  const closeDeal = useCallback(() => update({ deal: undefined }), [update]);
  const returnFocus = useCallback(() => {
    if (!selected) return h1Ref.current;
    const own = titleRefs.current.get(selected);
    if (own && own.isConnected) return own;
    const idx = items.findIndex((d) => d.opportunity_id === selected);
    const next = items.slice(idx + 1).find((d) => !fb.discarded[d.opportunity_id]);
    return (next && titleRefs.current.get(next.opportunity_id)) ?? h1Ref.current;
  }, [selected, items, fb.discarded]);

  useEffect(() => {
    if (!selected) setFocusAction(undefined);
  }, [selected]);

  const scope = state.agent ?? state.manager ?? state.region ?? t.queue.scopeAll;
  const openTotal = (counts.work ?? 0) + (counts.confirm ?? 0);

  return (
    <div>
      <FirstOpenNotice />
      <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 ref={h1Ref} tabIndex={-1} className="font-serif text-2xl font-bold outline-none">
            {state.agent ? t.queue.title : t.queue.titleTeam}
          </h1>
          <p className="mt-1 text-sm text-g4-muted">
            {page ? t.queue.subtitle(scope, openTotal, visible.length) : scope}
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label htmlFor="top-n" className="mb-1 block text-xs font-semibold text-g4-muted">
              {t.queue.topLabel}
            </label>
            <select
              id="top-n"
              className="select w-32"
              value={state.n}
              onChange={(e) => update({ n: Number(e.target.value) })}
            >
              {TOP_N_OPTIONS.map((n) => (
                <option key={n} value={n}>
                  {n === 0 ? t.queue.topAll : t.queue.topN(n)}
                </option>
              ))}
            </select>
          </div>
          {queue === 'work' && (
            <div>
              <label htmlFor="sort" className="mb-1 block text-xs font-semibold text-g4-muted">
                {t.queue.sortLabel}
              </label>
              <select
                id="sort"
                className="select w-44"
                value={state.sort}
                onChange={(e) => update({ sort: e.target.value as SortKey })}
              >
                {(Object.keys(t.queue.sort) as SortKey[]).map((k) => (
                  <option key={k} value={k}>
                    {t.queue.sort[k]}
                  </option>
                ))}
              </select>
            </div>
          )}
          <button
            type="button"
            className="btn-secondary"
            title={t.queue.exportHint}
            disabled={visible.length === 0}
            onClick={() =>
              downloadCsv(
                `lead-scorer_${page?.as_of ?? 'deals'}_${queue}_${scope}.csv`,
                dealsToCsv(visible),
              )
            }
          >
            {t.queue.export}
          </button>
        </div>
      </div>

      <div
        role="tablist"
        aria-label={t.queue.tabs.label}
        className="mb-6 flex gap-1 border-b border-g4line"
      >
        {(['work', 'confirm'] as const).map((k) => (
          <button
            key={k}
            role="tab"
            type="button"
            id={`tab-${k}`}
            aria-selected={queue === k}
            aria-controls={page ? `panel-${k}` : undefined}
            className={`-mb-px rounded-t px-4 py-2 text-sm font-semibold ${
              queue === k
                ? 'border border-b-white border-g4line bg-white text-g4-primary'
                : 'text-g4-navy700 hover:bg-g4-rowHover'
            }`}
            onClick={() => update({ queue: k })}
          >
            {t.queue.tabs[k]}
            {counts[k] !== undefined && (
              <span className="ml-2 rounded-full bg-g4-tintNavy px-2 py-0.5 text-xs tabular-nums text-g4-primary">
                {fmtInt(counts[k]!)}
              </span>
            )}
          </button>
        ))}
      </div>

      {query.isError && !page && <QueryError error={query.error} onRetry={() => query.refetch()} />}
      {query.isError && page && (
        <div className="mb-4">
          <ApiErrorBanner error={query.error} onRetry={() => query.refetch()} />
        </div>
      )}
      {query.isPending && !query.isError && <QueueSkeleton />}

      {page && (
        <div role="tabpanel" id={`panel-${queue}`} aria-labelledby={`tab-${queue}`}>
          {queue === 'work' ? (
            <>
              <p className="mb-4 text-xs font-medium text-g4-muted">{t.queue.orderNote}</p>
              {state.sort !== 'score' && (
                <p
                  role="status"
                  className="mb-4 rounded bg-g4-tintNavy px-3 py-2 text-xs font-semibold text-g4-primary"
                >
                  {t.queue.sortWarning}
                </p>
              )}
              <div className="mb-6 grid gap-3 sm:grid-cols-3">
                <Tile value={fmtInt(hot)} label={t.queue.tiles.hot} hint={t.queue.tiles.hotHint} />
                <Tile
                  value={fmtBRL(expected)}
                  label={`${t.queue.tiles.expected} ${visible.length}`}
                  hint={t.queue.tiles.expectedHint(visible.length)}
                />
                <Tile
                  value={fmtInt(cooling)}
                  label={t.queue.tiles.cooling}
                  hint={t.queue.tiles.coolingHint}
                />
              </div>
            </>
          ) : (
            <div className="card mb-6 p-4">
              <h2 className="text-xl font-semibold">{t.queue.confirm.title}</h2>
              <p className="mt-1 text-sm">
                {t.queue.confirm.intro(total, staleNominal != null ? fmtBRL(staleNominal) : '—')}
              </p>
              <p className="mt-1 text-xs font-medium text-g4-muted">{t.queue.confirm.order}</p>
              <div className="mt-3">
                <div className="flex items-center justify-between text-xs font-medium text-g4-muted">
                  <span id="quota-label">
                    {t.queue.confirm.quota(Math.min(handled, DAILY_QUOTA), DAILY_QUOTA)}
                  </span>
                  <span>{t.queue.confirm.progress(handled, total)}</span>
                </div>
                <div
                  role="progressbar"
                  aria-labelledby="quota-label"
                  aria-valuemin={0}
                  aria-valuemax={DAILY_QUOTA}
                  aria-valuenow={Math.min(handled, DAILY_QUOTA)}
                  className="mt-1 h-2 w-full overflow-hidden rounded bg-tier-Cbg"
                >
                  <div
                    className="h-full bg-g4-navy700"
                    style={{ width: `${Math.min(handled / DAILY_QUOTA, 1) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {total === 0 && openTotal === 0 && (
            <EmptyState
              title={t.states.emptyTitle}
              body={t.states.emptyBody}
              actionLabel={t.filters.clear}
              onAction={clearFilters}
            />
          )}
          {total === 0 && openTotal > 0 && queue === 'work' && (
            <EmptyState
              title={t.queue.confirm.workEmptyTitle}
              body={t.queue.confirm.workEmptyBody(counts.confirm ?? 0)}
              actionLabel={t.queue.confirm.goConfirm}
              onAction={() => update({ queue: 'confirm' })}
            />
          )}
          {total === 0 && openTotal > 0 && queue === 'confirm' && (
            <EmptyState title={t.queue.confirm.emptyTitle} body={t.queue.confirm.emptyBody} />
          )}
          {items.length > 0 && visible.length === 0 && (
            <EmptyState
              title={t.states.allHandledTitle}
              actionLabel={hasNext ? t.queue.more(limit) : undefined}
              onAction={hasNext ? () => update({ offset: state.offset + limit }) : undefined}
            />
          )}

          {visible.length > 0 && (
            <ol
              aria-label={queue === 'work' ? t.queue.listLabel : t.queue.confirm.title}
              className="space-y-3"
              aria-busy={query.isFetching}
            >
              {visible.map((deal, i) => {
                const days = deal.days_in_engaging ?? 0;
                const band = queue === 'confirm' ? ageBand(days) : null;
                const prevDays = i > 0 ? (visible[i - 1]!.days_in_engaging ?? 0) : null;
                const newBand = band && (i === 0 || ageBand(prevDays ?? 0).label !== band.label);
                return (
                  <li key={deal.opportunity_id}>
                    {newBand && (
                      <p className="mb-2 mt-4 text-xs font-semibold uppercase tracking-wide text-g4-muted first:mt-0">
                        {t.deal.ageBand}: {band.label}
                      </p>
                    )}
                    <DealRow
                      deal={deal}
                      queue={queue}
                      selected={deal.opportunity_id === selected}
                      feedback={fb.byDeal[deal.opportunity_id]}
                      onOpen={openDeal}
                      titleRef={(el) => {
                        if (el) titleRefs.current.set(deal.opportunity_id, el);
                        else titleRefs.current.delete(deal.opportunity_id);
                      }}
                    />
                  </li>
                );
              })}
            </ol>
          )}

          {total > 0 && (
            <nav
              aria-label={t.queue.pagination}
              className="mt-6 flex items-center justify-between gap-4 text-sm"
            >
              <button
                type="button"
                className="btn-secondary"
                disabled={!hasPrev}
                onClick={() => update({ offset: Math.max(0, state.offset - limit) })}
              >
                {t.queue.previous}
              </button>
              <span className="text-xs font-medium tabular-nums text-g4-muted">
                {t.queue.page(page.offset + 1, page.offset + items.length, total)}
              </span>
              <button
                type="button"
                className="btn-primary"
                disabled={!hasNext}
                onClick={() => update({ offset: state.offset + limit })}
              >
                {t.queue.more(remaining > 0 ? Math.min(limit, remaining) : limit)}
              </button>
            </nav>
          )}
        </div>
      )}

      {selected && (
        <DealDrawer
          dealId={selected}
          asOf={state.asOf}
          initial={initialDeal}
          actor={state.agent ?? initialDeal?.sales_agent}
          focusAction={focusAction}
          onClose={closeDeal}
          returnFocus={returnFocus}
        />
      )}
    </div>
  );
}
