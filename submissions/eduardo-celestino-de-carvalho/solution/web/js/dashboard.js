/* Dashboard: relatório de uma página para a gestão comercial. */
import { GLOSSARY, GROUPS, LANE, LANE_ORDER, info } from "./terms.js";
import { bindTooltip, compact, downloadCsv, esc, fmt, pct } from "./format.js";
import { scopedItems, scopedTeam, scopeLabel, state } from "./state.js";

const el = {
  root: document.getElementById("dashboard"),
  summary: document.getElementById("dashboard-summary"),
  groupBy: document.getElementById("group-by"),
};
const GRAY = "#A3A9B3";
const COMPOSITION_LIMIT = 15;
const INSIDE_BINS = 9; // o prazo máximo cai exatamente na divisa da 9ª coluna do histograma
let rows = [];        // linhas agregadas do agrupamento atual
let agents = [];      // linhas por vendedor (rankings)
let tableSort = { key: "negociarValue", dir: -1 };
let showAllRows = false;
let moreDataOpen = false;
let bins = { closed: [], open: [], size: 1 };

/* ---------- agregação ---------- */
function emptyRow(name, extra = {}) {
  const row = { name, ...extra, count: 0, value: 0, won: 0, lost: 0, revenue: 0, agents: new Set() };
  for (const lane of LANE_ORDER) { row[`${lane}Count`] = 0; row[`${lane}Value`] = 0; }
  return row;
}

function aggregate(groupBy) {
  const group = GROUPS[groupBy];
  const map = new Map();
  // Todos os membros do escopo aparecem, inclusive quem não tem oportunidades abertas.
  for (const member of scopedTeam()) {
    const key = group.key(member);
    if (!map.has(key)) map.set(key, emptyRow(key, { manager: member.manager, region: member.region }));
    map.get(key).agents.add(member.agent);
  }
  for (const item of scopedItems()) {
    const key = group.key(item);
    if (!map.has(key)) map.set(key, emptyRow(key, { manager: item.manager, region: item.region }));
    const row = map.get(key);
    row.count += 1;
    row.value += item.price;
    row[`${item.lane}Count`] += 1;
    row[`${item.lane}Value`] += item.price;
  }
  for (const row of map.values()) {
    for (const agent of row.agents) {
      const h = state.data.history.agent[agent];
      if (h) { row.won += h.won; row.lost += h.lost; row.revenue += h.revenue; }
    }
    const engaging = row.negociarValue + row.encerrarValue;
    row.health = engaging ? row.negociarValue / engaging : null;
    row.winRate = row.won + row.lost ? row.won / (row.won + row.lost) : null;
  }
  return [...map.values()];
}

const sum = (list, field) => list.reduce((acc, r) => acc + r[field], 0);

/* ---------- indicadores ---------- */
function kpis() {
  const neg = sum(rows, "negociarValue"), qual = sum(rows, "qualificarValue"), enc = sum(rows, "encerrarValue");
  const total = neg + qual + enc;
  const health = neg + enc ? neg / (neg + enc) : 0;
  const max = state.data.reference.maxCycle;
  const tile = (lane, label, tip, value, note) => `
    <div class="kpi">
      <div class="kpi-label"><i class="key" style="background:${LANE[lane].color}"></i>${label}${info(tip)}</div>
      <div class="kpi-value">${value}</div>
      <div class="kpi-note">${note}</div>
    </div>`;
  return `
    <section class="kpis">
      ${tile("negociar", "Em negociação, no prazo", GLOSSARY.negociar(max), compact(neg), `${fmt(sum(rows, "negociarCount"))} negócios com chance de fechar`)}
      ${tile("qualificar", "A qualificar", GLOSSARY.qualificar, compact(qual), `${fmt(sum(rows, "qualificarCount"))} oportunidades em prospecção`)}
      ${tile("encerrar", "A confirmar ou encerrar", GLOSSARY.encerrar(max), compact(enc), `${fmt(sum(rows, "encerrarCount"))} negócios parados · ${pct(enc, total)} do valor total`)}
      <div class="kpi">
        <div class="kpi-label">Pipeline no prazo${info(GLOSSARY.saude)}</div>
        <div class="kpi-value">${pct(neg, neg + enc)}</div>
        <div class="meter" aria-hidden="true"><span style="width:${health * 100}%"></span></div>
        <div class="kpi-note">De cada 100 em negociação, ${Math.round(health * 100)} ainda estão no prazo.</div>
      </div>
    </section>`;
}

