/* Pipeline: quadro Kanban em três colunas e detalhe da oportunidade. */
import { GLOSSARY, LANE, LANE_ORDER, NEGOTIATION_PHASES, PHASE, SECTORS, STAGE, info } from "./terms.js";
import { compact, downloadCsv, esc, firstName, fmt, fmtDate, initials, median, readStore, writeStore } from "./format.js";
import { doneFor, scopedItems, state, toggleDone } from "./state.js";
import { openHelp } from "./help.js";

const PAGE = 25;
const GUIDE_KEY = "lead-kanban-guide-dismissed";
const el = {
  board: document.getElementById("board"),
  guide: document.getElementById("pipeline-guide"),
  summary: document.getElementById("pipeline-summary"),
  modal: document.getElementById("deal-modal"),
  content: document.getElementById("deal-content"),
};
let shown = {};
let byLane = {};
let current = null; // { lane, index }

const maxCycle = () => state.data.reference.maxCycle;
const phaseInfo = (item) => PHASE[item.phase] || PHASE["Sem data"];
const stageLabel = (stage) => STAGE[stage] || stage;

function visibleItems() {
  const items = scopedItems().filter((i) => !state.onlyMissing || !i.account);
  // Os itens chegam na ordem recomendada; o sort estável preserva o desempate.
  if (state.sort === "recent") items.sort((a, b) => (a.days ?? Infinity) - (b.days ?? Infinity));
  if (state.sort === "oldest") items.sort((a, b) => (b.days ?? -1) - (a.days ?? -1));
  return items;
}

export function resetPaging() { shown = {}; }

/* Guia rápido para quem abre o quadro pela primeira vez. */
function renderGuide() {
  if (readStore(GUIDE_KEY, false)) { el.guide.hidden = true; return; }
  el.guide.hidden = false;
  el.guide.innerHTML = `
    <div class="guide-steps">
      ${LANE_ORDER.map((id, i) => `
        <div class="guide-step"><span class="guide-num" style="background:${LANE[id].color}">${i + 1}</span>
          <div><strong>${LANE[id].title}</strong><span>${LANE[id].pitch}</span></div></div>`).join("")}
    </div>
    <div class="guide-actions">
      <span>Clique em um cartão para ver o que fazer.</span>
      <button type="button" class="ghost-btn" data-guide-video>▶ Assistir tutorial (2 min)</button>
      <button type="button" class="ghost-btn" data-guide-help>Ver regras completas</button>
      <button type="button" class="primary-btn" data-guide-close>Entendi</button>
    </div>`;
}

export function renderPipeline() {
  const items = visibleItems();
  byLane = Object.fromEntries(LANE_ORDER.map((id) => [id, []]));
  for (const item of items) byLane[item.lane].push(item);
  const total = items.reduce((sum, i) => sum + i.price, 0);
  el.summary.textContent = `${fmt(items.length)} oportunidades abertas · ${compact(total)} em valor potencial`;
  renderGuide();
  el.board.setAttribute("aria-busy", "false");
  el.board.innerHTML = state.data.lanes.map((lane) => laneHtml(lane, byLane[lane.id])).join("");
}

function laneHtml(lane, items) {
  const limit = shown[lane.id] || PAGE;
  const value = items.reduce((sum, i) => sum + i.price, 0);
  const rest = items.length - limit;
  const definition = typeof GLOSSARY[lane.id] === "function" ? GLOSSARY[lane.id](maxCycle()) : GLOSSARY[lane.id];
  return `
    <section class="lane" style="--lane:${LANE[lane.id].color}" aria-labelledby="lane-${lane.id}">
      <header class="lane-head">
        <div class="lane-title-row">
          <i class="lane-key" aria-hidden="true"></i>
          <h2 id="lane-${lane.id}">${esc(lane.title)}</h2>
          ${info(definition)}
          <span class="lane-count" title="Oportunidades nesta coluna">${fmt(items.length)}</span>
        </div>
        <p class="lane-pitch">${LANE[lane.id].pitch}</p>
        <div class="lane-value">${compact(value)} <span>em valor potencial</span></div>
        ${laneMeta(lane.id, items)}
      </header>
      <div class="lane-list">
        ${items.slice(0, limit).map((item, i) => cardHtml(item, lane.id, i)).join("") || `<div class="lane-empty">${emptyText(lane.id)}</div>`}
        ${rest > 0 ? `<button type="button" class="more-btn" data-more="${lane.id}">Mostrar mais ${Math.min(rest, PAGE)} de ${fmt(rest)}</button>` : ""}
      </div>
    </section>`;
}

