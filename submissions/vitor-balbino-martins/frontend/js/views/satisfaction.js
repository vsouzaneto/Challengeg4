/**
 * View "Satisfacao" - POST /api/v1/reports/satisfaction
 *
 * O backend casa cada ticket com nota ao documento mais proximo do segundo
 * dataset (TF-IDF + vizinho mais proximo por cosseno) e agrupa por topico.
 * A view mostra a media por topico contra a media geral e expoe as evidencias
 * que sustentam cada grupo, com a linha de origem no CSV.
 */

import { api, ApiError } from "../api.js";
import { el, render, errorState, emptyState, toast, $ } from "../dom.js";
import * as fmt from "../format.js";
import { statTile, chartCard, divergingBarChart, dataTable } from "../charts.js";

let controller = null;
let ticker = null;
let lastResult = null;

/** Media ponderada das notas por topico: serve de linha de base do divergente. */
function overallAverage(topics) {
  const withData = topics.filter((t) => Number.isFinite(t.avg_rating) && Number.isFinite(t.tickets));
  const total = withData.reduce((acc, t) => acc + t.tickets, 0);
  if (!total) return null;
  return withData.reduce((acc, t) => acc + t.avg_rating * t.tickets, 0) / total;
}

function evidenceCard(title, eyebrow, summaries, dark = false) {
  if (!summaries?.length) return null;

  return el("article", { class: dark ? "tile-dark" : "card" }, [
    el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: eyebrow })]),
    el("h3", { text: title }),
    el("div", { class: "finding-list" },
      summaries.map((item) =>
        el("div", { class: "finding" }, [
          el("span", { class: "finding-title", text: fmt.label(item.topic) }),
          el("span", {
            class: "card-note",
            text: `Nota media ${fmt.rating(item.avg_rating)} · ${fmt.num(item.tickets)} tickets · ${fmt.num(item.low_rating_count)} com nota <= 2 · ${fmt.num(item.high_rating_count)} com nota >= 4`,
          }),
        ]),
      ),
    ),
  ]);
}

/** Tickets individuais que o backend devolveu como prova de cada topico. */
function evidenceTable(topics) {
  const rows = topics
    .flatMap((topic) =>
      (topic.evidence ?? []).map((item) => ({
        topic: fmt.label(topic.topic),
        ticket: String(item.ticket_id ?? "—"),
        subject: String(item.subject ?? "—"),
        rating: fmt.rating(item.rating),
        similarity: fmt.percent(item.similarity ?? 0),
        source: String(item.document_source ?? "—"),
      })),
    )
    .slice(0, 40);

  if (!rows.length) return null;

  return el("article", { class: "card" }, [
    el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: "TOPICS[].EVIDENCE" })]),
    el("h3", { text: "Tickets que sustentam cada topico" }),
    el("p", {
      class: "card-note",
      text: "Os tres tickets de menor nota de cada topico, com a similaridade do casamento e a linha exata do documento de origem.",
    }),
    el("div", { style: "height:12px" }),
    el("div", { class: "table-wrap" }, [
      dataTable({
        columns: [
          { key: "topic", label: "Topico" },
          { key: "ticket", label: "Ticket" },
          { key: "subject", label: "Assunto" },
          { key: "rating", label: "Nota", num: true },
          { key: "similarity", label: "Similaridade", num: true },
          { key: "source", label: "Origem" },
        ],
        rows,
      }),
    ]),
  ]);
}

