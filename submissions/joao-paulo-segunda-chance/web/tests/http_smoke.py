"""Read-only deployed smoke test. Capability stays in process memory."""
import json,urllib.request,urllib.error
BASE='https://uxpcrjryxrbwgpakesti.supabase.co/functions/v1/challenge-web'
def request(path,body=None,token=None):
 headers={'Content-Type':'application/json'}
 if token: headers['x-challenge-session']=token
 r=urllib.request.urlopen(urllib.request.Request(BASE+'/'+path,data=None if body is None else json.dumps(body).encode(),headers=headers),timeout=60)
 return json.load(r)
def main():
 try: request('dashboard');raise AssertionError('Missing capability allowed')
 except urllib.error.HTTPError as e: assert e.code==401
 token=request('session',{})['token'];d=request('dashboard',token=token)
 assert len(d['sources'])==5 and len(d['quality'])==89
 detail=request('detail',{'id':d['accounts'][0]['id']},token)
 assert detail['snapshot']['id']==d['accounts'][0]['id']
 print(json.dumps({'dashboard':'ok','detail':'ok','missing_session':'blocked','accounts':len(d['accounts']),'checks':len(d['quality'])}))
if __name__=='__main__':main()
