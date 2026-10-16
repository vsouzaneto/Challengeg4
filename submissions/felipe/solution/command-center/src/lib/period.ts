import type { Conta } from "../types";

export function formatMonthLabel(m: string): string {
  const [y, mo] = m.split("-");
  const names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
  const idx = parseInt(mo, 10) - 1;
  return `${names[idx] ?? mo}/${y?.slice(2) ?? ""}`;
}

function monthOf(iso?: string | null): string | null {
  if (!iso) return null;
  return iso.slice(0, 7);
}

export function monthInRange(month: string, start: string, end: string): boolean {
  const s = start || "0000-01";
  const e = end || "9999-12";
  return month >= s && month <= e;
}

export function accountInPeriod(c: Conta, start: string, end: string): boolean {
  if (!start && !end) return true;
  const s = start || "0000-01";
  const e = end || "9999-12";
  const months = [monthOf(c.data_cadastro), monthOf(c.data_ultimo_churn), monthOf(c.data_ultimo_uso)];
  return months.some((m) => m != null && m >= s && m <= e);
}

export function lastNMonthsRange(months: string[], n: number): { inicio: string; fim: string } {
  if (!months.length) return { inicio: "", fim: "" };
  const fim = months[months.length - 1];
  const inicio = months[Math.max(0, months.length - n)];
  return { inicio, fim };
}
