// Component acceptance in an emulated DOM. This is NOT browser/visual QA.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import ts from 'typescript';
const {Window}=await import(process.env.TEST_DOM_MODULE??'happy-dom');
const window=new Window({url:'https://component-test.invalid'});
for(const name of ['window','document','navigator','HTMLElement','HTMLInputElement','HTMLTextAreaElement','Event','KeyboardEvent','MouseEvent','FormData','File','Blob','localStorage','sessionStorage']) Object.defineProperty(globalThis,name,{value:name==='window'?window:window[name],configurable:true,writable:true});
globalThis.IS_REACT_ACT_ENVIRONMENT=true;
const {default:React,act}=await import('react');
const {createRoot}=await import('react-dom/client');
const folder=path.dirname(fileURLToPath(import.meta.url)),generated=path.join(folder,'.generated');await fs.mkdir(generated,{recursive:true});
const source=await fs.readFile(process.env.TEST_PAGE_SOURCE??path.join(folder,'../app/page.tsx'),'utf8');
const output=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX}}).outputText.replace("'../lib/api'","'./api.mjs'").replace("'../lib/auth'","'./auth.mjs'").replace("'../lib/contracts.mjs'","'../../lib/contracts.mjs'").replace("'./AssistantScreen'","'./AssistantScreen.mjs'").replace("'./UsersScreen'","'./UsersScreen.mjs'").replace("'../lib/permissions.mjs'","'../../lib/permissions.mjs'");
const assistantSource=await fs.readFile(path.join(folder,'../app/AssistantScreen.tsx'),'utf8');await fs.writeFile(path.join(generated,'AssistantScreen.mjs'),ts.transpileModule(assistantSource,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX}}).outputText.replace("'../lib/api'","'./api.mjs'"));
const usersSource=await fs.readFile(path.join(folder,'../app/UsersScreen.tsx'),'utf8');await fs.writeFile(path.join(generated,'UsersScreen.mjs'),ts.transpileModule(usersSource,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX}}).outputText.replace("'../lib/api'","'./api.mjs'").replace("'../lib/permissions.mjs'","'../../lib/permissions.mjs'"));
await fs.writeFile(path.join(generated,'page.mjs'),output);await fs.writeFile(path.join(generated,'api.mjs'),'export const api=(...args)=>globalThis.__api(...args);\n');
await fs.writeFile(path.join(generated,'auth.mjs'),'export const getAuthClient=()=>globalThis.__auth;\n');
const {default:Dashboard}=await import('./.generated/page.mjs');
const {contracts}=await import('../lib/contracts.mjs');
const run={id:'run-original',version_id:'version-original',reference_date:'2024-12-31',published_at:'2026-10-12',metrics:{accounts:25,contract_mrr:2500}};
function fixture(){return {user:{id:'qa-user',session_id:'qa-session',name:'QA User',role:'user',permissions:['analytics.read','accounts.read','quality.read','method.read','decisions.read','decisions.create','actions.update','data.import','data.publish','assistant.use']},run,workspace:{name:'Example'},accounts:Array.from({length:25},(_,i)=>({id:`snapshot-${i}`,account_id:`QA-${i}`,account_name:`Example ${String(i).padStart(3,'0')}`,signup_date:'2024-01-01',industry:i<20?'Alpha':'Beta',country:'BR',cadastral_churn:i===0,has_any_event:false,churn_events:0,reactivation_events:0,reconciliation_state:i===0?'flag_without_event':'no_observed_churn_history',open_contracts:1,contract_mrr:100,coherent_usage_rows_30d:0,coherent_usage_rows_previous_30d:0,recorded_usage_30d:null,recorded_usage_previous_30d:null,eligible_tickets_30d:0,closed_tickets_30d:0,satisfaction_responses:0,mean_satisfaction:null,quality_flags:['telemetry_coverage_not_confirmed']})),evidence:[{id:'evidence-coverage',rule_code:'usage_coverage',summary:'Cobertura não confirmada.'}],quality:[],sources:Object.keys(contracts).map(k=>({source_type:k,filename:`${k}.csv`,rows:25,file_hash:'0'.repeat(64),received_at:'2026-10-12'})),decisions:[],actions:[],history:[],versions:[run],uploads:[]};}
let root,container,state,calls,handler;
async function setup(loggedIn=true,role='user'){state=fixture();state.user.role=role;calls=[];handler=null;let callback;const session={access_token:'synthetic-jwt',user:{id:'qa-user'}};globalThis.__auth={auth:{onAuthStateChange:cb=>{callback=cb;globalThis.__authEvent=cb;queueMicrotask(()=>cb('INITIAL_SESSION',loggedIn?session:null));return {data:{subscription:{unsubscribe(){}}}};},signInWithPassword:async credentials=>{if(credentials.password==='bad')return {error:{message:'Invalid credentials'}};callback('SIGNED_IN',session);return {error:null};},signOut:async()=>{callback('SIGNED_OUT',null);return {error:null};}}};document.body.innerHTML='<div id="root"></div>';container=document.getElementById('root');globalThis.__api=async(name,body)=>{calls.push({name,body});if(handler){const r=await handler(name,body);if(r!==undefined)return r;}if(name==='session')return {user:structuredClone(state.user)};if(name==='logout')return {signed_out:true};if(name==='dashboard')return structuredClone(state);if(name==='scope-options')return {run_id:run.id,metrics:[...['missing_cancel','cadastral_churn','contract_mrr','observed_usage','satisfaction'].map(code=>({code,label:code,scope_types:['account','segment','portfolio']})),{code:'quality_check',label:'Qualidade',scope_types:['quality']}],quality:[{code:'usage.before_subscription',sources:['usage','subscriptions'],interpretation:'Uso anterior',affected_count:2,denominator:5}]};if(name==='scope-preview'){const members=body.scope.type==='quality'?[]:state.accounts.filter(a=>body.scope.type==='portfolio'||(body.scope.type==='account'?a.account_id===body.scope.account_id:(!body.scope.industry||a.industry===body.scope.industry)&&(!body.scope.country||a.country===body.scope.country))).map(a=>({snapshot_id:a.id,account_id:a.account_id,account_name:a.account_name,highlighted:a.cadastral_churn}));if(!members.length&&body.scope.type!=='quality')throw Error('Nenhuma conta elegível neste recorte');return {run,scope:body.scope,scope_label:body.scope.type==='account'?'Conta: '+members[0].account_name:body.scope.type==='segment'?'Segmento: '+(body.scope.industry??'Todos'):'Carteira inteira',metric:body.metric,preview_hash:'a'.repeat(64),population_count:members.length,affected_count:members.filter(a=>a.highlighted).length,members,measure:{label:body.metric,value:1,numerator:1,denominator:members.length,unit:'contas',state:'indeterminate'},warnings:['Limites explícitos']};}if(name==='detail')return {snapshot:state.accounts.find(a=>a.id===body.id),evidence:[],events:[],subscriptions:[],usage:[],support:[]};throw Error('Unhandled '+name);};root=createRoot(container);await act(async()=>{root.render(React.createElement(Dashboard));});}
async function cleanup(){await act(async()=>root.unmount());}
const text=()=>container.textContent;
const button=(name,within=container)=>[...within.querySelectorAll('button')].find(b=>b.textContent.trim()===name);
async function click(el){assert.ok(el,'Clickable element exists');await act(async()=>el.dispatchEvent(new window.MouseEvent('click',{bubbles:true})));}
async function nav(name){await click([...container.querySelectorAll('nav button')].find(b=>b.textContent.trim().startsWith(name)));}
async function change(el,value){await act(async()=>{el.value=value;el.dispatchEvent(new window.Event('change',{bubbles:true}));});}
async function input(el,value){await act(async()=>{const proto=el.tagName==='TEXTAREA'?window.HTMLTextAreaElement.prototype:window.HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(proto,'value').set.call(el,value);el.dispatchEvent(new window.Event('input',{bubbles:true}));el.dispatchEvent(new window.Event('change',{bubbles:true}));});}
async function submit(form){await act(async()=>form.dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true})));}

