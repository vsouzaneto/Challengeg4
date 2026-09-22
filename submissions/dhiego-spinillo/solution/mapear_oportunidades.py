"""Busca exploratória integral no D2. Menção não mede intenção nem elegibilidade.

Uso: python solution/mapear_oportunidades.py data/dataset2.zip
"""
import collections
import json
import random
import re
import sys
from explorar_cx import read_zip

PATTERNS = {
    'password_reset': r'\b(?:password\s+reset\w*|reset\w*\s+(?:(?:my|your|the)\s+)?password)\b',
    'profile_update': r'\b(?:updat\w*|chang\w*|modif\w*|correct\w*)\b.{0,55}\b(?:profile|personal details|personal information|contact details|phone number|mobile number)\b|\b(?:profile|personal details|personal information|contact details|phone number|mobile number)\b.{0,55}\b(?:updat\w*|chang\w*|modif\w*|correct\w*)\b',
    'distress_words': r'\b(?:frustrat\w*|angry|unhappy|disappoint\w*)\b',
}


def main():
    sha, rows = read_zip(sys.argv[1])
    results = {}
    for name, expression in PATTERNS.items():
        pattern = re.compile(expression, re.I)
        matched = [(i, row) for i, row in enumerate(rows, 1) if pattern.search(row['Document'])]
        results[name] = {
            'regex': expression, 'count': len(matched), 'pct': len(matched) / len(rows) * 100,
            'categories': dict(collections.Counter(row['Topic_group'] for _, row in matched)),
            'inspection_seed': 42,
            'inspection_rows': [i for i, _ in random.Random(42).sample(matched, min(6, len(matched)))],
        }
    print(json.dumps({'csv_sha256': sha, 'n': len(rows), 'row_numbering': '1-based data rows, excluding header',
                      'limitation': 'Overlapping keyword searches, not labeled intentions, sentiment, or automation eligibility. Do not extrapolate to challenge annual volume.',
                      'results': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
