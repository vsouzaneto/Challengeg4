"""Auth acceptance. --guards-only is read-only. Account login prompts password securely, never via CLI arguments or files."""
import argparse,json,getpass,re,urllib.request,urllib.error
from pathlib import Path
ROOT='https://uxpcrjryxrbwgpakesti.supabase.co'
KEY=re.search(r"SUPABASE_PUBLISHABLE_KEY='([^']+)'",(Path(__file__).resolve().parents[1]/'frontend/lib/auth.ts').read_text())[1]
def call(url,body=None,jwt=None,extra=None):
 headers={'apikey':KEY,'Content-Type':'application/json',**(extra or {})}
 if jwt:headers['Authorization']='Bearer '+jwt
 with urllib.request.urlopen(urllib.request.Request(ROOT+url,data=None if body is None else json.dumps(body).encode(),headers=headers),timeout=30) as r:return json.load(r)
def reject(url,body=None,jwt=None,extra=None,expected=401):
 try:call(url,body,jwt,extra);raise AssertionError('Unprotected request accepted')
 except urllib.error.HTTPError as e:assert e.code==expected,(e.code,url);e.close()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guards-only',action='store_true');p.add_argument('--legacy-blocks',action='store_true',help='Verify old endpoints after login activation; no business writes.');p.add_argument('--email');p.add_argument('--expect-role',choices=['super_admin','administrator','user']);args=p.parse_args()
 reject('/functions/v1/challenge-auth-web/dashboard')
 reject('/functions/v1/challenge-auth-decisions/scope-options',{'run_id':'synthetic'})
 reject('/functions/v1/challenge-auth-web/session',{},extra={'x-challenge-session':'obsolete-capability'})
 reject('/functions/v1/challenge-auth-web/dashboard',jwt='invalid.jwt.signature')
 if args.legacy_blocks:
  reject('/functions/v1/challenge-web/session',{})
  reject('/functions/v1/challenge-web/dashboard')
  reject('/functions/v1/challenge-decisions/scope-options',{'run_id':'synthetic'})
 if args.guards_only:
  result={'anonymous_read':'blocked','anonymous_decision_route':'blocked','legacy_capability':'blocked','invalid_jwt':'blocked','valid_account_login':'not_attempted'}
  if args.legacy_blocks:result.update({'legacy_session_creation':'blocked','legacy_dashboard':'blocked','legacy_decisions':'blocked'})
  print(json.dumps(result));return
 if not args.email or not args.expect_role:p.error('--email and --expect-role are required without --guards-only')
 password=getpass.getpass('Supabase account password (not saved): ')
 tokens=call('/auth/v1/token?grant_type=password',{'email':args.email,'password':password});password=None;jwt=tokens['access_token']
 try:
  profile=call('/functions/v1/challenge-auth-web/session',jwt=jwt)['user'];assert profile['role']==args.expect_role
  d=call('/functions/v1/challenge-auth-web/dashboard',jwt=jwt);assert d['user']['id']==profile['id'] and len(d['sources'])==5
  options=call('/functions/v1/challenge-auth-decisions/scope-options',{'run_id':d['run']['id']},jwt);assert len(options['metrics'])==6
  call('/functions/v1/challenge-auth-web/logout',{},jwt)
  reject('/functions/v1/challenge-auth-web/dashboard',jwt=jwt)
  print(json.dumps({'account_login':'passed','expected_role':args.expect_role,'dashboard':'passed','decision_options':'passed','logout_reuse':'blocked','business_writes':0}))
 finally:
  try:call('/auth/v1/logout?scope=local',{},jwt)
  except urllib.error.HTTPError as e:e.close()
if __name__=='__main__':main()
