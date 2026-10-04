// Eval runner (PRD §33–36). Roda o pipeline REAL sobre dois golden sets:
// 1. Classificação: 480 tickets do conjunto de TESTE do Dataset 2 (nunca vistos no treino).
// 2. Comportamental: casos rotulados à mão — segurança, escalonamento, RAG, gaps e prioridade.
// Cada execução fica salva → regression testing ao mudar prompt, threshold, KB ou modelo.
import goldenCls from "../../data/generated/golden_classification.json";
import goldenBeh from "../../data/golden_behavior.json";
import { classify, CLASSIFIER_VERSION } from "./ai/classifier";
import { runPipeline } from "./ai/pipeline";
import type { GateConfig } from "./ai/gate";
import { getGateConfig } from "./ai/gate-store";
import { all, run } from "./db";

export const pipelineVersion = (g: GateConfig) =>
  `pipeline-v3 · ${CLASSIFIER_VERSION} · gate ${g.suggestThreshold}/${g.autoThreshold} · w ${g.wClassifier} · kb ${g.kbStrong}/${g.kbGap}`;

type Beh = { input: string; suite: string; should_escalate: boolean | null; expect_block?: boolean; expect_pii?: boolean; expect_gap?: boolean; expected_topic?: string; expected_priority?: string };
const PRI = ["Low", "Medium", "High", "Critical"];

export type EvalResult = Awaited<ReturnType<typeof runEvals>>;

export async function runEvals(opts: { useLlm?: boolean; gate?: GateConfig; save?: boolean } = {}) {
  const t0 = Date.now();
  const gate = opts.gate ?? (await getGateConfig());

  // 1. Classification eval
  const gc = goldenCls as { text: string; expected: string; python_pred: string }[];
  const labels = [...new Set(gc.map((g) => g.expected))].sort();
  let correct = 0, parity = 0;
  const per: Record<string, { tp: number; fp: number; fn: number }> = Object.fromEntries(labels.map((l) => [l, { tp: 0, fp: 0, fn: 0 }]));
  const clsErrors: { text: string; expected: string; predicted: string; confidence: number }[] = [];
  for (const g of gc) {
    const c = classify(g.text, { normalize: false });
    if (c.category === g.python_pred) parity++;
    if (c.category === g.expected) { correct++; per[g.expected].tp++; }
    else {
      per[g.expected].fn++; if (per[c.category]) per[c.category].fp++;
      if (clsErrors.length < 12) clsErrors.push({ text: g.text.slice(0, 140), expected: g.expected, predicted: c.category, confidence: c.confidence });
    }
  }
  const f1s = labels.map((l) => {
    const { tp, fp, fn } = per[l];
    const p = tp / (tp + fp || 1), r = tp / (tp + fn || 1);
    return { label: l, precision: p, recall: r, f1: (2 * p * r) / (p + r || 1) };
  });

  // 2. Behavioral eval
  const cases = goldenBeh as Beh[];
  const rows: { suite: string; input: string; pass: boolean; got: string; expected: string }[] = [];
  let escTP = 0, escFN = 0, escFP = 0, escTN = 0, unsafeAuto = 0;
  let blockTP = 0, blockN = 0, blockFP = 0, benignN = 0;
  let topicHit = 0, topicN = 0, groundSum = 0, groundN = 0, gapHit = 0, gapN = 0;
  let priExact = 0, priNear = 0, priN = 0;
  for (const c of cases) {
    const a = await runPipeline(c.input, { useLlm: opts.useLlm ?? false, gate });
    const escalated = a.decision === "human";
    const checks: [boolean, string, string][] = [];
    if (c.should_escalate !== null) {
      if (c.should_escalate && escalated) escTP++;
      if (c.should_escalate && !escalated) { escFN++; if (a.decision === "auto") unsafeAuto++; }
      if (!c.should_escalate && escalated) escFP++;
      if (!c.should_escalate && !escalated) escTN++;
      checks.push([c.should_escalate === escalated, `escalate=${escalated} (${a.decision})`, `escalate=${c.should_escalate}`]);
    }
    if (c.expect_block !== undefined) {
      const blocked = !a.input.allowed;
      if (c.expect_block) { blockN++; if (blocked) blockTP++; }
      checks.push([blocked === c.expect_block, `blocked=${blocked}`, `blocked=${c.expect_block}`]);
    } else if (c.suite !== "safety") { benignN++; if (!a.input.allowed) blockFP++; }
    if (c.expect_pii) checks.push([a.input.flags.some((f) => f.kind === "pii_masked"), `pii=${a.input.flags.some((f) => f.kind === "pii_masked")}`, "pii mascarado"]);
    if (c.expected_topic) {
      topicN++;
      const hit = a.kb.article?.topic === c.expected_topic && a.kbConfidence >= 0.6;
      if (hit) topicHit++;
      if (a.replyGrounded !== null) { groundSum += a.replyGrounded; groundN++; }
      checks.push([hit, `artigo=${a.kb.article?.topic ?? "—"} (${a.kb.score.toFixed(2)})`, `artigo=${c.expected_topic}`]);
    }
    if (c.expect_gap) { gapN++; if (a.createGap) gapHit++; checks.push([a.createGap, `gap=${a.createGap}`, "gap=true"]); }
    if (c.expected_priority) {
      priN++;
      const d = Math.abs(PRI.indexOf(a.priority.priority) - PRI.indexOf(c.expected_priority));
      if (d === 0) priExact++;
      if (d <= 1) priNear++;
      checks.push([d <= 1, `prioridade=${a.priority.priority}`, `prioridade=${c.expected_priority} (±1)`]);
    }
    rows.push({ suite: c.suite, input: c.input, pass: checks.every((x) => x[0]), got: checks.map((x) => x[1]).join(" · "), expected: checks.map((x) => x[2]).join(" · ") });
  }

  const metrics = {
    classification: { n: gc.length, accuracy: correct / gc.length, parityWithPython: parity / gc.length, macroF1: f1s.reduce((s, x) => s + x.f1, 0) / f1s.length },
    escalation: { recall: escTP / (escTP + escFN || 1), precision: escTP / (escTP + escFP || 1), unsafeAuto, n: escTP + escFN + escFP + escTN },
    safety: { detection: blockTP / (blockN || 1), falsePositiveRate: blockFP / (benignN || 1), n: blockN },
    rag: { retrievalHit: topicHit / (topicN || 1), groundedness: groundN ? groundSum / groundN : null, n: topicN },
    gaps: { detection: gapHit / (gapN || 1), n: gapN },
    priority: { exact: priExact / (priN || 1), withinOne: priNear / (priN || 1), n: priN },
    behavioral: { pass: rows.filter((r) => r.pass).length, n: rows.length },
    ms: Date.now() - t0,
    llm: opts.useLlm ?? false,
  };
  const details = { perClass: f1s, clsErrors, rows };
  if (opts.save !== false) await run("INSERT INTO eval_runs (created_at, version, metrics, details) VALUES (?,?,?,?)", [Date.now(), pipelineVersion(gate), JSON.stringify(metrics), JSON.stringify(details)]);
  return { metrics, details };
}

export async function evalHistory() {
  return all<{ id: number; created_at: number; version: string; metrics: string; details: string }>("SELECT * FROM eval_runs ORDER BY id DESC LIMIT 20");
}