function laneMeta(laneId, items) {
  if (!items.length) return "";
  if (laneId === "negociar") {
    return `<div class="lane-meta">${NEGOTIATION_PHASES.map((p) =>
      `<span class="tag ${PHASE[p].tag}" title="${esc(PHASE[p].hint)}">${p} · ${items.filter((i) => i.phase === p).length}</span>`).join("")}</div>`;
  }
  if (laneId === "encerrar") {
    return `<div class="lane-meta"><span class="meta-text">Parados, em média, há <b>${fmt(median(items.map((i) => i.days)))} dias</b></span></div>`;
  }
  return `<div class="lane-meta"><span class="meta-text"><b>${fmt(items.filter((i) => !i.account).length)}</b> sem empresa cadastrada</span></div>`;
}

function emptyText(laneId) {
  if (laneId === "negociar" && state.filters.agent) {
    return `${esc(firstName(state.filters.agent))} não tem negócios dentro do prazo. Foco em qualificar e em confirmar ou encerrar.`;
  }
  return "Nenhuma oportunidade com os filtros atuais.";
}

function phaseTag(item) {
  return `<span class="tag ${phaseInfo(item).tag}" title="${esc(phaseInfo(item).hint)}">${esc(item.phase)}</span>`;
}

function deadlineHtml(item) {
  const max = maxCycle();
  if (item.days === null) {
    return `<div class="deadline"><div class="deadline-track is-empty"></div><div class="deadline-label">Negociação ainda não iniciada</div></div>`;
  }
  if (item.daysBeyond) {
    return `<div class="deadline"><div class="deadline-track is-over"><span style="width:100%"></span></div>
      <div class="deadline-label"><b>${item.days} dias</b> em negociação · <b class="is-over">${item.daysBeyond} além do prazo</b></div></div>`;
  }
  return `<div class="deadline"><div class="deadline-track"><span style="width:${(item.days / max) * 100}%"></span></div>
    <div class="deadline-label"><b>${item.days} dias</b> em negociação · faltam ${max - item.days}</div></div>`;
}

function cardHtml(item, laneId, index) {
  const done = doneFor(item).length;
  const total = item.actions.length;
  return `
    <button type="button" class="card${done === total ? " is-done" : ""}" data-lane="${laneId}" data-index="${index}"
            aria-label="Abrir ${esc(item.product)}, ${esc(item.account || "conta pendente")}, valor ${fmt(item.price)}">
      <div class="card-top">
        <span class="card-rank" title="Posição na coluna">#${index + 1}</span>
        <span class="card-title">${esc(item.product)}</span>
        <span class="card-value" title="Valor potencial (preço de tabela)">${fmt(item.price)}</span>
      </div>
      <div class="card-account${item.account ? "" : " is-missing"}">${item.account ? esc(item.account) : "Conta pendente"}</div>
      ${deadlineHtml(item)}
      <div class="card-foot">
        <span class="avatar" aria-hidden="true">${esc(initials(item.agent))}</span>
        <span class="card-agent">${esc(item.agent)}</span>
        ${item.phase === "Sem data" ? "" : phaseTag(item)}
        <span class="progress${done === total ? " is-complete" : ""}" title="Ações concluídas">
          <span class="progress-bar"><span style="width:${(done / total) * 100}%"></span></span>${done}/${total}
        </span>
      </div>
    </button>`;
}

/* ---------- detalhe ---------- */
function ringHtml(item) {
  const max = maxCycle();
  const r = 34, c = 2 * Math.PI * r;
  let frac = 0, big = "—", small = "sem início", stroke = "#d8c19c";
  if (item.days !== null) {
    frac = Math.min(item.days / max, 1);
    big = item.days;
    small = "dias";
    if (item.daysBeyond) stroke = "#e58b79";
  }
  const label = item.days === null ? "Negociação ainda não iniciada" : `${item.days} dias em negociação; prazo máximo de ${max}`;
  return `
    <div class="ring" role="img" aria-label="${label}">
      <svg viewBox="0 0 84 84" width="100%" height="100%">
        <circle cx="42" cy="42" r="${r}" fill="none" stroke="rgba(255,255,255,.14)" stroke-width="7"/>
        <circle cx="42" cy="42" r="${r}" fill="none" stroke="${stroke}" stroke-width="7" stroke-linecap="round" stroke-dasharray="${c * frac} ${c}" transform="rotate(-90 42 42)"/>
      </svg>
      <div class="ring-label"><strong>${big}</strong><small>${small}</small></div>
    </div>`;
}

