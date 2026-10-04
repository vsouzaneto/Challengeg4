"use server";
import { revalidatePath } from "next/cache";
import { requireUser } from "@/lib/auth";
import { run, one, logEvent } from "@/lib/db";
import { invalidateKbCache } from "@/lib/ai/kb";
import { runPipeline } from "@/lib/ai/pipeline";

/** Fecha o ciclo: gap pendente → artigo publicado. As variações da pergunta viram perguntas-exemplo. */
export async function resolveGapAction(gapId: number, form: { title: string; body: string; questions: string; topic: string }) {
  const u = await requireUser();
  const now = Date.now();
  const r = await run(
    "INSERT INTO kb_articles (title, body, body_en, questions, tags, topic, source, uses, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
    [form.title, form.body, "", form.questions, form.title.toLowerCase(), form.topic || null, "gap", 0, now, now]);
  await run("UPDATE kb_gaps SET status='resolved', article_id=?, updated_at=? WHERE id=?", [Number(r.lastInsertRowid), now, gapId]);
  await logEvent(null, "gap_resolved", { gapId, articleId: Number(r.lastInsertRowid), by: u.name });
  invalidateKbCache();
  revalidatePath("/knowledge");
}

export async function dismissGapAction(gapId: number) {
  await requireUser();
  await run("UPDATE kb_gaps SET status='dismissed', updated_at=? WHERE id=?", [Date.now(), gapId]);
  revalidatePath("/knowledge");
}

export async function createArticleAction(form: { title: string; body: string; questions: string; topic: string }) {
  await requireUser();
  const now = Date.now();
  await run("INSERT INTO kb_articles (title, body, body_en, questions, tags, topic, source, uses, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
    [form.title, form.body, "", form.questions, form.title.toLowerCase(), form.topic || null, "manual", 0, now, now]);
  invalidateKbCache();
  revalidatePath("/knowledge");
}

export async function deleteArticleAction(id: number) {
  await requireUser();
  const a = await one<{ source: string }>("SELECT source FROM kb_articles WHERE id=?", [id]);
  if (!a) return;
  await run("DELETE FROM kb_articles WHERE id=?", [id]);
  await run("UPDATE kb_gaps SET status='pending', article_id=NULL WHERE article_id=?", [id]);
  invalidateKbCache();
  revalidatePath("/knowledge");
}

/** Simulador: o que o pipeline faria com esta pergunta agora? (não grava nada) */
export async function testQuestionAction(question: string) {
  await requireUser();
  const a = await runPipeline(question);
  return {
    decision: a.decision, confidence: a.aiConfidence, kbScore: a.kb.score, article: a.kb.article?.title ?? null,
    createGap: a.createGap, reply: a.reply, reasons: a.decisionReasons, steps: a.steps,
  };
}
