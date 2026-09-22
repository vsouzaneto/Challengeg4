import json
import sqlite3

import pytest
from test_app import client
import service_flow as flow
import app as module


def start(client, scenario='reset', **kwargs):
    r = client.post('/api/flows', json={'scenario_id': scenario, 'use_ai': False, **kwargs})
    assert r.status_code == 200, r.text
    return r.json()


def action(client, run, name, **kwargs):
    return client.post('/api/flows/'+run['id']+'/actions', json={'action': name, **kwargs})


@pytest.mark.parametrize('scenario,lane', [('reset','self_service'),('failed','prepared'),('leave','prepared'),('incident','human'),('disabled','human'),('unavailable','human')])
def test_demo_routes_consult_context_and_retain_original(client, scenario, lane):
    run = start(client, scenario)
    assert run['plan']['lane'] == lane
    assert len(run['context']['sources']) == 3
    assert run['simulation'] is True
    assert run['original'] == flow.scenario_for(scenario)['text']
    assert run['state'] == 'ready'


def test_customer_completes_once_without_analyst_and_without_token_exposure(client):
    run = start(client)
    assert action(client, run, 'complete_recovery', token='invented').status_code == 409
    requested = action(client, run, 'request_recovery').json()
    assert requested['state'] == 'awaiting_customer'
    assert requested['credential_version'] == 0
    token = requested['demo_token']
    assert action(client, run, 'request_recovery').status_code == 409
    assert action(client, run, 'complete_recovery', token='wrong').status_code == 409
    complete = action(client, run, 'complete_recovery', token=token)
    assert complete.status_code == 200
    assert complete.json()['state'] == 'resolved_demo'
    assert complete.json()['credential_version'] == 1
    assert all('atendente' not in e['actor'] for e in complete.json()['events'])
    assert action(client, run, 'complete_recovery', token=token).status_code == 409
    saved = client.get('/api/flows/'+run['id'])
    assert token not in saved.text and 'token_hash' not in saved.text
    assert saved.json()['credential_version'] == 1


def test_expiry_and_context_change_prevent_completion(client, monkeypatch):
    run = start(client)
    token = action(client, run, 'request_recovery').json()['demo_token']
    with sqlite3.connect(module.DB_PATH) as db:
        db.execute('UPDATE service_runs SET expires_at=0 WHERE id=?',(run['id'],))
    assert action(client,run,'complete_recovery',token=token).status_code == 409
    assert client.get('/api/flows/'+run['id']).json()['credential_version'] == 0
    another = start(client)
    token2 = action(client,another,'request_recovery').json()['demo_token']
    real = flow.connect_context
    monkeypatch.setattr(flow,'connect_context',lambda scenario:{**real(scenario),'active':False})
    assert action(client,another,'complete_recovery',token=token2).status_code == 409


def test_token_is_bound_to_run(client):
    a, b = start(client), start(client)
    token = action(client,a,'request_recovery').json()['demo_token']
    action(client,b,'request_recovery')
    assert action(client,b,'complete_recovery',token=token).status_code == 409


@pytest.mark.parametrize('scenario',['failed','leave','incident','disabled','unavailable'])
def test_no_action_bypass_from_non_eligible_lane(client,scenario):
    run = start(client,scenario)
    assert action(client,run,'request_recovery').status_code == 409
    assert action(client,run,'complete_recovery',token='x').status_code == 409


def test_failure_handoff_invalidates_token_and_carries_attempt(client):
    run = start(client)
    token = action(client,run,'request_recovery').json()['demo_token']
    result = action(client,run,'report_failure').json()
    assert result['plan']['lane'] == 'prepared'
    assert 'histórico' in result['events'][-1]['event']
    assert action(client,run,'complete_recovery',token=token).status_code == 409
    assert action(client,run,'report_failure').status_code == 409


def test_reopen_after_simulated_completion(client):
    run = start(client)
    token=action(client,run,'request_recovery').json()['demo_token']
    action(client,run,'complete_recovery',token=token)
    assert action(client,run,'report_failure').json()['plan']['lane']=='prepared'


def test_prepared_reply_uses_system_record_and_persists_edit(client):
    run = start(client,'leave')
    assert run['plan']['draft'] and 'constam lançadas' in run['plan']['draft']
    assert action(client,run,'approve_draft',draft='').status_code==409
    result=action(client,run,'approve_draft',draft='Texto conferido e editado.').json()
    assert result['state']=='approved_demo'
    assert result['approved_draft']=='Texto conferido e editado.'
    assert action(client,run,'approve_draft',draft='Segundo envio').status_code==409


def test_investigation_does_not_claim_resolution(client):
    run=start(client,'incident')
    assert run['plan']['draft'] is None
    result=action(client,run,'acknowledge_handoff').json()
    assert result['state']=='investigating'
    assert 'continuam em aberto' in result['events'][-1]['event']
    assert action(client,run,'approve_draft',draft='Resolvido').status_code==409


