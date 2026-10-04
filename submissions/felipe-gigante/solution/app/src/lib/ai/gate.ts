// Confidence Gate configurável (PRD §18 e §51).
// Funções puras: o mesmo cálculo roda no pipeline, na simulação da página /confianca
// (no navegador) e no reprocessamento do histórico — por isso este arquivo não importa o banco.

export type GateConfig = {
  /** Score ≥ este valor e risco baixo → IA responde sozinha (AUTO). */
  autoThreshold: number;
  /** Score ≥ este valor → resposta sugerida para humano aprovar. Abaixo → HUMANO. */
  suggestThreshold: number;
  /** Peso do classificador no score (o peso da KB é 1 − este valor). */
  wClassifier: number;
  /** Penalidade aplicada quando o cliente está frustrado. */
  frustrationPenalty: number;
  /** Similaridade da KB considerada "cobertura total" (kbConfidence = score / kbStrong). */
  kbStrong: number;
  /** kbConfidence abaixo disso → não responde com a KB e registra Knowledge Gap. */
  kbGap: number;
};

// Valores calibrados: ≥0,85 → 97,3% de acurácia do classificador (validação do Dataset 2);
// pesos/KB ajustados até o golden set comportamental ter 0 automações inseguras.
export const DEFAULT_GATE: GateConfig = {
  autoThreshold: 0.85,
  suggestThreshold: 0.6,
  wClassifier: 0.25,
  frustrationPenalty: 0.1,
  kbStrong: 0.45,
  kbGap: 0.6,
};

export const GATE_LIMITS: Record<keyof GateConfig, { min: number; max: number; step: number; label: string; help: string }> = {
  autoThreshold: { min: 0.5, max: 0.99, step: 0.01, label: "Threshold máximo (AUTO)", help: "Acima disso, e com risco baixo, a IA responde sem humano." },
  suggestThreshold: { min: 0.2, max: 0.95, step: 0.01, label: "Threshold mínimo (SUGESTÃO)", help: "Entre o mínimo e o máximo, a IA só sugere. Abaixo do mínimo, vai para humano." },
  wClassifier: { min: 0, max: 1, step: 0.05, label: "Peso do classificador", help: "Quanto a certeza sobre a categoria pesa. O restante é o peso da Knowledge Base." },
  frustrationPenalty: { min: 0, max: 0.4, step: 0.01, label: "Penalidade por frustração", help: "Desconto no score quando o cliente está frustrado — evita robô insistente." },
  kbStrong: { min: 0.2, max: 0.9, step: 0.01, label: "Similaridade de cobertura total da KB", help: "Similaridade a partir da qual a KB conta como 100% coberta. Maior = mais exigente." },
  kbGap: { min: 0.2, max: 0.95, step: 0.01, label: "Mínimo de KB para responder", help: "Abaixo disso a IA não usa a KB para responder e registra um Knowledge Gap." },
};

export function sanitizeGate(input: Partial<GateConfig>): GateConfig {
  const c = { ...DEFAULT_GATE } as GateConfig;
  for (const k of Object.keys(GATE_LIMITS) as (keyof GateConfig)[]) {
    const v = Number(input[k]);
    if (Number.isFinite(v)) c[k] = Math.min(GATE_LIMITS[k].max, Math.max(GATE_LIMITS[k].min, v));
  }
  if (c.suggestThreshold > c.autoThreshold) c.suggestThreshold = c.autoThreshold;
  return c;
}

/** weight < 1 quando a KB foi encontrada só pelo assunto do formulário (sinal mais fraco). */
export const kbConfidenceOf = (cfg: GateConfig, kbScore: number, weight = 1) => weight * Math.min(1, kbScore / cfg.kbStrong);

export type ScoreParts = { classifier: number; kb: number; penalty: number; score: number; kbConfidence: number };

/** score = wClassifier·confiança_classificador + (1 − wClassifier)·confiança_KB − penalidade_frustração */
export function computeScore(cfg: GateConfig, categoryConfidence: number, kbConfidence: number, sentimentLabel: string): ScoreParts {
  const classifier = cfg.wClassifier * categoryConfidence;
  const kb = (1 - cfg.wClassifier) * kbConfidence;
  const penalty = sentimentLabel === "Frustrated" ? cfg.frustrationPenalty : 0;
  return { classifier, kb, penalty, score: Math.max(0, Math.min(1, classifier + kb - penalty)), kbConfidence };
}

export type GateInput = { score: number; riskLevel: string; mandatoryHuman: boolean; inputAllowed: boolean };
export type GateDecision = "auto" | "suggest" | "human";

export function decide(cfg: GateConfig, g: GateInput): GateDecision {
  if (!g.inputAllowed || g.mandatoryHuman) return "human";
  if (g.score < cfg.suggestThreshold) return "human";
  if (g.score < cfg.autoThreshold || g.riskLevel === "MEDIUM") return "suggest";
  return "auto";
}
