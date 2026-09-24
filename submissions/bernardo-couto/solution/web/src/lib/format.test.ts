import { fmtBRL, fmtDate, fmtWeight, median } from './format';

describe('format', () => {
  it('formats BRL without cents', () => {
    expect(fmtBRL(3412.5)).toBe('R$\u00a03.413');
  });
  it('formats weights as signed points with one decimal (already in score points)', () => {
    expect(fmtWeight(9)).toBe('+9,0');
    expect(fmtWeight(-18)).toBe('−18,0');
    expect(fmtWeight(0.56)).toBe('+0,6');
    expect(fmtWeight(0.04)).toBe('0,0');
    expect(fmtWeight(-0.04)).toBe('0,0');
  });
  it('formats ISO dates as dd/mm/aaaa without timezone shift', () => {
    expect(fmtDate('2017-12-31')).toBe('31/12/2017');
    expect(fmtDate(null)).toBe('—');
  });
  it('computes a median', () => {
    expect(median([3, 1, 2])).toBe(2);
    expect(median([4, 1, 2, 3])).toBe(3);
    expect(median([])).toBe(0);
  });
});
