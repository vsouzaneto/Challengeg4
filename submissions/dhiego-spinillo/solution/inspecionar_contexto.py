#!/usr/bin/env python3
"""Extrai exemplos públicos para discutir compreensão e recap; não implementa IA.

Uso: python3 solution/inspecionar_contexto.py dataset1.zip dataset2.zip
Posições no D2 são 1-based, sem cabeçalho, e dependem do hash do CSV.
"""
import json
import statistics
import sys

from explorar_cx import read_zip


def profile(rows, col):
    lengths = sorted(len(x[col].split()) for x in rows)
    return {
        'n': len(rows),
        'columns': list(rows[0]),
        'word_count_min': lengths[0],
        'word_count_median': statistics.median(lengths),
        'word_count_p95_lower_order_statistic': lengths[int((len(lengths) - 1) * .95)],
        'word_count_max': lengths[-1],
        'at_least_100_words': sum(n >= 100 for n in lengths),
        'at_least_200_words': sum(n >= 200 for n in lengths),
        'at_least_500_words': sum(n >= 500 for n in lengths),
        'interpretation': 'Comprimento não comprova múltiplas interações ou uma conversa completa.',
    }


def main():
    sha1, rows = read_zip(sys.argv[1])
    sha2, rows2 = read_zip(sys.argv[2])
    selected = ['7', '68']
    d2_positions = [2982, 8614, 9766]
    out = {
        'reference_date': '2026-09-15',
        'sha256_csv': {'dataset_1': sha1, 'dataset_2': sha2},
        'selection': 'Exemplos intencionais encontrados na exploração de termos; não são amostra aleatória nem validação de recap. Nenhuma chamada à API de modelo.',
        'dataset_1': profile(rows, 'Ticket Description'),
        'dataset_2': profile(rows2, 'Document'),
        'd1_examples': [
            {k: x[k] for k in ['Ticket ID', 'Ticket Type', 'Ticket Subject', 'Ticket Description', 'Ticket Priority']}
            for x in rows if x['Ticket ID'] in selected
        ],
        'd2_examples': [
            {'row_position_1_based_without_header': i, 'topic_group': rows2[i - 1]['Topic_group'], 'document': rows2[i - 1]['Document']}
            for i in d2_positions
        ],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Uso: inspecionar_contexto.py dataset1.zip dataset2.zip')
    main()
