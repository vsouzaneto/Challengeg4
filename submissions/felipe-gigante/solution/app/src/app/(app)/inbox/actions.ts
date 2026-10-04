"use server";
import { revalidatePath } from "next/cache";
import { requireUser } from "@/lib/auth";
import { agentSend, escalate, rejectSuggestion, resolveTicket, returnToAi, getTicket, getMessages, analysisColumns } from "@/lib/tickets";
import { runPipeline } from "@/lib/ai/pipeline";
import { run, logEvent } from "@/lib/db";

export async function sendReplyAction(ticketId: string, body: string, suggested: string | null) {
  const u = await requireUser();
  if (!body.trim()) return;
  const feedback = suggested === null ? "manual" : body.trim() === suggested.trim() ? "accepted" : "edited";
  await agentSend(ticketId, u.name, body.trim(), feedback);
  revalidatePath("/inbox");
}

export async function rejectAction(ticketId: string, reason: string) {
  const u = await requireUser();
  await rejectSuggestion(ticketId, u.name, reason || "sem motivo");
  revalidatePath("/inbox");
}

export async function escalateAction(ticketId: string) {
  const u = await requireUser();
  await escalate(ticketId, u.name, "assumido manualmente pelo agente");
  revalidatePath("/inbox");
}

export async function returnToAiAction(ticketId: string, note: string) {
  const u = await requireUser();
  await returnToAi(ticketId, u.name, note.trim());
  revalidatePath("/inbox");
}

export async function resolveAction(ticketId: string) {
  const u = await requireUser();
  await resolveTicket(ticketId, u.name);
  revalidatePath("/inbox");
}

/** Regenerar: roda o pipeline de novo na última mensagem do cliente (com LLM, se configurado). */
export async function regenerateAction(ticketId: string) {
  await requireUser();
  const t = await getTicket(ticketId);
  if (!t) return;
  const msgs = await getMessages(ticketId);
  const last = [...msgs].reverse().find((m) => m.role === "customer");
  if (!last) return;
  const a = await runPipeline(last.body, { customerName: t.customer_name, subject: t.source === "dataset" ? t.subject : undefined, declaredType: t.dataset_type ?? undefined });
  const c = analysisColumns(a);
  await run("UPDATE tickets SET suggested_reply=?, trace=?, ai_confidence=?, kb_score=?, kb_weight=?, kb_article_id=?, model_tier=?, updated_at=? WHERE id=?",
    [c.suggested_reply, c.trace, c.ai_confidence, c.kb_score, c.kb_weight, c.kb_article_id, c.model_tier, Date.now(), ticketId]);
  await logEvent(ticketId, "reply_regenerated", { tier: a.modelTier });
  revalidatePath("/inbox");
}
