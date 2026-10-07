const ui = {
  count: document.querySelector('#open-count'),
  results: document.querySelector('#results-count'),
  list: document.querySelector('#queue-list'),
  footer: document.querySelector('#queue-footer'),
  detail: document.querySelector('#detail-panel'),
  search: document.querySelector('#search'),
  seller: document.querySelector('#seller-filter'),
  manager: document.querySelector('#manager-filter'),
  office: document.querySelector('#office-filter'),
  announcer: document.querySelector('#workflow-announcer'),
  tabs: [...document.querySelectorAll('.stage-tab')],
  queueStart: document.querySelector('#queue-mode-start'),
  queueDialog: document.querySelector('#queue-dialog'),
  queueClose: document.querySelector('#queue-mode-close'),
  queueDetail: document.querySelector('#queue-mode-detail'),
  queueAnnouncer: document.querySelector('#queue-mode-announcer'),
};

const state = {
  opportunities: [],
  stage: 'all',
  seller: localStorage.getItem('foco-seller') || 'all',
  manager: localStorage.getItem('foco-manager') || 'all',
  office: localStorage.getItem('foco-office') || 'all',
  query: '',
  selectedId: null,
  pageSize: 8,
  lastNotes: {},
  activity: {},
  queueOrder: [],
  recentAccounts: {},
  callCapacityByAgent: {},
  today: '',
  actionsTodayByAgent: {},
  noteDrafts: {},
  sentimentDrafts: {},
  followUpDrafts: {},
  pendingActionIds: {},
  noteEditorOpen: false,
  reviewEditorOpen: false,
  queueMode: false,
  queueHandledIds: new Set(),
  queueActionCount: 0,
  builderCardVisible: false,
  builderCardShown: false,
  busy: false,
  error: '',
};

const number = new Intl.NumberFormat('pt-BR');
const decimal = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
const usd = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
const date = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC', day: '2-digit', month: 'short', year: 'numeric' });
const noteDate = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
const sessionId = sessionStorage.getItem('foco-session-id')
  || (window.crypto?.randomUUID?.() ?? `session-${Date.now()}-${Math.random().toString(36).slice(2)}`);
sessionStorage.setItem('foco-session-id', sessionId);

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
}

function stageName(stage) {
  return stage === 'Engaging' ? 'Em negociação' : 'Prospecção';
}

function accountName(item) {
  return item.account || 'Empresa não informada';
}

function formatDate(value) {
  return value ? date.format(new Date(`${value}T00:00:00Z`)) : 'Não registrada';
}

function formatSector(value) {
  const sectors = {
    technology: 'Tecnologia',
    software: 'Software',
    retail: 'Varejo',
    medical: 'Saúde',
    marketing: 'Marketing',
    finance: 'Finanças',
    services: 'Serviços',
    entertainment: 'Entretenimento',
    telecommunications: 'Telecomunicações',
  };
  return sectors[value] || value || 'Não informado';
}

function formatOffice(value) {
  return { Central: 'Centro', East: 'Leste', West: 'Oeste' }[value] || value || 'Não informado';
}

function nextStep(item) {
  const activity = state.activity[item.id];
  if (activity?.queue_section === 'review') {
    return { title: 'Definir o próximo passo', description: 'Revise a última interação antes de reagendar ou encerrar esta oportunidade.' };
  }
  if (activity?.queue_section === 'later') {
    return { title: 'Retorno agendado', description: `Próximo contato previsto para ${formatDate(activity.next_due_on)}.` };
  }
  if (activity?.last_action === 'no_answer') {
    return { title: 'Tentar novo contato', description: 'A última tentativa não teve resposta. Confira as observações antes de ligar.' };
  }
  if (item.stage === 'Engaging' && item.daysInEngaging > 138) {
    return {
      title: 'Revalidar a oportunidade',
      description: `Está em negociação há ${number.format(item.daysInEngaging)} dias. Confirme se o negócio continua ativo e registre o próximo passo.`,
    };
  }
  if (item.stage === 'Engaging' && item.daysInEngaging > 104) {
    return {
      title: 'Confirmar o andamento',
      description: `Está em negociação há ${number.format(item.daysInEngaging)} dias. Verifique a situação atual com o vendedor.`,
    };
  }
  if (!item.account) {
    return {
      title: 'Identificar a empresa',
      description: 'Confirme a empresa com o vendedor e registre o próximo passo comercial.',
    };
  }
  if (item.stage === 'Engaging') {
    return {
      title: 'Revisar a negociação',
      description: 'Confirme com o vendedor a situação atual e registre o próximo passo comercial.',
    };
  }
  return {
    title: 'Validar o primeiro contato',
    description: 'Confira se a conta já foi abordada e defina o próximo passo comercial.',
  };
}

