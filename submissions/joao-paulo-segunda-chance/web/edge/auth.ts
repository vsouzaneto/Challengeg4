import {verifiedIdentity} from '../domain/auth_identity.mjs';
// Authenticated gateway shared by ingestion and decisions. No role from user metadata.
export async function authenticate(req:Request,rpc:(name:string,args:Record<string,unknown>)=>Promise<any>,url:string,key:string){
 const authorization=req.headers.get('authorization')??'';
 if(!/^Bearer [^\s]+$/.test(authorization)||authorization.length>8192){const e=new Error('Entre com e-mail e senha para acessar o painel.');(e as any).code='28000';throw e;}
 const verified=await fetch(url+'/auth/v1/user',{headers:{apikey:key,Authorization:authorization},signal:AbortSignal.timeout(10000)});
 if(!verified.ok){const e=new Error(verified.status>=500?'Autenticação indisponível. Tente novamente.':'Sessão ausente ou expirada.');(e as any).code=verified.status>=500?'PT503':'28000';throw e;}
 let claims;try{claims=verifiedIdentity(authorization.slice(7),await verified.json());}catch{const e=new Error('Sessão ausente ou expirada.');(e as any).code='28000';throw e;}
 const encoder=new TextEncoder();
 const secret=await crypto.subtle.importKey('raw',encoder.encode(key),{name:'HMAC',hash:'SHA-256'},false,['sign']);
 const hex=(bytes:ArrayBuffer)=>Array.from(new Uint8Array(bytes)).map(x=>x.toString(16).padStart(2,'0')).join('');
 // Stable logical session across JWT refreshes. This value never leaves the server.
 const p_token=hex(await crypto.subtle.sign('HMAC',secret,encoder.encode('challenge-auth:'+claims.user_id+':'+claims.auth_session_id)));
 const peer=req.headers.get('x-forwarded-for')?.split(',')[0]??'unknown';
 const profile=await rpc('challenge_web_bind',{p_token,p_user:claims.user_id,p_auth_session:claims.auth_session_id,p_peer:hex(await crypto.subtle.digest('SHA-256',encoder.encode(peer)))});
 return {p_token,user:profile.user};
}
