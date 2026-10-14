// Scope value object and applicability specifications. No database, DOM or metrics.
const fields={account:['account_id'],segment:['industry','country'],portfolio:[],quality:['source','check_code']};
const metrics=['missing_cancel','cadastral_churn','contract_mrr','observed_usage','satisfaction'];
export function normalizeScope(input){
 if(!input||Array.isArray(input)||typeof input!=='object'||typeof input.type!=='string'||!Object.hasOwn(fields,input.type))throw Error('Selecione um escopo válido.');
 const allowed=['type',...fields[input.type]];
 if(Object.keys(input).some(k=>!allowed.includes(k)))throw Error('Filtro incompatível com o escopo.');
 const out={type:input.type};
 for(const k of fields[input.type])if(Object.hasOwn(input,k)){
  if(typeof input[k]!=='string'||input[k].length>200)throw Error('Valor de escopo inválido.');
  const value=input[k].trim();if(value)out[k]=value;
 }
 if(out.type==='account'&&!out.account_id)throw Error('Selecione uma conta.');
 if(out.type==='segment'&&!out.industry&&!out.country)throw Error('Selecione setor ou país.');
 if(out.type==='quality'&&(!['accounts','subscriptions','usage','support','churn'].includes(out.source)||!out.check_code))throw Error('Selecione fonte e verificação.');
 return out;
}
export function validateMetric(scope,metric){
 if(scope.type==='quality'?metric!=='quality_check':!metrics.includes(metric))throw Error('Dado incompatível com o escopo.');return metric;
}
