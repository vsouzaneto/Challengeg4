/**
 * View "Relatorio" - POST /api/v1/reports/support
 *
 * Renderiza o payload inteiro do endpoint: metricas calculadas em Python,
 * consolidacao dos agentes Ollama e o bloco de auditoria com as fontes.
 */

import { api, ApiError } from "../api.js";
import { DATASETS } from "../config.js";
import { el, render, errorState, emptyState, toast, $ } from "../dom.js";
import * as fmt from "../format.js";
import {
  statTile, chartCard, barChart, divergingBarChart, dataTable, countsToItems, meter,
} from "../charts.js";
import { setReport, get, subscribe } from "../store.js";

/** Ordem natural da prioridade - habilita a rampa ordinal no grafico. */
const PRIORITY_ORDER = ["Low", "Medium", "High", "Critical"];

let controller = null;
let ticker = null;

/* -- Normalizacao da saida dos agentes ----------------------------------- */

/**
 * O modelo devolve JSON livre: um achado pode vir como string, lista de
 * strings, lista de objetos ou objeto unico. Reduz tudo a { title, body }.
 */
function toFindings(value) {
  if (value === null || value === undefined) return [];
  if (typeof value === "string") return value.trim() ? [{ title: null, body: value.trim() }] : [];
  if (typeof value === "number" || typeof value === "boolean") return [{ title: null, body: String(value) }];

  if (Array.isArray(value)) return value.flatMap(toFindings);

  // Objeto: procura um rotulo e um corpo entre chaves comuns do prompt.
  const titleKeys = ["titulo", "title", "nome", "name", "gargalo", "combinacao", "item", "problema", "recomendacao"];
  const bodyKeys = ["descricao", "description", "detalhe", "detalhes", "explicacao", "justificativa", "impacto", "texto", "valor", "acao"];

  const pick = (keys) => {
    for (const key of keys) {
      const v = value[key];
      if (typeof v === "string" && v.trim()) return v.trim();
      if (typeof v === "number") return String(v);
    }
    return null;
  };

  const title = pick(titleKeys);
  const body = pick(bodyKeys);
  if (title || body) return [{ title, body: body ?? "" }];

  // Sem chave reconhecida: lista os pares para nao esconder conteudo.
  const pairs = Object.entries(value)
    .filter(([, v]) => v !== null && v !== undefined && typeof v !== "object")
    .map(([k, v]) => `${fmt.label(k)}: ${v}`);
  return pairs.length ? [{ title: null, body: pairs.join(" · ") }] : [];
}

function findingList(value, emptyText) {
  const items = toFindings(value);
  if (!items.length) return el("p", { class: "card-note", text: emptyText });

  return el(
    "div",
    { class: "finding-list" },
    items.slice(0, 12).map((item) =>
      el("div", { class: "finding" }, [
        item.title ? el("span", { class: "finding-title", text: item.title }) : null,
        item.body ? el("span", { text: item.body }) : null,
      ]),
    ),
  );
}

/** "Ticket Channel: Email · Ticket Priority: Critical" -> "Email · Critical" */
function dimensionLabel(dimensions) {
  if (!dimensions || typeof dimensions !== "object") return "Sem informacao";
  const parts = Object.values(dimensions).map((v) => fmt.label(v));
  return parts.length ? parts.join(" · ") : "Sem informacao";
}

/* -- Blocos --------------------------------------------------------------- */

function kpiRow(metrics) {
  return el("div", { class: "grid grid-4" }, [
    statTile({
      label: "Tickets analisados",
      value: fmt.num(metrics.ticket_count),
      hero: true,
      foot: "Linhas lidas do CSV completo",
    }),
    statTile({
      label: "Satisfacao media",
      value: fmt.rating(metrics.avg_satisfaction),
      unit: "/ 5",
      foot: "Campo Customer Satisfaction Rating",
    }),
    statTile({
      label: "Resolucao media",
      value: fmt.decimal(metrics.avg_resolution, 1),
      unit: "h",
      foot: "Campo Time to Resolution",
    }),
    statTile({
      label: "Primeira resposta",
      value: fmt.decimal(metrics.avg_first_response, 1),
      unit: "h",
      foot: "Campo First Response Time",
    }),
  ]);
}

function distributionCard({ eyebrow, title, counts, total, ordinalOrder = null }) {
  const items = countsToItems(counts, total, ordinalOrder);
  return chartCard({
    eyebrow,
    title,
    chart: () =>
      barChart({
        items: items.map((i) => ({
          name: fmt.label(i.name),
          value: i.value,
          display: fmt.num(i.value),
          extra: `${fmt.percent(i.share)} do total`,
        })),
        ordinalOrder,
        valueLabel: "Tickets",
      }),
    table: () =>
      dataTable({
        columns: [
          { key: "name", label: "Categoria" },
          { key: "tickets", label: "Tickets", num: true },
          { key: "share", label: "Participacao", num: true },
        ],
        rows: items.map((i) => ({
          name: fmt.label(i.name),
          tickets: fmt.num(i.value),
          share: fmt.percent(i.share),
        })),
      }),
  });
}

