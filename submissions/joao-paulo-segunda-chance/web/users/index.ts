import {authenticate} from '../edge/auth.ts';
import {validateUserInput,validatePassword} from '../domain/permissions.mjs';
const url=Deno.env.get('SUPABASE_URL')!,key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'content-type,authorization,apikey','Access-Control-Allow-Methods':'GET,POST,OPTIONS','Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
const reply=(value:unknown,status=200)=>new Response(JSON.stringify(value),{status,headers});
async function rpc(name:string,args:Record<string,unknown>){const r=await fetch(url+'/rest/v1/rpc/'+name,{method:'POST',headers:{apikey:key,Authorization:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(args),signal:AbortSignal.timeout(15000)});const d=await r.json();if(!r.ok){const e=new Error(d.message??'Operação indisponível.');(e as any).code=d.code;throw e;}return d;}
Deno.serve(async(req:Request)=>{
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
 try{
  const {p_token}=await authenticate(req,rpc,url,key),path=new URL(req.url).pathname.split('/').pop();
  if(path==='users-list'&&req.method==='GET')return reply(await rpc('challenge_users_list',{p_token}));
  if(req.method!=='POST')return reply({error:'Método não permitido.'},405);
  if(Number(req.headers.get('content-length')??0)>12000)return reply({error:'Requisição muito grande.'},413);
  const raw=await req.text();if(raw.length>12000)return reply({error:'Requisição muito grande.'},413);const b=JSON.parse(raw);
  if(!['users-create','users-update','users-reset','users-takeover','password-change'].includes(path??''))return reply({error:'Operação desconhecida.'},404);
  if(path==='users-takeover')return reply(await rpc('challenge_users_takeover',{p_token,p_request:b.request_key}));
  if(path==='users-update')return reply(await rpc('challenge_users_update',{p_token,p_target:b.id,p_revision:b.revision,p_data:validateUserInput(b)}));
  const self=path==='password-change',create=path==='users-create';
  const password=validatePassword(b.password);
  const op=await rpc('challenge_users_prepare',{p_token,p_request:b.request_key,p_kind:create?'create':self?'change_password':'reset_password',p_target:create||self?null:b.id,p_revision:self||create?null:b.revision,p_data:create?validateUserInput(b,true):{}});
  if(op.state==='completed')return reply({completed:true});
  // No password is ever sent to SQL, logs, app_metadata, audit records or the response.
  // The immutable operation marker allows safe reconciliation after ambiguous Auth timeouts.
  const authPath=self?'/auth/v1/user':create&&!op.target_id?'/auth/v1/admin/users':'/auth/v1/admin/users/'+op.target_id;
  const payload=create&&!op.target_id?{email:op.email,password,email_confirm:true,app_metadata:{ravenstack_creation_operation:op.id}}:{password};
  let r;try{r=await fetch(url+authPath,{method:create&&!op.target_id?'POST':'PUT',headers:{apikey:key,Authorization:self?req.headers.get('authorization')!:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(15000)});}catch{throw Object.assign(new Error('Não foi possível confirmar a operação. Aguarde um minuto e retome a mesma solicitação; o acesso permanece protegido.'),{code:'PT503'});}
  if(!r.ok){const d=await r.json().catch(()=>({}));const weak=d.code==='weak_password'||d.error_code==='weak_password'||d.code==='same_password'||d.error_code==='same_password';throw Object.assign(new Error(weak?'A senha foi recusada pelo Supabase. Use outra senha e tente novamente.':'O Supabase não confirmou a gravação. Confira a lista e retome esta solicitação; nenhuma senha foi registrada no histórico.'),{code:weak?'22023':'PT503'});}
  // Do not forward Auth's user object or provider errors to the client.
  await r.json();
  await rpc('challenge_users_finish',{p_token,p_request:op.id,p_attempt:op.attempt});
  return reply({completed:true});
 }catch(e){const code=(e as any).code,status=code==='28000'?401:code==='PT403'?403:code==='PT409'?409:code==='PT429'?429:code==='PT503'?503:400;return reply({error:(e as Error).message},status);}
});
