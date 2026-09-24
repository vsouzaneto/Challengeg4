import { useEffect, useRef, useState } from 'react';
import type { ScoredDeal } from '../api/client';
import { useDeal, useModelMetrics } from '../api/queries';
import { UI_TO_API, useFeedback, type UiAction } from '../features/feedback/feedbackStore';
import { t } from '../i18n/pt-BR';
import { fmtBRL, fmtPct, fmtScore, fmtTime } from '../lib/format';
import { isStale, splitReasons } from '../lib/reasons';
import { ConfidenceBadge } from './ConfidenceBadge';
import { Dialog } from './Dialog';
import { ReasonLine } from './ReasonLine';
import { BlockSkeleton } from './Skeleton';
import { QueryError } from './States';
import { TierBadge } from './TierBadge';

interface Props {
  dealId: string;
  asOf?: string;
  /** Row data already loaded, shown while the detail request is in flight. */
  initial?: ScoredDeal;
  actor?: string;
  focusAction?: UiAction;
  onClose: () => void;
  returnFocus: () => HTMLElement | null;
}

const ACTIONS: { key: UiAction; label: string }[] = [
  { key: 'contacted', label: t.actions.contacted },
  { key: 'meeting', label: t.actions.meeting },
  { key: 'proposal', label: t.actions.proposal },
];

/** MODEL_CONTRIBUTION is hidden while the model runs in shadow mode (blend weight 0). */
function useModelWeight(): number {
  const metrics = useModelMetrics();
  const m = metrics.data?.metrics as Record<string, unknown> | undefined;
  const summary = (m?.summary ?? {}) as Record<string, unknown>;
  const w = (summary.blend_model_weight ?? m?.blend_model_weight ?? 0) as unknown;
  return typeof w === 'number' ? w : 0;
}

