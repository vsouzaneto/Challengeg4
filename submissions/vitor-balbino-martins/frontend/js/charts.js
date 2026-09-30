/**
 * Graficos do painel.
 *
 * Decisoes de codificacao (seguem o guia de dataviz):
 *  - Categorias NOMINais (canal, tipo, topico, cluster) usam um unico azul.
 *    Colorir cada barra por tamanho gastaria o canal de identidade repetindo
 *    o que o comprimento ja mostra.
 *  - Categorias ORDINais (prioridade) usam a rampa azul de 4 passos, validada
 *    contra #ffffff e #272729 (monotona, delta L >= 0.06, ponta clara >= 2:1).
 *  - Toda marca e fina, com ponta arredondada em 4px e base reta.
 *  - Todo grafico tem um gemeo em tabela: nenhum valor existe so no hover.
 *  - Serie unica nao ganha caixa de legenda; o titulo ja diz o que esta ali.
 */

import { el, render, append } from "./dom.js";

/* -- Tooltip compartilhado ---------------------------------------------- */

const tip = () => document.getElementById("tooltip");

function showTip(anchor, { value, label, extra }) {
  const node = tip();
  if (!node) return;

  render(node, [
    el("strong", { class: "tooltip-value", text: value }),
    el("span", { class: "tooltip-label", text: label }),
    extra ? el("span", { class: "tooltip-label", text: extra }) : null,
  ]);

  node.dataset.open = "true";
  node.setAttribute("aria-hidden", "false");

  const box = anchor.getBoundingClientRect();
  const size = node.getBoundingClientRect();
  const left = Math.min(Math.max(8, box.left), window.innerWidth - size.width - 8);
  const above = box.top - size.height - 8;
  node.style.left = `${left}px`;
  node.style.top = `${above > 8 ? above : box.bottom + 8}px`;
}

function hideTip() {
  const node = tip();
  if (!node) return;
  node.dataset.open = "false";
  node.setAttribute("aria-hidden", "true");
}

/* -- Stat tile ----------------------------------------------------------- */

/**
 * @param {object} spec
 * @param {string} spec.label
 * @param {string} spec.value    ja formatado
 * @param {string} [spec.unit]
 * @param {string} [spec.foot]
 * @param {{text:string, tone:"good"|"critical"|"neutral"}} [spec.delta]
 *        Tom de status nunca vai sozinho: o texto do delta carrega o sinal.
 * @param {boolean} [spec.hero]  figura heroi (uma por view)
 * @param {boolean} [spec.dark]
 */
export function statTile({ label, value, unit, foot, delta, hero = false, dark = false }) {
  return el("article", { class: `${dark ? "tile-dark" : "card"} stat` }, [
    el("span", { class: "stat-label", text: label }),
    el("strong", { class: `stat-value${hero ? " hero-figure" : ""}` }, [
      value,
      unit ? el("span", { class: "stat-unit", text: ` ${unit}` }) : null,
    ]),
    delta ? el("span", { class: `delta delta-${delta.tone}`, text: delta.text }) : null,
    foot ? el("span", { class: "stat-foot", text: foot }) : null,
  ]);
}

/* -- Medidor ------------------------------------------------------------- */

/** Barra de proporcao unica. `ratio` entre 0 e 1. */
export function meter(ratio, describedBy) {
  const pct = Math.max(0, Math.min(1, Number(ratio) || 0));
  return el(
    "div",
    {
      class: "meter",
      role: "meter",
      "aria-valuenow": Math.round(pct * 100),
      "aria-valuemin": "0",
      "aria-valuemax": "100",
      ...(describedBy ? { "aria-label": describedBy } : {}),
    },
    [el("i", { style: `width:${(pct * 100).toFixed(2)}%` })],
  );
}

/* -- Bloco grafico + tabela --------------------------------------------- */

/**
 * Envolve um grafico com o botao de alternancia para a tabela equivalente.
 * @param {object} spec
 * @param {string} spec.eyebrow
 * @param {string} spec.title
 * @param {string} [spec.note]
 * @param {() => Node} spec.chart
 * @param {() => Node} spec.table
 * @param {boolean} [spec.dark]
 */
