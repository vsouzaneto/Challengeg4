import type { Tier } from '../api/client';
import { t } from '../i18n/pt-BR';

// Contrast per docs/design/design-tokens.md §2: A gold + navy text, B navy + white,
// C/D tinted background + dark text (white on C/D fails AA).
const TIER_CLASS: Record<Tier, string> = {
  A: 'bg-tier-A text-g4-primary',
  B: 'bg-tier-B text-white',
  C: 'bg-tier-Cbg text-tier-Ctext',
  D: 'bg-tier-Dbg text-tier-Dtext',
};

export function TierBadge({ tier, size = 'md' }: { tier: Tier; size?: 'md' | 'sm' }) {
  const dims = size === 'md' ? 'h-7 w-7 text-sm' : 'h-6 w-6 text-xs';
  return (
    <span
      role="img"
      className={`inline-flex shrink-0 items-center justify-center rounded font-bold ${dims} ${TIER_CLASS[tier]}`}
      aria-label={t.a11y.tierBadge(tier, t.tierHint[tier])}
      title={t.tierHint[tier]}
    >
      {tier}
    </span>
  );
}
