import React from 'https://esm.sh/react@18.3.1';
import { createRoot } from 'https://esm.sh/react-dom@18.3.1/client';
import { Bar } from 'https://esm.sh/@visx/shape@4.0.0?deps=react@18.3.1';
import { scaleBand, scaleLinear } from 'https://esm.sh/@visx/scale@4.0.0';
import { Group } from 'https://esm.sh/@visx/group@4.0.0?deps=react@18.3.1';

const e = React.createElement;
const { useState, useEffect } = React;

const orange = '#ff5c1a', muted = '#77756f', gridColor = '#29292c';

const CHANNEL_PT = { 'Social media': 'Redes sociais', Chat: 'Chat', Email: 'E-mail', Phone: 'Telefone' };
const TYPE_PT = { 'Refund request': 'Reembolso', 'Cancellation request': 'Cancelamento', 'Product inquiry': 'Produto', 'Billing inquiry': 'Cobrança', 'Technical issue': 'Técnico' };
const CAT_ORDER = ['Hardware', 'HR Support', 'Access', 'Miscellaneous', 'Storage', 'Purchase', 'Internal Project', 'Administrative rights'];
const CHANNEL_ORDER = ['Social media', 'Chat', 'Email', 'Phone'];

const fmt = (n, d = 1) => Number(n).toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (n, d = 1) => fmt(n * 100, d) + '%';

const OPERATION_FIELDS = [
  ['Ticket ID', 'Identificador do chamado. Cada linha representa um ticket.'],
  ['Customer Name', 'Nome do cliente. Dado pessoal; não é exibido nos gráficos.'],
  ['Customer Email', 'E-mail do cliente. Dado pessoal; não é exibido nos gráficos.'],
  ['Customer Age', 'Idade do cliente; avaliada na análise exploratória de satisfação.'],
  ['Customer Gender', 'Gênero cadastrado do cliente.'],
  ['Product Purchased', 'Produto comprado relacionado ao atendimento.'],
  ['Date of Purchase', 'Data da compra; não é a data de abertura do chamado.'],
  ['Ticket Type', 'Tipo do pedido: problema técnico, cobrança, produto, reembolso ou cancelamento.'],
  ['Ticket Subject', 'Assunto resumido do chamado.'],
  ['Ticket Description', 'Texto com o relato do problema ou pedido do cliente.'],
  ['Ticket Status', 'Situação: aberto, fechado ou aguardando resposta do cliente.'],
  ['Resolution', 'Texto da solução registrada pelo agente; pode estar vazio.'],
  ['Ticket Priority', 'Prioridade atribuída: baixa, média, alta ou crítica.'],
  ['Ticket Channel', 'Canal de entrada: e-mail, chat, telefone ou redes sociais.'],
  ['First Response Time', 'Data e hora registradas para a primeira resposta. Não é uma duração.'],
  ['Time to Resolution', 'Data e hora registradas para a resolução. Subtraímos a primeira resposta para calcular o intervalo analisado.'],
  ['Customer Satisfaction Rating', 'Nota de satisfação do cliente (CSAT), de 1 a 5; pode estar vazia.'],
];
const TRAINING_FIELDS = [
  ['Document', 'Texto do ticket já processado. É a entrada usada para treinar e testar o classificador.'],
  ['Topic_group', 'Categoria conhecida do texto. É a resposta de referência usada para ensinar o modelo e avaliar seus acertos.'],
];

function DatasetFields({ fields, missing, purpose }) {
  return e('div', { className: 'dataset-fields' },
    e('h4', null, `O que está armazenado: ${fields.length} colunas`),
    e('dl', null, fields.map(([name, description]) =>
      e('div', { className: 'dataset-field', key: name },
        e('dt', null, name), e('dd', null, description)))),
    e('p', { className: 'dataset-note' }, e('strong', null, 'O que não contém: '), missing),
    e('p', { className: 'dataset-note' }, e('strong', null, 'Uso nesta solução: '), purpose));
}

// ---------------------------------------------------------------- BarChart (visx)
function BarChart({ data, label, value, max = 20, suffix = 'h', color = orange }) {
  const w = 560, h = 250, m = { t: 10, r: 15, b: 45, l: 32 };
  const x = scaleBand({ domain: data.map((d) => d[0]), range: [m.l, w - m.r], padding: 0.38 });
  const y = scaleLinear({ domain: [0, max], range: [h - m.b, m.t], nice: true });
  return e(
    'svg',
    { viewBox: `0 0 ${w} ${h}`, className: 'chart', role: 'img', 'aria-label': label },
    [0, 5, 10, 15, 20].map((v) =>
      e(
        'g',
        { key: v },
        e('line', { x1: m.l, x2: w - m.r, y1: y(v), y2: y(v), stroke: gridColor }),
        e('text', { x: '0', y: y(v) + 4, fill: muted, fontSize: '10', fontFamily: 'DM Mono' }, v)
      )
    ),
    e(
      Group,
      null,
      data.map((d) => {
        const v = value(d), bx = x(d[0]);
        return e(
          'g',
          { key: d[0] },
          e(Bar, { x: bx, y: y(v), width: x.bandwidth(), height: y(0) - y(v), fill: color, rx: 2 }),
          e('text', { x: bx + x.bandwidth() / 2, y: y(v) - 7, textAnchor: 'middle', fill: '#f1f0ed', fontSize: '11', fontFamily: 'DM Mono' }, v.toFixed(1) + suffix),
          e('text', { x: bx + x.bandwidth() / 2, y: h - 18, textAnchor: 'middle', fill: muted, fontSize: '10', fontFamily: 'DM Mono' }, d[0])
        );
      })
    )
  );
}

// ---------------------------------------------------------------- classifier (client-side inference)
function tokenize(text) {
  const toks = text.toLowerCase().match(/[a-z0-9_]{2,}/g) || [];
  const grams = toks.slice();
  for (let i = 0; i < toks.length - 1; i++) grams.push(toks[i] + ' ' + toks[i + 1]);
  return grams;
}

// Same TF-IDF representation the classifier uses (unigrams+bigrams, idf-weighted,
// L2-normalized) — reused below for duplicate detection via cosine similarity, so
// "duplicidade" isn't a second bolted-on method, it's the same vector space.
function vectorize(text, weights) {
  const termIndex = weights.__termIndex;
  const grams = tokenize(text);
  const counts = new Map();
  for (const g of grams) {
    const idx = termIndex.get(g);
    if (idx === undefined) continue;
    counts.set(idx, (counts.get(idx) || 0) + 1);
  }
  const vecIdx = [], vecValRaw = [];
  let sumSq = 0;
  for (const [idx, count] of counts) {
    const tf = 1 + Math.log(count);
    const v = tf * weights.idf[idx];
    vecIdx.push(idx);
    vecValRaw.push(v);
    sumSq += v * v;
  }
  const norm = Math.sqrt(sumSq) || 1;
  const vec = new Map();
  for (let k = 0; k < vecIdx.length; k++) vec.set(vecIdx[k], vecValRaw[k] / norm);
  return { vec, matched: vecIdx.length, tokens: grams.length };
}

// Cosine similarity between two already-L2-normalized sparse vectors: since both
// have unit norm, this is just their dot product over shared dimensions.
function cosineSim(vecA, vecB) {
  const [small, big] = vecA.size <= vecB.size ? [vecA, vecB] : [vecB, vecA];
  let dot = 0;
  for (const [idx, val] of small) {
    const other = big.get(idx);
    if (other !== undefined) dot += val * other;
  }
  return dot;
}

const DUPLICATE_THRESHOLD = 0.6; // illustrative, not tuned on labeled duplicate pairs

function findLikelyDuplicate(vec, openTickets, weights) {
  let best = null;
  for (const ticket of openTickets) {
    if (ticket.duplicateOf) continue; // don't chain duplicates off duplicates
    const score = cosineSim(vec, vectorize(ticket.text, weights).vec);
    if (score >= DUPLICATE_THRESHOLD && (!best || score > best.score)) best = { ticket, score };
  }
  return best;
}

function classify(text, weights) {
  const { vec, matched, tokens } = vectorize(text, weights);
  const nClasses = weights.classes.length;
  const scores = weights.intercept.slice();
  for (let c = 0; c < nClasses; c++) {
    const coefRow = weights.coef[c];
    let s = 0;
    for (const [idx, val] of vec) s += val * coefRow[idx];
    scores[c] += s;
  }
  const maxScore = Math.max(...scores);
  const exps = scores.map((s) => Math.exp(s - maxScore));
  const sumExp = exps.reduce((a, b) => a + b, 0);
  const probs = exps.map((v) => v / sumExp);
  const order = weights.classes.map((c, i) => ({ label: c, p: probs[i] })).sort((a, b) => b.p - a.p);
  return { matched, tokens, order };
}

