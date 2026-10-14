"""Adaptador operacional de importação, executado SOMENTE no backend.

Requer SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no ambiente. Não imprime chave,
IDs de contas, payloads ou relatórios. Não use no frontend. Neste bootstrap,
as mesmas operações foram executadas pela conexão autorizada de Supabase.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.prepare_initial_import import prepare
from scripts.audit_data import audit


class SupabaseImportAdapter:
    def __init__(self,url,key):
        self.url=url.rstrip('/')
        self.key=key

    def rpc(self,name,body):
        headers={'apikey':self.key,'Content-Type':'application/json'}
        if self.key.startswith('eyJ'): headers['Authorization']='Bearer '+self.key
        request=urllib.request.Request(self.url+'/rest/v1/rpc/'+name,
            data=json.dumps(body,ensure_ascii=False).encode(),headers=headers,method='POST')
        try:
            with urllib.request.urlopen(request,timeout=120) as response:
                data=response.read()
                return json.loads(data) if data else None
        except urllib.error.HTTPError as exc:
            # Do not dump payloads or request headers in errors.
            raise RuntimeError(f'RPC {name} falhou: HTTP {exc.code}') from None


def import_sources(adapter,data_dir,work_dir,workspace_id,reference_date):
    manifest=prepare(data_dir,work_dir)
    report=audit(data_dir)
    meta=adapter.rpc('challenge_start_import',dict(p_workspace=workspace_id,p_request_hash=manifest['request_hash'],
        p_label='Importação CSV',p_sources=[{k:s[k] for k in ('source_type','filename','contract_version','file_hash','expected_rows','expected_bytes')} for s in manifest['sources']]))
    for source in manifest['sources']:
        file=next(f for f in meta['files'] if f['source_type']==source['source_type'])
        if file['status']=='verified': continue
        for name in source['chunks']:
            chunk=json.loads((work_dir/source['source_type']/name).read_text())
            adapter.rpc('challenge_append_file_chunk',dict(p_file=file['file_id'],p_index=chunk['index'],p_text=chunk['text']))
        for name in source['rows']:
            payload=json.loads((work_dir/source['source_type']/name).read_text())
            adapter.rpc('challenge_append_rows',dict(p_file=file['file_id'],p_payload=payload))
        adapter.rpc('challenge_verify_file',dict(p_file=file['file_id']))
    return adapter.rpc('challenge_finish_import',dict(p_version=meta['version_id'],p_reference=reference_date,p_checks=report['findings']))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir',type=Path,required=True)
    p.add_argument('--work-dir',type=Path,default=Path('.work/import'))
    p.add_argument('--workspace-id',required=True)
    p.add_argument('--reference-date',required=True)
    args=p.parse_args()
    adapter=SupabaseImportAdapter(os.environ['SUPABASE_URL'],os.environ['SUPABASE_SERVICE_ROLE_KEY'])
    import_sources(adapter,args.data_dir,args.work_dir,args.workspace_id,args.reference_date)
    print('Importação verificada e versão publicada.')
