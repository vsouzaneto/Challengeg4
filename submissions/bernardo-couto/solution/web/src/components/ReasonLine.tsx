import type { Direction, Reason } from '../api/client';
import { t } from '../i18n/pt-BR';
import { fmtWeight } from '../lib/format';

const ICON: Record<Direction, string> = { '+': '▲', '-': '▼', i: 'ℹ' };
const COLOR: Record<Direction, string> = {
  '+': 'text-signal-pos',
  '-': 'text-signal-neg',
  i: 'text-g4-muted',
};

/** Direction is conveyed by icon + sr-only text + signed weight; color is redundant. */
export function ReasonLine({ reason, withWeight }: { reason: Reason; withWeight?: boolean }) {
  const pts = fmtWeight(reason.weight);
  return (
    <span className="flex items-start gap-2 text-sm">
      <span aria-hidden="true" className={`w-4 shrink-0 text-center ${COLOR[reason.direction]}`}>
        {ICON[reason.direction]}
      </span>
      <span className="sr-only">
        {t.direction[reason.direction]}
        {withWeight ? `, ${t.deal.pointsSr(pts)}` : '.'}
      </span>
      {withWeight && (
        <span className={`w-14 shrink-0 tabular-nums font-semibold ${COLOR[reason.direction]}`}>
          {t.deal.points(pts)}
        </span>
      )}
      <span className="min-w-0">{reason.text_pt}</span>
    </span>
  );
}

export function MainReason({ reason }: { reason: Reason }) {
  return (
    <span className="flex min-w-0 items-center gap-2 text-sm" title={reason.text_pt}>
      <span aria-hidden="true" className={`w-4 shrink-0 text-center ${COLOR[reason.direction]}`}>
        {ICON[reason.direction]}
      </span>
      <span className="sr-only">{t.direction[reason.direction]}.</span>
      <span className="truncate">{reason.text_pt}</span>
    </span>
  );
}