function renderResult(container, payload) {
  const crossing = payload.crossing ?? {};
  const topics = Array.isArray(payload.topics) ? payload.topics : [];
  const baseline = overallAverage(topics);

  const worst = payload.lowest_satisfaction?.[0];
  const best = payload.highest_satisfaction?.[0];

  const items = topics.map((t) => ({
    name: fmt.label(t.topic),
    value: t.avg_rating,
    extra: `${fmt.num(t.tickets)} tickets · ${fmt.num(t.low_rating_count)} com nota <= 2`,
  }));

  render(container, [
    el("div", { class: "grid grid-4" }, [
      statTile({
        label: "Tickets casados",
        value: fmt.num(crossing.matched_tickets),
        hero: true,
        foot: "Tickets com nota que acharam um documento correspondente",
      }),
      statTile({
        label: "Topicos identificados",
        value: fmt.num(topics.length),
        foot: "Campo Topic_group do dataset textual",
      }),
      statTile({
        label: "Media geral",
        value: fmt.rating(baseline),
        unit: "/ 5",
        foot: "Media ponderada pelos tickets de cada topico",
      }),
      statTile({
        label: "Maior dor",
        value: fmt.rating(worst?.avg_rating),
        unit: "/ 5",
        delta: worst ? { text: `▼ ${fmt.label(worst.topic)}`, tone: "critical" } : null,
        foot: worst ? `${fmt.num(worst.tickets)} tickets neste topico` : null,
      }),
    ]),

    el("div", { class: "grid" }, [
      chartCard({
        eyebrow: "TOPICS",
        title: "Nota media por topico",
        note: baseline
          ? `Distancia ate a media geral de ${fmt.rating(baseline)}. Azul acima da media, vermelho abaixo; o sinal tambem vem escrito no valor.`
          : "Sem base suficiente para calcular a media geral.",
        chart: () =>
          baseline === null
            ? el("p", { class: "card-note", text: "Sem dados para exibir." })
            : divergingBarChart({
                items, baseline, valueLabel: "Nota media",
                format: (v) => fmt.rating(v),
                deltaFormat: (v) => fmt.decimal(v, 2),
              }),
        table: () =>
          dataTable({
            columns: [
              { key: "topic", label: "Topico" },
              { key: "avg", label: "Nota media", num: true },
              { key: "delta", label: "vs. media", num: true },
              { key: "tickets", label: "Tickets", num: true },
              { key: "low", label: "Nota <= 2", num: true },
              { key: "high", label: "Nota >= 4", num: true },
            ],
            rows: topics.map((t) => ({
              topic: fmt.label(t.topic),
              avg: fmt.rating(t.avg_rating),
              delta: baseline === null ? "—" : fmt.signed(t.avg_rating - baseline, 2),
              tickets: fmt.num(t.tickets),
              low: fmt.num(t.low_rating_count),
              high: fmt.num(t.high_rating_count),
            })),
          }),
      }),
    ]),

    el("div", { class: "grid grid-2" }, [
      evidenceCard("Menores notas", "LOWEST_SATISFACTION", payload.lowest_satisfaction, true),
      evidenceCard("Maiores notas", "HIGHEST_SATISFACTION", payload.highest_satisfaction),
    ]),

    el("div", { class: "grid" }, [evidenceTable(topics)]),

    el("div", { class: "grid" }, [
      el("article", { class: "card" }, [
        el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: "CROSSING" })]),
        el("h3", { text: "Como o cruzamento foi feito" }),
        el("div", { class: "finding-list" }, [
          el("div", { class: "finding" }, [
            el("span", { class: "finding-title", text: "Metodo" }),
            el("span", { text: String(crossing.method ?? "—") }),
          ]),
          el("div", { class: "finding" }, [
            el("span", { class: "finding-title", text: "Dataset de metricas" }),
            el("span", { text: String(crossing.metrics_dataset ?? "—") }),
          ]),
          el("div", { class: "finding" }, [
            el("span", { class: "finding-title", text: "Dataset textual" }),
            el("span", { text: String(crossing.text_dataset ?? "—") }),
          ]),
        ]),
        best
          ? el("p", { class: "card-note", style: "margin-top:16px" }, [
              `Topico mais bem avaliado: ${fmt.label(best.topic)} (${fmt.rating(best.avg_rating)} / 5).`,
            ])
          : null,
      ]),
    ]),
  ]);
}

export function initSatisfaction() {
  const form = $("#sat-filters");
  const body = $("#sat-body");
  const hint = $("#sat-hint");
  const runBtn = $("#sat-run");
  const cancelBtn = $("#sat-cancel");

  const paint = () => {
    if (!lastResult) {
      render(body, emptyState(
        "Cruzamento ainda nao executado",
        "O endpoint vetoriza os dois CSVs com TF-IDF e busca, para cada ticket com nota, o documento mais proximo. E uma operacao pesada de CPU e roda de forma sincrona.",
      ));
      return;
    }
    renderResult(body, lastResult);
  };

  const setRunning = (running, startedAt) => {
    runBtn.disabled = running;
    runBtn.textContent = running ? "Cruzando..." : "Cruzar datasets";
    cancelBtn.hidden = !running;
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

    controller = new AbortController();
    const startedAt = Date.now();
    setRunning(true, startedAt);

    if (!lastResult) {
      render(body, el("div", { class: "state state-center", role: "status", "aria-live": "polite" }, [
        el("div", { class: "spinner" }),
        el("h3", { text: "Casando tickets e documentos" }),
        el("p", { text: "Vetorizando os dois datasets com TF-IDF e buscando o vizinho mais proximo de cada ticket." }),
      ]));
    }

    try {
      lastResult = await api.satisfaction(controller.signal);
      paint();
      toast(`Cruzamento concluido em ${fmt.elapsed(Date.now() - startedAt)}.`);
    } catch (error) {
      if (controller.signal.aborted) {
        toast("Cruzamento cancelado.");
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
