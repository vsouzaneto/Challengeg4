"""Live import acceptance: same account facts converted to Excel; no source facts edited.
Requires explicit --publish and the private original accounts CSV. Never logs capability.
"""
import argparse,csv,io,json,uuid,urllib.request,urllib.error
from pathlib import Path
from openpyxl import Workbook
from http_smoke import request,BASE

def multipart(path,token,fields,filename,payload):
 boundary='challenge-'+uuid.uuid4().hex;parts=[]
 for name,value in fields.items():parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
 parts.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode(),payload,f'\r\n--{boundary}--\r\n'.encode()])
 r=urllib.request.urlopen(urllib.request.Request(BASE+'/'+path,data=b''.join(parts),headers={'Content-Type':'multipart/form-data; boundary='+boundary,'x-challenge-session':token}),timeout=90)
 return json.load(r)

def main():
 p=argparse.ArgumentParser();p.add_argument('--accounts-csv',type=Path,required=True);p.add_argument('--publish',action='store_true');args=p.parse_args()
 token=request('session',{})['token'];before=request('dashboard',token=token)
 with args.accounts_csv.open(newline='',encoding='utf-8-sig') as f:rows=list(csv.reader(f))
 wb=Workbook();ws=wb.active;ws.title='Contas';
 for row in rows:ws.append(row)
 out=io.BytesIO();wb.save(out);payload=out.getvalue()
 inspect=multipart('inspect',token,{},'contas_aceitacao.xlsx',payload);assert inspect['rows']==len(rows)-1 and inspect['sheets']==['Contas']
 mapping={h:h for h in rows[0]};fields={'source':'accounts','reference':before['run']['reference_date'],'sheet':'Contas','mapping':json.dumps(mapping)}
 # Invalid CSV cannot stage or publish a candidate.
 bad=[r[:] for r in rows];bad[1][bad[0].index('seats')]='não é número';buf=io.StringIO();csv.writer(buf).writerows(bad)
 invalid=multipart('preview',token,fields,'invalid.csv',buf.getvalue().encode());assert invalid['accepted'] is False and invalid['error_count']==1
 assert request('dashboard',token=token)['run']['id']==before['run']['id']
 preview=multipart('preview',token,fields,'contas_aceitacao.xlsx',payload);assert preview['accepted'];assert preview['preview']['added']==0 and preview['preview']['removed']==0 and preview['preview']['changed']==0
 print(json.dumps({'excel_inspect':'ok','invalid_types':'blocked','preview':'ok','active_preserved_before_confirmation':True,'rows':inspect['rows']}),flush=True)
 if not args.publish:return
 request('begin',{'id':preview['id']},token);progress=request('advance',{'id':preview['id']},token)
 assert request('dashboard',token=token)['run']['id']==before['run']['id']
 # Resume by calling a fresh request; checkpoints live in Postgres.
 while progress['stage']!='published':progress=request('advance',{'id':preview['id']},token)
 after=request('dashboard',token=token);assert after['run']['id']!=before['run']['id'] and after['run']['id']==progress['run_id']
 assert after['run']['metrics']==before['run']['metrics'] and len(after['quality'])==89
 for a,b in zip(sorted(before['accounts'],key=lambda x:x['account_id']),sorted(after['accounts'],key=lambda x:x['account_id'])):
  assert {k:v for k,v in a.items() if k not in ['id','run_id']}=={k:v for k,v in b.items() if k not in ['id','run_id']},a['account_id']
 assert request('advance',{'id':preview['id']},token)==progress
 old=request('detail',{'id':before['accounts'][0]['id']},token);assert old['snapshot']['run_id']==before['run']['id']
 print(json.dumps({'publication':'ok','resume':'ok','replay':'idempotent','metrics':'unchanged','old_evidence':'preserved','version_count':len(after['versions'])}),flush=True)
if __name__=='__main__':main()
