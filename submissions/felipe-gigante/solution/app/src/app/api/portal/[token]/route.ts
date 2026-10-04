import { getMessages, getTicketByToken } from "@/lib/tickets";

export const dynamic = "force-dynamic";

// Polling do widget do cliente. Só expõe o que o cliente pode ver (sem notas internas/system).
export async function GET(_: Request, ctx: { params: Promise<{ token: string }> }) {
  const { token } = await ctx.params;
  const t = await getTicketByToken(token);
  if (!t) return Response.json({ error: "not found" }, { status: 404 });
  const msgs = (await getMessages(t.id)).filter((m) => m.role !== "system");
  return Response.json({
    ticket: { id: t.id, status: t.status, csat: t.csat, subject: t.subject, assignee: t.assignee.startsWith("Fila") ? "Especialista" : t.assignee },
    messages: msgs.map((m) => ({ id: m.id, role: m.role, author: m.role === "agent" ? m.author : m.role === "ai" ? "Assistente G4" : m.author, body: m.body, at: m.created_at })),
    insight: { decision: t.decision, confidence: t.ai_confidence, category: t.category, priority: t.priority, sentiment: t.sentiment, sentimentScore: t.sentiment_score, risk: t.risk_level, tier: t.model_tier, trace: t.trace ? JSON.parse(t.trace) : null },
  });
}
