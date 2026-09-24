import type { Confidence } from '../api/client';
import { t } from '../i18n/pt-BR';

const ICON: Record<Confidence, string> = { alta: '●', media: '◐', baixa: '○' };

export function ConfidenceBadge({ level }: { level: Confidence }) {
  return (
    <span
      className="inline-flex items-center gap-1 whitespace-nowrap text-xs font-medium text-g4-muted"
      title={t.confidence.hint[level]}
    >
      <span aria-hidden="true" className="text-g4-navy700">
        {ICON[level]}
      </span>
      {t.confidence[level]}
    </span>
  );
}
