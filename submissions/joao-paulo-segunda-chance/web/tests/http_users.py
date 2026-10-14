"""Read-only anonymous/invalid-token guards. Never creates users or resets passwords."""
import json,urllib.request,urllib.error
BASE='https://uxpcrjryxrbwgpakesti.supabase.co/functions/v1/challenge-users/'
cases=[('users-list','GET',None),('users-create','POST',None),('users-reset','POST','invalid-token'),('password-change','POST',None)]
for path,method,token in cases:
 headers={'Content-Type':'application/json'}
 if token:headers['Authorization']='Bearer '+token
 request=urllib.request.Request(BASE+path,data=b'{}' if method=='POST' else None,method=method,headers=headers)
 try:
  with urllib.request.urlopen(request,timeout=20) as response:status=response.status
 except urllib.error.HTTPError as error:status=error.code
 assert status==401,(path,status)
 print(path+': 401 PASS')
print('4 anonymous/invalid-token guards passed; no user mutation attempted with valid credentials.')
