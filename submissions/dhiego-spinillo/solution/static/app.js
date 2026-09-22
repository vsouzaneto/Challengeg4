'use strict';
const $ = id => document.getElementById(id);
const pct = value => value == null ? 'Não atingido' : (100 * value).toLocaleString('pt-BR', {maximumFractionDigits: 2}) + '%';
const num = value => Number(value).toLocaleString('pt-BR', {maximumFractionDigits: 2});
const labels = ['Hardware','HR Support','Access','Miscellaneous','Storage','Purchase','Internal Project','Administrative rights'];
let examples = [], activeAnalysis = null, revision = 0;
function node(tag, text, className) { const n = document.createElement(tag); if (text != null) n.textContent = text; if (className) n.className = className; return n; }
function status(id, text, error = false) { $(id).textContent = text; $(id).classList.toggle('error', error); }
async function getJSON(url, options) { const response = await fetch(url, options); if (!response.ok) { if(response.status === 422) throw new Error('Confira o tamanho do texto, a categoria e o motivo informado.'); throw new Error('Não foi possível concluir ('+response.status+'). Tente novamente ou revise manualmente.'); } return response.json(); }
function invalidate() { revision++; activeAnalysis = null; $('result').hidden = true; $('empty-state').hidden = false; $('input-count').textContent = num($('ticket-text').value.length) + ' caracteres'; status('analysis-status',''); status('review-status',''); }
$('ticket-text').addEventListener('input', invalidate); $('domain-confirmed').addEventListener('change', invalidate); $('include-recap').addEventListener('change', invalidate);
$('example-select').addEventListener('change', () => { const item = examples[Number($('example-select').value)]; if ($('example-select').value === '' || !item) return; $('ticket-text').value = item.text; $('domain-confirmed').checked = true; $('example-note').textContent = 'D2 · registro '+num(item.row)+' · exemplo do treino. A categoria da base fica disponível após analisar; este exemplo não mede desempenho.'; invalidate(); });
for (const label of labels) { const option = node('option',label); option.value = label; $('review-category').append(option); }

