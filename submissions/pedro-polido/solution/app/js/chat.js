import { TriageModel, LANES } from './model.js';
import { decide, needsTranslation, QUEUE_PT } from './chat-policy.js';

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pct = (v) => `${Math.round(100 * v)}%`;
const hora = () => new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
const LANE_ICON = { auto: '🤖', assistido: '🤝', humano: '🧑', detalhes: '🤝' };

const model = new TriageModel(await (await fetch('data/model.json')).json());
let llm = { ok: false };
try {
  const r = await fetch('api/assist');
  if (r.ok) llm = await r.json();
} catch { /* sem função serverless: o chat segue só com o modelo local */ }
$('#llm-status').textContent = llm.ok
  ? `Gemini ativo (${llm.modelo}): tickets em português são traduzidos antes da triagem.`
  : 'Gemini indisponível neste ambiente: escreva em inglês; texto em português vai direto para uma pessoa.';

const SCENARIOS = [
  ['Senha expirada', 'Minha senha expirou e não consigo entrar no Outlook'],
  ['Pedido vago', 'não funciona, me ajuda'],
  ['Reembolso', 'Quero o reembolso, fui cobrado duas vezes pela licença'],
  ['Perda de dados', 'Apaguei sem querer a pasta do projeto, dá pra recuperar?'],
  ['Tema sensível', 'Estou de licença-maternidade a partir de dezembro, como fica meu apontamento de horas?'],
  ['Compra', 'Preciso de um pedido de compra para dois monitores e um teclado para o funcionário novo'],
  ['Em inglês', 'my laptop screen is flickering when I connect the docking station'],
];

let state;
function reset() {
  state = { proto: null, textos: [], stage: 'novo', last: null, busy: false };
  $('#messages').innerHTML = '';
  $('#events').innerHTML = '';
  $('#panel').innerHTML = '<div class="empty-state">Nenhum ticket ainda. Escreva no chat ou escolha um cenário.</div>';
  $('#actions').innerHTML = '';
  $('#panel-title').textContent = 'Painel do atendente';
  $('#panel-badge').innerHTML = '';
  addMsg('bot', 'Olá! Sou o assistente do suporte de TI. Conte o que está acontecendo.');
}

function addMsg(role, text, note) {
  const who = { cliente: 'Você (cliente)', bot: 'Assistente', atendente: 'Atendente' }[role];
  $('#messages').insertAdjacentHTML('beforeend', `
    <div class="msg ${role}">
      <div class="bubble">${esc(text).replace(/\n/g, '<br>')}</div>
      <div class="meta">${who} · ${hora()}${note ? ` · ${esc(note)}` : ''}</div>
    </div>`);
  $('#messages').scrollTop = $('#messages').scrollHeight;
}

function typing(on) {
  $('#messages .typing')?.remove();
  if (on) {
    $('#messages').insertAdjacentHTML('beforeend', '<div class="msg bot typing"><div class="bubble"><span></span><span></span><span></span></div></div>');
    $('#messages').scrollTop = $('#messages').scrollHeight;
  }
}

function logEvent(icon, text) {
  $('#events').insertAdjacentHTML('beforeend', `<li><span class="ev-icon">${icon}</span><span>${esc(text)}</span><span class="tiny muted">${hora()}</span></li>`);
}

async function callLLM(payload) {
  const r = await fetch('api/assist', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || `erro ${r.status}`);
  return j;
}

