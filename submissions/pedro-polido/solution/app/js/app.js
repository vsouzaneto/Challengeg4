import { TriageModel, pct, LANES } from './model.js';
import { histogram, lineChart, groupedBars, dotsCI } from './charts.js';

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const int = (n) => Math.round(n).toLocaleString('pt-BR');
const dec = (n, d = 1) => n.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
const brl = (n) => (Math.abs(n) >= 1e6 ? `R$ ${dec(n / 1e6, 1)} mi` : Math.abs(n) >= 1e3 ? `R$ ${dec(n / 1e3, 1)} mil` : `R$ ${int(n)}`);
const bind = (k, v) => document.querySelectorAll(`[data-k="${k}"]`).forEach((el) => { el.textContent = v; });

async function load(name) {
  const r = await fetch(`data/${name}`);
  if (!r.ok) throw new Error(`falha ao carregar ${name}`);
  return r.json();
}

const [audit, diag, op, sim, modelData, examples, rev] = await Promise.all(
  ['audit.json', 'diagnostico.json', 'operacao.json', 'simulador.json', 'model.json', 'exemplos.json', 'revisao.json'].map(load),
);
const model = new TriageModel(modelData);
const classes = sim.classes;
const FLAG = sim.flag_bits;

// ---------------------------------------------------------------------------------------------- simulação
function simulate({ tau, sens = true, empty = true }) {
  const lanes = { auto: 0, assistido: 0, humano: 0, detalhes: 0 };
  let autoOk = 0; let assistTop2 = 0;
  const perQueue = classes.map(() => ({ n: 0, ok: 0 }));
  for (let i = 0; i < sim.y.length; i += 1) {
    const conf = sim.conf[i] / 1000;
    const f = sim.flags[i];
    let lane;
    if (empty && (f & FLAG.info_poor)) lane = 'detalhes';
    else if (f & FLAG.ood) lane = 'humano';
    else if (sens && (f & FLAG.sensitive)) lane = 'humano';
    else if (conf >= tau) lane = 'auto';
    else if (conf >= sim.limiar_assistido) lane = 'assistido';
    else lane = 'humano';
    lanes[lane] += 1;
    const ok = sim.pred[i] === sim.y[i];
    if (lane === 'auto') {
      autoOk += ok;
      perQueue[sim.pred[i]].n += 1;
      perQueue[sim.pred[i]].ok += ok;
    } else if (lane === 'assistido') assistTop2 += ok || sim.second[i] === sim.y[i];
  }
  const n = sim.y.length;
  const share = Object.fromEntries(Object.entries(lanes).map(([k, v]) => [k, v / n]));
  return {
    share, lanes, perQueue,
    accAuto: lanes.auto ? autoOk / lanes.auto : 1,
    top2Assist: lanes.assistido ? assistTop2 / lanes.assistido : 1,
  };
}

const base = simulate({ tau: sim.limiar_auto });

// ---------------------------------------------------------------------------------------------- resumo
const confusion = op.confusao;
const errorsInto = classes.map((_, j) => confusion.reduce((s, row, i) => s + (i === j ? 0 : row[j]), 0));
const totalErrors = errorsInto.reduce((a, b) => a + b, 0);
const hw = classes.indexOf('Hardware');
const hwVolume = op.filas[hw].volume / op.total;
const emptyTotal = Object.values(op.vazio_rotulos).reduce((a, b) => a + b, 0);
const threadTop = [...op.filas].sort((a, b) => b.cadeia - a.cadeia);