function timelineHtml(item) {
  const { maxCycle: max, medianLost, medianWon } = state.data.reference;
  if (item.days === null) {
    return `<p class="plain">A negociação ainda não começou. A contagem de dias começa quando o negócio entra em negociação.</p>`;
  }
  const scale = Math.max(max, item.days) * 1.04;
  const at = (d) => `${(d / scale) * 100}%`;
  const status = item.daysBeyond
    ? `Está <strong>${item.daysBeyond} dias além</strong> do maior tempo que uma venda já levou.`
    : `Faltam <strong>${max - item.days} dias</strong> para o maior tempo que uma venda já levou.`;
  return `
    <p class="plain">${status}</p>
    <div class="ruler" aria-hidden="true">
      <div class="ruler-track">
        <span class="ruler-in" style="width:${at(max)}"></span>
        <span class="ruler-deal${item.daysBeyond ? " is-over" : ""}${item.days / scale > 0.7 ? " is-right" : ""}" style="left:${at(item.days)}"><em>este negócio</em></span>
      </div>
      <div class="ruler-scale"><span>0</span><span style="left:${at(max)}">${max} dias</span></div>
    </div>
    <ul class="facts-list">
      <li><b>${medianLost} dias</b> metade das vendas perdidas se decide até aqui</li>
      <li><b>${medianWon} dias</b> metade das vendas ganhas fecha até aqui</li>
      <li><b>${max} dias</b> nenhuma venda fechou depois disso</li>
    </ul>`;
}

function historyRow(label, h) {
  if (!h || h.won + h.lost === 0) return `<div class="hist-row"><span class="hist-label">${label}</span><span class="hist-nums is-muted">sem vendas concluídas</span></div>`;
  const total = h.won + h.lost;
  return `
    <div class="hist-row">
      <span class="hist-label">${label}</span>
      <span class="wl" aria-hidden="true"><span class="w" style="width:${(h.won / total) * 100}%"></span><span class="l" style="width:${(h.lost / total) * 100}%"></span></span>
      <span class="hist-nums">${h.won} de ${total} ganhas</span>
    </div>`;
}

function detailHtml(item, position, total) {
  const { accounts, products, history, lanes } = state.data;
  const lane = lanes.find((l) => l.id === item.lane);
  const account = item.account ? accounts[item.account] : null;
  const done = new Set(doneFor(item));
  const accHistory = item.account ? history.account[item.account] : null;

  const accountPanel = account ? `
    <dl class="facts">
      <dt>Empresa</dt><dd>${esc(item.account)}</dd>
      <dt>Setor</dt><dd>${esc(SECTORS[account.sector] || account.sector)}</dd>
      <dt>Faturamento anual</dt><dd>${fmt(account.revenue)} mi</dd>
      <dt>Funcionários</dt><dd>${fmt(account.employees)}</dd>
      <dt>Sede</dt><dd>${esc(account.location)}</dd>
      ${account.subsidiaryOf ? `<dt>Grupo</dt><dd>${esc(account.subsidiaryOf)}</dd>` : ""}
    </dl>` : `<div class="alert">Sem empresa cadastrada no CRM. Cadastrar está na lista de ações; isso não muda a ordem do negócio.</div>`;

  return `
    <header class="modal-head" style="--lane:${LANE[item.lane].color}">
      <div class="modal-head-main">
        <p class="kicker"><i class="lane-key" aria-hidden="true"></i>${esc(lane.title)} · #${position + 1} de ${fmt(total)}</p>
        <h2 id="deal-title">${esc(item.product)}</h2>
        <p class="modal-sub">${item.account ? esc(item.account) : `<span class="is-missing">Conta pendente</span>`} · ${esc(item.agent)}</p>
        <div class="head-stats">
          <span><small>Valor potencial ${info(GLOSSARY.valorPotencial)}</small><strong>${fmt(item.price)}</strong></span>
          <span><small>Etapa</small><strong>${stageLabel(item.stage)}</strong></span>
          <span><small>Fase</small><strong>${esc(item.phase)}</strong></span>
        </div>
      </div>
      ${ringHtml(item)}
      <button class="icon-btn" type="button" data-close aria-label="Fechar">✕</button>
    </header>
    <div class="modal-body">
      <div class="detail-grid">
        <div>
          <section class="panel">
            <h3>O que fazer agora <span class="aside" id="action-count">${done.size}/${item.actions.length} feitas</span></h3>
            <div class="next-action">${esc(item.nextAction)}</div>
            <ul class="checklist">
              ${item.actions.map((a, i) => `<li><label><input type="checkbox" data-action="${i}"${done.has(i) ? " checked" : ""}><span>${esc(a)}</span></label></li>`).join("")}
            </ul>
          </section>
          <section class="panel">
            <h3>Por que está em “${esc(lane.title)}”</h3>
            <ul class="reasons">
              ${item.reasons.map((r) => `<li><div class="reason-head"><strong>${esc(r.label)}</strong><span>${esc(r.value)}</span></div><p>${esc(r.detail)}</p></li>`).join("")}
            </ul>
          </section>
        </div>
        <div>
          <section class="panel"><h3>Tempo de negociação</h3>${timelineHtml(item)}</section>
          <section class="panel"><h3>Empresa</h3>${accountPanel}</section>
          <section class="panel">
            <h3>Histórico de vendas</h3>
            ${item.account ? historyRow("Com esta empresa", accHistory) : ""}
            ${historyRow(`${esc(firstName(item.agent))} vendendo ${esc(item.product)}`, history.agentProduct[`${item.agent}|${item.product}`])}
            <dl class="facts compact-facts">
              <dt>Série do produto</dt><dd>${esc(products[item.product].series)}</dd>
              <dt>Manager · Regional</dt><dd>${esc(item.manager)} · ${esc(item.region)}</dd>
              ${item.engageDate ? `<dt>Início da negociação</dt><dd>${fmtDate(item.engageDate)}</dd>` : ""}
            </dl>
          </section>
        </div>
      </div>
    </div>
    <footer class="modal-foot">
      <span class="kbd-hint">Use ← → para passar de cartão</span>
      <button type="button" class="nav-btn" data-nav="-1"${position === 0 ? " disabled" : ""}>← Anterior</button>
      <button type="button" class="nav-btn" data-nav="1"${position >= total - 1 ? " disabled" : ""}>Próximo →</button>
    </footer>`;
}

