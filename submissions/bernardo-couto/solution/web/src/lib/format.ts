// Presentation-only formatting. No score/tier/urgency logic lives here.
const brl = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});
const brlCompact = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  notation: 'compact',
  maximumFractionDigits: 1,
});
const int = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });

export const fmtBRL = (v: number) => brl.format(v);
export const fmtBRLCompact = (v: number) => brlCompact.format(v);
export const fmtInt = (v: number) => int.format(v);
export const fmtPct = (ratio: number) => `${Math.round(ratio * 100)}`;
export const fmtScore = (v: number) => Math.round(v);

/** ISO date (YYYY-MM-DD) -> dd/mm/aaaa, without timezone shifts. */
export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
}

export function fmtTime(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? '—'
    : d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

/** Reason weight is already in priority_score points (0–100); |w| < 1 are genuine sub-point values. */
export function fmtWeight(weight: number): string {
  const abs = Math.abs(weight).toFixed(1).replace('.', ',');
  if (abs === '0,0') return '0,0';
  return weight > 0 ? `+${abs}` : `−${abs}`;
}

export const STALE_DAYS = 100; // p90 of the Won cycle (ux-spec §3.2 item 9) — display threshold only

export function median(values: number[]): number {
  if (values.length === 0) return 0;
  const s = [...values].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid]! : Math.round((s[mid - 1]! + s[mid]!) / 2);
}
