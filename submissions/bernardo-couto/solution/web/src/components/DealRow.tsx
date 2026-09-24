import type { ScoredDeal } from '../api/client';
import type { DealFeedback } from '../features/feedback/feedbackStore';
import { t } from '../i18n/pt-BR';
import { fmtBRL, fmtScore } from '../lib/format';
import {
  ageBand,
  isCooling,
  isStale,
  mainReason,
  ZOMBIE_DAYS,
  type QueueKind,
} from '../lib/reasons';
import { ConfidenceBadge } from './ConfidenceBadge';
import { MainReason } from './ReasonLine';
import { TierBadge } from './TierBadge';

const ACTION_LABEL = {
  contacted: t.actions.contacted,
  meeting: t.actions.meeting,
  proposal: t.actions.proposal,
  discard: t.actions.discard,
  accountFixed: t.actions.accountFixed,
  closedInCrm: t.actions.closedInCrm,
} as const;

interface Props {
  deal: ScoredDeal;
  selected: boolean;
  feedback?: DealFeedback;
  onOpen: (deal: ScoredDeal, opts?: { focusAction?: 'accountFixed' }) => void;
  titleRef?: (el: HTMLButtonElement | null) => void;
  queue?: QueueKind;
}

/**
 * Rich row (ux-spec §3.2 + revops-review §3c): tier · score · account/product · value ·
 * confidence · main reason · next action · days. In the "confirm" queue there is no tier badge,
 * the value is flagged as out of forecast and the age band is visible. Account unknown = icon +
 * muted text (decision V3); the full banner lives in the drawer.
 */
export function DealRow({ deal, selected, feedback, onOpen, titleRef, queue = 'work' }: Props) {
  const id = deal.opportunity_id;
  const account = deal.account ?? t.deal.accountUnknown;
  const main = mainReason(deal);
  const days = deal.days_in_engaging;
  const stale = isStale(deal);
  const cooling = isCooling(deal);
  const badge = feedback && feedback.status !== 'error' ? ACTION_LABEL[feedback.action] : null;
  const confirmQueue = queue === 'confirm';

  return (
    <article
      aria-labelledby={`deal-${id}-title`}
      aria-describedby={`deal-${id}-meta deal-${id}-reason`}
      className={`card cursor-pointer p-4 transition-colors hover:bg-g4-rowHover focus-within:bg-g4-rowHover ${
        selected ? 'border-g4-navy700 bg-g4-rowSelected' : ''
      }`}
      onClick={() => onOpen(deal)}
    >
      <div className="flex flex-wrap items-start gap-2 sm:flex-nowrap sm:gap-3">
        {confirmQueue ? (
          <span
            className="shrink-0 rounded bg-tier-Dbg px-2 py-1 text-xs font-semibold text-tier-Dtext"
            title={t.deal.ageBand}
          >
            {days !== null && days !== undefined ? ageBand(days).label : t.deal.prospecting}
          </span>
        ) : (
          <>
            <TierBadge tier={deal.tier} />
            <span
              className="w-8 shrink-0 text-xl font-bold tabular-nums leading-7"
              title={t.deal.score(fmtScore(deal.priority_score))}
            >
              <span aria-hidden="true">{fmtScore(deal.priority_score)}</span>
              <span className="sr-only">{t.deal.score(fmtScore(deal.priority_score))}</span>
            </span>
          </>
        )}
        <div className="min-w-0 flex-1">
          <button
            id={`deal-${id}-title`}
            ref={titleRef}
            type="button"
            className="block w-full truncate rounded text-left text-base font-semibold"
            aria-label={t.deal.openDetail(account, deal.product)}
            aria-expanded={selected}
            onClick={(e) => {
              e.stopPropagation();
              onOpen(deal);
            }}
          >
            {deal.account ? (
              <span>{deal.account}</span>
            ) : (
              <span className="italic text-g4-muted">
                <span aria-hidden="true">⚠ </span>
                {t.deal.accountUnknown}
              </span>
            )}
            <span className="text-g4-muted"> · </span>
            <span>{deal.product}</span>
          </button>
          <p id={`deal-${id}-reason`} className="mt-1">
            {main ? <MainReason reason={main} /> : null}
          </p>
          {cooling && days !== null && days !== undefined && (
            <p className="mt-1 text-sm font-semibold text-g4-risk">
              <span aria-hidden="true">⏳ </span>
              {t.deal.countdown(ZOMBIE_DAYS - days)}
            </p>
          )}
          <p className="mt-1 text-sm font-semibold text-g4-navy700">
            <span aria-hidden="true">→ </span>
            <span className="sr-only">{t.deal.nextAction}: </span>
            {deal.next_action}
          </p>
          {badge && (
            <p className="mt-2">
              <span
                className={`inline-flex items-center rounded bg-g4-tintNavy px-2 py-0.5 text-xs font-semibold text-g4-primary ${
                  feedback?.status === 'pending' ? 'opacity-70' : ''
                }`}
              >
                <span aria-hidden="true">✓ </span>
                {t.actions.badgeToday(badge)}
              </span>
            </p>
          )}
        </div>
        <div
          id={`deal-${id}-meta`}
          className="flex w-full shrink-0 flex-row items-center justify-between gap-2 sm:w-auto sm:flex-col sm:items-end"
        >
          <span className="text-base font-semibold tabular-nums">
            {stale && deal.sales_price != null ? (
              <>
                {fmtBRL(deal.sales_price)}{' '}
                <span className="text-xs font-medium text-g4-muted">
                  {t.deal.nominalOutOfForecast}
                </span>
              </>
            ) : (
              <>
                {fmtBRL(deal.expected_value)}{' '}
                <span className="text-xs font-medium text-g4-muted">{t.deal.expected}</span>
              </>
            )}
          </span>
          {stale ? (
            <span className="text-xs font-medium text-g4-muted">{t.deal.noHistoryAtAge}</span>
          ) : (
            <ConfidenceBadge level={deal.confidence} />
          )}
          <span className="text-xs font-medium tabular-nums text-g4-muted">
            {days === null || days === undefined ? (
              t.deal.prospecting
            ) : (
              <>
                {stale && (
                  <span aria-hidden="true" className="mr-1 text-g4-riskDeep">
                    ⏳
                  </span>
                )}
                {stale && <span className="sr-only">{t.deal.staleIcon}, </span>}
                {t.deal.days(days)}
              </>
            )}
          </span>
        </div>
      </div>
      {!deal.account && (
        <div className="mt-3 flex items-center justify-end">
          <button
            type="button"
            className="btn-secondary h-8 px-3 text-xs"
            aria-label={t.deal.accountUnknownCtaLabel(deal.product)}
            onClick={(e) => {
              e.stopPropagation();
              onOpen(deal, { focusAction: 'accountFixed' });
            }}
          >
            {t.deal.accountUnknownCta}
          </button>
        </div>
      )}
    </article>
  );
}
