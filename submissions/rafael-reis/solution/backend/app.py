"""API local e aplicação estática: .venv/bin/python -m uvicorn backend.app:app."""
from __future__ import annotations

from collections import Counter
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse
import hashlib
import json
import logging
import os
import threading
import time

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .pipeline import ARTIFACTS, POLICY_VERSION, ROOT, Pipeline, Unavailable, catalog_ready, sanitize
from .sessions import Store

logger = logging.getLogger(__name__)
DIMENSIONS = ('channel', 'priority', 'category', 'status', 'product')
Dataset = Literal['ds1', 'ds2']


class Body(BaseModel):
    model_config = ConfigDict(extra='forbid')
    request_id: str | None = Field(default=None, min_length=1, max_length=128)


class Analyze(Body):
    text: str = Field(min_length=1, max_length=10000)
    dataset_id: Dataset = 'ds2'
    space_id: str | None = Field(default=None, max_length=100)
    session_id: str | None = Field(default=None, max_length=100)
    add_to_live_session: bool = False

    @field_validator('text')
    @classmethod
    def text_required(cls, value):
        if not value.strip():
            raise ValueError('Informe o texto do ticket.')
        return value.strip()


class SessionCreate(Body):
    dataset_id: Dataset = 'ds2'
    size: int = Field(default=50, ge=1, le=500)
    scenario: Literal['mixed', 'incident'] = 'mixed'
    speed: Literal[1, 2, 5, 10] = 1


class Control(Body):
    action: Literal['play', 'pause', 'speed', 'reset']
    speed: Literal[1, 2, 5, 10] | None = None


class CopilotRequest(Body):
    ticket_id: str = Field(min_length=1, max_length=200)
    session_id: str | None = Field(default=None, max_length=100)


class FeedbackRequest(Body):
    suggestion_id: str = Field(min_length=1, max_length=100)
    decision: Literal['accept', 'edit', 'reject']
    text: str | None = Field(default=None, max_length=20000)


