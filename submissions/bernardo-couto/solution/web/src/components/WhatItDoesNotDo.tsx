import { useState } from 'react';
import { t } from '../i18n/pt-BR';

const KEY = 'lead-scorer.not-list.dismissed';

/** The eight "this tool does not…" statements (revops-review §3d). */
export function WhatItDoesNotDo({ compact = false }: { compact?: boolean }) {
  return (
    <section aria-labelledby="not-title" className={compact ? '' : 'card p-4'}>
      <h2 id="not-title" className="text-xl font-semibold">
        {t.quality.notTitle}
      </h2>
      <ol className="mt-2 list-decimal space-y-1 pl-5 text-sm">
        {t.quality.not.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ol>
    </section>
  );
}

/** First-open notice on the queue, dismissable (per-browser convenience only). */
export function FirstOpenNotice() {
  const [dismissed, setDismissed] = useState(() => {
    try {
      return localStorage.getItem(KEY) === '1';
    } catch {
      return false;
    }
  });
  if (dismissed) return null;
  return (
    <div className="card mb-6 border-g4-navy700 p-4">
      <WhatItDoesNotDo compact />
      <button
        type="button"
        className="btn-primary mt-3"
        onClick={() => {
          try {
            localStorage.setItem(KEY, '1');
          } catch {
            /* storage unavailable */
          }
          setDismissed(true);
        }}
      >
        {t.quality.notDismiss}
      </button>
    </div>
  );
}
