/**
 * View "Agrupamentos" - POST /api/v1/clustering
 *
 * Mostra cada grupo do MiniBatchKMeans com seu tamanho, a distribuicao de
 * canal / prioridade / tipo e os tickets mais proximos do centroide, que sao
 * o que torna o grupo auditavel.
 */

import { api, ApiError } from "../api.js";
import { DATASETS } from "../config.js";
import { el, render, errorState, emptyState, toast, $ } from "../dom.js";
import * as fmt from "../format.js";
import { chartCard, barChart, dataTable, countsToItems, meter } from "../charts.js";

const PRIORITY_ORDER = ["Low", "Medium", "High", "Critical"];

let controller = null;
let ticker = null;
let lastResult = null;

/** Barra compacta usada dentro do card de cluster. */
function miniBreakdown(titleText, counts, total, ordinalOrder = null) {
  const items = countsToItems(counts, total, ordinalOrder);
  if (!items.length) return null;

  return el("div", { style: "margin-top:16px" }, [
    el("span", { class: "eyebrow", text: titleText }),
    el("div", { style: "height:10px" }),
    barChart({
      items: items.slice(0, 6).map((i) => ({
        name: fmt.label(i.name),
        value: i.value,
        display: fmt.num(i.value),
        extra: `${fmt.percent(i.share)} do grupo`,
      })),
      ordinalOrder,
      valueLabel: "Tickets no grupo",
    }),
  ]);
}

function clusterCard(group, totalRecords) {
  const share = totalRecords ? group.size / totalRecords : 0;
  const reps = Array.isArray(group.representatives) ? group.representatives : [];

  return el("article", { class: "card" }, [
    el("div", { class: "card-head" }, [
      el("span", { class: "eyebrow", text: `CLUSTER ${group.cluster}` }),
      el("span", { class: "card-note", text: `${fmt.percent(share)} da base` }),
    ]),
    el("h3", { text: `${fmt.num(group.size)} tickets` }),
    meter(share, `Participacao do cluster ${group.cluster} na base`),

    miniBreakdown("CANAIS", group.channels, group.size),
    miniBreakdown("PRIORIDADES", group.priorities, group.size, PRIORITY_ORDER),
    miniBreakdown("TIPOS", group.ticket_types, group.size),

    reps.length
      ? el("div", { style: "margin-top:20px" }, [
          el("span", { class: "eyebrow", text: "MAIS PROXIMOS DO CENTROIDE" }),
          el("div", { style: "height:10px" }),
          el("div", { class: "finding-list" },
            reps.map((rep) =>
              el("div", { class: "finding" }, [
                el("span", { class: "finding-title", text: rep.subject || "Sem assunto" }),
                el("span", {
                  class: "card-note",
                  text: `Ticket ${rep.ticket_id ?? "—"} · linha ${rep.source_index ?? "—"} do CSV`,
                }),
              ]),
            ),
          ),
        ])
      : null,
  ]);
}