bind('d2_total', int(op.total));
bind('neg_pct', pct(audit.negativos, 1));
bind('auto_share', pct(base.share.auto));
bind('auto_acc', pct(base.accAuto, 1));
bind('assist_share', pct(base.share.assistido));
bind('human_share', pct(base.share.humano + base.share.detalhes));
bind('test_n', int(sim.y.length));
bind('seg_tested', int(diag.segmentos_testados));
bind('seg_flags', String(diag.real.gargalos_tempo + diag.real.gargalos_csat));
bind('false_alarm', pct(diag.rodadas_com_alarme));
bind('closed_n', int(audit.fechados));
bind('thread', pct(op.cadeia_total, 1));
bind('thread_note', `O pedido chega no meio de uma conversa e alguém precisa garimpar o que se quer. É ${pct(threadTop[0].cadeia)} em ${threadTop[0].fila} e ${pct(threadTop.at(-1).cadeia)} em ${threadTop.at(-1).fila}. O modelo acerta igual com uma ou com várias mensagens, então ler a cadeia deixa de ser trabalho humano.`);
bind('sink', pct(errorsInto[hw] / totalErrors));
bind('sink_note', `Hardware recebe ${pct(hwVolume)} do volume, mas ${pct(errorsInto[hw] / totalErrors)} dos tickets mal roteados. Na operação, é a fila que mais perde tempo com o que não é dela.`);
bind('empty_hr', pct(op.vazio_rotulos['HR Support'] / emptyTotal));
bind('empty_note', `Tickets como "${op.vazio_exemplos[0]}" não dizem o que querem, mas foram rotulados como RH. O modelo aprendeu esse vício e "acerta" quase todos. Na política, pedido vazio nunca é roteado: recebe um pedido de detalhes.`);

// ---------------------------------------------------------------------------------------------- 1. auditoria
$('#checks').innerHTML = audit.checks.map((c) => `
  <div class="check ${c.peso === 'medio' ? 'medio' : ''}">
    <div class="v num">${esc(c.valor)}</div>
    <h3>${esc(c.titulo)}</h3>
    <p>${esc(c.evidencia)}</p>
  </div>`).join('');

histogram($('#chart-ttr'), {
  counts: audit.ttr_hist.counts,
  edges: audit.ttr_hist.edges,
  color: (lo) => (lo < 0 ? 'var(--bad)' : 'var(--faint)'),
  xFmt: (v) => `${v > 0 ? '+' : ''}${v} h`,
  annotate: { x: 'left', text: `${pct(audit.negativos, 1)} "resolvidos antes de responder"`, color: 'var(--bad)' },
});
$('#ttr-note').textContent = `Um tempo real de atendimento nunca é negativo e tem cauda longa à direita. Aqui é um triângulo simétrico em torno de zero (desvio de ${dec(audit.ttr_desvio_h, 1)} h, curtose de ${dec(audit.ttr_curtose, 1)}): a assinatura da diferença entre dois horários sorteados de forma independente (teórico: 9,8 h e −0,6).`;

dotsCI($('#chart-csat'), {
  items: audit.csat.por_canal.map((r) => ({ label: r['Ticket Channel'], mean: r.mean, ci: r.ci95 })),
  x: { min: 2.6, max: 3.4, ticks: [2.6, 2.8, 3.0, 3.2, 3.4] },
  fmt: (v) => dec(v, 1),
});
$('#csat-note').textContent = `As notas médias ficam todas em torno de 3, com intervalos sobrepostos. Com ${int(audit.fechados)} tickets fechados, uma diferença de ${dec(audit.csat.mde_canal, 2)} ponto entre canais seria detectada, e não há nenhuma. Um modelo com todas as variáveis prevê a nota com ${pct(audit.csat.modelo, 1)} de acerto, o mesmo que chutar a nota mais comum (${pct(audit.csat.classe_mais_comum, 1)}).`;

$('#naive').innerHTML = audit.ingenuo.map((n) => `
  <div class="naive-item">
    <div class="claim"><span class="label">Análise ingênua</span><s>${esc(n.afirmacao)}</s></div>
    <div class="truth"><span class="label">Teste</span>${esc(n.teste)}</div>
  </div>`).join('');