export function chartCard({ eyebrow, title, note, chart, table, dark = false, extra }) {
  const body = el("div");
  const card = el("article", { class: dark ? "tile-dark" : "card" });

  const btnChart = el("button", { type: "button", "aria-pressed": "true" }, "Grafico");
  const btnTable = el("button", { type: "button", "aria-pressed": "false" }, "Tabela");

  const show = (mode) => {
    btnChart.setAttribute("aria-pressed", String(mode === "chart"));
    btnTable.setAttribute("aria-pressed", String(mode === "table"));
    render(body, mode === "chart" ? chart() : el("div", { class: "table-wrap" }, [table()]));
  };

  btnChart.addEventListener("click", () => show("chart"));
  btnTable.addEventListener("click", () => show("table"));

  append(card, [
    el("div", { class: "card-head" }, [
      el("span", { class: "eyebrow", text: eyebrow }),
      el("div", { class: "chart-toggle" }, [btnChart, btnTable]),
    ]),
    el("h3", { text: title }),
    note ? el("p", { class: "card-note", text: note }) : null,
    note ? el("div", { style: "height:12px" }) : null,
    body,
    extra,
  ]);

  show("chart");
  return card;
}

/* -- Barras horizontais -------------------------------------------------- */

/**
 * Lista de barras horizontais ordenada.
 *
 * @param {object} spec
 * @param {Array<{name:string, value:number, display?:string, extra?:string}>} spec.items
 * @param {string[]} [spec.ordinalOrder]
 *        Quando informado, as categorias sao tratadas como ordinais e recebem
 *        a rampa de 4 passos na ordem dada. Sem isso, todas usam o mesmo azul.
 * @param {string} [spec.valueLabel] nome da grandeza, usado no tooltip
 */
export function barChart({ items, ordinalOrder = null, valueLabel = "Valor" }) {
  const rows = items.filter((item) => Number.isFinite(item.value));
  if (!rows.length) return el("p", { class: "card-note", text: "Sem dados para exibir." });

  const max = Math.max(...rows.map((r) => Math.abs(r.value)), 0) || 1;

  const ordStep = (name) => {
    if (!ordinalOrder) return null;
    const index = ordinalOrder.findIndex((o) => o.toLowerCase() === String(name).toLowerCase());
    if (index < 0) return null;
    // Distribui os passos 1..4 sobre a ordem informada.
    const span = Math.max(1, ordinalOrder.length - 1);
    return String(1 + Math.round((index / span) * 3));
  };

  const chart = el("div", { class: "chart", role: "list" });

  for (const item of rows) {
    const display = item.display ?? String(item.value);
    const width = (Math.abs(item.value) / max) * 100;
    const step = ordStep(item.name);

    const row = el(
      "div",
      {
        class: "bar-row",
        role: "listitem",
        tabindex: "0",
        "aria-label": `${item.name}: ${display}${item.extra ? `. ${item.extra}` : ""}`,
      },
      [
        el("span", { class: "bar-name", title: item.name, text: item.name }),
        el("div", { class: "bar-track" }, [
          el("div", {
            class: "bar-fill",
            style: `width:${width.toFixed(2)}%`,
            ...(step ? { dataset: { ord: step } } : {}),
          }),
        ]),
        el("span", { class: "bar-value", text: display }),
      ],
    );

    const payload = { value: display, label: `${valueLabel} · ${item.name}`, extra: item.extra };
    row.addEventListener("pointerenter", () => showTip(row, payload));
    row.addEventListener("focus", () => showTip(row, payload));
    row.addEventListener("pointerleave", hideTip);
    row.addEventListener("blur", hideTip);

    chart.appendChild(row);
  }

  return chart;
}

/**
 * Barras divergentes contra uma linha de base (ex.: media geral das notas).
 * Azul acima da base, vermelho de status abaixo - polos quente/frio, com o
 * sinal repetido no rotulo para nao depender da cor.
 */
