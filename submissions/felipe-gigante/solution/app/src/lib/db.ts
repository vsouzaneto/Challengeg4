// SQLite via libsql.
// - Local: arquivo data/app.db (gerado por `npm run seed`).
// - Vercel: o filesystem é read-only, então o app.db empacotado no build é copiado para /tmp
//   no cold start (escritas valem enquanto a instância vive — suficiente para demo).
// - Persistência real: defina TURSO_DATABASE_URL + TURSO_AUTH_TOKEN (SQLite gerenciado, mesmo driver).
import { createClient, type Client, type InValue } from "@libsql/client";
import fs from "node:fs";
import path from "node:path";

const BUNDLED = path.join(process.cwd(), "data", "app.db");

let client: Client | null = null;
let ready: Promise<void> | null = null;

function resolveUrl(): { url: string; authToken?: string } {
  if (process.env.TURSO_DATABASE_URL) return { url: process.env.TURSO_DATABASE_URL, authToken: process.env.TURSO_AUTH_TOKEN };
  if (process.env.DATABASE_FILE) return { url: `file:${process.env.DATABASE_FILE}` };
  if (process.env.VERCEL) {
    const tmp = "/tmp/app.db";
    if (!fs.existsSync(tmp)) {
      if (!fs.existsSync(BUNDLED)) throw new Error(`SQLite empacotado não encontrado em ${BUNDLED} — verifique outputFileTracingIncludes.`);
      fs.copyFileSync(BUNDLED, tmp);
    }
    return { url: `file:${tmp}` };
  }
  return { url: `file:${BUNDLED}` };
}

export function getClient(): Client {
  if (!client) client = createClient(resolveUrl());
  return client;
}

export const SCHEMA = `
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'agent', created_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS tickets (
  id TEXT PRIMARY KEY, source TEXT NOT NULL, customer_name TEXT, customer_email TEXT, channel TEXT, product TEXT,
  subject TEXT, topic TEXT, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL,
  status TEXT NOT NULL, assignee TEXT NOT NULL,
  category TEXT, category_conf REAL, team TEXT, priority TEXT, priority_score INTEGER,
  sentiment TEXT, sentiment_score INTEGER, ai_confidence REAL, kb_score REAL, kb_weight REAL DEFAULT 1, kb_article_id INTEGER,
  decision TEXT, risk_level TEXT, risk_reasons TEXT, guardrail_flags TEXT, model_tier TEXT,
  summary TEXT, suggested_reply TEXT, first_response_at INTEGER, resolved_at INTEGER,
  csat INTEGER, csat_comment TEXT, automated INTEGER DEFAULT 0, portal_token TEXT,
  dataset_type TEXT, dataset_priority TEXT, dataset_status TEXT, dataset_resolution TEXT, trace TEXT);
CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id TEXT NOT NULL, role TEXT NOT NULL, author TEXT,
  body TEXT NOT NULL, created_at INTEGER NOT NULL, meta TEXT);
CREATE INDEX IF NOT EXISTS idx_messages_ticket ON messages(ticket_id);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id TEXT, type TEXT NOT NULL, payload TEXT, created_at INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type, created_at);
CREATE TABLE IF NOT EXISTS kb_articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT NOT NULL, body_en TEXT NOT NULL DEFAULT '', questions TEXT NOT NULL DEFAULT '',
  tags TEXT NOT NULL DEFAULT '', topic TEXT, source TEXT NOT NULL DEFAULT 'seed', uses INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS kb_gaps (
  id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, topic TEXT, category TEXT, occurrences INTEGER NOT NULL DEFAULT 1,
  best_score REAL, status TEXT NOT NULL DEFAULT 'pending', article_id INTEGER, ticket_ids TEXT NOT NULL DEFAULT '[]',
  examples TEXT NOT NULL DEFAULT '[]', created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS eval_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at INTEGER NOT NULL, version TEXT, metrics TEXT NOT NULL, details TEXT NOT NULL);
`;

/** Mantém a demo "viva": desloca as datas do seed para terminarem em agora. */
async function rebaseSeedDates(db: Client) {
  const r = await db.execute("SELECT value FROM meta WHERE key='anchor_time'");
  const anchor = Number(r.rows[0]?.value ?? 0);
  if (!anchor) return;
  const shift = Date.now() - anchor;
  if (shift < 60 * 60 * 1000) return;
  await db.batch([
    { sql: "UPDATE tickets SET created_at=created_at+?, updated_at=updated_at+?, first_response_at=first_response_at+?, resolved_at=resolved_at+?", args: [shift, shift, shift, shift] },
    { sql: "UPDATE messages SET created_at=created_at+?", args: [shift] },
    { sql: "UPDATE events SET created_at=created_at+?", args: [shift] },
    { sql: "UPDATE kb_gaps SET created_at=created_at+?, updated_at=updated_at+?", args: [shift, shift] },
    { sql: "UPDATE meta SET value=? WHERE key='anchor_time'", args: [String(Date.now())] },
  ], "write");
}

export async function db(): Promise<Client> {
  const c = getClient();
  if (!ready) {
    ready = (async () => {
      await c.executeMultiple(SCHEMA);
      await rebaseSeedDates(c);
    })().catch((e) => { ready = null; throw e; });
  }
  await ready;
  return c;
}

export async function all<T = Record<string, unknown>>(sql: string, args: InValue[] = []): Promise<T[]> {
  const r = await (await db()).execute({ sql, args });
  return r.rows.map((row) => ({ ...row }) as T);
}

export async function one<T = Record<string, unknown>>(sql: string, args: InValue[] = []): Promise<T | null> {
  return (await all<T>(sql, args))[0] ?? null;
}

export async function run(sql: string, args: InValue[] = []) {
  return (await db()).execute({ sql, args });
}

export async function logEvent(ticketId: string | null, type: string, payload: unknown = {}) {
  await run("INSERT INTO events (ticket_id, type, payload, created_at) VALUES (?,?,?,?)", [ticketId, type, JSON.stringify(payload), Date.now()]);
}