const powerColors = ['var(--accent)', 'var(--auto)', 'var(--assist)'];
const targets = [...new Set(diag.poder.map((p) => p.alvo))];
lineChart($('#chart-power'), {
  series: targets.map((t, i) => ({
    label: t, color: powerColors[i], dots: true,
    points: diag.poder.filter((p) => p.alvo === t).map((p) => [p.efeito_h, p.deteccao]),
  })),
  x: { min: 0, max: 12.5, ticks: [1, 2, 3, 4, 6, 8, 12], fmt: (v) => `+${v}h` },
  y: { min: 0, max: 1, ticks: [0, 0.5, 1], fmt: (v) => pct(v) },
  xLabel: 'tamanho do gargalo injetado',
  height: 230,
});
$('#legend-power').innerHTML = targets.map((t, i) => `<span><i style="background:${powerColors[i]}"></i>${esc(t)}</span>`).join('');

// ---------------------------------------------------------------------------------------------- 2. operação
const maxVol = Math.max(...op.filas.map((f) => f.volume));
$('#queues').innerHTML = [...op.filas].sort((a, b) => b.volume - a.volume).map((f) => `
  <div class="queue-row">
    <div>
      <div class="queue-name">${esc(f.fila)}</div>
      <div class="queue-desc">${esc(f.descricao)}</div>
    </div>
    <div>
      <div class="hbar" style="grid-template-columns:1fr 150px">
        <div class="track"><div class="fill" style="width:${(100 * f.volume) / maxVol}%"></div></div>
        <div class="val small">${int(f.volume)} · ${pct(f.volume / op.total)} · F1 ${dec(f.f1, 2)}</div>
      </div>
      <div>${f.termos.slice(0, 8).map((t) => `<span class="pill">${esc(t)}</span>`).join('')}
        <span class="pill" title="tickets que chegam como cadeia de e-mails">cadeia ${pct(f.cadeia)}</span></div>
    </div>
  </div>`).join('');

const bandPos = (t) => (t - 0.2) / 0.1;
groupedBars($('#chart-local'), {
  groups: op.acerto_local.map((b) => b.faixa.replace('.', ',').replace('.', ',')),
  series: [
    { label: 'acerta a fila', color: 'var(--accent)', values: op.acerto_local.map((b) => b.top1) },
    { label: 'fila certa entre as 2 primeiras', color: 'color-mix(in srgb, var(--accent) 35%, transparent)', values: op.acerto_local.map((b) => b.top2) },
  ],
  y: { min: 0, max: 1, ticks: [0, 0.5, 1], fmt: (v) => pct(v) },
  width: 1000,
  height: 290,
  bands: [
    { from: 0, to: bandPos(sim.limiar_assistido), color: 'var(--human)', label: 'humano' },
    { from: bandPos(sim.limiar_assistido), to: bandPos(sim.limiar_auto), color: 'var(--assist)', label: 'assistido' },
    { from: bandPos(sim.limiar_auto), to: op.acerto_local.length, color: 'var(--auto)', label: 'auto' },
  ],
});
const lowIdx = sim.conf.map((c, i) => i).filter((i) => sim.conf[i] / 1000 < sim.limiar_assistido && !(sim.flags[i] & (FLAG.sensitive | FLAG.info_poor | FLAG.ood)));
const lowTop1 = lowIdx.filter((i) => sim.pred[i] === sim.y[i]).length / lowIdx.length;
const lowShare = lowIdx.length / sim.y.length;
$('#local-note').textContent = `Os limiares foram escolhidos em validação cruzada no treino e só depois medidos no teste. Abaixo de ${pct(sim.limiar_assistido)} de confiança, a 1ª sugestão acerta ${pct(lowTop1)}: esses tickets vão para uma pessoa. A partir de ${pct(sim.limiar_auto, 1)}, o acerto passa de ${pct(sim.meta_auto)} e o ticket pode ser roteado sozinho.`;

