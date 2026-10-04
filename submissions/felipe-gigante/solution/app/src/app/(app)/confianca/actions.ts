"use server";
import { revalidatePath } from "next/cache";
import { requireUser } from "@/lib/auth";
import { all, db, logEvent } from "@/lib/db";
import { computeScore, decide, kbConfidenceOf, sanitizeGate, DEFAULT_GATE, type GateConfig } from "@/lib/ai/gate";
import { saveGateConfig } from "@/lib/ai/gate-store";
import { runEvals } from "@/lib/evals";

/** Testa uma configuração no golden set SEM salvar — o gestor vê o risco antes de aplicar. */
export async function testGateAction(input: Partial<GateConfig>) {
  await requireUser();
  const { metrics } = await runEvals({ gate: sanitizeGate(input), save: false });
  return metrics;
}

/** Salva, roda os evals (registrados no histórico) e reprocessa as decisões dos tickets do histórico. */
export async function saveGateAction(input: Partial<GateConfig> | "default") {
  const u = await requireUser();
  if (u.role !== "manager") return { error: "Apenas gestores podem alterar o gate." };
  const cfg = await saveGateConfig(input === "default" ? DEFAULT_GATE : input);
  const rows = await all<{ id: string; category_conf: number; kb_score: number; kb_weight: number; sentiment: string; risk_level: string; blocked: number }>(
    `SELECT id, category_conf, kb_score, COALESCE(kb_weight,1) kb_weight, sentiment, risk_level, guardrail_flags LIKE '%"severity":"block"%' blocked FROM tickets WHERE source='dataset'`);
  const stmts = rows.map((r) => {
    const s = computeScore(cfg, r.category_conf, kbConfidenceOf(cfg, r.kb_score, r.kb_weight), r.sentiment);
    const d = decide(cfg, { score: s.score, riskLevel: r.risk_level, mandatoryHuman: r.risk_level === "HIGH", inputAllowed: !r.blocked });
    return { sql: "UPDATE tickets SET ai_confidence=?, decision=? WHERE id=?", args: [s.score, d, r.id] };
  });
  const c = await db();
  for (let i = 0; i < stmts.length; i += 1000) await c.batch(stmts.slice(i, i + 1000), "write");
  await logEvent(null, "gate_config_changed", { by: u.name, cfg });
  const { metrics } = await runEvals({ gate: cfg });
  revalidatePath("/", "layout");
  return { ok: true, reprocessed: rows.length, metrics };
}
