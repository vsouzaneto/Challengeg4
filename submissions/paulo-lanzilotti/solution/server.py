"""Servidor local do fluxo comercial, com fila e interações persistidas em SQLite."""

import argparse
import json
import os
import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import median
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("FOCO_DB_PATH", APP_DIR / "runtime" / "workflow.sqlite3"))
STATIC_PATHS = {"/", "/index.html", "/styles.css", "/app.js", "/data.json", "/assets/mona-sans-latin-wght-normal.woff2", "/assets/paulo-lanzilotti-applied-ai.pdf"}
ACTIONS = {"skip", "contacted", "no_answer", "reopen", "close"}
SENTIMENTS = {"positive", "neutral", "negative"}
LOCAL_TIMEZONE = ZoneInfo("America/Sao_Paulo")
OPPORTUNITIES = {item["id"]: item for item in json.loads((APP_DIR / "data.json").read_text(encoding="utf-8"))}

by_agent = defaultdict(list)
for opportunity in OPPORTUNITIES.values():
    by_agent[opportunity["agent"]].append(opportunity)
TOP_PRIORITY_IDS = set()
for agent_items in by_agent.values():
    ordered = sorted(agent_items, key=lambda item: (-item["priority_score"], item["id"]))
    cutoff = ordered[max(0, (len(ordered) + 4) // 5 - 1)]["priority_score"]
    TOP_PRIORITY_IDS.update(item["id"] for item in ordered if item["priority_score"] >= cutoff)


def connect():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def add_business_days(start, amount):
    current = start
    for _ in range(amount):
        current += timedelta(days=1)
        while current.weekday() >= 5:
            current += timedelta(days=1)
    return current


def follow_up_days(action, sentiment, streak):
    if action == "contacted":
        return {"positive": 2, "neutral": 5}[sentiment]
    if action == "no_answer":
        return 1 if streak == 1 else 3
    return 1


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect()) as connection, connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS interaction_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id TEXT NOT NULL,
                action TEXT NOT NULL CHECK (action IN ('skip', 'contacted', 'no_answer', 'reopen', 'close')),
                note TEXT,
                assigned_agent TEXT NOT NULL,
                priority_score INTEGER NOT NULL,
                stage TEXT NOT NULL,
                session_id TEXT,
                occurred_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS opportunity_state (
                opportunity_id TEXT PRIMARY KEY,
                last_note TEXT,
                last_note_at TEXT,
                last_action TEXT NOT NULL,
                last_action_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS queue_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        connection.execute("INSERT OR IGNORE INTO queue_meta(key, value) VALUES ('first_seen_on', ?)",
                           (datetime.now(LOCAL_TIMEZONE).date().isoformat(),))
        event_columns = {row["name"] for row in connection.execute("PRAGMA table_info(interaction_events)")}
        state_columns = {row["name"] for row in connection.execute("PRAGMA table_info(opportunity_state)")}
        for column, definition in {
            "sentiment": "TEXT", "next_due_on": "TEXT", "local_date": "TEXT", "is_revisit": "INTEGER NOT NULL DEFAULT 0",
            "actor_id": "TEXT", "client_action_id": "TEXT", "follow_up_on": "TEXT"
        }.items():
            if column not in event_columns:
                connection.execute(f"ALTER TABLE interaction_events ADD COLUMN {column} {definition}")
        for column, definition in {
            "last_action_on": "TEXT", "next_due_on": "TEXT", "sentiment": "TEXT", "streak": "INTEGER NOT NULL DEFAULT 0",
            "attempt_count": "INTEGER NOT NULL DEFAULT 0", "last_attempt_on": "TEXT", "deadline_on": "TEXT",
            "status": "TEXT NOT NULL DEFAULT 'active'", "no_answer_streak": "INTEGER NOT NULL DEFAULT 0",
            "skip_streak": "INTEGER NOT NULL DEFAULT 0", "version": "INTEGER NOT NULL DEFAULT 0",
            "due_source": "TEXT NOT NULL DEFAULT 'automatic'"
        }.items():
            if column not in state_columns:
                connection.execute(f"ALTER TABLE opportunity_state ADD COLUMN {column} {definition}")
        connection.execute("UPDATE interaction_events SET local_date = substr(occurred_at, 1, 10) WHERE local_date IS NULL")
        old_rows = connection.execute("SELECT opportunity_id, last_action, last_action_at FROM opportunity_state WHERE last_action_on IS NULL").fetchall()
        for row in old_rows:
            action_on = datetime.fromisoformat(row["last_action_at"].replace("Z", "+00:00")).astimezone(LOCAL_TIMEZONE).date()
            due = add_business_days(action_on, follow_up_days(row["last_action"], "neutral", 1))
            if row["opportunity_id"] in TOP_PRIORITY_IDS:
                due = min(due, add_business_days(action_on, 10))
            attempts = connection.execute("SELECT COUNT(*) FROM interaction_events WHERE opportunity_id = ?", (row["opportunity_id"],)).fetchone()[0]
            connection.execute("""
                UPDATE opportunity_state SET last_action_on = ?, next_due_on = ?, attempt_count = ?, streak = 1,
                    last_attempt_on = ?, deadline_on = ?, version = ?
                WHERE opportunity_id = ?
            """, (action_on.isoformat(), due.isoformat(), attempts,
                  action_on.isoformat() if row["last_action"] in ("contacted", "no_answer") else None,
                  due.isoformat(), attempts, row["opportunity_id"]))
        connection.execute("""
            UPDATE opportunity_state SET
                deadline_on = COALESCE(deadline_on, next_due_on),
                last_attempt_on = CASE
                    WHEN last_attempt_on IS NULL AND last_action IN ('contacted', 'no_answer') THEN last_action_on
                    ELSE last_attempt_on END,
                version = CASE WHEN version = 0 THEN attempt_count ELSE version END
        """)
        connection.execute("""
            UPDATE opportunity_state SET attempt_count = (
                SELECT COUNT(*) FROM interaction_events
                WHERE interaction_events.opportunity_id = opportunity_state.opportunity_id
                  AND action IN ('contacted', 'no_answer')
            )
        """)
        event_schema = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'interaction_events'"
        ).fetchone()[0]
        if "'reopen'" not in event_schema:
            connection.executescript("""
                CREATE TABLE interaction_events_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id TEXT NOT NULL,
                    action TEXT NOT NULL CHECK (action IN ('skip', 'contacted', 'no_answer', 'reopen', 'close')),
                    note TEXT, assigned_agent TEXT NOT NULL, priority_score INTEGER NOT NULL,
                    stage TEXT NOT NULL, session_id TEXT, occurred_at TEXT NOT NULL,
                    sentiment TEXT, next_due_on TEXT, local_date TEXT, is_revisit INTEGER NOT NULL DEFAULT 0,
                    actor_id TEXT, client_action_id TEXT, follow_up_on TEXT
                );
                INSERT INTO interaction_events_new
                SELECT id, opportunity_id, action, note, assigned_agent, priority_score, stage,
                       session_id, occurred_at, sentiment, next_due_on, local_date, is_revisit,
                       actor_id, client_action_id, follow_up_on
                FROM interaction_events;
                DROP TABLE interaction_events;
                ALTER TABLE interaction_events_new RENAME TO interaction_events;
            """)
        connection.executescript("""
            CREATE INDEX IF NOT EXISTS idx_interaction_events_opportunity ON interaction_events(opportunity_id, occurred_at DESC);
            CREATE INDEX IF NOT EXISTS idx_interaction_events_agent_day ON interaction_events(assigned_agent, local_date);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_interaction_events_client_action
                ON interaction_events(client_action_id) WHERE client_action_id IS NOT NULL;
        """)


def first_seen_on(connection):
    return date.fromisoformat(connection.execute(
        "SELECT value FROM queue_meta WHERE key = 'first_seen_on'"
    ).fetchone()[0])


def serialize_activity(row, item, today, first_seen):
    if row is None:
        deadline = add_business_days(first_seen, 10 if item["id"] in TOP_PRIORITY_IDS else 20).isoformat()
        return {
            "last_action": None, "last_action_at": None, "last_action_on": None,
            "last_attempt_on": None, "next_due_on": None, "deadline_on": deadline,
            "sentiment": None, "attempt_count": 0, "status": "new",
            "version": 0, "due_source": None, "protected": item["id"] in TOP_PRIORITY_IDS,
            "queue_section": "active",
        }
    if row["status"] == "closed":
        section = "closed"
    elif row["status"] == "review":
        section = "review"
    elif row["next_due_on"] and row["next_due_on"] > today:
        section = "later"
    else:
        section = "active"
    return {
        "last_action": row["last_action"],
        "last_action_at": row["last_action_at"],
        "last_action_on": row["last_action_on"],
        "last_attempt_on": row["last_attempt_on"],
        "next_due_on": row["next_due_on"],
        "deadline_on": row["deadline_on"],
        "sentiment": row["sentiment"],
        "attempt_count": row["attempt_count"],
        "status": row["status"],
        "version": row["version"],
        "due_source": row["due_source"],
        "protected": item["id"] in TOP_PRIORITY_IDS,
        "queue_section": section,
    }


def queue_order(activity):
    sections = {"review": 0, "active": 1, "later": 2, "closed": 3}
    return sorted(
        (item for item in OPPORTUNITIES.values() if activity[item["id"]]["queue_section"] != "closed"),
        key=lambda item: (
            sections[activity[item["id"]]["queue_section"]],
            activity[item["id"]]["deadline_on"] or "9999-12-31",
            -item["priority_score"],
            item["id"],
        ),
    )


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/state":
            today = datetime.now(LOCAL_TIMEZONE).date().isoformat()
            with closing(connect()) as connection:
                rows = connection.execute("SELECT * FROM opportunity_state").fetchall()
                first_seen = first_seen_on(connection)
                counts = connection.execute("""
                    SELECT assigned_agent, COUNT(*) AS total FROM interaction_events
                    WHERE local_date = ? GROUP BY assigned_agent
                """, (today,)).fetchall()
                attempts = connection.execute("""
                    SELECT assigned_agent, local_date, COUNT(*) AS total FROM interaction_events
                    WHERE action IN ('contacted', 'no_answer')
                    GROUP BY assigned_agent, local_date ORDER BY local_date DESC
                """).fetchall()
                recent_calls = connection.execute("""
                    SELECT opportunity_id, assigned_agent, action, occurred_at FROM interaction_events
                    WHERE local_date >= ? AND action IN ('contacted', 'no_answer')
                    ORDER BY occurred_at DESC, id DESC
                """, ((date.fromisoformat(today) - timedelta(days=7)).isoformat(),)).fetchall()
            notes = {row["opportunity_id"]: {"text": row["last_note"], "at": row["last_note_at"]} for row in rows if row["last_note"]}
            saved = {row["opportunity_id"]: row for row in rows}
            activity = {item["id"]: serialize_activity(saved.get(item["id"]), item, today, first_seen)
                        for item in OPPORTUNITIES.values()}
            attempts_by_agent = defaultdict(list)
            for row in attempts:
                if len(attempts_by_agent[row["assigned_agent"]]) < 10:
                    attempts_by_agent[row["assigned_agent"]].append(row["total"])
            capacity = {agent: median(values) if len(values) >= 5 else None
                        for agent, values in attempts_by_agent.items()}
            recent_accounts = {}
            for row in recent_calls:
                account = OPPORTUNITIES[row["opportunity_id"]].get("account")
                if account and account not in recent_accounts:
                    recent_accounts[account] = {"opportunity_id": row["opportunity_id"],
                                                "agent": row["assigned_agent"], "at": row["occurred_at"]}
            self.send_json(200, {"lastNotes": notes, "activity": activity, "today": today,
                                 "queueOrder": [item["id"] for item in queue_order(activity)],
                                 "actionsTodayByAgent": {row["assigned_agent"]: row["total"] for row in counts},
                                 "callCapacityByAgent": capacity, "recentAccounts": recent_accounts})
            return
        if path not in STATIC_PATHS:
            self.send_error(404, "Not found")
            return
        self.path = "/index.html" if path == "/" else path
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/interactions":
            self.send_error(404, "Not found")
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            self.send_json(415, {"error": "Envie os dados em JSON"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 8192:
                raise ValueError("Tamanho de solicitação inválido")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Formato inválido")
            opportunity_id = payload.get("opportunity_id")
            action = payload.get("action")
            actor_id = payload.get("actor_id")
            expected_version = payload.get("expected_version")
            client_action_id = payload.get("client_action_id")
            session_id = payload.get("session_id", "")
            note = payload.get("note")
            sentiment = payload.get("sentiment")
            follow_up_on = payload.get("follow_up_on")
            if not isinstance(opportunity_id, str) or opportunity_id not in OPPORTUNITIES or action not in ACTIONS:
                raise ValueError("Oportunidade ou ação inválida")
            if not isinstance(actor_id, str) or actor_id not in by_agent:
                raise ValueError("Selecione o vendedor responsável")
            if not isinstance(expected_version, int) or isinstance(expected_version, bool) or expected_version < 0:
                raise ValueError("Versão da oportunidade inválida")
            if not isinstance(client_action_id, str) or not 1 <= len(client_action_id) <= 80:
                raise ValueError("Identificador da ação inválido")
            if not isinstance(session_id, str) or len(session_id) > 80:
                raise ValueError("Sessão inválida")
            if action == "contacted":
                if not isinstance(note, str) or not note.strip() or len(note.strip()) > 1000:
                    raise ValueError("Escreva uma observação de até 1.000 caracteres")
                if sentiment not in SENTIMENTS:
                    raise ValueError("Selecione o resultado da conversa")
                note = note.strip()
            else:
                note = None
                sentiment = None
            if follow_up_on is not None:
                if not isinstance(follow_up_on, str):
                    raise ValueError("Data de retorno inválida")
                follow_up_date = date.fromisoformat(follow_up_on)
            else:
                follow_up_date = None
            if action == "reopen" and follow_up_date is None:
                raise ValueError("Escolha a data do próximo contato")
            if action not in ("contacted", "reopen") and follow_up_date is not None:
                raise ValueError("Data de retorno não se aplica a esta ação")
            if action == "contacted" and sentiment == "negative" and follow_up_date is not None:
                raise ValueError("Conversa negativa precisa de revisão")
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
            return

        item = OPPORTUNITIES[opportunity_id]
        if actor_id != item["agent"]:
            self.send_json(403, {"error": "Esta oportunidade pertence a outro vendedor"})
            return
        now = datetime.now(timezone.utc)
        occurred_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
        action_on = now.astimezone(LOCAL_TIMEZONE).date()
        if follow_up_date is not None and follow_up_date < action_on:
            self.send_json(400, {"error": "A data de retorno não pode estar no passado"})
            return

        try:
            with closing(connect()) as connection, connection:
                connection.execute("BEGIN IMMEDIATE")
                first_seen = first_seen_on(connection)
                previous = connection.execute(
                    "SELECT * FROM opportunity_state WHERE opportunity_id = ?", (opportunity_id,)
                ).fetchone()
                duplicate = connection.execute(
                    "SELECT opportunity_id, action, actor_id FROM interaction_events WHERE client_action_id = ?",
                    (client_action_id,)
                ).fetchone()
                if duplicate:
                    if (duplicate["opportunity_id"], duplicate["action"], duplicate["actor_id"]) != (opportunity_id, action, actor_id):
                        self.send_json(409, {"error": "Identificador de ação já utilizado"})
                        return
                    current = serialize_activity(previous, item, action_on.isoformat(), first_seen)
                    last_note = ({"text": previous["last_note"], "at": previous["last_note_at"]}
                                 if previous and previous["last_note"] else None)
                    self.send_json(200, {"saved": True, "duplicate": True, "lastNote": last_note,
                                         "activity": current})
                    return
                version = previous["version"] if previous else 0
                if expected_version != version:
                    self.send_json(409, {"error": "Esta oportunidade mudou em outra sessão. Recarregue a fila."})
                    return
                if previous and previous["status"] == "closed":
                    self.send_json(409, {"error": "Esta oportunidade já foi encerrada"})
                    return
                if previous and previous["status"] == "review" and action not in ("reopen", "close"):
                    self.send_json(409, {"error": "Revise ou encerre esta oportunidade antes de ligar novamente"})
                    return
                if previous and previous["next_due_on"] and previous["next_due_on"] > action_on.isoformat() and action in ("skip", "no_answer", "contacted"):
                    self.send_json(409, {"error": "O retorno desta oportunidade ainda não venceu"})
                    return
                if action == "reopen" and (not previous or
                                           (previous["status"] != "review" and
                                            not (previous["next_due_on"] and previous["next_due_on"] > action_on.isoformat()))):
                    self.send_json(409, {"error": "Esta oportunidade não está em revisão nem agendada"})
                    return

                original_deadline = (previous["deadline_on"] if previous and previous["deadline_on"]
                                     else add_business_days(first_seen, 10 if opportunity_id in TOP_PRIORITY_IDS else 20).isoformat())
                attempts = previous["attempt_count"] if previous else 0
                last_attempt = previous["last_attempt_on"] if previous else None
                no_answer_streak = previous["no_answer_streak"] if previous else 0
                skip_streak = previous["skip_streak"] if previous else 0
                old_sentiment = previous["sentiment"] if previous else None
                status = "active"
                due_source = "automatic"
                due_on = None
                deadline_on = original_deadline

                if action == "skip":
                    skip_streak += 1
                    if skip_streak >= 2:
                        status = "review"
                    else:
                        due_on = add_business_days(action_on, 1).isoformat()
                    # Pular não renova o prazo nem conta como ligação.
                elif action == "no_answer":
                    attempts += 1
                    last_attempt = action_on.isoformat()
                    no_answer_streak += 1
                    skip_streak = 0
                    if no_answer_streak >= 3:
                        status = "review"
                        deadline_on = None
                    else:
                        due_on = add_business_days(action_on, follow_up_days(action, None, no_answer_streak)).isoformat()
                        deadline_on = due_on
                elif action == "contacted":
                    attempts += 1
                    last_attempt = action_on.isoformat()
                    no_answer_streak = 0
                    skip_streak = 0
                    if sentiment == "negative":
                        status = "review"
                        deadline_on = None
                    else:
                        due_source = "manual" if follow_up_date else "automatic"
                        due_on = (follow_up_date or add_business_days(action_on, follow_up_days(action, sentiment, 1))).isoformat()
                        deadline_on = due_on
                elif action == "reopen":
                    if previous and previous["status"] == "review":
                        no_answer_streak = 0
                        skip_streak = 0
                    due_source = "manual"
                    due_on = follow_up_date.isoformat()
                    deadline_on = due_on
                else:
                    status = "closed"
                    no_answer_streak = 0
                    skip_streak = 0
                    deadline_on = None

                note_at = occurred_at if note else (previous["last_note_at"] if previous else None)
                saved_note = note if note else (previous["last_note"] if previous else None)
                saved_sentiment = sentiment if sentiment else old_sentiment
                connection.execute("""
                    INSERT INTO interaction_events
                    (opportunity_id, action, note, assigned_agent, priority_score, stage, session_id,
                     occurred_at, sentiment, next_due_on, local_date, is_revisit, actor_id,
                     client_action_id, follow_up_on)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (opportunity_id, action, note, item["agent"], item["priority_score"], item["stage"],
                      session_id, occurred_at, sentiment, due_on, action_on.isoformat(), int(previous is not None),
                      actor_id, client_action_id, follow_up_date.isoformat() if follow_up_date else None))
                connection.execute("""
                    INSERT INTO opportunity_state
                    (opportunity_id, last_note, last_note_at, last_action, last_action_at,
                     last_action_on, next_due_on, sentiment, streak, attempt_count,
                     last_attempt_on, deadline_on, status, no_answer_streak, skip_streak, version, due_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(opportunity_id) DO UPDATE SET
                        last_note = excluded.last_note,
                        last_note_at = excluded.last_note_at,
                        last_action = excluded.last_action,
                        last_action_at = excluded.last_action_at,
                        last_action_on = excluded.last_action_on,
                        next_due_on = excluded.next_due_on,
                        sentiment = excluded.sentiment,
                        streak = excluded.streak,
                        attempt_count = excluded.attempt_count,
                        last_attempt_on = excluded.last_attempt_on,
                        deadline_on = excluded.deadline_on,
                        status = excluded.status,
                        no_answer_streak = excluded.no_answer_streak,
                        skip_streak = excluded.skip_streak,
                        version = excluded.version,
                        due_source = excluded.due_source
                """, (opportunity_id, saved_note, note_at, action, occurred_at, action_on.isoformat(),
                      due_on, saved_sentiment, max(no_answer_streak, skip_streak), attempts,
                      last_attempt, deadline_on, status, no_answer_streak, skip_streak, version + 1, due_source))
                saved = connection.execute(
                    "SELECT * FROM opportunity_state WHERE opportunity_id = ?", (opportunity_id,)
                ).fetchone()
                count = connection.execute("""
                    SELECT COUNT(*) FROM interaction_events WHERE assigned_agent = ? AND local_date = ?
                """, (item["agent"], action_on.isoformat())).fetchone()[0]
        except sqlite3.Error:
            self.send_json(500, {"error": "Não foi possível salvar a interação"})
            return

        last_note = {"text": saved["last_note"], "at": saved["last_note_at"]} if saved["last_note"] else None
        self.send_json(201, {"saved": True, "lastNote": last_note,
                             "activity": serialize_activity(saved, item, action_on.isoformat(), first_seen),
                             "today": action_on.isoformat(), "agent": item["agent"],
                             "actionsTodayForAgent": count})


def main():
    parser = argparse.ArgumentParser(description="Servidor local do Foco")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    initialize_database()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Foco em http://localhost:{args.port} (dados locais em {DB_PATH})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
