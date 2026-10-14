"""Live decision acceptance: persists one labeled QA decision with a completed action.
Capabilities stay in memory; no source facts, e-mails, or review requests are changed.
"""
import argparse,json,uuid,urllib.error
from http_smoke import request

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-qa',action='store_true',help='Explicitly allow persisting a labeled QA decision and completed action');args=p.parse_args()
 if not args.write_qa:p.print_help();return
 token=request('session',{})['token'];before=request('dashboard',token=token);snap=before['accounts'][0]
 body={'request_key':str(uuid.uuid4()),'snapshot_id':snap['id'],'title':'[QA] Verificar rastreabilidade da decisão','rationale':'Teste de aceitação: validar que a decisão conserva a versão e os limites da evidência utilizada.','actor':'QA automatizado (sessão declarada)','action':'[QA] Conferir persistência e histórico de transições','responsible':'Validação automatizada','due':'2026-10-13'}
 created=request('decide',body,token);assert request('decide',body,token)==created
 try:request('decide',{**body,'title':'[QA] Conteúdo divergente na mesma chave'},token);raise AssertionError('Conflicting replay allowed')
 except urllib.error.HTTPError as e:assert e.code==400;e.close()
 request('transition',{'id':created['action_id'],'revision':0,'status':'in_progress'},token)
 for invalid,expected_status in [({'id':created['action_id'],'revision':0,'status':'completed','result':'Resultado de teste'},409), ({'id':created['action_id'],'revision':1,'status':'completed','result':''},400)]:
  try:request('transition',invalid,token);raise AssertionError('Invalid transition allowed')
  except urllib.error.HTTPError as e:assert e.code==expected_status;e.close()
 request('transition',{'id':created['action_id'],'revision':1,'status':'completed','result':'Teste concluído: decisão persistente, repetição idempotente, revisão concorrente protegida e resultado obrigatório. Nenhuma inferência causal.'},token)
 after=request('dashboard',token=token);d=next(d for d in after['decisions'] if d['id']==created['decision_id']);a=next(a for a in after['actions'] if a['id']==created['action_id']);h=[h for h in after['history'] if h['action_id']==a['id']]
 assert d['evidence_context']['run']['id']==before['run']['id'];assert a['status']=='completed' and a['revision']==2;assert len(h)==3
 print(json.dumps({'create':'ok','replay':'idempotent','conflicting_replay':'blocked','stale_revision':'blocked','missing_result':'blocked','completion':'ok','history_entries':len(h),'qa_action_status':a['status']}))
if __name__=='__main__':main()
