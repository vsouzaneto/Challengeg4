#!/usr/bin/env python3
"""Comparação reproduzível: prepare, jev e report. Teste reservado antes de treinar."""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import httpx
import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import HashingVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from threadpoolctl import threadpool_limits

from explorar_cx import read_zip
from triage_core import ROOT, LABELS, jev_payload, key_from_env, parse_jev, prompt_fingerprint

OUT = ROOT / 'solution/reports/comparison'
LOCAL = ROOT / 'artifacts'
SEED = 42
EXPECTED_HASH = '044fdace33fa564e1e60453f2941dafc95539c99878b0d32746950394b9dd4d4'


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def read(name):
    return json.loads((OUT / name).read_text())


def prepare(zip_path):
    sha, rows = read_zip(zip_path)
    if sha != EXPECTED_HASH:
        raise SystemExit('Hash diferente da auditoria; revisar dados antes de continuar.')
    texts = np.array([r['Document'] for r in rows], dtype=object)
    y = np.array([r['Topic_group'] for r in rows])
    idx = np.arange(len(rows))
    trainval, test = train_test_split(idx, test_size=800, stratify=y, random_state=SEED)
    train, val = train_test_split(trainval, test_size=400, stratify=y[trainval], random_state=SEED)
    # Hash de palavras/pares usa apenas textos; nenhuma categoria informa o filtro.
    H = HashingVectorizer(n_features=2**18, alternate_sign=False, ngram_range=(1, 2), norm='l2').transform(texts)

    def purge(query, references):
        keep, removed = [], []
        for start in range(0, len(query), 256):
            batch = query[start:start + 256]
            similarity = (H[batch] @ H[references].T).tocsr()
            maximum = similarity.max(axis=1).toarray().ravel()
            nearest = np.asarray(similarity.argmax(axis=1)).ravel()
            for i, score, neighbor in zip(batch, maximum, nearest):
                if score >= 0.92:
                    removed.append({'row': int(i + 1), 'near_row': int(references[neighbor] + 1), 'similarity': float(score)})
                else:
                    keep.append(i)
        return np.array(keep), removed

    val, removed_val = purge(val, test)
    train, removed_train = purge(train, np.concatenate([val, test]))
    # Dependência residual entre exemplos de teste é quantificada e declarada.
    test_similarity = (H[test] @ H[test].T).tocsr()
    test_similarity.setdiag(0)
    test_near_pairs = int((test_similarity >= 0.92).sum() // 2)
    LOCAL.mkdir(exist_ok=True)
    split = {'seed': SEED, 'csv_sha256': sha, 'sklearn': sklearn.__version__,
             'train_rows': (train + 1).tolist(), 'validation_rows': (val + 1).tolist(), 'test_rows': (test + 1).tolist(),
             'counts': {name: dict(Counter(y[ids])) for name, ids in [('train', train), ('validation', val), ('test', test)]},
             'near_duplicate_filter': {'method': 'cosine HashingVectorizer word(1,2), 2**18, alternate_sign=False',
                                       'threshold': 0.92, 'removed_train': removed_train, 'removed_validation': removed_val,
                                       'near_pairs_within_test': test_near_pairs,
                                       'limit': 'Heurística lexical; não garante ausência de paráfrases/contaminação prévia do Jev. Teste pode conter pares correlacionados.'},
             'jev_prompt_sha256': prompt_fingerprint(), 'jev_request_template': jev_payload('<TICKET_TEXT>'),
             'threshold_rule': 'max coverage with empirical validation error <=0.05, >=30 accepted; grid 0.50..0.99 step0.01; no feasible => null',
             'api_policy': '4 concurrent, no automatic retry; checkpoint keyed by row+prompt, failures counted as abstentions'}
    save('split.json', split)
    print('Divisão congelada:', {k: len(v) for k, v in [('train', train), ('validation', val), ('test', test)]}, flush=True)
    print('Removidos por proximidade:', len(removed_train), 'treino;', len(removed_val), 'validação', flush=True)
    pipeline = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=60000, sublinear_tf=True),
                             LogisticRegression(C=4, max_iter=1000, random_state=SEED))
    start = time.perf_counter()
    with threadpool_limits(limits=4):
        pipeline.fit(texts[train].tolist(), y[train])
    fit_seconds = time.perf_counter() - start
    joblib.dump(pipeline, LOCAL / 'classifier.joblib', compress=3)
    records = []
    for partition, ids in [('validation', val), ('test', test)]:
        for i in ids:
            start = time.perf_counter()
            probs = pipeline.predict_proba([texts[i]])[0]
            prediction = str(pipeline.classes_[int(probs.argmax())])
            records.append({'row': int(i + 1), 'partition': partition, 'truth': str(y[i]), 'prediction': prediction,
                            'probabilities': dict(zip(pipeline.classes_.tolist(), probs.tolist())), 'score': float(probs.max()),
                            'elapsed_ms': (time.perf_counter() - start) * 1000})
    save('local-predictions.json', records)
    save('training.json', {'fit_seconds': fit_seconds, 'classes': pipeline.classes_.tolist(), 'iterations': pipeline[-1].n_iter_.tolist(),
                           'parameters': {'tfidf': 'word(1,2), min_df2, max_features60000, sublinear_tf', 'logistic': 'C4, max_iter1000'},
                           'class_majority': str(Counter(y[train]).most_common(1)[0][0]),
                           'model_sha256': hashlib.sha256((LOCAL/'classifier.joblib').read_bytes()).hexdigest()})
    # Apenas exemplos públicos de treino para demonstrar a interface, sem campos pessoais do D1.
    rng = np.random.default_rng(SEED)
    examples = []
    for label in LABELS:
        candidates = [i for i in train if y[i] == label and 12 <= len(texts[i].split()) <= 110]
        chosen = int(rng.choice(candidates))
        examples.append({'row': chosen + 1, 'text': texts[chosen], 'dataset_label': label})
    save('demo-examples.json', examples)
    print('Modelo treinado e previsões locais gravadas.', flush=True)


