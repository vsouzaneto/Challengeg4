import { OPERATIONAL_TIME_ZONE } from './config';
import type { DayKey } from './types';

export function operationalDayKey(now: Date = new Date()): DayKey {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: OPERATIONAL_TIME_ZONE,
    year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(now);
  const part = (type: string) => parts.find((item) => item.type === type)!.value;
  return `${part('year')}-${part('month')}-${part('day')}` as DayKey;
}

export function nextCalendarDay(dayKey: DayKey): DayKey {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dayKey)) throw new Error('Data operacional inválida.');
  const date = new Date(`${dayKey}T12:00:00.000Z`);
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== dayKey) {
    throw new Error('Data operacional inválida.');
  }
  date.setUTCDate(date.getUTCDate() + 1);
  return date.toISOString().slice(0, 10) as DayKey;
}

export function greeting(now: Date = new Date()): string {
  const hour = Number(new Intl.DateTimeFormat('en-US', {
    timeZone: OPERATIONAL_TIME_ZONE, hour: '2-digit', hourCycle: 'h23',
  }).format(now));
  return hour < 12 ? 'Bom dia' : hour < 18 ? 'Boa tarde' : 'Boa noite';
}
