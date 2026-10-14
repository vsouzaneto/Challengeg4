"""Nonce stays in process memory. Print only its hash; start HTTP after 'run' on stdin.
Requires administrator to insert hash through MCP, deploy fixed-fixture probe, then disable it.
Never reads OPENAI_API_KEY. Public client key comes from the checked-in frontend.
"""
import secrets,hashlib,json,re,sys,urllib.request,urllib.error
from pathlib import Path
nonce=secrets.token_urlsafe(32)
print(json.dumps({'nonce_hash':hashlib.sha256(nonce.encode()).hexdigest()}),flush=True)
if input().strip()!='run':sys.exit(0)
key=re.search(r"SUPABASE_PUBLISHABLE_KEY='([^']+)'",(Path(__file__).resolve().parents[1]/'web/frontend/lib/auth.ts').read_text())[1]
req=urllib.request.Request('https://uxpcrjryxrbwgpakesti.supabase.co/functions/v1/challenge-assistant-probe',headers={'apikey':key,'x-assistant-check':nonce,'Content-Type':'application/json'},data=b'{}')
try:
 with urllib.request.urlopen(req,timeout=120) as r:result=json.load(r)
 print(json.dumps(result),flush=True)
except urllib.error.HTTPError as e:print(json.dumps({'http_status':e.code}),flush=True);e.close()
nonce=None