async def run_jev(zip_path):
    split = read('split.json')
    sha, rows = read_zip(zip_path)
    if sha != split['csv_sha256'] or prompt_fingerprint() != split['jev_prompt_sha256']:
        raise SystemExit('Dados/prompt divergiram do protocolo congelado.')
    key = key_from_env('TYPESAFE_API_KEY')
    if not key:
        raise SystemExit('TYPESAFE_API_KEY ausente')
    path = OUT / 'jev-predictions.jsonl'
    previous = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    expected_partition = {i: p for p,k in [('validation','validation_rows'),('test','test_rows')] for i in split[k]}
    if any(r.get('prompt_sha256') != prompt_fingerprint() or r.get('partition') != expected_partition.get(r.get('row'))
           or r.get('truth') != rows[r['row'] - 1]['Topic_group'] for r in previous):
        raise SystemExit('Checkpoint divergente do prompt, split ou dataset; não reaproveitar.')
    done = {r['row'] for r in previous}
    if len(done) != len(previous):
        raise SystemExit('Checkpoint duplicado; revisar antes de retomar.')
    jobs = [(partition, i) for partition, name in [('validation', 'validation_rows'), ('test', 'test_rows')]
            for i in split[name] if i not in done]
    semaphore = asyncio.Semaphore(4)
    count = len(done)
    total = count + len(jobs)
    async with httpx.AsyncClient(timeout=35, headers={'Authorization': 'Bearer ' + key}, follow_redirects=False) as client:
        async def request_one(partition, row):
            nonlocal count
            async with semaphore:
                start = time.perf_counter()
                record = {'row': row, 'partition': partition, 'truth': rows[row - 1]['Topic_group'], 'prompt_sha256': prompt_fingerprint()}
                try:
                    response = await client.post('https://api.typesafe.ai/v1/systemone', json=jev_payload(rows[row - 1]['Document']))
                    response.raise_for_status()
                    record.update(parse_jev(response.json()))
                except httpx.HTTPStatusError as error:
                    record['error'] = f'HTTP {error.response.status_code}'
                except (httpx.HTTPError, ValueError, KeyError, TypeError):
                    record['error'] = 'network_or_contract'
                record['elapsed_ms'] = (time.perf_counter() - start) * 1000
                with path.open('a') as f:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
                count += 1
                if count % 40 == 0 or 'error' in record or count == total:
                    print(f'Jev: {count}/{total}' + (f' — {record["error"]}' if 'error' in record else ''), flush=True)
        # Falha no primeiro pedido interrompe antes de enviar o lote completo.
        if jobs:
            await request_one(*jobs[0])
            first = json.loads(path.read_text().splitlines()[-1])
            if first.get('error'):
                raise SystemExit('Primeira chamada falhou; lote interrompido, revisar antes de retomar.')
            await asyncio.gather(*(request_one(*job) for job in jobs[1:]))


