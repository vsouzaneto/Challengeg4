import {adoptSession,setSession,subscribe} from './session.ts';

const originalFetch=globalThis.fetch;
const calls:string[]=[];
globalThis.fetch=async input=>{
 const url=String(input);calls.push(url);
 if(url.includes('/events?'))return new Response(JSON.stringify({detail:'Cursor posterior ao log; recarregue o snapshot.'}),{status:422,headers:{'Content-Type':'application/json'}});
 if(url.endsWith('/snapshot'))return new Response(JSON.stringify({session_id:'resync',last_seq:7,state:'PAUSED'}),{headers:{'Content-Type':'application/json'}});
 throw Error(`Rota inesperada: ${url}`);
};
let resolveResync:(()=>void)|undefined;
const resynced=new Promise<void>(resolve=>resolveResync=resolve);
const off=subscribe(snapshot=>{if(snapshot?.last_seq===7)resolveResync?.();});
try{
 adoptSession({session_id:'resync',last_seq:999,state:'PLAYING'});
 await Promise.race([resynced,new Promise((_,reject)=>setTimeout(()=>reject(Error('Polling não refez o snapshot')),2500))]);
 if(!calls.some(url=>url.includes('/events?after_seq=999'))||!calls.some(url=>url.endsWith('/snapshot')))throw Error('Cursor inválido não foi reconciliado pelo snapshot.');
 console.log('Sessão: cursor inválido recuperado por snapshot.');
}finally{
 off();await setSession('');globalThis.fetch=originalFetch;
}