export function divergingBarChart({ items, baseline, valueLabel = "Valor", format = String, deltaFormat = null }) {
  const fmtDelta = deltaFormat ?? format;
  const rows = items.filter((item) => Number.isFinite(item.value));
  if (!rows.length) return el("p", { class: "card-note", text: "Sem dados para exibir." });

  const max = Math.max(...rows.map((r) => Math.abs(r.value - baseline)), 0) || 1;
  const chart = el("div", { class: "chart", role: "list" });

  for (const item of rows) {
    const delta = item.value - baseline;
    const side = delta >= 0 ? "pos" : "neg";
    const width = (Math.abs(delta) / max) * 50;
    const sign = delta >= 0 ? "+" : "−";
    const deltaText = `${sign}${fmtDelta(Math.abs(delta))}`;

    const fill = el("div", {
      class: "div-fill",
      dataset: { side },
      style: side === "pos"
        ? `left:50%;width:${width.toFixed(2)}%`
        : `right:50%;width:${width.toFixed(2)}%`,
    });

    const row = el(
      "div",
      {
        class: "div-row",
        role: "listitem",
        tabindex: "0",
        "aria-label": `${item.name}: ${format(item.value)}, ${deltaText} em relacao a base ${format(baseline)}`,
      },
      [
        el("span", { class: "bar-name", title: item.name, text: item.name }),
        el("div", { class: "div-track" }, [el("span", { class: "div-zero", style: "left:50%" }), fill]),
        el("span", { class: "bar-value", text: deltaText }),
      ],
    );

    const payload = {
      value: format(item.value),
      label: `${valueLabel} · ${item.name}`,
      extra: `${deltaText} vs. base ${format(baseline)}${item.extra ? ` · ${item.extra}` : ""}`,
    };
    row.addEventListener("pointerenter", () => showTip(row, payload));
    row.addEventListener("focus", () => showTip(row, payload));
    row.addEventListener("pointerleave", hideTip);
    row.addEventListener("blur", hideTip);

    chart.appendChild(row);
  }

  return chart;
}


/* -- Tabela -------------------------------------------------------------- */

/**
 * @param {object} spec
 * @param {string} [spec.caption]
 * @param {Array<{key:string, label:string, num?:boolean}>} spec.columns
 * @param {object[]} spec.rows valores ja formatados como string
 */
export function dataTable({ caption, columns, rows }) {
  return el("table", { class: "data" }, [
    caption ? el("caption", { text: caption }) : null,
    el("thead", {}, [
      el("tr", {}, columns.map((c) => el("th", { class: c.num ? "num" : null, scope: "col", text: c.label }))),
    ]),
    el(
      "tbody",
      {},
      rows.map((row) =>
        el("tr", {}, columns.map((c) => el("td", { class: c.num ? "num" : null, text: row[c.key] ?? "—" }))),
      ),
    ),
  ]);
}

/**
 * Converte um objeto { chave: contagem } em itens de barra.
 *
 * Nominal sai do maior para o menor (o ranking e a informacao). Ordinal sai na
 * ordem natural, para a rampa de cor crescer junto com a posicao na lista -
 * ordenar por contagem embaralharia os passos da rampa.
 */
export function countsToItems(counts, total = null, ordinalOrder = null) {
  if (!counts || typeof counts !== "object") return [];
  const entries = Object.entries(counts).filter(([, v]) => Number.isFinite(Number(v)));
  const sum = total ?? entries.reduce((acc, [, v]) => acc + Number(v), 0);
  const items = entries.map(([name, value]) => ({
    name, value: Number(value), share: sum ? Number(value) / sum : 0,
  }));

  if (!ordinalOrder) return items.sort((a, b) => b.value - a.value);

  const rank = (name) => {
    const i = ordinalOrder.findIndex((o) => o.toLowerCase() === String(name).toLowerCase());
    return i < 0 ? ordinalOrder.length : i;
  };
  return items.sort((a, b) => rank(a.name) - rank(b.name) || b.value - a.value);
}

export { hideTip };
