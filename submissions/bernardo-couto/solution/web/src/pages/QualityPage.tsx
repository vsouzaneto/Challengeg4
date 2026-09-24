import { useState } from 'react';
import { ApiError } from '../api/client';
import { useModelMetrics } from '../api/queries';
import { HBarChart } from '../components/HBarChart';
import { BlockSkeleton } from '../components/Skeleton';
import { ApiErrorBanner, ArtifactsMissing } from '../components/States';
import { Tile } from '../components/Tile';
import { WhatItDoesNotDo } from '../components/WhatItDoesNotDo';
import { adaptMetrics, type BaselineKey } from '../features/quality/metricsAdapter';
import { t } from '../i18n/pt-BR';
import { fmtDate, fmtInt, fmtPct } from '../lib/format';

const fmt1 = (v: number) => v.toFixed(1).replace('.', ',');
const ROW_ORDER = ['scorer', 'random', 'newest', 'price', 'base_rate'];

export function QualityPage() {
  const query = useModelMetrics();
  const [cut, setCut] = useState<string | undefined>();

  if (query.isPending) {
    return (
      <div className="space-y-6">
        <BlockSkeleton className="h-12" />
        <BlockSkeleton className="h-64" />
      </div>
    );
  }
  if (query.isError) {
    if (query.error instanceof ApiError && query.error.artifactsMissing) {
      return (
        <ArtifactsMissing title={t.states.metricsMissing} body={t.states.metricsMissingBody} />
      );
    }
    return (
      <ApiErrorBanner
        error={query.error}
        onRetry={() => query.refetch()}
        title={t.states.apiErrorTitleGeneric}
        standalone
      />
    );
  }

  const res = query.data;
  const view = adaptMetrics(res.metrics, cut);
  const tenOf = (v: number) => t.quality.outOf10(v * 10);
  const ciOf = (lo: number, hi: number) => t.quality.ci(lo * 10, hi * 10);
  const scorerRow = view.rows.find((r) => r.key === 'scorer');
  const randomRow = view.rows.find((r) => r.key === 'random') ?? scorerRow;
  const priceRow = view.rows.find((r) => r.key === 'price');
  const rows = [...view.rows]
    .sort((a, b) => ROW_ORDER.indexOf(a.key) - ROW_ORDER.indexOf(b.key))
    .map((r) => ({
      key: r.key,
      label: t.quality.baselines[r.key as BaselineKey],
      value: r.precisionAt10,
      ci: r.ci,
      highlight: r.key === 'scorer',
    }));

  return (
    <div>
      <h1 className="font-serif text-2xl font-bold">{t.quality.title(res.model_version)}</h1>
      <p className="mt-1 text-sm text-g4-muted">
        {view.cuts.length
          ? t.quality.intro(view.cuts.map(fmtDate).join(' e '))
          : t.quality.introNoCuts}
      </p>
      {view.cuts.length > 1 && (
        <div className="mt-3">
          <label htmlFor="cut" className="mr-2 text-xs font-semibold text-g4-muted">
            {t.quality.cutLabel}
          </label>
          <select
            id="cut"
            className="select inline-block w-44"
            value={view.cut ?? ''}
            onChange={(e) => setCut(e.target.value)}
          >
            {view.cuts.map((c) => (
              <option key={c} value={c}>
                {fmtDate(c)}
              </option>
            ))}
          </select>
        </div>
      )}

      <section aria-labelledby="q1" className="card mt-6 p-4">
        <h2 id="q1" className="text-xl font-semibold">
          1. {t.quality.q1}
        </h2>
        <p className="mt-1 text-sm text-g4-muted">{t.quality.q1Sub}</p>
        {rows.length ? (
          <>
            {view.verdict && scorerRow && randomRow && (
              <p className="mt-3 text-sm font-semibold">
                {view.verdict.kind === 'wins' &&
                  t.quality.wins(
                    view.verdict.delta.toFixed(1).replace('.', ','),
                    t.quality.baselines[view.verdict.best],
                  )}
                {view.verdict.kind === 'ties' &&
                  t.quality.ties(
                    fmt1(scorerRow.precisionAt10 * 10),
                    fmt1(randomRow.precisionAt10 * 10),
                  )}
                {view.verdict.kind === 'loses' &&
                  t.quality.loses(
                    fmt1(scorerRow.precisionAt10 * 10),
                    fmt1(randomRow.precisionAt10 * 10),
                  )}
              </p>
            )}
            <HBarChart
              data={rows}
              max={1}
              formatValue={tenOf}
              formatCi={ciOf}
              ariaLabel={t.quality.chartLabel}
            />
            <p className="mt-2 text-xs font-medium text-g4-muted">
              <span aria-hidden="true">ⓘ </span>
              {t.quality.ciHint}
            </p>
          </>
        ) : (
          <p className="mt-3 text-sm text-g4-muted">{t.quality.unavailable}</p>
        )}
      </section>

      <section aria-labelledby="q2" className="card mt-6 p-4">
        <h2 id="q2" className="text-xl font-semibold">
          2. {t.quality.q2}
        </h2>
        {view.calibration ? (
          <>
            <table className="mt-3 w-full text-sm tabular-nums">
              <thead>
                <tr className="text-left text-xs font-semibold text-g4-muted">
                  <th scope="col" className="py-1">
                    {t.quality.calibrationCols.predicted}
                  </th>
                  <th scope="col" className="py-1">
                    {t.quality.calibrationCols.actual}
                  </th>
                  <th scope="col" className="py-1 text-right">
                    {t.quality.calibrationCols.deals}
                  </th>
                </tr>
              </thead>
              <tbody>
                {view.calibration.bins.map((b) => (
                  <tr key={b.label} className="border-t border-g4line">
                    <th scope="row" className="py-1 text-left font-semibold">
                      {b.label}
                    </th>
                    <td className="py-1">
                      <span className="flex items-center gap-2">
                        <span
                          aria-hidden="true"
                          className="h-3 rounded-sm bg-g4-navy700"
                          style={{ width: `${Math.round(b.actual * 100)}%`, maxWidth: '160px' }}
                        />
                        {fmtPct(b.actual)} %
                      </span>
                    </td>
                    <td className="py-1 text-right">{fmtInt(b.count)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {view.calibration.meanError !== undefined && (
              <p className="mt-3 text-sm font-semibold">
                {t.quality.calibrationSummary(Math.round(view.calibration.meanError * 100))}
              </p>
            )}
          </>
        ) : (
          <p className="mt-3 text-sm text-g4-muted">{t.quality.unavailable}</p>
        )}
      </section>

      <section aria-labelledby="q3" className="card mt-6 p-4">
        <h2 id="q3" className="text-xl font-semibold">
          3. {t.quality.q3}
        </h2>
        {view.coverage ? (
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            {view.coverage.scored !== undefined && (
              <Tile
                value="100 %"
                label={t.quality.coverageAll(fmtInt(view.coverage.scored)).replace(/^100 % /, '')}
              />
            )}
            {view.coverage.accountKnownRate !== undefined && (
              <Tile
                value={`${fmtPct(view.coverage.accountKnownRate)} %`}
                label={t.quality
                  .coverageAccount(Number(fmtPct(view.coverage.accountKnownRate)))
                  .replace(/^\d+ % /, '')}
              />
            )}
            {view.coverage.prospectingCount !== undefined && (
              <Tile
                value={fmtInt(view.coverage.prospectingCount)}
                label={t.quality
                  .coverageProspecting(fmtInt(view.coverage.prospectingCount))
                  .replace(/^[\d.]+ /, '')}
              />
            )}
            {view.coverage.zombieCount !== undefined && (
              <Tile
                value={fmtInt(view.coverage.zombieCount)}
                label={t.quality
                  .coverageZombies(fmtInt(view.coverage.zombieCount))
                  .replace(/^[\d.]+ /, '')}
              />
            )}
          </div>
        ) : (
          <p className="mt-3 text-sm text-g4-muted">{t.quality.unavailable}</p>
        )}
      </section>

      <section aria-labelledby="q4" className="card mt-6 p-4">
        <h2 id="q4" className="text-xl font-semibold">
          4. {t.quality.q4}
        </h2>
        {view.revenue ? (
          <p className="mt-3 text-sm">
            {t.quality.revenue(
              Number(fmtPct(view.revenue.scorer)),
              view.revenue.random !== undefined ? Number(fmtPct(view.revenue.random)) : 20,
              priceRow?.revenueCaptureTop20 !== undefined
                ? Number(fmtPct(priceRow.revenueCaptureTop20))
                : undefined,
            )}
            {view.lift !== undefined && (
              <> {t.quality.lift(view.lift.toFixed(1).replace('.', ','))}</>
            )}
          </p>
        ) : (
          <p className="mt-3 text-sm text-g4-muted">{t.quality.unavailable}</p>
        )}
      </section>

      <div className="mt-6">
        <WhatItDoesNotDo />
      </div>
      <p className="mt-6 text-xs font-medium text-g4-muted">{t.quality.limits}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {res.model_card_markdown && (
          <details className="w-full">
            <summary className="btn-secondary cursor-pointer">{t.quality.modelCard}</summary>
            <pre className="card mt-3 max-h-96 overflow-auto whitespace-pre-wrap p-4 text-xs">
              {res.model_card_markdown}
            </pre>
          </details>
        )}
        <a className="btn-secondary" href="/docs" target="_blank" rel="noreferrer">
          {t.quality.swagger}
        </a>
      </div>
    </div>
  );
}
