import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCsv, normalizeRows, compareSources, auditSources } from '../domain/import.mjs';
import { contracts } from '../domain/contracts.mjs';
const account={account_id:'a',account_name:'A',industry:'SaaS',country:'BR',referral_source:'web',plan_tier:'pro',seats:'3',is_trial:'false',churn_flag:'true',signup_date:'2024-01-01'};
test('CSV preserva vírgula, quebra de linha e aspas nos campos',()=>{assert.deepEqual(parseCsv('\ufeffid,note\r\n1,"a,b\n""c"""\r\n'),{headers:['id','note'],rows:[['1','a,b\n"c"']]});});
test('CSV incompleto não é aceito silenciosamente',()=>{assert.throws(()=>parseCsv('a,b\n"não fecha'));assert.throws(()=>parseCsv('a,b\n1,2,3'));});
test('Cabeçalho repetido ou extra é bloqueante',()=>{const h=Object.keys(account);assert.throws(()=>normalizeRows('accounts',[...h,'seats'],[[...Object.values(account),'2']]));assert.throws(()=>normalizeRows('accounts',[...h,'extra'],[[...Object.values(account),'x']]));});
test('Não converte ausente para zero/falso',()=>{const h=Object.keys(account);const rows=normalizeRows('accounts',h,[[...Object.values({...account,seats:'',churn_flag:''})]]);assert.equal(rows.errors.length,1);assert.equal(rows.normalized.length,0);});
test('Datas, inteiros e booleanos estritos',()=>{for(const change of [{signup_date:'2024-02-30'},{seats:'3.1'},{seats:'Infinity'},{churn_flag:'1'}]) assert.equal(normalizeRows('accounts',Object.keys(account),[Object.values({...account,...change})]).errors.length,1);});
test('Contrato válido mantém flag e data sem projetar histórico',()=>{const n=normalizeRows('accounts',Object.keys(account),[Object.values(account)]);assert.equal(n.errors.length,0);assert.equal(n.normalized[0].churn_flag,true);assert.equal(n.normalized[0].signup_date,'2024-01-01');});
test('Comparação de fonte registra removidos e não faz upsert implícito',()=>{const old=[account,{...account,account_id:'b'}], now=[{...account,seats:'4'},{...account,account_id:'c'}];assert.deepEqual(compareSources('accounts',old,now),{added:1,removed:1,changed:1,old_rows:2,new_rows:2});});
test('Churn cadastral sem eventos é indeterminado; uso conflitante preservado',()=>{const data={accounts:[account],subscriptions:[],usage:[],support:[],churn:[]};const result=auditSources(data);assert.equal(result.findings.find(x=>x.code==='churn.flag_true_without_any_event').count,1);assert.equal(result.blockers.length,0);assert.equal(result.findings.length,89);});
test('Chave pai repetida e FK órfã impedem publicação',()=>{const d={accounts:[account,account],subscriptions:[{subscription_id:'s',account_id:'missing'}],usage:[],support:[],churn:[]};assert.ok(auditSources(d).blockers.some(x=>x.code==='accounts.repeated_key_rows'));assert.ok(auditSources(d).blockers.some(x=>x.code==='subscriptions.orphan'));});
test('As cinco estruturas oficiais estão disponíveis',()=>{assert.deepEqual(Object.keys(contracts).sort(),['accounts','churn','subscriptions','support','usage']);});
test('Término futuro de contrato não projeta cobertura factual para o futuro',()=>{
 const a={...account,signup_date:'2024-01-01'},s={subscription_id:'s',account_id:'a',plan_tier:'pro',billing_frequency:'monthly',seats:'1',mrr_amount:'10',arr_amount:'120',is_trial:'false',upgrade_flag:'false',downgrade_flag:'false',churn_flag:'true',auto_renew_flag:'false',start_date:'2024-02-01',end_date:'2030-01-01'};
 assert.equal(auditSources({accounts:[a],subscriptions:[s],usage:[],support:[],churn:[]}).observed_fact_date,'2024-02-01');
});
