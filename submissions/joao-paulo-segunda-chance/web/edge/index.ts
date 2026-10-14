import {authenticate} from './auth.ts';
import ExcelJS from 'npm:exceljs@4.4.0';
import { Buffer } from 'node:buffer';
import { contracts } from '../domain/contracts.mjs';
import {parseCsv,normalizeRows,auditSources,compareSources} from '../domain/import.mjs';

const url=Deno.env.get('SUPABASE_URL')!;
const key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!; // Built-in runtime secret. Never returned.
const headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'content-type,authorization,apikey','Access-Control-Allow-Methods':'GET,POST,OPTIONS','Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
const response=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers});
const hash=async(bytes:Uint8Array)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
const textHash=(s:string)=>hash(new TextEncoder().encode(s));
async function rpc(name:string,args:Record<string,unknown>={}) {
 const res=await fetch(`${url}/rest/v1/rpc/${name}`,{method:'POST',headers:{apikey:key,Authorization:`Bearer ${key}`,'Content-Type':'application/json'},body:JSON.stringify(args)});
 const body=await res.json();if(!res.ok){const e=new Error(body.message??'Erro no banco.');(e as any).code=body.code;throw e;}return body;
}
function checkZip(bytes:Uint8Array) {
 const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);let end=-1;
 for(let i=bytes.length-22;i>=Math.max(0,bytes.length-65557);i--)if(view.getUint32(i,true)===0x06054b50){end=i;break;}
 if(end<0)throw Error('Excel não é um arquivo .xlsx válido.');
 const count=view.getUint16(end+10,true),start=view.getUint32(end+16,true);if(count>1500)throw Error('Excel excede o limite de entradas.');
 let at=start,total=0;for(let i=0;i<count;i++){if(at+46>bytes.length||view.getUint32(at,true)!==0x02014b50)throw Error('Estrutura Excel inválida.');total+=view.getUint32(at+24,true);at+=46+view.getUint16(at+28,true)+view.getUint16(at+30,true)+view.getUint16(at+32,true);}
 if(total>64*1024*1024)throw Error('Excel descompactado excede 64 MB. Divida o arquivo.');
}
async function readFile(file:File,sheet?:string) {
 if(!file.size||file.size>8*1024*1024)throw Error('Envie arquivo não vazio de até 8 MB.');
 const bytes=new Uint8Array(await file.arrayBuffer());
 if(file.name.toLowerCase().endsWith('.csv'))return {...parseCsv(new TextDecoder('utf-8',{fatal:true}).decode(bytes)),bytes,sheets:[]};
 if(!file.name.toLowerCase().endsWith('.xlsx'))throw Error('Formato aceito: CSV UTF-8 ou Excel .xlsx.');
 checkZip(bytes);const wb=new ExcelJS.Workbook();await wb.xlsx.load(Buffer.from(bytes));
 const sheets=wb.worksheets.map(s=>s.name),ws=sheet?wb.getWorksheet(sheet):wb.worksheets[0];if(!ws)throw Error('Aba não encontrada.');
 if(ws.rowCount>50001||ws.columnCount>128)throw Error('Excel excede 50.000 linhas ou 128 colunas.');
 function cellValue(cell:any){const v=cell.value;if(v==null)return '';if(v instanceof Date)return v.toISOString().replace(/\.000Z$/,'');if(typeof v==='object'){if(v.formula||v.sharedFormula)throw Error('Fórmulas não são aceitas. Exporte os valores calculados.');if(v.richText)return v.richText.map((x:any)=>x.text).join('');if(v.text)return v.text;throw Error('Célula com tipo não suportado.');}return String(v);}
 const matrix:string[][]=[];ws.eachRow({includeEmpty:false},row=>{const values=Array.from({length:ws.columnCount},(_,i)=>cellValue(row.getCell(i+1)));if(values.some(x=>x!==''))matrix.push(values);});
 if(!matrix.length)throw Error('Aba vazia.');const h=matrix.shift()!;while(h.at(-1)==='')h.pop();
 return {headers:h.map(x=>x.trim()),rows:matrix.map(r=>r.slice(0,h.length)),bytes,sheets};
}
Deno.serve(async(req:Request)=>{
 if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
 try{
  const path=new URL(req.url).pathname.split('/').pop();
  const {p_token,user}=await authenticate(req,rpc,url,key);
  if(path==='session')return response({user});
  if(path==='logout'&&req.method==='POST')return response(await rpc('challenge_web_logout',{p_token}));
  if(path==='dashboard'&&req.method==='GET')return response({...await rpc('challenge_web_dashboard',{p_token}),user});
  if(path==='inspect'||path==='preview'){
   if(req.method!=='POST')return response({error:'Método não permitido.'},405);
   // Check capability before parsing untrusted uploads.
   const current=await rpc('challenge_web_sources',{p_token});
   if(Number(req.headers.get('content-length')??0)>9*1024*1024)throw Error('Arquivo excede o limite.');
   const form=await req.formData(),file=form.get('file');if(!(file instanceof File))throw Error('Selecione um arquivo.');
   const parsed=await readFile(file,String(form.get('sheet')??'')||undefined);
   if(path==='inspect')return response({headers:parsed.headers,sheets:parsed.sheets,rows:parsed.rows.length});
   const source=String(form.get('source')),contract=contracts[source as keyof typeof contracts];if(!contract)throw Error('Fonte desconhecida.');
   let h=parsed.headers,rows=parsed.rows;
   const mapping=JSON.parse(String(form.get('mapping')??'null'));
   if(mapping){h=Object.keys(contract);const indices=h.map(k=>parsed.headers.indexOf(mapping[k]));if(indices.some(i=>i<0)||new Set(indices).size!==indices.length)throw Error('Mapeie cada coluna obrigatória para uma coluna distinta.');rows=parsed.rows.map(r=>indices.map((i,j)=>{const v=r[i];return (contract as any)[h[j]].kind==='date'&&/^\d{4}-\d{2}-\d{2}T00:00:00$/.test(v)?v.slice(0,10):v;}));}
   if(!rows.length||rows.length>50000)throw Error('Envie entre 1 e 50.000 linhas.');
   const prepared=normalizeRows(source,h,rows);if(prepared.errors.length)return response({accepted:false,errors:prepared.errors.slice(0,100),error_count:prepared.errors.length});
   const merged={...current.sources,[source]:prepared.raw};const audit=auditSources(merged);
   if(audit.blockers.length)return response({accepted:false,blockers:audit.blockers,errors:[]});
   const reference=String(form.get('reference'));if(!/^\d{4}-\d{2}-\d{2}$/.test(reference)||new Date(reference).toISOString().slice(0,10)!==reference||!audit.observed_fact_date||reference>audit.observed_fact_date)throw Error('Data de referência inválida ou além das fontes observadas.');
   const diff=compareSources(source,current.sources[source],prepared.raw),quality=audit.findings.filter((x:any)=>x.count>0);
   const preview={...diff,quality,reference_date:reference,parent_reference_date:current.run.reference_date,source_type:source,mapping,original_headers:parsed.headers,sheet:String(form.get('sheet')??''),warnings:['Substitui esta fonte inteira. As outras quatro fontes são reutilizadas.','Ausência de registros não confirma ausência de uso.']};
   const packed=prepared.raw.map((r:any,i:number)=>[i+1,h.map(k=>r[k]),h.map(k=>prepared.normalized[i][k]==null?null:String(prepared.normalized[i][k])),[]]);
   const id=await rpc('challenge_web_stage',{p_token,p_parent:current.run.id,p_source:source,p_filename:file.name,p_hash:await hash(parsed.bytes),p_base64:Buffer.from(parsed.bytes).toString('base64'),p_headers:h,p_rows:packed,p_checks:audit.findings,p_preview:preview,p_reference:reference});
   return response({accepted:true,id,preview});
  }
  if(req.method!=='POST')return response({error:'Rota ou método desconhecido.'},404);
  const body=await req.json();
  if(path==='detail')return response(await rpc('challenge_web_detail',{p_token,p_snapshot:body.id}));
  if(path==='begin'||path==='advance')return response(await rpc(`challenge_web_${path}`,{p_token,p_upload:body.id}));
  if(path==='decide')return response(await rpc('challenge_web_decide',{p_token,p_request:body.request_key,p_evidence:body.evidence_id??null,p_snapshot:body.snapshot_id??null,p_title:body.title,p_rationale:body.rationale,p_actor:user.name,p_action:body.action,p_responsible:body.responsible,p_due:body.due}));
  if(path==='transition')return response(await rpc('challenge_web_transition',{p_token,p_action:body.id,p_revision:body.revision,p_status:body.status,p_result:body.result??null}));
  return response({error:'Operação desconhecida.'},404);
 }catch(e){return response({error:(e as Error).message},(e as any).code==='28000'?401:(e as any).code==='PT409'?409:(e as any).code==='PT403'?403:(e as any).code==='PT503'?503:400);}
});
