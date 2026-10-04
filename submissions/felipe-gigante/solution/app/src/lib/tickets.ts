// Repositório de tickets + fluxos de Human in the Loop (upstream/downstream), feedback loop e CSAT.
import crypto from "node:crypto";
import { all, one, run, logEvent } from "./db";
import { runPipeline, type Analysis } from "./ai/pipeline";
import { registerGap } from "./ai/kb";

export type Ticket = {
  id: string; source: string; customer_name: string; customer_email: string; channel: string; product: string | null;
  subject: string; topic: string; created_at: number; updated_at: number; status: string; assignee: string;
  category: string; category_conf: number; team: string; priority: string; priority_score: number;
  sentiment: string; sentiment_score: number; ai_confidence: number; kb_score: number; kb_weight: number; kb_article_id: number | null;
  decision: string; risk_level: string; risk_reasons: string; guardrail_flags: string; model_tier: string;
  summary: string; suggested_reply: string | null; first_response_at: number | null; resolved_at: number | null;
  csat: number | null; csat_comment: string | null; automated: number; portal_token: string | null;
  dataset_type: string | null; dataset_priority: string | null; dataset_status: string | null; dataset_resolution: string | null; trace: string | null;
};
export type Message = { id: number; ticket_id: string; role: "customer" | "ai" | "agent" | "system"; author: string; body: string; created_at: number; meta: string | null };

export async function nextTicketId(): Promise<string> {
  const r = await one<{ n: number }>("SELECT COUNT(*) n FROM tickets");
  return `TK-${String((r?.n ?? 0) + 1).padStart(5, "0")}`;
}

export function analysisColumns(a: Analysis) {
  return {
    topic: a.topic, category: a.category, category_conf: a.categoryConfidence, team: a.team, priority: a.priority.priority,
    priority_score: a.priority.score, sentiment: a.sentiment.label, sentiment_score: a.sentiment.score,
    ai_confidence: a.aiConfidence, kb_score: a.kb.score, kb_weight: a.kbWeight, kb_article_id: a.kb.article?.id ?? null, decision: a.decision,
    risk_level: a.risk.level, risk_reasons: JSON.stringify(a.risk.reasons), guardrail_flags: JSON.stringify([...a.input.flags, ...a.outputFlags]),
    model_tier: a.modelTier, summary: a.summary, suggested_reply: a.reply, trace: JSON.stringify({ steps: a.steps, reasons: a.decisionReasons, kb: a.kb.candidates, sentimentSignals: a.sentiment.signals, priority: a.priority, topTerms: a.topTerms, grounded: a.replyGrounded }),
  };
}

async function addMessage(ticketId: string, role: Message["role"], author: string, body: string, meta: unknown = null, at = Date.now()) {
  await run("INSERT INTO messages (ticket_id, role, author, body, created_at, meta) VALUES (?,?,?,?,?,?)", [ticketId, role, author, body, at, meta ? JSON.stringify(meta) : null]);
}

/** Aplica a decisão do gate: AUTO responde ao cliente; SUGGEST/HUMAN deixa rascunho para o agente. */
async function applyDecision(id: string, a: Analysis, question: string, isFollowUp: boolean) {
  const now = Date.now();
  if (a.createGap && !isFollowUp) {
    const gap = await registerGap(question, id, a.topic, a.category, a.kb.score);
    await logEvent(id, "knowledge_gap", gap);
  }
  if (!a.input.allowed) await logEvent(id, "guardrail_input_block", a.input.flags);
  if (a.frustration) await logEvent(id, "frustration_detected", { score: a.sentiment.score });

  if (a.decision === "auto" && a.reply) {
    await addMessage(id, "ai", "AI Agent", a.reply, { kb: a.kb.article?.id, grounded: a.replyGrounded, tier: a.modelTier });
    await run("UPDATE tickets SET status='pending', assignee='AI Agent', automated=1, first_response_at=COALESCE(first_response_at, ?), updated_at=? WHERE id=?", [now, now, id]);
    if (a.kb.article) await run("UPDATE kb_articles SET uses=uses+1 WHERE id=?", [a.kb.article.id]);
    await logEvent(id, "ai_auto_reply", { confidence: a.aiConfidence });
  } else if (a.decision === "suggest") {
    await addMessage(id, "system", "AI Support OS", "Resposta sugerida pela IA aguardando aprovação de um agente.", { decision: "suggest" });
    // Primeira resposta imediata ao cliente (FRT ~0s) sem comprometer: confirma recebimento.
    if (!isFollowUp) await addMessage(id, "ai", "AI Agent", a.lang === "pt" ? "Recebemos sua mensagem! Já estou preparando a resposta com um especialista — em instantes você recebe o retorno aqui." : "We got your message! I'm preparing the answer with a specialist — you'll hear back here shortly.");
    await run("UPDATE tickets SET status='open', assignee='Fila: ' || team, first_response_at=COALESCE(first_response_at, ?), updated_at=? WHERE id=?", [now, now, id]);
  } else {
    const why = a.decisionReasons.join(" · ");
    await addMessage(id, "system", "AI Support OS", `Escalado para humano (upstream): ${why}`, { decision: "human" });
    await addMessage(id, "ai", "AI Agent", a.reply ?? "", { handoff: true });
    await run("UPDATE tickets SET status='escalated', assignee='Fila: ' || team, first_response_at=COALESCE(first_response_at, ?), updated_at=? WHERE id=?", [now, now, id]);
    await logEvent(id, "escalated", { reasons: a.decisionReasons, by: "ai" });
  }
}

