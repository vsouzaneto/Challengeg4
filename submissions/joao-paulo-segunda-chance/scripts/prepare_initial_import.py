"""Cria payloads locais ignorados pelo Git. Não contém credenciais.

python scripts/prepare_initial_import.py --data-dir /pasta/csv --output-dir .work/import
O operador envia os payloads com um adaptador autorizado. Nenhum arquivo de
origem é alterado; um contrato inválido continua preservado em raw.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from application.prepare_import import prepare_row
from domain.source_contracts import CONTRACT_VERSION
from scripts.audit_data import FILES


def prepare(folder, output, rows_per_batch=300, chunk_bytes=40000):
    output.mkdir(parents=True,exist_ok=True)
    manifest = []
    for source_type,(filename,_) in FILES.items():
        source = (folder/filename).read_bytes()
        reader = csv.DictReader(io.StringIO(source.decode('utf-8-sig')))
        headers = reader.fieldnames or []
        if len(set(headers)) != len(headers): raise ValueError('Cabeçalhos repetidos')
        rows = list(reader)
        if rows and (None in rows[0] or any(None in row for row in rows)):
            raise ValueError('CSV malformado: colunas sem cabeçalho')
        directory=output/source_type;directory.mkdir(exist_ok=True)
        prepared=[prepare_row(source_type,index+1,row) for index,row in enumerate(rows)]
        batches=[]
        for start in range(0,len(prepared),rows_per_batch):
            name=f'rows_{start//rows_per_batch:04d}.json'
            selected=prepared[start:start+rows_per_batch]
            packed={'headers':headers,'rows':[[r['row_number'],[r['content'][h] for h in headers],
                    [r['normalized_content'][h] for h in headers] if r['normalized_content'] is not None else None,
                    r['validation_errors']] for r in selected]}
            (directory/name).write_text(json.dumps(packed,ensure_ascii=False,separators=(',',':')))
            batches.append(name)
        chunks=[]
        # UTF-8 text chunks reassemble exact bytes (including BOM/newlines).
        # XLSX/binary sources will use Storage in the web import adapter.
        text=source.decode('utf-8')
        for start in range(0,len(text),chunk_bytes):
            name=f'bytes_{start//chunk_bytes:04d}.json'
            (directory/name).write_text(json.dumps({'index':start//chunk_bytes,'text':text[start:start+chunk_bytes]},ensure_ascii=False))
            chunks.append(name)
        manifest.append(dict(source_type=source_type,filename=filename,contract_version=CONTRACT_VERSION,
                             file_hash=hashlib.sha256(source).hexdigest(),expected_rows=len(rows),expected_bytes=len(source),
                             invalid_records=sum(bool(row['validation_errors']) for row in prepared),rows=batches,chunks=chunks))
    manifest_hash=hashlib.sha256(json.dumps([{k:x[k] for k in ('source_type','file_hash','contract_version')} for x in manifest],sort_keys=True).encode()).hexdigest()
    result={'request_hash':manifest_hash,'sources':manifest}
    (output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args()
    result=prepare(args.data_dir,args.output_dir)
    print(json.dumps({'sources':len(result['sources']),'rows':sum(s['expected_rows'] for s in result['sources']),
                      'invalid_records':sum(s['invalid_records'] for s in result['sources'])}))
