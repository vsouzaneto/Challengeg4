/**
 * MCP server do AI Support OS (stdio).
 * Expõe Knowledge Base e triagem como tools reutilizáveis por qualquer agente (single responsibility + reuso).
 *
 *   npm run mcp
 *
 * Claude Code:  claude mcp add support-os -- npx tsx mcp/server.ts   (rodar dentro de solution/app)
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { retrieve, registerGap } from "../src/lib/ai/kb";
import { classify, TEAM_BY_CATEGORY } from "../src/lib/ai/classifier";
import { runPipeline } from "../src/lib/ai/pipeline";
import { all, one } from "../src/lib/db";
import { dashboard } from "../src/lib/analytics";

const server = new McpServer({ name: "support-os", version: "1.0.0" });
const text = (o: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(o, null, 2) }] });

server.registerTool("knowledge.search_articles", {
  description: "Busca o artigo mais relevante da Knowledge Base para uma pergunta. Retorna score, cobertura e candidatos.",
  inputSchema: { query: z.string().min(2) },
}, async ({ query }) => {
  const r = await retrieve(query);
  return text({ article: r.article && { id: r.article.id, title: r.article.title, body: r.article.body }, score: r.score, coverage: r.coverage, candidates: r.candidates });
});

server.registerTool("knowledge.list_gaps", {
  description: "Lista Knowledge Gaps pendentes (perguntas sem resposta), ordenados por ocorrências.",
  inputSchema: { limit: z.number().int().min(1).max(50).default(10) },
}, async ({ limit }) => text(await all("SELECT id, question, topic, occurrences, examples FROM kb_gaps WHERE status='pending' ORDER BY occurrences DESC LIMIT ?", [limit])));

server.registerTool("knowledge.create_gap", {
  description: "Registra uma pergunta sem resposta como Knowledge Gap (agrupa automaticamente com gaps similares).",
  inputSchema: { question: z.string().min(5), source: z.string().default("mcp") },
}, async ({ question, source }) => {
  const c = classify(question);
  return text(await registerGap(question, source, "Other", c.category, 0));
});

server.registerTool("support.classify_text", {
  description: "Classifica um texto em uma das 8 categorias (modelo treinado no IT Service Ticket Dataset) e indica o time de roteamento.",
  inputSchema: { text: z.string().min(2) },
}, async ({ text: t }) => {
  const c = classify(t);
  return text({ category: c.category, confidence: c.confidence, team: TEAM_BY_CATEGORY[c.category], topTerms: c.topTerms });
});

server.registerTool("support.triage_ticket", {
  description: "Roda o pipeline completo (guardrails, classificação, sentimento, risco, prioridade, KB, gate) sem gravar nada. Retorna a decisão e o trace.",
  inputSchema: { message: z.string().min(2) },
}, async ({ message }) => {
  const a = await runPipeline(message);
  return text({ decision: a.decision, reasons: a.decisionReasons, confidence: a.aiConfidence, category: a.category, team: a.team, priority: a.priority, sentiment: a.sentiment, risk: a.risk, reply: a.reply, steps: a.steps });
});

server.registerTool("support.get_ticket", {
  description: "Retorna um ticket e suas mensagens.",
  inputSchema: { id: z.string() },
}, async ({ id }) => text({ ticket: await one("SELECT * FROM tickets WHERE id=?", [id]), messages: await all("SELECT role, author, body, created_at FROM messages WHERE ticket_id=? ORDER BY id", [id]) }));

server.registerTool("support.ops_metrics", {
  description: "KPIs operacionais (volume, backlog, CSAT, decisão do gate, gaps) para um período em dias (1, 7, 30, 60, 90).",
  inputSchema: { days: z.number().int().min(1).max(90).default(30) },
}, async ({ days }) => {
  const d = await dashboard(days);
  return text({ total: d.total, backlog: d.backlog, csat: d.csat, decision: d.decision, gaps: d.gaps, topTopics: d.topics.slice(0, 5), escalationReasons: d.escalationReasons });
});

server.connect(new StdioServerTransport()).catch((e) => { console.error(e); process.exit(1); });
