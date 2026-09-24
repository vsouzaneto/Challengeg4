import { useState } from 'react';
import type { Tier } from '../api/client';
import { t } from '../i18n/pt-BR';
import { fmtInt } from '../lib/format';

// Tier fills come from the design tokens; C/D use their tinted backgrounds with dark labels
// so every segment label passes AA. Identity is never color-alone: letter + % inside each
// segment, legend with counts, and a table toggle (dataviz + accessibility.md §5).
const FILL: Record<Tier, string> = {
  A: 'bg-tier-A text-g4-primary',
  B: 'bg-tier-B text-white',
  C: 'bg-tier-Cbg text-tier-Ctext',
  D: 'bg-tier-Dbg text-tier-Dtext',
};
const TIERS: Tier[] = ['A', 'B', 'C', 'D'];

export function StackedBar({ distribution }: { distribution: Record<Tier, number> }) {
  const [table, setTable] = useState(false);
  const total = TIERS.reduce((s, k) => s + distribution[k], 0);
  const pct = (k: Tier) => (total ? Math.round((distribution[k] / total) * 100) : 0);
  const label = TIERS.map((k) => `${k} ${pct(k)} %`).join(', ');

  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">{t.team.tierDistribution}</h2>
        <button
          type="button"
          className="btn-secondary h-8 text-xs"
          aria-pressed={table}
          onClick={() => setTable((v) => !v)}
        >
          {table ? t.team.showChart : t.team.showTable}
        </button>
      </div>
      {table ? (
        <table className="mt-3 w-full text-sm tabular-nums">
          <thead>
            <tr className="text-left text-xs font-semibold text-g4-muted">
              <th scope="col" className="py-1">
                Tier
              </th>
              <th scope="col" className="py-1 text-right">
                Deals
              </th>
              <th scope="col" className="py-1 text-right">
                %
              </th>
            </tr>
          </thead>
          <tbody>
            {TIERS.map((k) => (
              <tr key={k} className="border-t border-g4line">
                <th scope="row" className="py-1 text-left font-semibold">
                  {t.tiers[k]}
                </th>
                <td className="py-1 text-right">{fmtInt(distribution[k])}</td>
                <td className="py-1 text-right">{pct(k)} %</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <>
          <div
            role="img"
            aria-label={t.team.tierDistributionLabel(label)}
            className="mt-3 flex h-10 w-full gap-0.5 overflow-hidden rounded bg-g4-surface"
          >
            {TIERS.map((k) =>
              distribution[k] > 0 ? (
                <div
                  key={k}
                  style={{ width: `${(distribution[k] / Math.max(total, 1)) * 100}%` }}
                  className={`flex items-center justify-center overflow-hidden whitespace-nowrap text-xs font-bold ${FILL[k]}`}
                >
                  {pct(k) >= 8 ? `${k} ${pct(k)} %` : ''}
                </div>
              ) : null,
            )}
          </div>
          <ul className="mt-2 flex flex-wrap gap-4 text-xs font-medium text-g4-muted">
            {TIERS.map((k) => (
              <li key={k} className="flex items-center gap-1">
                <span
                  aria-hidden="true"
                  className={`inline-block h-3 w-3 rounded-sm border border-g4line ${FILL[k].split(' ')[0]}`}
                />
                {t.tiers[k]} · {fmtInt(distribution[k])} ({pct(k)} %)
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
