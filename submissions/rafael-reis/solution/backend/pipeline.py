"""Inferência e consulta dos artefatos locais, sem respostas simuladas."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from statistics import mean, median, pstdev
import json
import hashlib
import os
import re
import sqlite3
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path(os.environ.get('SUPPORT_ARTIFACTS_DIR', str(ROOT / 'artifacts' / 'v1'))).expanduser().resolve()
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
POLICY_VERSION = 'experimental-demo-v1'
ROUTES = {
    'Hardware': 'Suporte de hardware', 'HR Support': 'Recursos humanos',
    'Access': 'Gestão de acesso', 'Storage': 'Infraestrutura e armazenamento',
    'Purchase': 'Compras', 'Administrative rights': 'Gestão de privilégios',
    'Internal Project': 'Equipe do projeto', 'Miscellaneous': 'Triagem geral',
}


class Unavailable(Exception):
    """Uma capacidade depende de artefato inexistente ou incompatível."""


def sanitize(text: str | None) -> str:
    text = str(text or '')
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email]', text)
    text = re.sub(r'(?<!\w)(?:\+?\d[\d ().-]{8,}\d)(?!\w)', '[telefone/identificador]', text)
    return text


def read_json(path: Path):
    if not path.exists():
        raise Unavailable(f'Artefato ainda indisponível: {path.name}. Execute a preparação correspondente.')
    return json.loads(path.read_text())


def catalog_ready(path: Path):
    """Confere as tabelas e contagens que atendem as consultas históricas."""
    if not path.exists():
        return False
    try:
        with sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True) as db:
            db.execute('''SELECT ticket_id, dataset_id, source, text, subject, category, channel, priority,
                                 status, product, csat, resolution FROM catalog_tickets LIMIT 1''').fetchone()
            db.execute('''SELECT ticket_id, predicted_category, confidence, model_version, inference_mode
                          FROM catalog_predictions LIMIT 1''').fetchone()
            metadata = dict(db.execute('SELECT key, value FROM catalog_metadata'))
            records = db.execute('SELECT COUNT(*) FROM catalog_tickets').fetchone()[0]
            predictions = db.execute('SELECT COUNT(*) FROM catalog_predictions').fetchone()[0]
    except sqlite3.Error:
        return False
    return (records > 0 and predictions > 0 and metadata.get('records') == str(records)
            and metadata.get('prediction_records') == str(predictions))


def read_catalog(path: Path):
    if not path.exists():
        raise Unavailable('Catálogo SQLite ainda indisponível. Execute scripts/prepare_data.py.')
    try:
        with sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            rows = [dict(row) for row in db.execute('''
                SELECT ticket_id, dataset_id, source, text, subject, category, channel, priority, status, product, csat, resolution
                FROM catalog_tickets ORDER BY row_order
            ''')]
            metadata = dict(db.execute('SELECT key, value FROM catalog_metadata'))
    except sqlite3.Error as exc:
        raise Unavailable('Catálogo SQLite incompatível; execute scripts/prepare_data.py.') from exc
    if not rows or metadata.get('records') != str(len(rows)):
        raise Unavailable('Catálogo SQLite incompleto; execute scripts/prepare_data.py.')
    return rows


def read_predictions(path: Path):
    try:
        with sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            rows = [dict(row) for row in db.execute('''
                SELECT ticket_id, predicted_category, confidence, model_version, inference_mode FROM catalog_predictions
            ''')]
            metadata = dict(db.execute('SELECT key, value FROM catalog_metadata'))
    except sqlite3.Error as exc:
        raise Unavailable('Predições históricas SQLite indisponíveis; execute scripts/train.py.') from exc
    if metadata.get('prediction_records') != str(len(rows)):
        raise Unavailable('Predições históricas SQLite incompletas; execute scripts/train.py.')
    return {row.pop('ticket_id'): row for row in rows}


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo = int(pos)
    return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (pos - lo)


class Pipeline:
    def __init__(self, artifacts=ARTIFACTS):
        self.artifacts = Path(artifacts)
        self._catalog = None
        self._spaces = {}
        self._classifier = None
        self._predictions = None
        self._encoders = {}
        self.lock = threading.RLock()

    @property
    def catalog(self):
        with self.lock:
            if self._catalog is None:
                rows = read_catalog(self.artifacts / 'catalog.sqlite3')
                self._catalog = {r['ticket_id']: dict(r, source='historical') for r in rows}
            return self._catalog

    def ticket(self, ticket_id):
        if ticket_id not in self.catalog:
            raise KeyError('Ticket não encontrado.')
        return self.catalog[ticket_id]

    def list_tickets(self, dataset_id='ds1', q='', cluster_id=None, space_id=None, **filters):
        rows = [r for r in self.catalog.values() if r['dataset_id'] == dataset_id]
        for field in ('channel', 'priority', 'category', 'status', 'product'):
            if filters.get(field):
                rows = [r for r in rows if r.get(field) == filters[field]]
        if filters.get('csat_presence') == 'present':
            rows = [r for r in rows if r.get('csat') is not None]
        elif filters.get('csat_presence') == 'missing':
            rows = [r for r in rows if r.get('csat') is None]
        if filters.get('csat_score') is not None:
            score = float(filters['csat_score'])
            rows = [r for r in rows if r.get('csat') is not None and float(r['csat']) == score]
        if q:
            query = q.casefold()
            rows = [r for r in rows if query in (r.get('text', '') + ' ' + r['ticket_id']).casefold()]
        if cluster_id:
            space = self.space(space_id or f'{dataset_id}-semantic-v1')
            label = self.cluster_label(cluster_id, space['space_id'])
            valid = {space['ids'][i] for i, c in enumerate(space['labels']) if int(c) == label}
            rows = [r for r in rows if r['ticket_id'] in valid]
        return rows

    def diagnosis(self, dimension='channel', secondary=None, group_by=None, **filters):
        rows = self.list_tickets(dataset_id='ds1', **filters)
        cols = ('channel', 'priority', 'category', 'status', 'product')
        def stats(sample):
            values = [float(r['csat']) for r in sample if r.get('csat') is not None]
            return {'count': len(sample), 'csat_count': len(values),
                    'csat_coverage': len(values) / len(sample) if sample else None,
                    'csat_mean': mean(values) if values else None,
                    'csat_median': median(values) if values else None,
                    'csat_p75': percentile(values, .75), 'csat_p90': percentile(values, .90),
                    'csat_p95': percentile(values, .95),
                    'csat_std': pstdev(values) if values else None}
        def groups(dim, second=None, dimensions=None):
            dimensions = dimensions or ([dim, second] if second else [dim])
            grouped = {}
            for row in rows:
                key = tuple(str(row.get(d) or 'Não informado') for d in dimensions)
                grouped.setdefault(key, []).append(row)
            return [dict(label=' × '.join(k), dimensions=dict(zip(dimensions, k)), primary=k[0],
                         secondary=k[1] if len(k) > 1 else None, **stats(v))
                    for k, v in sorted(grouped.items(), key=lambda item: -len(item[1]))]
        result = read_json(self.artifacts / 'diagnosis.json')
        values = [float(r['csat']) for r in rows if r.get('csat') is not None]
        result.update(total=len(rows), source='historical', dataset_id='ds1',
                      counts={c: dict(Counter(str(r.get(c) or 'Não informado') for r in rows)) for c in cols},
                      groups=groups(dimension, dimensions=group_by), cross_table=groups(dimension, secondary) if secondary else [],
                      group_by=group_by or [dimension],
                      crossings={','.join(dims): groups(dims[0], dimensions=dims) for dims in
                                 [['channel','priority'],['channel','category'],['priority','category'],
                                  ['channel','priority','category'],['product','category'],['status','channel']]},
                      applied_filters={k: v for k, v in filters.items() if v})
        result['csat'] = {'count': len(values), 'coverage': len(values) / len(rows) if rows else None,
                          'mean': mean(values) if values else None, 'median': median(values) if values else None,
                          'positive_count': sum(v >= 4 for v in values),
                          'positive_rate': sum(v >= 4 for v in values) / len(values) if values else None,
                          'distribution': {str(score): sum(v == score for v in values) for score in range(1, 6)},
                          'positive_definition': 'CSAT 4 ou 5 entre notas presentes'}
        result['temporal'] = dict(result.get('temporal', {}), frt_available=False, ttr_available=False,
                                  quality_scope='full_dataset',
                                  reason='Timestamps sem data de abertura; duração indisponível.')
        return result

    def model_metrics(self):
        return read_json(self.artifacts / 'model_metrics.json')

    def review_threshold(self):
        return float(self.model_metrics()['policy']['review_threshold'])

    def classify(self, text):
        with self.lock:
            if self._classifier is None:
                import joblib
                path = self.artifacts / 'classifier.joblib'
                if not path.exists():
                    raise Unavailable('Classificador ainda não preparado.')
                self._classifier = joblib.load(path)
            bundle = self._classifier
            estimator = bundle['pipeline']
            probabilities = estimator.predict_proba([text])[0]
            classes = bundle.get('classes', getattr(estimator, 'classes_', []))
            idx = int(probabilities.argmax())
            return {'predicted_category': str(classes[idx]), 'confidence': float(probabilities[idx]),
                    'model_version': bundle.get('model_version', 'classifier-v1'),
                    'confidence_method': bundle.get('confidence_method', 'predict_proba_uncalibrated')}

    def space(self, space_id):
        if space_id not in ('ds1-semantic-v1', 'ds2-semantic-v1'):
            raise KeyError('Espaço semântico inexistente ou versão incompatível.')
        with self.lock:
            if space_id not in self._spaces:
                import numpy as np
                import faiss
                faiss.omp_set_num_threads(1)
                dataset_id = space_id.split('-')[0]
                folder = self.artifacts / dataset_id
                manifest = read_json(folder / 'semantic.json')
                required = ['embeddings.npy', 'coordinates.npy', 'clusters.npy', 'map_ids.json', 'index.faiss']
                if any(not (folder / p).exists() for p in required):
                    raise Unavailable(f'Espaço {space_id} ainda está sendo preparado.')
                ids = read_json(folder / 'map_ids.json')
                for filename, expected in manifest.get('checksums', {}).items():
                    artifact = folder / filename
                    if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest() != expected:
                        raise Unavailable(f'Checksum incompatível no espaço {space_id}: {filename}.')
                space = dict(space_id=space_id, dataset_id=dataset_id, manifest=manifest,
                    ids=ids, positions={tid: i for i, tid in enumerate(ids)},
                    vectors=np.load(folder / 'embeddings.npy', mmap_mode='r'),
                    coords=np.load(folder / 'coordinates.npy', mmap_mode='r'),
                    labels=np.load(folder / 'clusters.npy', mmap_mode='r'),
                    index=faiss.read_index(str(folder / 'index.faiss')), folder=folder)
                if (manifest.get('space_id') != space_id or manifest.get('dataset_id') != dataset_id or
                    len(set(ids)) != len(ids) or len(ids) != manifest.get('count') or
                    space['vectors'].shape != (len(ids), manifest.get('dimension')) or
                    space['coords'].shape != (len(ids), 2) or space['labels'].shape != (len(ids),) or
                    space['index'].ntotal != len(ids) or space['index'].d != manifest.get('dimension') or
                    any(tid not in self.catalog or self.catalog[tid]['dataset_id'] != dataset_id for tid in ids)):
                    raise Unavailable(f'Artefatos incompatíveis em {space_id}; reconstrua a versão completa.')
                if not np.isfinite(space['vectors']).all() or not np.isfinite(space['coords']).all():
                    raise Unavailable('Artefatos contêm valores não finitos.')
                import joblib
                space['projector'] = joblib.load(folder / 'projector.joblib') if (folder / 'projector.joblib').exists() else None
                space['clusterer'] = joblib.load(folder / 'clusterer.joblib') if (folder / 'clusterer.joblib').exists() else None
                space['neighbors'] = read_json(folder / 'neighbors.json') if (folder / 'neighbors.json').exists() else None
                self._spaces[space_id] = space
            return self._spaces[space_id]

    def embed(self, text, space):
        import numpy as np
        with self.lock:
            manifest = space['manifest']
            name = os.environ.get('SUPPORT_ENCODER_PATH') or manifest.get('encoder_name') or manifest.get('encoder', {}).get('name')
            if not name:
                raise Unavailable('Nome do encoder ausente no manifesto.')
            if name not in self._encoders:
                import torch
                from sentence_transformers import SentenceTransformer
                torch.set_num_threads(1)
                kwargs = {'local_files_only': True, 'device': 'cpu'}
                revision = manifest.get('revision') or manifest.get('encoder_revision')
                if revision and not Path(name).exists():
                    kwargs['revision'] = revision
                try:
                    self._encoders[name] = SentenceTransformer(name, **kwargs)
                except Exception as exc:
                    raise Unavailable('Encoder local indisponível; execute a preparação semântica.') from exc
            vector = self._encoders[name].encode([text], normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(vector, dtype='float32')

    @staticmethod
    def cluster_label(cluster_id, space_id):
        prefix = f'{space_id}:cluster:'
        if not str(cluster_id).startswith(prefix):
            raise ValueError('Cluster incompatível com o espaço selecionado.')
        try:
            return int(str(cluster_id)[len(prefix):])
        except ValueError as exc:
            raise ValueError('Identificador de cluster inválido.') from exc

    def neighbors(self, vector, space, exclude=None, limit=8):
        scores, indices = space['index'].search(vector, min(len(space['ids']), limit + 1))
        result = []
        for score, i in zip(scores[0], indices[0]):
            if i < 0:
                continue
            tid = space['ids'][int(i)]
            if tid == exclude:
                continue
            label = int(space['labels'][int(i)])
            row = self.ticket(tid)
            result.append(dict(row, similarity=float(score),
                               cluster_id=f"{space['space_id']}:cluster:{label}" if label >= 0 else None,
                               coordinates=[float(v) for v in space['coords'][int(i)]]))
        return result[:limit]

    def semantic_result(self, text, space_id, source_ticket_id=None):
        import numpy as np
        space = self.space(space_id)
        if source_ticket_id is not None:
            i = space['positions'][source_ticket_id]
            vector = np.asarray(space['vectors'][i:i + 1], dtype='float32')
            coords = [float(v) for v in space['coords'][i]]
            method = 'precomputed_umap'
        else:
            vector = self.embed(text, space)
            coords, method = None, None
        neighbors = self.neighbors(vector, space, exclude=source_ticket_id)
        if coords is None and space.get('projector') is not None:
            with self.lock:
                coords = space['projector'].transform(vector)[0].tolist()
            method = 'umap_transform'
        if coords is None:
            positives = [n for n in neighbors if n['similarity'] > 0]
            if positives:
                weights = np.array([n['similarity'] for n in positives])
                coords = np.average(np.array([n['coordinates'] for n in positives]), axis=0, weights=weights).tolist()
                method = 'neighbor_weighted_approximation'
            else:
                coords, method = [0., 0.], 'unassociated_origin'
        cluster_label, strength = -1, None
        if source_ticket_id is not None:
            cluster_label = int(space['labels'][space['positions'][source_ticket_id]])
        elif space.get('clusterer') is not None:
            import hdbscan
            bundle = space['clusterer']
            labels, strengths = hdbscan.approximate_predict(bundle['clusterer'], bundle['pca'].transform(vector))
            cluster_label, strength = int(labels[0]), float(strengths[0])
        nearest = {'cluster_id': f'{space_id}:cluster:{cluster_label}', 'method': 'hdbscan_membership' if source_ticket_id else 'hdbscan_approximate_predict',
                   'strength': strength, 'neighbors_evaluated': len(neighbors)} if cluster_label >= 0 else None
        duplicate = next((n for n in neighbors if n['similarity'] >= .90), None)
        return {'space_id': space_id, 'similar_tickets': neighbors, 'nearest_cluster': nearest,
                'coordinates': coords, 'position_method': method,
                'potential_duplicate': {'ticket_id': duplicate['ticket_id'], 'similarity': duplicate['similarity'],
                                        'threshold': .90, 'policy_version': POLICY_VERSION,
                                        'status': 'candidate_unvalidated'} if duplicate else None}

    def analyze(self, text, dataset_id='ds2', source_ticket_id=None):
        start = time.perf_counter()
        text = sanitize(text.strip())
        result = {'text': text, 'dataset_id': dataset_id, 'processing_status': 'complete', 'errors': [],
                  'source_ticket_id': source_ticket_id, 'policy_version': POLICY_VERSION,
                  'inference_mode': 'precomputed' if source_ticket_id else 'online'}
        if dataset_id == 'ds2':
            if source_ticket_id:
                if self._predictions is None:
                    self._predictions = read_predictions(self.artifacts / 'catalog.sqlite3')
                prediction = self._predictions.get(source_ticket_id)
                if prediction is None:
                    raise Unavailable('Predição histórica não encontrada no artefato.')
                result.update(prediction)
                result.setdefault('model_version', self.model_metrics().get('model_version', 'classifier-v1'))
                result.setdefault('confidence_method', self.model_metrics().get('confidence_method', 'predict_proba_uncalibrated'))
            else:
                result.update(self.classify(text))
        else:
            result.update(predicted_category=None, confidence=None, model_version=None,
                          classification_reason='Classificador DS2 não validado para este corpus.')
        try:
            result.update(self.semantic_result(text, f'{dataset_id}-semantic-v1', source_ticket_id))
        except Unavailable as exc:
            result.update(processing_status='partial', similar_tickets=[], nearest_cluster=None,
                          potential_duplicate=None, coordinates=None, position_method=None,
                          space_id=f'{dataset_id}-semantic-v1')
            result['errors'].append(str(exc))
        sensitive = bool(re.search(r'\b(password|credential|permission|access|senha|acesso|security|breach)\b', text, re.I))
        priority = 'High' if re.search(r'\b(urgent|outage|critical|down|urgente|indisponível)\b', text, re.I) else 'Medium'
        confidence = result.get('confidence')
        threshold = self.review_threshold() if dataset_id == 'ds2' else None
        reasons = []
        if confidence is None or confidence < threshold:
            reasons.append(f'Confiança ausente ou abaixo do limiar experimental ({threshold}).')
        # ponytail: não inferir idioma por heurística; entradas livres não têm validação de domínio/idioma.
        if source_ticket_id is None:
            reasons.append('Entrada livre: idioma e domínio não validados; o benchmark cobre apenas o corpus IT DS2.')
        if sensitive:
            reasons.append('Acesso/credenciais exigem validação humana.')
        if not result.get('similar_tickets') or result['similar_tickets'][0]['similarity'] < .50:
            reasons.append('Evidência semântica ausente ou abaixo do limiar experimental de 0,50.')
        if dataset_id != 'ds2':
            reasons.append('Domínio sem classificação validada.')
        result.update(suggested_priority=priority, suggested_route=ROUTES.get(result.get('predicted_category'), 'Triagem geral'),
                      decision_origin='policy_suggested', human_review_required=bool(reasons), review_reasons=reasons,
                      policy_notice='Política experimental da demonstração; prioridade e rota não são rótulos supervisionados.',
                      suggested_action='Revisar evidências e encaminhamento.' if reasons else 'Confirmar encaminhamento sugerido na demonstração.',
                      review_threshold=threshold,
                      latency_ms=round((time.perf_counter() - start) * 1000, 2))
        return result

    def cluster_summaries(self, space):
        if 'summaries' in space:
            return deepcopy(space['summaries'])
        summaries = []
        for label, count in Counter(int(x) for x in space['labels']).most_common():
            indices = [i for i, x in enumerate(space['labels']) if int(x) == label]
            cats = Counter(self.ticket(space['ids'][i]).get('category') or 'Não informado' for i in indices)
            coords = space['coords'][indices].mean(axis=0)
            summaries.append({'id': f"{space['space_id']}:cluster:{label}",
                              'cluster_id': f"{space['space_id']}:cluster:{label}",
                              'label': 'Sem cluster estável (ruído)' if label < 0 else f'{cats.most_common(1)[0][0]} · grupo {label}', 'count': count,
                              'x': float(coords[0]), 'y': float(coords[1]), 'category': cats.most_common(1)[0][0],
                              'categories': dict(cats), 'size': min(28, 5 + count ** .5 / 3),
                              'source': 'historical', 'type': 'cluster', 'is_noise': label < 0})
        space['summaries'] = summaries
        return deepcopy(summaries)

    def graph(self, space_id, level='overview', cluster_id=None, ticket_id=None, overlay=None, limit=200, highlight_ids=None):
        import numpy as np
        space = self.space(space_id)
        summaries = self.cluster_summaries(space)
        overlay = [r for r in (overlay or []) if r.get('space_id') == space_id]
        focused = next((r for r in overlay if r['ticket_id'] == ticket_id), None)
        if level == 'overview' and not cluster_id and not ticket_id:
            for group in summaries:
                members = [r for r in overlay if (r.get('nearest_cluster') or {}).get('cluster_id') == group['cluster_id']]
                group['session_count'] = len(members)
                group['session_sources'] = dict(Counter(r['source'] for r in members))
                group['historical_count'] = group['count']
            # Relações entre grupos usam os centroides dos embeddings reais;
            # a linha é uma pista agregada e mantém o score original explícito.
            overview_edges = []
            clustered = [(group, int(group.get('cluster_id', '').rsplit(':', 1)[-1])) for group in summaries
                         if int(group.get('cluster_id', '').rsplit(':', 1)[-1]) >= 0]
            centroids = {}
            for group, label in clustered:
                members = [i for i, value in enumerate(space['labels']) if int(value) == label]
                vector = np.asarray(space['vectors'][members], dtype='float32').mean(axis=0)
                norm = float(np.linalg.norm(vector))
                if norm:
                    centroids[group['cluster_id']] = vector / norm
            for source, source_vector in centroids.items():
                candidates = []
                for target, target_vector in centroids.items():
                    if source >= target:
                        continue
                    score = float(np.dot(source_vector, target_vector))
                    if score >= .40:
                        candidates.append((score, target))
                for score, target in sorted(candidates, reverse=True)[:4]:
                    overview_edges.append({'id': f'{source}|{target}', 'source': source, 'target': target,
                                           'weight': score, 'type': 'aggregate',
                                           'method': 'centroid_cosine'})
            nodes = summaries[:100]
            return {'space_id': space_id, 'dataset_id': space['dataset_id'], 'level': 'overview',
                    'nodes': nodes, 'edges': overview_edges[:400], 'clusters': summaries[:100], 'total': len(summaries),
                    'displayed': len(nodes), 'truncated': len(summaries) > 100,
                    'ticket_count': len(space['ids']), 'session_ticket_count': len(overlay),
                    'noise_count': sum(int(x) < 0 for x in space['labels'])}
        indices = list(range(len(space['ids'])))
        if cluster_id:
            label = self.cluster_label(cluster_id, space_id)
            indices = [i for i in indices if int(space['labels'][i]) == label]
        if ticket_id:
            if focused:
                selected = [n['ticket_id'] for n in focused.get('similar_tickets', [])]
                indices = [space['positions'][tid] for tid in selected if tid in space['positions']]
            elif ticket_id in space['positions']:
                i = space['positions'][ticket_id]
                nearest = self.neighbors(np.asarray(space['vectors'][i:i + 1], dtype='float32'), space, exclude=ticket_id, limit=min(30, limit - 1))
                indices = [i] + [space['positions'][n['ticket_id']] for n in nearest]
            else:
                raise KeyError('Ticket não pertence ao espaço ou à sessão selecionada.')
        total = len(indices)
        relevant = [r for r in overlay if not cluster_id or (r.get('nearest_cluster') or {}).get('cluster_id') == cluster_id]
        if focused:
            relevant = [focused]
        if highlight_ids:
            missing = set(highlight_ids) - {r['ticket_id'] for r in relevant}
            if missing:
                raise KeyError('Evidência do alerta não encontrada na sessão/espaço selecionados.')
            selected = [r for r in relevant if r['ticket_id'] in highlight_ids]
            rest = [r for r in relevant if r['ticket_id'] not in highlight_ids]
            relevant = (selected + rest[-50:])[:limit]
        else:
            relevant = relevant[-min(50, limit):]
        indices = indices[:max(0, limit - len(relevant))]
        nodes, edges = [], []
        for i in indices:
            tid = space['ids'][i]
            row = self.ticket(tid)
            label = int(space['labels'][i])
            nodes.append({'id': tid, 'ticket_id': tid, 'label': row.get('subject') or row.get('text', '')[:65],
                          'text': row.get('text'), 'x': float(space['coords'][i][0]), 'y': float(space['coords'][i][1]),
                          'size': 5, 'type': 'ticket', 'source': 'historical', 'category': row.get('category'),
                          'priority': row.get('priority'), 'csat': row.get('csat'),
                          'cluster_id': f'{space_id}:cluster:{label}' if label >= 0 else None})
        visible = {n['id'] for n in nodes}
        if indices:
            vectors = np.asarray(space['vectors'][indices], dtype='float32')
            scores, neighbors = space['index'].search(vectors, min(7, len(space['ids'])))
            seen = set()
            for row_idx, i in enumerate(indices):
                tid = space['ids'][i]
                for score, j in zip(scores[row_idx], neighbors[row_idx]):
                    other = space['ids'][int(j)] if j >= 0 else None
                    if other in visible and other != tid and score >= .40:
                        pair = tuple(sorted((tid, other)))
                        if pair not in seen:
                            edges.append({'id': '|'.join(pair), 'source': pair[0], 'target': pair[1], 'weight': float(score)})
                            edges[-1].update(type='knn', method='faiss_inner_product')
                            seen.add(pair)
        for row in relevant:
            coords = row.get('coordinates')
            if coords is None:
                continue
            nodes.append({'id': row['ticket_id'], 'ticket_id': row['ticket_id'], 'label': row['text'][:65],
                          'x': float(coords[0]), 'y': float(coords[1]), 'size': 8, 'type': 'ticket',
                          'category': row.get('predicted_category'), 'confidence': row.get('confidence'),
                          'human_review_required': row.get('human_review_required'),
                          'potential_duplicate': row.get('potential_duplicate'),
                          'review_threshold': row.get('review_threshold'),
                          'source': row['source'], 'cluster_id': (row.get('nearest_cluster') or {}).get('cluster_id'),
                          'highlighted': row['ticket_id'] in (highlight_ids or []),
                          'position_method': row.get('position_method')})
            for n in row.get('similar_tickets', []):
                if n['ticket_id'] in visible:
                    edges.append({'id': row['ticket_id'] + '|' + n['ticket_id'], 'source': row['ticket_id'],
                                  'target': n['ticket_id'], 'weight': n['similarity'],
                                  'type': 'session_knn', 'method': 'stored_similarity'})
        return {'space_id': space_id, 'dataset_id': space['dataset_id'], 'level': 'tickets', 'nodes': nodes,
                'edges': edges[:1500], 'clusters': summaries[:100], 'total': total + len(relevant),
                'displayed': len(nodes), 'truncated': total > len(indices),
                'highlighted_ticket_ids': highlight_ids or [],
                'position_notice': 'Posição 2D aproximada; scores provêm dos embeddings originais.'}

    def replay_ids(self, dataset_id, size, scenario):
        import random
        space = self.space(f'{dataset_id}-semantic-v1')
        ids = list(space['ids'])
        if scenario == 'incident':
            counts = Counter(int(x) for x in space['labels'] if int(x) >= 0)
            if not counts:
                raise Unavailable('Nenhum cluster mensurado disponível para o cenário de concentração.')
            label = counts.most_common(1)[0][0]
            ids = [tid for i, tid in enumerate(ids) if int(space['labels'][i]) == label]
        random.Random(42).shuffle(ids)
        return ids[:size]

    def copilot(self, ticket):
        if ticket['dataset_id'] != 'ds1':
            return {'status': 'insufficient_evidence', 'text': '', 'sources': [], 'mode': 'extractive',
                    'limitations': ['Este corpus não possui resoluções históricas. Não existe join com DS1.'],
                    'human_review_required': True}
        semantic = self.semantic_result(ticket['text'], 'ds1-semantic-v1',
                                        ticket['ticket_id'] if ticket['ticket_id'].startswith('ds1:') else None)
        sources = [n for n in semantic['similar_tickets'] if n.get('resolution') and n['similarity'] >= .50][:3]
        limitations = ['Resoluções do DS1 são genéricas/templateadas; não comprovam solução para o caso atual.',
                       'Rascunho extrativo local. Exige revisão humana e não é enviado ao cliente.']
        text = '\n\n'.join(f"Referência [{s['ticket_id']}]: {sanitize(s['resolution'])}" for s in sources)
        return {'status': 'ready' if sources else 'insufficient_evidence', 'text': text, 'sources': sources,
                'mode': 'extractive', 'limitations': limitations, 'human_review_required': True}