function sortOpportunities(a, b) {
  if (a.priority_score !== b.priority_score) return b.priority_score - a.priority_score;
  if (a.engageDate !== b.engageDate) return (b.engageDate || '').localeCompare(a.engageDate || '');
  return a.id.localeCompare(b.id);
}

function filteredOpportunities() {
  const query = state.query.trim().toLocaleLowerCase('pt-BR');
  return state.opportunities.filter((item) => {
    if (state.stage !== 'all' && item.stage !== state.stage) return false;
    if (state.seller !== 'all' && item.agent !== state.seller) return false;
    if (state.manager !== 'all' && item.manager !== state.manager) return false;
    if (state.office !== 'all' && item.office !== state.office) return false;
    if (!query) return true;
    return [item.account, item.product, item.id, item.agent, item.manager, item.office, item.sector]
      .some((value) => String(value || '').toLocaleLowerCase('pt-BR').includes(query));
  });
}

function queuePlan() {
  const allowed = new Map(filteredOpportunities().map((item) => [item.id, item]));
  const items = state.queueOrder.map((id) => allowed.get(id)).filter(Boolean);
  const activeCount = items.filter((item) => state.activity[item.id]?.queue_section !== 'later').length;
  return { items, activeCount };
}

function renderRow(item) {
  const title = escapeHtml(accountName(item));
  const activity = state.activity[item.id];
  const timing = activity?.queue_section === 'review'
    ? '<span class="row-return">Revisar</span>'
    : activity?.queue_section === 'later'
      ? `<span class="row-later">Agendado ${escapeHtml(formatDate(activity.next_due_on))}</span>`
      : activity?.last_action
        ? '<span class="row-return">Retorno</span>'
        : '';
  const subtitle = `${escapeHtml(item.product)} <span aria-hidden="true">/</span> ${escapeHtml(item.id)} ${timing}`;
  const selected = item.id === state.selectedId;
  return `<button type="button" class="opportunity-row ${selected ? 'is-selected' : ''}" data-id="${escapeHtml(item.id)}" aria-pressed="${selected}" aria-label="${title}, ${escapeHtml(item.product)}, Priority Score ${item.priority_score}, ${stageName(item.stage)}">
    <span class="row-main"><span class="row-title">${title}</span><span class="row-subtitle">${subtitle}</span></span>
    <span class="row-side"><span class="row-stage ${item.stage === 'Prospecting' ? 'is-prospecting' : ''}"><span class="row-score">${item.priority_score}</span><span class="row-separator" aria-hidden="true">·</span>${stageName(item.stage)}</span><span class="row-owner">${escapeHtml(item.agent)}</span></span>
  </button>`;
}

function sentimentButton(value, label, mouth, itemId, disabled) {
  const active = state.sentimentDrafts[itemId] === value;
  return `<button type="button" class="sentiment-button sentiment-${value} ${active ? 'is-selected' : ''}" data-sentiment="${value}" aria-label="${label}" title="${label}" aria-pressed="${active}" ${disabled}>
    <svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="9"></circle><path d="M9 9h.01M15 9h.01" stroke-width="2.6"></path><path d="${mouth}"></path>
    </svg>
  </button>`;
}

function activeDetail() {
  return state.queueMode ? ui.queueDetail : ui.detail;
}

function builderCardMarkup() {
  return `<article class="builder-card" aria-labelledby="builder-card-title">
    <div class="builder-card-mark" aria-hidden="true">p<span>l.</span></div>
    <p class="builder-card-eyebrow">Uma pausa rápida na fila</p>
    <h3 id="builder-card-title">Paulo Lanzilotti</h3>
    <p class="builder-card-role">Product &amp; AI Technology Leader</p>
    <p class="builder-card-proposition">I turn complex operations into AI-enabled products that create measurable commercial outcomes.</p>
    <div class="builder-card-tags" aria-label="Áreas de atuação"><span>Product strategy</span><span>AI</span><span>Marketing</span></div>
    <p class="builder-card-projects">Ford · Neuron · JEM · The Flooring Empire · RefurbHub</p>
    <div class="builder-card-actions"><a class="builder-card-portfolio" href="https://portfolio.lanzilotti.com.br/" target="_blank" rel="noopener noreferrer">Explore my journey <span aria-hidden="true">↗</span></a><button type="button" class="builder-card-continue" data-builder-continue>Continue to the queue</button></div>
  </article>`;
}