function satisfactionCard(metrics) {
  const rows = metrics.satisfaction_by_channel ?? [];
  if (!rows.length) return null;

  const baseline = metrics.avg_satisfaction;
  const items = rows.map((row) => ({
    name: dimensionLabel(row.dimensions),
    value: row.avg,
    extra: `${fmt.num(row.tickets)} tickets avaliados`,
  }));

  if (!Number.isFinite(baseline)) {
    return chartCard({
      eyebrow: "METRICS.SATISFACTION_BY_CHANNEL",
      title: "Nota media por canal",
      chart: () => barChart({
        items: items.map((i) => ({ ...i, display: fmt.rating(i.value) })),
        valueLabel: "Nota media",
      }),
      table: () => satisfactionTable(items),
    });
  }

  return chartCard({
    eyebrow: "METRICS.SATISFACTION_BY_CHANNEL",
    title: "Nota media por canal",
    note: `Distancia ate a media geral de ${fmt.rating(baseline)}. Azul acima da media, vermelho abaixo.`,
    chart: () => divergingBarChart({
      items, baseline, valueLabel: "Nota media",
      format: (v) => fmt.rating(v),
      deltaFormat: (v) => fmt.decimal(v, 2),
    }),
    table: () => satisfactionTable(items, baseline),
  });
}

function satisfactionTable(items, baseline = null) {
  const columns = [
    { key: "name", label: "Canal" },
    { key: "avg", label: "Nota media", num: true },
    { key: "tickets", label: "Tickets", num: true },
  ];
  if (baseline !== null) columns.splice(2, 0, { key: "delta", label: "vs. media", num: true });

  return dataTable({
    columns,
    rows: items.map((i) => ({
      name: i.name,
      avg: fmt.rating(i.value),
      delta: baseline === null ? null : fmt.signed(i.value - baseline, 2),
      tickets: i.extra.replace(" tickets avaliados", ""),
    })),
  });
}

function worstCombinationsCard(metrics) {
  const rows = metrics.worst_combinations ?? [];
  if (!rows.length) return null;

  // Tres dimensoes por linha: tabela le melhor que qualquer grafico aqui.
  return el("article", { class: "card" }, [
    el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: "METRICS.WORST_COMBINATIONS" })]),
    el("h3", { text: "Combinacoes com maior tempo de resolucao" }),
    el("p", {
      class: "card-note",
      text: "Canal, prioridade e tipo cruzados, ordenados pelo tempo medio. E daqui que sai o benchmark do desperdicio.",
    }),
    el("div", { style: "height:12px" }),
    el("div", { class: "table-wrap" }, [
      dataTable({
        columns: [
          { key: "rank", label: "#", num: true },
          { key: "combo", label: "Canal / Prioridade / Tipo" },
          { key: "avg", label: "Tempo medio", num: true },
          { key: "tickets", label: "Tickets", num: true },
        ],
        rows: rows.map((row, index) => ({
          rank: String(index + 1),
          combo: dimensionLabel(row.dimensions),
          avg: fmt.hours(row.avg, 1),
          tickets: fmt.num(row.tickets),
        })),
      }),
    ]),
  ]);
}

function correlationCard(metrics) {
  const corr = metrics.correlations_with_satisfaction ?? {};
  const entries = [
    { label: "Primeira resposta × satisfacao", value: corr.first_response },
    { label: "Tempo de resolucao × satisfacao", value: corr.resolution },
  ];

  return el("article", { class: "card" }, [
    el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: "METRICS.CORRELATIONS" })]),
    el("h3", { text: "Correlacao de Pearson" }),
    el("div", { class: "finding-list" },
      entries.map((entry) =>
        el("div", { class: "finding" }, [
          el("span", { class: "finding-title", text: entry.label }),
          el("span", {
            text: Number.isFinite(entry.value)
              ? `${fmt.signed(entry.value, 3)} · ${fmt.correlationStrength(entry.value)}`
              : "A API nao retornou este valor (pares insuficientes).",
          }),
        ]),
      ),
    ),
    el("p", {
      class: "card-note",
      style: "margin-top:12px",
      text: "Faixa de -1 a +1. Valores negativos indicam que, quanto maior o tempo, menor a nota.",
    }),
  ]);
}

