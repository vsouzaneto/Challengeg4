import { METRICS } from '../../mocks/fixtures';
import { adaptMetrics } from './metricsAdapter';

describe('metricsAdapter', () => {
  it('reads the scoring-spec §8 layout and picks the latest cut', () => {
    const v = adaptMetrics(METRICS.metrics);
    expect(v.cut).toBe('2017-09-30');
    expect(v.cuts).toEqual(['2017-06-30', '2017-09-30']);
    expect(v.rows.map((r) => r.key)).toEqual(['scorer', 'newest', 'price', 'base_rate', 'random']);
    expect(v.verdict).toMatchObject({ kind: 'ties', best: 'random' });
    expect(v.calibration?.bins).toHaveLength(5);
    expect(v.calibration?.bins[0]).toEqual({ label: '40–50 %', actual: 0.46, count: 118 });
    expect(v.coverage).toEqual({
      scored: 2089,
      accountKnownRate: 0.32,
      prospectingCount: 500,
      zombieCount: 1291,
    });
    expect(v.revenue).toEqual({ scorer: 0.359, random: 0.206, ci: [0.305, 0.398] });
    expect(v.lift).toBe(1.14);
  });

  it('honours a requested cut and hides blocks that are missing', () => {
    const v = adaptMetrics(METRICS.metrics, '2017-06-30');
    expect(v.cut).toBe('2017-06-30');
    expect(adaptMetrics({})).toEqual({ cuts: [], rows: [] });
    expect(adaptMetrics(null).rows).toEqual([]);
    const partial = adaptMetrics({ backtest: { '2017-09-30': { precision_at_10: 0.7 } } });
    expect(partial.rows).toHaveLength(1);
    expect(partial.verdict).toBeUndefined();
    expect(partial.calibration).toBeUndefined();
  });

  it('declares a win only when the intervals do not overlap', () => {
    const m = {
      backtest: { c: { precision_at_10: 0.8, precision_at_10_ci: [0.75, 0.85] } },
      baselines: { random: { c: { precision_at_10: 0.6, precision_at_10_ci: [0.55, 0.65] } } },
    };
    expect(adaptMetrics(m).verdict).toMatchObject({ kind: 'wins', best: 'random' });
    expect(adaptMetrics(m).verdict?.delta).toBeCloseTo(2);
  });
});