const RISK = /(fraud|chargeback|unauthori[sz]ed|breach|lawsuit|legal|password|leak|hack|phishing|refund|reimburse|cancel|billing|payment|bank|credit card|access|permission|fraude|reembolso|cancelamento|cobran[çc]a|pagamento|banco|cart[aã]o|senha|acesso|permiss)/i;
const AUTO_REPLY_CONFIDENCE = 0.90;
const SAFE_AUTOREPLY_TEMPLATES = [
  { id: 'storage-capacity-v1', category: 'Storage', intent: /(storage|disk|quota|space|capacity|folder full)/i, excludes: /(shared folder|grant|restore|role|access|permission)/i, reply: 'Recebemos seu chamado sobre capacidade de armazenamento. Verifique arquivos temporários e itens duplicados antes de excluir qualquer conteúdo. Se o problema continuar, responda com o nome do recurso afetado para que a equipe responsável faça a análise.' },
  { id: 'hardware-basic-check-v1', category: 'Hardware', intent: /(keyboard|mouse|monitor|screen|battery)/i, excludes: /(replacement|replace|purchase|warranty|damage)/i, reply: 'Recebemos seu chamado de hardware. Verifique a conexão física, reinicie o equipamento e teste o periférico em outra porta. Se o problema persistir, responda informando o equipamento e o erro observado.' },
];
function routingDecision(text, top, weights) {
  const risky = RISK.test(text);
  const lowConf = top.p < weights.confidence_threshold;
  if (risky)
    return { auto: false, title: 'Revisão humana obrigatória', reason: 'Texto contém termo de risco (segurança, fraude, senha ou similar) — guardrail desvia para humano independente da confiança do modelo.' };
  if (lowConf)
    return { auto: false, title: 'Revisão humana recomendada', reason: `Confiança do modelo (${pct(top.p)}) abaixo do limiar de ${pct(weights.confidence_threshold)} — melhor perguntar/triagem manual do que arriscar um roteamento errado.` };
  return { auto: true, title: 'Auto-rotear + rascunho de resposta', reason: `Confiança ${pct(top.p)} ≥ limiar de ${pct(weights.confidence_threshold)} e nenhum termo de risco detectado — segue para a fila especialista com rascunho para aprovação do agente.` };
}

function automaticReplyDecision(text, top) {
  if (RISK.test(text)) return { autoReply: false, reason: 'Bloqueado por tema crítico ou de segurança.' };
  if (top.p < AUTO_REPLY_CONFIDENCE) return { autoReply: false, reason: `Confiança abaixo de ${pct(AUTO_REPLY_CONFIDENCE, 0)}.` };
  const template = SAFE_AUTOREPLY_TEMPLATES.find((item) => item.category === top.label && item.intent.test(text) && !item.excludes.test(text));
  if (!template) return { autoReply: false, reason: 'Não há template aprovado para esta categoria e intenção.' };
  return { autoReply: true, template, reason: `Template aprovado ${template.id}; confiança ${pct(top.p)}; sem termo crítico detectado.` };
}

function computeResult(text, weights, humanOwned = false) {
  const { matched, tokens, order } = classify(text, weights);
  const top = order[0];
  const decision = routingDecision(text, top, weights);
  const autoReply = humanOwned
    ? { autoReply: false, reason: 'Agente responsável: você. Automação pausada neste ticket; respostas dependem do seu envio.' }
    : automaticReplyDecision(text, top);
  return { matched, tokens, order, top, decision, autoReply };
}

// ---------------------------------------------------------------- Agent workspace demo
// Priority is never self-reported by the customer — it's easy to game (everyone picks
// "high") and the diagnostic already showed the declared label in Dataset 1 doesn't
// predict real resolution time. The system's `priority` is computed only from signals
// in the text via suggestPriority(), independent of any customer input.
const AGENT_SEEDS = [
  { id: 'TK-1043', channel: 'E-mail', customer: 'Julia Martins', text: 'My disk storage is full and I need help freeing capacity.', status: 'Resposta automática enviada' },
  { id: 'TK-1042', channel: 'E-mail', customer: 'Marina Costa', text: 'I cannot access the shared folder after my role changed. Please restore access.', status: 'Novo' },
  { id: 'TK-1041', channel: 'Chat', customer: 'Diego Ramos', text: 'My laptop keyboard stopped working and I need help with a replacement.', status: 'Novo' },
  { id: 'TK-1040', channel: 'Telefone', customer: 'Cliente protegido', text: 'There is an unauthorized charge on my account and I need help urgently.', status: 'Novo' },
];