test('Navegação nas seis áreas, filtro por setor e paginação',async()=>{await setup();try{
 assert.match(text(),/Uma visão clara/);await nav('Contas');assert.equal(container.querySelectorAll('tbody tr').length,20);await click(button('Próxima'));assert.equal(container.querySelectorAll('tbody tr').length,5);
 await change(container.querySelector('.filters select'),'Alpha');assert.equal(container.querySelectorAll('tbody tr').length,20);assert.match(text(),/Página 1/);
 for(const name of ['Diagnóstico','Decisões e ações','Dados e qualidade','Metodologia','Visão executiva']){await nav(name);assert.equal(container.querySelector('h1').textContent,name==='Visão executiva'?'Uma visão clara. Decisões melhores.':name);}
 }finally{await cleanup();}});

test('Detalhe de conta abre, Escape fecha e restaura o foco',async()=>{await setup();try{
 await nav('Contas');const link=container.querySelector('.account-link');link.focus();await click(link);assert.ok(document.querySelector('[role="dialog"]'));assert.match(text(),/Nenhum evento de churn registrado/);
 await act(async()=>document.dispatchEvent(new window.KeyboardEvent('keydown',{key:'Escape',bubbles:true})));assert.equal(document.querySelector('[role="dialog"]'),null);assert.equal(document.activeElement,link);
 }finally{await cleanup();}});

