/**
 * Seed do banco SQLite com dados REAIS do Dataset 1 (8.469 tickets) processados pelo pipeline de IA.
 *
 * - Textos: descrição original com placeholders de template ({product_purchased}...) substituídos.
 * - Datas: o dataset concentra tudo em ~27h e não tem timestamp de criação; para os dashboards de
 *   1d/7d/30d/60d/90d, os tickets são redistribuídos (seed determinístico) nos últimos 90 dias.
 *   O ordenamento relativo e todos os demais campos são preservados.
 * - TTR: usado apenas onde é válido (Time to Resolution > First Response Time, 1.402 tickets).
 * - CSAT: valor original do dataset nos tickets fechados.
 *
 * Uso: npm run seed
 */
import fs from "node:fs";
import path from "node:path";
import { getClient, SCHEMA } from "../src/lib/db";
import { runPipeline } from "../src/lib/ai/pipeline";
import { invalidateKbCache } from "../src/lib/ai/kb";
import { cleanDatasetText } from "../src/lib/ai/text";
import { analysisColumns, createPortalTicket, customerReply, agentSend, returnToAi, submitCsat, escalate, getTicket } from "../src/lib/tickets";
import { hashPassword } from "../src/lib/password";
import { runEvals } from "../src/lib/evals";
import { KB_ARTICLES } from "../src/lib/seed/kb-articles";
import { DEMO_CONVERSATIONS, UNANSWERED_QUESTIONS, SUGGESTED } from "../src/lib/seed/demo";

const ROOT = path.join(__dirname, "..");
const DB_FILE = path.join(ROOT, "data", "app.db");
const CSV = path.join(ROOT, "data", "raw", "customer_support_tickets.csv");
const DAY = 86_400_000;

function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = [];
  let row: string[] = [], field = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else q = false; }
      else field += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(field); rows.push(row); row = []; field = "";
    } else field += ch;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [head, ...body] = rows.filter((r) => r.length > 1);
  return body.map((r) => Object.fromEntries(head.map((h, i) => [h, r[i] ?? ""])));
}

function mulberry32(seed: number) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