// ---------------------------------------------------------------------------------------------- 3. simulador
const LANE_ORDER = ['auto', 'assistido', 'humano', 'detalhes'];
const inputs = ['vol', 'cost', 'manual', 'assist', 'rework'].reduce((o, k) => ({ ...o, [k]: $(`#p-${k}`) }), {});
const tauEl = $('#tau');
tauEl.value = sim.limiar_auto;

const curveCache = new Map();
function curve(sens, empty) {
  const key = `${sens}-${empty}`;
  if (!curveCache.has(key)) {
    const pts = [];
    for (let t = 0.5; t <= 0.99 + 1e-9; t += 0.01) {
      const r = simulate({ tau: t, sens, empty });
      pts.push([t, r.share.auto, r.lanes.auto ? r.accAuto : null]);
    }
    curveCache.set(key, pts);
  }
  return curveCache.get(key);
}

function renderSim() {
  const tau = parseFloat(tauEl.value);
  const sens = $('#t-sens').checked;
  const empty = $('#t-empty').checked;
  const p = Object.fromEntries(Object.entries(inputs).map(([k, el]) => [k, Math.max(0, parseFloat(el.value) || 0)]));
  const r = simulate({ tau, sens, empty });

  $('#tau-v').textContent = pct(tau, 1);
  $('#tau-hint').textContent = Math.abs(tau - sim.limiar_auto) < 0.003
    ? `Limiar escolhido pelos dados: o menor com ≥ ${pct(sim.meta_auto)} de acerto na validação cruzada.`
    : tau < sim.limiar_assistido
      ? 'Abaixo do limiar da faixa assistida: tudo que não é sensível nem vazio é roteado sozinho.'
      : `O limiar escolhido pelos dados é ${pct(sim.limiar_auto, 1)}.`;

  $('#sim-bar').innerHTML = LANE_ORDER.map((k) => `<div class="lane-${k}" style="flex-basis:${100 * r.share[k]}%" title="${LANES[k].nome}: ${pct(r.share[k], 1)}">${r.share[k] > 0.06 ? pct(r.share[k]) : ''}</div>`).join('');
  const perMonth = (s) => int(s * p.vol);
  const detail = {
    auto: `${pct(r.accAuto, 1)} de acerto`,
    assistido: `fila certa entre as 2 sugestões em ${pct(r.top2Assist, 1)}`,
    humano: sens ? 'baixa confiança ou tema sensível' : 'baixa confiança',
    detalhes: 'resposta automática pede o que falta',
  };
  $('#sim-lanes').innerHTML = LANE_ORDER.map((k) => `
    <div class="lane-card lane-${k}">
      <div class="t">${LANES[k].nome}</div>
      <div class="v num">${pct(r.share[k], 1)}</div>
      <div class="d">${perMonth(r.share[k])} tickets/mês · ${detail[k]}</div>
    </div>`).join('');

  // Horas: hoje, toda triagem é manual. Com IA: assistida custa menos, humana/detalhes custam o mesmo,
  // automática custa zero, mas cada erro automático gera retrabalho.
  const today = (p.vol * p.manual) / 60;
  const errors = p.vol * r.share.auto * (1 - r.accAuto);
  const withAI = (p.vol * (r.share.assistido * p.assist + (r.share.humano + r.share.detalhes) * p.manual)) / 60 + (errors * p.rework) / 60;
  const saved = today - withAI;
  $('#sim-kpis').innerHTML = `
    <div class="kpi ${saved >= 0 ? 'good' : 'bad'}"><div class="kpi-label">Horas de triagem liberadas</div><div class="kpi-value num">${int(saved)} h</div><div class="kpi-sub">por mês, de ${int(today)} h hoje</div></div>
    <div class="kpi ${saved >= 0 ? 'good' : 'bad'}"><div class="kpi-label">Economia por ano</div><div class="kpi-value num">${brl(saved * 12 * p.cost)}</div><div class="kpi-sub">custo da hora × horas liberadas</div></div>
    <div class="kpi"><div class="kpi-label">Erros do roteamento automático</div><div class="kpi-value num">${int(errors)}</div><div class="kpi-sub">tickets/mês na fila errada</div></div>
    <div class="kpi"><div class="kpi-label">Equivale a</div><div class="kpi-value num">${dec(saved / 160, 1)}</div><div class="kpi-sub">atendente(s) em tempo integral (160 h/mês)</div></div>`;

  const pts = curve(sens, empty);
  lineChart($('#chart-curve'), {
    series: [
      { label: 'cobertura', color: 'var(--accent)', points: pts.map((q) => [q[0], q[1]]) },
      { label: 'acerto', color: 'var(--auto)', points: pts.map((q) => [q[0], q[2]]) },
    ],
    x: { min: 0.5, max: 0.99, ticks: [0.5, 0.6, 0.7, 0.8, 0.9, 0.99], fmt: (v) => pct(v) },
    y: { min: 0, max: 1, ticks: [0, 0.25, 0.5, 0.75, 1], fmt: (v) => pct(v) },
    marker: { x: tau, points: [{ y: r.accAuto, color: 'var(--auto)', label: pct(r.accAuto, 1) }, { y: r.share.auto, color: 'var(--accent)', label: pct(r.share.auto, 1) }] },
    xLabel: 'confiança mínima para rotear sozinho',
    width: 760,
    height: 290,
  });

  const rows = r.perQueue.map((q, k) => ({ fila: classes[k], ...q })).sort((a, b) => b.n - a.n);
  const scale = p.vol / sim.y.length;
  $('#sim-table').innerHTML = `<thead><tr><th>Fila de destino</th><th class="n">Roteados sozinhos/mês</th><th class="n">Acerto</th><th class="n">Na fila errada/mês</th></tr></thead><tbody>${
    rows.map((q) => `<tr><td>${esc(q.fila)}</td><td class="n">${int(q.n * scale)}</td><td class="n">${q.n ? pct(q.ok / q.n, 1) : '–'}</td><td class="n">${int((q.n - q.ok) * scale)}</td></tr>`).join('')}</tbody>`;
}
[tauEl, $('#t-sens'), $('#t-empty'), ...Object.values(inputs)].forEach((el) => el.addEventListener('input', renderSim));
renderSim();