test('Decisão enviada com a evidência; falha mantém formulário e mensagem',async()=>{await setup();try{
 await click(button('Registrar decisão'));const form=document.querySelector('.modal form');for(const [k,v]of Object.entries({title:'Validar extração',rationale:'Ausência de eventos limita o diagnóstico.',actor:'Pessoa declarada',action:'Conferir origem',responsible:'Equipe de dados',due:'2026-10-13'}))form.elements.namedItem(k).value=v;
 handler=async(name)=>{if(name==='decide-scoped')throw Error('Falha controlada na gravação');};await click(button('Revisar evidência',form));await submit(form);assert.match(document.querySelector('[role="dialog"]').textContent,/Falha controlada/);assert.equal(form.elements.namedItem('title').value,'Validar extração');assert.equal(calls.find(c=>c.name==='decide-scoped').body.scope.type,'portfolio');assert.equal(calls.find(c=>c.name==='decide-scoped').body.preview_hash,'a'.repeat(64));
 }finally{await cleanup();}});

test('Erro ao concluir ação precisa aparecer dentro do modal e preservar o resultado',async()=>{await setup();try{
 state.decisions=[{id:'d',title:'Investigar dados',rationale:'Verificar origem e cobertura.',actor_display_name:'QA',evidence_context:{run}}];state.actions=[{id:'a',decision_id:'d',title:'Conferir origem',responsible:'QA',due_date:'2026-10-13',status:'in_progress',revision:1}];await click(container.querySelector('[aria-label="Atualizar dados"]'));await nav('Decisões e ações');await click(button('Concluir'));
 const result=document.querySelector('.modal textarea');result.focus();await input(result,'Resultado completo do teste');assert.equal(document.activeElement,result);handler=async(name)=>{if(name==='transition')throw Error('Revisão desatualizada');};await submit(document.querySelector('.modal form'));
 assert.match(document.querySelector('[role="dialog"]').textContent,/Revisão desatualizada/);assert.equal(result.value,'Resultado completo do teste');
 }finally{await cleanup();}});

test('Falha ao carregar detalhe de conta precisa aparecer no diálogo e permitir retry',async()=>{await setup();try{
 handler=async(name)=>{if(name==='detail')throw Error('Detalhe indisponível');};await nav('Contas');await click(container.querySelector('.account-link'));
 assert.match(document.querySelector('[role="dialog"]').textContent,/Detalhe indisponível/);assert.ok(button('Tentar novamente',document.querySelector('[role="dialog"]')));handler=null;await click(button('Tentar novamente',document.querySelector('[role="dialog"]')));assert.match(document.querySelector('[role="dialog"]').textContent,/Nenhum evento de churn registrado/);
 }finally{await cleanup();}});

test('Upload: mapear, revisar prévia, pausar após etapa e retomar publicação',async()=>{await setup();try{
 const headers=Object.keys(contracts.accounts);let count=0,releaseSecond;const second=new Promise(resolve=>{releaseSecond=resolve;});
 handler=async(name)=>{if(name==='inspect')return {headers,sheets:[],rows:600};if(name==='preview')return {accepted:true,id:'upload-qa',preview:{new_rows:600,added:0,changed:0,removed:0,quality:[]}};if(name==='begin')return {stage:'processing'};if(name==='advance'){count++;if(count===1)return {stage:'processing',processed:300,total:600};if(count===2)return second;return {stage:'published',processed:600,total:600};}};
 await nav('Dados e qualidade');const file=document.querySelector('input[type="file"]');Object.defineProperty(file,'files',{value:[new window.File(['synthetic'],'test.csv',{type:'text/csv'})],configurable:true});await act(async()=>file.dispatchEvent(new window.Event('change',{bubbles:true})));assert.match(text(),/600 linhas/);
 await click(button('Validar e gerar prévia'));assert.match(text(),/PRÉVIA VALIDADA/);assert.equal(calls.filter(c=>c.name==='begin').length,0);
 await click(button('Confirmar e publicar'));assert.equal(count,2);await click(button('Pausar após esta etapa'));await act(async()=>releaseSecond({stage:'verified',processed:600,total:600}));assert.match(text(),/Processamento pausado/);assert.equal(count,2);
 await click(button('Retomar'));assert.match(text(),/Versão publicada/);assert.equal(count,3);
 }finally{await cleanup();}});

