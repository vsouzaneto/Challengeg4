// Parse claims ONLY after Supabase Auth /user has verified the bearer token.
// This module is not a signature verifier and must never authorize a token alone.
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export function verifiedIdentity(jwt,user,now=Date.now()/1000){
 if(!user?.id||user.is_anonymous)throw Error('Sessão de usuário inválida.');
 let claims;try{const parts=jwt.split('.');if(parts.length!==3)throw Error();const raw=parts[1].replaceAll('-','+').replaceAll('_','/');claims=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(raw.padEnd(Math.ceil(raw.length/4)*4,'=')),c=>c.charCodeAt(0))));}catch{throw Error('Sessão de usuário inválida.');}
 if(!uuid.test(claims.sub)||claims.sub!==user.id||!uuid.test(claims.session_id)||typeof claims.exp!=='number'||!Number.isFinite(claims.exp)||claims.exp<=now)throw Error('Sessão ausente ou expirada.');
 return {user_id:user.id,auth_session_id:claims.session_id};
}