// ---------------------------------------------------------------------------------------------- 4. triagem ao vivo
const ticketEl = $('#ticket');
const resultEl = $('#result');
const bannerEl = $('#pt-banner');
const PT_WORDS = /\b(não|nao|está|estou|meu|minha|preciso|consigo|acessar|acesso|senha|computador|tela|problema|ajuda|olá|ola|obrigad[oa]|bom dia|boa tarde|por favor|você|voce|funciona|conta|pedido|férias|ferias|licença|licenca|impressora|notebook novo)\b/gi;
let llm = { ok: false };
let translated = null; // { original, en } quando o texto veio do Gemini
let lastPrediction = null;

fetch('api/assist').then((r) => (r.ok ? r.json() : { ok: false })).then((j) => { llm = j; render(); }).catch(() => {});

$('#examples').innerHTML = examples.map((e, i) => `<button class="chip" data-i="${i}">${esc(e.titulo)}</button>`).join('');
$('#examples').addEventListener('click', (ev) => {
  const b = ev.target.closest('.chip');
  if (!b) return;
  const ex = examples[+b.dataset.i];
  ticketEl.value = ex.texto;
  ticketEl.dataset.rotulo = ex.rotulo;
  translated = null;
  render();
});

// ?exemplo=N abre a página já com um exemplo carregado (útil para compartilhar um caso)
const initial = examples[Number(new URLSearchParams(location.search).get('exemplo'))];
if (initial) {
  ticketEl.value = initial.texto;
  ticketEl.dataset.rotulo = initial.rotulo;
  render();
}

let timer;
ticketEl.addEventListener('input', () => {
  delete ticketEl.dataset.rotulo;
  translated = null;
  clearTimeout(timer);
  timer = setTimeout(render, 120);
});

