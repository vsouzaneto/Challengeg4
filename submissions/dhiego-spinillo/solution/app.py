"""Protótipo local sem autenticação: executar somente em 127.0.0.1.

Classificação não executa atendimento, revisão não retreina o modelo. O SQLite
contém texto original e deve permanecer local; a exportação o omite sempre.
"""
import csv
import hashlib
import io
import json
import math
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

import joblib
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, field_validator

from investigation import Investigation, prepare_next_step
from recap import RecapValidationError, generate_recap
from triage_core import LABELS, ROOT, key_from_env, route_suggestion

SOLUTION = Path(__file__).resolve().parent
MODEL_PATH = ROOT / 'artifacts/classifier.joblib'
DB_PATH = ROOT / 'artifacts/runtime/reviews.sqlite3'
SUMMARY_PATH = SOLUTION / 'reports/comparison/summary.json'
EXAMPLES_PATH = SOLUTION / 'reports/comparison/demo-examples.json'
app = FastAPI(title='G4 · Suporte assistido · demonstração local', docs_url=None, redoc_url=None)
app.mount('/static', StaticFiles(directory=str(SOLUTION / 'static'), check_dir=False), name='static')
templates = Jinja2Templates(directory=str(SOLUTION / 'templates'))

# Somente arquivos versionados públicos. Nunca montar ROOT, artifacts ou reports
# integralmente: predições completas, banco e credenciais não são públicos.
PUBLIC_FILES = {
    'reports/' + name: SOLUTION / 'reports' / name for name in (
        'coortes-qualidade.json', 'exploracao-cx.json', 'contexto-e-recap.json',
        'auditoria-datasets.json', 'comparison/summary.json',
        'comparison/training.json', 'comparison/demo-examples.json',
    )
}
PUBLIC_FILES.update({name: SOLUTION / name for name in (
    'REPRODUZIR.md', 'analise-preliminar-cx.md', 'qualidade-por-pergunta.md',
    'contexto-e-recap.md', 'diagnostico-inicial.md',
)})
PUBLIC_FILES.update({'docs/identidade-visual.md': ROOT / 'docs/identidade-visual.md',
                     'process-log/README.md': ROOT / 'process-log/README.md',
                     'visual/assets/g4-logo.svg': SOLUTION / 'visual/assets/g4-logo.svg'})


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    try:
        with connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS analyses (
                analysis_id TEXT PRIMARY KEY, original_text TEXT NOT NULL,
                text_sha256 TEXT NOT NULL, prediction TEXT, score REAL,
                domain_confirmed INTEGER NOT NULL, policy_json TEXT NOT NULL,
                recap_json TEXT, recap_error TEXT, created_at TEXT NOT NULL)''')
            connection.execute('''CREATE TABLE IF NOT EXISTS reviews (
                review_id TEXT PRIMARY KEY, analysis_id TEXT NOT NULL REFERENCES analyses(analysis_id),
                original_category TEXT, category TEXT NOT NULL, reason TEXT NOT NULL,
                created_at TEXT NOT NULL)''')
            connection.execute('''CREATE TABLE IF NOT EXISTS investigations (
                review_id TEXT PRIMARY KEY REFERENCES reviews(review_id),
                context_json TEXT NOT NULL, plan_json TEXT NOT NULL)''')
            yield connection
    finally:
        connection.close()


@lru_cache(maxsize=1)
def get_model():
    # Carregar somente o artefato local produzido pelo script de comparação.
    return joblib.load(MODEL_PATH)


def get_classifier():
    try:
        return get_model()
    except Exception:
        raise HTTPException(503, 'Classificador local indisponível. Reproduza o treinamento.') from None


def evidence():
    try:
        return json.loads(SUMMARY_PATH.read_text())
    except (OSError, ValueError):
        raise HTTPException(503, 'Evidência comparativa indisponível.') from None


def validated_threshold():
    threshold = evidence()['systems']['tfidf_logistic']['validation']['threshold_from_validation']
    if isinstance(threshold, (int, float)) and not isinstance(threshold, bool) and 0 <= threshold <= 1:
        return threshold
    return None


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    text: str = Field(min_length=10, max_length=16000)
    domain_confirmed: bool
    include_recap: bool = False

    @field_validator('text')
    @classmethod
    def meaningful_text(cls, value):
        if len(value.strip()) < 10:
            raise ValueError('Informe pelo menos 10 caracteres de texto.')
        return value


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    analysis_id: str = Field(min_length=1, max_length=100)
    category: str
    reason: str = Field(min_length=3, max_length=1000)
    investigation: Investigation | None = None
    response_draft: str | None = Field(default=None, max_length=3000)

    @field_validator('category')
    @classmethod
    def supported_category(cls, value):
        if value not in LABELS:
            raise ValueError('Categoria desconhecida.')
        return value

    @field_validator('reason')
    @classmethod
    def meaningful_reason(cls, value):
        if len(value.strip()) < 3:
            raise ValueError('Explique a confirmação ou correção em pelo menos 3 caracteres.')
        return value


class PlanRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    analysis_id: str = Field(min_length=1, max_length=100)
    investigation: Investigation


def verified_plan(context, original):
    try:
        return prepare_next_step(context, original)
    except ValueError as error:
        raise HTTPException(422, str(error)) from None


@app.get('/')
def home(request: Request):
    return templates.TemplateResponse(request=request, name='app.html', context={'categories': list(LABELS)})


@app.get('/diagnostico')
def diagnostic():
    return FileResponse(SOLUTION / 'visual/index.html')


@app.get('/api/health')
def health():
    try:
        get_model()
        model_available = True
    except Exception:
        model_available = False
    return {'model_available': model_available, 'recap_available': bool(key_from_env('OPENROUTER_API_KEY'))}


@app.get('/api/evidence')
def api_evidence():
    return evidence()


@app.get('/api/examples')
def examples():
    rows = json.loads(EXAMPLES_PATH.read_text())
    guided = json.loads((SOLUTION / 'reports/revisao-guiada.json').read_text())['cases']
    selected = [{'row': case['row'], 'text': case['original'],
                 'dataset_label': case['classification_archived']['truth'],
                 'source': 'Caso discutido com Dhiego; veio do teste e agora orienta desenvolvimento. Não é uma nova avaliação.'}
                for case in guided]
    return [{**row, 'source': row.get('source', 'Exemplo do treino; não mede desempenho.'),
             'disclaimer': 'Rótulo original do dataset; não é verdade revisada por humano.'}
            for row in selected + rows]


@app.post('/api/analyze')
async def analyze(body: AnalyzeRequest, classifier=Depends(get_classifier)):
    started = time.perf_counter()
    try:
        values = classifier.predict_proba([body.text])[0]
        probabilities = {str(label): float(value) for label, value in zip(classifier.classes_, values)}
        if (set(probabilities) != set(LABELS)
                or any(not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities.values())
                or abs(sum(probabilities.values()) - 1) > .001):
            raise ValueError('Distribuição inválida')
        prediction = max(probabilities, key=probabilities.get)
    except Exception:
        raise HTTPException(503, 'Falha na classificação local. Encaminhe para revisão manual.') from None
    elapsed_ms = (time.perf_counter() - started) * 1000
    score = probabilities[prediction]
    threshold = validated_threshold()
    policy = route_suggestion(prediction, score, threshold, domain_confirmed=body.domain_confirmed)
    policy['requires_human_confirmation'] = True
    recap, recap_error = None, None
    if body.include_recap:
        if not key_from_env('OPENROUTER_API_KEY'):
            recap_error = 'Recap indisponível: OpenRouter não configurado. Classificação local preservada.'
        else:
            try:
                recap = await generate_recap(body.text)
            except RecapValidationError as exc:
                recap_error = str(exc)
            except Exception:
                recap_error = 'Recap indisponível: falha ou resposta incompleta do provedor. Classificação local preservada.'
    analysis_id = str(uuid4())
    created_at = utc_now()
    with database() as db:
        db.execute('INSERT INTO analyses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
            analysis_id, body.text, hashlib.sha256(body.text.encode()).hexdigest(),
            prediction, score, int(body.domain_confirmed), json.dumps(policy, ensure_ascii=False),
            json.dumps(recap, ensure_ascii=False) if recap is not None else None, recap_error, created_at,
        ))
    return {'analysis_id': analysis_id, 'text': body.text, 'prediction': prediction,
            'score': score, 'probabilities': probabilities, 'elapsed_ms': elapsed_ms,
            'model': 'tfidf_logistic', 'threshold': threshold, 'policy': policy,
            'recap': recap, 'recap_error': recap_error, 'created_at': created_at}


@app.post('/api/plan')
def plan(body: PlanRequest):
    with database() as db:
        original = db.execute('SELECT original_text FROM analyses WHERE analysis_id=?', (body.analysis_id,)).fetchone()
        if original is None:
            raise HTTPException(404, 'Análise não encontrada.')
        return verified_plan(body.investigation, original['original_text'])


@app.post('/api/review')
def review(body: ReviewRequest):
    with database() as db:
        original = db.execute('SELECT prediction, original_text FROM analyses WHERE analysis_id=?', (body.analysis_id,)).fetchone()
        if original is None:
            raise HTTPException(404, 'Análise não encontrada.')
        plan_result = verified_plan(body.investigation, original['original_text']) if body.investigation is not None else None
        if body.response_draft is not None and (plan_result is None or plan_result['reply_draft'] is None):
            raise HTTPException(422, 'As conferências registradas ainda não sustentam um rascunho de resposta.')
        result = {'review_id': str(uuid4()), 'analysis_id': body.analysis_id,
                  'original_category': original['prediction'], 'category': body.category,
                  'reason': body.reason, 'created_at': utc_now()}
        db.execute('INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?)', tuple(result.values()))
        if plan_result is not None:
            db.execute('INSERT INTO investigations VALUES (?, ?, ?)', (
                result['review_id'], json.dumps({**body.investigation.model_dump(),
                                                'response_draft': body.response_draft}, ensure_ascii=False),
                json.dumps(plan_result, ensure_ascii=False),
            ))
    return {'ok': True, **result, 'plan': plan_result}


def csv_safe(value):
    text = '' if value is None else str(value)
    # Planilhas podem ignorar espaços/controles antes de interpretar fórmulas.
    stripped = text.lstrip(' \t\r\n\ufeff')
    if stripped.startswith(('=', '+', '-', '@')) or text.startswith(('\t', '\r', '\n')):
        return "'" + text
    return text


@app.get('/api/export')
def export_reviews():
    with database() as db:
        rows = db.execute('''SELECT r.review_id, r.analysis_id, a.text_sha256,
            r.original_category, r.category, r.reason, r.created_at, i.context_json, i.plan_json
            FROM reviews r JOIN analyses a ON r.analysis_id=a.analysis_id
            LEFT JOIN investigations i ON i.review_id=r.review_id
            ORDER BY r.created_at, r.review_id''').fetchall()
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    fields = ['review_id', 'analysis_id', 'text_sha256', 'original_category', 'category', 'reason', 'created_at']
    writer.writerow(fields + ['other_tickets_check', 'system_check', 'internal_notes_check',
                              'system_outcome', 'incident_reported', 'next_step_code', 'rule_version'])
    for row in rows:
        context = json.loads(row['context_json']) if row['context_json'] else {}
        plan_result = json.loads(row['plan_json']) if row['plan_json'] else {}
        # O trecho do relato e o texto original permanecem somente no banco local.
        values = [row[field] for field in fields] + [context.get('checks', {}).get(name, '')
                   for name in ('other_tickets', 'system', 'internal_notes')]
        values += [context.get('system_outcome', ''), context.get('incident_reported', ''),
                   plan_result.get('code', ''), plan_result.get('rule_version', '')]
        writer.writerow([csv_safe(value) for value in values])
    return Response(content='\ufeff' + output.getvalue(), media_type='text/csv; charset=utf-8',
                    headers={'Content-Disposition': 'attachment; filename="revisoes-suporte.csv"',
                             'Cache-Control': 'no-store'})


@app.get('/{public_path:path}')
def public_file(public_path: str):
    file = PUBLIC_FILES.get(public_path)
    if file is None or not file.is_file() or file.is_symlink():
        raise HTTPException(404, 'Arquivo público não encontrado.')
    return FileResponse(file)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