def wilson(correct, n):
    if n == 0:
        return None
    z = 1.96
    p = correct / n
    mid = (p + z*z/(2*n)) / (1 + z*z/n)
    half = z*((p*(1-p)/n + z*z/(4*n*n))**0.5)/(1+z*z/n)
    return [mid-half, mid+half]


def threshold(validation):
    feasible = []
    for t in np.arange(.50, 1.00, .01):
        t = float(round(t, 2))
        accepted = [r for r in validation if not r.get('error') and r['score'] >= t]
        errors = sum(r['prediction'] != r['truth'] for r in accepted)
        if len(accepted) >= 30 and errors / len(accepted) <= .05:
            feasible.append((len(accepted), float(round(t, 2))))
    return min(feasible, key=lambda x: (-x[0], x[1]))[1] if feasible else None


def metrics(records, t):
    y = [r['truth'] for r in records]
    p = [r.get('prediction', '__ERROR__') for r in records]
    good = [r for r in records if not r.get('error')]
    accepted = [r for r in good if t is not None and r['score'] >= t]
    correct = sum(a == b for a,b in zip(y,p))
    bins = []
    for lo in np.arange(0,1,.1):
        subset = [r for r in good if min(int(r['score'] * 10), 9) == int(round(lo * 10))]
        if subset:
            bins.append({'from': round(float(lo), 1), 'n': len(subset), 'mean_score': float(np.mean([r['score'] for r in subset])),
                         'accuracy': float(np.mean([r['prediction'] == r['truth'] for r in subset]))})
    brier = float(np.mean([sum((r['probabilities'][k]-(k == r['truth']))**2 for k in LABELS) for r in good])) if good else None
    return {'n':len(records), 'accuracy_including_api_errors': correct/len(records), 'accuracy_ci95_wilson': wilson(correct,len(records)),
            'macro_f1': f1_score(y,p,labels=list(LABELS),average='macro',zero_division=0),
            'by_class':classification_report(y,p,labels=list(LABELS),output_dict=True,zero_division=0),
            'confusion_labels':list(LABELS)+['__ERROR__'], 'confusion':confusion_matrix(y,p,labels=list(LABELS)+['__ERROR__']).tolist(),
            'api_errors':len(records)-len(good), 'brier_multiclass_sum_on_valid':brier, 'reliability_bins':bins,
            'latency_ms': {k:float(np.percentile([r['elapsed_ms'] for r in records],q)) for k,q in [('p50',50),('p95',95)]},
            'threshold_from_validation':t, 'accepted_n':len(accepted), 'coverage':len(accepted)/len(records),
            'accepted_accuracy': float(np.mean([r['prediction']==r['truth'] for r in accepted])) if accepted else None,
            'accepted_accuracy_ci95_wilson':wilson(sum(r['prediction']==r['truth'] for r in accepted),len(accepted))}


