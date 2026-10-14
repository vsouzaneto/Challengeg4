import { contracts } from './contracts.mjs';

export function parseCsv(text) {
  text=text.replace(/^\uFEFF/,'');
  const first=text.split(/\r?\n/)[0], delimiter=first.includes(',')?',':';';
  const rows=[]; let row=[],value='',quoted=false,after=false;
  for(let i=0;i<text.length;i++) {
    const c=text[i];
    if(quoted) {if(c==='"'){if(text[i+1]==='"'){value+='"';i++;}else{quoted=false;after=true;}}else value+=c;continue;}
    if(c==='"'){if(value||after)throw Error('Aspas em posição inválida no CSV.');quoted=true;continue;}
    if(c===delimiter){row.push(value);value='';after=false;continue;}
    if(c==='\r'||c==='\n'){if(c==='\r'&&text[i+1]==='\n')i++;row.push(value);if(row.some(v=>v!==''))rows.push(row);row=[];value='';after=false;continue;}
    if(after)throw Error('Conteúdo depois das aspas no CSV.');value+=c;
  }
  if(quoted)throw Error('Campo entre aspas não encerrado.');
  row.push(value);if(row.some(v=>v!==''))rows.push(row);
  if(!rows.length)throw Error('Arquivo vazio.');
  const headers=rows.shift().map(x=>x.trim());
  if(rows.some(r=>r.length!==headers.length))throw Error('Quantidade de campos divergente do cabeçalho.');
  return {headers,rows};
}
function convert(v,field) {
  const s=v==null?'':String(v).trim();
  if(!s){if(field.nullable)return null;throw Error('valor obrigatório ausente');}
  if(field.kind==='text')return s;
  if(field.kind==='boolean'){if(!/^(true|false)$/i.test(s))throw Error('use true/false');return s.toLowerCase()==='true';}
  if(field.kind==='integer'||field.kind==='numeric') {
    if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s))throw Error('número inválido');
    const n=Number(s);if(!Number.isFinite(n)||n<0||(field.kind==='integer'&&!Number.isSafeInteger(n)))throw Error('número não negativo fora do contrato');return field.kind==='numeric'?s:n;
  }
  if(field.kind==='date'){if(!/^\d{4}-\d{2}-\d{2}$/.test(s)||!Number.isFinite(Date.parse(s))||new Date(s).toISOString().slice(0,10)!==s)throw Error('data ISO inválida (AAAA-MM-DD)');return s;}
  // Source timestamps have no timezone. Never invent a local offset.
  if(/^\d{4}-\d{2}-\d{2}$/.test(s)){convert(s,{kind:'date'});return `${s}T00:00:00`;}
  if(!/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?$/.test(s))throw Error('timestamp ISO sem fuso esperado');
  const [day,time]=s.split(/[T ]/);convert(day,{kind:'date'});
  const [h,m,sec]=time.split(':').map(Number);if(h>23||m>59||sec>=60)throw Error('hora inválida');return `${day}T${time}`;
}
export function normalizeRows(source,headers,rows) {
  const c=contracts[source];if(!c)throw Error('Fonte desconhecida.');
  if(new Set(headers).size!==headers.length)throw Error('Cabeçalhos repetidos.');
  const required=Object.keys(c),missing=required.filter(k=>!headers.includes(k)),extra=headers.filter(k=>!required.includes(k));
  if(missing.length||extra.length)throw Error(`Colunas ausentes: ${missing.join(', ')||'nenhuma'}. Extras: ${extra.join(', ')||'nenhuma'}.`);
  const errors=[],normalized=[],raw=[];
  rows.forEach((r,i)=>{
    const original=Object.fromEntries(headers.map((h,j)=>[h,r[j]==null?'':String(r[j])])),n={};raw.push(original);
    try{if(r.length!==headers.length)throw Error('Campos insuficientes');for(const [k,f]of Object.entries(c)){try{n[k]=convert(original[k],f);}catch(e){throw Error(`${k}: ${e.message}`);}}normalized.push(n);}
    catch(e){errors.push({row:i+2,message:e.message});}
  });return {raw,normalized,errors};
}
const keys={accounts:'account_id',subscriptions:'subscription_id',usage:'usage_id',support:'ticket_id',churn:'churn_event_id'};
const stable=r=>JSON.stringify(Object.keys(r).sort().map(k=>[k,String(r[k]??'')]));
export function compareSources(source,oldRows,newRows) {
  const key=keys[source],group=rows=>{const m=new Map();for(const r of rows){const k=r[key];if(!m.has(k))m.set(k,[]);m.get(k).push(stable(r));}for(const a of m.values())a.sort();return m;};
  const old=group(oldRows),now=group(newRows);
  return {added:[...now.keys()].filter(k=>!old.has(k)).length,removed:[...old.keys()].filter(k=>!now.has(k)).length,changed:[...now].filter(([k,v])=>old.has(k)&&JSON.stringify(v)!==JSON.stringify(old.get(k))).length,old_rows:oldRows.length,new_rows:newRows.length};
}
export function auditSources(data) {
  const findings=[],blockers=[],f={};
  const add=(code,rows,test,interpretation,policy='Preservar origem e revisar definição.',kind='quality',key)=>{
    const selected=rows.filter(test); const entry={code,kind,count:selected.length,denominator:rows.length,interpretation,policy,examples:selected.slice(0,10).map(r=>r[key??keys[code.split('.')[0]]]??r.account_id)};findings.push(entry);return entry;
  };
  const blank=v=>v==null||String(v).trim()==='',num=v=>blank(v)?null:Number(v);
  const counts=(rows,key)=>{const m=new Map();for(const r of rows)m.set(r[key],(m.get(r[key])??0)+1);return m;};
  for(const name of Object.keys(contracts)) {
    const rows=data[name]??[],key=keys[name],repeated=counts(rows,key),seen=new Set();
    add(`${name}.blank_key`,rows,r=>blank(r[key]),'Chave ausente.','Bloquear publicação.');
    const dup=add(`${name}.repeated_key_rows`,rows,r=>repeated.get(r[key])>1,'Linhas com IDs repetidos.','Uso conflitante é preservado e excluído das medidas; demais chaves bloqueiam publicação.');
    if(name!=='usage'&&dup.count)blockers.push(dup);
    add(`${name}.exact_duplicate_excess`,rows,r=>{const s=stable(r),has=seen.has(s);seen.add(s);return has;},'Repetição exata além da primeira linha.');
    f[name]=rows.map(r=>{const n={...r};for(const [k,field]of Object.entries(contracts[name])) {
      if(field.kind==='date'||field.kind==='timestamp')n[k]=blank(r[k])?null:String(r[k]).replace(' ','T');
      else if(field.kind==='numeric'||field.kind==='integer')n[k]=num(r[k]);
      else if(field.kind==='boolean')n[k]=r[k]===true||String(r[k]).toLowerCase()==='true';
    }return n;});
    for(const [k,field]of Object.entries(contracts[name])) {
      if(field.kind==='date'||field.kind==='timestamp')add(`${name}.invalid_${k}`,rows,r=>{if(blank(r[k]))return false;try{convert(r[k],field);return false;}catch{return true;}},'Data não interpretável.','Bloquear publicação.');
      if(field.kind==='numeric'||field.kind==='integer') {
        add(`${name}.invalid_${k}`,rows,r=>!blank(r[k])&&!Number.isFinite(Number(r[k])),'Número não interpretável.','Bloquear publicação.');
        add(`${name}.negative_${k}`,rows,r=>Number(r[k])<0,'Valor negativo.','Bloquear publicação.');
      }
      if(field.kind==='boolean')add(`${name}.invalid_${k}`,rows,r=>!/^(true|false)$/i.test(String(r[k]).trim()),'Booleano fora de true/false.','Bloquear publicação.');
    }
  }
  const {accounts:a,subscriptions:s,usage:u,support:t,churn:c}=f,am=new Map(a.map(r=>[r.account_id,r])),sm=new Map(s.map(r=>[r.subscription_id,r]));
  for(const [name,parent,field]of [['subscriptions',am,'account_id'],['usage',sm,'subscription_id'],['support',am,'account_id'],['churn',am,'account_id']]) {
    const q=add(`${name}.orphan`,f[name],r=>!parent.has(r[field]),'Relacionamento sem pai na versão.','Bloquear publicação.');if(q.count)blockers.push(q);
  }
  const lt=(x,y)=>x!=null&&y!=null&&x<y,gt=(x,y)=>x!=null&&y!=null&&x>y;
  for(const [name,col]of [['subscriptions','start_date'],['support','submitted_at'],['churn','churn_date']])add(`${name}.before_signup`,f[name],r=>lt(r[col],am.get(r.account_id)?.signup_date),'Fato anterior ao cadastro.');
  const linked=u.map(r=>({...r,...{account_id:sm.get(r.subscription_id)?.account_id,start_date:sm.get(r.subscription_id)?.start_date,end_date:sm.get(r.subscription_id)?.end_date,signup_date:am.get(sm.get(r.subscription_id)?.account_id)?.signup_date}}));
  add('usage.before_signup',linked,r=>lt(r.usage_date,r.signup_date),'Uso anterior ao cadastro.','Excluir da análise temporal qualificada.');
  add('usage.before_subscription',linked,r=>lt(r.usage_date,r.start_date),'Uso anterior à assinatura.','Excluir da análise temporal qualificada.');
  add('usage.after_subscription_end',linked,r=>gt(r.usage_date,r.end_date),'Uso após término registrado.','Excluir da análise temporal qualificada.');
  add('usage.errors_above_count',u,r=>r.error_count>r.usage_count,'Erros acima da quantidade; semântica precisa ser confirmada.');
  add('usage.zero_count_with_activity',u,r=>r.usage_count===0&&(r.error_count>0||r.usage_duration_secs>0),'Quantidade zero com duração/erros.');
  add('subscriptions.end_before_start',s,r=>lt(r.end_date,r.start_date),'Intervalo contratual invertido.','Excluir linha do cálculo contratual.');
  add('subscriptions.arr_mrr_mismatch',s,r=>Math.abs(r.arr_amount-r.mrr_amount*12)>1e-6,'ARR diferente de 12 × MRR.');
  add('subscriptions.churn_without_end',s,r=>r.churn_flag&&!r.end_date,'Cancelamento sem término registrado.');
  add('subscriptions.end_without_churn',s,r=>!r.churn_flag&&!!r.end_date,'Término sem flag de cancelamento.');
  add('subscriptions.upgrade_and_downgrade',s,r=>r.upgrade_flag&&r.downgrade_flag,'Ambas as flags podem representar histórico.');
  const elapsed=r=>r.closed_at&&r.submitted_at?(Date.parse(r.closed_at+'Z')-Date.parse(r.submitted_at+'Z'))/3600000:null;
  add('support.closed_before_submitted',t,r=>lt(r.closed_at,r.submitted_at),'Encerramento anterior à abertura.');
  add('support.duration_mismatch',t,r=>elapsed(r)!=null&&r.resolution_time_hours!=null&&Math.abs(elapsed(r)-r.resolution_time_hours)>1e-6,'Duração difere de encerramento menos abertura.');
  add('support.response_after_closure',t,r=>elapsed(r)!=null&&r.first_response_time_minutes>elapsed(r)*60,'Primeira resposta após duração total.','Excluir da medida de resolução qualificada.');
  add('support.missing_satisfaction',t,r=>r.satisfaction_score==null,'Ausência de nota não significa insatisfação.','Mostrar respondentes e denominador.','coverage');
  add('support.invalid_satisfaction_range',t,r=>r.satisfaction_score!=null&&(r.satisfaction_score<1||r.satisfaction_score>5),'Nota fora da escala proposta 1–5.');
  const actual=c.filter(r=>!r.is_reactivation),any=new Set(c.map(r=>r.account_id)),cancel=new Set(actual.map(r=>r.account_id));
  add('churn.flag_true_without_any_event',a,r=>r.churn_flag&&!any.has(r.account_id),'Churn cadastral sem evento: data, motivo e perda indeterminados.','Reconciliar com a origem.','reconciliation','account_id');
  add('churn.flag_true_only_reactivation',a,r=>r.churn_flag&&any.has(r.account_id)&&!cancel.has(r.account_id),'Flag de churn com apenas reativação.','Não criar cancelamento sintético.','reconciliation','account_id');
  add('churn.flag_false_with_churn',a,r=>!r.churn_flag&&cancel.has(r.account_id),'Evento histórico e cadastro divergem; status atual não demonstrado.','Reconstruir episódios.','reconciliation','account_id');
  const dayCounts=counts(actual.map(r=>({...r,key:r.account_id+'|'+r.churn_date})),'key');
  add('churn.repeated_account_day_rows',actual,r=>dayCounts.get(r.account_id+'|'+r.churn_date)>1,'Mais de um evento da conta no mesmo dia.','Não equiparar eventos a contas.','reconciliation');
  add('churn.upgrade_and_downgrade',c,r=>r.preceding_upgrade_flag&&r.preceding_downgrade_flag,'Movimentos prévios sem datas individuais.','Não atribuir data da assinatura às mudanças.','limitation');
  const first=new Map();for(const r of actual)if(!first.has(r.account_id)||r.churn_date<first.get(r.account_id))first.set(r.account_id,r.churn_date);
  for(const [name,rows,col]of [['usage',linked,'usage_date'],['support',t,'submitted_at']])add(`${name}.after_first_churn`,rows,r=>gt(r[col],first.get(r.account_id)),'Fato após primeiro churn não prova erro: há reativação/contratos simultâneos.','Reconstruir episódios.','reconciliation');
  const byAccount=new Map();for(const r of s){if(!byAccount.has(r.account_id))byAccount.set(r.account_id,[]);byAccount.get(r.account_id).push(r);}
  add('churn.event_with_other_open_contract',actual,r=>(byAccount.get(r.account_id)??[]).some(x=>x.start_date<=r.churn_date&&(!x.end_date||x.end_date>r.churn_date)),'Evento de churn coexistindo com contrato aberto.','Não somar todo MRR como perda.','reconciliation');
  add('churn.event_without_same_day_subscription_end',actual,r=>!(byAccount.get(r.account_id)??[]).some(x=>x.end_date===r.churn_date),'Evento sem término contratual no mesmo dia.','Vínculo financeiro indeterminado.','reconciliation');
  add('churn.reactivation_without_prior_churn',c.filter(r=>r.is_reactivation),r=>!first.has(r.account_id)||r.churn_date<=first.get(r.account_id),'Reativação sem cancelamento estritamente anterior.','Histórico insuficiente.','reconciliation');
  let reference=null;for(const name of Object.keys(contracts))for(const r of f[name])for(const [k,field]of Object.entries(contracts[name]))if((field.kind==='date'||field.kind==='timestamp')&&r[k]&&(!reference||r[k]>reference))reference=r[k];
  const cutoff=reference?.slice(0,10),opened=new Set(s.filter(r=>r.start_date<=cutoff&&(!r.end_date||r.end_date>cutoff)).map(r=>r.account_id));
  add('churn.flag_true_with_open_contract_at_source_end',a,r=>r.churn_flag&&opened.has(r.account_id),'Flag cadastral com contrato aberto no corte observado.','Distinguir cadastro e carteira contratual.','reconciliation','account_id');
  let observed=null;for(const [name,col]of [['accounts','signup_date'],['subscriptions','start_date'],['usage','usage_date'],['support','submitted_at'],['churn','churn_date']])for(const r of f[name])if(r[col]&&(!observed||r[col].slice(0,10)>observed))observed=r[col].slice(0,10);
  return {audit_version:'web-1.0.0',findings,blockers,reference_date:cutoff,observed_fact_date:observed};
}
