#!/usr/bin/env python3
"""Exploração descritiva orientada às perguntas de CX; não infere SLA ou churn.

Uso: python3 solution/explorar_cx.py dataset1.zip dataset2.zip > resultado.json
Só biblioteca padrão. Não exporta nomes, emails ou descrições completas.
"""
import collections
import csv
import hashlib
import io
import json
import random
import statistics
import sys
import zipfile


def read_zip(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith('.csv')]
        if len(names) != 1:
            raise ValueError('Esperado um CSV por ZIP')
        raw = z.read(names[0])
    return hashlib.sha256(raw).hexdigest(), list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))


def describe(rows):
    scores = [float(x['Customer Satisfaction Rating']) for x in rows if x['Customer Satisfaction Rating']]
    return {
        'n': len(rows),
        'status': dict(sorted(collections.Counter(x['Ticket Status'] for x in rows).items())),
        'priority': dict(sorted(collections.Counter(x['Ticket Priority'] for x in rows).items())),
        'rated_n': len(scores),
        'rating_mean': statistics.mean(scores) if scores else None,
        'low_1_2_n': sum(x <= 2 for x in scores),
        'high_4_5_n': sum(x >= 4 for x in scores),
        'low_1_2_pct_among_rated': 100 * sum(x <= 2 for x in scores) / len(scores) if scores else None,
    }


def main():
    sha1, rows = read_zip(sys.argv[1])
    sha2, rows2 = read_zip(sys.argv[2])
    phrases = {
        'explicit_urgently': 'urgently',
        'repeat_contact_statement': 'already contacted customer support multiple times',
        'as_soon_as_possible': 'as soon as possible',
        'today': 'today',
        'deadline': 'deadline',
        'frustrat_stem': 'frustrat',
    }
    repeated = collections.defaultdict(list)
    for row in rows:
        repeated[row['Customer Email'].strip().lower()].append(row)
    repeated = [group for group in repeated.values() if len(group) > 1]
    closed = [x for x in rows if x['Resolution']]
    sizes = [len(x['Resolution'].split()) for x in closed]
    out = {
        'reference_date': '2026-09-15',
        'sha256_csv': {'dataset_1': sha1, 'dataset_2': sha2},
        'method': 'Contagens integrais, busca literal sem distinção de caixa, amostra de resoluções com seed 42. Resultados descritivos; não são inferência de urgência, sentimento, reincidência ou causalidade.',
        'rating_convention': 'Notas 1–2 agrupadas como baixas e 4–5 como altas apenas para leitura exploratória; não é definição oficial de CSAT.',
        'overall': describe(rows),
        'groups': {
            col: {value: describe([x for x in rows if x[col] == value]) for value in sorted({x[col] for x in rows})}
            for col in ['Ticket Channel', 'Ticket Priority', 'Ticket Type']
        },
        'phrase_matches': {
            key: {'literal': phrase, **describe([x for x in rows if phrase in x['Ticket Description'].lower()])}
            for key, phrase in phrases.items()
        },
        'repeated_email': {
            'unique_emails': len({x['Customer Email'].strip().lower() for x in rows}),
            'repeated_groups': len(repeated),
            'rows_in_repeated_groups': sum(map(len, repeated)),
            'groups_with_multiple_names': sum(len({x['Customer Name'] for x in g}) > 1 for g in repeated),
            'groups_with_multiple_ages': sum(len({x['Customer Age'] for x in g}) > 1 for g in repeated),
            'groups_with_multiple_genders': sum(len({x['Customer Gender'] for x in g}) > 1 for g in repeated),
            'interpretation': 'Email repetido não é identidade de cliente validada; diferenças podem refletir inconsistência ou conta compartilhada. Não calcular reincidência individual com essa chave sem reconciliação.',
        },
        'resolutions': {
            'nonempty': len(closed),
            'word_count': {'min': min(sizes), 'median': statistics.median(sizes), 'max': max(sizes)},
            'word_count_distribution': dict(sorted(collections.Counter(sizes).items())),
            'inspection_sample_seed': 42,
            'inspection_sample': [{'ticket_id': x['Ticket ID'], 'subject': x['Ticket Subject'], 'resolution': x['Resolution']} for x in random.Random(42).sample(closed, 20)],
            'interpretation': 'Comprimento não mede qualidade. A amostra permite inspecionar plausibilidade; não oferece diálogo agente-cliente para medir cobertura de perguntas.',
        },
        'dataset_2': {
            'n': len(rows2),
            'columns': list(rows2[0]),
            'classes': dict(sorted(collections.Counter(x['Topic_group'] for x in rows2).items())),
            'interpretation': 'Permite avaliar categoria; não traz cliente, sequência de atendimento, prioridade, sentimento, prazos ou desfecho de churn.',
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Uso: explorar_cx.py dataset1.zip dataset2.zip')
    main()