def report():
    split = read('split.json')
    local = read('local-predictions.json')
    jev = [json.loads(line) for line in (OUT/'jev-predictions.jsonl').read_text().splitlines()]
    expected = set(split['validation_rows'] + split['test_rows'])
    expected_partition = {i: p for p,k in [('validation','validation_rows'),('test','test_rows')] for i in split[k]}
    for records in (local,jev):
        if len(records) != len(expected) or {r['row'] for r in records} != expected:
            raise SystemExit('Comparação incompleta ou com linhas duplicadas; retomar antes do relatório.')
        if any(r['partition'] != expected_partition[r['row']] or r['truth'] not in LABELS for r in records):
            raise SystemExit('Partição ou referência inválida no relatório.')
    local_truth = {r['row']:r['truth'] for r in local}
    if any(r['truth'] != local_truth[r['row']] or r.get('prompt_sha256') != split['jev_prompt_sha256'] for r in jev):
        raise SystemExit('Referências ou fingerprints divergentes entre os sistemas.')
    if any(not r.get('error') and r.get('model') != 'jev-1.13.0' for r in jev):
        raise SystemExit('Versões Jev misturadas; separar execuções antes de comparar.')
    if (hashlib.sha256((LOCAL/'classifier.joblib').read_bytes()).hexdigest() != read('training.json')['model_sha256']):
        raise SystemExit('Artefato local diferente do modelo registrado.')
    result = {'created_at_utc':datetime.now(timezone.utc).isoformat(), 'protocol':'split.json', 'systems':{}}
    for name, records in [('tfidf_logistic',local),('jev',jev)]:
        validation=[r for r in records if r['partition']=='validation']
        test=[r for r in records if r['partition']=='test']
        t=threshold(validation)
        result['systems'][name]={'validation':metrics(validation,t),'test':metrics(test,t)}
    jt={r['row']:r for r in jev if r['partition']=='test'}
    lt={r['row']:r for r in local if r['partition']=='test'}
    diff=np.array([int(lt[i]['prediction']==lt[i]['truth'])-int(jt[i].get('prediction')==jt[i]['truth']) for i in sorted(lt)])
    rng=np.random.default_rng(SEED)
    bootstrap=np.mean(rng.choice(diff,size=(2000,len(diff)),replace=True),axis=1)
    result['paired_accuracy_difference_local_minus_jev']={'point':float(diff.mean()),'ci95_bootstrap':np.percentile(bootstrap,[2.5,97.5]).tolist(),
        'limit':'Bootstrap por linha; similaridade residual pode estreitar o intervalo. Não identifica desempenho fora do D2.'}
    majority=read('training.json')['class_majority']
    result['majority_test_accuracy']=sum(r['truth']==majority for r in lt.values())/len(lt)
    result['jev_models']=sorted(set(r['model'] for r in jev if not r.get('error')))
    result['jev_input_tokens']=sum(r.get('usage',{}).get('input_tokens',0) or 0 for r in jev)
    result['jev_output_tokens']=sum(r.get('usage',{}).get('output_tokens',0) or 0 for r in jev)
    result['jev_cost_usd_estimate']={'input_price_per_million':.042,'output_price_per_million':0,'estimated':result['jev_input_tokens']*.042/1e6,
        'source':'https://typesafe.ai/blog/introducing-system-one-models-and-jev','note':'Estimativa pela tabela publicada, não fatura; entradaUS$0.042/M, saída gratuita. Inclui validação e teste, apenas tokens reportados.'}
    result['limitations']=['Jev pré-treinado com descrições; regressão aprende rótulos do D2: comparação de sistemas, não isolamento de arquitetura.',
        'Referência Topic_group não auditada integralmente por humanos. Não demonstra redução de tempo de trabalho ou churn.',
        'Limiar escolhido por erro empírico <=5% na validação, não garantia de segurança. Todos os destinos no protótipo exigem confirmação.',
        '33 distribuições Jev somaram0.99 devido ao arredondamento; preservadas como recebidas. Brier não renormalizado (efeito pequeno).',
        'Latência Jev com pool e4requisiçõesconcorrentes inclui rede; local uma inferência por vez após carregar modelo. Treino reportado separadamente.']
    save('summary.json',result)
    for name,data in result['systems'].items():
        m=data['test'];print(name,'n=',m['n'],'accuracy=',round(m['accuracy_including_api_errors'],4),'macroF1=',round(m['macro_f1'],4),'coverage=',round(m['coverage'],4),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['prepare','jev','report'])
    parser.add_argument('--zip',type=Path,default=ROOT/'data/dataset2.zip')
    args=parser.parse_args()
    if args.stage=='prepare':prepare(args.zip)
    elif args.stage=='jev':asyncio.run(run_jev(args.zip))
    else:report()
