/**
 * View "Busca RAG" - POST /rag/search, POST /rag/index, GET /rag/index/status
 *
 * Sobre o score: o repositorio usa PGVector com a estrategia padrao COSINE, e
 * `similarity_search_with_score` devolve a coluna `distance`. Ou seja, o numero
 * e uma DISTANCIA (0 = identico, maior = mais distante), nao uma similaridade.
 * A view mostra a distancia crua e converte em "proximidade" so na barra.
 */

import { api, ApiError } from "../api.js";
import { el, render, errorState, emptyState, toast, $ } from "../dom.js";
import * as fmt from "../format.js";
import { meter } from "../charts.js";

let controller = null;
let pollTimer = null;
let lastResults = null;
let lastQuery = "";

/** Distancia cosseno -> proporcao 0..1 para a barra. */
function proximity(distance) {
  if (!Number.isFinite(distance)) return 0;
  return Math.max(0, Math.min(1, 1 - distance));
}

/** `.result-body` corta em 7.5em = 5 linhas; o botao segue o mesmo criterio. */
function isClamped(text) {
  return text.split("\n").length > 5 || text.length > 420;
}

function resultCard(item, index) {
  const meta = item.metadata ?? {};
  const distance = Number.isFinite(item.score) ? item.score : null;

  const card = el("article", { class: "result" });
  const bodyText = String(item.content ?? "");

  const body = el("p", { class: "result-body", text: bodyText });

  const more = el("button", {
    class: "result-more",
    type: "button",
    onClick: () => {
      const open = card.dataset.expanded === "true";
      card.dataset.expanded = open ? "false" : "true";
      more.textContent = open ? "Mostrar documento completo" : "Recolher";
    },
  }, "Mostrar documento completo");

  render(card, [
    el("div", { class: "result-top" }, [
      el("span", { class: "result-src" }, [
        `#${index + 1} · `,
        String(meta.source ?? "origem desconhecida"),
        meta.ticket_id ? ` · ticket ${meta.ticket_id}` : "",
      ]),
      distance === null
        ? null
        : el("span", { class: "result-score" }, [
            el("span", { text: `distancia ${fmt.decimal(distance, 3)}` }),
            meter(proximity(distance), `Proximidade do resultado ${index + 1}`),
          ]),
    ]),
    body,
    isClamped(bodyText) ? more : null,
  ]);

  return card;
}

function renderResults(container, results, query) {
  if (!results.length) {
    render(container, emptyState(
      "Nenhum documento encontrado",
      `A busca por "${query}" nao retornou resultados. Se o indice acabou de ser criado, confirme no painel ao lado que a indexacao terminou.`,
    ));
    return;
  }

  render(container, [
    el("p", { class: "card-note", style: "margin-bottom:12px" }, [
      `${fmt.num(results.length)} documentos para "${query}". Menor distancia = mais proximo da consulta.`,
    ]),
    el("div", { class: "grid" }, results.map((item, index) => resultCard(item, index))),
  ]);
}

/* -- Painel do indice ----------------------------------------------------- */

const INDEX_LABEL = {
  idle: "Indice nao construido nesta sessao",
  queued: "Indexacao enfileirada",
  running: "Indexando",
  completed: "Indice pronto",
  failed: "Indexacao falhou",
};

function renderIndexPanel(container, status, { onIndex, busy }) {
  const state = status?.status ?? "unknown";
  const processed = Number(status?.processed) || 0;
  const total = Number(status?.total) || 0;
  const ratio = total ? processed / total : 0;

  render(container, [
    el("strong", { class: "stat-value", style: "font-size:21px;line-height:1.3;margin-top:4px" }, [
      INDEX_LABEL[state] ?? "Estado desconhecido",
    ]),

    state === "running" || state === "completed"
      ? el("div", { style: "margin-top:16px" }, [
          meter(ratio, "Progresso da indexacao"),
          el("p", { class: "card-note", style: "margin-top:8px" }, [
            `${fmt.num(processed)} de ${fmt.num(total)} documentos`,
          ]),
        ])
      : null,

    state === "failed" && status?.error
      ? el("p", { class: "card-note", style: "margin-top:12px", text: String(status.error) })
      : null,

    el("p", { class: "card-note", style: "margin-top:16px" }, [
      "O estado e mantido em memoria pelo processo do backend: reiniciar o servidor volta para “idle”, mas os vetores ja gravados continuam no PGVector.",
    ]),

    el("div", { style: "height:16px" }),
    el("button", {
      class: "btn btn-primary",
      type: "button",
      disabled: busy || state === "running" || state === "queued",
      onClick: onIndex,
    }, state === "completed" ? "Reindexar" : "Indexar CSVs"),
  ]);
}

export function initSearch() {
  const form = $("#search-filters");
  const body = $("#search-body");
  const hint = $("#search-hint");
  const runBtn = $("#rag-run");
  const indexBody = $("#index-body");

  let indexBusy = false;

  const paintResults = () => {
    if (!lastResults) {
      render(body, emptyState(
        "Faca uma consulta",
        "A busca roda sobre os vetores gravados no PGVector. Use linguagem natural: o casamento e semantico, nao por palavra exata.",
      ));
      return;
    }
    renderResults(body, lastResults, lastQuery);
  };

  const startIndexing = async () => {
    indexBusy = true;
    try {
      const response = await api.ragIndex();
      toast(response?.message ?? "Indexacao enfileirada.");
      await pollIndex();
    } catch (error) {
      if (error instanceof ApiError) {
        render(indexBody, errorState(error, () => startIndexing()));
        toast(error.message, "error");
      } else throw error;
    } finally {
      indexBusy = false;
    }
  };

  async function pollIndex() {
    if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
    try {
      const status = await api.ragIndexStatus();
      renderIndexPanel(indexBody, status, { onIndex: startIndexing, busy: indexBusy });
      // Enquanto estiver rodando, consulta de novo; parado, nao insiste.
      if (status?.status === "running" || status?.status === "queued") {
        pollTimer = setTimeout(pollIndex, 3000);
      }
    } catch (error) {
      if (error instanceof ApiError) {
        render(indexBody, errorState(error, () => pollIndex()));
      } else throw error;
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (controller) return;

    const query = $("#rag-query").value.trim();
    if (query.length < 2) {
      toast("A consulta precisa de pelo menos 2 caracteres.", "error");
      return;
    }

    controller = new AbortController();
    runBtn.disabled = true;
    runBtn.textContent = "Buscando...";
    hint.textContent = "Consultando o PGVector...";
    body.classList.toggle("is-refetching", Boolean(lastResults));

    try {
      const results = await api.ragSearch({ query, k: Number($("#rag-k").value) || 5 }, controller.signal);
      lastResults = Array.isArray(results) ? results : [];
      lastQuery = query;
      paintResults();
    } catch (error) {
      if (error instanceof ApiError) {
        render(body, errorState(error, () => form.requestSubmit()));
        toast(error.message, "error");
      } else if (!controller.signal.aborted) {
        throw error;
      }
    } finally {
      controller = null;
      runBtn.disabled = false;
      runBtn.textContent = "Buscar";
      hint.textContent = "";
      body.classList.remove("is-refetching");
    }
  });

  paintResults();
  renderIndexPanel(indexBody, { status: "idle" }, { onIndex: startIndexing, busy: false });

  /** Chamado pelo roteador ao entrar na view, para o estado nunca vir velho. */
  return { onEnter: pollIndex };
}
