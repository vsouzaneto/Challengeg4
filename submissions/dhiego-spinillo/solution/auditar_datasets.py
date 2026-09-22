#!/usr/bin/env python3
"""Auditoria exploratória dos ZIPs públicos do Challenge 002; só biblioteca padrão.

Uso: python3 solution/auditar_datasets.py dataset1.zip dataset2.zip > solution/reports/auditoria-datasets.json
Não imprime nomes, emails nem textos de clientes. Não treina modelos.
"""
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime


def read_csv(path):
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.endswith('.csv')]
        if len(names) != 1:
            raise ValueError(f'Esperado um CSV em {path}; encontrados {names}')
        raw = archive.read(names[0])
    return names[0], hashlib.sha256(raw).hexdigest(), list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))


def categorical_effect(rows, column):
    groups = defaultdict(list)
    for row in rows:
        if row['Customer Satisfaction Rating']:
            groups[row[column]].append(float(row['Customer Satisfaction Rating']))
    values = [v for group in groups.values() for v in group]
    mean = sum(values) / len(values)
    total = sum((v - mean) ** 2 for v in values)
    between = sum(len(v) * (sum(v) / len(v) - mean) ** 2 for v in groups.values())
    return {
        'n': len(values),
        'eta_squared_descriptive': between / total if total else None,
        'groups': {k: {'n': len(v), 'mean': sum(v) / len(v)} for k, v in sorted(groups.items())},
        'interpretation': 'Associação descritiva apenas entre tickets com nota; sem inferência causal.',
    }


def main():
    result = {'audit_date': '2026-09-15', 'method': 'CSV integral; contagens exatas; sem imputação ou correção dos dados.'}
    for i, path in enumerate(sys.argv[1:], 1):
        name, sha, rows = read_csv(path)
        info = {'filename': name, 'sha256_csv': sha, 'rows': len(rows), 'columns': list(rows[0]),
                'missing': {k: sum(not r[k].strip() for r in rows) for k in rows[0]}}
        if i == 1:
            complete = [r for r in rows if r['First Response Time'] and r['Time to Resolution']]
            deltas = [(datetime.fromisoformat(r['Time to Resolution']) - datetime.fromisoformat(r['First Response Time'])).total_seconds() / 3600 for r in complete]
            negative = sum(d < 0 for d in deltas)
            info.update({
                'status_counts': dict(Counter(r['Ticket Status'] for r in rows)),
                'type_counts': dict(Counter(r['Ticket Type'] for r in rows)),
                'channel_counts': dict(Counter(r['Ticket Channel'] for r in rows)),
                'description_unique': len({r['Ticket Description'] for r in rows}),
                'description_product_placeholder_count': sum('{product_purchased}' in r['Ticket Description'] for r in rows),
                'timestamp_order_check': {'paired': len(complete), 'resolution_before_response': negative, 'negative_pct': negative / len(complete) * 100},
                'timestamp_ranges': {k: {'min': min(r[k] for r in rows if r[k]), 'max': max(r[k] for r in rows if r[k])} for k in ['First Response Time', 'Time to Resolution']},
                'nonempty_by_status': {s: {k: sum(bool(r[k]) for r in rows if r['Ticket Status'] == s) for k in ['First Response Time', 'Time to Resolution', 'Customer Satisfaction Rating']} for s in sorted({r['Ticket Status'] for r in rows})},
                'satisfaction_associations': {k: categorical_effect(rows, k) for k in ['Ticket Channel', 'Ticket Priority', 'Ticket Type']},
            })
        else:
            normalized = Counter(re.sub(r'\s+', ' ', r['Document'].strip().lower()) for r in rows)
            labels = Counter(r['Topic_group'] for r in rows)
            info.update({'category_counts': dict(labels), 'majority_class_baseline_accuracy': max(labels.values()) / len(rows), 'normalized_duplicate_rows': sum(n - 1 for n in normalized.values()), 'near_duplicates_checked': False})
        result[f'dataset_{i}'] = info
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Uso: auditar_datasets.py dataset1.zip dataset2.zip')
    main()