function wasteCard(metrics, onOpenCosts) {
  const waste = metrics.waste ?? {};
  const recoverable = waste.recoverable_hours;
  const benchmark = waste.benchmark_resolution;

  // Fracao do tempo total que esta acima do benchmark.
  const totalHours = Number.isFinite(metrics.avg_resolution) && Number.isFinite(metrics.ticket_count)
    ? metrics.avg_resolution * metrics.ticket_count
    : null;
  const ratio = Number.isFinite(recoverable) && totalHours ? recoverable / totalHours : 0;

  return el("article", { class: "tile-dark" }, [
    el("span", { class: "eyebrow", text: "METRICS.WASTE" }),
    el("h3", { text: "Horas acima do benchmark" }),
    // Nao e figura heroi: a view ja tem uma (o total de tickets no topo).
    el("strong", { class: "stat-value" }, [fmt.hoursCompact(recoverable)]),
    el("p", { class: "card-note", style: "margin-bottom:16px" }, [
      `Soma do que cada ticket gastou alem do melhor tempo medio observado (${fmt.hours(benchmark, 2)}).`,
    ]),
    meter(ratio, "Participacao das horas recuperaveis no tempo total"),
    el("p", { class: "card-note", style: "margin-top:8px" }, [
      Number.isFinite(recoverable) && totalHours
        ? `${fmt.percent(ratio)} do tempo total estimado (${fmt.hoursCompact(totalHours)}).`
        : "Sem base para calcular a participacao.",
    ]),
    Number.isFinite(waste.estimated_cost)
      ? el("p", { class: "card-note", style: "margin-top:16px" }, [
          "Custo estimado pela API: ",
          el("strong", { style: "color:#fff", text: fmt.money(waste.estimated_cost) }),
        ])
      : el("p", { class: "card-note", style: "margin-top:16px", text: "Informe o custo por hora para a API calcular o valor." }),
    el("div", { style: "height:16px" }),
    el("button", { class: "btn btn-primary", type: "button", onClick: onOpenCosts }, "Abrir view de custo"),
  ]);
}

function consolidationCard(consolidation) {
  const summary = consolidation?.resumo_executivo;
  const reasoning = consolidation?.justificativa;

  return el("article", { class: "tile-dark" }, [
    el("span", { class: "eyebrow", text: "CONSOLIDATION · AGENTE OLLAMA" }),
    el("h3", { text: "Resumo executivo" }),
    summary
      ? findingList(summary, "")
      : el("p", { class: "card-note", text: "O agente nao devolveu resumo executivo nesta execucao." }),
    reasoning
      ? el("div", { style: "margin-top:20px" }, [
          el("span", { class: "eyebrow", text: "JUSTIFICATIVA" }),
          el("div", { style: "height:10px" }),
          findingList(reasoning, ""),
        ])
      : null,
  ]);
}

function findingsGrid(audit) {
  const findings = audit?.findings ?? {};
  const blocks = [
    ["FINDINGS.FLOW_BOTTLENECKS", "Onde o fluxo trava", findings.flow_bottlenecks],
    ["FINDINGS.SATISFACTION_DRIVERS", "O que move a satisfacao", findings.satisfaction_drivers],
    ["FINDINGS.RECOVERABLE_WASTE", "Desperdicio recuperavel", findings.recoverable_waste],
    ["FINDINGS.RECOMMENDATIONS", "Recomendacoes", findings.recommendations],
  ];

  return el("div", { class: "grid grid-2" },
    blocks.map(([eyebrow, title, value]) =>
      el("article", { class: "card" }, [
        el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: eyebrow })]),
        el("h3", { text: title }),
        findingList(value, "O agente nao devolveu itens para este bloco."),
      ]),
    ),
  );
}

function auditCard(payload) {
  const audit = payload.audit ?? {};
  const sources = Array.isArray(audit.sources) ? audit.sources : [];
  const chunks = payload.extraction?.chunks;

  return el("article", { class: "card" }, [
    el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: "AUDIT · RASTREABILIDADE" })]),
    el("h3", { text: "De onde vem cada numero" }),
    el("div", { class: "tag-row", style: "margin-bottom:16px" }, [
      el("span", { class: "pill-tag", text: `schema ${audit.schema_version ?? "?"}` }),
      el("span", { class: "pill-tag", text: `dataset ${payload.dataset}` }),
      el("span", { class: "pill-tag", text: `${fmt.num(chunks)} lotes enviados ao agente` }),
      payload.extraction?.trimmed
        ? el("span", { class: "pill-tag", text: "extracao por lote nao mantida no cache local" })
        : null,
    ]),
    sources.length
      ? el("div", { class: "table-wrap" }, [
          dataTable({
            columns: [
              { key: "file", label: "Arquivo" },
              { key: "rows", label: "Linhas" },
              { key: "records", label: "Registros", num: true },
              { key: "basis", label: "Base" },
            ],
            rows: sources.map((s) => ({
              file: String(s.file ?? "—"),
              rows: String(s.rows ?? "—"),
              records: fmt.num(s.records),
              basis: String(s.basis ?? "—"),
            })),
          }),
        ])
      : el("p", { class: "card-note", text: "A API nao retornou a lista de fontes." }),
  ]);
}

