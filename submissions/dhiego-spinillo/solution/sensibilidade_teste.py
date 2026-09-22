#!/usr/bin/env python3
"""Remove todos os envolvidos em pares próximos dentro do teste, sem retreino."""
import json
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from comparar_classificadores import metrics, read, save
from explorar_cx import read_zip
from triage_core import ROOT

split=read('split.json')
sha,rows=read_zip(ROOT/'data/dataset2.zip')
assert sha == split['csv_sha256']
ids=split['test_rows']
H=HashingVectorizer(n_features=2**18,alternate_sign=False,ngram_range=(1,2),norm='l2').transform([rows[i-1]['Document'] for i in ids])
S=(H@H.T).tocsr();S.setdiag(0)
excluded={ids[i] for i in np.where(S.max(axis=1).toarray().ravel()>=.92)[0]}
summary=read('summary.json')
result={'excluded_test_rows':sorted(excluded),'remaining_n':len(ids)-len(excluded),
        'method':'Remove todos os tickets de teste envolvidos em pares>=.92; não altera treino, prompt ou limiares. Sensibilidade pós-revisão; não substitui teste principal.', 'systems':{}}
for name,file in [('tfidf_logistic','local-predictions.json'),('jev','jev-predictions.jsonl')]:
    path=ROOT/'solution/reports/comparison'/file
    data=json.loads(path.read_text()) if file.endswith('.json') else [json.loads(line) for line in path.read_text().splitlines()]
    subset=[r for r in data if r['partition']=='test' and r['row'] not in excluded]
    result['systems'][name]=metrics(subset,summary['systems'][name]['test']['threshold_from_validation'])
save('sensitivity.json',result)
print('Sensibilidade registrada:',result['remaining_n'],'tickets; nenhum retreino ou nova chamada API.')