function highlight(text, favor, contra) {
  const f = new Set(favor.map((t) => t.termo));
  const c = new Set(contra.map((t) => t.termo));
  let out = '';
  let last = 0;
  for (const m of text.matchAll(/[\p{L}\p{N}_]{2,}/gu)) {
    const tok = m[0].toLowerCase();
    out += esc(text.slice(last, m.index));
    out += f.has(tok) ? `<mark>${esc(m[0])}</mark>` : c.has(tok) ? `<mark class="contra">${esc(m[0])}</mark>` : esc(m[0]);
    last = m.index + m[0].length;
  }
  return out + esc(text.slice(last));
}

function render() {
  const original = ticketEl.value.trim();
  if (!original) {
    resultEl.innerHTML = '<div class="empty-state">Escreva ou escolha um exemplo para ver a triagem.</div>';
    bannerEl.hidden = true;
    return;
  }
  const text = translated?.original === original ? translated.en : original;
  const r = model.predict(text);
  const known = r.cobertura.tokens ? r.cobertura.conhecidos / r.cobertura.tokens : 0;
  const looksPt = !translated && (original.match(PT_WORDS) || []).length >= 2;

  bannerEl.hidden = !looksPt;
  if (looksPt) {
    bannerEl.innerHTML = `Parece português. O classificador foi treinado com tickets em inglês e reconhece ${r.cobertura.conhecidos} de ${r.cobertura.tokens} palavras deste texto.
      ${llm.ok ? '<button class="btn" id="btn-translate" style="margin-left:6px">Traduzir com Gemini e classificar</button>' : '<br><span class="muted">O Gemini não está configurado neste ambiente: escreva em inglês ou use um exemplo.</span>'}`;
  }

  const lane = r.lane;
  const top3 = r.order.slice(0, 3);
  const rotulo = ticketEl.dataset.rotulo;
  resultEl.innerHTML = `
    <div class="result-head">
      <span class="badge lane-${lane.id}">${esc(lane.nome)}</span>
      <span class="small muted">confiança <strong class="num" style="color:var(--text)">${pct(r.conf, 1)}</strong></span>
    </div>
    <div class="queue-big">${esc(r.top)}</div>
    <div class="small muted">${esc(model.queueInfo[r.top])}</div>
    ${rotulo ? `<div class="small" style="margin-top:6px">Rótulo no dataset: <strong>${esc(rotulo)}</strong> ${rotulo === r.top ? '✓' : '· o modelo discorda'}</div>` : ''}
    <p class="small" style="margin-top:12px"><strong>${esc(lane.acao)}</strong> ${esc(lane.motivo)}</p>
    ${translated?.original === original ? `<div class="banner">Classificado a partir da tradução do Gemini: <em>${esc(translated.en)}</em></div>` : ''}
    <div class="proba">${top3.map((k) => `
      <div class="hbar"><span>${esc(classes[k])}</span><div class="track"><div class="fill" style="width:${100 * r.proba[k]}%;${k === r.order[0] ? '' : 'opacity:.35'}"></div></div><span class="val">${pct(r.proba[k])}</span></div>`).join('')}
    </div>
    <div class="why">
      <div class="small"><strong>Por que ${esc(r.top)} e não ${esc(r.second)}</strong></div>
      <div class="terms">${r.explicacao.favor.map((t) => `<span class="term">${esc(t.termo)}</span>`).join('') || '<span class="small muted">nenhuma palavra conhecida pesou a favor</span>'}
        ${r.explicacao.contra.map((t) => `<span class="term contra" title="puxa para ${esc(r.second)}">${esc(t.termo)}</span>`).join('')}</div>
      <div class="analyzed">${highlight(text, r.explicacao.favor, r.explicacao.contra)}</div>
      <div class="tiny muted" style="margin-top:6px">Em verde, palavras que puxam para ${esc(r.top)}; em amarelo, para ${esc(r.second)}. O modelo reconhece ${r.cobertura.conhecidos} de ${r.cobertura.tokens} palavras (${pct(known)}).</div>
    </div>
    <div class="flags">
      ${flag(r.flags.sensitive, 'Tema sensível', 'saúde, remuneração ou desligamento')}
      ${flag(r.flags.urgent, 'Sinal de urgência', 'sugere prioridade alta')}
      ${flag(r.flags.selfService, 'Senha / bloqueio', 'enviar link de autoatendimento')}
      ${flag(r.flags.messages > 1, `${r.flags.messages} mensagens`, 'cadeia de e-mails')}
    </div>
    <div class="llm-box">
      <div class="row" style="justify-content:space-between">
        <strong class="small">Rascunho de resposta (Gemini)</strong>
        <button class="btn ghost" id="btn-draft" ${llm.ok ? '' : 'disabled title="Gemini não configurado neste ambiente"'}>Gerar rascunho</button>
      </div>
      <div id="draft" class="small muted" style="margin-top:6px">${llm.ok ? 'O atendente revisa antes de enviar. Nada é enviado automaticamente.' : 'Indisponível neste ambiente: a função serverless precisa da variável GEMINI_API_KEY.'}</div>
    </div>`;
  lastPrediction = { r, text };
}
function flag(on, title, sub) {
  return on ? `<div class="flag on"><b>${esc(title)}</b><span class="muted">${esc(sub)}</span></div>` : '';
}

