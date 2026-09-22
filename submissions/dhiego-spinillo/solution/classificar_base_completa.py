"""Perfil integral do D2 com modelo/split congelados; nenhuma chamada externa.

Uso: python solution/classificar_base_completa.py data/dataset2.zip --output /tmp/d2-integral
Não treina, não ajusta limiar e não executa procedimentos de atendimento.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import time

import joblib
import numpy as np
from threadpoolctl import threadpool_limits

from explorar_cx import read_zip
from triage_core import ROOT


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def partition_rows(split, size):
    """Exigir partições exclusivas e cobertura integral, incluindo descartados."""
    groups = {name: split[name + '_rows'] for name in ('train', 'validation', 'test')}
    for source in ('train', 'validation'):
        groups['excluded_' + source] = [r['row'] for r in split['near_duplicate_filter']['removed_' + source]]
    mapping = {}
    for name, rows in groups.items():
        for row in rows:
            if type(row) is not int or not 1 <= row <= size or row in mapping:
                raise ValueError('Split com sobreposição, duplicação ou linha inválida')
            mapping[row] = name
    if len(mapping) != size:
        raise ValueError('Split não cobre todas as linhas da base')
    return mapping


def summarize(records, threshold):
    selected = [r for r in records if r['score'] >= threshold]
    disagreements = [r for r in records if r['prediction'] != r['dataset_label']]
    return {
        'n': len(records),
        'label_distribution': dict(sorted(Counter(r['dataset_label'] for r in records).items())),
        'prediction_distribution': dict(sorted(Counter(r['prediction'] for r in records).items())),
        'agreement_n': len(records) - len(disagreements),
        'agreement_rate': (len(records) - len(disagreements)) / len(records) if records else None,
        'disagreement_n': len(disagreements),
        'above_threshold_n': len(selected),
        'above_threshold_disagreement_n': sum(r['prediction'] != r['dataset_label'] for r in selected),
        'top_disagreements': [
            {'dataset_label': pair[0], 'prediction': pair[1], 'n': count}
            for pair, count in Counter((r['dataset_label'], r['prediction']) for r in disagreements).most_common(10)
        ],
    }


def verify_historical(records, historical):
    by_row = {r['row']: r for r in records}
    expected = {r['row'] for r in records if r['partition'] in ('validation', 'test')}
    if len(historical) != len(expected) or {r['row'] for r in historical} != expected:
        raise ValueError('Referência histórica incompleta ou duplicada')
    max_difference = 0.0
    for old in historical:
        current = by_row[old['row']]
        if any(current[k] != old[k] for k in ('partition', 'prediction')) or current['dataset_label'] != old['truth']:
            raise ValueError('Predição/partição/rótulo divergiu da avaliação original')
        delta = abs(current['score'] - old['score'])
        if not np.isfinite(delta) or delta > 1e-10:
            raise ValueError('Score divergiu da avaliação original')
        max_difference = max(max_difference, delta)
    return {'n': len(historical), 'predictions_identical': True, 'max_absolute_score_difference': max_difference}


def render_report(report):
    def number(value):
        return f'{value:,}'.replace(',', '.')
    def percent(value):
        return f'{value * 100:.2f}%'.replace('.', ',')
    pop = report['population']
    names = {'train': 'Treino', 'validation': 'Validação', 'test': 'Teste original',
             'excluded_train': 'Excluídos do treino por proximidade',
             'excluded_validation': 'Excluídos da validação por proximidade'}
    lines = [
        '# Classificação da base completa do D2', '',
        f'**{number(pop["n"])} registros processados com o modelo local congelado. Nenhum novo treino ou chamada paga.**', '',
        '## O que esta rodada acrescenta', '',
        f'Perfil integral de categorias, scores e **{number(pop["disagreement_n"])} divergências** entre modelo e rótulo da base. '
        f'Destas, **{number(pop["above_threshold_disagreement_n"])}** têm score ≥ 0,61. São casos para revisão: '
        'a divergência pode vir do modelo, do rótulo ou de ambiguidade. Score alto não confirma intenção nem autoriza procedimento.', '',
        '**A evidência de desempenho continua sendo o teste original: 688/800 (86%).** '
        'As 1.192 previsões de validação/teste foram reproduzidas, incluindo scores dentro da tolerância de 1e-10. '
        'Não são novos exemplos. Alguns tickets de teste foram posteriormente examinados no desenvolvimento.', '',
        '## Universos separados', '',
        '| Universo | Registros | Concordâncias | Divergências | Concordância com rótulo |',
        '|---|---:|---:|---:|---:|',
    ]
    for name, stats in report['partitions'].items():
        lines.append(f'| {names[name]} | {number(stats["n"])} | {number(stats["agreement_n"])} | {number(stats["disagreement_n"])} | {percent(stats["agreement_rate"])} |')
    lines += ['', f'A concordância global é {percent(pop["agreement_rate"])}; **não usar como acurácia independente**, '
              'pois 45.790 registros participaram do treino. A validação escolheu o limiar; os excluídos têm proximidade lexical '
              'com outros grupos e não são um novo teste. O teste contém dependência residual documentada na comparação.', '',
              '## Distribuição de categorias', '', '| Categoria | Rótulo da base | Sugestão local |', '|---|---:|---:|---:|']
    for label, count in pop['label_distribution'].items():
        lines.append(f'| {label} | {number(count)} | {number(pop["prediction_distribution"].get(label, 0))} |')
    lines += ['', 'Hardware e RH concentram 24.532/47.837 rótulos (51,28%). Isso orienta uma amostra de revisão do domínio. '
              'Não mede demanda na empresa do desafio, urgência, carga de trabalho ou elegibilidade ao autosserviço.', '',
              '## Uso na decisão', '',
              '1. Manter classificação assistida: no teste, 44 dos 658 tickets acima do limiar divergiram (6,69%), acima da meta de 5%.',
              '2. Revisar a taxonomia e as divergências antes de automatizar encaminhamentos. Hardware ↔ RH concentra 239 divergências na base inteira, majoritariamente usada no treino.',
              '3. Avaliar intenção, tentativas, risco e completude separadamente. O D2 não possui referência para essas tarefas, nem estado da conta, notas internas ou resultado da resolução.',
              '4. Medir elegibilidade e ganho no piloto. Não multiplicar os 30 mil tickets anuais pelo percentual acima do limiar para estimar saving.', '',
              '## Rastreabilidade', '',
              '- [Resumo JSON e metadados](summary.json).',
              '- [Predição por registro — CSV comprimido](predictions.csv.gz): linha, partição, rótulo, sugestão e score; sem texto original.',
              '- [Script](../../classificar_base_completa.py) verifica hashes do CSV/modelo, cobertura exclusiva do split e igualdade com a avaliação histórica.',
              '- [Comparação Local × Jev](../../comparacao.md) preservada. Jev e LLM não foram executados sobre toda a base.', '',
              'Reprodução, da pasta da submissão:', '', '```bash',
              '.venv/bin/python solution/classificar_base_completa.py data/dataset2.zip --output /tmp/g4-d2-integral', '```', '',
              'Comparar o JSON e o CSV com os arquivos versionados. Timestamp e duração dependem da execução. '
              'O resumo Markdown é gerado junto aos resultados; seus links pressupõem a estrutura versionada `solution/reports/full-population/`.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    comparison = ROOT / 'solution/reports/comparison'
    split = json.loads((comparison / 'split.json').read_text())
    training = json.loads((comparison / 'training.json').read_text())
    original = json.loads((comparison / 'summary.json').read_text())
    model_path = ROOT / 'artifacts/classifier.joblib'
    csv_hash, rows = read_zip(args.dataset)
    if csv_hash != split['csv_sha256'] or sha256(model_path) != training['model_sha256']:
        raise ValueError('Dataset/modelo diferente da avaliação congelada')
    partitions = partition_rows(split, len(rows))
    threshold = original['systems']['tfidf_logistic']['test']['threshold_from_validation']
    model = joblib.load(model_path)
    if list(model.classes_) != training['classes'] or any(r['Topic_group'] not in model.classes_ for r in rows):
        raise ValueError('Categorias divergentes')
    records = []
    start = time.perf_counter()
    with threadpool_limits(limits=4):
        for offset in range(0, len(rows), 1024):
            batch = rows[offset:offset + 1024]
            probabilities = model.predict_proba([r['Document'] for r in batch])
            if not np.isfinite(probabilities).all() or not np.allclose(probabilities.sum(axis=1), 1):
                raise ValueError('Probabilidades inválidas')
            for index, (row, scores) in enumerate(zip(batch, probabilities), offset + 1):
                records.append({'row': index, 'partition': partitions[index], 'dataset_label': row['Topic_group'],
                                'prediction': str(model.classes_[scores.argmax()]), 'score': float(scores.max())})
    seconds = time.perf_counter() - start
    historical = verify_historical(records, json.loads((comparison / 'local-predictions.json').read_text()))
    report = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'csv_sha256': csv_hash, 'model_sha256': sha256(model_path),
        'split_sha256': sha256(comparison / 'split.json'),
        'script_sha256': sha256(Path(__file__)),
        'threshold_from_original_validation': threshold,
        'inference_seconds_local_batch': seconds, 'external_api_calls': 0,
        'retrained': False, 'row_numbering': '1-based data rows, excluding header',
        'historical_reproduction': historical,
        'population': summarize(records, threshold),
        'partitions': {name: summarize([r for r in records if r['partition'] == name], threshold)
                       for name in ('train', 'validation', 'test', 'excluded_train', 'excluded_validation')},
        'limitations': [
            'Whole-population agreement is largely training fit, not an independent accuracy estimate.',
            'Validation selected the threshold; excluded rows are near neighbors, not a new test.',
            'Test reproduces the original 800 records. Some were later inspected during development.',
            'Dataset labels may be inconsistent. Agreement does not demonstrate semantic correctness.',
            'Scores do not authorize actions. No sentiment, LLM extraction, replies or resolution measured.',
            'No automation eligibility, operational savings or annual-volume extrapolation inferred.',
        ],
    }
    # Sem texto original ou dados pessoais. Compressão determinística e rastreio por linha.
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
    compressed = gzip.compress(buffer.getvalue().encode(), mtime=0)
    report['predictions_csv_gz_sha256'] = hashlib.sha256(compressed).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'predictions.csv.gz').write_bytes(compressed)
    (args.output / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (args.output / 'report.md').write_text(render_report(report))
    print(json.dumps({'n': len(records), 'seconds': seconds, 'historical_reproduction': historical,
                      'partitions': {p: {k: v[k] for k in ('n', 'agreement_n', 'disagreement_n', 'above_threshold_n', 'above_threshold_disagreement_n')}
                                     for p, v in report['partitions'].items()}}, indent=2))


if __name__ == '__main__':
    main()
