"""Check the connected product against a running local service; preserve every session."""
from pathlib import Path
import csv
import hashlib
import json
import os
import time
import uuid

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("SUPPORT_BASE_URL", "http://127.0.0.1:8000")


def main():
    checks = []
    with httpx.Client(base_url=BASE, timeout=180) as client:
        def get(path, **params):
            response = client.get(path, params=params)
            response.raise_for_status()
            return response.json()

        def post(path, **data):
            response = client.post(path, json=data)
            response.raise_for_status()
            return response.json()

        health = get('/api/health')
        catalog = get('/api/catalog')
        assert catalog and health
        diagnosis = get('/api/diagnosis')
        assert diagnosis['total'] == 8469
        assert diagnosis['csat']['count'] == 2769
        assert diagnosis['csat']['positive_count'] == 1087
        assert diagnosis['temporal']['ttr_available'] is False
        with (ROOT / 'customer_support_tickets.csv').open(newline='', encoding='utf-8-sig') as stream:
            raw = list(csv.DictReader(stream))
        selected = [r for r in raw if r['Ticket Channel'] == 'Phone' and r['Ticket Priority'] == 'High']
        cut = get('/api/diagnosis', channel='Phone', priority='High')
        assert cut['total'] == len(selected)
        checks.append('Agregações e recorte conferem com CSV; duração indisponível.')

        metrics = get('/api/models/current')
        assert 0 < metrics['macro_f1'] <= 1 and metrics['split']['test']['count'] == 7176
        invalid = client.post('/api/tickets/analyze', json={'text': ' ', 'dataset_id': 'ds2'})
        assert invalid.status_code == 422
        request_id = str(uuid.uuid4())
        payload = dict(text='I changed my password yesterday and now I cannot access my work account.',
                       dataset_id='ds2', request_id=request_id, add_to_live_session=False)
        manual = post('/api/tickets/analyze', **payload)
        same = post('/api/tickets/analyze', **payload)
        assert manual['ticket_id'] == same['ticket_id']
        assert manual['source'] == 'user_created' and manual['inference_mode'] == 'online'
        assert manual['model_version'] == metrics['model_version']
        assert manual['similar_tickets'] and manual['coordinates']
        assert manual['human_review_required']
        graph = get('/api/spaces/ds2-semantic-v1/graph', ticket_id=manual['ticket_id'],
                    session_id=manual['session_id'], level='tickets')
        assert any(n['id'] == manual['ticket_id'] for n in graph['nodes'])
        edge_neighbors = {e['target'] for e in graph['edges'] if e['source'] == manual['ticket_id']}
        assert edge_neighbors.intersection(n['ticket_id'] for n in manual['similar_tickets'])
        assert get(f"/api/sessions/{manual['session_id']}/snapshot")['processed'] == 0
        checks.append('Entrada manual real, idempotência, sandbox e Lab→Graph conectados.')

        session = post('/api/sessions', dataset_id='ds2', size=10, scenario='incident', speed=10,
                       request_id=str(uuid.uuid4()))
        sid = session['session_id']
        post(f'/api/sessions/{sid}/control', action='play', request_id=str(uuid.uuid4()))
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            snapshot = get(f'/api/sessions/{sid}/snapshot')
            if snapshot['state'] == 'COMPLETED':
                break
            if snapshot.get('error'):
                raise AssertionError(snapshot['error'])
            time.sleep(.4)
        assert snapshot['state'] == 'COMPLETED', snapshot['state']
        assert snapshot['processed'] == snapshot['total'] == 10
        assert snapshot['metrics']['median_ttr'] is None
        assert snapshot['metrics']['csat'] is None
        events, cursor = [], 0
        while True:
            response = get(f'/api/sessions/{sid}/events', after_seq=cursor, limit=30)
            events.extend(response['items'])
            cursor = response['next_seq']
            if not response['has_more']:
                break
        seqs = [e['seq'] for e in events]
        assert seqs == sorted(set(seqs)) and cursor == snapshot['last_seq']
        assert sum(e['event_type'] == 'TICKET_ARRIVED' for e in events) == 10
        assert snapshot['alerts'], 'Cenário concentrado não gerou alerta; revisar evidência/regra.'
        alert = snapshot['alerts'][0]
        view = get('/api/spaces/ds2-semantic-v1/graph', session_id=sid, alert_id=alert['alert_id'],
                   cluster_id=alert['cluster_id'], level='tickets')
        visible = {n['id'] for n in view['nodes']}
        assert set(alert['ticket_ids']) <= visible
        reset = post(f'/api/sessions/{sid}/control', action='reset', request_id=str(uuid.uuid4()))
        assert reset['session_id'] != sid
        assert get(f'/api/sessions/{sid}/snapshot')['processed'] == 10
        checks.append('Replay, eventos paginados, alerta→Graph e reset sem exclusão verificados.')

        sample = next(r for r in raw if r['Resolution'])
        suggestion = post('/api/copilot/suggestions', ticket_id=f"ds1:{sample['Ticket ID']}",
                          request_id=str(uuid.uuid4()))
        assert suggestion['status'] == 'ready' and suggestion['sources'] and suggestion['text']
        feedback = post('/api/feedback', suggestion_id=suggestion['suggestion_id'], decision='edit',
                        text='Rascunho revisado para validação humana; nenhuma mensagem enviada.',
                        request_id=str(uuid.uuid4()))
        assert feedback['decision'] == 'edit'
        ds2_suggestion = post('/api/copilot/suggestions', ticket_id=manual['ticket_id'],
                              request_id=str(uuid.uuid4()))
        assert ds2_suggestion['status'] == 'insufficient_evidence'
        assert not ds2_suggestion['sources']
        checks.append('Copilot extrativo DS1, feedback persistido e isolamento DS2 verificados.')

    original = json.loads((ROOT / 'tests' / 'original-hashes.json').read_text())
    assert len(original) == 13
    for filename, expected in original.items():
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected, filename
    checks.append(f'{len(original)} arquivos originais íntegros.')
    print(json.dumps({'checks': checks, 'session_id': sid, 'manual_ticket_id': manual['ticket_id']},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