async function callLLM(payload) {
  const r = await fetch('api/assist', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || `erro ${r.status}`);
  return j;
}

document.addEventListener('click', async (ev) => {
  if (ev.target.id === 'btn-translate') {
    const original = ticketEl.value.trim();
    ev.target.disabled = true;
    ev.target.textContent = 'Traduzindo…';
    try {
      const j = await callLLM({ mode: 'translate', text: original });
      translated = { original, en: j.traducao_en };
      render();
    } catch (e) {
      bannerEl.insertAdjacentHTML('beforeend', `<div class="muted">Falha na tradução: ${esc(e.message)}</div>`);
    }
  }
  if (ev.target.id === 'btn-draft' && lastPrediction) {
    const out = $('#draft');
    const { r, text } = lastPrediction;
    ev.target.disabled = true;
    out.textContent = 'Gerando…';
    try {
      const j = await callLLM({
        mode: 'draft', text: translated?.original ?? text, fila: r.top, faixa: r.lane.nome,
        sensivel: r.flags.sensitive, vazio: r.flags.infoPoor, autoatendimento: r.flags.selfService,
      });
      out.classList.remove('muted');
      out.innerHTML = `
        <div><strong>Resumo para o atendente:</strong> ${esc(j.resumo_interno)}</div>
        <pre>${esc(j.resposta_cliente)}</pre>
        ${j.perguntas?.length ? `<div style="margin-top:6px"><strong>Perguntar ao solicitante:</strong><ul class="clean">${j.perguntas.map((q) => `<li>${esc(q)}</li>`).join('')}</ul></div>` : ''}
        <div class="tiny muted" style="margin-top:6px">${esc(j.modelo)} · ${int(j.tokens)} tokens · rascunho, não enviado</div>`;
    } catch (e) {
      out.textContent = `Falha ao gerar: ${e.message}`;
    } finally {
      ev.target.disabled = false;
    }
  }
});

// ---------------------------------------------------------------------------------------------- 5. na prática
$('#lanes-explained').innerHTML = LANE_ORDER.map((k) => `
  <div class="lane-card lane-${k}">
    <div class="t">${LANES[k].nome}</div>
    <div class="v num">${pct(base.share[k], 1)}</div>
    <div class="d">${esc(LANES[k].acao)}</div>
  </div>`).join('');

