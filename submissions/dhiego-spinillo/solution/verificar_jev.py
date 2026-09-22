#!/usr/bin/env python3
"""Uma chamada sintética para verificar acesso ao Jev; não é benchmark."""
import json
import os
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    root = Path(__file__).resolve().parent
    key = os.environ.get('TYPESAFE_API_KEY')
    env_file = root.parent / '.env'
    if not key and env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith('TYPESAFE_API_KEY='):
                key = line.split('=', 1)[1].strip()
                break
    if not key:
        raise SystemExit('Configure TYPESAFE_API_KEY no ambiente ou no .env local.')

    payload = {
        'model': 'jev-latest',
        'state': 'My laptop will not power on. I tried another charger and it still will not start.',
        'questions': {
            'category': {
                'type': 'choice',
                'instructions': 'Classify the main issue described in this support request.',
                'criteria': {
                    'hardware': 'Physical computer, charger, or peripheral problems.',
                    'billing': 'Invoices, payments, or charges.',
                    'access': 'Login, passwords, or account permissions.',
                },
            },
        },
    }
    request = Request(
        'https://api.typesafe.ai/v1/systemone',
        data=json.dumps(payload).encode(),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
        method='POST',
    )
    # Python instalado separadamente no macOS pode não localizar o bundle do sistema.
    ca_file = ssl.get_default_verify_paths().cafile
    if ca_file is None and Path('/etc/ssl/cert.pem').is_file():
        ca_file = '/etc/ssl/cert.pem'
    context = ssl.create_default_context(cafile=ca_file)
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=45, context=context) as response:
            status = response.status
            result = json.load(response)
    except HTTPError as error:
        raise SystemExit(f'API retornou HTTP {error.code}; corpo e credencial omitidos.') from None
    except URLError as error:
        raise SystemExit(f'Falha de conexão/TLS ({type(error.reason).__name__}); detalhes sensíveis omitidos.') from None
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    answer = result.get('answers', {}).get('category', {})
    if answer.get('choice') not in payload['questions']['category']['criteria']:
        raise SystemExit('Resposta sem uma categoria válida; relatório não gravado.')
    report = {
        'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'purpose': 'Verificação de acesso e formato; um exemplo sintético, não benchmark do D2.',
        'request': payload,
        'http_status': status,
        'model_returned': result.get('model'),
        'answer': {k: answer[k] for k in ('type', 'choice', 'confidence', 'probabilities') if k in answer},
        'usage': {k: result.get('usage', {}).get(k) for k in ('input_tokens', 'output_tokens')},
        'elapsed_ms_client_single_request': elapsed_ms,
        'limitations': 'Inclui rede/TLS; não mede latência típica, calibração, acurácia ou economia. Não houve retentativa automática.',
    }
    target = root / 'reports/jev-conexao.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f'HTTP {status}; categoria: {answer["choice"]}; modelo: {result.get("model")}.')
    print(f'Relatório: {target.name}. Uma chamada sintética concluída; credencial omitida.')


if __name__ == '__main__':
    main()
