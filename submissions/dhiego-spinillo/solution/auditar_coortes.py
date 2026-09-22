#!/usr/bin/env python3
"""Separa universos analíticos por pergunta, sem corrigir valores de origem.

Uso: python3 solution/auditar_coortes.py dataset1.zip dataset2.zip
Saída agregada JSON, sem dados pessoais. Não declara uma base globalmente limpa.
"""
import collections
from datetime import datetime
import json
import statistics
import sys

from explorar_cx import read_zip


def normalized(value):
    return ' '.join(value.casefold().split())


def summarize_ratings(rows):
    values = [float(x['Customer Satisfaction Rating']) for x in rows if x['Customer Satisfaction Rating']]
    return {
        'n_tickets': len(rows),
        'n_ratings': len(values),
        'mean': statistics.mean(values) if values else None,
        'distribution': dict(sorted(collections.Counter(values).items())),
        'low_1_2_n': sum(v <= 2 for v in values),
        'high_4_5_n': sum(v >= 4 for v in values),
    }


def main():
    sha1, rows = read_zip(sys.argv[1])
    sha2, rows2 = read_zip(sys.argv[2])
    email_groups = collections.defaultdict(list)
    text_groups = collections.defaultdict(list)
    for row in rows:
        email_groups[normalized(row['Customer Email'])].append(row)
        text_groups[normalized(row['Ticket Description'])].append(row)
    ambiguous = {email for email, group in email_groups.items() if len({normalized(x['Customer Name']) for x in group}) > 1}
    identity_candidates = [x for x in rows if normalized(x['Customer Email']) not in ambiguous]
    repeated_text = [g for g in text_groups.values() if len(g) > 1]
    paired = [x for x in rows if x['First Response Time'] and x['Time to Resolution']]
    chronological = [x for x in paired if datetime.fromisoformat(x['Time to Resolution']) >= datetime.fromisoformat(x['First Response Time'])]
    ratings_present = [x for x in rows if x['Customer Satisfaction Rating']]
    ratings_valid = []
    for row in ratings_present:
        try:
            v = float(row['Customer Satisfaction Rating'])
            if v.is_integer() and 1 <= v <= 5:
                ratings_valid.append(row)
        except ValueError:
            pass
    d2_docs = collections.defaultdict(list)
    for row in rows2:
        d2_docs[normalized(row['Document'])].append(row['Topic_group'])
    d2_valid = [x for x in rows2 if normalized(x['Document']) and x['Topic_group'].strip()]
    result = {
        'reference_date': '2026-09-15',
        'sha256_csv': {'dataset_1': sha1, 'dataset_2': sha2},
        'rule': 'Filtros independentes por finalidade. Quantidades sinalizadas podem se sobrepor; não somar exclusões. Nenhuma reclassificação ou imputação aplicada.',
        'd1': {
            'n': len(rows),
            'columns': list(rows[0]),
            'unique_ticket_ids': len({x['Ticket ID'] for x in rows}),
            'missing_any_field_n': sum(any(not v.strip() for v in x.values()) for x in rows),
            'identity': {
                'ambiguous_email_groups': len(ambiguous),
                'ambiguous_rows': len(rows) - len(identity_candidates),
                'remaining_rows': len(identity_candidates),
                'remaining_unique_emails': len({normalized(x['Customer Email']) for x in identity_candidates}),
                'max_names_per_email': max(len({normalized(x['Customer Name']) for x in group}) for group in email_groups.values()),
                'interpretation': 'Restante não tem repetição de email e não permite observar reincidência por essa chave. Identidade de origem não validada.',
            },
            'time': {
                'missing_pair': len(rows) - len(paired),
                'paired': len(paired),
                'resolution_before_response': len(paired) - len(chronological),
                'nonnegative_order': len(chronological),
                'opening_timestamp_present': False,
                'eligible_for_opening_based_duration': 0,
                'interpretation': 'Descartar pares invertidos não cria abertura nem valida esforço/tempo de resolução nos pares restantes. Não classificar restante como SLA limpo.',
            },
            'satisfaction': {
                'missing_n': len(rows) - len(ratings_present),
                'present_n': len(ratings_present),
                'valid_integer_1_to_5_n': len(ratings_valid),
                'invalid_n': len(ratings_present) - len(ratings_valid),
                'status_of_valid': dict(collections.Counter(x['Ticket Status'] for x in ratings_valid)),
                'all': summarize_ratings(rows),
                'excluding_ambiguous_identity': summarize_ratings(identity_candidates),
                'interpretation': 'Válido no formato, não valida representatividade nem realismo. Não imputar ausência. Comparação sem emails ambíguos é sensibilidade, não filtro necessário à descrição por ticket.',
            },
            'text': {
                'nonempty_n': sum(bool(normalized(x['Ticket Description'])) for x in rows),
                'product_placeholder_n': sum('{product_purchased}' in x['Ticket Description'] for x in rows),
                'normalized_repeated_groups': len(repeated_text),
                'rows_in_repeated_groups': sum(map(len, repeated_text)),
                'different_labels_for_same_normalized_text': {
                    col: {
                        'groups': sum(len({x[col] for x in g}) > 1 for g in repeated_text),
                        'rows': sum(len(g) for g in repeated_text if len({x[col] for x in g}) > 1),
                    }
                    for col in ['Ticket Type', 'Ticket Subject', 'Ticket Priority']
                },
                'interpretation': 'Mesmo texto com rótulos diferentes limita predição baseada apenas no texto. Não prova erro em todos os casos: contexto externo pode mudar prioridade. Remover placeholder não valida semântica.',
            },
            'urgency_sensitivity': {
                name: {
                    'literal_urgently_n': sum('urgently' in x['Ticket Description'].lower() for x in cohort),
                    'literal_urgently_low_medium_n': sum('urgently' in x['Ticket Description'].lower() and x['Ticket Priority'] in ['Low', 'Medium'] for x in cohort),
                }
                for name, cohort in [('all_rows', rows), ('excluding_ambiguous_identity', identity_candidates)]
            },
            'not_present': ['agent_id', 'assignment_history', 'message_thread', 'pending_reason', 'nps', 'opening_timestamp', 'confirmed_deadline'],
        },
        'd2': {
            'n': len(rows2),
            'columns': list(rows2[0]),
            'nonempty_text_and_label_n': len(d2_valid),
            'distinct_labels': sorted({x['Topic_group'] for x in rows2}),
            'normalized_duplicate_excess_rows': sum(len(labels) - 1 for labels in d2_docs.values()),
            'normalized_text_conflicting_label_groups': sum(len(set(labels)) > 1 for labels in d2_docs.values()),
            'near_duplicates_checked': False,
            'semantic_labels_validated': False,
            'interpretation': 'Candidatos à avaliação de categoria após checagem formal; não uma declaração de limpeza semântica completa.',
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Uso: auditar_coortes.py dataset1.zip dataset2.zip')
    main()
