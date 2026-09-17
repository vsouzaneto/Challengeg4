"""Sessões e auditoria local: SQLite, transações curtas, sem exclusões."""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
import threading
import uuid


def now():
    return datetime.now(timezone.utc).isoformat()


def uid():
    return str(uuid.uuid4())


def ticket_context(ticket):
    ticket = ticket or {}
    source = ticket.get('source') or 'simulation'
    source_ticket_id = ticket.get('source_ticket_id')
    return {
        'ticket_id': ticket.get('ticket_id'), 'source_ticket_id': source_ticket_id, 'source': source,
        'content_origin': ticket.get('content_origin') or (ticket.get('dataset_id') if source == 'historical' or source_ticket_id else source),
        'dataset_id': ticket.get('dataset_id'), 'model_version': ticket.get('model_version'),
        'policy_version': ticket.get('policy_version'), 'space_id': ticket.get('space_id'),
        'inference_mode': ticket.get('inference_mode'), 'simulation_time': ticket.get('simulation_time'),
    }


def session_context(db, sid):
    row = db.execute('SELECT config FROM sessions WHERE id=?', (sid,)).fetchone()
    config = json.loads(row['config']) if row else {}
    source = 'user_created' if config.get('kind') == 'sandbox' else 'simulation'
    return {
        'ticket_id': None, 'source_ticket_id': None, 'source': source,
        'content_origin': config.get('dataset_id') if source == 'simulation' else source,
        'dataset_id': config.get('dataset_id'), 'model_version': config.get('model_version'),
        'policy_version': config.get('policy_version'), 'space_id': config.get('space_id'),
        'inference_mode': None, 'simulation_time': None,
    }


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY, state TEXT NOT NULL, config TEXT NOT NULL,
                    next_index INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, error TEXT);
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY, session_id TEXT NOT NULL, result TEXT NOT NULL,
                    published INTEGER NOT NULL DEFAULT 1);
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, seq INTEGER NOT NULL,
                    data TEXT NOT NULL, UNIQUE(session_id, seq));
                CREATE TABLE IF NOT EXISTS requests (
                    key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS suggestions (
                    id TEXT PRIMARY KEY, session_id TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY, suggestion_id TEXT NOT NULL, session_id TEXT NOT NULL,
                    decision TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY, session_id TEXT NOT NULL, cluster_id TEXT NOT NULL,
                    data TEXT NOT NULL, UNIQUE(session_id, cluster_id));
            ''')
            # Recuperação conservadora: não reiniciar produtor silenciosamente após falha.
            db.execute("UPDATE sessions SET state='PAUSED', error='Servidor reiniciado; retome a sessão para continuar.' WHERE state='PLAYING'")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
        try:
            with db:
                yield db
        finally:
            db.close()

    def cached(self, key, fingerprint):
        if not key:
            return None
        with self.connect() as db:
            row = db.execute('SELECT * FROM requests WHERE key=?', (key,)).fetchone()
        if row:
            if row['fingerprint'] != fingerprint:
                raise ValueError('request_id já utilizado com outro conteúdo.')
            return json.loads(row['result'])
        return None

    def cache(self, key, fingerprint, result):
        if key:
            with self.lock, self.connect() as db:
                db.execute('INSERT INTO requests VALUES (?,?,?)', (key, fingerprint, json.dumps(result)))

    def create(self, config):
        sid = uid()
        with self.lock, self.connect() as db:
            db.execute('INSERT INTO sessions(id,state,config,created_at,updated_at) VALUES(?,?,?,?,?)',
                       (sid, 'STOPPED', json.dumps(config), now(), now()))
            self._event(db, sid, 'SESSION_CREATED', None, {'config': config})
        return sid

    def session(self, sid):
        with self.connect() as db:
            row = db.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
        if not row:
            raise KeyError('Sessão não encontrada.')
        result = dict(row)
        result['session_id'] = result.pop('id')
        result['config'] = json.loads(result['config'])
        return result

    def control(self, sid, action, speed=None):
        with self.lock:
            session = self.session(sid)
            config = session['config']
            state = session['state']
            if action == 'reset':
                with self.connect() as db:
                    db.execute("UPDATE sessions SET state=CASE WHEN state='PLAYING' THEN 'PAUSED' ELSE state END, updated_at=? WHERE id=?", (now(), sid))
                    self._event(db, sid, 'SESSION_RESET_REQUESTED', None, {'preserved': True})
                return self.create(config)
            if action == 'play':
                if config.get('kind') == 'sandbox':
                    raise ValueError('Sessão de análise manual não possui replay.')
                if state == 'COMPLETED':
                    raise ValueError('Sessão concluída. Reset cria uma nova sessão sem apagar esta.')
                state = 'PLAYING'
            elif action == 'pause':
                state = 'PAUSED' if state == 'PLAYING' else state
            elif action == 'speed':
                if speed not in (1, 2, 5, 10):
                    raise ValueError('Velocidade deve ser 1, 2, 5 ou 10.')
                config['speed'] = speed
            else:
                raise ValueError('Comando inválido.')
            with self.connect() as db:
                db.execute('UPDATE sessions SET state=?,config=?,updated_at=?,error=NULL WHERE id=?',
                           (state, json.dumps(config), now(), sid))
                self._event(db, sid, 'SESSION_CONTROLLED', None, {'action': action, 'state': state, 'speed': config.get('speed')})
        return sid

    def playing(self):
        with self.connect() as db:
            return [row['id'] for row in db.execute("SELECT id FROM sessions WHERE state='PLAYING'")]

    def set_error(self, sid, error):
        with self.lock, self.connect() as db:
            db.execute("UPDATE sessions SET state='PAUSED',error=?,updated_at=? WHERE id=?", (error, now(), sid))
            self._event(db, sid, 'PROCESSING_FAILED', None, {'message': error})

    def _event(self, db, sid, event_type, ticket, payload=None):
        seq = db.execute('SELECT COALESCE(MAX(seq),0)+1 FROM events WHERE session_id=?', (sid,)).fetchone()[0]
        event = {'event_id': uid(), 'session_id': sid, 'seq': seq, 'event_type': event_type,
                 'occurred_at': now(), **(ticket_context(ticket) if ticket else session_context(db, sid)),
                 'payload': payload or {}}
        db.execute('INSERT INTO events VALUES(?,?,?,?)', (event['event_id'], sid, seq, json.dumps(event)))
        return event

    def save_ticket(self, result, sid, source, published=True, replay_index=None):
        self.session(sid)
        result = dict(result, ticket_id=f'session:{sid}:{uid()}', session_id=sid, source=source,
                      content_origin=result.get('content_origin') or (result.get('dataset_id') if source == 'simulation' else source))
        if replay_index is not None:
            result['simulation_time'] = float(replay_index + 1)
        with self.lock, self.connect() as db:
            if replay_index is not None:
                current = db.execute('SELECT next_index,state FROM sessions WHERE id=?', (sid,)).fetchone()
                if current['next_index'] != replay_index:
                    raise ValueError('Checkpoint do replay mudou; resultado não pode ser duplicado.')
            db.execute('INSERT INTO tickets VALUES(?,?,?,?)', (result['ticket_id'], sid, json.dumps(result), int(published)))
            self._event(db, sid, 'TICKET_ARRIVED', result, {'published': published})
            if result.get('predicted_category') is not None:
                self._event(db, sid, 'CLASSIFICATION_STARTED', result,
                            {'inference_mode': result.get('inference_mode'), 'model_version': result.get('model_version')})
                self._event(db, sid, 'CLASSIFICATION_COMPLETED', result,
                            {k: result.get(k) for k in ('predicted_category', 'confidence', 'model_version', 'confidence_method')})
            else:
                self._event(db, sid, 'CLASSIFICATION_SKIPPED', result, {'reason': result.get('classification_reason')})
            if result.get('coordinates') is not None:
                self._event(db, sid, 'EMBEDDING_CREATED' if source == 'user_created' else 'EMBEDDING_LOADED', result,
                            {'inference_mode': result['inference_mode']})
                self._event(db, sid, 'NEIGHBORS_FOUND', result,
                            {'neighbors': [{'ticket_id': n['ticket_id'], 'similarity': n['similarity']} for n in result.get('similar_tickets', [])]})
            for event_type, keys in (
                ('DUPLICATE_ANALYSIS', ('potential_duplicate',)),
                ('PRIORITY_ANALYSIS', ('suggested_priority', 'policy_version')),
                ('ROUTING_DECISION', ('suggested_route', 'policy_notice')),
                ('HUMAN_OR_AUTO_DECISION', ('human_review_required', 'review_reasons')),
            ):
                self._event(db, sid, event_type, result, {k: result.get(k) for k in keys})
            if result.get('coordinates') is not None:
                self._event(db, sid, 'GRAPH_NODE_CREATED', result, {'ticket_id': result['ticket_id'], 'coordinates': result['coordinates']})
            self._event(db, sid, 'DASHBOARD_UPDATED', result, {'published': published})
            if replay_index is not None:
                session = db.execute('SELECT config FROM sessions WHERE id=?', (sid,)).fetchone()
                total = len(json.loads(session['config']).get('ticket_ids', []))
                db.execute('UPDATE sessions SET next_index=?,state=CASE WHEN ? >= ? THEN ? ELSE state END,updated_at=? WHERE id=?',
                           (replay_index + 1, replay_index + 1, total, 'COMPLETED', now(), sid))
                if replay_index + 1 >= total:
                    self._event(db, sid, 'SESSION_COMPLETED', None, {'total': total})
            self._detect_alert(db, sid, result)
        return result

    def _detect_alert(self, db, sid, ticket):
        cluster = (ticket.get('nearest_cluster') or {}).get('cluster_id')
        if ticket['source'] != 'simulation' or not cluster:
            return
        current = ticket.get('simulation_time', 0)
        rows = [json.loads(r['result']) for r in db.execute('SELECT result FROM tickets WHERE session_id=? AND published=1', (sid,))]
        members = [r for r in rows if r['source'] == 'simulation' and
                   (r.get('nearest_cluster') or {}).get('cluster_id') == cluster and
                   current - 30 <= r.get('simulation_time', 0) <= current]
        unique = {r.get('source_ticket_id') for r in members}
        if len(unique) < 5:
            return
        similarities = [float(neighbor['similarity'])
                        for member in members
                        for neighbor in member.get('similar_tickets', [])
                        if neighbor.get('cluster_id') == cluster and neighbor.get('similarity') is not None]
        row = db.execute('SELECT id,data FROM alerts WHERE session_id=? AND cluster_id=?', (sid, cluster)).fetchone()
        aid = row['id'] if row else uid()
        data = {'alert_id': aid, 'type': 'possible_emerging_incident', 'title': 'Possível concentração semântica',
                'source': 'simulation', 'session_id': sid, 'cluster_id': cluster, 'space_id': ticket.get('space_id'),
                'dataset_id': ticket['dataset_id'], 'ticket_ids': [r['ticket_id'] for r in members],
                'source_ticket_ids': sorted(unique), 'count': len(members), 'unique_count': len(unique),
                'window_steps': 30, 'threshold': 5, 'simulation_time': current,
                'mean_similarity': round(sum(similarities) / len(similarities), 4) if similarities else None,
                'rule_version': 'incident-demo-v1', 'label': 'CENÁRIO SIMULADO; regra experimental, sem validação estatística.',
                'dominant_category': Counter(r.get('predicted_category') or 'Sem classificação' for r in members).most_common(1)[0][0]}
        if row:
            db.execute('UPDATE alerts SET data=? WHERE id=?', (json.dumps(data), aid))
        else:
            db.execute('INSERT INTO alerts VALUES(?,?,?,?)', (aid, sid, cluster, json.dumps(data)))
        self._event(db, sid, 'ALERT_UPDATED' if row else 'ALERT_CREATED', ticket, data)

    def ticket(self, tid):
        with self.connect() as db:
            row = db.execute('SELECT result FROM tickets WHERE id=?', (tid,)).fetchone()
        if not row:
            raise KeyError('Ticket de sessão não encontrado.')
        return json.loads(row['result'])

    def tickets(self, sid, published_only=False):
        self.session(sid)
        with self.connect() as db:
            rows = db.execute('SELECT result FROM tickets WHERE session_id=?' + (' AND published=1' if published_only else ''), (sid,)).fetchall()
        return [json.loads(r['result']) for r in rows]

    def events(self, sid, after_seq=0, limit=200):
        self.session(sid)
        with self.connect() as db:
            maximum = db.execute('SELECT COALESCE(MAX(seq),0) FROM events WHERE session_id=?', (sid,)).fetchone()[0]
            if after_seq > maximum:
                raise ValueError('Cursor posterior ao log; recarregue o snapshot.')
            rows = db.execute('SELECT data FROM events WHERE session_id=? AND seq>? ORDER BY seq LIMIT ?', (sid, after_seq, limit)).fetchall()
        items = [json.loads(r['data']) for r in rows]
        next_seq = items[-1]['seq'] if items else after_seq
        return {'items': items, 'next_seq': next_seq, 'has_more': next_seq < maximum}

    def snapshot(self, sid):
        with self.lock, self.connect() as db:
            db.execute('BEGIN')
            row = db.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
            if not row:
                raise KeyError('Sessão não encontrada.')
            config = json.loads(row['config'])
            tickets = [json.loads(r['result']) for r in db.execute('SELECT result FROM tickets WHERE session_id=? AND published=1', (sid,))]
            alerts = [json.loads(r['data']) for r in db.execute('SELECT data FROM alerts WHERE session_id=?', (sid,))]
            last_seq = db.execute('SELECT COALESCE(MAX(seq),0) FROM events WHERE session_id=?', (sid,)).fetchone()[0]
            feedback = [json.loads(r['data']) for r in db.execute('SELECT data FROM feedback WHERE session_id=? ORDER BY rowid', (sid,))]
            suggestions = sum(json.loads(r['data']).get('status') == 'ready' for r in
                              db.execute('SELECT data FROM suggestions WHERE session_id=?', (sid,)))
        latest = {f['suggestion_id']: f for f in feedback}
        feedback_counts = dict(Counter(f['decision'] for f in latest.values()))
        confidence = [r['confidence'] for r in tickets if r.get('confidence') is not None]
        low_count = sum(r['confidence'] < r.get('review_threshold', .75) for r in tickets if r.get('confidence') is not None)
        n = len(tickets)
        triage_eligible = [r for r in tickets if r.get('processing_status') == 'complete'
                           and r.get('decision_origin') == 'policy_suggested'
                           and r.get('suggested_route')]
        triage_eligible_count = len(triage_eligible)
        reviews = sum(bool(r.get('human_review_required')) for r in triage_eligible)
        auto_routed = triage_eligible_count - reviews
        simulated = [r for r in tickets if r['source'] == 'simulation']
        metrics = {'processed': n, 'triage_eligible_count': triage_eligible_count,
                   'triage_ineligible_count': n - triage_eligible_count,
                   'human_review_count': reviews,
                   'human_review_rate': reviews / triage_eligible_count if triage_eligible_count else None,
                   'auto_routed_count': auto_routed,
                   'auto_route_rate': auto_routed / triage_eligible_count if triage_eligible_count else None,
                   'low_confidence_count': low_count,
                   'low_confidence_rate': low_count / len(confidence) if confidence else None,
                   'average_confidence': sum(confidence) / len(confidence) if confidence else None,
                   'duplicate_count': sum(bool(r.get('potential_duplicate')) for r in tickets),
                   'category_distribution': dict(Counter(r.get('predicted_category') or 'Sem classificação' for r in tickets)),
                   'confidence_distribution': {label: sum(lo <= c < hi for c in confidence) for label, lo, hi in
                                               [('0–50%', 0, .5), ('50–75%', .5, .75), ('75–90%', .75, .90), ('90–100%', .90, 1.00001)]},
                   'source_counts': dict(Counter(r['source'] for r in tickets)),
                   'source_breakdown': {source: {'count': len(sample),
                                               'human_review_count': sum(bool(r.get('human_review_required')) for r in sample),
                                               'category_distribution': dict(Counter(r.get('predicted_category') or 'Sem classificação' for r in sample))}
                                        for source in ('simulation', 'user_created')
                                        for sample in [[r for r in tickets if r['source'] == source]]},
                   'suggestions': suggestions, 'feedback': feedback_counts, 'feedback_denominator': len(latest),
                   'median_ttr': None, 'p90_ttr': None, 'first_response_time': None, 'backlog': None,
                   'csat': None, 'operational_unavailable_reason': 'Replay de chegadas não cria duração, CSAT ou resolução.',
                   'latency_by_mode': {mode: {'count': len(values), 'mean_ms': sum(values) / len(values) if values else None}
                                       for mode in ('online', 'precomputed')
                                       for values in [[r['latency_ms'] for r in tickets if r.get('inference_mode') == mode]]}}
        safe_config = {k: v for k, v in config.items() if k != 'ticket_ids'}
        return {'session_id': sid, 'state': row['state'], 'config': safe_config, 'created_at': row['created_at'],
                'updated_at': row['updated_at'], 'error': row['error'], 'last_seq': last_seq,
                'processed': n, 'arrived': len(simulated), 'total': len(config.get('ticket_ids', [])), 'queue': 0,
                'simulation_time': float(row['next_index']), 'metrics': metrics, 'alerts': alerts,
                'recent_decisions': tickets[-20:][::-1],
                'replay_processed': len(simulated), 'manual_processed': n - len(simulated),
                'source': 'simulation' if config.get('kind') == 'replay' else 'user_created',
                'notice': ('SIMULAÇÃO: conteúdo histórico; ordem e horários simulados.' if config.get('kind') == 'replay'
                           else 'SANDBOX: análises manuais isoladas; sem tráfego de produção.')}

    def alert(self, sid, aid):
        self.session(sid)
        with self.connect() as db:
            row = db.execute('SELECT data FROM alerts WHERE id=? AND session_id=?', (aid, sid)).fetchone()
        if not row:
            raise KeyError('Alerta não encontrado nesta sessão.')
        return json.loads(row['data'])

    def save_suggestion(self, sid, ticket, data):
        context = ticket_context(ticket)
        suggestion = dict(data, **context, suggestion_id=uid(), session_id=sid, created_at=now())
        with self.lock, self.connect() as db:
            db.execute('INSERT INTO suggestions VALUES(?,?,?)', (suggestion['suggestion_id'], sid, json.dumps(suggestion)))
            self._event(db, sid, 'SUGGESTION_GENERATED' if data['status'] == 'ready' else 'SUGGESTION_UNAVAILABLE',
                        suggestion, {'suggestion_id': suggestion['suggestion_id'], 'status': data['status']})
        return suggestion

    def feedback(self, suggestion_id, decision, text=None):
        with self.lock, self.connect() as db:
            row = db.execute('SELECT * FROM suggestions WHERE id=?', (suggestion_id,)).fetchone()
            if not row:
                raise KeyError('Sugestão não encontrada.')
            suggestion = json.loads(row['data'])
            if suggestion['status'] != 'ready':
                raise ValueError('Não existe sugestão utilizável para receber feedback.')
            result = {'feedback_id': uid(), 'suggestion_id': suggestion_id, 'session_id': row['session_id'],
                      **ticket_context(suggestion), 'decision': decision, 'text': text, 'created_at': now(),
                      'original_text': suggestion['text']}
            db.execute('INSERT INTO feedback VALUES(?,?,?,?,?,?)', (result['feedback_id'], suggestion_id, row['session_id'], decision, json.dumps(result), result['created_at']))
            self._event(db, row['session_id'], 'FEEDBACK_RECORDED', suggestion, result)
        return result