const PRIORITY_ORDER = { 'Crítica': 0, 'Alta': 1, 'Média': 2, 'Baixa': 3 };
const priorityDeadline = { 'Crítica': 15, 'Alta': 60, 'Média': 240, 'Baixa': 480 };
const URGENCY_TERMS = /(urgent|immediately|asap|down|outage|cannot work|can't work|stopped working|not working|critical|emergency|urgente|imediatamente|parado|cr[ií]tico|emerg[eê]ncia)/i;

// Independent triage signal: risk terms escalate hardest (they already force human
// review anyway); urgency language escalates next; low classifier confidence is treated
// as "needs eyes on it soon"; otherwise defaults to the lowest tier. Illustrative
// thresholds, same spirit as the classifier's own confidence threshold — not tuned on
// labeled priority data, since this dataset doesn't have ground-truth urgency labels.
function suggestPriority(text, top) {
  if (RISK.test(text)) return { level: 'Crítica', reason: 'Termo de risco (segurança, fraude ou financeiro) detectado no texto.' };
  if (URGENCY_TERMS.test(text)) return { level: 'Alta', reason: 'Termo de urgência operacional no texto (ex.: "down", "not working", "urgent").' };
  if (top.p < 0.6) return { level: 'Média', reason: 'Confiança de classificação baixa — sinal insuficiente para descartar revisão.' };
  return { level: 'Baixa', reason: 'Nenhum termo de risco ou urgência detectado; classificação com confiança alta.' };
}
const CLOSED_STATUSES = new Set(['Resolvido', 'Vinculado como duplicata']);
function dueLabel(ticket) {
  if (ticket.status === 'Resolvido') return 'Concluído';
  if (ticket.status === 'Vinculado como duplicata') return 'Vinculado';
  const minutes = Math.max(0, Math.ceil((ticket.dueAt - Date.now()) / 60000));
  if (minutes === 0) return 'Prazo vencido';
  return minutes < 60 ? `Prazo: ${minutes} min` : `Prazo: ${Math.ceil(minutes / 60)} h`;
}
function orderedTickets(tickets) {
  return [...tickets].sort((a, b) => {
    const aDone = CLOSED_STATUSES.has(a.status) ? 1 : 0;
    const bDone = CLOSED_STATUSES.has(b.status) ? 1 : 0;
    return aDone - bDone || PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority] || a.dueAt - b.dueAt;
  });
}
function priorityClass(priority) {
  return priority.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

function suggestedReply(result) {
  if (result.autoReply.autoReply) return result.autoReply.template.reply;
  if (!result.decision.auto) return 'Obrigado por nos avisar. Um especialista vai revisar seu caso antes de seguirmos com qualquer ação. Vamos retornar com a próxima atualização assim que possível.';
  return `Recebemos sua solicitação. Ela foi direcionada à fila de ${result.top.label}; um especialista vai revisar o caso e responder com os próximos passos.`;
}

function initialConversation(ticket, weights) {
  const result = computeResult(ticket.text, weights);
  const entries = [{ role: 'customer', label: ticket.customer, text: ticket.text, time: 'Agora' }];
  if (ticket.status === 'Resposta automática enviada' && result.autoReply.autoReply) {
    entries.push({ role: 'automation', label: 'Resposta automática', text: suggestedReply(result), time: 'Agora', template: result.autoReply.template.id });
  }
  return entries;
}

function AgentWorkspace({ weights }) {
  const [tickets, setTickets] = useState(() =>
    AGENT_SEEDS.map((seed) => {
      const suggestion = suggestPriority(seed.text, computeResult(seed.text, weights).top);
      return { ...seed, priority: suggestion.level, priorityReason: suggestion.reason, dueAt: Date.now() + priorityDeadline[suggestion.level] * 60 * 1000 };
    })
  );
  const [selectedId, setSelectedId] = useState(AGENT_SEEDS[0].id);
  const [message, setMessage] = useState('I cannot access the shared folder after my role changed. Please restore access.');
  const [channel, setChannel] = useState('E-mail');
  const [notice, setNotice] = useState('');
  const [conversations, setConversations] = useState(() => Object.fromEntries(AGENT_SEEDS.map((ticket) => [ticket.id, initialConversation(ticket, weights)])));
  const selected = tickets.find((ticket) => ticket.id === selectedId) || tickets[0];
  const result = computeResult(selected.text, weights, selected.humanOwned);
  const [draft, setDraft] = useState(() => suggestedReply(computeResult(AGENT_SEEDS[0].text, weights)));

  function choose(ticket) {
    setSelectedId(ticket.id);
    setDraft(suggestedReply(computeResult(ticket.text, weights)));
    setNotice('');
  }
  function submitTicket() {
    const text = message.trim();
    if (!text) return;
    const inference = computeResult(text, weights);
    const openTickets = tickets.filter((t) => !CLOSED_STATUSES.has(t.status));
    const dup = findLikelyDuplicate(vectorize(text, weights).vec, openTickets, weights);
    const status = dup ? 'Possível duplicata' : inference.autoReply.autoReply ? 'Resposta automática enviada' : 'Novo';
    const suggestion = suggestPriority(text, inference.top);
    const ticket = {
      id: `TK-${1044 + tickets.length}`, channel, customer: 'Nova solicitação', text, status,
      priority: suggestion.level, priorityReason: suggestion.reason,
      dueAt: Date.now() + priorityDeadline[suggestion.level] * 60 * 1000,
      duplicateOf: dup ? dup.ticket.id : null,
      duplicateScore: dup ? dup.score : null,
    };
    setTickets((current) => [ticket, ...current]);
    setConversations((current) => ({ ...current, [ticket.id]: dup ? [{ role: 'customer', label: ticket.customer, text, time: 'Agora' }] : initialConversation(ticket, weights) }));
    setSelectedId(ticket.id);
    setDraft(suggestedReply(inference));
    setNotice(
      dup
        ? `Possível duplicata do ${dup.ticket.id} (${pct(dup.score)} de similaridade de texto) — resposta automática pausada até o agente revisar.`
        : inference.autoReply.autoReply
        ? `Resposta enviada automaticamente com o template ${inference.autoReply.template.id}.`
        : 'Ticket criado e enviado para a fila de atendimento.'
    );
  }
  function linkAsDuplicate() {
    if (!selected.duplicateOf) return;
    const originalId = selected.duplicateOf;
    setTickets((current) => current.map((t) => (t.id === selected.id ? { ...t, status: 'Vinculado como duplicata' } : t)));
    setConversations((current) => ({
      ...current,
      [selected.id]: [...(current[selected.id] || []), { role: 'system', label: 'Vinculação de duplicata', text: `Vinculado ao ${originalId} como o mesmo caso; não será trabalhado separadamente.`, time: 'Agora' }],
    }));
    setNotice(`Vinculado ao ${originalId}. Removido da fila ativa.`);
  }
  function dismissDuplicate() {
    if (!selected.duplicateOf) return;
    setTickets((current) => current.map((t) => (t.id === selected.id ? { ...t, duplicateOf: null, duplicateScore: null, status: 'Novo' } : t)));
    setConversations((current) => ({
      ...current,
      [selected.id]: [...(current[selected.id] || []), { role: 'system', label: 'Duplicata descartada', text: 'Agente revisou o par sinalizado e confirmou que é um caso distinto; segue tratamento normal.', time: 'Agora' }],
    }));
    setNotice('Marcado como caso novo, não duplicata.');
  }
  function act(label, status) {
    setTickets((current) => current.map((ticket) => ticket.id === selected.id ? { ...ticket, status } : ticket));
    const event = status === 'Resolvido'
      ? { role: 'agent', label: 'Agente de suporte', text: draft, time: 'Agora' }
      : { role: 'system', label: 'Registro da operação', text: label, time: 'Agora' };
    setConversations((current) => ({ ...current, [selected.id]: [...(current[selected.id] || []), event] }));
    setNotice(label);
  }
  function sendReply() {
    if (selected.status === 'Resolvido') return;
    setTickets((current) => current.map((ticket) => ticket.id === selected.id ? { ...ticket, status: 'Aguardando cliente' } : ticket));
    setConversations((current) => ({ ...current, [selected.id]: [...(current[selected.id] || []), { role: 'agent', label: 'Agente de suporte', text: draft, time: 'Agora' }] }));
    setNotice('Resposta enviada. O ticket continua aberto até a confirmação de resolução do cliente.');
  }
  function requestResolutionConfirmation() {
    if (selected.status === 'Resolvido') return;
    setTickets((current) => current.map((ticket) => ticket.id === selected.id ? { ...ticket, status: 'Confirmação enviada' } : ticket));
    setConversations((current) => ({ ...current, [selected.id]: [...(current[selected.id] || []), { role: 'automation', label: 'Confirmação de resolução', text: 'Conseguimos resolver sua solicitação? Confirme para encerrarmos o atendimento.', time: 'Agora' }] }));
    setNotice('Pedido de confirmação enviado. A resolução só será concluída após a resposta do cliente.');
  }
  function confirmResolved() {
    setTickets((current) => current.map((ticket) => ticket.id === selected.id ? { ...ticket, status: 'Resolvido', awaitingRating: true } : ticket));
    setConversations((current) => ({ ...current, [selected.id]: [...(current[selected.id] || []), { role: 'customer', label: selected.customer, text: 'Sim, meu problema foi resolvido.', time: 'Agora' }, { role: 'automation', label: 'Pesquisa de satisfação', text: 'Que bom! Como você avalia este atendimento de 1 a 5?', time: 'Agora' }] }));
    setNotice('Resolução confirmada pelo cliente. Falta apenas registrar a satisfação.');
  }
  function reopenTicket() {
    setTickets((current) => current.map((ticket) => ticket.id === selected.id ? { ...ticket, status: 'Reaberto', humanOwned: true } : ticket));
    setConversations((current) => ({ ...current, [selected.id]: [...(current[selected.id] || []), { role: 'customer', label: selected.customer, text: 'Ainda preciso de ajuda.', time: 'Agora' }, { role: 'system', label: 'Controle humano', text: 'Ticket reaberto e devolvido ao atendimento humano.', time: 'Agora' }] }));
    setNotice('Ticket reaberto e colocado sob controle humano.');
  }
  function rateSatisfaction(score) {
    setTickets((current) => current.map((ticket) => ticket.id === selected.id ? { ...ticket, satisfaction: score, awaitingRating: false } : ticket));
    setConversations((current) => ({ ...current, [selected.id]: [...(current[selected.id] || []), { role: 'customer', label: selected.customer, text: `Minha avaliação: ${score} de 5.`, time: 'Agora' }, { role: 'system', label: 'CSAT registrado', text: `Satisfação registrada: ${score}/5.`, time: 'Agora' }] }));
    setNotice(`Satisfação registrada: ${score}/5.`);
  }
  function assumeTicket() {
    if (selected.humanOwned || selected.status === 'Resolvido') return;
    const time = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    const label = `Atendimento assumido por você às ${time}. Automação pausada; respostas anteriores permanecem no histórico.`;
    setTickets(current => current.map(ticket => ticket.id === selected.id
      ? { ...ticket, humanOwned: true, status: 'Em atendimento', assumedAt: time } : ticket));
    setConversations(current => ({ ...current, [selected.id]: [...(current[selected.id] || []),
      { role: 'system', label: 'Controle humano', text: label, time }] }));
    setNotice(label);
  }
  const badge = selected.duplicateOf ? 'review' : selected.humanOwned ? 'review' : result.autoReply.autoReply ? 'sent' : result.decision.auto ? 'ready' : result.decision.title.includes('obrigatória') ? 'risk' : 'review';
  const badgeLabel = selected.duplicateOf
    ? `Possível duplicata de ${selected.duplicateOf}`
    : selected.humanOwned
    ? 'Sob seu controle · Automação pausada'
    : result.autoReply.autoReply
    ? 'Resposta automática enviada'
    : result.decision.title;

  return e('div', { className: 'agent-demo' },
    e(
      'div',
      { className: 'agent-titlebar' },
      e('span', { className: 'agent-wordmark' }, e('span', { className: 'wordmark-dot' }), 'Winnow'),
      e('span', { className: 'agent-live' }, e('span', { className: 'live-dot' }), 'ao vivo, no seu navegador')
    ),
    e('div', { className: 'customer-composer glass-pane' },
      e('div', null,
        e('p', { className: 'agent-kicker' }, 'SIMULE A ENTRADA DO CLIENTE'),
        e('h3', null, 'Envie um ticket para a central'),
        e('p', null, 'Use texto em inglês: o modelo atual foi treinado em tickets de TI nesse idioma.'),
        e('p', { className: 'auto-criteria' }, 'Envio automático: confiança ≥ 90% + categoria/intenção com template aprovado + nenhum termo financeiro, de cancelamento, acesso, senha, fraude ou jurídico.'),
        e('p', { className: 'auto-criteria priority-note' }, 'Não existe campo de prioridade aqui de propósito: o cliente tende a marcar tudo como urgente. Quem decide a prioridade é a triagem automática, calculada só a partir do texto.')
      ),
        e('div', { className: 'composer-fields' },
          e('select', { value: channel, onChange: (event) => setChannel(event.target.value), 'aria-label': 'Canal do ticket' }, ['E-mail', 'Chat', 'Telefone', 'Redes sociais'].map((item) => e('option', { key: item }, item))),
          e('textarea', { value: message, onChange: (event) => setMessage(event.target.value), 'aria-label': 'Mensagem do cliente', placeholder: 'Descreva o problema do cliente…' }),
        e('button', { className: 'btn-accent', onClick: submitTicket }, 'Enviar para a central')
      )
    ),
    e('div', { className: 'agent-console' },
      e('aside', { className: 'ticket-list glass-pane' },
        e('div', { className: 'agent-pane-head' }, e('span', null, 'Fila por urgência e prazo'), e('b', null, tickets.filter((ticket) => !CLOSED_STATUSES.has(ticket.status)).length)),
        e('p', { className: 'queue-sort-note' }, 'Ordenada pela prioridade que a triagem automática calcula do texto — crítica primeiro, depois o prazo mais próximo. O cliente não define isso.'),
        orderedTickets(tickets).map((ticket) => {
          const itemResult = computeResult(ticket.text, weights, ticket.humanOwned);
          const itemClass = ticket.duplicateOf ? 'review' : itemResult.autoReply.autoReply ? 'sent' : itemResult.decision.auto ? 'ready' : itemResult.decision.title.includes('obrigatória') ? 'risk' : 'review';
          return e('button', { key: ticket.id, className: `ticket-row ${ticket.id === selected.id ? 'selected' : ''}`, onClick: () => choose(ticket) },
            e('span', { className: `ticket-dot ${itemClass}` }),
            e('span', { className: 'ticket-row-main' }, e('b', null, ticket.customer), e('small', null, `${ticket.id} · ${ticket.channel}`)),
            e('span', { className: 'ticket-row-side' },
              ticket.duplicateOf && e('span', { className: 'duplicate-chip' }, `Duplicata? · ${ticket.duplicateOf}`),
              e('span', { className: `priority-chip priority-${priorityClass(ticket.priority)}` }, ticket.priority),
              e('span', { className: 'ticket-deadline' }, dueLabel(ticket)),
              e('span', { className: 'ticket-state' }, ticket.humanOwned ? `${ticket.status} · Você` : ticket.status)));
        })
      ),
      e('article', { className: 'ticket-detail glass-pane' },
        e('div', { className: 'agent-pane-head' }, e('span', null, `${selected.id} · ${selected.channel}`), e('span', { className: `decision-badge ${badge}` }, badgeLabel)),
        e('p', { className: 'customer-name' }, selected.customer),
        e('blockquote', null, selected.text),
        selected.duplicateOf && e('div', { className: 'duplicate-callout' },
          e('strong', null, `Possível duplicata de ${selected.duplicateOf}`),
          e('span', null, `${pct(selected.duplicateScore)} de similaridade de texto (mesma representação TF-IDF do classificador) — resposta automática pausada até revisão.`),
          e('div', { className: 'duplicate-actions' },
            e('button', { className: 'btn-outline', onClick: linkAsDuplicate }, 'Vincular como duplicata'),
            e('button', { className: 'btn-outline', onClick: dismissDuplicate }, 'Tratar como caso novo'))),
        e('div', { className: 'ai-decision' },
          e('div', null, e('span', null, 'Leitura da IA'), e('strong', null, result.top.label)),
          e('div', null, e('span', null, 'Confiança'), e('strong', null, pct(result.top.p))),
          e('div', null, e('span', null, 'Alternativas'), e('strong', null, result.order.slice(1, 3).map((item) => item.label).join(' · ')))
        ),
        e('div', { className: 'priority-insight' },
          e('span', null, e('span', { className: 'pi-label' }, 'Prioridade — triagem automática') , e('strong', null, selected.priority)),
          e('p', null, selected.priorityReason)
        ),
        e('p', { className: 'agent-reason' }, selected.humanOwned ? 'Você assumiu este atendimento. A IA continua oferecendo classificação e sugestões; o envio fica sob sua responsabilidade.' : result.decision.reason),
        e('div', { className: `auto-policy ${selected.duplicateOf ? 'blocked' : result.autoReply.autoReply ? 'allowed' : 'blocked'}` },
          e('strong', null, selected.duplicateOf ? 'Envio automático bloqueado' : result.autoReply.autoReply ? 'Envio automático autorizado' : 'Envio automático bloqueado'),
          e('span', null, selected.duplicateOf ? `Possível duplicata de ${selected.duplicateOf} — aguardando decisão do agente antes de qualquer envio.` : result.autoReply.reason)),
        e('label', { className: 'draft-label', htmlFor: 'agentDraft' }, 'Resposta sugerida — revise antes de enviar'),
        e('textarea', { id: 'agentDraft', value: draft, onChange: (event) => setDraft(event.target.value) }),
        e('div', { className: 'agent-actions' },
          e('button', { className: 'btn-outline', onClick: assumeTicket, disabled: selected.humanOwned || selected.status === 'Resolvido' }, selected.humanOwned ? 'Atendimento assumido por você' : 'Assumir atendimento'),
          e('button', { className: 'btn-outline', onClick: () => act('Categoria revisada pelo agente. A correção foi registrada para avaliação no próximo retreino.', 'Revisado') }, 'Corrigir categoria'),
          e('button', { className: 'btn-outline', onClick: () => act('Ticket encaminhado para a fila especializada.', 'Encaminhado') }, 'Encaminhar'),
          !result.autoReply.autoReply && e('button', { className: 'btn-outline', onClick: sendReply, disabled: selected.status === 'Resolvido' || selected.status === 'Confirmação enviada' }, 'Enviar resposta'),
          e('button', { className: 'btn-accent', onClick: requestResolutionConfirmation, disabled: selected.status === 'Resolvido' || selected.status === 'Confirmação enviada' }, 'Confirmar resolução')
        ),
        notice && e('p', { className: 'agent-notice' }, notice)
      )
    ),
    e('section', { className: 'conversation-panel glass-pane' },
      e('div', { className: 'conversation-head' },
        e('div', null, e('p', { className: 'agent-kicker' }, 'HISTÓRICO DO ATENDIMENTO'), e('h3', null, `Conversa · ${selected.id}`)),
        e('span', null, selected.status)
      ),
      e('div', { className: 'conversation-body' },
        (conversations[selected.id] || []).map((entry, index) =>
          e('div', { key: `${entry.role}-${index}`, className: `message-row ${entry.role}` },
            entry.role === 'system'
              ? e('div', { className: 'system-event' }, entry.text)
              : e('div', { className: 'message-bubble' },
                  e('div', { className: 'message-meta' }, entry.label, entry.template && ` · ${entry.template}`, e('time', null, entry.time)),
                  e('p', null, entry.text)
                )
          )
        ),
        !(conversations[selected.id] || []).some((entry) => entry.role === 'agent' || entry.role === 'automation') && e('p', { className: 'conversation-waiting' }, 'Aguardando aprovação ou resposta automática.'),
        selected.status === 'Confirmação enviada' && e('div', { className: 'resolution-choice' }, e('p', null, 'Simular resposta do cliente'), e('button', { className: 'btn-accent', onClick: confirmResolved }, 'Sim, foi resolvido'), e('button', { className: 'btn-outline', onClick: reopenTicket }, 'Ainda preciso de ajuda')),
        selected.awaitingRating && e('div', { className: 'satisfaction-request' }, e('p', null, 'Coletar satisfação — CSAT (nota de satisfação do cliente): como o cliente avaliou o atendimento?'), e('div', { className: 'rating-buttons' }, [1, 2, 3, 4, 5].map((score) => e('button', { key: score, onClick: () => rateSatisfaction(score), 'aria-label': `Avaliar atendimento com ${score} de 5` }, score))))
      )
    )
  );
}

// ---------------------------------------------------------------- static-ish HTML block builders
function heroChips(dq) {
  return [`${dq.total_rows.toLocaleString('pt-BR')} tickets recebidos`, `${dq.rows_valid_for_cycle_time.toLocaleString('pt-BR')} cronologias válidas`, 'Dataset operacional + corpus IT', 'React · visx · scikit-learn'];
}

function mismatchCalloutHtml(dq) {
  return `<strong>O que não bate:</strong> o enunciado descreve aproximadamente 30 mil tickets operacionais; o arquivo entregue contém ${dq.total_rows.toLocaleString(
    'pt-BR'
  )}. E a taxonomia de TI (tecnologia da informação) do corpus de treinamento não é a mesma de tickets comerciais. A modelagem separa essas funções para evitar conclusões ou métricas contaminadas.`;
}

function kpiQualityHtml(dq) {
  const rows = [
    ['Tickets na base', dq.total_rows.toLocaleString('pt-BR'), 'Universo operacional entregue'],
    ['Com resolução + satisfação (CSAT)', dq.rows_with_resolution_and_rating.toLocaleString('pt-BR'), `${(100 * dq.rows_with_resolution_and_rating / dq.total_rows).toFixed(1)}% com desfecho preenchido`],
    ['Cronologia válida', dq.rows_valid_for_cycle_time.toLocaleString('pt-BR'), `${dq.pct_valid_for_cycle_time}% aptos para duração`],
    ['Tempo até 1ª resposta', '?', '`created_at` não existe na base'],
  ];
  return rows.map(([l, v, n]) => `<div class="kpi"><span class="kpi-label">${l}</span><strong class="kpi-value">${v}</strong><span class="kpi-note">${n}</span></div>`).join('');
}

function qualityCalloutHtml(dq) {
  return `<strong>Leitura correta:</strong> \`First Response Time\` vem como timestamp, não duração. Entre os ${dq.rows_with_both_timestamps.toLocaleString(
    'pt-BR'
  )} registros com os dois timestamps preenchidos, ${dq.rows_with_invalid_or_zero_duration.toLocaleString(
    'pt-BR'
  )} têm duração negativa ou zero (zero foi excluído por convenção). Por isso este diagnóstico usa exclusivamente os ${dq.rows_valid_for_cycle_time.toLocaleString(
    'pt-BR'
  )} pares temporais válidos e recomenda corrigir o rastreamento antes de instituir um novo SLA (prazo acordado de atendimento).`;
}

function worstRowsHtml(diag) {
  return diag.worst_combinations
    .slice(0, 4)
    .map((r) => {
      const danger = r.avg_satisfaction != null && r.avg_satisfaction < 2.5;
      return `<tr><td>${CHANNEL_PT[r['Ticket Channel']] || r['Ticket Channel']} · ${r['Ticket Priority']} · ${TYPE_PT[r['Ticket Type']] || r['Ticket Type']}</td><td class="num">${fmt(
        r.p90_hours
      )}h</td><td class="num ${danger ? 'danger' : ''}">${r.avg_satisfaction != null ? fmt(r.avg_satisfaction, 2) : '—'}</td></tr>`;
    })
    .join('');
}

function findingGridHtml(diag) {
  const slow = diag.by_type[0], priority = diag.by_priority[0];
  const sat = diag.satisfaction_drivers.summaries.by_type[0];
  return [
    ['A', 'Maior duração observada', `Reembolso tem P90 de ${fmt(slow.p90_hours)}h após a primeira resposta. Investigar aprovações e transferências; a causa ainda não foi medida.`],
    ['B', 'Prioridade e complexidade', `Prioridade alta: P90 de ${fmt(priority.p90_hours)}h. Coletar gravidade real, esforço ativo e histórico da fila antes de avaliar o processo.`],
    ['C', 'Todas as avaliações', `${TYPE_PT[sat.label]} tem a menor média observada: ${fmt(sat.mean, 2)}/5 em ${sat.n} avaliações. Diferenças pequenas não estabelecem um fator causal.`]
  ].map(([n,t,d]) => `<article class="finding"><span class="number">${n}</span><h3>${t}</h3><p>${d}</p></article>`).join('');
}

function satisfactionTableHtml(diag) {
  return '<thead><tr><th>Tipo</th><th class="num">Avaliações</th><th class="num">Média / 5</th><th class="num">Intervalo de 95%</th></tr></thead><tbody>' +
    diag.satisfaction_drivers.summaries.by_type.map(r => `<tr><td>${TYPE_PT[r.label]}</td><td class="num">${r.n}</td><td class="num">${fmt(r.mean,2)}</td><td class="num">${fmt(r.ci95_low,2)} a ${fmt(r.ci95_high,2)}</td></tr>`).join('') + '</tbody>';
}

function scenariosHtml(roi) {
  return '<thead><tr><th>Cenário</th><th class="num">Elegíveis após risco</th><th class="num">Triagem / retrabalho</th><th class="num">Horas/ano</th><th class="num">Valor/ano</th></tr></thead><tbody>' +
    roi.scenarios.map(r => `<tr><td>${r.name}</td><td class="num">${pct(r.eligible_share)}</td><td class="num">${r.triage_minutes} / ${r.rework_minutes} min</td><td class="num">${r.capacity_hours}</td><td class="num">R$ ${fmt(r.capacity_value_brl,0)}</td></tr>`).join('') + '</tbody>';
}

function doListHtml(m) {
  return [
    ['Classificação e roteamento assistidos', `Cobre ${pct(m.coverage_at_threshold, 0)} dos tickets com ${pct(m.accuracy_when_confidence_above_threshold, 0)} de acurácia condicional — essa fatia, não a acurácia bruta, vira auto-roteamento.`],
    ['Rascunho de resposta para o agente', 'A IA organiza o pedido e sugere um rascunho para categorias de alta confiança; o agente sempre aprova antes de enviar.'],
    ['Sinalização de risco', 'Termos de fraude, senha e acesso não autorizado disparam revisão obrigatória — nunca resposta automática (teste ao vivo abaixo).'],
    ['Detecção de duplicatas', 'Cada ticket novo é comparado por similaridade de cosseno (mesmo vetor TF-IDF do classificador) contra os tickets abertos; acima de 60% de similaridade, a resposta automática é pausada e o agente decide vincular ou tratar como caso novo — nunca a IA decide sozinha.'],
    ['Triagem de prioridade', 'Calculada só do texto (termos de risco, urgência, confiança do classificador) — nunca perguntada ao cliente, porque autorrelato de urgência é fácil de inflar. Fila ordenada por essa prioridade e pelo prazo (Winnow, abaixo).'],
  ]
    .map(([t, d]) => `<div class="action-item"><h5>${t}</h5><p>${d}</p></div>`)
    .join('');
}

function dontListHtml(m, diag) {
  const worstType = diag.by_type[0];
  return [
    ['Reembolso, cancelamento, cobrança contestada', `Impacto financeiro direto — "${TYPE_PT[worstType['Ticket Type']] || worstType['Ticket Type']}" já é o tipo com pior P90 nos dados.`],
    ['Incidentes de segurança e contas bloqueadas', 'Automatizar uma resposta ou mudança de acesso pode agravar um ataque em andamento.'],
    ['Confiança abaixo do limiar', `Abaixo de ${pct(m.confidence_threshold, 0)}, a acurácia real cai para ${pct(m.accuracy_when_confidence_below_threshold, 0)} — auto-rotear aí custa mais em retrabalho do que economiza.`],
  ]
    .map(([t, d]) => `<div class="action-item"><h5>${t}</h5><p>${d}</p></div>`)
    .join('');
}

function perClassTableHtml(m) {
  const rows = CAT_ORDER.map((label) => ({ label, ...m.per_class[label] })).sort((a, b) => b.f1 - a.f1);
  return `<thead><tr><th>Categoria</th><th class="num">Precisão</th><th class="num">Recall</th><th class="num">F1</th><th class="num">Suporte</th></tr></thead><tbody>${rows
    .map((r) => `<tr><td>${r.label}</td><td class="num">${fmt(r.precision * 100, 1)}%</td><td class="num">${fmt(r.recall * 100, 1)}%</td><td class="num">${fmt(r.f1 * 100, 1)}%</td><td class="num">${r.support.toLocaleString('pt-BR')}</td></tr>`)
    .join('')}</tbody>`;
}

function embExperimentTableHtml(embExp) {
  const base = embExp.tfidf_baseline;
  const emb = embExp.embeddings_result;
  const rows = [
    ['Acurácia geral', base.accuracy, emb.accuracy, embExp.delta.accuracy],
    ['Macro F1', base.macro_f1, emb.macro_f1, embExp.delta.macro_f1],
    ['Cobertura @ 60% confiança', base.coverage_at_threshold, emb.coverage_at_threshold, embExp.delta.coverage_at_threshold],
    ['Acurácia na cobertura', base.accuracy_when_covered, emb.accuracy_when_covered, embExp.delta.accuracy_when_covered],
  ];
  return `<thead><tr><th>Métrica</th><th class="num">TF-IDF + LR (em produção)</th><th class="num">Embeddings (${embExp.model_tested})</th><th class="num">Delta</th></tr></thead><tbody>${rows
    .map(
      ([label, b, e2, d]) =>
        `<tr><td>${label}</td><td class="num">${pct(b, 1)}</td><td class="num">${pct(e2, 1)}</td><td class="num danger">${d >= 0 ? '+' : ''}${fmt(d * 100, 1)}pp</td></tr>`
    )
    .join('')}</tbody>`;
}

function kpiRoiHtml(m, roi) {
  const c = roi.calculation;
  const rows = [
    ['Capacidade potencial/ano', c.potential_capacity_hours_per_year.toLocaleString('pt-BR'), 'Ganho − retrabalho de erro'],
    ['Valor potencial/ano', 'R$ ' + c.potential_capacity_value_brl_per_year.toLocaleString('pt-BR'), `a R$${roi.assumptions.hourly_loaded_cost_brl}/h, antes dos custos de implantação`],
    ['Cobertura do modelo', pct(m.coverage_at_threshold, 0), `≥${pct(m.confidence_threshold, 0)} de confiança`],
    ['Acurácia na cobertura', pct(m.accuracy_when_confidence_above_threshold, 0), 'medida em holdout'],
  ];
  return rows.map(([l, v, n]) => `<div class="kpi"><span class="kpi-label">${l}</span><strong class="kpi-value">${v}</strong><span class="kpi-note">${n}</span></div>`).join('');
}

function roiTableHtml(roi) {
  const c = roi.calculation;
  return `<thead><tr><th>Cálculo</th><th class="num">Valor</th></tr></thead><tbody>
    <tr><td>Elegibilidade após risco (hipótese)</td><td class="num">${pct(roi.assumptions.eligible_share_after_risk_rules)}</td></tr>
    <tr><td>Triagem / retrabalho (hipóteses)</td><td class="num">${roi.assumptions.manual_triage_minutes_per_ticket} / ${roi.assumptions.rework_minutes_per_misroute} min</td></tr>
    <tr><td>Volume anual assumido</td><td class="num">${roi.assumptions.annual_ticket_volume.toLocaleString('pt-BR')} tickets</td></tr>
    <tr><td>Encaminhamentos projetados/ano (após elegibilidade assumida)</td><td class="num">${c.auto_routed_tickets_per_year.toLocaleString('pt-BR')}</td></tr>
    <tr><td>… corretamente roteados</td><td class="num">${c.correctly_auto_routed_per_year.toLocaleString('pt-BR')}</td></tr>
    <tr><td>… roteados errado (geram retrabalho)</td><td class="num">${c.incorrectly_auto_routed_per_year.toLocaleString('pt-BR')}</td></tr>
    <tr><td>Horas ganhas (triagem eliminada)</td><td class="num">+${c.hours_saved_from_correct_routing.toLocaleString('pt-BR')}h</td></tr>
    <tr><td>Horas perdidas (retrabalho de erro)</td><td class="num">−${c.hours_lost_to_rework_from_wrong_routing.toLocaleString('pt-BR')}h</td></tr>
  </tbody>`;
}

// ---------------------------------------------------------------- SideNav (scroll-spy)
const NAV_SECTIONS = [
  { id: 'modelagem', num: '00', label: 'Modelagem' },
  { id: 'metodologia', num: '01', label: 'Metodologia' },
  { id: 'qualidade', num: '02', label: 'Qualidade' },
  { id: 'ciclo', num: '03', label: 'Ciclo' },
  { id: 'tipo', num: '04', label: 'Tipo' },
  { id: 'decisao', num: '05', label: 'Winnow' },
  { id: 'roi', num: '06', label: 'ROI' },
];

function SideNav() {
  const [activeId, setActiveId] = useState(NAV_SECTIONS[0].id);

  useEffect(() => {
    const sections = NAV_SECTIONS.map((s) => document.getElementById(s.id)).filter(Boolean);
    if (!sections.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActiveId(entry.target.id);
        });
      },
      { rootMargin: '-45% 0px -50% 0px', threshold: 0 }
    );
    sections.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return e(
    'nav',
    { className: 'side-nav', 'aria-label': 'Navegação da página' },
    NAV_SECTIONS.map((s) =>
      e(
        'a',
        {
          key: s.id,
          href: `#${s.id}`,
          className: `side-nav-link${s.id === activeId ? ' active' : ''}`,
          onClick: (ev) => {
            ev.preventDefault();
            const el = document.getElementById(s.id);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          },
        },
        e('span', { className: 'side-nav-num' }, s.num),
        e('span', { className: 'side-nav-label' }, s.label)
      )
    )
  );
}

