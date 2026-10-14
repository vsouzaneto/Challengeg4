// Temporary fixed-fixture check only. Custom authentication: random one-use 256-bit nonce,
// only its SHA-256 is in a private DB row, expires after ten minutes. No user/Auth data access.
// After checking, redeploy this function as an always-410, verify_jwt=true tombstone.
import {executeQuestion} from '../domain/assistant.mjs';
const url=Deno.env.get('SUPABASE_URL')!,key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const reply=(x:unknown,status=200)=>new Response(JSON.stringify(x),{status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});
async function rpc(name:string,args:Record<string,unknown>){const r=await fetch(url+'/rest/v1/rpc/'+name,{method:'POST',headers:{apikey:key,Authorization:'Bearer '+key,'Content-Type':'application/json'},body:JSON.stringify(args),signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('check_database');return r.json();}
Deno.serve(async(req:Request)=>{
 if(req.method!=='POST')return reply({error:'Not available.'},405);
 const nonce=req.headers.get('x-assistant-check')??'';if(nonce.length<40||nonce.length>128)return reply({error:'Unauthorized.'},401);
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(nonce)))).map(x=>x.toString(16).padStart(2,'0')).join('');
 let id;try{id=await rpc('challenge_assistant_check_claim',{p_hash:hash});}catch{return reply({error:'Unavailable.'},503);}if(!id)return reply({error:'Unauthorized or consumed.'},401);
 const apiKey=Deno.env.get('OPENAI_API_KEY')?.trim();const result:any={key_present:!!apiKey,model:'gpt-6-luna',fixture:'synthetic_only',tests:[],usage:{input_tokens:0,output_tokens:0},provider_responses:0};
 const context={run_id:'integration-fixture',reference_date:'2024-12-31',filters:{},catalog:{industry:['EdTech'],country:['BR'],plan_tier:['Basic']}};
 const modelCall=async(body:any)=>{const r=await fetch('https://api.openai.com/v1/responses',{method:'POST',headers:{Authorization:'Bearer '+apiKey,'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(25000)});if(!r.ok){const e=new Error('provider_http_'+r.status);(e as any).code='provider_http_'+r.status;throw e;}const b=await r.json();result.usage.input_tokens+=b.usage?.input_tokens??0;result.usage.output_tokens+=b.usage?.output_tokens??0;result.provider_responses++;return b;};
 try{
  if(!apiKey)throw Object.assign(new Error('configuration'),{code:'configuration'});
  for(const [name,question,expected] of [['accounts','Quantas contas cadastradas existem na base fornecida?','fact'],['ambiguous_mrr','Quanto de MRR anual há em EdTech?','clarification'],['unsupported_forecast','Preveja quanto perderemos em MRR no próximo ano e qual cliente vai cancelar.','unsupported']]){
   const r=await executeQuestion({question,context,history:[],modelCall,query:async q=>{if(q.metric!=='accounts'||q.industry!==null||q.country!==null)throw Object.assign(new Error('unexpected_query'),{code:'unexpected_query'});return {metric:'accounts',label:'Contas cadastradas de teste',value:'3',unit:'contas',run_id:'integration-fixture',reference_date:'2024-12-31',filters:{},definition:'Fixture sintético de integração com três cadastros, não representa a carteira real.',warnings:[]};}});
   const passed=r.kind===expected&&(name!=='accounts'||r.evidence?.value==='3');result.tests.push({name,expected,actual:r.kind,passed});
  }
  result.passed=result.tests.length===3&&result.tests.every((x:any)=>x.passed);
 }catch(e){result.passed=false;result.error_code=(e as any).code??'unexpected_check_error';}
 try{await rpc('challenge_assistant_check_finish',{p_id:id,p_result:result});}catch{return reply({error:'Check result could not be recorded.'},503);}
 return reply(result);
});
