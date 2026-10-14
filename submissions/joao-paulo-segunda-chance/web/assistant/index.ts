import {authenticate} from '../edge/auth.ts';
import {executeQuestion,publicError,assistantVersion} from '../domain/assistant.mjs';
const url=Deno.env.get('SUPABASE_URL')!,key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'content-type,authorization,apikey','Access-Control-Allow-Methods':'GET,POST,OPTIONS','Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
const reply=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers});
async function rpc(name:string,args:Record<string,unknown>){const r=await fetch(url+'/rest/v1/rpc/'+name,{method:'POST',headers:{apikey:key,Authorization:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(args),signal:AbortSignal.timeout(15000)});const b=await r.json();if(!r.ok){const e=new Error(b.message??'Consulta indisponível.');(e as any).code=b.code;throw e;}return b;}
Deno.serve(async(req:Request)=>{
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
 try{
  const {p_token}=await authenticate(req,rpc,url,key);await rpc('challenge_access_check',{p_token,p_permission:'assistant.use'});const path=new URL(req.url).pathname.split('/').pop();
  if(path==='assistant-status'&&req.method==='GET')return reply({configured:!!Deno.env.get('OPENAI_API_KEY')?.trim(),model:'gpt-6-luna',version:assistantVersion});
  if(req.method!=='POST')return reply({error:'Método não permitido.'},405);
  if(Number(req.headers.get('content-length')??0)>16000)return reply({error:'Solicitação muito grande.'},413);
  const raw=await req.text();if(raw.length>16000)return reply({error:'Solicitação muito grande.'},413);const b=JSON.parse(raw);
  if(!b||typeof b!=='object'||Array.isArray(b))return reply({error:'Solicitação inválida.'},400);
  if(path==='assistant-list')return reply(await rpc('challenge_assistant_list',{p_token,p_query:b.query??'',p_archived:b.archived??false,p_offset:b.offset??0}));
  if(path==='assistant-create')return reply(await rpc('challenge_assistant_create',{p_token,p_filters:b.filters??{}}));
  if(path==='assistant-conversation')return reply(await rpc('challenge_assistant_conversation',{p_token,p_id:b.id,p_before:b.before??null}));
  if(path==='assistant-update')return reply(await rpc('challenge_assistant_update',{p_token,p_id:b.id,p_action:b.action,p_title:b.title??'',p_archived:b.archived??false,p_filters:b.filters??{}}));
  if(path!=='assistant-ask')return reply({error:'Operação desconhecida.'},404);
  const apiKey=Deno.env.get('OPENAI_API_KEY')?.trim();if(!apiKey)return reply({error:publicError({code:'configuration'}),code:'configuration'},503);
  if(typeof b.question!=='string'||!b.question.trim()||b.question.length>2000)return reply({error:'Pergunta deve ter entre 1 e 2.000 caracteres.'},400);
  const started=await rpc('challenge_assistant_begin',{p_token,p_conversation:b.id,p_request:b.request_key,p_question:b.question});
  if(started.state==='cached')return reply(started.result);
  const ledger={input_tokens:0,output_tokens:0,provider_responses:[] as string[],usage_complete:true};
  const modelCall=async(body:unknown)=>{let r;try{r=await fetch('https://api.openai.com/v1/responses',{method:'POST',headers:{Authorization:'Bearer '+apiKey,'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(25000)});}catch{ledger.usage_complete=false;throw Error('Provider unavailable');}
   if(!r.ok){ledger.usage_complete=false;const e=new Error('Provider unavailable');(e as any).code=[401,403,404].includes(r.status)?'provider_credentials':r.status===429?'provider_limit':'provider';throw e;}let out;try{out=await r.json();}catch{ledger.usage_complete=false;throw Error('Provider unavailable');}if(!out.usage)ledger.usage_complete=false;ledger.input_tokens+=Number(out.usage?.input_tokens)||0;ledger.output_tokens+=Number(out.usage?.output_tokens)||0;if(out.id)ledger.provider_responses.push(out.id);return out;};
  try{
   const result=await executeQuestion({question:b.question,context:started.context,history:started.history,modelCall,query:(p_query:unknown)=>rpc('challenge_assistant_query',{p_token,p_turn:started.turn_id,p_execution:started.execution_id,p_query})});
   return reply(await rpc('challenge_assistant_finish',{p_token,p_turn:started.turn_id,p_execution:started.execution_id,p_status:'completed',p_result:result,p_usage:ledger}));
  }catch(e){const code=(e as any).code;const text=['22023','PT409','PT429'].includes(code)?(e as Error).message:publicError(e);
   await rpc('challenge_assistant_finish',{p_token,p_turn:started.turn_id,p_execution:started.execution_id,p_status:'failed',p_result:{answer:text,kind:'error',evidence:null,warnings:[],explanation:'',status:'failed'},p_usage:ledger});return reply({error:text,code:code??'provider'},code==='22023'?400:code==='PT429'?429:code==='PT409'?409:503);
  }
 }catch(e){const code=(e as any).code,status=code==='28000'?401:code==='PT403'?403:code==='PT404'?404:code==='PT409'?409:code==='PT429'?429:code==='22023'?400:503;return reply({error:status===503?'O assistente está indisponível. Tente novamente.':(e as Error).message},status);}
});