export async function createPortalTicket(input: { name: string; email: string; message: string; channel?: string; product?: string }) {
  const a = await runPipeline(input.message, { customerName: input.name });
  const id = await nextTicketId();
  const token = crypto.randomBytes(12).toString("hex");
  const now = Date.now();
  const c = analysisColumns(a);
  const subject = input.message.split(/[.!?\n]/)[0].slice(0, 80);
  await run(
    `INSERT INTO tickets (id, source, customer_name, customer_email, channel, product, subject, created_at, updated_at, status, assignee, portal_token,
      topic, category, category_conf, team, priority, priority_score, sentiment, sentiment_score, ai_confidence, kb_score, kb_weight, kb_article_id,
      decision, risk_level, risk_reasons, guardrail_flags, model_tier, summary, suggested_reply, trace)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?)`,
    [id, "portal", input.name, input.email, input.channel ?? "Chat", input.product ?? null, subject, now, now, "new", "AI Agent", token,
      c.topic, c.category, c.category_conf, c.team, c.priority, c.priority_score, c.sentiment, c.sentiment_score, c.ai_confidence, c.kb_score, c.kb_weight, c.kb_article_id,
      c.decision, c.risk_level, c.risk_reasons, c.guardrail_flags, c.model_tier, c.summary, c.suggested_reply, c.trace],
  );
  await addMessage(id, "customer", input.name, a.input.sanitized, { sentiment: a.sentiment.score }, now);
  await applyDecision(id, a, a.input.sanitized, false);
  return { id, token, analysis: a };
}

const ACK = /\b(funcionou|resolveu|resolvido|deu certo|consegui|obrigad[oa]|valeu|worked|solved|fixed|thanks|thank you)\b/i;
const NOT_ACK = /\b(não|nao|not|didn'?t|doesn'?t|ainda|still|mas|but)\b/i;
export function isResolutionAck(text: string) {
  return text.length < 120 && ACK.test(text) && !NOT_ACK.test(text);
}
function humanOwnedTicket(t: Ticket) {
  return t.status === "escalated" || (t.assignee !== "AI Agent" && !t.assignee.startsWith("Fila"));
}

/** Nova mensagem do cliente em um ticket existente: reavalia (inclui tendência de sentimento). */
export async function customerReply(ticketId: string, body: string) {
  const t = await getTicket(ticketId);
  if (!t) throw new Error("ticket not found");
  const prev = await all<{ meta: string }>("SELECT meta FROM messages WHERE ticket_id=? AND role='customer' ORDER BY id", [ticketId]);
  const scores = prev.map((m) => (m.meta ? JSON.parse(m.meta).sentiment : null)).filter((s): s is number => typeof s === "number");
  const a = await runPipeline(body, { customerName: t.customer_name, previousSentiment: scores });
  await addMessage(ticketId, "customer", t.customer_name, a.input.sanitized, { sentiment: a.sentiment.score });
  const c = analysisColumns(a);
  // Humano já está no controle? IA só atualiza os insights e sugere — não responde.
  if (isResolutionAck(body) && !humanOwnedTicket(t)) {
    await addMessage(ticketId, "ai", "AI Agent", a.lang === "pt"
      ? "Que ótimo! Fico feliz em ajudar. Pode avaliar sua experiência abaixo? Leva 5 segundos."
      : "Great! Happy to help. Could you rate your experience below? It takes 5 seconds.");
    await run("UPDATE tickets SET status='resolved', resolved_at=?, updated_at=? WHERE id=?", [Date.now(), Date.now(), ticketId]);
    await logEvent(ticketId, "resolved", { by: "ai", automated: t.automated });
    return a;
  }
  const humanOwned = humanOwnedTicket(t);
  await run(
    `UPDATE tickets SET sentiment=?, sentiment_score=?, priority=CASE WHEN ?>priority_score THEN ? ELSE priority END,
      priority_score=MAX(priority_score, ?), suggested_reply=?, trace=?, risk_level=?, risk_reasons=?, ai_confidence=?, kb_score=?, kb_weight=?, kb_article_id=?, decision=?, updated_at=? WHERE id=?`,
    [c.sentiment, c.sentiment_score, c.priority_score, c.priority, c.priority_score, c.suggested_reply, c.trace, c.risk_level, c.risk_reasons, c.ai_confidence, c.kb_score, c.kb_weight, c.kb_article_id, c.decision, Date.now(), ticketId],
  );
  if (humanOwned) {
    if (a.frustration) await logEvent(ticketId, "frustration_detected", { score: a.sentiment.score });
    await run("UPDATE tickets SET status=CASE WHEN status='pending' THEN 'open' ELSE status END WHERE id=?", [ticketId]);
    return a;
  }
  await applyDecision(ticketId, a, a.input.sanitized, true);
  return a;
}