function legend() {
  return `<div class="legend">${LANE_ORDER.map((l) => `<span><i style="background:${LANE[l].color}"></i>${LANE[l].title}</span>`).join("")}</div>`;
}

function composition(groupBy) {
  const all = [...rows].sort((a, b) => b.value - a.value);
  const list = showAllRows ? all : all.slice(0, COMPOSITION_LIMIT);
  const max = Math.max(1, ...list.map((r) => r.value));
  const label = GROUPS[groupBy].label.toLowerCase();
  const toggle = all.length > COMPOSITION_LIMIT
    ? `<button type="button" class="more-btn more-inline" data-show-all>${showAllRows ? `Mostrar só os ${COMPOSITION_LIMIT} maiores` : `Ver todos os ${all.length} ${GROUPS[groupBy].plural}`}</button>` : "";
  return `
    <section class="card-block">
      <header class="block-head">
        <div>
          <h2>Onde está o valor, por ${label}</h2>
          <p>Cada barra soma o valor das oportunidades abertas, dividido pelas três colunas. Passe o mouse para ver os números.</p>
        </div>
        ${legend()}
      </header>
      <div class="stack-chart" role="list">
        ${list.map((r) => `
          <div class="stack-row" role="listitem">
            <span class="stack-name" title="${esc(r.name)}">${esc(r.name)}</span>
            <span class="stack-track">
              <span class="stack-bar" style="width:${(r.value / max) * 100}%">
                ${LANE_ORDER.filter((l) => r[`${l}Value`] > 0).map((l) =>
                  `<span class="seg" tabindex="0" data-tip="comp:${all.indexOf(r)}" style="flex-grow:${r[`${l}Value`]};background:${LANE[l].color}"></span>`).join("")}
              </span>
              <span class="stack-total">${r.value ? compact(r.value) : "sem oportunidades"}${r.health !== null ? `<small>${Math.round(r.health * 100)}% no prazo</small>` : ""}</span>
            </span>
          </div>`).join("")}
      </div>
      ${toggle}
    </section>`;
}

/* ---------- rankings ---------- */
function rankCard(title, subtitle, list, field, color, format) {
  const max = Math.max(1, ...list.map((r) => r[field] ?? 0));
  return `
    <section class="card-block rank">
      <header class="block-head"><div><h2>${title}</h2><p>${subtitle}</p></div></header>
      ${list.length ? `<ol class="rank-list">${list.map((r, i) => `
        <li>
          <span class="rank-pos">${i + 1}</span>
          <span class="rank-name">${esc(r.name)}<small>${esc(r.manager)} · ${esc(r.region)}</small></span>
          <span class="rank-bar"><span style="width:${((r[field] ?? 0) / max) * 100}%;background:${color}"></span></span>
          <span class="rank-value">${format(r)}</span>
        </li>`).join("")}</ol>` : `<p class="empty">Nada a destacar neste recorte.</p>`}
    </section>`;
}