function renderResult(container, payload) {
  const groups = Array.isArray(payload.groups) ? payload.groups : [];
  const total = payload.total_records;
  const bySize = [...groups].sort((a, b) => b.size - a.size);

  render(container, [
    el("div", { class: "grid grid-3" }, [
      el("article", { class: "card stat" }, [
        el("span", { class: "stat-label", text: "Registros agrupados" }),
        el("strong", { class: "stat-value hero-figure", text: fmt.num(total) }),
        el("span", { class: "stat-foot", text: payload.dataset }),
      ]),
      el("article", { class: "card stat" }, [
        el("span", { class: "stat-label", text: "Grupos" }),
        el("strong", { class: "stat-value", text: fmt.num(payload.clusters) }),
        el("span", { class: "stat-foot", text: `Maior grupo: ${fmt.num(bySize[0]?.size)} tickets` }),
      ]),
      el("article", { class: "tile-dark stat" }, [
        el("span", { class: "stat-label", text: "Modelo de embeddings" }),
        el("strong", { class: "stat-value", style: "font-size:21px;line-height:1.3", text: payload.model }),
        el("span", { class: "stat-foot", text: "MiniBatchKMeans sobre os vetores normalizados" }),
      ]),
    ]),

    el("article", { class: "cluster-guide" }, [
      el("div", { class: "cluster-guide-icon", text: "✦" }),
      el("div", {}, [
        el("span", { class: "eyebrow", text: "COMO LER ESTA TELA" }),
        el("h3", { text: "Um cluster é um grupo de tickets parecidos" }),
        el("p", { text: "O modelo transforma assunto, descrição, resolução, tipo e produto em vetores. Tickets próximos no espaço semântico entram no mesmo grupo. Tamanho mostra o volume; canais, prioridades e tipos mostram o perfil; representantes são os exemplos mais típicos do grupo." }),
      ]),
    ]),

    el("div", { class: "grid" }, [
      chartCard({
        eyebrow: "GROUPS",
        title: "Tamanho de cada grupo",
        note: "Ordenado do maior para o menor. Grupos grandes concentram tickets repetitivos - sao os candidatos naturais a automacao.",
        chart: () =>
          barChart({
            items: bySize.map((g) => ({
              name: `Cluster ${g.cluster}`,
              value: g.size,
              display: fmt.num(g.size),
              extra: `${fmt.percent(total ? g.size / total : 0)} da base`,
            })),
            valueLabel: "Tickets",
          }),
        table: () =>
          dataTable({
            columns: [
              { key: "cluster", label: "Cluster" },
              { key: "size", label: "Tickets", num: true },
              { key: "share", label: "Participacao", num: true },
              { key: "top", label: "Assunto representativo" },
            ],
            rows: bySize.map((g) => ({
              cluster: `Cluster ${g.cluster}`,
              size: fmt.num(g.size),
              share: fmt.percent(total ? g.size / total : 0),
              top: g.representatives?.[0]?.subject ?? "—",
            })),
          }),
      }),
    ]),

    el("div", { class: "cluster-grid" }, bySize.map((g) => clusterCard(g, total))),
  ]);
}

export function initClusters() {
  const form = $("#cluster-filters");
  const body = $("#cluster-body");
  const hint = $("#cluster-hint");
  const runBtn = $("#cluster-run");
  const cancelBtn = $("#cluster-cancel");
  const datasetSelect = $("#cluster-dataset");

  render(datasetSelect, DATASETS.map((d) => el("option", { value: d.value, text: d.label })));

  const paint = () => {
    if (!lastResult) {
      render(body, emptyState(
        "Nenhum agrupamento rodado ainda",
        "O endpoint gera embeddings de todos os tickets antes de agrupar. Na primeira execucao o modelo de embeddings precisa ser baixado, o que leva mais tempo.",
      ));
      return;
    }
    renderResult(body, lastResult);
  };

  const setRunning = (running, startedAt) => {
    runBtn.disabled = running;
    runBtn.textContent = running ? "Agrupando..." : "Agrupar";
    cancelBtn.hidden = !running;
    for (const input of form.querySelectorAll("input, select")) input.disabled = running;
    body.classList.toggle("is-refetching", running && Boolean(lastResult));

    if (ticker) { clearInterval(ticker); ticker = null; }
    if (running) {
      const tick = () => { hint.textContent = `Executando ha ${fmt.elapsed(Date.now() - startedAt)}.`; };
      tick();
      ticker = setInterval(tick, 1000);
    } else {
      hint.textContent = "";
    }
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (controller) return;

    const params = {
      dataset: datasetSelect.value,
      clusters: Number($("#cluster-k").value) || 12,
      batch_size: Number($("#cluster-batch").value) || 256,
      representatives: Number($("#cluster-reps").value) || 5,
    };

    controller = new AbortController();
    const startedAt = Date.now();
    setRunning(true, startedAt);

    if (!lastResult) {
      render(body, el("div", { class: "state state-center", role: "status", "aria-live": "polite" }, [
        el("div", { class: "spinner" }),
        el("h3", { text: "Gerando embeddings" }),
        el("p", { text: `Vetorizando ${params.dataset} e rodando MiniBatchKMeans com ${params.clusters} grupos.` }),
      ]));
    }

    try {
      lastResult = await api.clustering(params, controller.signal);
      paint();
      toast(`${params.clusters} grupos em ${fmt.elapsed(Date.now() - startedAt)}.`);
    } catch (error) {
      if (controller.signal.aborted) {
        toast("Agrupamento cancelado.");
        paint();
      } else if (error instanceof ApiError) {
        render(body, errorState(error, () => form.requestSubmit()));
        toast(error.message, "error");
      } else {
        throw error;
      }
    } finally {
      controller = null;
      setRunning(false);
    }
  });

  cancelBtn.addEventListener("click", () => {
    controller?.abort(new DOMException("cancelado pelo usuario", "AbortError"));
  });

  paint();
}
