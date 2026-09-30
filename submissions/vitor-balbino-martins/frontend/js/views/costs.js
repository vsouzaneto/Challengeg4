/**
 * View "Custo" - derivada de POST /api/v1/reports/support
 *
 * Nada aqui e inventado: as horas e o benchmark vem de `metrics.waste`, e as
 * combinacoes vem de `metrics.worst_combinations`. O usuario fornece apenas
 * duas premissas - custo/hora e fatia capturavel - e elas ficam rotuladas
 * como premissas na propria tela.
 *
 * A conta do custo e a mesma do backend (`excess_hours * hourly_cost`), feita
 * no cliente para nao exigir uma nova execucao dos agentes a cada ajuste.
 *
 * O formulario e montado uma vez e nunca e recriado: so o bloco de resultados
 * e redesenhado a cada ajuste, para o slider nao perder o foco enquanto arrasta.
 */

import { el, render, append, emptyState, $ } from "../dom.js";
import * as fmt from "../format.js";
import { statTile, chartCard, barChart, dataTable, meter } from "../charts.js";
import { get, subscribe } from "../store.js";

const STATE = { hourlyCost: 80, capture: 0.4 };

/** Excedente por combinacao: (tempo medio - benchmark) x tickets. */
function excessByCombination(metrics) {
  const benchmark = metrics.waste?.benchmark_resolution;
  const rows = metrics.worst_combinations ?? [];
  if (!Number.isFinite(benchmark) || !rows.length) return [];

  return rows
    .map((row) => {
      const excessPerTicket = Math.max(0, (row.avg ?? 0) - benchmark);
      return {
        name: Object.values(row.dimensions ?? {}).map((v) => fmt.label(v)).join(" · "),
        tickets: row.tickets ?? 0,
        avg: row.avg,
        excessHours: excessPerTicket * (row.tickets ?? 0),
      };
    })
    .filter((row) => row.excessHours > 0)
    .sort((a, b) => b.excessHours - a.excessHours);
}

/* -- Bloco de resultados (redesenhado a cada ajuste) --------------------- */

function renderResults(container, report) {
  const metrics = report.metrics;
  const waste = metrics.waste ?? {};
  const hours = Number(waste.recoverable_hours);
  const benchmark = Number(waste.benchmark_resolution);
  const apiCost = Number(waste.estimated_cost);
  const apiHourly = Number(get("reportParams")?.hourly_cost);

  const capturableHours = Number.isFinite(hours) ? hours * STATE.capture : NaN;
  const totalCost = Number.isFinite(hours) ? hours * STATE.hourlyCost : NaN;
  const capturableCost = Number.isFinite(capturableHours) ? capturableHours * STATE.hourlyCost : NaN;

  const totalHours = Number.isFinite(metrics.avg_resolution) && Number.isFinite(metrics.ticket_count)
    ? metrics.avg_resolution * metrics.ticket_count
    : null;

  const combos = excessByCombination(metrics);
  const body = el("div");

  append(body, [
    el("div", { class: "grid grid-4" }, [
      statTile({
        label: "Custo do excedente",
        value: fmt.moneyCompact(totalCost),
        hero: true,
        foot: `${fmt.hoursCompact(hours)} x ${fmt.money(STATE.hourlyCost, true)} por hora`,
      }),
      statTile({
        label: "Recuperavel na sua premissa",
        value: fmt.moneyCompact(capturableCost),
        delta: { text: `▲ ${fmt.percent(STATE.capture, 0)} do excedente`, tone: "good" },
        foot: `Equivale a ${fmt.hoursCompact(capturableHours)}`,
      }),
      statTile({
        label: "Benchmark de resolucao",
        value: fmt.decimal(benchmark, 2),
        unit: "h",
        foot: "Melhor tempo medio entre as combinacoes canal/prioridade/tipo",
      }),
      statTile({
        label: "Conferencia com a API",
        value: Number.isFinite(apiCost) ? fmt.moneyCompact(apiCost) : fmt.EMPTY,
        foot: Number.isFinite(apiCost) && Number.isFinite(apiHourly)
          ? `metrics.waste.estimated_cost, calculado com ${fmt.money(apiHourly, true)} por hora`
          : "Envie hourly_cost ao gerar o relatorio para a API devolver este campo",
      }),
    ]),

    el("div", { class: "grid grid-wide-left" }, [
      el("article", { class: "card" }, [
        el("div", { class: "card-head" }, [el("span", { class: "eyebrow", text: "COMO A CONTA E FEITA" })]),
        el("h3", { text: "Do CSV ate o valor" }),
        el("div", { class: "finding-list" }, [
          el("div", { class: "finding" }, [
            el("span", { class: "finding-title", text: "1. Benchmark (API)" }),
            el("span", { text: `O menor tempo medio entre todas as combinacoes de canal, prioridade e tipo: ${fmt.hours(benchmark, 2)}.` }),
          ]),
          el("div", { class: "finding" }, [
            el("span", { class: "finding-title", text: "2. Excedente (API)" }),
            el("span", { text: `Para cada ticket, quanto o tempo passou do benchmark. Somado, da ${fmt.hoursCompact(hours)}.` }),
          ]),
          el("div", { class: "finding" }, [
            el("span", { class: "finding-title", text: "3. Custo (premissa)" }),
            el("span", { text: `Excedente x custo/hora = ${fmt.money(totalCost)}.` }),
          ]),
          el("div", { class: "finding" }, [
            el("span", { class: "finding-title", text: "4. Captura (premissa)" }),
            el("span", { text: `Eliminando ${fmt.percent(STATE.capture, 0)} desse excedente: ${fmt.money(capturableCost)}.` }),
          ]),
        ]),
      ]),

      el("article", { class: "tile-dark" }, [
        el("span", { class: "eyebrow", text: "PESO DO EXCEDENTE" }),
        el("h3", { text: "Quanto do tempo total esta acima do benchmark" }),
        meter(totalHours ? hours / totalHours : 0, "Participacao do excedente no tempo total"),
        el("p", { class: "card-note", style: "margin-top:12px" }, [
          totalHours
            ? `${fmt.percent(hours / totalHours)} de ${fmt.hoursCompact(totalHours)} estimados no total, sobre ${fmt.num(metrics.ticket_count)} tickets.`
            : "Sem tempo medio na resposta para calcular a participacao.",
        ]),
      ]),
    ]),
  ]);

  if (combos.length) {
    append(body, el("div", { class: "grid" }, [
      chartCard({
        eyebrow: "METRICS.WORST_COMBINATIONS",
        title: "Onde o excedente se concentra",
        note: "Horas acima do benchmark por combinacao, entre as mais lentas que a API retornou. Estas sao as filas que pagam mais caro pela demora.",
        chart: () =>
          barChart({
            items: combos.map((row) => ({
              name: row.name,
              value: row.excessHours,
              display: fmt.money(row.excessHours * STATE.hourlyCost),
              extra: `${fmt.hoursCompact(row.excessHours)} acima do benchmark · ${fmt.num(row.tickets)} tickets`,
            })),
            valueLabel: "Custo do excedente",
          }),
        table: () =>
          dataTable({
            columns: [
              { key: "name", label: "Canal / Prioridade / Tipo" },
              { key: "tickets", label: "Tickets", num: true },
              { key: "avg", label: "Tempo medio", num: true },
              { key: "excess", label: "Horas excedentes", num: true },
              { key: "cost", label: "Custo", num: true },
            ],
            rows: combos.map((row) => ({
              name: row.name,
              tickets: fmt.num(row.tickets),
              avg: fmt.hours(row.avg, 1),
              excess: fmt.hoursCompact(row.excessHours),
              cost: fmt.money(row.excessHours * STATE.hourlyCost),
            })),
          }),
      }),
    ]));
  }

  render(container, body);
}