function renderPanel(d, original, english) {
  const { r } = d;
  $('#panel-title').textContent = `Ticket #${state.proto}`;
  $('#panel-badge').innerHTML = `<span class="badge lane-${d.lane}">${LANE_ICON[d.lane]} ${esc(LANES[d.lane].nome)}</span>`;
  const top3 = r.order.slice(0, 3);
  $('#panel').innerHTML = `
    <div class="small"><b>Decisão:</b> ${esc(LANES[d.lane].acao)}</div>
    <div class="small muted" style="margin-top:4px">${esc(d.motivo)}</div>
    ${d.riscos.length ? `<div class="flags">${d.riscos.map((x) => `<div class="flag on"><b>Regra de risco</b><span class="muted">${esc(x.motivo)}</span></div>`).join('')}</div>` : ''}
    <div class="proba" style="margin-top:14px">${top3.map((k) => `
      <div class="hbar"><span>${esc(QUEUE_PT[model.classes[k]])} <span class="tiny muted">(${esc(model.classes[k])})</span></span>
        <div class="track"><div class="fill" style="width:${100 * r.proba[k]}%;${k === r.order[0] ? '' : 'opacity:.35'}"></div></div>
        <span class="val">${pct(r.proba[k])}</span></div>`).join('')}
    </div>
    <div class="flags">
      ${r.flags.urgent ? '<div class="flag"><b>Sinal de urgência</b><span class="muted">sugere prioridade alta</span></div>' : ''}
      ${r.flags.selfService ? '<div class="flag"><b>Senha / bloqueio</b><span class="muted">link de autoatendimento</span></div>' : ''}
    </div>
    ${r.explicacao.favor.length ? `<div class="small" style="margin-top:12px"><b>Palavras que pesaram para ${esc(QUEUE_PT[r.top])}:</b></div>
      <div class="terms">${r.explicacao.favor.map((t) => `<span class="term">${esc(t.termo)}</span>`).join('')}</div>` : ''}
    <div class="analyzed">${english ? `<b>Tradução usada pelo classificador (Gemini):</b><br>${esc(english)}` : esc(original)}</div>`;
}

// Caixa de resposta do atendente, com rascunho opcional do Gemini (🤝: nada vai ao cliente sem o clique do atendente).
// once = some depois do envio (pedido de detalhes); senão fica aberta para outras respostas.
function replyBox(title, draftPayload, { initial = '', once = false, onSend }) {
  $('#actions').innerHTML = `
    <div class="llm-box">
      <div class="row" style="justify-content:space-between"><strong class="small">${esc(title)}</strong>
        <button class="btn ghost" id="act-draft" ${llm.ok ? '' : 'disabled title="Gemini indisponível neste ambiente"'}>Rascunho com Gemini</button></div>
      <textarea id="act-text" rows="4" style="min-height:96px;margin-top:8px" placeholder="Escreva a resposta ao cliente…">${esc(initial)}</textarea>
      <div class="row" style="margin-top:8px;justify-content:flex-end"><button class="btn" id="act-send">Aprovar e enviar</button></div>
    </div>`;
  $('#act-draft').onclick = async () => {
    const btn = $('#act-draft');
    btn.disabled = true;
    btn.textContent = 'Gerando…';
    try {
      const j = await callLLM(draftPayload);
      const perguntas = j.perguntas?.length ? `\n\n${j.perguntas.map((q) => `• ${q}`).join('\n')}` : '';
      $('#act-text').value = `${j.resposta_cliente}${perguntas}`;
      logEvent('🤝', 'Gemini redigiu um rascunho; aguardando revisão do atendente.');
    } catch (e) {
      logEvent('⚠️', `Falha ao gerar rascunho: ${e.message}`);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Rascunho com Gemini';
    }
  };
  $('#act-send').onclick = () => {
    const text = $('#act-text').value.trim();
    if (!text) return;
    onSend(text);
    if (once) $('#actions').innerHTML = '';
    else $('#act-text').value = '';
  };
}

const attendantReply = (text) => {
  addMsg('atendente', text, 'escrito ou aprovado pelo atendente');
  logEvent('🧑', 'Atendente respondeu ao cliente.');
};