function rankings() {
  const top = (field) => [...agents].filter((r) => r[field] > 0).sort((a, b) => b[field] - a[field]).slice(0, 5);
  const weakest = [...agents].filter((r) => r.health !== null).sort((a, b) => a.health - b.health || b.encerrarValue - a.encerrarValue).slice(0, 5);
  const idle = agents.filter((r) => r.negociarCount === 0).sort((a, b) => b.encerrarValue - a.encerrarValue);
  return `
    <div class="rank-grid">
      ${rankCard("Mais valor para fechar", "Quem tem mais valor em negociação dentro do prazo.", top("negociarValue"), "negociarValue", LANE.negociar.color,
        (r) => `${compact(r.negociarValue)}<small>${r.negociarCount} negócios</small>`)}
      ${rankCard("Mais valor parado", "Quem mais precisa confirmar ou encerrar negócios.", top("encerrarValue"), "encerrarValue", LANE.encerrar.color,
        (r) => `${compact(r.encerrarValue)}<small>${r.encerrarCount} negócios</small>`)}
      ${rankCard("Menos pipeline no prazo", "Menor parte do valor em negociação ainda no prazo.", weakest, "health", "#5b6472",
        (r) => `${pct(r.negociarValue, r.negociarValue + r.encerrarValue)}<small>no prazo</small>`)}
      <section class="card-block rank">
        <header class="block-head"><div><h2>Sem negociação ativa</h2><p>Nenhum negócio na coluna Negociar.</p></div></header>
        ${idle.length ? `<ul class="idle-list">${idle.map((r) => `
          <li><span>${esc(r.name)}<small>${esc(r.manager)}</small></span><span class="idle-meta">${r.count ? `${r.qualificarCount} a qualificar<br>${r.encerrarCount} parados` : "sem oportunidades"}</span></li>`).join("")}</ul>`
          : `<p class="empty">Todos têm negociações ativas.</p>`}
      </section>
    </div>`;
}

/* ---------- por que a fila funciona assim ---------- */
function phaseResults(backtest) {
  const phases = [["Início", "até 14"], ["Em andamento", "15 a 89"], ["Perto do limite", "90 a 138"]].map(([p, label]) => ({
    label,
    deals: backtest.reduce((acc, c) => acc + (c.phases[p]?.deals || 0), 0),
    won: backtest.reduce((acc, c) => acc + (c.phases[p]?.won || 0), 0),
  }));
  phases.push({
    label: "mais de 138",
    deals: backtest.reduce((acc, c) => acc + c.cleanup.deals, 0),
    won: backtest.reduce((acc, c) => acc + c.cleanup.won, 0),
  });
  return phases.map((p) => ({ ...p, rate: p.deals ? p.won / p.deals : 0 }));
}

function fact(step, number, text, visual, conclusion) {
  return `
    <article class="fact">
      <span class="fact-step">${step}</span>
      <div class="fact-number">${number}</div>
      <p class="fact-text">${text}</p>
      <div class="fact-visual">${visual}</div>
      <p class="fact-conclusion">${conclusion}</p>
    </article>`;
}