test('Upload inválido conserva painel, apresenta erro e não confirma publicação',async()=>{await setup();try{
 handler=async(name)=>{if(name==='inspect')return {headers:Object.keys(contracts.accounts),sheets:[],rows:1};if(name==='preview')return {accepted:false,error_count:1,errors:[{row:2,message:'seats: inteiro inválido'}]};};await nav('Dados e qualidade');const file=document.querySelector('input[type="file"]');Object.defineProperty(file,'files',{value:[new window.File(['synthetic'],'bad.csv')],configurable:true});await act(async()=>file.dispatchEvent(new window.Event('change',{bubbles:true})));await click(button('Validar e gerar prévia'));assert.match(text(),/seats: inteiro inválido/);assert.equal(button('Confirmar e publicar'),undefined);assert.equal(calls.filter(c=>c.name==='begin'||c.name==='advance').length,0);assert.equal(state.run.id,'run-original');
 }finally{await cleanup();}});

test('Busca por conta reduz lista sem confundir ausência de uso com zero',async()=>{await setup();try{await nav('Contas');await input(container.querySelector('.search input'),'Example 024');assert.equal(container.querySelectorAll('tbody tr').length,1);assert.match(container.querySelector('tbody').textContent,/Não observado/);}finally{await cleanup();}});


test('Decisão permite escolher conta, revisar prévia e invalidar ao trocar escopo',async()=>{await setup();try{
 await click(button('Registrar decisão'));const dialog=document.querySelector('[role="dialog"]');assert.match(dialog.querySelector('#decision-review-guidance').textContent,/clique em “Revisar evidência”/);assert.equal(button('Registrar decisão e ação',dialog).getAttribute('aria-describedby'),'decision-review-guidance');await change(dialog.querySelector('[aria-label="Escopo da decisão"]'),'account');await input(dialog.querySelector('[aria-label="Buscar conta para decisão"]'),'Example 024');await change(dialog.querySelector('[aria-label="Conta da decisão"]'),'QA-24');await click(button('Revisar evidência',dialog));assert.match(dialog.textContent,/Conta: Example 024/);assert.equal(calls.find(c=>c.name==='scope-preview').body.scope.account_id,'QA-24');
 assert.equal(button('Registrar decisão e ação',dialog).disabled,false);assert.match(dialog.querySelector('#decision-review-guidance').textContent,/Evidência revisada/);await change(dialog.querySelector('[aria-label="Escopo da decisão"]'),'segment');assert.equal(button('Registrar decisão e ação',dialog).disabled,true);assert.equal(dialog.querySelector('.scope-evidence'),null);assert.match(dialog.querySelector('#decision-review-guidance').textContent,/Revise a evidência antes de registrar/);
 }finally{await cleanup();}});

test('Decisão herda setor/país do painel e exige revisar o recorte',async()=>{await setup();try{
 await change(container.querySelector('.filters select'),'Alpha');await click(button('Registrar decisão'));const dialog=document.querySelector('[role="dialog"]');assert.equal(dialog.querySelector('[aria-label="Escopo da decisão"]').value,'segment');assert.equal(dialog.querySelector('[aria-label="Setor da decisão"]').value,'Alpha');await click(button('Revisar evidência',dialog));assert.equal(dialog.querySelector('.scope-measures b').textContent,'20');assert.match(dialog.querySelector('.scope-measures').textContent,/contas no recorte/);assert.equal(calls.find(c=>c.name==='scope-preview').body.scope.industry,'Alpha');
 }finally{await cleanup();}});