function renderRecap(data) {
  const target = $('recap-content'); target.replaceChildren();
  $('recap-model').textContent = data.recap?.model ? 'Gerado nesta análise' : '';
  if (!data.recap) { target.append(node('p', data.recap_error || 'Recap experimental não solicitado. A classificação e a revisão manual continuam disponíveis.', 'recap-notice')); return; }
  const kindNames = {pedido:'Pedido',tentativa:'Tentativa relatada',pendencia:'Ponto em aberto'};
  for (const item of data.recap.items) {
    const section = node('article',null,'recap-item'); section.append(node('span',kindNames[item.kind] || item.kind,'small-label'),node('p',item.text));
    const button = node('button','Destacar no texto original ↗','quote-button'); button.type = 'button';
    button.addEventListener('click', () => { const text = $('ticket-text'); const start = text.value.indexOf(item.quote); if(start >= 0) { text.focus(); text.setSelectionRange(start, start + item.quote.length); text.scrollIntoView({block:'center',behavior:'smooth'}); } });
    section.append(button,node('blockquote',item.quote)); target.append(section);
  }
  if (data.recap.unknowns.length) { const box = node('div',null,'unknowns'); box.append(node('h3','O que ainda não sabemos')); const list = node('ul'); for (const item of data.recap.unknowns) list.append(node('li',item)); box.append(list); target.append(box); }
  const next = node('div',null,'next-step'); next.append(node('h3','Próximo passo sugerido'),node('p',data.recap.next_step)); target.append(next);
}
function renderResult(data) {
  const example = examples.find(item => item.text.trim() === data.text.trim());
  if (example) $('example-note').textContent = 'D2 · registro '+num(example.row)+' · rótulo da base: '+example.dataset_label+'. Exemplo do treino; não é avaliação de desempenho.';
  $('empty-state').hidden = true; $('result').hidden = false; $('classification-title').textContent = data.prediction;
  $('score-text').textContent = 'Score do modelo: '+pct(data.score); $('latency-text').textContent = 'Classificação local · '+num(data.elapsed_ms)+' ms';
  $('queue-text').textContent = data.policy.queue; $('policy-reason').textContent = data.policy.reason;
  const list = $('probabilities'); list.replaceChildren();
  for (const [label,value] of Object.entries(data.probabilities).sort((a,b)=>b[1]-a[1])) { const row = node('div',null,'probability-row'); const track = node('div',null,'bar-track'), fill = node('div',null,'bar-fill'); fill.style.width = (value*100)+'%'; track.append(fill); row.append(node('span',label),track,node('span',pct(value))); list.append(row); }
  renderRecap(data); $('review-category').value = data.prediction; $('review-reason').value = ''; status('review-status',''); $('review-button').disabled = false;
}
$('analyze-form').addEventListener('submit', async event => {
  event.preventDefault(); const button = $('analyze-button'); if(button.disabled)return;
  const text = $('ticket-text').value.trim(); if(text.length < 10) { status('analysis-status','Inclua pelo menos 10 caracteres para analisar.',true); return; }
  const submittedRevision = revision; activeAnalysis = null; $('result').hidden=true; $('empty-state').hidden=false; button.disabled = true;
  status('analysis-status',$('include-recap').checked ? 'Classificando e preparando o recap. A revisão continua sendo sua.' : 'Classificando o texto…');
  try { const data = await getJSON('/api/analyze', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,domain_confirmed:$('domain-confirmed').checked,include_recap:$('include-recap').checked})});
    if(revision !== submittedRevision) { status('analysis-status','O texto ou as opções mudaram. Analise novamente para atualizar.'); return; }
    activeAnalysis=data;renderResult(data);status('analysis-status','Análise pronta. Confira o contexto e registre sua decisão.');
    if(window.innerWidth < 741) $('result').scrollIntoView({block:'start',behavior:'smooth'});
  } catch(error) {status('analysis-status',error.message,true);} finally {button.disabled=false;}
});
$('review-form').addEventListener('submit', async event => { event.preventDefault(); if(!activeAnalysis)return; const button=$('review-button');button.disabled=true;
  try {await getJSON('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({analysis_id:activeAnalysis.analysis_id,category:$('review-category').value,reason:$('review-reason').value.trim()})});status('review-status','Decisão registrada com seu motivo. Nenhuma ação foi executada no atendimento.');}
  catch(error){status('review-status',error.message,true);}finally{button.disabled=false;}
});

function renderEvidence(data) {
  const a=data.systems.tfidf_logistic.test,b=data.systems.jev.test;
  const rows=[['Acerto na categoria',pct(a.accuracy_including_api_errors),pct(b.accuracy_including_api_errors)],['F1 médio entre as oito categorias',num(a.macro_f1),num(b.macro_f1)],['Tickets de teste',num(a.n),num(b.n)],['Tempo por ticket · mediana',num(a.latency_ms.p50)+' ms',num(b.latency_ms.p50)+' ms'],['Limiar encontrado na validação',a.threshold_from_validation == null?'Nenhum':num(a.threshold_from_validation),b.threshold_from_validation == null?'Nenhum':num(b.threshold_from_validation)],['Acerto no grupo selecionado pelo limiar',pct(a.accepted_accuracy),pct(b.accepted_accuracy)]];
  const wrapper=node('div',null,'table-wrap'),table=node('table'),head=node('thead'),tr=node('tr');
  for(const x of ['Mesmo conjunto de teste','Classificador local · escolhido','Jev · comparação'])tr.append(node('th',x));head.append(tr);table.append(head);const body=node('tbody');
  rows.forEach((row,index)=>{const tr=node('tr');row.forEach((x,col)=>{const cell=node('td',x,index===0&&col>0?'metric-big':col===1?'selected-system':'');tr.append(cell);});body.append(tr);});table.append(body);wrapper.append(table);
  const note=node('p','Referência: prever sempre a classe mais frequente acertaria '+pct(data.majority_test_accuracy)+' neste teste. Custo estimado do lote Jev (validação + teste): US$ '+num(data.jev_cost_usd_estimate.estimated)+'.','field-note');
  $('evidence-content').replaceChildren(wrapper,note);
}
async function init(){const results=await Promise.allSettled([getJSON('/api/examples'),getJSON('/api/evidence'),getJSON('/api/health')]);
  if(results[0].status==='fulfilled'){examples=results[0].value;examples.forEach((item,i)=>{const option=node('option','D2 · '+num(item.row)+' — '+item.text.slice(0,65)+'…');option.value=i;$('example-select').append(option);});}else{$('example-note').textContent='Exemplos indisponíveis. Você pode inserir um texto próprio.';}
  if(results[1].status==='fulfilled')renderEvidence(results[1].value);else $('evidence-content').textContent='Comparativo indisponível. Consulte os relatórios no pacote da entrega.';
  if(results[2].status==='fulfilled'){const h=results[2].value;$('service-note').textContent=h.model_available?(h.recap_available?'Classificação local pronta · recap disponível.':'Classificação local pronta · recap sem chave configurada.'):'Modelo local ausente. Siga a preparação descrita no README.';if(!h.recap_available){$('include-recap').checked=false;$('include-recap').disabled=true;}if(!h.model_available)$('analyze-button').disabled=true;}
  else $('service-note').textContent='Não foi possível verificar os serviços. Recarregue a página.';
}
init();