function actionIcon(kind) {
  const paths = {
    no_answer: '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.8 2.1Z"/><path d="m16 2 6 6m0-6-6 6"/>',
    skip: '<path d="m5 4 11 8-11 8Z"/><path d="M19 4v16"/>',
    contacted: '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.8 2.1Z"/><path d="m16 5 2 2 4-5"/>',
  };
  return `<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[kind]}</svg>`;
}

function renderDetail(item) {
  const target = activeDetail();
  ui.queueClose.disabled = state.busy;
  if (state.queueMode && state.builderCardVisible) {
    target.innerHTML = builderCardMarkup();
    return;
  }
  if (state.queueMode && state.seller === 'all') {
    target.innerHTML = `<div class="queue-intro"><h3 tabindex="-1" class="queue-client-title">Qual é a sua carteira?</h3><p>Escolha o vendedor para começar de onde a fila parou.</p>
      <form id="queue-seller-form"><label for="queue-seller">Vendedor responsável</label><select id="queue-seller" name="seller" required><option value="">Selecionar vendedor</option>${[...new Set(state.opportunities.map(item => item.agent))].sort((a,b) => a.localeCompare(b, 'pt-BR')).map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('')}</select><button type="submit" class="composer-save">Começar</button></form></div>`;
    return;
  }
  if (!item) {
    target.innerHTML = state.queueMode
      ? '<div class="queue-intro"><h3 tabindex="-1" class="queue-client-title">Sem próximas ações neste filtro.</h3><p>Você pode consultar a carteira para revisar pendências e agendamentos. Os retornos ficam disponíveis na data marcada.</p><button type="button" class="composer-save" data-exit-queue>Voltar à carteira</button></div>'
      : '<div class="detail-placeholder">Selecione uma oportunidade para ver o contexto.</div>';
    return;
  }
  const step = nextStep(item);
  const facts = [
    ['Produto', item.product],
    ['Preço de tabela', item.listPrice == null ? 'Não informado' : usd.format(item.listPrice)],
    ['Vendedor', item.agent],
    ['Escritório', formatOffice(item.office)],
    ['Setor', formatSector(item.sector)],
    ['Início da negociação', formatDate(item.engageDate)],
  ];
  const context = item.account
    ? 'A empresa está vinculada ao negócio. O dataset não traz histórico de atividades nem valor negociado para oportunidades abertas.'
    : 'A empresa ainda não foi informada no CRM. O dataset também não traz histórico de atividades nem valor negociado para oportunidades abertas.';
  const components = item.score_components;
  const confidence = item.score_confidence === 'limited' ? 'Limitada: conta não vinculada' : 'Parcial: sem histórico de atividades';
  const momentumWhy = item.stage === 'Engaging'
    ? `Em negociação há ${number.format(item.daysInEngaging || 0)} dias no snapshot histórico.`
    : 'Oportunidade ainda em prospecção.';
  const valueWhy = item.listPrice == null
    ? 'Preço de tabela indisponível.'
    : `Preço de tabela ${usd.format(item.listPrice)}; valor negociado não está disponível.`;
  const fitWhy = item.account
    ? `Combinação de setor e produto, com porte da empresa como sinal secundário. Setor: ${formatSector(item.sector)}.`
    : 'Sem conta vinculada; a parcela usa um valor neutro.';
  const historyWhy = item.account
    ? 'Histórico de negócios fechados da conta, suavizado para evitar amostras pequenas.'
    : 'Sem conta vinculada; a parcela usa um valor neutro.';
  const lastNote = state.lastNotes[item.id];
  const noteText = lastNote
    ? `<p class="last-note-text">${escapeHtml(lastNote.text)}</p><time class="last-note-date" datetime="${escapeHtml(lastNote.at)}">${noteDate.format(new Date(lastNote.at))}</time>`
    : '<p class="last-note-empty">Nenhuma observação registrada.</p>';
  const disabled = state.busy ? 'disabled' : '';
  const canAct = state.seller === item.agent;
  const accountActivity = item.account ? state.recentAccounts[item.account] : null;
  const accountWarning = accountActivity && accountActivity.opportunity_id !== item.id
    ? `<p class="account-warning">Esta empresa teve uma tentativa recente com ${escapeHtml(accountActivity.agent)} em ${escapeHtml(noteDate.format(new Date(accountActivity.at)))}. Confira antes de ligar.</p>`
    : '';
  const sentiment = state.sentimentDrafts[item.id];
  const dueInput = sentiment && sentiment !== 'negative'
    ? `<label class="follow-up-label" for="follow-up-on">Próximo contato <span>(opcional)</span></label>
       <input id="follow-up-on" name="follow_up_on" type="date" min="${escapeHtml(state.today)}" value="${escapeHtml(state.followUpDrafts[item.id] || '')}" ${disabled}>`
    : '';
  const actionContent = !canAct
    ? '<p class="workflow-hint">Selecione o vendedor responsável para registrar uma ação.</p>'
    : state.reviewEditorOpen
      ? `<form class="review-composer" id="review-form">
           <label for="review-date">Data do próximo contato</label>
           <input id="review-date" name="follow_up_on" type="date" min="${escapeHtml(state.today)}" required value="${escapeHtml(state.followUpDrafts[item.id] || '')}" ${disabled}>
           <div class="composer-buttons"><button type="button" class="composer-cancel" data-cancel-review ${disabled}>Cancelar</button><button type="submit" class="composer-save" ${disabled}>Reagendar</button></div>
         </form>`
    : state.activity[item.id]?.queue_section === 'review'
      ? `<div class="workflow-actions" role="group" aria-label="Resolver revisão">
           <button type="button" class="action-button action-contacted" data-action="reopen" ${disabled}>Reagendar</button>
           <button type="button" class="action-button action-no-answer" data-action="close" ${disabled}>Encerrar</button>
         </div>`
    : state.activity[item.id]?.queue_section === 'later'
      ? `<div class="workflow-actions" role="group" aria-label="Alterar retorno">
           <button type="button" class="action-button action-no-answer" data-action="reopen" ${disabled}>Alterar data</button>
         </div>`
    : state.noteEditorOpen
    ? `<form class="note-composer" id="contact-note-form">
         <label for="call-note">Observação da conversa</label>
         <div class="note-entry-row">
           <textarea id="call-note" name="note" rows="3" maxlength="1000" required placeholder="O que foi conversado e qual é o próximo passo?" ${disabled}>${escapeHtml(state.noteDrafts[item.id] || '')}</textarea>
           <div class="sentiment-stack" role="group" aria-label="Resultado da conversa">
             ${sentimentButton('positive', 'Positivo', 'M8 14c1.1 1.5 2.4 2.2 4 2.2s2.9-.7 4-2.2', item.id, disabled)}
             ${sentimentButton('neutral', 'Neutro', 'M8.5 15h7', item.id, disabled)}
             ${sentimentButton('negative', 'Negativo', 'M8 16c1.1-1.5 2.4-2.2 4-2.2s2.9.7 4 2.2', item.id, disabled)}
           </div>
         </div>
         ${dueInput}
         <div class="composer-footer"><span>Até 1.000 caracteres</span><div class="composer-buttons"><button type="button" class="composer-cancel" data-cancel-note ${disabled}>Cancelar</button><button type="submit" class="composer-save" ${disabled}>Salvar e avançar</button></div></div>
       </form>`
    : `<div class="workflow-actions" role="group" aria-label="Registrar atendimento">
         <button type="button" class="action-button action-contacted" data-action="contacted" ${disabled}>Contactado</button>
         <button type="button" class="action-button action-no-answer" data-action="no_answer" ${disabled}>No Answer</button>
         <button type="button" class="action-button action-skip" data-action="skip" ${disabled}>Pular <span aria-hidden="true">→</span></button>
       </div>`;
  if (state.queueMode) {
    const section = state.activity[item.id]?.queue_section;
    const queueActions = !state.noteEditorOpen && !state.reviewEditorOpen && section !== 'review' && section !== 'later'
      ? `<div class="queue-call-actions" role="group" aria-label="Registrar atendimento">${[['no_answer','No Answer'],['skip','Pular'],['contacted','Contactado']].map(([action,label]) => `<button type="button" class="queue-call-button queue-call-${action}" data-action="${action}" ${disabled}>${actionIcon(action)}<span>${label}</span></button>`).join('')}</div>`
      : actionContent;
    const queueFacts = [['Setor', formatSector(item.sector)], ['Preço de tabela', item.listPrice == null ? 'Não informado' : usd.format(item.listPrice)], ['Vendedor', item.agent], ['Telefone', 'Não informado']];
    target.innerHTML = `<div class="queue-client-heading"><div><h3 class="detail-title queue-client-title" tabindex="-1">${escapeHtml(accountName(item))}</h3><p class="detail-subtitle">${escapeHtml(item.product)} · ${stageName(item.stage)}</p></div><div class="score-readout"><span>Priority Score</span><strong>${number.format(item.priority_score)}</strong></div></div>
      <dl class="detail-facts queue-facts">${queueFacts.map(([label,value]) => `<div class="fact"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join('')}</dl>
      <section class="last-note queue-last-note"><h3>Últimas observações</h3>${noteText}</section>
      ${accountWarning}
      ${section === 'review' ? `<p class="workflow-hint">${escapeHtml(step.description)}</p>` : ''}
      <div class="queue-interaction" aria-busy="${state.busy}">${queueActions}${state.busy ? '<p class="queue-saving" role="status">Salvando…</p>' : ''}${state.error ? `<p class="workflow-error" role="alert">${escapeHtml(state.error)}</p>` : ''}</div>`;
    return;
  }
  target.innerHTML = `
    <div class="detail-topline"><span class="detail-label">Oportunidade ${escapeHtml(item.id)}</span><span class="score-readout"><span>Priority Score</span><strong>${number.format(item.priority_score)}</strong></span></div>
    <h2 class="detail-title">${escapeHtml(accountName(item))}</h2>
    <p class="detail-subtitle">${escapeHtml(item.product)} <span aria-hidden="true">/</span> ${stageName(item.stage)}</p>
    <section class="last-note"><h3>Últimas observações</h3>${noteText}</section>
    <div class="detail-divider"></div>
    <p class="next-step-label">Próximo passo sugerido</p>
    <h3 class="next-step">${escapeHtml(step.title)}</h3>
    <p class="next-step-copy">${escapeHtml(step.description)}</p>
    ${accountWarning}
    ${actionContent}
    ${state.error ? `<p class="workflow-error" role="alert">${escapeHtml(state.error)}</p>` : ''}
    <div class="detail-divider"></div>
    <h3 class="context-heading">Contexto</h3>
    <dl class="detail-facts">${facts.map(([label, value]) => `<div class="fact"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join('')}</dl>
    <details class="context-note"><summary>Como foi priorizada</summary><dl class="score-reasons">
      <div><dt>Momento · ${decimal.format(components.momentum)}/60</dt><dd>${escapeHtml(momentumWhy)}</dd></div>
      <div><dt>Valor · ${decimal.format(components.value)}/25</dt><dd>${escapeHtml(valueWhy)}</dd></div>
      <div><dt>Fit · ${decimal.format(components.fit)}/10</dt><dd>${escapeHtml(fitWhy)}</dd></div>
      <div><dt>Histórico · ${decimal.format(components.history)}/5</dt><dd>${escapeHtml(historyWhy)}</dd></div>
    </dl><p>Confiança: ${escapeHtml(confidence)}. ${escapeHtml(context)}</p></details>`;
}

function render() {
  const { items: matches, activeCount } = queuePlan();
  const selectable = state.queueMode ? matches.filter(item => state.activity[item.id]?.queue_section !== 'later' && !state.queueHandledIds.has(item.id)) : matches;
  if (!selectable.some((item) => item.id === state.selectedId)) {
    state.selectedId = activeCount ? selectable[0]?.id ?? null : null;
  }
  ui.count.textContent = `${number.format(state.queueOrder.length)} oportunidades em aberto`;
  ui.results.textContent = `${number.format(matches.length)} resultados`;
  ui.list.setAttribute('aria-busy', 'false');

  if (!matches.length) {
    ui.list.innerHTML = '<div class="empty-state"><h3>Nenhuma oportunidade encontrada</h3><p>Tente outro termo ou ajuste os filtros.</p></div>';
    ui.footer.innerHTML = '';
    renderDetail(null);
    return;
  }

  const selectedIndex = matches.findIndex((item) => item.id === state.selectedId);
  const pageStart = Math.floor(Math.max(selectedIndex, 0) / state.pageSize) * state.pageSize;
  const pageEnd = Math.min(pageStart + state.pageSize, matches.length);
  ui.list.innerHTML = matches.slice(pageStart, pageEnd).map(renderRow).join('');
  ui.footer.innerHTML = matches.length > state.pageSize
    ? `<button type="button" class="page-button" data-page="previous" ${pageStart === 0 ? 'disabled' : ''}>Anterior</button>
       <span class="page-position">${number.format(pageStart + 1)}–${number.format(pageEnd)} de ${number.format(matches.length)}</span>
       <button type="button" class="page-button" data-page="next" ${pageEnd === matches.length ? 'disabled' : ''}>Próximos</button>`
    : '';
  renderDetail(matches.find((item) => item.id === state.selectedId));
  if (!state.selectedId && !activeCount) {
    ui.detail.innerHTML = '<div class="detail-placeholder"><strong>Fila em dia.</strong><br>Os próximos retornos aparecem aqui na data agendada.</div>';
  }
}

function populateSellers() {
  const names = [...new Set(state.opportunities.map((item) => item.agent))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
  ui.seller.innerHTML = `<option value="all">Todos os vendedores</option>${names.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('')}`;
  if (names.includes(state.seller)) ui.seller.value = state.seller;
  else {
    state.seller = 'all';
    localStorage.removeItem('foco-seller');
  }
  const managers = [...new Set(state.opportunities.map((item) => item.manager).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
  ui.manager.innerHTML = `<option value="all">Todos os managers</option>${managers.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('')}`;
  if (managers.includes(state.manager)) ui.manager.value = state.manager;
  else { state.manager = 'all'; localStorage.removeItem('foco-manager'); }
  const offices = [...new Set(state.opportunities.map((item) => item.office).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
  ui.office.innerHTML = `<option value="all">Todas as regiões</option>${offices.map((office) => `<option value="${escapeHtml(office)}">${escapeHtml(formatOffice(office))}</option>`).join('')}`;
  if (offices.includes(state.office)) ui.office.value = state.office;
  else { state.office = 'all'; localStorage.removeItem('foco-office'); }
}

function applySavedState(savedState) {
  state.lastNotes = savedState.lastNotes || {};
  state.activity = savedState.activity || {};
  state.queueOrder = savedState.queueOrder || [];
  state.recentAccounts = savedState.recentAccounts || {};
  state.callCapacityByAgent = savedState.callCapacityByAgent || {};
  state.today = savedState.today || '';
  state.actionsTodayByAgent = savedState.actionsTodayByAgent || {};
}

async function refreshState() {
  const response = await fetch('./api/state');
  if (!response.ok) throw new Error('Não foi possível atualizar a fila');
  applySavedState(await response.json());
}

async function loadData() {
  ui.list.setAttribute('aria-busy', 'true');
  try {
    const [dataResponse, stateResponse] = await Promise.all([
      fetch('./data.json'),
      fetch('./api/state'),
    ]);
    if (!dataResponse.ok || !stateResponse.ok) throw new Error('Dados ou servidor de interações indisponíveis');
    const [data, savedState] = await Promise.all([dataResponse.json(), stateResponse.json()]);
    if (!Array.isArray(data)) throw new Error('Formato de dados inválido');
    applySavedState(savedState);
    state.opportunities = data.sort(sortOpportunities);
    state.selectedId = null;
    populateSellers();
    ui.queueStart.disabled = false;
    render();
  } catch (error) {
    ui.count.textContent = 'Dados indisponíveis';
    ui.results.textContent = '';
    ui.list.setAttribute('aria-busy', 'false');
    ui.list.innerHTML = '<div class="error-state"><h3>Não foi possível carregar a carteira</h3><p>Inicie com python3 server.py e tente novamente.</p><button type="button" class="retry-button" id="retry">Tentar de novo</button></div>';
    ui.footer.innerHTML = '';
    renderDetail(null);
    console.error('Falha ao carregar dados:', error);
  }
}

function selectOpportunity(id) {
  state.selectedId = id;
  state.noteEditorOpen = false;
  state.reviewEditorOpen = false;
  state.error = '';
  render();
}

function resetSelection() {
  selectOpportunity(null);
}

function currentOpportunity() {
  return state.opportunities.find((item) => item.id === state.selectedId);
}

async function recordInteraction(action, note = null, sentiment = null, followUpOn = null) {
  if (state.busy) return;
  const item = currentOpportunity();
  if (!item) return;
  if (state.seller !== item.agent) return;
  const actionKey = `${item.id}:${action}`;
  const clientActionId = state.pendingActionIds[actionKey]
    || (window.crypto?.randomUUID?.() ?? `action-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  state.pendingActionIds[actionKey] = clientActionId;
  state.busy = true;
  state.error = '';
  renderDetail(item);

  try {
    const response = await fetch('./api/interactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        opportunity_id: item.id, action, note, sentiment, follow_up_on: followUpOn,
        actor_id: state.seller, expected_version: state.activity[item.id]?.version ?? 0,
        client_action_id: clientActionId, session_id: sessionId
      }),
    });
    const result = await response.json();
    if (!response.ok) {
      const error = new Error(result.error || 'Não foi possível salvar a interação');
      error.status = response.status;
      throw error;
    }
    await refreshState();
    delete state.pendingActionIds[actionKey];
    if (state.queueMode) {
      state.queueHandledIds.add(item.id);
      if (['skip', 'no_answer', 'contacted'].includes(action)) {
        state.queueActionCount += 1;
        if (state.queueActionCount === 5 && !state.builderCardShown) {
          state.builderCardVisible = true;
          state.builderCardShown = true;
        }
      }
    }
    if (action === 'contacted') {
      delete state.noteDrafts[item.id];
      delete state.sentimentDrafts[item.id];
      delete state.followUpDrafts[item.id];
    }
    if (action === 'reopen') delete state.followUpDrafts[item.id];
    state.busy = false;
    state.noteEditorOpen = false;
    state.reviewEditorOpen = false;
    state.selectedId = null;
    state.error = '';
    render();
    const next = currentOpportunity();
    const label = {
      skip: 'Oportunidade pulada', contacted: 'Contato registrado',
      no_answer: 'Sem resposta registrado', reopen: 'Retorno agendado', close: 'Oportunidade encerrada'
    }[action];
    ui.queueAnnouncer.textContent = ui.announcer.textContent = next
      ? `${label}. Próxima oportunidade: ${accountName(next)}.`
      : `${label}. Fila em dia neste filtro.`;
    if (state.queueMode) ui.queueDetail.querySelector('.queue-client-title')?.focus();
  } catch (error) {
    state.busy = false;
    if (error.status === 409) {
      delete state.pendingActionIds[actionKey];
      try { await refreshState(); } catch (_) { /* O erro original permanece visível. */ }
    }
    state.error = error.message || 'Não foi possível salvar a interação';
    render();
  }
}

ui.tabs.forEach((tab) => tab.addEventListener('click', () => {
  state.stage = tab.dataset.stage;
  ui.tabs.forEach((button) => {
    const active = button === tab;
    button.classList.toggle('is-active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  resetSelection();
}));

ui.search.addEventListener('input', () => {
  state.query = ui.search.value;
  resetSelection();
});

ui.seller.addEventListener('change', () => {
  state.seller = ui.seller.value;
  localStorage.setItem('foco-seller', state.seller);
  resetSelection();
});

ui.manager.addEventListener('change', () => {
  state.manager = ui.manager.value;
  localStorage.setItem('foco-manager', state.manager);
  resetSelection();
});

ui.office.addEventListener('change', () => {
  state.office = ui.office.value;
  localStorage.setItem('foco-office', state.office);
  resetSelection();
});

ui.list.addEventListener('click', (event) => {
  const row = event.target.closest('.opportunity-row');
  if (!row) return;
  selectOpportunity(row.dataset.id);
  if (window.matchMedia('(max-width: 900px)').matches) ui.detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

ui.footer.addEventListener('click', (event) => {
  const control = event.target.closest('[data-page]');
  if (!control || control.disabled) return;
  const matches = queuePlan().items;
  const currentIndex = matches.findIndex((item) => item.id === state.selectedId);
  const start = Math.floor(Math.max(currentIndex, 0) / state.pageSize) * state.pageSize;
  const nextStart = control.dataset.page === 'next'
    ? Math.min(start + state.pageSize, matches.length - 1)
    : Math.max(start - state.pageSize, 0);
  selectOpportunity(matches[nextStart].id);
});

function handleDetailClick(event) {
  if (state.busy) return;
  if (event.target.closest('[data-builder-continue]')) {
    state.builderCardVisible = false;
    state.error = '';
    render();
    ui.queueDetail.querySelector('.queue-client-title')?.focus();
    return;
  }
  if (event.target.closest('[data-exit-queue]')) { closeQueueMode(); return; }
  const sentiment = event.target.closest('[data-sentiment]')?.dataset.sentiment;
  if (sentiment) {
    state.sentimentDrafts[state.selectedId] = sentiment;
    if (sentiment === 'negative') delete state.followUpDrafts[state.selectedId];
    state.error = '';
    renderDetail(currentOpportunity());
    activeDetail().querySelector(`[data-sentiment="${sentiment}"]`)?.focus();
    return;
  }
  const action = event.target.closest('[data-action]')?.dataset.action;
  if (action === 'contacted') {
    state.noteEditorOpen = true;
    state.error = '';
    renderDetail(currentOpportunity());
    activeDetail().querySelector('#call-note')?.focus();
  } else if (action === 'reopen') {
    state.reviewEditorOpen = true;
    state.error = '';
    renderDetail(currentOpportunity());
    activeDetail().querySelector('#review-date')?.focus();
  } else if (action === 'close') {
    recordInteraction('close');
  } else if (action === 'skip' || action === 'no_answer') {
    recordInteraction(action);
  } else if (event.target.closest('[data-cancel-note]')) {
    delete state.noteDrafts[state.selectedId];
    delete state.sentimentDrafts[state.selectedId];
    delete state.followUpDrafts[state.selectedId];
    state.noteEditorOpen = false;
    state.error = '';
    renderDetail(currentOpportunity());
  } else if (event.target.closest('[data-cancel-review]')) {
    delete state.followUpDrafts[state.selectedId];
    state.reviewEditorOpen = false;
    state.error = '';
    renderDetail(currentOpportunity());
  }
}

function handleDetailInput(event) {
  if (event.target.id === 'call-note') state.noteDrafts[state.selectedId] = event.target.value;
  if (event.target.id === 'follow-up-on' || event.target.id === 'review-date') {
    state.followUpDrafts[state.selectedId] = event.target.value;
  }
}

function handleDetailSubmit(event) {
  if (event.target.id === 'queue-seller-form') {
    event.preventDefault();
    state.seller = event.target.elements.seller.value;
    ui.seller.value = state.seller;
    localStorage.setItem('foco-seller', state.seller);
    resetSelection();
    ui.queueDetail.querySelector('.queue-client-title')?.focus();
    return;
  }
  if (event.target.id === 'review-form') {
    event.preventDefault();
    const followUpOn = event.target.elements.follow_up_on.value;
    if (followUpOn) recordInteraction('reopen', null, null, followUpOn);
    return;
  }
  if (event.target.id !== 'contact-note-form') return;
  event.preventDefault();
  const note = event.target.elements.note.value.trim();
  state.noteDrafts[state.selectedId] = note;
  if (!note) {
    state.error = 'Escreva uma observação antes de avançar.';
    renderDetail(currentOpportunity());
    activeDetail().querySelector('#call-note')?.focus();
    return;
  }
  const sentiment = state.sentimentDrafts[state.selectedId];
  if (!sentiment) {
    state.error = 'Selecione o resultado da conversa.';
    renderDetail(currentOpportunity());
    activeDetail().querySelector('[data-sentiment]')?.focus();
    return;
  }
  recordInteraction('contacted', note, sentiment,
    sentiment === 'negative' ? null : state.followUpDrafts[state.selectedId] || null);
}

ui.list.addEventListener('click', (event) => {
  if (event.target.closest('#retry')) loadData();
});

for (const panel of [ui.detail, ui.queueDetail]) {
  panel.addEventListener('click', handleDetailClick);
  panel.addEventListener('input', handleDetailInput);
  panel.addEventListener('submit', handleDetailSubmit);
}

function closeQueueMode() {
  if (state.busy) return;
  ui.queueDialog.close();
}

ui.queueStart.addEventListener('click', () => {
  if (state.busy) return;
  // Keep the background in its normal read state; drafts remain associated with their opportunity.
  state.noteEditorOpen = false;
  state.reviewEditorOpen = false;
  render();
  state.queueMode = true;
  state.queueHandledIds.clear();
  state.queueActionCount = 0;
  state.builderCardVisible = false;
  ui.queueAnnouncer.textContent = '';
  state.selectedId = null;
  state.error = '';
  render();
  document.body.classList.add('queue-mode-open');
  ui.queueDialog.showModal();
  ui.queueDetail.querySelector('#queue-seller, .queue-client-title')?.focus();
});
ui.queueClose.addEventListener('click', closeQueueMode);
ui.queueDialog.addEventListener('cancel', event => {
  if (state.busy) event.preventDefault();
});
ui.queueDialog.addEventListener('close', () => {
  state.queueMode = false;
  state.noteEditorOpen = false;
  state.reviewEditorOpen = false;
  document.body.classList.remove('queue-mode-open');
  ui.queueDetail.innerHTML = '';
  render();
  ui.queueStart.focus();
});

document.addEventListener('visibilitychange', async () => {
  if (document.hidden || state.busy || state.noteEditorOpen || state.reviewEditorOpen || !state.opportunities.length) return;
  try {
    await refreshState();
    render();
  } catch (error) {
    console.error('Falha ao atualizar fila:', error);
  }
});

loadData();
