// Orquestrador do pipeline (PRD §13):
// Input Guardrail → Classificação → Sentimento → Risco → Prioridade → KB → Confidence Gate → Output Guardrail
// Cada etapa registra um passo no "trace", exibido na interface (explicabilidade para o agente e para o gestor).
import { classify, TEAM_BY_CATEGORY, CATEGORIES } from "./classifier";
import { analyzeSentiment, frustrationTrend, type Sentiment } from "./sentiment";
import { assessRisk, detectIntent, type Risk } from "./risk";
import { scorePriority, type PriorityResult } from "./priority";
import { retrieve, type Retrieval } from "./kb";
import { checkInput, checkOutput, SAFE_FALLBACK_EN, SAFE_FALLBACK_PT, type GuardrailFlag } from "./guardrails";
import { detectLanguage } from "./text";
import { llmAnalyze, llmAnswer, llmEnabled, FAST_MODEL, STRONG_MODEL } from "./llm";

// Thresholds e pesos do Confidence Gate são configuráveis em /confianca (ver gate.ts).
import { computeScore, decide, kbConfidenceOf, type GateConfig, type ScoreParts } from "./gate";
import { getGateConfig } from "./gate-store";

export type Decision = "auto" | "suggest" | "human";
export type Step = { name: string; status: "ok" | "warn" | "block" | "skip"; detail: string; ms: number };

export type Analysis = {
  lang: "pt" | "en";
  input: { allowed: boolean; sanitized: string; flags: GuardrailFlag[] };
  category: string;
  categoryConfidence: number;
  team: string;
  topTerms: string[];
  topic: string;
  sentiment: Sentiment;
  frustration: boolean;
  risk: Risk;
  priority: PriorityResult;
  kb: Retrieval;
  kbConfidence: number;
  kbWeight: number;
  aiConfidence: number;
  scoreParts: ScoreParts;
  gate: GateConfig;
  decision: Decision;
  decisionReasons: string[];
  createGap: boolean;
  reply: string | null; // resposta enviada (auto) ou sugerida (suggest/human)
  replyGrounded: number | null;
  outputFlags: GuardrailFlag[];
  summary: string;
  modelTier: string;
  steps: Step[];
};

type Ctx = {
  customerName?: string;
  previousSentiment?: number[];
  useLlm?: boolean;
  /** Campo estruturado do formulário (ex.: "Ticket Type" do Dataset 1) — sinal de risco declarado pelo cliente. */
  declaredType?: string;
  /** Sobrescreve a configuração salva (usado para testar uma config nos evals antes de salvar). */
  gate?: GateConfig;
  /** Assunto do ticket (linha de assunto do e-mail / campo do formulário). */
  subject?: string;
};

const firstName = (n?: string) => (n ? n.split(" ")[0] : "");

function compose(lang: "pt" | "en", name: string | undefined, title: string, body: string): string {
  const hi = lang === "pt" ? `Olá${name ? `, ${firstName(name)}` : ""}!` : `Hi${name ? ` ${firstName(name)}` : ""}!`;
  const intro = lang === "pt" ? `Sobre "${title}", veja como resolver:` : `About "${title}", here is how to fix it:`;
  const outro = lang === "pt"
    ? "Isso resolveu? Se não, é só responder aqui que eu chamo um especialista."
    : "Did this solve it? If not, just reply here and I'll bring in a specialist.";
  return `${hi} ${intro}\n\n${body}\n\n${outro}`;
}

