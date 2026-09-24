// Reads models/latest/metrics.json as served by GET /api/v1/model/metrics (`metrics`).
// Layout: docs/specs/scoring-spec.md §8. Tolerant: every block is optional and hidden
// when absent — the UI never computes a metric, it only picks and formats what is there.

export type BaselineKey = 'scorer' | 'newest' | 'price' | 'base_rate' | 'random';
export const BASELINE_ORDER: BaselineKey[] = ['scorer', 'newest', 'price', 'base_rate', 'random'];

export interface BaselineRow {
  key: BaselineKey;
  precisionAt10: number; // 0..1
  ci?: [number, number];
  revenueCaptureTop20?: number;
  liftTopDecile?: number;
}

export interface CalibrationBin {
  label: string; // "60–62 %"
  actual: number; // 0..1
  count: number;
}

export interface QualityView {
  cuts: string[];
  cut?: string;
  rows: BaselineRow[];
  verdict?: { kind: 'wins' | 'ties' | 'loses'; delta: number; best: BaselineKey };
  calibration?: { bins: CalibrationBin[]; meanError?: number; brier?: number };
  coverage?: {
    scored?: number;
    accountKnownRate?: number;
    prospectingCount?: number;
    zombieCount?: number;
  };
  revenue?: { scorer: number; random?: number; ci?: [number, number] };
  lift?: number;
}

type Rec = Record<string, unknown>;
const isRec = (v: unknown): v is Rec => typeof v === 'object' && v !== null && !Array.isArray(v);
const num = (v: unknown): number | undefined =>
  typeof v === 'number' && Number.isFinite(v) ? v : undefined;
const ci = (v: unknown): [number, number] | undefined =>
  Array.isArray(v) && v.length === 2 && num(v[0]) !== undefined && num(v[1]) !== undefined
    ? [v[0] as number, v[1] as number]
    : undefined;

function pickCut(metrics: Rec, requested?: string): { cuts: string[]; cut?: string } {
  const listed = Array.isArray(metrics.cuts)
    ? metrics.cuts.filter((c): c is string => typeof c === 'string')
    : [];
  const backtest = isRec(metrics.backtest) ? Object.keys(metrics.backtest) : [];
  const cuts = [...new Set([...listed, ...backtest])].sort();
  const cut = requested && cuts.includes(requested) ? requested : cuts[cuts.length - 1];
  return { cuts, cut };
}

function pct100(v: number) {
  return Math.round(v * 100);
}

export function adaptMetrics(metrics: unknown, requestedCut?: string): QualityView {
  if (!isRec(metrics)) return { cuts: [], rows: [] };
  const { cuts, cut } = pickCut(metrics, requestedCut);
  const backtest =
    isRec(metrics.backtest) && cut && isRec(metrics.backtest[cut])
      ? (metrics.backtest[cut] as Rec)
      : undefined;
  const baselines = isRec(metrics.baselines) ? metrics.baselines : {};
  const summary = isRec(metrics.summary) ? metrics.summary : {};

  const rows: BaselineRow[] = [];
  const readRow = (key: BaselineKey, src: Rec | undefined) => {
    const p = num(src?.precision_at_10);
    if (p === undefined) return;
    rows.push({
      key,
      precisionAt10: p,
      ci: ci(src?.precision_at_10_ci),
      revenueCaptureTop20: num(src?.revenue_capture_top20),
      liftTopDecile: num(src?.lift_top_decile),
    });
  };
  readRow('scorer', backtest);
  for (const key of BASELINE_ORDER) {
    if (key === 'scorer') continue;
    const b = baselines[key];
    if (isRec(b) && cut && isRec(b[cut])) readRow(key, b[cut] as Rec);
  }

  let verdict: QualityView['verdict'];
  const scorer = rows.find((r) => r.key === 'scorer');
  const others = rows.filter((r) => r.key !== 'scorer');
  if (scorer && others.length) {
    const best = others.reduce((a, b) => (b.precisionAt10 > a.precisionAt10 ? b : a));
    const delta = (scorer.precisionAt10 - best.precisionAt10) * 10;
    let kind: 'wins' | 'ties' | 'loses' = 'ties';
    if (scorer.ci && best.ci) {
      if (scorer.ci[0] > best.ci[1]) kind = 'wins';
      else if (scorer.ci[1] < best.ci[0]) kind = 'loses';
    } else if (Math.abs(delta) >= 0.5) {
      kind = delta > 0 ? 'wins' : 'loses';
    }
    verdict = { kind, delta, best: best.key };
  }

  let calibration: QualityView['calibration'];
  if (backtest && Array.isArray(backtest.calibration_bins)) {
    const bins = backtest.calibration_bins
      .filter(isRec)
      .map((b) => {
        const lo = num(b.p_low);
        const hi = num(b.p_high);
        const actual = num(b.actual);
        const count = num(b.count);
        if (actual === undefined || count === undefined) return null;
        const label =
          lo !== undefined && hi !== undefined
            ? `${pct100(lo)}–${pct100(hi)} %`
            : String(b.bin ?? '');
        return { label, actual, count } satisfies CalibrationBin;
      })
      .filter((b): b is CalibrationBin => b !== null);
    if (bins.length) {
      calibration = {
        bins,
        meanError: num(summary.mean_calibration_error),
        brier: num(backtest.brier),
      };
    }
  }

  const coverage = {
    scored: num(summary.coverage),
    accountKnownRate: num(summary.account_known_rate),
    prospectingCount: num(summary.prospecting_count),
    zombieCount: num(summary.zombie_count),
  };
  const hasCoverage = Object.values(coverage).some((v) => v !== undefined);

  let revenue: QualityView['revenue'];
  const rc = num(backtest?.revenue_capture_top20);
  if (rc !== undefined) {
    const rnd =
      isRec(baselines.random) && cut && isRec(baselines.random[cut])
        ? num((baselines.random[cut] as Rec).revenue_capture_top20)
        : undefined;
    revenue = { scorer: rc, random: rnd, ci: ci(backtest?.revenue_capture_top20_ci) };
  }

  return {
    cuts,
    cut,
    rows,
    verdict,
    calibration,
    coverage: hasCoverage ? coverage : undefined,
    revenue,
    lift: num(backtest?.lift_top_decile),
  };
}
