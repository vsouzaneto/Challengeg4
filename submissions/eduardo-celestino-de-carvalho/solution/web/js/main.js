/* Ponto de entrada: carrega dados, filtros globais e navegação entre telas. */
import { bindInfo, esc } from "./format.js";
import { activeFilterCount, defaultFilters, loadPrefs, savePrefs, state } from "./state.js";
import { bindPipeline, renderPipeline, resetPaging } from "./pipeline.js";
import { bindDashboard, renderDashboard } from "./dashboard.js";
import { bindHelp } from "./help.js";

const $ = (id) => document.getElementById(id);
const el = {
  region: $("f-region"), manager: $("f-manager"), agent: $("f-agent"), search: $("f-search"),
  clear: $("f-clear"), sort: $("f-sort"), missing: $("f-missing"),
  filters: $("filters"), filtersToggle: $("filters-toggle"), filtersCount: $("filters-count"),
  views: { pipeline: $("view-pipeline"), dashboard: $("view-dashboard") },
};

const option = (value, label, selected) =>
  `<option value="${esc(value)}"${selected ? " selected" : ""}>${esc(label)}</option>`;

function populateFilters() {
  const { team } = state.data;
  const f = state.filters;
  const regions = [...new Set(team.map((t) => t.region))].sort();
  if (!regions.includes(f.region)) f.region = "";
  el.region.innerHTML = option("", "Todas as regionais", !f.region) + regions.map((r) => option(r, r, r === f.region)).join("");

  const managers = [...new Set(team.filter((t) => !f.region || t.region === f.region).map((t) => t.manager))].sort();
  if (!managers.includes(f.manager)) f.manager = "";
  el.manager.innerHTML = option("", "Todos os managers", !f.manager) + managers.map((m) => option(m, m, m === f.manager)).join("");

  const agents = team.filter((t) => (!f.region || t.region === f.region) && (!f.manager || t.manager === f.manager)).map((t) => t.agent);
  if (!agents.includes(f.agent)) f.agent = "";
  el.agent.innerHTML = option("", "Todos os vendedores", !f.agent) + agents.map((a) => option(a, a, a === f.agent)).join("");

  el.search.value = f.search;
  el.sort.value = state.sort;
  el.missing.checked = state.onlyMissing;
  const count = activeFilterCount();
  el.filtersCount.textContent = count ? `· ${count}` : "";
  el.clear.hidden = !count;
  for (const select of [el.region, el.manager, el.agent]) select.classList.toggle("is-set", !!select.value);
}

function render() {
  if (!state.data) return;
  if (state.view === "dashboard") renderDashboard(); else renderPipeline();
}

function onFiltersChanged() {
  populateFilters();
  resetPaging();
  savePrefs();
  render();
}

function route() {
  state.view = location.hash === "#/dashboard" ? "dashboard" : "pipeline";
  document.querySelectorAll("dialog[open]").forEach((dialog) => dialog.close());
  for (const [name, node] of Object.entries(el.views)) node.hidden = name !== state.view;
  document.querySelectorAll(".tabs [data-view]").forEach((a) => {
    a.classList.toggle("is-active", a.dataset.view === state.view);
    if (a.dataset.view === state.view) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  document.title = `${state.view === "dashboard" ? "Dashboard" : "Pipeline"} · Lead Kanban`;
  render();
}

function bind() {
  el.region.addEventListener("change", () => { state.filters.region = el.region.value; onFiltersChanged(); });
  el.manager.addEventListener("change", () => { state.filters.manager = el.manager.value; onFiltersChanged(); });
  el.agent.addEventListener("change", () => { state.filters.agent = el.agent.value; onFiltersChanged(); });
  let timer;
  el.search.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => { state.filters.search = el.search.value; onFiltersChanged(); }, 150);
  });
  el.clear.addEventListener("click", () => { state.filters = defaultFilters(); onFiltersChanged(); });
  el.sort.addEventListener("change", () => { state.sort = el.sort.value; onFiltersChanged(); });
  el.missing.addEventListener("change", () => { state.onlyMissing = el.missing.checked; onFiltersChanged(); });
  el.filtersToggle.addEventListener("click", () => {
    const open = el.filters.classList.toggle("is-open");
    el.filtersToggle.setAttribute("aria-expanded", open);
  });
  document.addEventListener("lk:prefs", savePrefs);
  for (const dialog of document.querySelectorAll("dialog")) {
    dialog.addEventListener("click", (e) => {
      if (e.target === dialog || e.target.closest("[data-close]")) dialog.close();
    });
  }
  window.addEventListener("hashchange", route);
  bindInfo();
  bindPipeline();
  bindDashboard();
  bindHelp();
}

/* Servidor Python (api/board) ou demo estática (data/board.json, gerado por build_static.py).
   Caminhos relativos: a demo pública roda numa subpasta. */
async function loadBoard() {
  let lastError;
  const isStatic = document.querySelector('meta[name="lead-kanban-static"]');
  for (const url of isStatic ? ["data/board.json"] : ["api/board", "data/board.json"]) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
      lastError = new Error(`HTTP ${response.status}`);
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError;
}

async function init() {
  bind();
  try {
    state.data = await loadBoard();
  } catch (err) {
    $("board").innerHTML = `<div class="board-error">Não foi possível carregar as oportunidades (${esc(err.message)}). Verifique se o servidor está em execução.</div>`;
    return;
  }
  loadPrefs();
  populateFilters();
  route();
}

init();
