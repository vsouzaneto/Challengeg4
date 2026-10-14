import {createClient,type SupabaseClient} from '@supabase/supabase-js';
export const SUPABASE_URL='https://uxpcrjryxrbwgpakesti.supabase.co';
// Public client key. Credentials/privileged keys must never be placed here.
export const SUPABASE_PUBLISHABLE_KEY='sb_publishable_gZlOlDPQ7oqVbH7yaUD7tg_zQ6Bb73h';
let browserClient:SupabaseClient|null=null;
export function getAuthClient(){
 if(typeof window==='undefined')throw Error('Autenticação disponível apenas no navegador.');
 if(!browserClient){localStorage.removeItem('ravenstack_session');browserClient=createClient(SUPABASE_URL,SUPABASE_PUBLISHABLE_KEY,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:false}});}
 return browserClient;
}
