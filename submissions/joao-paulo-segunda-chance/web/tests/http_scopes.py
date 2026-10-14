"""Acceptance of deployed explicit scopes. Read-only by default; --write-qa persists one labeled QA decision and completes its action."""
import argparse,json,uuid,urllib.request,urllib.error
from http_smoke import request as legacy
BASE='https://uxpcrjryxrbwgpakesti.supabase.co/functions/v1/challenge-decisions'
def request(path,body,token=None):
 headers={'Content-Type':'application/json'}
 if token:headers['x-challenge-session']=token
 with urllib.request.urlopen(urllib.request.Request(BASE+'/'+path,data=json.dumps(body).encode(),headers=headers),timeout=30) as r:return json.load(r)
def reject(path,body,token,status):
 try:request(path,body,token);raise AssertionError('Invalid operation accepted')
 except urllib.error.HTTPError as e:assert e.code==status,(e.code,e.read().decode());e.close()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-qa',action='store_true');args=p.parse_args()
 token=legacy('session',{})['token'];dashboard=legacy('dashboard',token=token);run=dashboard['run']['id'];base={'run_id':run}
 reject('scope-options',base,None,401)
 options=request('scope-options',base,token);assert len(options['metrics'])==6
 first=dashboard['accounts'][0];account=request('scope-preview',{**base,'scope':{'type':'account','account_id':first['account_id']},'metric':'contract_mrr'},token);assert account['population_count']==1 and account['measure']['value']==first['contract_mrr']
 scope={'type':'segment','industry':first['industry']};members=[a for a in dashboard['accounts'] if a['industry']==first['industry']]
 preview=request('scope-preview',{**base,'scope':scope,'metric':'missing_cancel'},token);assert preview['population_count']==len(members);assert preview['affected_count']==sum(a['reconciliation_state'] in ['flag_without_event','flag_with_reactivation_only'] for a in members)
 weighted=request('scope-preview',{**base,'scope':scope,'metric':'satisfaction'},token);respondents=sum(a['satisfaction_responses'] for a in members);assert weighted['measure']['numerator']==respondents
 if respondents:assert abs(weighted['measure']['value']-sum((a['mean_satisfaction'] or 0)*a['satisfaction_responses'] for a in members)/respondents)<1e-9
 portfolio=request('scope-preview',{**base,'scope':{'type':'portfolio'},'metric':'contract_mrr'},token);assert portfolio['population_count']==len(dashboard['accounts']);assert portfolio['measure']['value']==dashboard['run']['metrics']['contract_mrr']
 if options['quality']:
  check=options['quality'][0];q=request('scope-preview',{**base,'scope':{'type':'quality','source':check['sources'][0],'check_code':check['code']},'metric':'quality_check'},token);assert q['members']==[] and q['population_count']==check['denominator']
 reject('scope-preview',{**base,'scope':{'type':'segment'},'metric':'contract_mrr'},token,400)
 reject('scope-preview',{**base,'scope':{'type':'portfolio','country':'BR'},'metric':'contract_mrr'},token,400)
 result={'account':'passed','segment':'passed','portfolio':'passed','quality':'passed' if options['quality'] else 'no_occurrences','weighted_satisfaction':'passed','invalid_scope':'blocked','write':'not_requested'}
 if args.write_qa:
  body={**base,'scope':scope,'metric':'missing_cancel','preview_hash':preview['preview_hash'],'request_key':str(uuid.uuid4()),'title':'[QA] Validar decisão com recorte explícito','rationale':'Teste de aceitação de população e evidência congeladas; não é decisão do CEO.','actor':'QA automatizado (sessão declarada)','action':'[QA] Conferir vínculos do recorte','responsible':'Validação automatizada','due':'2026-10-13'}
  reject('decide-scoped',{**body,'preview_hash':'0'*64},token,409)
  created=request('decide-scoped',body,token);assert request('decide-scoped',body,token)==created
  reject('decide-scoped',{**body,'title':'[QA] Conteúdo divergente na mesma chave'},token,409)
  legacy('transition',{'id':created['action_id'],'revision':0,'status':'in_progress'},token)
  legacy('transition',{'id':created['action_id'],'revision':1,'status':'completed','result':'Teste de recorte concluído; evidência e contas vinculadas à versão original. Sem inferência causal.'},token)
  after=legacy('dashboard',token=token);decision=next(d for d in after['decisions'] if d['id']==created['decision_id']);action=next(a for a in after['actions'] if a['id']==created['action_id']);assert decision['evidence_context']==preview;assert action['status']=='completed';assert len([h for h in after['history'] if h['action_id']==action['id']])==3
  result['write']='QA_completed_with_frozen_evidence_and_idempotency'
 print(json.dumps(result))
if __name__=='__main__':main()