export async function getTicket(id: string) {
  return one<Ticket>("SELECT * FROM tickets WHERE id=?", [id]);
}
export async function getTicketByToken(token: string) {
  return one<Ticket>("SELECT * FROM tickets WHERE portal_token=?", [token]);
}
export async function getMessages(id: string) {
  return all<Message>("SELECT * FROM messages WHERE ticket_id=? ORDER BY created_at, id", [id]);
}

/** Feedback loop: accepted / edited / rejected viram AI Acceptance Rate. */
export async function agentSend(ticketId: string, agent: string, body: string, feedback: "accepted" | "edited" | "manual") {
  const now = Date.now();
  await addMessage(ticketId, "agent", agent, body);
  await run("UPDATE tickets SET status='pending', assignee=?, first_response_at=COALESCE(first_response_at, ?), updated_at=? WHERE id=?", [agent, now, now, ticketId]);
  if (feedback !== "manual") await logEvent(ticketId, `reply_${feedback}`, { agent });
}

export async function rejectSuggestion(ticketId: string, agent: string, reason: string) {
  await logEvent(ticketId, "reply_rejected", { agent, reason });
  await run("UPDATE tickets SET suggested_reply=NULL, updated_at=? WHERE id=?", [Date.now(), ticketId]);
}

/** Upstream manual: agente/gestor puxa o ticket da IA. */
export async function escalate(ticketId: string, agent: string, reason: string) {
  await addMessage(ticketId, "system", "AI Support OS", `${agent} assumiu o atendimento (upstream): ${reason}`);
  await run("UPDATE tickets SET status='escalated', assignee=?, updated_at=? WHERE id=?", [agent, Date.now(), ticketId]);
  await logEvent(ticketId, "escalated", { reasons: [reason], by: agent });
}

/** Downstream: humano resolve a parte crítica e devolve para a IA concluir e pedir CSAT. */
export async function returnToAi(ticketId: string, agent: string, note: string) {
  const t = await getTicket(ticketId);
  if (!t) return;
  const pt = !/^(hi|hello|my|i |the )/i.test(t.summary ?? "");
  await addMessage(ticketId, "system", "AI Support OS", `${agent} devolveu o atendimento para a IA (downstream). Nota: ${note}`);
  await addMessage(ticketId, "ai", "AI Agent", pt
    ? `Tudo certo! ${note ? `Confirmando: ${note}. ` : ""}Seu atendimento foi concluído. Pode avaliar sua experiência abaixo? Leva 5 segundos.`
    : `All set! ${note ? `To confirm: ${note}. ` : ""}Your request is complete. Could you rate your experience below? It takes 5 seconds.`);
  await run("UPDATE tickets SET status='resolved', assignee='AI Agent', resolved_at=?, updated_at=? WHERE id=?", [Date.now(), Date.now(), ticketId]);
  await logEvent(ticketId, "returned_to_ai", { agent, note });
}

export async function resolveTicket(ticketId: string, by: string) {
  await run("UPDATE tickets SET status='resolved', resolved_at=?, updated_at=? WHERE id=?", [Date.now(), Date.now(), ticketId]);
  await logEvent(ticketId, "resolved", { by });
}

export async function submitCsat(ticketId: string, score: number, comment: string) {
  const t = await getTicket(ticketId);
  if (!t) return;
  await run("UPDATE tickets SET csat=?, csat_comment=?, status='closed', updated_at=? WHERE id=?", [score, comment || null, Date.now(), ticketId]);
  await logEvent(ticketId, "csat", { score, comment, automated: t.automated, category: t.category, final_sentiment: t.sentiment_score, resolution_ms: t.resolved_at ? t.resolved_at - t.created_at : null });
}