function evidence() {
  const { reference, backtest } = state.data;
  const max = reference.maxCycle;
  const open = scopedItems().filter((i) => i.days !== null);
  const over = open.filter((i) => i.days > max);
  const overValue = over.reduce((acc, i) => acc + i.price, 0);
  const overShare = open.length ? over.length / open.length : 0;

  const fact1 = fact(1, `${max} dias`, "é o maior tempo que uma venda já levou para fechar.",
    `<div class="split-bar"><span class="split-a" style="flex:9;background:${LANE.negociar.color}">${fmt(reference.closed)} vendas</span><span class="split-b is-hatched" style="flex:2">0</span></div>
     <div class="split-legend"><span>fecharam em até ${max} dias</span><span>depois</span></div>`,
    `Por isso, acima de ${max} dias o negócio vai para <b>Confirmar ou encerrar</b>.`);

  const fact2 = fact(2, pct(over.length, open.length), "dos negócios em negociação já passaram desse prazo.",
    `<div class="split-bar"><span class="split-a" style="flex:${Math.max(1 - overShare, 0.08)};background:${LANE.negociar.color}">${fmt(open.length - over.length)}</span><span class="split-b" style="flex:${Math.max(overShare, 0.08)};background:${LANE.encerrar.color}">${fmt(over.length)}</span></div>
     <div class="split-legend"><span>no prazo</span><span>prazo excedido</span></div>`,
    `São <b>${compact(overValue)}</b> em valor que parecem pipeline, mas estão parados.`);

  let fact3 = "", fact4 = "";
  if (backtest && backtest.length) {
    const phases = phaseResults(backtest);
    const top = Math.max(...phases.map((p) => p.rate), 0.01);
    fact3 = fact(3, pct(phases[0].won, phases[0].deals), `dos negócios novos viraram venda. Perto do limite, só ${pct(phases[2].won, phases[2].deals)}.`,
      `<div class="mini-cols" role="list">${phases.map((p) => `
        <div class="mini-col" role="listitem" aria-label="${p.label} dias: ${pct(p.won, p.deals)} viraram venda">
          <span class="mini-val">${pct(p.won, p.deals)}</span>
          <span class="mini-bar"><span style="height:${(p.rate / top) * 100}%;background:${LANE.negociar.color}"></span></span>
          <span class="mini-label">${p.label}</span>
        </div>`).join("")}</div>
       <div class="mini-caption">dias em negociação</div>`,
      "Por isso, no empate de valor, <b>o negócio mais recente vem primeiro</b>.");

    // Comparação com o método óbvio (só valor) e o passo intermediário: tirar os parados sem olhar a idade.
    const total = (key, field) => backtest.reduce((acc, c) => acc + (c.top5[key]?.[field] || 0), 0);
    const current = total("focus_rule", "won_revenue"), byValue = total("price_only_no_lanes", "won_revenue");
    const noStale = total("lanes_price_no_recency", "won_revenue");
    const ci = state.data.decomposition?.bootstrap?.focus_rule_vs_price_only_no_lanes?.ci95;
    const margin = ci ? ` Margem provável: de +${Math.round(ci[0] * 100)}% a +${Math.round(ci[1] * 100)}%.` : "";
    const bar = (label, value, color) =>
      `<div><span>${label}</span><span class="compare-bar"><span style="width:${(value / current) * 100}%;background:${color}"></span></span><b>${compact(value)}</b></div>`;
    fact4 = fact(4, `+${pct(current - byValue, byValue)}`, `de receita em relação a ordenar só pelo valor, num teste com dados passados.${margin}`,
      `<div class="compare">
         ${bar("Só pelo valor", byValue, GRAY)}
         ${noStale ? bar("Sem os parados", noStale, "#8fb3d4") : ""}
         ${bar("Lead Kanban", current, LANE.negociar.color)}
       </div>`,
      "Vem da idade do negócio: <b>tirar os parados</b> da fila e, no empate de valor, <b>começar pelo mais novo</b>.");
  }

  return `
    <section class="card-block">
      <header class="block-head">
        <div>
          <h2>Por que a fila funciona assim</h2>
          <p>Quatro fatos dos dados de vendas que definem as colunas e a ordem dos cartões.</p>
        </div>
      </header>
      <div class="facts-grid">${fact1}${fact2}${fact3}${fact4}</div>
      <details class="more-data"${moreDataOpen ? " open" : ""}>
        <summary>Ver dados completos</summary>
        ${histograms(open)}
      </details>
    </section>`;
}

/* Detalhe opcional para análise: distribuição completa por tempo de negociação. */
function binLabel(i) {
  const from = Math.ceil(i * bins.size), to = Math.ceil((i + 1) * bins.size) - 1;
  return `${from} a ${to} dias`;
}

function histogram(kind, data, series, maxCount) {
  return `
    <div class="histo-wrap">
      <span class="histo-max">${fmt(maxCount)}</span>
      <div class="histo" role="list">
        ${data.map((b, i) => `<span class="histo-col" role="listitem" tabindex="0" data-tip="${kind}:${i}" aria-label="${binLabel(i)}">
          ${series.filter((s) => b[s.key] > 0).map((s) => `<span class="histo-seg" style="height:${(b[s.key] / maxCount) * 100}%;background:${s.color}"></span>`).join("")}
        </span>`).join("")}
        <span class="histo-limit" style="left:${(INSIDE_BINS / data.length) * 100}%"></span>
      </div>
    </div>`;
}