export function DealDrawer({
  dealId,
  asOf,
  initial,
  actor,
  focusAction,
  onClose,
  returnFocus,
}: Props) {
  const query = useDeal(dealId, asOf);
  const deal = query.data ?? initial;
  const modelWeight = useModelWeight();
  const titleRef = useRef<HTMLHeadingElement>(null);
  const accountFixedRef = useRef<HTMLButtonElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  const [confirmDiscard, setConfirmDiscard] = useState(false);
  const { state, record, undo } = useFeedback();
  const fb = state.byDeal[dealId];

  useEffect(() => {
    if (confirmDiscard) cancelRef.current?.focus();
  }, [confirmDiscard]);

  const act = (action: UiAction) => {
    if (!deal) return;
    record(deal.opportunity_id, action, actor ?? deal.sales_agent);
    setConfirmDiscard(false);
  };

  const account = deal?.account ?? t.deal.accountUnknown;
  const reasons = deal ? splitReasons(deal.reasons, modelWeight > 0) : { score: [], context: [] };
  const stale = deal ? isStale(deal) : false;
  const pressed = (key: UiAction) => fb?.action === key && fb.status !== 'error';

  return (
    <Dialog
      labelledBy="deal-title"
      describedBy="deal-summary"
      onClose={onClose}
      returnFocus={returnFocus}
      initialFocus={() =>
        focusAction === 'accountFixed' ? accountFixedRef.current : titleRef.current
      }
      className="w-drawer p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          {deal && (
            <div className="flex items-center gap-3">
              <TierBadge tier={deal.tier} />
              <span className="text-xl font-bold tabular-nums">
                <span aria-hidden="true">{fmtScore(deal.priority_score)}</span>
                <span className="sr-only">{t.deal.score(fmtScore(deal.priority_score))}</span>
              </span>
              <h2
                id="deal-title"
                ref={titleRef}
                tabIndex={-1}
                className="truncate text-xl font-semibold outline-none"
              >
                {deal.account ? (
                  deal.account
                ) : (
                  <span className="italic text-g4-muted">{account}</span>
                )}
                <span className="text-g4-muted"> · </span>
                {deal.product}
              </h2>
            </div>
          )}
          {!deal && (
            <h2 id="deal-title" ref={titleRef} tabIndex={-1} className="text-xl font-semibold">
              {t.states.loadingGeneric}
            </h2>
          )}
        </div>
        <button
          type="button"
          className="btn-secondary h-10 w-10 shrink-0 px-0 text-xl"
          aria-label={t.deal.close}
          onClick={onClose}
        >
          <span aria-hidden="true">×</span>
        </button>
      </div>

      {query.isError && !deal && (
        <div className="mt-6">
          <QueryError error={query.error} onRetry={() => query.refetch()} title={t.deal.notFound} />
        </div>
      )}
      {!deal && query.isPending && (
        <div className="mt-6">
          <BlockSkeleton className="h-64" />
        </div>
      )}

      {deal && (
        <>
          <p id="deal-summary" className="mt-2 text-sm text-g4-muted">
            {deal.sales_agent} · {deal.regional_office} ·{' '}
            {deal.days_in_engaging === null || deal.days_in_engaging === undefined
              ? t.deal.prospecting
              : t.deal.engagingSince(deal.days_in_engaging)}
            <br />
            {stale
              ? t.deal.noHistoryAtAge
              : t.deal.productRate(Number(fmtPct(deal.p_win)), deal.product)}{' '}
            ·{' '}
            {stale && deal.sales_price != null
              ? `${fmtBRL(deal.sales_price)} ${t.deal.nominalOutOfForecast}`
              : `${fmtBRL(deal.expected_value)} ${t.deal.expected}`}{' '}
            · <ConfidenceBadge level={deal.confidence} />
          </p>

          <section aria-labelledby="deal-next" className="mt-6 border-t border-g4line pt-4">
            <h3
              id="deal-next"
              className="text-xs font-semibold uppercase tracking-wide text-g4-muted"
            >
              <span aria-hidden="true">→ </span>
              {t.deal.nextAction}
            </h3>
            <p className="mt-1 text-base font-semibold text-g4-navy700">{deal.next_action}</p>
          </section>

          <section aria-labelledby="deal-why" className="mt-6">
            <h3
              id="deal-why"
              className="text-xs font-semibold uppercase tracking-wide text-g4-muted"
            >
              {t.deal.whyTitle}
            </h3>
            <ul aria-label={t.deal.reasonsLabel} className="mt-2 space-y-2">
              {reasons.score.map((r, i) => (
                <li key={`${r.code}-${i}`}>
                  <ReasonLine reason={r} withWeight />
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs font-medium text-g4-muted">
              <span aria-hidden="true">ⓘ </span>
              {t.deal.whyHint}
            </p>
          </section>

          {reasons.context.length > 0 && (
            <section aria-labelledby="deal-context" className="mt-6">
              <h3
                id="deal-context"
                className="text-xs font-semibold uppercase tracking-wide text-g4-muted"
              >
                {t.deal.contextTitle}
              </h3>
              <ul aria-label={t.deal.contextLabel} className="mt-2 space-y-2">
                {reasons.context.map((r, i) => (
                  <li key={`${r.code}-${i}`}>
                    <ReasonLine reason={r} />
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-xs font-medium text-g4-muted">{t.deal.contextHint}</p>
            </section>
          )}

          {deal.account ? (
            <section aria-labelledby="deal-history" className="mt-6">
              <h3
                id="deal-history"
                className="text-xs font-semibold uppercase tracking-wide text-g4-muted"
              >
                {t.deal.historyTitle}
              </h3>
              {/* Account facts (sector, size, previous deals) need an API endpoint (ux-spec B3); only the name is shown. */}
              <p className="mt-1 text-sm">
                {t.deal.accountLabel}: <span className="font-semibold">{deal.account}</span>
              </p>
            </section>
          ) : (
            <div className="mt-6 flex items-start gap-2 rounded bg-g4-highlight/20 px-3 py-2 text-sm">
              <span aria-hidden="true">⚠</span>
              <p>{t.deal.accountUnknownWarning}</p>
            </div>
          )}

          <section aria-labelledby="deal-actions" className="mt-6 border-t border-g4line pt-4">
            <h3
              id="deal-actions"
              className="text-xs font-semibold uppercase tracking-wide text-g4-muted"
            >
              {t.actions.title}
            </h3>
            <div role="group" aria-label={t.actions.title} className="mt-3 flex flex-wrap gap-2">
              {ACTIONS.map((a) => (
                <button
                  key={a.key}
                  type="button"
                  className={`btn-secondary ${pressed(a.key) ? 'border-g4-navy700 bg-g4-tintNavy text-g4-primary' : ''}`}
                  aria-pressed={pressed(a.key)}
                  onClick={() => act(a.key)}
                >
                  {a.label}
                </button>
              ))}
              <button
                type="button"
                className="btn-danger"
                aria-pressed={pressed('discard')}
                onClick={() => setConfirmDiscard(true)}
              >
                {t.actions.discard}
              </button>
              <button
                type="button"
                className={`btn-secondary ${pressed('closedInCrm') ? 'border-g4-navy700 bg-g4-tintNavy text-g4-primary' : ''}`}
                aria-pressed={pressed('closedInCrm')}
                title={t.actions.closedInCrmHint}
                onClick={() => act('closedInCrm')}
              >
                {t.actions.closedInCrm}
              </button>
              <button
                ref={accountFixedRef}
                type="button"
                className={`${deal.account ? 'btn-secondary' : 'btn-action'} ${pressed('accountFixed') ? 'border-g4-navy700' : ''}`}
                aria-pressed={pressed('accountFixed')}
                onClick={() => act('accountFixed')}
              >
                {t.actions.accountFixed}
              </button>
            </div>

            <p className="mt-2 text-xs font-medium text-g4-muted">{t.actions.closedInCrmHint}</p>
            {confirmDiscard && (
              <div
                role="alertdialog"
                aria-labelledby="discard-confirm"
                className="mt-3 rounded border border-g4-risk bg-signal-negBg p-3 text-sm"
              >
                <p id="discard-confirm" className="font-semibold text-g4-risk">
                  {t.actions.discardConfirm}
                </p>
                <div className="mt-2 flex gap-2">
                  <button
                    ref={cancelRef}
                    type="button"
                    className="btn-secondary h-8 text-xs"
                    onClick={() => setConfirmDiscard(false)}
                  >
                    {t.actions.cancel}
                  </button>
                  <button
                    type="button"
                    className="btn-danger h-8 text-xs"
                    onClick={() => act('discard')}
                  >
                    {t.actions.confirm}
                  </button>
                </div>
              </div>
            )}

            <div role="status" aria-live="polite" className="mt-3 min-h-6 text-sm">
              {fb && fb.status === 'pending' && (
                <span className="text-g4-muted">{t.actions.recording(labelOf(fb.action))}</span>
              )}
              {fb && fb.status === 'ok' && (
                <span>
                  <span aria-hidden="true">✓ </span>
                  {t.actions.recorded(
                    labelOf(fb.action),
                    fb.recordedAt ? fmtTime(fb.recordedAt) : '—',
                  )}
                  {' · '}
                  <button
                    type="button"
                    className="rounded underline"
                    title={t.actions.undoHint}
                    onClick={() => undo(deal.opportunity_id)}
                  >
                    {t.actions.undo}
                  </button>
                </span>
              )}
            </div>
            {fb && fb.status === 'error' && (
              <p role="alert" className="mt-2 text-sm font-semibold text-g4-risk">
                {t.actions.error}{' '}
                <button type="button" className="rounded underline" onClick={() => act(fb.action)}>
                  {t.actions.retry}
                </button>
              </p>
            )}
          </section>
        </>
      )}
    </Dialog>
  );
}

function labelOf(action: UiAction): string {
  switch (action) {
    case 'contacted':
      return t.actions.contacted;
    case 'meeting':
      return t.actions.meeting;
    case 'proposal':
      return t.actions.proposal;
    case 'discard':
      return t.actions.discard;
    case 'accountFixed':
      return t.actions.accountFixed;
    case 'closedInCrm':
      return t.actions.closedInCrm;
  }
}

export { UI_TO_API };
