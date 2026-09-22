import csv
import io
import json
import sqlite3

import pytest
from pydantic import ValidationError

from test_app import client, analyze
from investigation import Investigation, prepare_next_step
import app as module


def context(outcome='unknown', **overrides):
    return {'checks': {'other_tickets': 'checked', 'system': 'checked', 'internal_notes': 'checked'},
            'system_outcome': outcome, **overrides}


def test_unchecked_context_does_not_invent_customer_reply():
    plan = prepare_next_step(Investigation(), 'issue solved')
    assert plan['code'] == 'check_context'
    assert plan['reply_draft'] is None
    assert len(plan['pending_checks']) == 3
    assert plan['external_action_executed'] is False


@pytest.mark.parametrize('state,code,has_draft', [
    ('resolved', 'confirm_remaining_need', True),
    ('unresolved', 'update_diagnosis', True),
    ('unknown', 'recover_context', False),
])
def test_next_step_uses_recorded_system_result(state, code, has_draft):
    plan = prepare_next_step(Investigation(**context(state)), 'ticket unrelated to system outcome')
    assert plan['code'] == code
    assert bool(plan['reply_draft']) is has_draft
    assert plan['requires_human_confirmation'] is True


@pytest.mark.parametrize('unchecked', ['pending', 'unavailable'])
@pytest.mark.parametrize('outcome', ['resolved', 'unresolved'])
def test_system_outcome_requires_declared_system_consultation(unchecked, outcome):
    data = context(outcome)
    data['checks']['system'] = unchecked
    with pytest.raises(ValidationError):
        Investigation(**data)


def test_unavailable_is_not_unresolved():
    data = context()
    data['checks']['system'] = 'unavailable'
    plan = prepare_next_step(Investigation(**data), 'issue solved')
    assert plan['code'] == 'recover_context'
    assert plan['reply_draft'] is None
    assert plan['unavailable_checks'] == ['system']


def test_pending_internal_notes_prevents_premature_resolution_reply():
    data = context('resolved')
    data['checks']['internal_notes'] = 'pending'
    plan = prepare_next_step(Investigation(**data), 'original')
    assert plan['code'] == 'check_context'
    assert plan['reply_draft'] is None


def test_human_incident_signal_does_not_wait_for_routine_checks():
    original = 'annual leave seems able access data for another colleague'
    data = Investigation(incident_reported=True, incident_quote='access data for another colleague')
    plan = prepare_next_step(data, original)
    assert plan['code'] == 'investigate_incident'
    assert len(plan['pending_checks']) == 3
    assert plan['reply_draft']
    assert 'RLS' not in plan['reply_draft']
    assert 'causa' in ' '.join(plan['steps'])


@pytest.mark.parametrize('quote', ['', '   '])
def test_incident_requires_nonblank_quote(quote):
    with pytest.raises(ValidationError):
        Investigation(incident_reported=True, incident_quote=quote)


def test_incident_quote_must_belong_to_original():
    data = Investigation(incident_reported=True, incident_quote='invented evidence')
    with pytest.raises(ValueError):
        prepare_next_step(data, 'annual leave text')


@pytest.mark.parametrize('data', [
    {'incident_quote': 'unmarked'}, {'incident_reported': 'true'},
    {'checks': {'system': True}}, {'system_outcome': 'probably_resolved'},
    {'checks': {'system': 'checked', 'autocheck': True}},
])
def test_strict_context_rejects_inconsistent_or_unknown_values(data):
    with pytest.raises(ValidationError):
        Investigation(**data)


def test_preview_does_not_save_review_or_call_llm(client, monkeypatch):
    async def forbidden(*args, **kwargs):
        raise AssertionError('LLM must not run during rule-based preparation')
    monkeypatch.setattr(module, 'generate_recap', forbidden)
    analysis = analyze(client).json()
    result = client.post('/api/plan', json={'analysis_id': analysis['analysis_id'],
                                         'investigation': context('resolved')})
    assert result.status_code == 200
    assert result.json()['code'] == 'confirm_remaining_need'
    with sqlite3.connect(module.DB_PATH) as db:
        assert db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0] == 0


def test_incident_keeps_category_and_stores_edited_reply_but_export_omits_quote(client):
    original = 'PRIVATE account shows another person data'
    analysis = analyze(client, text=original).json()
    data = context(incident_reported=True, incident_quote='another person data')
    response = client.post('/api/review', json={'analysis_id': analysis['analysis_id'],
        'category': 'HR Support', 'reason': 'Investigar relato com responsável',
        'investigation': data, 'response_draft': 'Edited response retained locally'})
    assert response.status_code == 200
    assert response.json()['category'] == 'HR Support'
    assert response.json()['plan']['code'] == 'investigate_incident'
    with sqlite3.connect(module.DB_PATH) as db:
        saved = json.loads(db.execute('SELECT context_json FROM investigations').fetchone()[0])
        assert saved['response_draft'] == 'Edited response retained locally'
        assert saved['incident_quote'] == 'another person data'
    exported = client.get('/api/export').text
    assert original not in exported
    assert data['incident_quote'] not in exported
    assert 'Edited response' not in exported
    row = list(csv.DictReader(io.StringIO(exported.lstrip('\ufeff'))))[0]
    assert row['category'] == 'HR Support'
    assert row['next_step_code'] == 'investigate_incident'
    assert row['incident_reported'] == 'True'


def test_old_and_new_reviews_coexist(client):
    analysis = analyze(client).json()
    payload = {'analysis_id': analysis['analysis_id'], 'category': 'Hardware', 'reason': 'Revisão válida'}
    assert client.post('/api/review', json=payload).status_code == 200
    assert client.post('/api/review', json={**payload, 'investigation': context('unresolved')}).status_code == 200
    rows = list(csv.DictReader(io.StringIO(client.get('/api/export').text.lstrip('\ufeff'))))
    assert len(rows) == 2
    assert {r['next_step_code'] for r in rows} == {'', 'update_diagnosis'}


def test_invalid_quote_cannot_be_saved_by_skipping_preview(client):
    analysis = analyze(client).json()
    response = client.post('/api/review', json={'analysis_id': analysis['analysis_id'],
        'category': 'HR Support', 'reason': 'Relato precisa ser verificado',
        'investigation': context(incident_reported=True, incident_quote='not present')})
    assert response.status_code == 422
    with sqlite3.connect(module.DB_PATH) as db:
        assert db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0] == 0


def test_draft_cannot_bypass_unknown_context(client):
    analysis = analyze(client).json()
    response = client.post('/api/review', json={'analysis_id': analysis['analysis_id'],
        'category': 'Hardware', 'reason': 'Revisto', 'investigation': context(),
        'response_draft': 'A sua solicitação já foi atendida.'})
    assert response.status_code == 422


def test_unknown_analysis_is_explicit(client):
    assert client.post('/api/plan', json={'analysis_id': 'absent', 'investigation': context()}).status_code == 404