async function onCustomer(text) {
  addMsg('cliente', text);
  if (['humano', 'encaminhado', 'assistido'].includes(state.stage)) {
    logEvent('🧑', 'Nova mensagem do cliente anexada ao ticket, para o atendente responsável.');
    return;
  }
  if (state.busy) {
    // Chegou outra mensagem enquanto a triagem roda: entra no texto do ticket e é considerada na próxima decisão
    state.textos.push(text);
    logEvent('🤖', 'Mensagem recebida durante a análise: juntada ao texto do ticket.');
    return;
  }
  state.busy = true;
  if (!state.proto) {
    state.proto = String(Math.floor(100000 + Math.random() * 900000));
    addMsg('bot', `Recebemos sua mensagem. Protocolo #${state.proto}. Já estou analisando e te respondo por aqui.`);
    logEvent('🤖', `Acuse de recebimento enviado na hora (protocolo #${state.proto}).`);
  }
  state.textos.push(text);
  const original = state.textos.join('\n');
  let english = null;
  if (needsTranslation(model, original)) {
    if (llm.ok) {
      typing(true);
      try {
        english = (await callLLM({ mode: 'translate', text: original })).traducao_en;
        logEvent('🤖', 'Texto traduzido para o inglês antes da triagem (o classificador foi treinado em inglês).');
      } catch (e) {
        logEvent('⚠️', `Falha na tradução (${e.message}): o ticket segue sem tradução.`);
      }
      typing(false);
    } else {
      logEvent('⚠️', 'Texto em outro idioma e sem Gemini neste ambiente: a regra de cobertura manda para uma pessoa.');
    }
  }
  const d = decide(model, original, english);
  state.last = { d, original, english };
  renderPanel(d, original, english);
  const fila = QUEUE_PT[d.r.top];
  const base = { text: original, fila: d.r.top, sensivel: d.r.flags.sensitive, vazio: d.vago, autoatendimento: d.r.flags.selfService };

  if (d.lane === 'auto') {
    state.stage = 'encaminhado';
    logEvent('🤖', `Roteado sozinho para ${fila} (${d.r.top}), confiança ${pct(d.r.conf)}.`);
    addMsg('bot', `Encaminhei seu pedido para a equipe de ${fila}. O protocolo continua #${state.proto}.`);
    if (d.r.flags.selfService) {
      addMsg('bot', 'Se for senha ou conta bloqueada, você já pode resolver agora pelo autoatendimento: [link do portal].');
      logEvent('🤖', 'Link de autoatendimento de senha enviado (regra).');
    }
    replyBox(`Resposta da equipe de ${fila} (opcional)`, { ...base, mode: 'draft', faixa: LANES.auto.nome }, { onSend: attendantReply });
  } else if (d.lane === 'assistido') {
    state.stage = 'assistido';
    addMsg('bot', 'Estou confirmando com a equipe qual área cuida do seu pedido. Já te aviso.');
    logEvent('🤝', `Confiança ${pct(d.r.conf)}: o atendente escolhe entre ${d.r.top} e ${d.r.second}.`);
    const [a, b] = d.r.order;
    $('#actions').innerHTML = `
      <div class="llm-box"><strong class="small">Qual fila? A IA sugere as duas primeiras:</strong>
        <div class="row" style="margin-top:8px">
          <button class="btn" data-q="${esc(model.classes[a])}">${esc(QUEUE_PT[model.classes[a]])} · ${pct(d.r.proba[a])}</button>
          <button class="btn ghost" data-q="${esc(model.classes[b])}">${esc(QUEUE_PT[model.classes[b]])} · ${pct(d.r.proba[b])}</button>
        </div></div>`;
    $('#actions').querySelectorAll('button[data-q]').forEach((btn) => {
      btn.onclick = () => {
        const q = btn.dataset.q;
        state.stage = 'encaminhado';
        logEvent('🤝', `Atendente confirmou a fila ${q}${q === d.r.top ? ' (1ª sugestão da IA)' : ' (2ª sugestão da IA)'}. Na operação, essa escolha vira rótulo de treino.`);
        addMsg('bot', `Pronto: seu pedido está com a equipe de ${QUEUE_PT[q]}. Protocolo #${state.proto}.`);
        replyBox(`Resposta da equipe de ${QUEUE_PT[q]} (opcional)`, { ...base, fila: q, mode: 'draft', faixa: LANES.assistido.nome }, { onSend: attendantReply });
      };
    });
  } else if (d.lane === 'humano') {
    state.stage = 'humano';
    logEvent('🧑', `Passado para uma pessoa. ${d.motivo}`);
    addMsg('bot', d.riscos.length
      ? 'Seu caso precisa da atenção de uma pessoa do time. Já transferi, e ela continua a conversa por aqui.'
      : 'Vou te passar para uma pessoa do time, para entender melhor o seu pedido. Ela continua a conversa por aqui.');
    replyBox('Responder como atendente', { ...base, mode: 'draft', faixa: LANES.humano.nome }, { onSend: attendantReply });
  } else {
    // Pedido vago: a IA redige o pedido de detalhes; o atendente aprova antes de enviar
    state.stage = 'detalhes';
    logEvent('🤝', 'Pedido vago: a IA prepara uma pergunta, e o atendente aprova antes de enviar.');
    let draft = 'Pode me contar um pouco mais? O que acontece, em qual equipamento ou sistema, e se aparece alguma mensagem de erro?';
    if (llm.ok) {
      typing(true);
      try {
        const j = await callLLM({ ...base, mode: 'draft', faixa: LANES.detalhes.nome, vazio: true });
        draft = `${j.resposta_cliente}${j.perguntas?.length ? `\n\n${j.perguntas.map((x) => `• ${x}`).join('\n')}` : ''}`;
        logEvent('🤝', 'Gemini redigiu o pedido de detalhes.');
      } catch (e) {
        logEvent('⚠️', `Gemini indisponível (${e.message}): usando o texto padrão.`);
      }
      typing(false);
    }
    replyBox('Pedido de detalhes (revise antes de enviar)', { ...base, mode: 'draft', faixa: LANES.detalhes.nome, vazio: true }, {
      initial: draft,
      once: true,
      onSend: (msg) => {
        addMsg('bot', msg, 'aprovado pelo atendente');
        logEvent('🤝', 'Pedido de detalhes aprovado e enviado. A próxima mensagem do cliente refaz a triagem com o texto completo.');
      },
    });
  }
  state.busy = false;
}