test('Qualidade oferece só regras relacionadas à fonte e não permite métrica de carteira',async()=>{await setup();try{
 await click(button('Registrar decisão'));const dialog=document.querySelector('[role="dialog"]');await change(dialog.querySelector('[aria-label="Escopo da decisão"]'),'quality');await change(dialog.querySelector('[aria-label="Fonte da decisão"]'),'usage');await change(dialog.querySelector('[aria-label="Verificação da decisão"]'),'usage.before_subscription');assert.equal(dialog.querySelector('[aria-label="Dado da decisão"]').value,'quality_check');assert.equal(dialog.querySelector('[aria-label="Dado da decisão"]').options.length,1);await click(button('Revisar evidência',dialog));assert.equal(calls.find(c=>c.name==='scope-preview').body.scope.source,'usage');
 }finally{await cleanup();}});


test('Atualizar contexto invalida prévia e preserva rascunho da decisão',async()=>{await setup();try{
 await click(button('Registrar decisão'));const dialog=document.querySelector('[role="dialog"]'),title=dialog.querySelector('[name="title"]');await input(title,'Investigar cobertura');await click(button('Revisar evidência',dialog));assert.equal(button('Registrar decisão e ação',dialog).disabled,false);state.run={...run,id:'run-new'};await click(button('Atualizar contexto',dialog));assert.equal(title.value,'Investigar cobertura');assert.equal(button('Registrar decisão e ação',dialog).disabled,true);assert.equal(dialog.querySelector('.scope-evidence'),null);assert.equal(calls.filter(c=>c.name==='scope-options').at(-1).body.run_id,'run-new');
 }finally{await cleanup();}});

test('Lista filtra escopo novo e preserva leitura de decisão anterior',async()=>{await setup();try{
 state.decisions=[{id:'old',title:'Registro anterior',rationale:'Conferir cobertura.',actor_display_name:'QA',evidence_context:{run}},{id:'new',scope_type:'segment',title:'Investigar setor',rationale:'Conferir extração.',actor_display_name:'QA',evidence_context:{run,scope:{type:'segment',industry:'Alpha'},scope_label:'Segmento: Alpha / Todos os países'}}];state.actions=state.decisions.map(d=>({id:'a-'+d.id,decision_id:d.id,title:'Conferir origem',responsible:'QA',due_date:'2026-10-13',status:'completed',revision:2}));await click(container.querySelector('[aria-label="Atualizar dados"]'));await nav('Decisões e ações');assert.equal(container.querySelectorAll('.decision-card').length,2);await change(container.querySelector('[aria-label="Filtrar decisões por escopo"]'),'segment');assert.equal(container.querySelectorAll('.decision-card').length,1);assert.match(text(),/Investigar setor/);await change(container.querySelector('[aria-label="Filtrar decisões por escopo"]'),'legacy');assert.equal(container.querySelectorAll('.decision-card').length,1);await click(button('Evidência e histórico'));assert.match(document.querySelector('[role="dialog"]').textContent,/Registro anterior/);assert.match(document.querySelector('[role="dialog"]').textContent,/Evidência geral · registro anterior/);
 }finally{await cleanup();}});


test('Login impede consulta do painel sem sessão e permite mostrar senha',async()=>{await setup(false);try{
 assert.match(text(),/Entre na sua conta/);assert.equal(calls.filter(c=>c.name==='dashboard').length,0);const password=container.querySelector('[name="password"]');assert.equal(password.type,'password');await click(container.querySelector('[aria-label="Mostrar senha"]'));assert.equal(password.type,'text');
 }finally{await cleanup();}});
test('Senha incorreta mantém login com mensagem e não consulta dados',async()=>{await setup(false);try{
 await input(container.querySelector('[name="email"]'),'qa@example.invalid');await input(container.querySelector('[name="password"]'),'bad');await submit(container.querySelector('form'));assert.match(text(),/E-mail ou senha incorretos/);assert.equal(calls.filter(c=>c.name==='dashboard').length,0);assert.equal(container.querySelector('[name="email"]').value,'qa@example.invalid');
 }finally{await cleanup();}});
