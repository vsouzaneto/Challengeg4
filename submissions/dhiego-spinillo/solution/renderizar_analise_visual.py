#!/usr/bin/env python3
"""Gera a v1 visual a partir dos relatórios versionados; nenhuma chamada de IA."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
reports = root / 'reports'
data = {
    name: json.loads((reports / filename).read_text())
    for name, filename in {
        'audit': 'auditoria-datasets.json',
        'cx': 'exploracao-cx.json',
        'quality': 'coortes-qualidade.json',
        'context': 'contexto-e-recap.json',
    }.items()
}
serialized = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
template = (root / 'visual/template.html').read_text()
logo = (root / 'visual/assets/g4-logo.svg').read_text()
html = template.replace('__DATA__', serialized).replace('__LOGO__', logo)
(root / 'visual/index.html').write_text(html)
print(f'Análise visual gerada: {len(html.encode())} bytes; quatro relatórios incorporados.')