// ---------------------------------------------------------------- App
function App() {
  const [state, setState] = useState({ loading: true, error: null, diag: null, weights: null, metrics: null, roi: null, embExp: null });

  useEffect(() => {
    Promise.all([
      fetch('../output/diagnostic.json').then((r) => r.json()),
      fetch('../output/model_weights.json').then((r) => r.json()),
      fetch('../output/classifier_metrics.json').then((r) => r.json()),
      fetch('../output/roi_model.json').then((r) => r.json()),
      fetch('../output/embeddings_experiment.json').then((r) => r.json()),
    ])
      .then(([diag, weights, metrics, roi, embExp]) => {
        weights.__termIndex = new Map(weights.vocab_terms.map((t, i) => [t, i]));
        setState({ loading: false, error: null, diag, weights, metrics, roi, embExp });
      })
      .catch((err) => setState({ loading: false, error: err.message, diag: null, weights: null, metrics: null, roi: null, embExp: null }));
  }, []);

  if (state.loading) return e('div', { className: 'loading' }, 'Carregando diagnóstico…');
  if (state.error) return e('div', { className: 'error' }, 'Erro ao carregar os dados: ' + state.error);

  const { diag, weights, metrics: m, roi, embExp } = state;
  const dq = diag.data_quality;
  const o = diag.overall;
  const tail = diag.cycle_time_tail;
  const worstType = diag.by_type[0];
  const worstPriority = diag.by_priority[0];
  const worstCsatType = diag.by_type.slice().sort((a, b) => (a.avg_satisfaction ?? 5) - (b.avg_satisfaction ?? 5))[0];

  const chData = CHANNEL_ORDER.map((ch) => {
    const r = diag.by_channel.find((x) => x['Ticket Channel'] === ch);
    return [CHANNEL_PT[ch] || ch, r ? r.p90_hours : 0];
  });
  const tyData = diag.by_type.map((r) => [TYPE_PT[r['Ticket Type']] || r['Ticket Type'], r.p90_hours]);
  const bestCh = diag.by_channel.slice().sort((a, b) => b.p90_hours - a.p90_hours)[0];

  return e(
    React.Fragment,
    null,
    e('div', { className: 'shell nav' }, e('div', { className: 'brand' }, e('b', null, '>_'), ' CLEITON_EUGENIO'), e('span', null, 'Case · Operações / CX')),
    e(SideNav),

    e(
      'main',
      null,
      // hero
      e(
        'div',
        { className: 'shell hero' },
        e('p', { className: 'eyebrow' }, 'DIAGNÓSTICO · SUPORTE AO CLIENTE'),
        e('h1', null, 'O suporte não está só lento. ', e('em', null, 'Ele está mal medido.')),
        e(
          'p',
          { className: 'lede' },
          'Uma análise dos tickets operacionais para separar o que é gargalo real do que é ruído de instrumentação — e um classificador de verdade, rodando ao vivo no navegador, para testar onde IA pode reduzir esforço sem remover julgamento humano.'
        ),
        e('div', { className: 'chips' }, heroChips(dq).map((c, i) => e('span', { key: i, className: 'chip' }, c)))
      ),

      // 00 MODELAGEM
      e(
        'section',
        { id: 'modelagem' },
        e(
          'div',
          { className: 'shell' },
          e(
            'div',
            { className: 'section-head' },
            e('p', { className: 'section-num' }, '00 · MODELAGEM'),
            e('h2', null, 'Duas fontes, ', e('span', null, 'dois papéis — e uma divergência que importa.')),
            e('p', { className: 'section-copy' }, 'A análise começou pelo inventário das fontes e pela definição do grão de cada dado. Não é válido misturar métricas da operação com categorias de treinamento como se descrevessem o mesmo negócio.')
          ),
          e(
            'div',
            { className: 'source-grid' },
            e(
              'article',
              { className: 'source-card' },
              e('div', { className: 'file' }, 'customer_support_tickets.csv'),
              e('h3', null, 'Operação de suporte'),
              e(
                'p',
                null,
                e('strong', null, `${dq.total_rows.toLocaleString('pt-BR')} tickets.`),
                ' Fonte usada para medir o fluxo: canal, prioridade, tipo, timestamps, status, resolução e satisfação. O grão é um ticket identificado por ',
                e('span', { className: 'mono' }, 'Ticket ID'),
                '.'
              ),
              e(DatasetFields, {
                fields: OPERATION_FIELDS,
                missing: 'Data e hora de abertura, histórico de transferências, tempo ativo do agente e custos do atendimento. Por isso não medimos a demora até a primeira resposta nem o desperdício financeiro real.',
                purpose: 'Diagnóstico por canal, prioridade e tipo, análise de satisfação e intervalo entre primeira resposta e resolução. Registros incompletos são tratados conforme a métrica; não excluímos uma avaliação apenas porque sua duração é inválida.',
              })
            ),
            e(
              'article',
              { className: 'source-card' },
              e('div', { className: 'file' }, 'all_tickets_processed_improved_v3.csv'),
              e('h3', null, 'Corpus para classificação'),
              e(
                'p',
                null,
                e('strong', null, '47.837 tickets de TI (tecnologia da informação).'),
                ' Fonte usada apenas para treinar e testar o classificador do protótipo. O grão é um documento com uma categoria conhecida; não entra nos indicadores operacionais.'
              ),
              e(DatasetFields, {
                fields: TRAINING_FIELDS,
                missing: 'Canal, prioridade, datas de atendimento, solução aplicada, custos e nota de satisfação. Esta base não permite calcular os indicadores operacionais.',
                purpose: 'Treinar e testar a classificação de textos em oito categorias de TI (tecnologia da informação). As categorias são diferentes das do suporte comercial; as duas bases não foram unidas por ticket.',
              }),
              e('h4', null, 'Categorias presentes em Topic_group'),
              e('ul', { className: 'dataset-categories' }, [
                'Hardware (equipamentos)', 'HR Support (suporte a recursos humanos)',
                'Access (acesso)', 'Miscellaneous (assuntos diversos)',
                'Storage (armazenamento)', 'Purchase (compras)',
                'Internal Project (projeto interno)', 'Administrative rights (permissões administrativas)',
              ].map(label => e('li', { key: label }, label)))
            )
          ),
          e('div', { className: 'callout', dangerouslySetInnerHTML: { __html: mismatchCalloutHtml(dq) } })
        )
      ),

      // 01 METODOLOGIA
      e(
        'section',
        { id: 'metodologia' },
        e(
          'div',
          { className: 'shell' },
          e(
            'div',
            { className: 'section-head' },
            e('p', { className: 'section-num' }, '01 · METODOLOGIA'),
            e('h2', null, 'Primeiro entender o dado. ', e('span', null, 'Depois decidir o que ele permite afirmar.')),
            e('p', { className: 'section-copy' }, 'A abordagem foi desenhada para evitar dois erros comuns: usar uma base incompleta como se fosse verdade absoluta, e chamar de automação algo que ainda precisa de julgamento humano.')
          ),
          e(
            'div',
            { className: 'method-grid' },
            [
              ['01 · INVENTÁRIO', 'Separar as fontes', 'Mapeamos as duas bases e definimos seu papel. A base operacional explica o fluxo; a base de TI treina o classificador. Elas não foram misturadas.'],
              ['02 · QUALIDADE', 'Validar antes de medir', 'Checamos preenchimento, datas e cronologia. Tickets sem desfecho ou com horário impossível não entraram nos cálculos de duração.'],
              ['03 · DIAGNÓSTICO', 'Procurar a cauda', 'Usamos mediana e percentil 90 para encontrar onde os casos se alongam por canal, prioridade e tipo — sem confundir percentil com média.'],
              ['04 · PROTÓTIPO', 'Testar com holdout', `Classificador treinado com ${m.train_rows.toLocaleString('pt-BR')} textos e testado em ${m.test_rows.toLocaleString('pt-BR')} exemplos separados, nunca vistos no treino. Resultado: ${pct(m.accuracy, 1)} de acurácia.`],
              ['05 · ROI', 'Ancorar no medido', 'Combinamos desempenho medido em TI com hipóteses de elegibilidade, tempo de triagem e retrabalho. Um piloto deve validar essas premissas no suporte comercial.'],
              ['06 · GUARDRAILS', 'Decidir onde parar', 'Baixa confiança, fraude, senha, reembolso, cancelamento e questões legais exigem revisão humana. IA acelera a triagem; não decide o irreversível.'],
            ].map(([num, title, text]) => e('article', { key: num, className: 'method' }, e('span', { className: 'number' }, num), e('h3', null, title), e('p', null, text)))
          )
        )
      ),

      // 02 QUALIDADE
      e(
        'section',
        { id: 'qualidade' },
        e(
          'div',
          { className: 'shell' },
          e(
            'div',
            { className: 'section-head' },
            e('p', { className: 'section-num' }, '02 · QUALIDADE'),
            e('h2', null, 'Antes do insight, ', e('span', null, 'o dado precisa parar em pé.')),
            e('p', { className: 'section-copy' }, 'A primeira etapa não foi procurar um culpado pela nota de satisfação do cliente (CSAT). Foi testar se os eventos permitiam calcular o tempo do processo sem inventar duração.')
          ),
          e('div', { className: 'kpis', dangerouslySetInnerHTML: { __html: kpiQualityHtml(dq) } }),
          e('div', { className: 'callout', dangerouslySetInnerHTML: { __html: qualityCalloutHtml(dq) } })
        )
      ),

      // 03 CICLO
      e(
        'section',
        { id: 'ciclo' },
        e(
          'div',
          { className: 'shell' },
          e(
            'div',
            { className: 'section-head' },
            e('p', { className: 'section-num' }, '03 · CICLO'),
            e('h2', null, `Da primeira resposta à resolução: mediana de ${fmt(o.median_hours)}h. `, e('span', null, `Cerca de 10% ultrapassam ${fmt(o.p90_hours)}h.`)),
            e('p', { className: 'section-copy' }, 'Medimos resolução menos primeira resposta, em horas corridas. Falta a abertura do chamado para medir o tempo total ou a demora até a primeira resposta. Os recortes mais demorados orientam investigação; espera, transferências e retrabalho são hipóteses, pois suas etapas não estão registradas.')
          ),
          e(
            'div',
            { className: 'chart-grid' },
            e(
              'article',
              { className: 'chart-card' },
              e('h3', null, 'Tempo após a primeira resposta para resolver 90% dos tickets'),
              e('p', null, 'Horas corridas desde a primeira resposta · P90, não média'),
              e(BarChart, { data: chData, label: 'P90 do intervalo entre primeira resposta e resolução por canal', value: (d) => d[1] }),
              e(
                'div',
                { className: 'legend' },
                e('span', null, e('i', { style: { background: orange } }), `Ex.: ${CHANNEL_PT[bestCh['Ticket Channel']] || bestCh['Ticket Channel']} = 90 de cada 100 tickets são resolvidos em até ${fmt(bestCh.p90_hours)}h após a primeira resposta`),
                e('span', null, `Base: ${dq.rows_valid_for_cycle_time.toLocaleString('pt-BR')} tickets`)
              )
            ),
            e(
              'article',
              { className: 'chart-card' },
              e('h3', null, 'Onde concentrar a investigação'),
              e('p', null, 'Combinações canal × prioridade × tipo com maior sinal de espera ou insatisfação'),
              e('table', { className: 'table' }, e('thead', null, e('tr', null, e('th', null, 'Combinação'), e('th', { className: 'num' }, 'P90'), e('th', { className: 'num' }, 'CSAT'))), e('tbody', { dangerouslySetInnerHTML: { __html: worstRowsHtml(diag) } })),
              e('p', { className: 'source' }, 'Amostras pequenas (n<25): hipótese para investigar, não sentença causal.')
            )
          ),
          e(
            'div',
            { style: { marginTop: '46px' } },
            e('p', { className: 'section-num', style: { marginBottom: '10px' } }, 'QUANTO ESTAMOS DESPERDIÇANDO'),
            e('h3', { style: { fontSize: '22px', letterSpacing: '-.03em', margin: '0 0 20px' } }, 'Em horas, medido. Em R$, deliberadamente não.'),
            e('div', { className: 'kpis' },
              [
                ['Horas em excesso na cauda', tail.sample_total_excess_hours_above_median.toLocaleString('pt-BR'), `nos ${tail.sample_size.toLocaleString('pt-BR')} tickets válidos da amostra`],
                ['Excesso médio por ticket na cauda', fmt(tail.avg_excess_hours_per_tail_ticket), `horas além da mediana de ${fmt(tail.median_cycle_hours)}h`],
                ['Tickets na cauda', pct(tail.pct_tickets_above_median_in_long_tail / 100, 0), 'passam da mediana de tempo de ciclo'],
              ].map(([l, v, n]) => e('div', { key: l, className: 'kpi' }, e('span', { className: 'kpi-label' }, l), e('strong', { className: 'kpi-value' }, v), e('span', { className: 'kpi-note' }, n)))
            ),
            e('div', { className: 'callout', style: { marginTop: '20px' }, dangerouslySetInnerHTML: { __html: `<strong>Por que não vira R$:</strong> ${tail.interpretation}` } }),
            e('p', { className: 'source', style: { marginTop: '10px' } }, `Extrapolação ilustrativa, não medição: se essa mesma proporção se repetisse em ${tail.projected_annual_volume_assumed.toLocaleString('pt-BR')} tickets/ano (o volume citado no briefing), seriam ~${tail.projected_excess_hours_per_year.toLocaleString('pt-BR')} horas/ano na cauda — carrega o mesmo risco de generalizar de uma amostra de ${tail.sample_size.toLocaleString('pt-BR')} tickets.`)
          )
        )
      ),

      // 04 TIPO
      e(
        'section',
        { id: 'tipo' },
        e(
          'div',
          { className: 'shell' },
          e(
            'div',
            { className: 'section-head' },
            e('p', { className: 'section-num' }, '04 · TIPO'),
            e('h2', null, `${TYPE_PT[worstType['Ticket Type']] || worstType['Ticket Type']} tem o maior P90 observado. `, e('span', null, `A satisfação exige uma análise própria.`)),
            e('p', { className: 'section-copy' }, `A prioridade ${worstPriority['Ticket Priority']} tem P90 de ${fmt(worstPriority.p90_hours)}h. Isso não prova falha na priorização: complexidade e esforço ativo não foram medidos. Investigar antes de mudar prazos.`)
          ),
          e('article', { className: 'chart-card' }, e('h3', null, 'P90 por tipo de ticket'), e('p', null, 'Horas desde a primeira resposta · subconjunto com duração positiva'), e(BarChart, { data: tyData, label: 'P90 por tipo', value: (d) => d[1] })),
          e('div', { className: 'finding-grid', style: { marginTop: '18px' }, dangerouslySetInnerHTML: { __html: findingGridHtml(diag) } }),
          e('h3', null, 'Satisfação: todas as avaliações disponíveis'),
          e('p', null, `Base: ${diag.satisfaction_drivers.n_rated_tickets} avaliações. Comparações com duração usam ${diag.satisfaction_drivers.n_valid_for_time_association} pares positivos. Média da nota de 1 a 5; não é percentual de clientes satisfeitos.`),
          e('table', { className: 'table', dangerouslySetInnerHTML: { __html: satisfactionTableHtml(diag) } }),
          e('p', { className: 'source' }, diag.satisfaction_drivers.uncertainty_method),
          e('div', { className: 'callout', style: { marginTop: '20px' }, dangerouslySetInnerHTML: { __html: `<strong>Associação exploratória com satisfação:</strong> ${diag.satisfaction_drivers.interpretation}` } })
        )
      ),

      // 05 DECISÃO + SIMULADOR
      e(
        'section',
        { id: 'decisao' },
        e(
          'div',
          { className: 'shell' },
          e(
            'div',
            { className: 'section-head' },
            e('p', { className: 'section-num' }, '05 · DECISÃO'),
            e('h2', null, 'IA para tirar atrito. ', e('span', null, 'Humano para decidir o irreversível.')),
            e(
              'p',
              { className: 'section-copy' },
              `O classificador de textos de TI (tecnologia da informação) atingiu ${pct(m.accuracy, 1)} de acurácia em uma amostra separada de ${m.test_rows.toLocaleString('pt-BR')} tickets. Ao só auto-rotear acima de ${pct(
                m.confidence_threshold,
                0
              )} de confiança, cobre ${pct(m.coverage_at_threshold, 0)} do volume com ${pct(m.accuracy_when_confidence_above_threshold, 0)} de acerto — sinal suficiente para triagem assistida de alta confiança, não licença para automatizar todos os contatos.`
            )
          ),
          e(
            'div',
            { className: 'flow' },
            [
              ['01', 'Entrada', 'Mascarar dados pessoais identificáveis (PII); registrar canal e conteúdo do pedido — prioridade não é perguntada ao cliente.'],
              ['02', 'Risco', 'Fraude, senha, chargeback, legal e cancelamento vão direto à revisão — independente da confiança do modelo.'],
              ['03', 'Duplicata', 'Comparado por similaridade de texto (mesmo vetor do classificador) com os tickets abertos; acima de 60%, pausa a automação até o agente vincular ou descartar.'],
              ['04', 'Classificar', 'Categoria, confiança e três alternativas calculadas — nunca só um rótulo, sempre auditável.'],
              ['05', 'Decidir', `≥${pct(AUTO_REPLY_CONFIDENCE, 0)} de confiança + template aprovado → resposta automática; ≥${pct(m.confidence_threshold, 0)} → rascunho para aprovação; abaixo disso → revisão manual.`],
              ['06', 'Atender', 'Fila ordenada por prioridade e prazo; agente aprova, edita, assume ou encaminha — nunca a IA decide sozinha o envio.'],
              ['07', 'Fechar o ciclo', 'Cliente confirma a resolução ou reabre; CSAT coletado; correções e reaberturas alimentam o retreino mensal.'],
            ].map(([num, title, text]) => e('div', { key: num, className: 'step' }, e('b', null, num), e('h3', null, title), e('p', null, text)))
          ),
          e(
            'div',
            { className: 'action-grid' },
            e('div', { className: 'action-col do' }, e('h4', null, 'Automatizar agora'), e('div', { dangerouslySetInnerHTML: { __html: doListHtml(m) } })),
            e('div', { className: 'action-col dont' }, e('h4', null, 'Não automatizar'), e('div', { dangerouslySetInnerHTML: { __html: dontListHtml(m, diag) } }))
          ),
          e(
            'div',
            { style: { marginTop: '46px' } },
            e('p', { className: 'section-num', style: { marginBottom: '10px' } }, 'WINNOW · DEMONSTRAÇÃO AO VIVO'),
            e('h3', { style: { fontSize: '22px', letterSpacing: '-.03em', margin: '0 0 10px' } }, 'Winnow: do ticket recebido à decisão do agente'),
            e(
              'p',
              { className: 'section-copy', style: { gridColumn: 'auto', maxWidth: '640px' } },
              'Winnow separa o que a IA resolve sozinha do que precisa de julgamento humano — como uma peneira, não como um substituto do agente. Envie uma mensagem na parte superior e acompanhe sua entrada na fila abaixo. O classificador real roda no navegador; a resposta sugerida é um rascunho demonstrativo e exige aprovação humana.'
            )
          ),
          e(AgentWorkspace, { weights }),
          e(
            'div',
            { className: 'sim-foot' },
            e('table', { className: 'table', style: { marginTop: '10px' }, dangerouslySetInnerHTML: { __html: perClassTableHtml(m) } }),
            e('p', { style: { marginTop: '14px' } }, `Acurácia geral: ${pct(m.accuracy, 1)} · Macro F1: ${fmt(m.macro_f1, 3)} · Treino: ${m.train_rows.toLocaleString('pt-BR')} tickets · Teste: ${m.test_rows.toLocaleString('pt-BR')} tickets.`)
          ),
          e(
            'div',
            { style: { marginTop: '46px' } },
            e('p', { className: 'section-num', style: { marginBottom: '10px' } }, 'EXPERIMENTO REJEITADO'),
            e('h3', { style: { fontSize: '22px', letterSpacing: '-.03em', margin: '0 0 10px' } }, 'Tentamos outro modelo. Não valeu a troca.'),
            e(
              'p',
              { className: 'section-copy', style: { gridColumn: 'auto', maxWidth: '680px', marginBottom: '20px' } },
              `Hipótese testada: ${embExp.hypothesis} Resultado real, com o mesmo split e a mesma metodologia de avaliação do modelo em produção — não uma suposição.`
            ),
            e('table', { className: 'table', dangerouslySetInnerHTML: { __html: embExperimentTableHtml(embExp) } }),
            e('div', { className: 'callout', style: { marginTop: '20px' }, dangerouslySetInnerHTML: { __html: `<strong>Por que perdeu:</strong> ${embExp.conclusion}` } })
          )
        )
      ),

      // 06 ROI
      e(
        'section',
        { id: 'roi' },
        e(
          'div',
          { className: 'shell' },
          e(
            'div',
            { className: 'section-head' },
            e('p', { className: 'section-num' }, '06 · ROI'),
            e('h2', null, 'Uma estimativa de capacidade, ', e('span', null, 'com hipóteses para validar.')),
            e(
              'p',
              { className: 'section-copy' },
              'O cenário combina desempenho medido em TI com volume, tempos de trabalho e elegibilidade assumidos. Estima capacidade recuperável antes de implantação, manutenção e supervisão; não mede desperdício atual ou retorno financeiro. A triagem é uma oportunidade candidata, sem evidência de que seja a maior.'
            )
          ),
          e('div', { className: 'kpis', dangerouslySetInnerHTML: { __html: kpiRoiHtml(m, roi) } }),
          e('table', { className: 'table', style: { marginTop: '26px' }, dangerouslySetInnerHTML: { __html: roiTableHtml(roi) } }),
          e('h3', null, 'Sensibilidade às hipóteses — não são previsões'),
          e('table', { className: 'table', dangerouslySetInnerHTML: { __html: scenariosHtml(roi) } }),
          e('h3', null, 'O que medir no piloto'),
          e('ol', null, roi.pilot.map(item => e('li', { key: item }, item))),
          e('div', { className: 'callout', dangerouslySetInnerHTML: { __html: `<strong>Premissa não medida:</strong> ${roi.caveat}` } })
        )
      )
    ),

    e('footer', { className: 'shell footer' }, `SOBRE ESTE DIAGNÓSTICO`, e('br'), `Base operacional: ${dq.total_rows.toLocaleString('pt-BR')} tickets fornecidos · Métricas calculadas com ${dq.rows_valid_for_cycle_time.toLocaleString('pt-BR')} cronologias válidas · Classificador: 47.837 tickets IT rotulados, ${pct(m.accuracy, 1)} de acurácia · Cleiton Eugênio, 2026 — análise e protótipo com Claude Code.`)
  );
}

createRoot(document.getElementById('root')).render(e(App));
