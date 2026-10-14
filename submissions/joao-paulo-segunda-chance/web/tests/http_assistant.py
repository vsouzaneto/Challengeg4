"""Read-only live guards. Authenticated owner testing must use a real login; no token/key extraction."""
import json,urllib.request,urllib.error,re
from pathlib import Path
ROOT='https://uxpcrjryxrbwgpakesti.supabase.co/functions/v1/challenge-assistant/'
KEY=re.search(r"SUPABASE_PUBLISHABLE_KEY='([^']+)'",(Path(__file__).resolve().parents[1]/'frontend/lib/auth.ts').read_text())[1]
checks={}
for route,body in [('assistant-status',None),('assistant-list',{}),('assistant-ask',{'question':'Quantas contas existem?'})]:
 req=urllib.request.Request(ROOT+route,headers={'apikey':KEY,'Content-Type':'application/json'},data=None if body is None else json.dumps(body).encode())
 try:
  with urllib.request.urlopen(req,timeout=30):raise AssertionError('Anonymous route accepted')
 except urllib.error.HTTPError as e:
  assert e.code==401,(route,e.code);checks[route]='blocked';e.close()
print(json.dumps({'guards':checks,'valid_auth_and_openai':'not_attempted','business_writes':0}))
