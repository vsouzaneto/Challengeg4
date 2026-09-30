/**
 * Boot do painel: roteamento entre views, verificacao de saude da API e o
 * dialogo de configuracao da base URL.
 *
 * O roteador e de hash (`#/relatorio`), para o F5 cair na mesma tela sem
 * precisar de nenhuma regra de rewrite no servidor estatico.
 */

import { api, ApiError } from "./api.js";
import { getApiBase, setApiBase, defaultApiBase } from "./config.js";
import { $, $$, toast } from "./dom.js";
import * as fmt from "./format.js";
import { restore } from "./store.js";
import { hideTip } from "./charts.js";

import { initOverview } from "./views/overview.js";
import { initClusters } from "./views/clusters.js";
import { initSatisfaction } from "./views/satisfaction.js";
import { initSearch } from "./views/search.js";
import { initCosts } from "./views/costs.js";
import { initKanban } from "./views/kanban.js";
import { initImprovements } from "./views/improvements.js";

const ROUTES = {
  dashboard:    { hash: "dashboard",    title: "Dashboard" },
  overview:     { hash: "relatorio",     title: "Relatorio" },
  kanban:       { hash: "kanban",        title: "Kanban" },
  improvements: { hash: "melhorias",    title: "Melhorias" },
  clusters:     { hash: "agrupamentos",  title: "Agrupamentos" },
  satisfaction: { hash: "satisfacao",    title: "Satisfacao" },
  search:       { hash: "busca",         title: "Busca RAG" },
  costs:        { hash: "custo",         title: "Custo" },
};

const hooks = {};
let current = null;

/* -- Roteamento ----------------------------------------------------------- */