def create_app(artifacts=ARTIFACTS, database=None, start_worker=True, allowed_origins=None):
    pipeline = Pipeline(artifacts)
    runtime_database = Path(os.environ.get('SUPPORT_RUNTIME_DB', str(ROOT / 'runtime' / 'support.sqlite3'))).expanduser()
    store = Store(database or runtime_database)
    stop = threading.Event()
    mutation_lock = threading.RLock()

    def replay_worker():
        due = {}
        while not stop.wait(.1):
            for sid in store.playing():
                if stop.is_set():
                    return
                try:
                    session = store.session(sid)
                    if time.monotonic() < due.get(sid, 0):
                        continue
                    config, i = session['config'], session['next_index']
                    if i >= len(config['ticket_ids']):
                        continue
                    source_id = config['ticket_ids'][i]
                    ticket = pipeline.ticket(source_id)
                    result = pipeline.analyze(ticket['text'], config['dataset_id'], source_id)
                    store.save_ticket(result, sid, 'simulation', replay_index=i)
                    due[sid] = time.monotonic() + 1 / config['speed']
                except Exception:
                    logger.exception('Falha no replay da sessão %s', sid)
                    store.set_error(sid, 'Processamento indisponível; consulte a saúde dos artefatos e retome a sessão.')

    @asynccontextmanager
    async def lifespan(_app):
        worker = threading.Thread(target=replay_worker, name='support-replay', daemon=True) if start_worker else None
        if worker:
            worker.start()
        yield
        stop.set()
        if worker:
            worker.join(timeout=2)

    app = FastAPI(title='Support Intelligence', version='0.1.0', lifespan=lifespan)
    app.state.pipeline, app.state.store = pipeline, store
    origin_values = allowed_origins if allowed_origins is not None else os.environ.get('SUPPORT_ALLOWED_ORIGINS', '').split(',')
    if isinstance(origin_values, str):
        origin_values = origin_values.split(',')
    allowed_origins = tuple(clean for origin in origin_values if (clean := str(origin).strip().rstrip('/'))
                            and urlparse(clean).scheme in ('http', 'https') and urlparse(clean).netloc)
    if allowed_origins:
        app.add_middleware(CORSMiddleware, allow_origins=list(allowed_origins), allow_credentials=False,
                           allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

    @app.middleware('http')
    async def local_origin(request: Request, call_next):
        host = request.url.hostname
        local_host = host in ('localhost', '127.0.0.1', '::1', 'testserver')
        if not local_host and not allowed_origins:
            return JSONResponse({'detail': 'Aplicação restrita ao ambiente local.'}, status_code=403)
        origin = request.headers.get('origin')
        trusted_cross_origin = origin and origin.rstrip('/') in allowed_origins
        if origin:
            parsed = urlparse(origin)
            same_origin = parsed.netloc == request.url.netloc and parsed.scheme == request.url.scheme
            if not same_origin and not trusted_cross_origin:
                return JSONResponse({'detail': 'Origem não autorizada.'}, status_code=403)
        if request.headers.get('sec-fetch-site') == 'cross-site' and not trusted_cross_origin:
            return JSONResponse({'detail': 'Requisição entre sites não autorizada.'}, status_code=403)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Cache-Control'] = 'no-store' if request.url.path.startswith('/api/') else 'no-cache'
        return response

    @app.exception_handler(Unavailable)
    async def unavailable(_request, exc):
        return JSONResponse({'detail': str(exc), 'code': 'artifact_unavailable'}, status_code=503)

    @app.exception_handler(KeyError)
    async def not_found(_request, exc):
        return JSONResponse({'detail': str(exc.args[0]), 'code': 'not_found'}, status_code=404)

    @app.exception_handler(ValueError)
    async def invalid(_request, exc):
        return JSONResponse({'detail': str(exc), 'code': 'invalid_context'}, status_code=422)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request, exc):
        return JSONResponse({'detail': [{'loc': list(e['loc']), 'msg': e['msg'], 'type': e['type']}
                                        for e in exc.errors()], 'code': 'invalid_input'}, status_code=422)

    def idempotent(scope, body, operation):
        fingerprint = hashlib.sha256(json.dumps(body.model_dump(exclude={'request_id'}), sort_keys=True).encode()).hexdigest()
        key = f'{scope}:{body.request_id}' if body.request_id else None
        # ponytail: operações mutáveis serializadas na demo local; locks por sessão só se throughput exigir.
        with mutation_lock:
            previous = store.cached(key, fingerprint)
            if previous is not None:
                return previous
            result = operation()
            store.cache(key, fingerprint, result)
            return result

    def get_ticket(tid):
        return store.ticket(tid) if tid.startswith('session:') else pipeline.ticket(tid)

    @app.get('/api/health')
    def health():
        folder = Path(artifacts)
        catalog_ok = catalog_ready(folder / 'catalog.sqlite3')
        artifact_status = {
            'catalog.sqlite3': catalog_ok,
            'catalog_predictions': catalog_ok,
            **{name: (folder / name).exists() for name in ('diagnosis.json', 'classifier.joblib', 'model_metrics.json')},
        }
        spaces = {ds: (folder / ds / 'semantic.json').exists() for ds in ('ds1', 'ds2')}
        ready = all(artifact_status.values()) and all(spaces.values())
        payload = {'status': 'ok' if ready else 'degraded', 'service': 'support-intelligence',
                   'artifacts': artifact_status, 'spaces': spaces,
                   'llm_required': False, 'mode': 'local_demonstration'}
        return JSONResponse(payload, status_code=200 if ready else 503)

    @app.get('/api/catalog')
    def catalog():
        counts = Counter(t['dataset_id'] for t in pipeline.catalog.values())
        spaces = []
        for ds in ('ds1', 'ds2'):
            path = Path(artifacts) / ds / 'semantic.json'
            if path.exists():
                manifest = json.loads(path.read_text())
                spaces.append({k: manifest.get(k) for k in ('space_id', 'dataset_id', 'count', 'encoder_name', 'clustering', 'limitations')})
        model = pipeline.model_metrics() if (Path(artifacts) / 'model_metrics.json').exists() else None
        return {'datasets': [
                    {'dataset_id': 'ds1', 'label': 'Atendimento ao cliente', 'count': counts['ds1'],
                     'capabilities': ['diagnosis', 'csat', 'resolution_retrieval', 'semantic_search'],
                     'unavailable': ['valid_frt', 'valid_ttr', 'validated_classification']},
                    {'dataset_id': 'ds2', 'label': 'Tickets de TI', 'count': counts['ds2'],
                     'capabilities': ['classification', 'semantic_search'],
                     'unavailable': ['csat', 'resolution', 'channel', 'observed_priority', 'valid_ttr']}],
                'spaces': spaces, 'model': model,
                'limitations': ['DS1 contém placeholders e resoluções genéricas.',
                                'FRT/TTR indisponíveis: timestamps sem início e pares inconsistentes.',
                                'Sem join entre datasets; simulações não são tráfego de produção.']}

    @app.get('/api/diagnosis')
    def diagnosis(dimension: str = 'channel', secondary: str | None = None, group_by: str | None = None,
                  channel: str | None = None, priority: str | None = None, category: str | None = None,
                  status: str | None = None, product: str | None = None,
                  csat_presence: Literal['present', 'missing'] | None = None,
                  csat_score: int | None = Query(None, ge=1, le=5), q: str = Query('', max_length=200)):
        dimensions = group_by.split(',') if group_by else None
        if dimension not in DIMENSIONS or (secondary and secondary not in DIMENSIONS) or (
                dimensions and (len(dimensions) > 3 or any(d not in DIMENSIONS for d in dimensions))):
            raise ValueError('Dimensão de análise inválida.')
        return pipeline.diagnosis(dimension, secondary, dimensions, channel=channel, priority=priority,
                                  category=category, status=status, product=product,
                                  csat_presence=csat_presence, csat_score=csat_score, q=q)

    @app.get('/api/tickets')
    def tickets(dataset_id: Dataset = 'ds1', channel: str | None = None, priority: str | None = None,
                category: str | None = None, status: str | None = None, product: str | None = None,
                csat_presence: Literal['present', 'missing'] | None = None,
                csat_score: int | None = Query(None, ge=1, le=5),
                q: str = Query('', max_length=200), cluster_id: str | None = None, space_id: str | None = None,
                session_id: str | None = None, low_confidence: bool = False,
                limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):
        if session_id:
            rows = [r for r in store.tickets(session_id) if r['dataset_id'] == dataset_id]
            if any((channel, status, product)):
                raise ValueError('Este filtro operacional não está disponível para ocorrências de sessão.')
            if q:
                rows = [r for r in rows if q.casefold() in (r['text'] + ' ' + r['ticket_id']).casefold()]
            if category:
                rows = [r for r in rows if r.get('predicted_category') == category]
            if priority:
                rows = [r for r in rows if r.get('suggested_priority') == priority]
            if space_id:
                rows = [r for r in rows if r.get('space_id') == space_id]
            if cluster_id:
                pipeline.cluster_label(cluster_id, space_id or f'{dataset_id}-semantic-v1')
                rows = [r for r in rows if (r.get('nearest_cluster') or {}).get('cluster_id') == cluster_id]
            if low_confidence:
                rows = [r for r in rows if r.get('confidence') is not None and r['confidence'] < r.get('review_threshold', .75)]
        else:
            rows = pipeline.list_tickets(dataset_id, q, cluster_id, space_id, channel=channel, priority=priority,
                                         category=category, status=status, product=product,
                                         csat_presence=csat_presence, csat_score=csat_score)
        return {'items': rows[offset:offset + limit], 'total': len(rows), 'limit': limit, 'offset': offset}

    @app.get('/api/tickets/{ticket_id}')
    def ticket_detail(ticket_id: str):
        return get_ticket(ticket_id)

    @app.get('/api/models/current')
    def model():
        return pipeline.model_metrics()

    @app.post('/api/tickets/analyze')
    def analyze(body: Analyze):
        def operation():
            if body.space_id and body.space_id != f'{body.dataset_id}-semantic-v1':
                raise ValueError('Espaço incompatível com o corpus selecionado.')
            if body.add_to_live_session:
                if not body.session_id:
                    raise ValueError('Selecione uma sessão para publicar a análise.')
                session = store.session(body.session_id)
                if session['config']['dataset_id'] != body.dataset_id:
                    raise ValueError('Dataset incompatível com a sessão selecionada.')
                sid = body.session_id
            else:
                sid = None
            result = pipeline.analyze(body.text, body.dataset_id)
            if sid is None:
                sid = store.create({'kind': 'sandbox', 'dataset_id': body.dataset_id, 'ticket_ids': [],
                                    'model_version': result.get('model_version'), 'policy_version': result.get('policy_version'),
                                    'space_id': result.get('space_id')})
            return store.save_ticket(result, sid, 'user_created', published=body.add_to_live_session)
        return idempotent('analyze', body, operation)

    @app.get('/api/spaces/{space_id}/graph')
    def graph(space_id: str, level: Literal['overview', 'tickets'] = 'overview', cluster_id: str | None = None,
              ticket_id: str | None = None, session_id: str | None = None, alert_id: str | None = None,
              limit: int = Query(200, ge=1, le=200)):
        overlay = store.tickets(session_id) if session_id else []
        highlights = None
        if alert_id:
            if not session_id:
                raise ValueError('Alerta exige contexto de sessão.')
            alert = store.alert(session_id, alert_id)
            if alert['space_id'] != space_id:
                raise ValueError('Alerta pertence a outro espaço semântico.')
            cluster_id, highlights = alert['cluster_id'], alert['ticket_ids']
            if len(highlights) > limit:
                raise ValueError('Aumente o limite para mostrar toda a evidência do alerta.')
        return pipeline.graph(space_id, level, cluster_id, ticket_id, overlay, limit, highlights)

    @app.post('/api/copilot/suggestions')
    def copilot(body: CopilotRequest):
        def operation():
            ticket = get_ticket(body.ticket_id)
            ticket = dict(ticket, space_id=ticket.get('space_id') or f"{ticket['dataset_id']}-semantic-v1")
            sid = body.session_id or ticket.get('session_id')
            if sid:
                session = store.session(sid)
                if session['config']['dataset_id'] != ticket['dataset_id']:
                    raise ValueError('Sugestão incompatível com o corpus da sessão.')
                if ticket.get('session_id') and ticket['session_id'] != sid:
                    raise ValueError('Ticket pertence a outra sessão.')
            else:
                sid = store.create({'kind': 'sandbox', 'dataset_id': ticket['dataset_id'], 'ticket_ids': [],
                                    'model_version': ticket.get('model_version'), 'policy_version': ticket.get('policy_version'),
                                    'space_id': ticket.get('space_id')})
            result = pipeline.copilot(ticket)
            return store.save_suggestion(sid, ticket, result)
        return idempotent('copilot', body, operation)

    @app.post('/api/feedback')
    def feedback(body: FeedbackRequest):
        if body.decision == 'edit' and not (body.text or '').strip():
            raise ValueError('Uma edição precisa de texto.')
        return idempotent('feedback', body, lambda: store.feedback(body.suggestion_id, body.decision, sanitize(body.text) if body.text else None))

    @app.post('/api/sessions')
    def create_session(body: SessionCreate):
        def operation():
            ids = pipeline.replay_ids(body.dataset_id, body.size, body.scenario)
            if not ids:
                raise Unavailable('Nenhum registro elegível para este cenário.')
            config = dict(body.model_dump(exclude={'request_id'}), kind='replay', ticket_ids=ids, seed=42,
                          model_version=pipeline.model_metrics()['model_version'] if body.dataset_id == 'ds2' else None,
                          policy_version=POLICY_VERSION, space_id=f'{body.dataset_id}-semantic-v1')
            sid = store.create(config)
            return store.snapshot(sid)
        return idempotent('session', body, operation)

    @app.post('/api/sessions/{session_id}/control')
    def control(session_id: str, body: Control):
        return idempotent('control:' + session_id, body,
                          lambda: store.snapshot(store.control(session_id, body.action, body.speed)))

    @app.get('/api/sessions/{session_id}/snapshot')
    def snapshot(session_id: str):
        return store.snapshot(session_id)

    @app.get('/api/sessions/{session_id}/events')
    def events(session_id: str, after_seq: int = Query(0, ge=0), limit: int = Query(200, ge=1, le=1000)):
        return store.events(session_id, after_seq, limit)

    @app.get('/api/sessions/{session_id}/alerts/{alert_id}')
    def alert(session_id: str, alert_id: str):
        return store.alert(session_id, alert_id)

    @app.get('/brand/{filename}')
    @app.get('/api/assets/{filename}')
    def brand_asset(filename: str):
        allowed = {'logo-g4-branca.svg', 'logo-g4-escura.svg', 'logo-g4-valley.svg',
                   'logo-g4-valley-dark-text.svg', 'logo-g4-valley-full.svg'}
        if filename not in allowed:
            raise HTTPException(404, 'Asset não encontrado.')
        return FileResponse(ROOT / filename)

    @app.get('/assets/logo-g4-branca.svg')
    def logo():
        return brand_asset('logo-g4-branca.svg')

    @app.get('/assets/{filename:path}')
    def frontend_asset(filename: str):
        base = (ROOT / 'frontend' / 'dist' / 'assets').resolve()
        target = (base / filename).resolve()
        if not target.is_relative_to(base) or not target.is_file():
            raise HTTPException(404, 'Arquivo não encontrado.')
        return FileResponse(target)

    @app.get('/')
    def frontend():
        index = ROOT / 'frontend' / 'dist' / 'index.html'
        if not index.exists():
            raise HTTPException(503, 'Frontend ainda não compilado.')
        return FileResponse(index)

    return app


app = create_app()
