import {getAuthClient,SUPABASE_URL,SUPABASE_PUBLISHABLE_KEY} from './auth';
const BASE=SUPABASE_URL+'/functions/v1/challenge-auth-web';
const ASSISTANT_BASE=SUPABASE_URL+'/functions/v1/challenge-assistant';
const USERS_BASE=SUPABASE_URL+'/functions/v1/challenge-users';
const DECISIONS_BASE=SUPABASE_URL+'/functions/v1/challenge-auth-decisions';
const scopedRoutes=new Set(['scope-options','scope-preview','decide-scoped']);
export class ApiError extends Error{constructor(message:string,public status:number){super(message);}}
function expired(){window.dispatchEvent(new Event('ravenstack:auth-expired'));return new ApiError('Sua sessão expirou. Entre novamente.',401);}
export async function api(path:string,body?:unknown,retry=true):Promise<any>{
 const client=getAuthClient();const {data,error}=await client.auth.getSession();
 if(error||!data.session?.access_token)throw expired();
 const multipart=body instanceof FormData;
 const controller=new AbortController();
 const timeout=setTimeout(()=>controller.abort(),path==='assistant-ask'?75000:body===undefined?20000:45000);
 let r:Response,d:any;
 try{
  r=await fetch((path.startsWith('users-')||path==='password-change'?USERS_BASE:path.startsWith('assistant-')?ASSISTANT_BASE:scopedRoutes.has(path)?DECISIONS_BASE:BASE)+'/'+path,{method:body===undefined?'GET':'POST',cache:'no-store',signal:controller.signal,headers:{Authorization:'Bearer '+data.session.access_token,apikey:SUPABASE_PUBLISHABLE_KEY,...(multipart?{}:{'Content-Type':'application/json'})},body:body===undefined?undefined:multipart?body:JSON.stringify(body)});
  if(r.status!==401){try{d=await r.json();}catch{if(controller.signal.aborted)throw new Error('timeout');throw new ApiError('O serviço retornou uma resposta inesperada. Confira o histórico antes de repetir uma operação.',502);}}
 }catch(e){
  if(controller.signal.aborted)throw new ApiError('O tempo de espera terminou. Confira o histórico ou retome a operação; o servidor pode ter concluído o processamento.',408);
  if(e instanceof ApiError)throw e;
  throw new ApiError('Não foi possível conectar. Tente atualizar os dados antes de repetir uma operação.',0);
 }finally{clearTimeout(timeout);}
 if(r.status===401){
  if(retry){const refreshed=await client.auth.refreshSession();if(!refreshed.error&&refreshed.data.session)return api(path,body,false);}
  throw expired();
 }
 if(r.status===403)window.dispatchEvent(new Event('ravenstack:access-changed'));
 if(!r.ok)throw new ApiError(d?.error??'Falha na operação.',r.status);return d;
}