function histograms(open) {
  const { closedCycles, reference } = state.data;
  const max = reference.maxCycle;
  bins.size = (max + 1) / INSIDE_BINS;
  const maxDays = Math.max(max, ...open.map((i) => i.days));
  const count = Math.ceil((maxDays + 1) / bins.size);
  bins.closed = Array.from({ length: count }, () => ({ won: 0, lost: 0 }));
  bins.open = Array.from({ length: count }, () => ({ inside: 0, over: 0 }));
  closedCycles.won.forEach((n, d) => { bins.closed[Math.floor(d / bins.size)].won += n; });
  closedCycles.lost.forEach((n, d) => { bins.closed[Math.floor(d / bins.size)].lost += n; });
  for (const item of open) bins.open[Math.floor(item.days / bins.size)][item.days > max ? "over" : "inside"] += 1;
  const axis = `<div class="histo-axis"><span>0</span><span class="mid" style="left:${(INSIDE_BINS / count) * 100}%">${max} dias</span><span class="end">${maxDays} dias</span></div>`;
  return `
    <div class="histo-grid">
      <div>
        <h3 class="chart-title">Vendas concluídas, por tempo até fechar</h3>
        <div class="legend"><span><i style="background:${LANE.negociar.color}"></i>Ganhas</span><span><i style="background:${GRAY}"></i>Perdidas</span></div>
        ${histogram("closed", bins.closed, [{ key: "won", color: LANE.negociar.color }, { key: "lost", color: GRAY }], Math.max(...bins.closed.map((b) => b.won + b.lost)))}
        ${axis}
      </div>
      <div>
        <h3 class="chart-title">Negócios abertos, por tempo em negociação</h3>
        <div class="legend"><span><i style="background:${LANE.negociar.color}"></i>No prazo</span><span><i style="background:${LANE.encerrar.color}"></i>Prazo excedido</span></div>
        ${histogram("open", bins.open, [{ key: "inside", color: LANE.negociar.color }, { key: "over", color: LANE.encerrar.color }], Math.max(1, ...bins.open.map((b) => b.inside + b.over)))}
        ${axis}
      </div>
    </div>
    <p class="chart-note">Teste com dados passados: em 5 datas de 2017, cada regra escolheu 5 negócios por vendedor usando só o que se sabia naquela data; depois vimos quais viraram venda. O resultado é exploratório e está documentado no procedimento (botão ?).</p>`;
}

/* ---------- tabela ---------- */
const COLUMNS = [
  { key: "negociarCount", label: "Negociar", sub: "negócios" },
  { key: "negociarValue", label: "Negociar", sub: "valor" },
  { key: "qualificarValue", label: "Qualificar", sub: "valor" },
  { key: "encerrarValue", label: "Confirmar ou encerrar", sub: "valor" },
  { key: "value", label: "Total", sub: "valor" },
  { key: "health", label: "No prazo", sub: "% do valor" },
  { key: "winRate", label: "Vendas ganhas", sub: "histórico" },
  { key: "revenue", label: "Receita ganha", sub: "histórico" },
];

function cellValue(row, key) {
  if (key === "health" || key === "winRate") return row[key] === null ? "—" : `${Math.round(row[key] * 100)}%`;
  if (key.endsWith("Count")) return fmt(row[key]);
  return row[key] ? fmt(row[key]) : "—";
}

function sortedRows() {
  const { key, dir } = tableSort;
  return [...rows].sort((a, b) => ((a[key] ?? -1) - (b[key] ?? -1)) * dir || a.name.localeCompare(b.name));
}

const extraHeaders = (groupBy) => (groupBy === "agent" ? ["Manager", "Regional"] : groupBy === "manager" ? ["Regional"] : []);
const extraCells = (groupBy, r) => (groupBy === "agent" ? [r.manager, r.region] : groupBy === "manager" ? [r.region] : []);

function table(groupBy) {
  const label = GROUPS[groupBy].label;
  return `
    <section class="card-block">
      <header class="block-head">
        <div><h2>Tabela por ${label.toLowerCase()}</h2><p>Clique no nome de uma coluna para ordenar.</p></div>
      </header>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr>
            <th scope="col">${label}</th>${extraHeaders(groupBy).map((h) => `<th scope="col">${h}</th>`).join("")}
            ${COLUMNS.map((c) => `<th scope="col" class="num" aria-sort="${tableSort.key === c.key ? (tableSort.dir < 0 ? "descending" : "ascending") : "none"}"><button type="button" data-sort="${c.key}" class="${tableSort.key === c.key ? "is-sorted" : ""}">${c.label}<small>${c.sub}${tableSort.key === c.key ? (tableSort.dir < 0 ? " ↓" : " ↑") : ""}</small></button></th>`).join("")}
          </tr></thead>
          <tbody>${sortedRows().map((r) => `
            <tr><th scope="row">${esc(r.name)}</th>${extraCells(groupBy, r).map((v) => `<td>${esc(v)}</td>`).join("")}
            ${COLUMNS.map((c) => `<td class="num">${cellValue(r, c.key)}</td>`).join("")}</tr>`).join("")}
          </tbody>
        </table>
      </div>
    </section>`;
}