/* -- Render completo ------------------------------------------------------ */

function renderReport(container, payload, params, generatedAt, onOpenCosts) {
  const metrics = payload.metrics ?? {};
  const total = metrics.ticket_count;

  render(container, [
    el("p", { class: "card-note", style: "margin-bottom:16px" }, [
      `Relatorio de ${payload.dataset} · gerado ${fmt.since(generatedAt)} · lotes de ${fmt.num(params.chunk_size)} registros`,
    ]),

    kpiRow(metrics),

    el("div", { class: "grid grid-wide-left" }, [
      consolidationCard(payload.consolidation),
      wasteCard(metrics, onOpenCosts),
    ]),

    el("div", { class: "grid grid-3" }, [
      distributionCard({ eyebrow: "METRICS.CHANNELS", title: "Tickets por canal", counts: metrics.channels, total }),
      distributionCard({
        eyebrow: "METRICS.PRIORITIES",
        title: "Tickets por prioridade",
        counts: metrics.priorities,
        total,
        ordinalOrder: PRIORITY_ORDER,
      }),
      distributionCard({ eyebrow: "METRICS.TICKET_TYPES", title: "Tickets por tipo", counts: metrics.ticket_types, total }),
    ]),

    el("div", { class: "grid grid-2" }, [
      satisfactionCard(metrics),
      correlationCard(metrics),
    ]),

    el("div", { class: "grid" }, [worstCombinationsCard(metrics)]),

    findingsGrid(payload.audit),

    el("div", { class: "grid" }, [auditCard(payload)]),
  ]);
}

/* -- Ciclo de vida da view ------------------------------------------------ */

export function initOverview({ navigate }) {
  const form = $("#report-filters");
  const body = $("#report-body");
  const hint = $("#report-hint");
  const runBtn = $("#report-run");
  const cancelBtn = $("#report-cancel");
  const datasetSelect = $("#report-dataset");

  render(datasetSelect, DATASETS.map((d) => el("option", { value: d.value, text: d.label })));

  const paint = () => {
    const report = get("report");
    if (!report) {
      render(body, emptyState(
        "Nenhum relatorio gerado ainda",
        "A geracao le o CSV inteiro e envia um lote por vez ao Ollama. Com 8.469 tickets e lotes de 500, sao 17 chamadas ao modelo - pode levar varios minutos.",
      ));
      return;
    }
    renderReport(body, report, get("reportParams") ?? {}, get("reportAt"), () => navigate("costs"));
  };

  const setRunning = (running, startedAt) => {
    runBtn.disabled = running;
    runBtn.textContent = running ? "Gerando..." : "Gerar relatorio";
    cancelBtn.hidden = !running;
    for (const input of form.querySelectorAll("input, select")) input.disabled = running;
    body.classList.toggle("is-refetching", running && Boolean(get("report")));

    if (ticker) { clearInterval(ticker); ticker = null; }

    if (running) {
      const tick = () => {
        hint.textContent = `Executando ha ${fmt.elapsed(Date.now() - startedAt)}. Voce pode navegar entre as views; a execucao continua.`;
      };
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
      chunk_size: Number($("#report-chunk").value) || 100,
      hourly_cost: $("#report-cost").value === "" ? null : Number($("#report-cost").value),
    };

    controller = new AbortController();
    const startedAt = Date.now();
    setRunning(true, startedAt);

    if (!get("report")) {
      render(body, el("div", { class: "state state-center", role: "status", "aria-live": "polite" }, [
        el("div", { class: "spinner" }),
        el("h3", { text: "Rodando os agentes" }),
        el("p", { text: `Lendo ${params.dataset} e consolidando lote a lote. A pagina pode ficar aberta em outra view.` }),
      ]));
    }

    try {
      const payload = await api.supportReport(params, controller.signal);
      setReport(payload, params);
      // `controller` ainda esta setado aqui, entao o assinante do store se
      // abstem; o repaint desta view e feito explicitamente.
      paint();
      toast(`Relatorio pronto em ${fmt.elapsed(Date.now() - startedAt)}.`);
    } catch (error) {
      if (controller.signal.aborted) {
        toast("Geracao cancelada.");
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

  subscribe((keys) => {
    if (keys.includes("report") && !controller) paint();
  });

  paint();
}