function openDeal(laneId, index) {
  const list = byLane[laneId];
  if (!list || !list[index]) return;
  current = { lane: laneId, index };
  el.content.innerHTML = detailHtml(list[index], index, list.length);
  if (!el.modal.open) el.modal.showModal();
  el.content.querySelector(".modal-body").scrollTop = 0;
}

function exportPipeline() {
  const header = ["Coluna", "Fase", "Oportunidade", "Produto", "Valor potencial", "Dias em negociação",
    "Empresa", "Vendedor", "Manager", "Regional", "Próxima ação"];
  const rows = LANE_ORDER.flatMap((id) => byLane[id].map((i) => [LANE[id].title, i.phase, i.id, i.product, i.price,
    i.days ?? "", i.account || "Conta pendente", i.agent, i.manager, i.region, i.nextAction]));
  downloadCsv("lead-kanban-pipeline.csv", header, rows);
}

export function bindPipeline() {
  el.board.addEventListener("click", (e) => {
    const more = e.target.closest("[data-more]");
    if (more) {
      shown[more.dataset.more] = (shown[more.dataset.more] || PAGE) + PAGE;
      renderPipeline();
      return;
    }
    const card = e.target.closest(".card");
    if (card) openDeal(card.dataset.lane, Number(card.dataset.index));
  });
  el.guide.addEventListener("click", (e) => {
    if (e.target.closest("[data-guide-close]")) { writeStore(GUIDE_KEY, true); el.guide.hidden = true; }
    if (e.target.closest("[data-guide-help]")) document.getElementById("open-help").click();
    if (e.target.closest("[data-guide-video]")) openHelp({ play: true });
  });
  el.content.addEventListener("change", (e) => {
    const box = e.target.closest("[data-action]");
    if (!box || !current) return;
    const item = byLane[current.lane][current.index];
    const count = toggleDone(item, Number(box.dataset.action), box.checked);
    document.getElementById("action-count").textContent = `${count}/${item.actions.length} feitas`;
  });
  el.content.addEventListener("click", (e) => {
    const nav = e.target.closest("[data-nav]");
    if (nav && current) openDeal(current.lane, current.index + Number(nav.dataset.nav));
  });
  el.modal.addEventListener("keydown", (e) => {
    if (!current || (e.key !== "ArrowLeft" && e.key !== "ArrowRight")) return;
    e.preventDefault();
    openDeal(current.lane, current.index + (e.key === "ArrowRight" ? 1 : -1));
  });
  el.modal.addEventListener("close", () => { current = null; renderPipeline(); });
  document.getElementById("export-pipeline").addEventListener("click", exportPipeline);
}
