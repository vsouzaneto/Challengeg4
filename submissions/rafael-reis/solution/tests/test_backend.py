"""Check executável do backend real; preserva as sessões de teste em .cache."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from backend.app import create_app
from backend.pipeline import catalog_ready


def main():
    assert catalog_ready(ROOT / 'artifacts' / 'v1' / 'catalog.sqlite3')
    invalid_catalog = ROOT / '.cache' / f'backend-invalid-catalog-{uuid.uuid4().hex}.sqlite3'
    with sqlite3.connect(invalid_catalog):
        pass
    assert not catalog_ready(invalid_catalog)
    database = ROOT / '.cache' / f'backend-tests-{uuid.uuid4().hex}.sqlite3'
    app = create_app(database=database, start_worker=False)
    pipeline, store = app.state.pipeline, app.state.store
    with TestClient(app) as client:
        def post(path, data):
            response = client.post(path, json=data)
            assert response.status_code == 200, (path, response.status_code, response.text)
            return response.json()

        assert client.get('/api/health').status_code == 200
        assert client.get('/api/health', headers={'origin': 'https://example.com'}).status_code == 403
        assert client.get('/api/assets/customer_support_tickets.csv').status_code == 404
        assert client.get('/assets/logo-g4-branca.svg').status_code == 200
        for body in ({'text': '  '}, {'text': 'x', 'dataset_id': 'other'}, {'text': 'x' * 10001}):
            assert client.post('/api/tickets/analyze', json=body).status_code == 422
        assert client.get('/api/tickets?limit=1000').status_code == 422
        assert client.get('/api/diagnosis?group_by=channel,../status').status_code == 422
        diagnosis = client.get('/api/diagnosis').json()
        assert diagnosis['total'] == 8469 and diagnosis['csat']['count'] == 2769
        assert sum(diagnosis['csat']['distribution'].values()) == 2769
        with_csat = client.get('/api/diagnosis?csat_presence=present').json()
        without_csat = client.get('/api/diagnosis?csat_presence=missing').json()
        score_five = client.get('/api/diagnosis?csat_score=5').json()
        assert with_csat['total'] == 2769 and without_csat['total'] == 5700
        assert score_five['total'] == score_five['csat']['count'] == 544
        assert diagnosis['temporal']['ttr_available'] is False
        assert len(diagnosis['crossings']) == 6
        for groups in diagnosis['crossings'].values():
            assert sum(group['count'] for group in groups) == 8469
            assert all('csat_p95' in group and 'csat_std' in group for group in groups)
        empty = client.get('/api/diagnosis?channel=does-not-exist').json()
        assert empty['total'] == 0 and empty['csat']['mean'] is None and empty['groups'] == []
        assert empty['temporal']['quality_scope'] == 'full_dataset'

        payload = {'dataset_id': 'ds2', 'size': 5, 'scenario': 'incident', 'speed': 10, 'request_id': str(uuid.uuid4())}
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: post('/api/sessions', payload), range(2)))
        sid = results[0]['session_id']
        assert results[1]['session_id'] == sid
        session_created = store.events(sid)['items'][0]
        assert session_created['event_type'] == 'SESSION_CREATED'
        assert session_created['source'] == 'simulation' and session_created['content_origin'] == 'ds2'
        assert session_created['dataset_id'] == 'ds2' and session_created['space_id'] == 'ds2-semantic-v1'
        assert session_created['policy_version']
        assert client.post('/api/sessions', json=dict(payload, size=6)).status_code == 422
        post(f'/api/sessions/{sid}/control', {'action': 'play'})
        post(f'/api/sessions/{sid}/control', {'action': 'pause'})
        assert store.snapshot(sid)['state'] == 'PAUSED'
        assert client.post(f'/api/sessions/{sid}/control', json={'action': 'speed', 'speed': 3}).status_code == 422
        post(f'/api/sessions/{sid}/control', {'action': 'play'})
        session = store.session(sid)
        assert len(set(session['config']['ticket_ids'])) == 5
        for i, source_id in enumerate(session['config']['ticket_ids']):
            result = pipeline.analyze(pipeline.ticket(source_id)['text'], 'ds2', source_id)
            assert result['review_threshold'] == pipeline.review_threshold()
            assert all(n['ticket_id'] != source_id for n in result['similar_tickets'])
            store.save_ticket(result, sid, 'simulation', replay_index=i)
        snapshot = store.snapshot(sid)
        assert snapshot['state'] == 'COMPLETED' and snapshot['processed'] == 5
        assert snapshot['metrics']['median_ttr'] is None and snapshot['metrics']['csat'] is None
        assert snapshot['metrics']['triage_eligible_count'] == 5
        assert snapshot['metrics']['triage_ineligible_count'] == 0
        assert snapshot['metrics']['human_review_count'] + snapshot['metrics']['auto_routed_count'] == 5
        assert snapshot['metrics']['human_review_rate'] == snapshot['metrics']['human_review_count'] / 5
        assert snapshot['metrics']['auto_route_rate'] == snapshot['metrics']['auto_routed_count'] / 5
        events, cursor = [], 0
        while True:
            page = store.events(sid, cursor, 7)
            events.extend(page['items'])
            cursor = page['next_seq']
            if not page['has_more']:
                break
        assert [e['seq'] for e in events] == list(range(1, snapshot['last_seq'] + 1))
        assert sum(e['event_type'] == 'TICKET_ARRIVED' for e in events) == 5
        arrivals = [event for event in events if event['event_type'] == 'TICKET_ARRIVED']
        assert all(event['source'] == 'simulation' and event['content_origin'] == 'ds2'
                   and event['policy_version'] and event['space_id'] == 'ds2-semantic-v1' for event in arrivals)
        names = [event['event_type'] for event in events]
        assert names.index('TICKET_ARRIVED') < names.index('CLASSIFICATION_STARTED') < names.index('CLASSIFICATION_COMPLETED')
        assert all('text' not in n for e in events if e['event_type'] == 'NEIGHBORS_FOUND' for n in e['payload']['neighbors'])
        assert client.get(f'/api/sessions/{sid}/events?after_seq=999999').status_code == 422
        alert = snapshot['alerts'][0]
        assert 'mean_similarity' in alert
        graph = client.get('/api/spaces/ds2-semantic-v1/graph', params={'session_id': sid, 'alert_id': alert['alert_id']}).json()
        assert set(alert['ticket_ids']) <= {n['id'] for n in graph['nodes']}
        assert all('type' in edge and 'method' in edge for edge in graph['edges'])
        overview = client.get('/api/spaces/ds2-semantic-v1/graph', params={'session_id': sid}).json()
        assert overview['noise_count'] == 40640 and overview['session_ticket_count'] == 5
        assert any(n['is_noise'] and n['count'] == 40640 for n in overview['nodes'])
        assert sum(n['session_count'] for n in overview['nodes']) == 5

        partial_sid = store.create({'kind': 'sandbox', 'dataset_id': 'ds2', 'ticket_ids': [],
                                    'space_id': 'ds2-semantic-v1', 'policy_version': 'policy-v1'})
        store.save_ticket({'text': 'partial', 'dataset_id': 'ds2', 'processing_status': 'partial',
                           'errors': ['semantic unavailable'], 'decision_origin': 'policy_suggested',
                           'suggested_route': 'Triagem geral', 'human_review_required': True},
                          partial_sid, 'user_created')
        partial_metrics = store.snapshot(partial_sid)['metrics']
        assert partial_metrics['processed'] == 1 and partial_metrics['triage_eligible_count'] == 0
        assert partial_metrics['triage_ineligible_count'] == 1
        assert partial_metrics['human_review_rate'] is None and partial_metrics['auto_route_rate'] is None

        manual_payload = {'text': 'Não consigo acessar minha conta depois de trocar a senha.',
                          'dataset_id': 'ds2', 'request_id': str(uuid.uuid4())}
        manual = post('/api/tickets/analyze', manual_payload)
        repeated = post('/api/tickets/analyze', manual_payload)
        assert manual['ticket_id'] == repeated['ticket_id']
        assert manual['inference_mode'] == 'online' and manual['human_review_required']
        assert manual['suggested_action']
        assert any('idioma' in reason for reason in manual['review_reasons'])
        assert manual['similar_tickets'] and manual['position_method'] == 'umap_transform'
        sandbox_created = store.events(manual['session_id'])['items'][0]
        assert sandbox_created['source'] == sandbox_created['content_origin'] == 'user_created'
        assert sandbox_created['dataset_id'] == 'ds2' and sandbox_created['space_id'] == 'ds2-semantic-v1'
        assert store.snapshot(manual['session_id'])['processed'] == 0
        focused = client.get('/api/spaces/ds2-semantic-v1/graph', params={'session_id': manual['session_id'], 'ticket_id': manual['ticket_id']}).json()
        assert manual['ticket_id'] in {n['id'] for n in focused['nodes']}
        low_confidence = post('/api/tickets/analyze', {'text': 'aoeui qzxv blorp', 'dataset_id': 'ds2',
                                                        'request_id': str(uuid.uuid4())})
        assert low_confidence['confidence'] < low_confidence['review_threshold']
        assert any('abaixo do limiar' in reason for reason in low_confidence['review_reasons'])

        live = post('/api/sessions', {'dataset_id': 'ds2', 'size': 1, 'scenario': 'mixed', 'speed': 1,
                                      'request_id': str(uuid.uuid4())})
        live_payload = {'text': 'My account access is blocked after a password reset.', 'dataset_id': 'ds2',
                        'session_id': live['session_id'], 'add_to_live_session': True, 'request_id': str(uuid.uuid4())}
        live_manual = post('/api/tickets/analyze', live_payload)
        assert post('/api/tickets/analyze', live_payload)['ticket_id'] == live_manual['ticket_id']
        live_snapshot = store.snapshot(live['session_id'])
        assert live_snapshot['processed'] == live_snapshot['manual_processed'] == 1
        assert live_snapshot['metrics']['source_counts'] == {'user_created': 1}
        other = post('/api/sessions', {'dataset_id': 'ds2', 'size': 1, 'scenario': 'mixed', 'speed': 1,
                                       'request_id': str(uuid.uuid4())})
        assert client.post('/api/copilot/suggestions', json={'ticket_id': live_manual['ticket_id'],
                                                              'session_id': other['session_id']}).status_code == 422

        sample = next(row for row in pipeline.catalog.values() if row['dataset_id'] == 'ds1' and row.get('resolution'))
        suggestion = post('/api/copilot/suggestions', {'ticket_id': sample['ticket_id'], 'request_id': str(uuid.uuid4())})
        assert suggestion['status'] == 'ready' and suggestion['sources']
        suggestion_events = store.events(suggestion['session_id'])['items']
        generated = next(event for event in suggestion_events if event['event_type'] == 'SUGGESTION_GENERATED')
        assert generated['source'] == 'historical' and generated['content_origin'] == 'ds1'
        assert generated['dataset_id'] == 'ds1' and generated['space_id'] == 'ds1-semantic-v1'
        feedback_payload = {'suggestion_id': suggestion['suggestion_id'], 'decision': 'edit',
                            'text': 'Revisado para validação humana.', 'request_id': str(uuid.uuid4())}
        edited = post('/api/feedback', feedback_payload)
        assert post('/api/feedback', feedback_payload)['feedback_id'] == edited['feedback_id']
        assert edited['original_text'] == suggestion['text']
        post('/api/feedback', {'suggestion_id': suggestion['suggestion_id'], 'decision': 'reject'})
        feedback_snapshot = store.snapshot(suggestion['session_id'])
        assert feedback_snapshot['metrics']['feedback'] == {'reject': 1}
        assert feedback_snapshot['metrics']['feedback_denominator'] == 1
        feedback_event = [event for event in store.events(suggestion['session_id'])['items'] if event['event_type'] == 'FEEDBACK_RECORDED'][-1]
        assert feedback_event['source'] == 'historical' and feedback_event['content_origin'] == 'ds1'
        unavailable = post('/api/copilot/suggestions', {'ticket_id': manual['ticket_id']})
        assert unavailable['status'] == 'insufficient_evidence' and not unavailable['sources']
        assert store.snapshot(unavailable['session_id'])['metrics']['suggestions'] == 0
        assert client.post('/api/feedback', json={'suggestion_id': unavailable['suggestion_id'], 'decision': 'accept'}).status_code == 422

        reset_payload = {'action': 'reset', 'request_id': str(uuid.uuid4())}
        reset = post(f'/api/sessions/{sid}/control', reset_payload)
        assert reset['session_id'] != sid
        assert post(f'/api/sessions/{sid}/control', reset_payload)['session_id'] == reset['session_id']
        assert store.snapshot(sid)['processed'] == 5
        assert store.events(sid)['items']
    cors_database = ROOT / '.cache' / f'backend-cors-{uuid.uuid4().hex}.sqlite3'
    cors_app = create_app(database=cors_database, start_worker=False, allowed_origins=['https://support.example.test'])
    with TestClient(cors_app) as client:
        response = client.get('/api/health', headers={'origin': 'https://support.example.test'})
        assert response.status_code == 200
        assert response.headers['access-control-allow-origin'] == 'https://support.example.test'
        assert client.get('/api/health', headers={'origin': 'https://other.example.test'}).status_code == 403
    unready_app = create_app(artifacts=ROOT / '.cache' / 'missing-artifacts',
                             database=ROOT / '.cache' / f'backend-unready-{uuid.uuid4().hex}.sqlite3', start_worker=False)
    with TestClient(unready_app) as client:
        response = client.get('/api/health')
        assert response.status_code == 503 and response.json()['status'] == 'degraded'
    print(f'Backend: validação, métricas, inferência real, sessão, idempotência concorrente, eventos, Graph e feedback OK. Auditoria: {database}')


if __name__ == '__main__':
    main()
