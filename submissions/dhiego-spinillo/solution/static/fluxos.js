'use strict';
const $ = id => document.getElementById(id);
const names = {self_service:'Autosserviço',prepared:'Atendimento preparado',human:'Investigação humana'};
const states = {ready:'Pronto para o próximo passo',awaiting_customer:'Aguardando conclusão pelo cliente',resolved_demo:'Procedimento concluído no provedor simulado',approved_demo:'Resposta aprovada; sem envio externo',investigating:'Investigação recebida; caso ainda não resolvido'};
let scenarios = [], current = null, token = null, version = 0, busy = false;
function invalidate() {version++; $('flow-action-status').textContent=''; current=null; token=null; $('flow-result').hidden=true; $('flow-empty').hidden=false; $('flow-status').textContent='Entrada alterada. Processe o pedido para consultar o cenário novamente.';}
function choose() {const s=scenarios.find(s=>s.id===$('flow-scenario').value); $('flow-text').value=s.text; $('flow-source').textContent=s.source; invalidate();}
function itemList(target, items) {target.replaceChildren(); for(const item of items){const li=document.createElement('li');li.textContent=item;target.append(li);}}
function citedSignal(target,label,quotes,empty){const li=document.createElement('li');const strong=document.createElement('strong');strong.textContent=label;li.append(strong,document.createTextNode(' '));if(quotes.length){const span=document.createElement('span');span.textContent='Sinal encontrado no texto:';li.append(span);for(const quote of quotes){const block=document.createElement('blockquote');block.textContent=quote;li.append(block);}}else{li.append(document.createTextNode(empty));}target.append(li);}
function actionButton(label, action, primary=false) {const b=document.createElement('button');b.type='button';b.textContent=label;b.className=primary?'primary':'secondary';b.addEventListener('click',()=>act(action));$('flow-actions').append(b);}
function render(run) {
 current=run; $('flow-empty').hidden=true; $('flow-result').hidden=false;
 $('flow-lane').textContent=names[run.plan.lane]; $('flow-title').textContent=run.plan.title;
 $('flow-reason').textContent=run.plan.reason; $('flow-state').textContent=states[run.state];
 $('flow-facts').replaceChildren(); for(const source of run.context.sources){const dt=document.createElement('dt');dt.textContent=source.name+' · '+source.status;const dd=document.createElement('dd');dd.textContent=source.fact;$('flow-facts').append(dt,dd);}
 $('flow-extraction').textContent=run.signals.source;
 $('flow-warning').hidden=!run.signals.warning; $('flow-warning').textContent=run.signals.warning||'';
 $('flow-quotes').replaceChildren(); const quotes=[...(run.signals.intent_quote?[['Intenção',run.signals.intent_quote]]:[]),...run.signals.attempts.map(q=>['Tentativa ou erro',q]),...run.signals.risk_quotes.map(q=>['Sinal para investigação',q])];
 for(const [label,quote] of quotes){const li=document.createElement('li');li.textContent=label;const block=document.createElement('blockquote');block.textContent=quote;li.append(block);$('flow-quotes').append(li);}
 $('flow-empty-quotes').hidden=quotes.length>0;
 $('flow-operational-signals').replaceChildren();
 citedSignal($('flow-operational-signals'),'Temperatura:',run.signals.temperature_quotes||[],run.signals.temperature==='attention'?'sinal pendente de confirmação.':'nenhum atrito explícito identificado; isso não permite concluir que o cliente está tranquilo.');
 citedSignal($('flow-operational-signals'),'Prazo ou urgência:',run.signals.urgency_quotes||[],'nenhuma menção literal identificada; isso não permite concluir que não há urgência.');
 $('flow-sla-state').textContent=(run.signals.urgency_quotes||[]).length?'SLA: há uma menção temporal que o atendente deve confirmar no contexto. A demonstração não possui abertura, prazo de política, primeira resposta ou relógio de SLA para declarar atraso.':'SLA: não calculável nesta demonstração. Faltam abertura, prazo de política, primeira resposta e relógio operacional.';
 itemList($('flow-steps'),run.plan.next_steps); $('flow-actions').replaceChildren();
 $('flow-draft-section').hidden=!(run.plan.draft && run.state==='ready') && !run.approved_draft; $('flow-draft').value=run.approved_draft||run.plan.draft||''; $('flow-draft').readOnly=run.state!=='ready'; $('flow-approve').hidden=run.state!=='ready'; $('flow-draft-label').textContent=run.approved_draft?'Resposta aprovada e registrada':'Resposta preparada · texto por regra e fonte consultada';
 if(run.plan.lane==='self_service'){
  if(run.state==='ready')actionButton('Solicitar recuperação (cliente)','request_recovery',true);
  if(run.state==='awaiting_customer' && token)actionButton('Concluir no provedor simulado','complete_recovery',true);
  if(['ready','awaiting_customer','resolved_demo'].includes(run.state))actionButton('Não resolveu: encaminhar ao suporte','report_failure');
  if(run.state==='awaiting_customer') {const p=document.createElement('p');p.className='field-note';p.textContent='Este botão simula o retorno do provedor após a verificação do cliente. Nenhuma senha real é solicitada ou alterada.';$('flow-actions').append(p);}
 }
 if(run.plan.lane==='human'&&run.state==='ready')actionButton('Assumir investigação (humano)','acknowledge_handoff',true);
 $('flow-events').replaceChildren();for(const event of run.events){const li=document.createElement('li');const actor=document.createElement('strong');actor.textContent=event.actor;li.append(actor,document.createTextNode(event.event));$('flow-events').append(li);}
}
async function request(url,body){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok){const b=await r.json().catch(()=>({}));throw new Error(typeof b.detail==='string'?b.detail:'Não foi possível processar. Confira a entrada e tente novamente.');}return r.json();}
function lock(value){busy=value;$('flow-start').disabled=value;$('flow-scenario').disabled=value;$('flow-text').disabled=value;$('flow-ai').disabled=value;$('flow-draft').disabled=value;for(const b of $('flow-result').querySelectorAll('button'))b.disabled=value;}
$('flow-form').addEventListener('submit',async e=>{e.preventDefault();if(busy)return;invalidate();const revision=version;const text=$('flow-text').value;const useAI=$('flow-ai').checked;lock(true);$('flow-status').textContent=useAI?'Interpretando pedido com IA e consultando os registros de demonstração…':'Consultando registros e aplicando regras, sem IA…';try{const run=await request('/api/flows',{scenario_id:$('flow-scenario').value,text,use_ai:useAI});if(revision!==version)return;render(run);$('flow-status').textContent='Contexto consultado e caminho preparado. Registros de demonstração.';}catch(error){$('flow-status').textContent=error.message;}finally{lock(false);}});
async function act(action){if(!current||busy)return;lock(true);$('flow-action-status').textContent='Registrando…';try{const run=await request('/api/flows/'+encodeURIComponent(current.id)+'/actions',{action,token:action==='complete_recovery'?token:null,draft:action==='approve_draft'?$('flow-draft').value:null});token=run.demo_token||null;render(run);$('flow-action-status').textContent=states[run.state]+'.';}catch(error){$('flow-action-status').textContent=error.message;}finally{lock(false);}}
$('flow-approve').addEventListener('click',()=>act('approve_draft'));
$('flow-scenario').addEventListener('change',choose);$('flow-text').addEventListener('input',invalidate);$('flow-ai').addEventListener('change',invalidate);
(async()=>{try{const response=await fetch('/api/flows/scenarios');if(!response.ok)throw new Error();const data=await response.json();scenarios=data.scenarios;$('flow-scenario').replaceChildren();for(const s of scenarios){const option=document.createElement('option');option.value=s.id;option.textContent=s.title;$('flow-scenario').append(option);}$('flow-ai').checked=data.ai_available;$('flow-ai-note').textContent=data.ai_available?'IA disponível. Se a extração falhar, o atendimento segue preparado para revisão.':'IA não configurada: os exemplos podem rodar com regras lexicais identificadas como tal.';choose();lock(false);$('flow-status').textContent='Escolha o cenário e processe o pedido.';}catch{$('flow-status').textContent='Não foi possível carregar os exemplos. Recarregue a página.';}})();