test('Perfis acessam as áreas permitidas; administração aparece somente ao administrador',async()=>{for(const role of ['user','administrator']){await setup(false,role);try{
 await input(container.querySelector('[name="email"]'),'qa@example.invalid');await input(container.querySelector('[name="password"]'),'synthetic-password');await submit(container.querySelector('form'));assert.equal(container.querySelectorAll('nav button').length,role==='administrator'?8:7);assert.match(text(),/QA User/);assert.match(text(),role==='administrator'?/Administrador/:/Usuário/);await click(button('Sair'));assert.match(text(),/Entre na sua conta/);assert.equal(container.querySelector('nav'),null);assert.equal(calls.filter(c=>c.name==='logout').length,1);
 }finally{await cleanup();}}});


test('Troca de conta limpa o painel enquanto o novo perfil é validado',async()=>{await setup();try{
 let finish;handler=async(name)=>{if(name==='session')return new Promise(resolve=>{finish=resolve;});};await act(async()=>globalThis.__authEvent('SIGNED_IN',{access_token:'other',user:{id:'other-user'}}));assert.equal(container.querySelector('nav'),null);assert.match(text(),/Verificando seu acesso/);state.user={...state.user,id:'other-user',name:'Outra pessoa',session_id:'other-session'};await act(async()=>finish({user:state.user}));assert.match(text(),/Outra pessoa/);assert.equal(container.querySelectorAll('nav button').length,7);
 }finally{await cleanup();}});

test('Assistant exploration clears old search and reconciliation and preserves the evidence context',async()=>{await setup();try{
 await nav('Contas');await input(container.querySelector('[aria-label="Buscar conta"]'),'no-match');await change(container.querySelector('[aria-label="Reconciliação"]'),'flag_without_event');
 handler=async(name,body)=>{
 if(name==='assistant-status')return {configured:true};
 if(name==='assistant-list')return {conversations:[{id:'review-conv',title:'Review result'}],has_more:false};
 if(name==='assistant-conversation')return {conversation:{id:'review-conv',title:'Review result',run_id:run.id,filters:{},archived:false},messages:[{seq:1,role:'assistant',content:'25 contas',result:{evidence:{metric:'accounts',label:'Contas cadastradas',value:'25',unit:'contas',run_id:run.id,filters:{},reference_date:run.reference_date,definition:'Todas as contas'}}}],turns:[],current_run_id:run.id};
 };
 await nav('Assistente IA');await click([...container.querySelectorAll('.assistant-conversations button')][0]);await click(button('Explorar contas deste recorte'));
 assert.equal(container.querySelector('[aria-label="Buscar conta"]').value,'');assert.equal(container.querySelector('[aria-label="Reconciliação"]').value,'all');assert.equal(container.querySelectorAll('tbody tr').length,20);assert.match(text(),/Recorte vindo do assistente/);assert.match(text(),/Não é a lista de ocorrências da métrica/);
 }finally{await cleanup();}});
test('Account tickets expose satisfaction eligibility and keep absent notes distinct from zero',async()=>{await setup();try{
 handler=async(name,body)=>name==='detail'?{snapshot:state.accounts[0],evidence:[],events:[],subscriptions:[],usage:[],support:[
 {ticket_id:'T-OK',submitted_at:'2024-12-02 09:00:00',closed_at:'2024-12-03 09:00:00',satisfaction_score:3},
 {ticket_id:'T-NONE',submitted_at:'2024-12-02',closed_at:'2024-12-03',satisfaction_score:null},
 {ticket_id:'T-OUTSIDE',submitted_at:'2024-12-01',closed_at:'2024-12-03',satisfaction_score:5},
 {ticket_id:'T-FUTURE',submitted_at:'2024-12-31',closed_at:'2025-01-01',satisfaction_score:5}]}:undefined;
 await nav('Contas');await click(container.querySelector('tbody tr button'));const modal=container.querySelector('[role="dialog"]');assert.match(modal.textContent,/T-OK/);assert.match(modal.textContent,/Elegível para satisfação/);assert.match(modal.textContent,/Fechado elegível · sem nota/);assert.match(modal.textContent,/abertura fora da janela/);assert.match(modal.textContent,/não encerrado validamente até o corte/);assert.match(modal.textContent,/Sem nota/);
 }finally{await cleanup();}});
