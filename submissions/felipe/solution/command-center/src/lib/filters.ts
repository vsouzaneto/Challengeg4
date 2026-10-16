import { accountInPeriod, monthInRange } from "./period";
import type { Bundle, Conta, FilterState } from "../types";

export function toggleInList(arr: string[], val: string): string[] {
  return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val];
}

export type MultiFilterKey =
  | "status_conta"
  | "industria"
  | "canal_aquisicao"
  | "plano_atual"
  | "faixa_risco";

export function patchMultiFilter(
  state: FilterState,
  key: MultiFilterKey,
  value: string,
): FilterState {
  return { ...state, [key]: toggleInList(state[key], value) };
}

export function applyFilters(contas: Conta[], state: FilterState, medEsc: number): Conta[] {
  return contas.filter((c) => {
    if (state.status_conta.length && !state.status_conta.includes(c.status_conta)) return false;
    if (state.industria.length && !state.industria.includes(c.industria)) return false;
    if (state.canal_aquisicao.length && !state.canal_aquisicao.includes(c.canal_aquisicao))
      return false;
    if (state.plano_atual.length && !state.plano_atual.includes(c.plano_atual)) return false;
    if (state.faixa_risco.length && !state.faixa_risco.includes(String(c.faixa_risco ?? "")))
      return false;
    if (state.em_trial && c.em_trial !== state.em_trial) return false;
    if (state.escalacao_acima && (c.taxa_escalacao_pct ?? 0) / 100 <= medEsc) return false;
    if (!accountInPeriod(c, state.periodo_inicio, state.periodo_fim)) return false;
    return true;
  });
}

export function formatMonth(m: string): string {
  const [y, mo] = m.split("-");
  const names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
  const idx = parseInt(mo, 10) - 1;
  return `${names[idx] ?? mo}/${y?.slice(2) ?? ""}`;
}

export function usageSeries(
  bundle: Bundle,
  filteredIndustries: string[],
  periodoInicio = "",
  periodoFim = "",
  maxSeries = 4,
) {
  let rows = bundle.uso_mensal_por_industria;
  if (periodoInicio || periodoFim) {
    rows = rows.filter((r) => monthInRange(String(r.month), periodoInicio, periodoFim));
  }
  if (filteredIndustries.length) {
    rows = rows.filter((r) => filteredIndustries.includes(r.industry));
  } else {
    const totals: Record<string, number> = {};
    rows.forEach((r) => {
      totals[r.industry] = (totals[r.industry] ?? 0) + r.total_usage;
    });
    const top = Object.entries(totals)
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxSeries)
      .map(([k]) => k);
    rows = rows.filter((r) => top.includes(r.industry));
  }
  const months = [...new Set(rows.map((r) => r.month))].sort();
  const industries = [...new Set(rows.map((r) => r.industry))];
  const palette = ["#b88e5e", "#e8eaed", "#5a7088", "#a68966", "#8a9aab"];
  return {
    months: months.map(formatMonth),
    rawMonths: months,
    datasets: industries.map((ind, i) => ({
      name: ind,
      color: palette[i % palette.length],
      values: months.map((m) => rows.find((r) => r.month === m && r.industry === ind)?.total_usage ?? 0),
    })),
  };
}