/* -- Ciclo de vida -------------------------------------------------------- */

export function initCosts() {
  const root = $("#costs-body");

  const params = get("reportParams");
  if (params && Number.isFinite(Number(params.hourly_cost))) {
    STATE.hourlyCost = Number(params.hourly_cost);
  }

  // Formulario e resultados sao montados uma vez; so o segundo e redesenhado.
  const results = el("div");

  const costInput = el("input", {
    type: "number", id: "cost-hourly", min: "0", step: "5", value: String(STATE.hourlyCost),
  });
  const captureInput = el("input", {
    type: "range", id: "cost-capture", min: "0", max: "100", step: "5",
    value: String(Math.round(STATE.capture * 100)),
    style: "min-width:180px;padding:0;height:38px;border:0;accent-color:var(--primary)",
  });
  const captureOut = el("output", { for: "cost-capture", class: "card-note", text: fmt.percent(STATE.capture, 0) });

  const form = el("div", { class: "filters" }, [
    el("div", { class: "field" }, [
      el("label", { for: "cost-hourly", text: "Custo por hora de atendimento (R$)" }),
      costInput,
    ]),
    el("div", { class: "field" }, [
      el("label", { for: "cost-capture", text: "Fatia do excedente que voce consegue eliminar" }),
      el("div", { style: "display:flex;align-items:center;gap:12px" }, [captureInput, captureOut]),
    ]),
    el("p", { class: "filters-hint" }, [
      "As duas entradas acima sao premissas suas. As horas, o benchmark e as combinacoes vem do relatorio da API.",
    ]),
  ]);

  const paint = () => {
    const report = get("report");

    if (!report?.metrics) {
      render(root, emptyState(
        "Rode o relatorio primeiro",
        "Esta tela consome o bloco metrics.waste de POST /reports/support. Sem o relatorio nao ha horas nem benchmark para calcular.",
        el("button", {
          class: "btn btn-primary",
          type: "button",
          onClick: () => document.querySelector('[data-route="overview"]')?.click(),
        }, "Ir para o relatorio"),
      ));
      return;
    }

    if (root.firstChild !== form) render(root, [form, results]);
    renderResults(results, report);
  };

  costInput.addEventListener("input", () => {
    STATE.hourlyCost = Math.max(0, Number(costInput.value) || 0);
    paint();
  });
  captureInput.addEventListener("input", () => {
    STATE.capture = Number(captureInput.value) / 100;
    captureOut.textContent = fmt.percent(STATE.capture, 0);
    paint();
  });

  subscribe((keys) => {
    if (keys.includes("report")) {
      const next = get("reportParams");
      if (next && Number.isFinite(Number(next.hourly_cost))) {
        STATE.hourlyCost = Number(next.hourly_cost);
        costInput.value = String(STATE.hourlyCost);
      }
      paint();
    }
  });

  paint();
}