const sens = op.filas.reduce((s, f) => s + f.sensivel * f.volume, 0) / op.total;
const prec = Object.fromEntries(op.filas.map((f) => [f.fila, f.precisao]));
$('#not-automate').innerHTML = [
  `<strong>Temas sensíveis (${pct(sens, 1)} dos tickets):</strong> licença-maternidade, salário, desligamento, acidente. É dado pessoal sensível (LGPD) e pede empatia. O filtro prefere errar para o lado humano: "salary module" também cai aqui, e esse erro é barato.`,
  `<strong>Confiança abaixo de ${pct(sim.limiar_assistido)} (${pct(lowShare, 1)} dos tickets):</strong> a 1ª sugestão acerta ${pct(lowTop1)}. Rotear sozinho seria errar quase metade.`,
  `<strong>Conceder acesso ou direito de administrador:</strong> a IA identifica e roteia (precisão de ${pct(prec.Access)} em Access e ${pct(prec['Administrative rights'])} em Administrative rights), mas a concessão é decisão humana com aprovação.`,
  '<strong>Pedidos vazios:</strong> nenhum modelo acerta o que não foi dito. Uma resposta automática pede o que falta, e a triagem vem depois.',
  `<strong>Reclamação, cancelamento e reembolso:</strong> envolvem retenção e dinheiro. A IA redige, a pessoa envia. No CSV, pelo rótulo, reembolso é ${pct(rev.nao_automatizar.categorias[0].pct, 1)} e cancelamento ${pct(rev.nao_automatizar.categorias[1].pct, 1)} dos tickets (<a href="revisao.html#e22">revisão, 2.2</a>); como o texto não confirma o rótulo, a regra é de política.`,
].map((li) => `<li>${li}</li>`).join('');

// Benchmark LLM × linear (só aparece se o pipeline 04 tiver rodado)
const PROMPT_LABEL = { nomes: 'só os nomes das filas', descricoes: 'nomes + descrições das filas', exemplos: 'descrições + 24 exemplos' };
fetch('data/llm_benchmark.json').then((r) => (r.ok ? r.json() : null)).then((b) => {
  if (!b) return;
  const pv = (p) => (p < 0.001 ? '< 0,001' : `= ${dec(p, 3)}`);
  const rows = [
    { label: 'Classificador linear (este app)', acerto: b.linear.acerto, sub: 'custo zero por ticket, milissegundos', color: 'var(--auto)' },
    ...b.rodadas.map((r) => ({
      label: `${r.modelo} · ${PROMPT_LABEL[r.prompt]}`,
      acerto: r.acerto,
      sub: `${int(r.tokens_por_ticket)} tokens/ticket · diferença para o linear: McNemar p ${pv(r.p_mcnemar)}`,
      color: 'var(--accent)',
    })),
  ];
  const el = $('#llm-bench');
  el.innerHTML = `<div class="small"><strong>Medido: Gemini × classificador linear nos mesmos ${int(b.n)} tickets de teste</strong></div>
    <div class="proba">${rows.map((r) => `
      <div class="hbar" style="grid-template-columns:1fr 54px"><div><div class="tiny">${esc(r.label)}</div>
        <div class="track"><div class="fill" style="width:${100 * r.acerto}%;background:${r.color}"></div></div>
        <div class="tiny muted">${esc(r.sub)}</div></div><span class="val">${pct(r.acerto, 1)}</span></div>`).join('')}
    </div>
    ${b.modelos_indisponiveis?.length ? `<div class="tiny muted" style="margin-top:8px">Indisponíveis no momento do teste (503/429): ${esc(b.modelos_indisponiveis.join(', '))}.</div>` : ''}`;
  el.hidden = false;
}).catch(() => {});

// Navegação: destaca a seção visível
const links = [...document.querySelectorAll('.nav-links a')];
const observer = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) links.forEach((a) => a.classList.toggle('active', a.getAttribute('href') === `#${e.target.id}`));
  });
}, { rootMargin: '-45% 0px -50% 0px' });
document.querySelectorAll('main section').forEach((s) => observer.observe(s));
