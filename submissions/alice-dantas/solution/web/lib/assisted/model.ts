// Priorização assistida (ADR-010): as sete perguntas, os pesos e os pontos de cada resposta. Tudo aqui é hipótese
// declarada do desenho, não evidência do backtest: mudar um peso é mudar este arquivo e `POLICY_VERSION`.

export const POLICY_VERSION = "assisted-points-v1";
/** Versão do questionário gravado no navegador. */
export const ASSESSMENT_VERSION = 1;
/** Ação combinada para os próximos 7 dias conta como compromisso a cumprir. */
export const WINDOW_DAYS = 7;
/** Com tantas respostas "Não sei" (de 7), a oportunidade vai para o bloco à parte, sem posição. */
export const UNKNOWN_LIMIT = 4;
export const MIN_SET = 2;
export const MAX_SET = 5;

/** Na ordem do questionário. */
export const DIMENSIONS = ["interest", "timing", "need", "urgency", "budget", "authority", "progress"] as const;
export type Dimension = (typeof DIMENSIONS)[number];

/** As respostas de cada pergunta, da mais favorável para a menos; "unknown" é sempre a última. */
export const OPTIONS = {
  interest: ["replied", "no_reply", "no_contact", "unknown"],
  timing: ["within_30", "within_90", "later", "no_forecast", "not_discussed", "unknown"],
  need: ["confirmed", "investigating", "none", "unknown"],
  urgency: ["concrete", "possible", "none", "unknown"],
  budget: ["confirmed", "needs_approval", "none", "unknown"],
  authority: ["access", "no_access", "not_identified", "unknown"],
  progress: ["within_7", "within_30", "later", "undated", "none", "unknown"],
} as const;
export type AnswerOf<D extends Dimension> = (typeof OPTIONS)[D][number];
export type Answers = { [D in Dimension]?: AnswerOf<D> };

/** Peso máximo de cada dimensão; somam 100. */
export const WEIGHTS: Record<Dimension, number> = {
  interest: 20, timing: 20, need: 15, urgency: 15, budget: 15, authority: 10, progress: 5,
};

/** "Não sei" vale 0 ponto confirmado, mas não é um "não": a tela mostra o potencial que ele ainda deixa em aberto. */
export const POINTS: { [D in Dimension]: Record<AnswerOf<D>, number> } = {
  interest: { replied: 20, no_reply: 0, no_contact: 0, unknown: 0 },
  timing: { within_30: 20, within_90: 12, later: 4, no_forecast: 0, not_discussed: 0, unknown: 0 },
  need: { confirmed: 15, investigating: 7, none: 0, unknown: 0 },
  urgency: { concrete: 15, possible: 7, none: 0, unknown: 0 },
  budget: { confirmed: 15, needs_approval: 7, none: 0, unknown: 0 },
  authority: { access: 10, no_access: 5, not_identified: 0, unknown: 0 },
  progress: { within_7: 5, within_30: 5, later: 4, undated: 3, none: 0, unknown: 0 },
};

export type ConflictCode = "no_contact_with_action" | "no_contact_with_need";

export type CategoryCode =
  | "review_answers" | "commitment_due" | "commitment_to_organize" | "define_continuity"
  | "advance_qualification" | "resume_or_reassess" | "investigate_first" | "qualify_need";

export type NoteCode = "future_commitment" | "authority_gap";
export type Note = { code: NoteCode };

/** O que o vendedor declarou sobre uma oportunidade (é o que fica no navegador). */
export type Assessment = {
  opportunityId: string;
  answers: Answers;
  /** Contradições que o vendedor viu e disse estarem corretas. */
  confirmedConflicts: ConflictCode[];
  assessedAt: string;
  policyVersion: string;
  version: number;
};

export function emptyAssessment(opportunityId: string, now: Date = new Date()): Assessment {
  return {
    opportunityId, answers: {}, confirmedConflicts: [], assessedAt: now.toISOString(),
    policyVersion: POLICY_VERSION, version: ASSESSMENT_VERSION,
  };
}