async function main() {
  // Com Turso configurado, o build não deve re-semear o banco remoto a cada deploy.
  if (process.env.TURSO_DATABASE_URL && process.env.SEED_REMOTE !== "1") {
    console.log("TURSO_DATABASE_URL definido: seed ignorado (use SEED_REMOTE=1 npm run seed uma única vez).");
    return;
  }
  // Sempre grava em data/app.db (no build da Vercel, VERCEL=1 faria o db.ts apontar para /tmp).
  if (!process.env.TURSO_DATABASE_URL) process.env.DATABASE_FILE = DB_FILE;
  for (const f of [DB_FILE, `${DB_FILE}-wal`, `${DB_FILE}-shm`]) if (fs.existsSync(f)) fs.rmSync(f);
  const db = getClient();
  if (process.env.TURSO_DATABASE_URL) {
    // Banco remoto: recomeça do zero (o arquivo local é recriado acima; o remoto precisa de DROP).
    for (const t of ["meta", "users", "sessions", "tickets", "messages", "events", "kb_articles", "kb_gaps", "eval_runs"]) await db.execute(`DROP TABLE IF EXISTS ${t}`);
  }
  await db.executeMultiple(SCHEMA);
  const anchor = Date.now();
  await db.execute({ sql: "INSERT INTO meta (key, value) VALUES ('anchor_time', ?), ('seeded_at', ?)", args: [String(anchor), new Date(anchor).toISOString()] });

  // Usuário demo
  await db.execute({ sql: "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?,?,?,?,?)", args: ["Gestor Demo", "demo@g4.com.br", hashPassword("g4demo2026"), "manager", anchor] });

  // Knowledge Base
  for (const a of KB_ARTICLES) {
    await db.execute({
      sql: "INSERT INTO kb_articles (title, body, body_en, questions, tags, topic, source, uses, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
      args: [a.title, a.body, a.body_en, a.questions.join("\n"), `${a.tags} ${a.topic.toLowerCase()}`, a.topic, "seed", 0, anchor - 120 * DAY, anchor - 120 * DAY],
    });
  }
  invalidateKbCache();

  // Dataset 1
  const rows = parseCsv(fs.readFileSync(CSV, "utf8"));
  const rand = mulberry32(42);
  console.log(`Dataset 1: ${rows.length} tickets`);
  const stats = { auto: 0, suggest: 0, human: 0, gaps: 0 };
  let batch: { sql: string; args: (string | number | null)[] }[] = [];
  const t0 = Date.now();
  for (const [i, r] of rows.entries()) {
    // Assunto + descrição, como chegaria num formulário real; Ticket Type entra como sinal estruturado de risco.
    const text = cleanDatasetText(r["Ticket Description"], r["Product Purchased"]);
    const a = await runPipeline(text, { customerName: r["Customer Name"], useLlm: false, declaredType: r["Ticket Type"], subject: r["Ticket Subject"] });
    stats[a.decision]++;
    // Redistribui nos últimos 90 dias, com sazonalidade semanal (fim de semana com ~60% do volume).
    let created: number;
    do { created = anchor - Math.floor(rand() * 90 * DAY); } while ([0, 6].includes(new Date(created).getDay()) && rand() > 0.6);
    const frt = r["First Response Time"] ? Date.parse(r["First Response Time"].replace(" ", "T")) : NaN;
    const ttr = r["Time to Resolution"] ? Date.parse(r["Time to Resolution"].replace(" ", "T")) : NaN;
    const validDuration = !isNaN(frt) && !isNaN(ttr) && ttr > frt ? ttr - frt : null;
    const status = r["Ticket Status"] === "Closed" ? "closed" : r["Ticket Status"] === "Pending Customer Response" ? "pending" : a.decision === "human" ? "escalated" : "open";
    const assignee = status === "closed" || status === "pending" ? "Agente (histórico)" : a.decision === "human" ? `Fila: ${a.team}` : "AI Agent";
    const id = `TK-${String(i + 1).padStart(5, "0")}`;
    const c = analysisColumns(a);
    batch.push({
      sql: `INSERT INTO tickets (id, source, customer_name, customer_email, channel, product, subject, created_at, updated_at, status, assignee,
        topic, category, category_conf, team, priority, priority_score, sentiment, sentiment_score, ai_confidence, kb_score, kb_weight, kb_article_id,
        decision, risk_level, risk_reasons, guardrail_flags, model_tier, summary, suggested_reply, resolved_at, csat,
        dataset_type, dataset_priority, dataset_status, dataset_resolution, trace)
        VALUES (?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?, ?,?,?,?,?)`,
      args: [id, "dataset", r["Customer Name"], r["Customer Email"], r["Ticket Channel"], r["Product Purchased"], r["Ticket Subject"], created, created, status, assignee,
        r["Ticket Subject"], c.category, c.category_conf, c.team, c.priority, c.priority_score, c.sentiment, c.sentiment_score, c.ai_confidence, c.kb_score, c.kb_weight, c.kb_article_id,
        c.decision, c.risk_level, c.risk_reasons, c.guardrail_flags, c.model_tier, c.summary, c.suggested_reply, status === "closed" && validDuration ? created + validDuration : null,
        r["Customer Satisfaction Rating"] ? Number(r["Customer Satisfaction Rating"]) : null,
        r["Ticket Type"], r["Ticket Priority"], r["Ticket Status"], r["Resolution"] || null, c.trace],
    });
    batch.push({ sql: "INSERT INTO messages (ticket_id, role, author, body, created_at, meta) VALUES (?,?,?,?,?,?)", args: [id, "customer", r["Customer Name"], text, created, JSON.stringify({ sentiment: a.sentiment.score })] });
    if (a.decision === "human") batch.push({ sql: "INSERT INTO events (ticket_id, type, payload, created_at) VALUES (?,?,?,?)", args: [id, "escalated", JSON.stringify({ reasons: a.decisionReasons, by: "ai" }), created] });
    if (batch.length >= 600) { await db.batch(batch, "write"); batch = []; }
  }
  if (batch.length) await db.batch(batch, "write");
  console.log(`Pipeline em ${rows.length} tickets: ${((Date.now() - t0) / 1000).toFixed(1)}s`, stats);

  // Perguntas sem cobertura na KB (variações reais de clientes) → Knowledge Gaps agrupados por similaridade.
  for (const [i, q] of UNANSWERED_QUESTIONS.entries()) {
    const at = anchor - Math.floor(rand() * 20 * DAY);
    const res = await createPortalTicket({ name: q.name, email: `${q.name.split(" ")[0].toLowerCase()}@exemplo.com.br`, message: q.text, channel: q.channel });
    await db.execute({ sql: "UPDATE tickets SET source='demo', created_at=?, updated_at=?, first_response_at=? WHERE id=?", args: [at, at, at, res.id] });
    await db.execute({ sql: "UPDATE messages SET created_at=? WHERE ticket_id=?", args: [at, res.id] });
    await db.execute({ sql: "UPDATE events SET created_at=? WHERE ticket_id=?", args: [at, res.id] });
    if (res.analysis.createGap) stats.gaps++;
    if (i % 10 === 0) process.stdout.write(".");
  }

  // Conversas demo completas (upstream → humano → downstream → CSAT).
  for (const d of DEMO_CONVERSATIONS) {
    const res = await createPortalTicket({ name: d.name, email: d.email, message: d.first, channel: d.channel });
    for (const step of d.steps) {
      if (step.kind === "customer") await customerReply(res.id, step.text);
      if (step.kind === "escalate") await escalate(res.id, step.agent, step.text);
      if (step.kind === "agent") {
        const text = step.text === SUGGESTED ? (await getTicket(res.id))?.suggested_reply ?? "" : step.text;
        await agentSend(res.id, step.agent, text, step.feedback ?? "manual");
      }
      if (step.kind === "return") await returnToAi(res.id, step.agent, step.text);
      if (step.kind === "csat") await submitCsat(res.id, step.score, step.text);
    }
    const at = anchor - d.hoursAgo * 3_600_000;
    const shift = Date.now() - at;
    await db.batch([
      { sql: "UPDATE tickets SET source='demo', created_at=created_at-?, updated_at=updated_at-?, first_response_at=first_response_at-?, resolved_at=resolved_at-? WHERE id=?", args: [shift, shift, shift, shift, res.id] },
      { sql: "UPDATE messages SET created_at=created_at-? WHERE ticket_id=?", args: [shift, res.id] },
      { sql: "UPDATE events SET created_at=created_at-? WHERE ticket_id=?", args: [shift, res.id] },
    ], "write");
  }

  // Histórico de evals: a v1 (real, antes da correção do regex PT de reembolso) + a execução atual.
  const hist = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "eval_history_seed.json"), "utf8")) as { created_at: number; version: string; metrics: unknown; details: unknown }[];
  for (const h of hist) await db.execute({ sql: "INSERT INTO eval_runs (created_at, version, metrics, details) VALUES (?,?,?,?)", args: [h.created_at, h.version, JSON.stringify(h.metrics), JSON.stringify(h.details)] });
  const ev = await runEvals();
  console.log("\nEval:", ev.metrics.behavioral, "unsafeAuto", ev.metrics.escalation.unsafeAuto);

  const g = await db.execute("SELECT COUNT(*) n, SUM(occurrences) o FROM kb_gaps");
  console.log("\nGaps:", g.rows[0]);
}

main().then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); });