/* ---------- render e eventos ---------- */
export function renderDashboard() {
  const groupBy = state.groupBy;
  rows = aggregate(groupBy);
  agents = groupBy === "agent" ? rows : aggregate("agent");
  el.groupBy.querySelectorAll("[data-group]").forEach((b) => b.setAttribute("aria-checked", b.dataset.group === groupBy));
  el.summary.textContent = `${scopeLabel()} · ${fmt(sum(rows, "count"))} oportunidades abertas · ${fmt(agents.length)} vendedores`;
  el.root.innerHTML = kpis() + composition(groupBy) + rankings() + evidence() + table(groupBy);
}

function exportDashboard() {
  const groupBy = state.groupBy;
  const header = [GROUPS[groupBy].label, ...extraHeaders(groupBy), "Negociar (negócios)", "Negociar (valor)", "Qualificar (valor)",
    "Confirmar ou encerrar (valor)", "Total (valor)", "No prazo (%)", "Vendas ganhas no histórico (%)", "Receita ganha no histórico"];
  const ratio = (v) => (v === null ? "" : Math.round(v * 100));
  const data = sortedRows().map((r) => [r.name, ...extraCells(groupBy, r), r.negociarCount, r.negociarValue,
    r.qualificarValue, r.encerrarValue, r.value, ratio(r.health), ratio(r.winRate), r.revenue]);
  downloadCsv(`lead-kanban-dashboard-${GROUPS[groupBy].plural}.csv`, header, data);
}

export function bindDashboard() {
  el.groupBy.addEventListener("click", (e) => {
    const button = e.target.closest("[data-group]");
    if (!button) return;
    state.groupBy = button.dataset.group;
    showAllRows = false;
    document.dispatchEvent(new CustomEvent("lk:prefs"));
    renderDashboard();
  });
  el.root.addEventListener("click", (e) => {
    if (e.target.closest("[data-show-all]")) { showAllRows = !showAllRows; renderDashboard(); return; }
    const header = e.target.closest("[data-sort]");
    if (!header) return;
    const key = header.dataset.sort;
    tableSort = { key, dir: tableSort.key === key ? -tableSort.dir : -1 };
    renderDashboard();
  });
  el.root.addEventListener("toggle", (e) => {
    if (e.target.matches(".more-data")) moreDataOpen = e.target.open;
  }, true);
  bindTooltip(el.root, (target) => {
    const [kind, raw] = target.dataset.tip.split(":");
    const index = Number(raw);
    if (kind === "closed") {
      const b = bins.closed[index];
      return { title: `${binLabel(index)} até fechar`, rows: [
        { color: LANE.negociar.color, value: fmt(b.won), label: "ganhas" },
        { color: GRAY, value: fmt(b.lost), label: "perdidas" }] };
    }
    if (kind === "open") {
      const b = bins.open[index];
      return { title: `${binLabel(index)} em negociação`, rows: [
        { color: LANE.negociar.color, value: fmt(b.inside), label: "no prazo" },
        { color: LANE.encerrar.color, value: fmt(b.over), label: "prazo excedido" }] };
    }
    const r = [...rows].sort((a, b) => b.value - a.value)[index];
    if (!r) return null;
    return {
      title: r.name,
      rows: LANE_ORDER.map((l) => ({ color: LANE[l].color, value: fmt(r[`${l}Value`]), label: `${LANE[l].title} · ${r[`${l}Count`]}` })),
    };
  });
  document.getElementById("export-dashboard").addEventListener("click", exportDashboard);
}
