import { describe, expect, it } from 'vitest';
import { nextCalendarDay, operationalDayKey } from '../src/domain/dates';

describe('calendário operacional', () => {
  it('vira o dia em São Paulo e não na meia-noite UTC', () => {
    expect(operationalDayKey(new Date('2026-10-01T02:59:59Z'))).toBe('2026-09-30');
    expect(operationalDayKey(new Date('2026-10-01T03:00:00Z'))).toBe('2026-10-01');
  });
  it('adia pelo calendário em viradas de mês, ano e ano bissexto', () => {
    expect(nextCalendarDay('2026-09-30')).toBe('2026-10-01');
    expect(nextCalendarDay('2026-12-31')).toBe('2027-01-01');
    expect(nextCalendarDay('2028-02-28')).toBe('2028-02-29');
  });
  it('rejeita uma data inexistente', () => {
    expect(() => nextCalendarDay('2026-02-30')).toThrow('Data operacional inválida');
  });
});
