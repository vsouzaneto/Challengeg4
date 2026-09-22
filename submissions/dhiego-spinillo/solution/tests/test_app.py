import csv
import hashlib
import io
import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as module
from recap import RecapValidationError
from triage_core import LABELS


class Classifier:
    classes_ = list(LABELS)

    def __init__(self, category='Hardware', score=.9):
        self.category, self.score = category, score

    def predict_proba(self, texts):
        return [[self.score if label == self.category else (1-self.score)/7 for label in self.classes_]]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(module, 'DB_PATH', tmp_path / 'reviews.sqlite3')
    monkeypatch.setattr(module, 'key_from_env', lambda name: None)
    module.app.dependency_overrides[module.get_classifier] = lambda: Classifier()
    with TestClient(module.app) as client:
        yield client
    module.app.dependency_overrides.clear()


def analyze(client, **changes):
    return client.post('/api/analyze', json={
        'text': 'Meu computador precisa de reparo.', 'domain_confirmed': True,
        'include_recap': False, **changes,
    })


@pytest.mark.parametrize('text', ['', ' '*20, 'curto', 'x'*16001])
def test_reject_invalid_text(client, text):
    assert analyze(client, text=text).status_code == 422


def test_domain_is_required_boolean(client):
    assert client.post('/api/analyze', json={'text': 'Preciso de ajuda no laptop'}).status_code == 422
    assert analyze(client, domain_confirmed='true').status_code == 422


def test_policy_and_contract(client):
    result = analyze(client).json()
    assert result['prediction'] == 'Hardware'
    assert result['threshold'] == .61
    assert result['policy']['action'] == 'suggest'
    assert result['policy']['requires_human_confirmation'] is True
    assert sum(result['probabilities'].values()) == pytest.approx(1)
    assert result['elapsed_ms'] >= 0
    assert result['recap'] is None
    assert analyze(client, domain_confirmed=False).json()['policy']['action'] == 'review'


@pytest.mark.parametrize('category,score', [('Hardware', .60), ('Access', .99), ('Administrative rights', .99)])
def test_manual_review(client, category, score):
    module.app.dependency_overrides[module.get_classifier] = lambda: Classifier(category, score)
    assert analyze(client).json()['policy']['action'] == 'review'


def test_unconfigured_recap_preserves_classification(client):
    result = analyze(client, include_recap=True).json()
    assert result['prediction'] == 'Hardware'
    assert result['recap'] is None
    assert 'não configurado' in result['recap_error']


@pytest.mark.parametrize('error', [RecapValidationError('Recap omitido: citação inválida.'), RuntimeError('secret-provider-error')])
def test_recap_failure_preserves_classification(client, monkeypatch, error):
    monkeypatch.setattr(module, 'key_from_env', lambda name: 'secret-key')

    async def failed(text):
        raise error

    monkeypatch.setattr(module, 'generate_recap', failed)
    result = analyze(client, include_recap=True)
    assert result.status_code == 200
    assert result.json()['prediction'] == 'Hardware'
    assert result.json()['recap'] is None
    assert result.json()['recap_error']
    assert 'secret' not in result.text


def test_review_persistence_and_private_export(client):
    original = '=PRIVATE original computer report'
    result = analyze(client, text=original).json()
    payload = {'analysis_id': result['analysis_id'], 'category': 'Storage', 'reason': '=HYPERLINK("bad")'}
    saved = client.post('/api/review', json=payload)
    assert saved.status_code == 200
    assert saved.json()['original_category'] == 'Hardware'
    assert saved.json()['category'] == 'Storage'
    with sqlite3.connect(module.DB_PATH) as db:
        row = db.execute('SELECT original_text,text_sha256 FROM analyses').fetchone()
        assert row == (original, hashlib.sha256(original.encode()).hexdigest())
        assert db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0] == 1
    with TestClient(module.app) as restarted_client:
        export = restarted_client.get('/api/export')
    assert original not in export.text
    rows = list(csv.DictReader(io.StringIO(export.text.lstrip('\ufeff'))))
    assert rows[0]['reason'].startswith("'=")
    assert rows[0]['analysis_id'] == result['analysis_id']
    assert 'original_text' not in rows[0]
    assert 'attachment' in export.headers['content-disposition']


def test_multiple_reviews_preserve_original(client):
    result = analyze(client).json()
    for category in ('Storage', 'Purchase'):
        response = client.post('/api/review', json={
            'analysis_id': result['analysis_id'], 'category': category, 'reason': 'Revisado pelo atendente',
        })
        assert response.json()['original_category'] == 'Hardware'
    with sqlite3.connect(module.DB_PATH) as db:
        assert db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0] == 2


def test_invalid_review(client):
    good = {'analysis_id': 'missing', 'category': 'Hardware', 'reason': 'Revisto'}
    assert client.post('/api/review', json=good).status_code == 404
    for changes in ({'category': 'Other'}, {'reason': '  '}, {'reason': 'x'*1001}):
        assert client.post('/api/review', json={**good, **changes}).status_code == 422


@pytest.mark.parametrize('path', ['/.env', '/artifacts/classifier.joblib', '/artifacts/reviews.sqlite3',
    '/reports/comparison/jev-predictions.jsonl', '/reports/comparison/local-predictions.json',
    '/reports/%2e%2e/%2e%2e/.env', '/solution/app.py', '/reports/comparison/split.json'])
def test_private_files_not_served(client, path):
    assert client.get(path).status_code == 404


def test_public_evidence_and_examples(client):
    summary = client.get('/api/evidence').json()
    assert summary['systems']['tfidf_logistic']['test']['accuracy_including_api_errors'] == .86
    assert client.get('/reports/comparison/summary.json').status_code == 200
    assert client.get('/diagnostico').status_code == 200
    example = client.get('/api/examples').json()[0]
    assert {'text', 'dataset_label', 'disclaimer', 'row'} <= set(example)
    assert 'não é verdade revisada' in example['disclaimer']


def test_health_does_not_expose_key(client, monkeypatch):
    monkeypatch.setattr(module, 'get_model', lambda: Classifier())
    monkeypatch.setattr(module, 'key_from_env', lambda name: 'secret-key')
    response = client.get('/api/health')
    assert response.json() == {'model_available': True, 'recap_available': True}
    assert 'secret' not in response.text


@pytest.mark.parametrize('value', ['=1+1', '+cmd', '-2+1', '@SUM(A1)', '   =1', '\t=1', '\ntext', '\ufeff=1'])
def test_csv_escapes_formula_prefixes(value):
    assert module.csv_safe(value).startswith("'")


def test_classifier_failure_is_explicit(client):
    module.app.dependency_overrides[module.get_classifier] = lambda: object()
    response = analyze(client)
    assert response.status_code == 503
    assert 'revisão manual' in response.json()['detail']