test('Executive investigation includes reactivation-only accounts and passive cards are not buttons',async()=>{await setup();try{
 state.accounts[1].cadastral_churn=true;state.accounts[1].churn_events=0;state.accounts[1].reconciliation_state='flag_with_reactivation_only';
 await click(container.querySelector('[aria-label="Atualizar dados"]'));await click(button('Investigar por exposição'));assert.equal(container.querySelectorAll('tbody tr').length,2);assert.equal(container.querySelector('[aria-label="Reconciliação"]').value,'missing_cancel');
 await nav('Diagnóstico');assert.equal(container.querySelectorAll('button.stat').length,0);assert.equal(container.querySelectorAll('.stat').length,4);
 }finally{await cleanup();}});

test('Analytics-only access shows aggregates, with no account navigation or write controls',async()=>{await setup(false);try{
 state.user.permissions=['analytics.read'];state.accounts=[];state.analytics=[{industry:'Alpha',country:'BR',accounts:25,open_accounts:20,contract_mrr:2500,flagged:3,missing_cancel:2,missing:1,missing_cancel_mrr:200,responses:2,closed:3,satisfaction_total:8}];
 await input(container.querySelector('[name="email"]'),'qa@example.invalid');await input(container.querySelector('[name="password"]'),'valid');await submit(container.querySelector('form'));
 assert.equal(container.querySelectorAll('nav button').length,2);assert.match(text(),/indicadores agregados/);assert.equal(button('Registrar decisão'),undefined);assert.equal(container.querySelector('.account-link'),null);await nav('Diagnóstico');assert.match(text(),/Carteira por setor/);
 }finally{await cleanup();}});
test('Forced password change blocks dashboard; password is cleared after saving',async()=>{await setup(false);try{
 state.user.password_change_required=true;state.user.email='qa@example.invalid';handler=async(name)=>{if(name==='password-change'){state.user.password_change_required=false;state.user.revision=2;return {completed:true};}};
 await input(container.querySelector('[name="email"]'),'qa@example.invalid');await input(container.querySelector('[name="password"]'),'valid');await submit(container.querySelector('form'));
 assert.match(text(),/Defina sua senha pessoal/);assert.equal(calls.filter(c=>c.name==='dashboard').length,0);
 const inputs=container.querySelectorAll('input');await input(inputs[0],'SyntheticOnly123');await input(inputs[1],'SyntheticOnly123');await submit(container.querySelector('form'));assert.equal(calls.filter(c=>c.name==='password-change').length,1);assert.ok(container.querySelector('nav'));assert.equal(container.querySelector('input[type="password"]'),null);
 }finally{await cleanup();}});
test('User management protects owner, expands dependencies and clears the initial password on failure',async()=>{await setup(true,'administrator');try{
 handler=async(name)=>{if(name==='users-list')return {users:[{id:'owner',name:'Owner',email:'owner@example.invalid',role:'super_admin',active:true,permissions:[],revision:1}],audit:[],pending:[]};if(name==='users-create')throw Error('Synthetic transport interruption');};
 await nav('Usuários e permissões');assert.match(text(),/Conta protegida/);assert.equal(container.querySelector('[aria-label="Editar owner@example.invalid"]'),null);await click(button('Adicionar usuário'));
 const dialog=container.querySelector('[role="dialog"]');const inputs=dialog.querySelectorAll('input');await input(inputs[0],'New Person');await input(inputs[1],'new@example.invalid');
 const assistant=[...dialog.querySelectorAll('label')].find(l=>l.textContent.includes('Assistente IA e histórico próprio'));await click(assistant.querySelector('input'));const quality=[...dialog.querySelectorAll('label')].find(l=>l.textContent.includes('Dados e qualidade'));assert.equal(quality.querySelector('input').checked,true);
 await input(dialog.querySelector('input[type="password"]'),'SyntheticOnly123');await submit(dialog.querySelector('form'));assert.match(dialog.textContent,/Synthetic transport interruption/);assert.equal(dialog.querySelector('input[type="password"]').value,'');assert.equal(calls.find(c=>c.name==='users-create').body.permissions.includes('quality.read'),true);
 }finally{await cleanup();}});
test('Removing permissions remounts the dashboard and drops previously visible records',async()=>{await setup();try{
 await nav('Contas');assert.ok(container.querySelector('.account-link'));state.user.permissions=['method.read'];state.user.revision=2;state.accounts=[];await act(async()=>window.dispatchEvent(new window.Event('focus')));assert.equal(container.querySelectorAll('nav button').length,1);assert.equal(container.querySelector('.account-link'),null);assert.match(text(),/Uma observação, uma definição/);
 }finally{await cleanup();}});