$('#composer').addEventListener('submit', (ev) => {
  ev.preventDefault();
  const text = $('#input').value.trim();
  if (!text) return;
  $('#input').value = '';
  $('#input').style.height = '44px';
  onCustomer(text);
});
// A caixa do cliente cresce com o texto até 120 px (o CSS limita)
$('#input').addEventListener('input', () => {
  const el = $('#input');
  el.style.height = '44px';
  if (el.scrollHeight > el.clientHeight) el.style.height = `${el.scrollHeight + 2}px`;
});
$('#input').addEventListener('keydown', (ev) => {
  if (ev.key === 'Enter' && !ev.shiftKey) {
    ev.preventDefault();
    $('#composer').requestSubmit();
  }
});
$('#scenarios').innerHTML = SCENARIOS.map(([label], i) => `<button class="chip" data-i="${i}">${esc(label)}</button>`).join('');
$('#scenarios').addEventListener('click', (ev) => {
  const b = ev.target.closest('.chip');
  if (!b) return;
  reset();
  onCustomer(SCENARIOS[Number(b.dataset.i)][1]);
});
$('#reset').addEventListener('click', reset);
reset();

// Link direto para um cenário: chat.html?cenario=1 abre a conversa já com o 1º cenário (numeração a partir de 1)
const pedido = Number(new URLSearchParams(location.search).get('cenario'));
if (Number.isInteger(pedido) && pedido >= 1 && pedido <= SCENARIOS.length) onCustomer(SCENARIOS[pedido - 1][1]);