function routeFromHash() {
  const hash = window.location.hash.replace(/^#\/?/, "");
  const entry = Object.entries(ROUTES).find(([, meta]) => meta.hash === hash);
  return entry ? entry[0] : "overview";
}

function navigate(route, { updateHash = true } = {}) {
  if (!ROUTES[route]) route = "overview";
  current = route;

  for (const section of $$(".view")) {
    section.classList.toggle("is-active", section.id === `view-${route}`);
  }
  for (const button of $$("[data-route]")) {
    const active = button.dataset.route === route;
    button.toggleAttribute("aria-current", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  }

  $("#topbar-title").textContent = ROUTES[route].title;
  document.title = `${ROUTES[route].title} · Support Intelligence`;

  if (updateHash) window.location.hash = `#/${ROUTES[route].hash}`;
  hideTip();
  window.scrollTo({ top: 0, behavior: "instant" });

  hooks[route]?.onEnter?.();
}

/* -- Saude da API --------------------------------------------------------- */

async function checkHealth({ quiet = true } = {}) {
  const node = $("#conn");
  const label = $("#conn-label");
  const meta = $("#conn-meta");

  node.dataset.state = "unknown";
  label.textContent = "Verificando API";
  meta.textContent = getApiBase();

  try {
    const health = await api.health();
    const dbCheck = health?.checks?.database ?? "desconhecido";
    const ok = health?.status === "ok";

    node.dataset.state = ok ? "ok" : "degraded";
    label.textContent = ok ? "API conectada" : "API degradada";
    meta.textContent = ok
      ? `banco ok · v${health.version ?? "?"} · ${fmt.since(Date.now())}`
      : `banco: ${String(dbCheck).slice(0, 60)}`;

    node.title = `${getApiBase()}\nstatus: ${health?.status}\nbanco: ${dbCheck}`;

    if (!quiet) toast(ok ? "API respondendo normalmente." : "API no ar, mas o banco nao respondeu.");
    if (!ok && quiet) {
      toast("A API respondeu, mas o banco nao. A busca RAG depende do PGVector.", "error");
    }
  } catch (error) {
    node.dataset.state = "down";
    label.textContent = "API fora de alcance";
    meta.textContent = getApiBase();
    node.title = `${getApiBase()}\n${error?.message ?? ""}`;
    if (!quiet) toast(error instanceof ApiError ? error.message : "Falha ao consultar a API.", "error");
  }
}

/* -- Dialogo de configuracao ---------------------------------------------- */

function initSettings() {
  const dialog = $("#settings");
  const input = $("#api-base");
  const note = $("#settings-note");

  const open = () => {
    input.value = getApiBase();
    note.textContent = `Padrao detectado para esta pagina: ${defaultApiBase()}`;
    dialog.showModal();
  };

  $("#open-settings").addEventListener("click", open);
  $("#conn").addEventListener("click", open);
  $("#settings-cancel").addEventListener("click", () => dialog.close());

  $("#settings-form").addEventListener("submit", () => {
    // method="dialog" ja fecha; aqui so persistimos e revalidamos.
    setApiBase(input.value);
    checkHealth({ quiet: false });
  });

  $("#refresh-health").addEventListener("click", () => checkHealth({ quiet: false }));
}

async function initDashboard() {
  const body = $("#dashboard-body");
  const sync = $("#dashboard-sync");
  const paint = (data) => {
    const cards = [
      ["Tickets persistidos", fmt.num(data.ticket_count)],
      ["Resolucao media", fmt.hours(data.avg_resolution, 1)],
      ["Primeira resposta", fmt.hours(data.avg_first_response, 1)],
      ["Satisfacao", fmt.rating(data.avg_satisfaction)],
      ["Horas recuperaveis", fmt.hours(data.recoverable_hours, 1)],
      ["Custo estimado", data.estimated_cost == null ? "Informe custo/h" : fmt.money(data.estimated_cost)],
    ];
    body.innerHTML = `<div class="grid grid-3 dashboard-kpis">${cards.map(([label,value]) => `<article class="stat-tile"><span class="eyebrow">${label}</span><strong>${value ?? "—"}</strong><span class="card-note">Snapshot #${data.id} · ${fmt.since(data.generated_at)}</span></article>`).join("")}</div><article class="card" style="margin-top:16px"><div class="card-head"><span class="eyebrow">PERSISTENCIA</span></div><h3>Dados prontos para o Kanban</h3><p class="card-note">Os tickets estão armazenados em <code>support_tickets</code>. A etapa operacional pode ser atualizada sem alterar a fonte original do CSV.</p><button class="btn btn-primary" type="button" id="open-kanban">Abrir atendimento</button></article>`;
    $("#open-kanban")?.addEventListener("click", () => navigate("kanban"));
  };
  const load = async () => { try { paint(await api.dashboard()); } catch { body.innerHTML = `<div class="state state-center"><h3>Nenhum snapshot disponível</h3><p>Sincronize o CSV para criar os dados persistidos do dashboard.</p></div>`; } };
  sync?.addEventListener("click", async () => { sync.disabled = true; sync.textContent = "Sincronizando..."; try { paint(await api.syncDashboard({ dataset: "customer_support_tickets.csv" })); toast("Dashboard sincronizado."); } catch (e) { toast(e.message, "error"); } finally { sync.disabled = false; sync.textContent = "Sincronizar CSV"; } });
  await load();
}

/* -- Boot ----------------------------------------------------------------- */

function boot() {
  restore();

  initSettings();

  hooks.dashboard = initDashboard() ?? {};
  hooks.kanban = initKanban() ?? {};
  hooks.improvements = initImprovements() ?? {};
  hooks.overview = initOverview({ navigate }) ?? {};
  hooks.clusters = initClusters() ?? {};
  hooks.satisfaction = initSatisfaction() ?? {};
  hooks.search = initSearch() ?? {};
  hooks.costs = initCosts() ?? {};

  for (const button of $$("[data-route]")) {
    button.addEventListener("click", () => navigate(button.dataset.route));
  }

  window.addEventListener("hashchange", () => {
    const next = routeFromHash();
    if (next !== current) navigate(next, { updateHash: false });
  });

  // Tooltip nao pode ficar preso quando a pagina rola sob o ponteiro.
  window.addEventListener("scroll", hideTip, { passive: true });

  navigate(routeFromHash(), { updateHash: false });
  checkHealth();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot, { once: true });
} else {
  boot();
}