def test_model_failure_does_not_open_self_service(client,monkeypatch):
    async def broken(*args,**kwargs): raise RuntimeError('SECRET provider detail')
    monkeypatch.setattr(flow.openrouter_client,'chat',broken)
    run=start(client,use_ai=True)
    assert run['plan']['lane']=='prepared'
    assert run['signals']['failed'] is True
    assert 'SECRET' not in json.dumps(run)


def test_model_cannot_suppress_security_signal(client,monkeypatch):
    async def mistaken(*args,**kwargs):
        return {'content':json.dumps({'intent':'access_recovery','intent_quote':'password reset',
                                     'attempts':[],'risk_quotes':[],'temperature':'unknown',
                                     'temperature_quotes':[],'urgency_quotes':[],'multiple_requests':False}),'model':'test'}
    monkeypatch.setattr(flow.openrouter_client,'chat',mistaken)
    run=start(client,text='password reset please. I can access data for another colleague.',use_ai=True)
    assert run['plan']['lane']=='human'


@pytest.mark.parametrize('body',[
 {'intent':'access_recovery','intent_quote':'invented','attempts':[],'risk_quotes':[],'temperature':'unknown','temperature_quotes':[],'urgency_quotes':[],'multiple_requests':False},
 {'intent':'access_recovery','intent_quote':'','attempts':[],'risk_quotes':[],'temperature':'unknown','temperature_quotes':[],'urgency_quotes':[],'multiple_requests':False},
 {'intent':'other','intent_quote':'','attempts':[''],'risk_quotes':[],'temperature':'unknown','temperature_quotes':[],'urgency_quotes':[],'multiple_requests':False},
 {'intent':'other','intent_quote':'','attempts':[],'risk_quotes':[],'temperature':'unknown','temperature_quotes':[],'urgency_quotes':[],'multiple_requests':False,'command':'reset'},
 {'intent':'other','intent_quote':'','attempts':[],'risk_quotes':[],'temperature':'attention','temperature_quotes':[],'urgency_quotes':[],'multiple_requests':False},
 {'intent':'other','intent_quote':'','attempts':[],'risk_quotes':[],'temperature':'unknown','temperature_quotes':['frustrated'],'urgency_quotes':[],'multiple_requests':False},
])
def test_model_output_requires_supported_schema_and_literal_evidence(body):
    with pytest.raises(ValueError): flow.validate_signals(json.dumps(body),'password reset please')


def test_multiple_requests_are_never_single_procedure(client):
    run=start(client,text='password reset and annual leave balance please')
    assert run['plan']['lane']=='prepared'


def test_concatenated_thread_not_eligible_for_self_service(client):
    run=start(client,'thread')
    assert run['signals']['thread_ambiguous'] is True
    assert run['plan']['lane']=='prepared'


def test_uncertain_attempt_does_not_become_assertion_of_failure(client,monkeypatch):
    async def mistaken(*args,**kwargs):
        return {'content':json.dumps({'intent':'access_recovery','intent_quote':'password reset',
                                     'attempts':['please'],'risk_quotes':[],'temperature':'unknown',
                                     'temperature_quotes':[],'urgency_quotes':[],'multiple_requests':False}),'model':'test'}
    monkeypatch.setattr(flow.openrouter_client,'chat',mistaken)
    run=start(client,text='password reset please thank you',use_ai=True)
    assert run['plan']['lane']=='prepared'
    assert 'não funcionou' not in run['plan']['draft']
    assert 'falha' not in run['plan']['draft']


def test_existing_failure_blocks_reset_even_if_customer_omits_attempt(client):
    run=start(client,'failed',text='Please help me with a password reset.')
    assert run['plan']['lane']=='prepared'
    assert run['plan']['draft']
    assert action(client,run,'request_recovery').status_code==409


def test_temperature_and_urgency_are_cited_signals_not_priority(client):
    run=start(client,text='I am frustrated. I need a password reset urgently today.')
    assert run['signals']['temperature']=='attention'
    assert run['signals']['temperature_quotes']==['frustrated']
    assert run['signals']['urgency_quotes']==['urgently', 'today']
    # Um pedido simples com prazo explícito pode ser mais bem servido pelo autosserviço;
    # o texto não redefine prioridade nem afirma SLA.
    assert run['plan']['lane']=='self_service'


def test_newly_open_failure_prevents_pending_reset_completion(client,monkeypatch):
    run=start(client)
    token=action(client,run,'request_recovery').json()['demo_token']
    real=flow.connect_context
    monkeypatch.setattr(flow,'connect_context',lambda scenario:{**real(scenario),'recovery_issue_open':True})
    assert action(client,run,'complete_recovery',token=token).status_code==409


def test_malformed_input_and_unknown_run(client):
    assert client.post('/api/flows',json={'scenario_id':'missing'}).status_code==422
    assert client.post('/api/flows',json={'scenario_id':'reset','text':' '*20}).status_code==422
    assert client.get('/api/flows/missing').status_code==404
    assert client.post('/api/flows/missing/actions',json={'action':'request_recovery'}).status_code==404
