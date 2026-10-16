/* Estado compartilhado: dados carregados, filtros globais e preferências. */
import { readStore, writeStore } from "./format.js";

const PREFS_KEY = "lead-kanban-prefs-v1";
const ACTIONS_KEY = "lead-kanban-actions-v1";

export const state = {
  data: null,
  view: "pipeline",
  filters: defaultFilters(),
  sort: "recommended",
  onlyMissing: false,
  groupBy: "manager",
  done: readStore(ACTIONS_KEY, {}),
};

export function defaultFilters() {
  return { region: "", manager: "", agent: "", search: "" };
}

export function loadPrefs() {
  const saved = readStore(PREFS_KEY, null);
  if (!saved) return;
  Object.assign(state.filters, {
    region: saved.region || "", manager: saved.manager || "", agent: saved.agent || "",
  });
  state.sort = saved.sort || state.sort;
  state.onlyMissing = !!saved.onlyMissing;
  state.groupBy = saved.groupBy || state.groupBy;
}

export function savePrefs() {
  const { region, manager, agent } = state.filters;
  writeStore(PREFS_KEY, { region, manager, agent, sort: state.sort, onlyMissing: state.onlyMissing, groupBy: state.groupBy });
}

/* Itens que respeitam os filtros globais da barra de navegação. */
export function scopedItems() {
  const f = state.filters;
  const term = f.search.toLocaleLowerCase("pt-BR").trim();
  return state.data.items.filter((item) => {
    if (f.region && item.region !== f.region) return false;
    if (f.manager && item.manager !== f.manager) return false;
    if (f.agent && item.agent !== f.agent) return false;
    if (term) {
      const hay = [item.id, item.product, item.account || "conta pendente", item.agent].join(" ").toLocaleLowerCase("pt-BR");
      if (!hay.includes(term)) return false;
    }
    return true;
  });
}

export function scopedTeam() {
  const f = state.filters;
  return state.data.team.filter((t) => (!f.region || t.region === f.region)
    && (!f.manager || t.manager === f.manager) && (!f.agent || t.agent === f.agent));
}

export function activeFilterCount() {
  const f = state.filters;
  return [f.region, f.manager, f.agent, f.search.trim()].filter(Boolean).length;
}

export function scopeLabel() {
  const f = state.filters;
  return f.agent || f.manager || f.region || "Toda a operação";
}

/* Ações marcadas no detalhe, salvas apenas neste navegador. */
export function doneFor(item) {
  return (state.done[item.id] || []).filter((i) => i < item.actions.length);
}

export function toggleDone(item, index, checked) {
  const set = new Set(doneFor(item));
  checked ? set.add(index) : set.delete(index);
  if (set.size) state.done[item.id] = [...set].sort(); else delete state.done[item.id];
  writeStore(ACTIONS_KEY, state.done);
  return set.size;
}