export async function runPipeline(rawText: string, ctx: Ctx = {}): Promise<Analysis> {
  const steps: Step[] = [];
  const t = () => performance.now();
  const useLlm = ctx.useLlm !== false && llmEnabled();
  const cfg = ctx.gate ?? (await getGateConfig());
  let tier = "local";

  // 1. Input guardrail
  let t0 = t();
  const input = checkInput(rawText);
  const text = input.sanitized;
  const lang = detectLanguage(text);
  steps.push({
    name: "Input Guardrail",
    status: input.allowed ? (input.flags.length ? "warn" : "ok") : "block",
    detail: input.flags.length ? input.flags.map((f) => `${f.kind}: ${f.detail}`).join("; ") : "sem injeção, sem PII",
    ms: t() - t0,
  });

  // 2. Classificação (tier local → LLM se baixa confiança)
  t0 = t();
  const cls = classify(text);
  let category = cls.category, categoryConfidence = cls.confidence;
  let summary = text.split(/(?<=[.!?])\s/)[0].slice(0, 160);
  let llmSentiment: number | null = null;
  let clsDetail = `${category} (${(categoryConfidence * 100).toFixed(0)}%) · termos: ${cls.topTerms.join(", ") || "—"}`;
  if (useLlm && input.allowed && categoryConfidence < cfg.suggestThreshold) {
    const model = categoryConfidence < 0.4 ? STRONG_MODEL : FAST_MODEL;
    const llm = await llmAnalyze(text, CATEGORIES, model);
    if (llm) {
      tier = model === STRONG_MODEL ? "llm-strong" : "llm-fast";
      clsDetail += ` → cascata ${model}: ${llm.category} (${(llm.confidence * 100).toFixed(0)}%)`;
      if (llm.confidence > categoryConfidence) { category = llm.category; categoryConfidence = llm.confidence; }
      llmSentiment = llm.sentiment_score;
      if (llm.summary) summary = llm.summary;
    }
  }
  steps.push({ name: "Classificação", status: categoryConfidence >= cfg.suggestThreshold ? "ok" : "warn", detail: clsDetail, ms: t() - t0 });

  // 3. Sentimento + tendência
  t0 = t();
  const sentiment = analyzeSentiment(text);
  if (llmSentiment !== null) sentiment.score = Math.round((sentiment.score + llmSentiment) / 2);
  const trend = frustrationTrend([...(ctx.previousSentiment ?? []), sentiment.score]);
  steps.push({
    name: "Sentimento",
    status: sentiment.score < 45 || trend.dropping ? "warn" : "ok",
    detail: `${sentiment.label} (${sentiment.score}/100)${sentiment.signals.length ? " · " + sentiment.signals.join(", ") : ""}${trend.dropping ? " · ⚠ Customer frustration detected" : ""}`,
    ms: t() - t0,
  });

  // 4. Intenção + risco
  t0 = t();
  const riskText = ctx.subject ? `${ctx.subject}. ${text}` : text;
  const intent = ctx.subject ? detectIntent(ctx.subject) : detectIntent(text);
  const risk = assessRisk(riskText, sentiment.score, trend.dropping, ctx.declaredType);
  steps.push({
    name: "Risco",
    status: risk.level === "HIGH" ? "block" : risk.level === "MEDIUM" ? "warn" : "ok",
    detail: `${risk.level}${risk.reasons.length ? " · " + risk.reasons.join("; ") : ""} · intenção: ${intent.topic}`,
    ms: t() - t0,
  });

  // 5. Prioridade
  t0 = t();
  const priority = scorePriority(riskText, sentiment.score, risk.level);
  const b = priority.breakdown;
  steps.push({ name: "Prioridade", status: "ok", detail: `${priority.priority} (score ${priority.score} = sev ${b.severity} + urg ${b.urgency} + sent ${b.sentiment} + risco ${b.topic})`, ms: t() - t0 });

  // 6. Knowledge Base
  t0 = t();
  // E-mails longos trazem ruído: a busca usa assunto + início da mensagem.
  let kb = await retrieve(text.slice(0, 600));
  let kbConfidence = kbConfidenceOf(cfg, kb.score);
  if (ctx.subject) {
    // Assunto escolhido pelo cliente é sinal útil, mas sozinho não basta para resposta automática:
    // peso 0.8 → no máximo "sugestão" para o agente aprovar.
    const bySubject = await retrieve(ctx.subject);
    const subjConf = kbConfidenceOf(cfg, bySubject.score, 0.8);
    if (subjConf > kbConfidence) { kb = { ...bySubject, via: "subject" }; kbConfidence = subjConf; }
  }
  steps.push({
    name: "Knowledge Base",
    status: kbConfidence >= cfg.kbGap ? "ok" : "warn",
    detail: kb.article
      ? `${kb.article.title} · score ${kb.score.toFixed(2)} (similaridade ${kb.similarity.toFixed(2)} × cobertura ${(kb.coverage * 100).toFixed(0)}%) via ${kb.via === "question" ? "pergunta-exemplo" : kb.via === "subject" ? "assunto do formulário (peso 0.8)" : "documento"}${kb.missing.length && kbConfidence < cfg.kbGap ? ` · termos sem cobertura: ${kb.missing.join(", ")}` : ""}`
      : "nenhum artigo relevante",
    ms: t() - t0,
  });

  // 7. Confidence gate
  t0 = t();
  const scoreParts = computeScore(cfg, categoryConfidence, kbConfidence, sentiment.label);
  const aiConfidence = scoreParts.score;
  const pct = (v: number) => `${Math.round(v * 100)}%`;
  const reasons: string[] = [];
  let decision: Decision = decide(cfg, { score: aiConfidence, riskLevel: risk.level, mandatoryHuman: risk.mandatoryHuman, inputAllowed: input.allowed });
  if (!input.allowed) reasons.push("Guardrail de entrada bloqueou a mensagem");
  else if (risk.mandatoryHuman) reasons.push(...risk.reasons.map((r) => `Caso obrigatoriamente humano: ${r}`));
  else if (decision === "human") reasons.push(`Confiança ${pct(aiConfidence)} < mínimo ${pct(cfg.suggestThreshold)}`);
  else if (decision === "suggest") reasons.push(risk.level === "MEDIUM" ? `Risco médio (${risk.reasons.join("; ")}) — humano aprova` : `Confiança ${pct(aiConfidence)} entre ${pct(cfg.suggestThreshold)} e ${pct(cfg.autoThreshold)}`);
  else reasons.push(`Confiança ${pct(aiConfidence)} ≥ ${pct(cfg.autoThreshold)} e risco baixo`);
  const createGap = input.allowed && kbConfidence < cfg.kbGap && !risk.mandatoryHuman;
  if (createGap) reasons.push("Sem cobertura suficiente na KB → Knowledge Gap");
  steps.push({ name: "Confidence Gate", status: decision === "auto" ? "ok" : decision === "suggest" ? "warn" : "block", detail: `${decision.toUpperCase()} · score ${aiConfidence.toFixed(2)} = ${cfg.wClassifier.toFixed(2)}×classificador ${categoryConfidence.toFixed(2)} + ${(1 - cfg.wClassifier).toFixed(2)}×KB ${kbConfidence.toFixed(2)}${scoreParts.penalty ? ` − frustração ${scoreParts.penalty.toFixed(2)}` : ""} · ${reasons.join(" · ")}`, ms: t() - t0 });

  // 8. Geração de resposta + output guardrail
  t0 = t();
  let reply: string | null = null, replyGrounded: number | null = null;
  let outputFlags: GuardrailFlag[] = [];
  if (!input.allowed) {
    reply = lang === "pt"
      ? "Posso ajudar apenas com dúvidas de suporte sobre sua conta e nossos produtos. Um especialista vai revisar sua mensagem."
      : "I can only help with support questions about your account and our products. A specialist will review your message.";
    steps.push({ name: "Output Guardrail", status: "skip", detail: "resposta padrão de recusa", ms: t() - t0 });
  } else if (kb.article && kbConfidence >= cfg.kbGap) {
    const body = lang === "en" && kb.article.body_en ? kb.article.body_en : kb.article.body;
    let draft: string | null = null;
    if (useLlm) {
      draft = await llmAnswer(text, kb.article.title, body, lang, decision === "auto" ? FAST_MODEL : STRONG_MODEL);
      if (draft && tier === "local") tier = "llm-fast";
    }
    draft ??= compose(lang, ctx.customerName, kb.article.title, body);
    const out = checkOutput(draft, `${kb.article.title}\n${body}\n${ctx.customerName ?? ""} olá hi resolveu solve specialist especialista responder reply bring chamo aqui here veja como resolver about sobre`, lang, text);
    outputFlags = out.flags;
    replyGrounded = out.groundedness;
    if (out.ok) reply = out.text;
    else {
      reply = lang === "pt" ? SAFE_FALLBACK_PT : SAFE_FALLBACK_EN;
      if (decision === "auto") { decision = "suggest"; reasons.push("Output guardrail reprovou a resposta"); }
    }
    steps.push({
      name: "Output Guardrail",
      status: out.ok ? (out.flags.length ? "warn" : "ok") : "block",
      detail: `groundedness ${(out.groundedness * 100).toFixed(0)}%${out.flags.length ? " · " + out.flags.map((f) => f.detail).join("; ") : ""}`,
      ms: t() - t0,
    });
  } else {
    reply = lang === "pt" ? SAFE_FALLBACK_PT : SAFE_FALLBACK_EN;
    steps.push({ name: "Output Guardrail", status: "skip", detail: "sem suporte documental → não inventa resposta", ms: t() - t0 });
  }

  return {
    lang, input: { allowed: input.allowed, sanitized: text, flags: input.flags },
    category, categoryConfidence, team: TEAM_BY_CATEGORY[category] ?? "General Support", topTerms: cls.topTerms,
    topic: intent.topic !== "Other" ? intent.topic : kb.article?.topic && kbConfidence >= cfg.kbGap ? kb.article.topic : "Other",
    sentiment, frustration: trend.dropping, risk, priority, kb, kbConfidence, kbWeight: kb.via === "subject" ? 0.8 : 1, aiConfidence, scoreParts, gate: cfg,
    decision, decisionReasons: reasons, createGap, reply, replyGrounded, outputFlags, summary, modelTier: tier, steps,
  };
}
