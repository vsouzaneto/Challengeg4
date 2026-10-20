// Política assistida v1 (ADR-010): função pura das respostas do vendedor. Mesmas respostas, mesmo resultado. Não toca na
// classificação nem na ordem oficial: devolve um resultado à parte, que a tela rotula como declarado pelo vendedor.
import {
  DIMENSIONS, OPTIONS, POINTS, UNKNOWN_LIMIT, WEIGHTS, type Assessment, type CategoryCode, type ConflictCode,
  type Dimension, type Note,
} from "./model";

export type Status = "incomplete" | "conflict" | "complete";

export type Evaluation = {
  opportunityId: string;
  status: Status;
  /** Pontos das respostas dadas; "Não sei" vale 0. */
  confirmed: number;
  /** Confirmados + o máximo das dimensões em "Não sei": até onde a pontuação pode ir se elas se confirmarem. */
  potential: number;
  breakdown: { dimension: Dimension; answer: string | null; points: number; weight: number }[];
  /** Dimensões respondidas com "Não sei". */
  unknown: Dimension[];
  /** Dimensões ainda sem resposta. */
  missing: Dimension[];
  /** Contradições que o vendedor ainda não confirmou. */
  conflicts: ConflictCode[];
  category: CategoryCode | null;
  notes: Note[];
  /** Quase tudo desconhecido: fica no bloco à parte, sem posição. */
  aside: boolean;
};

/** Respostas de "próxima ação" que dizem que existe uma ação combinada. */
const HAS_ACTION: string[] = ["within_7", "within_30", "later", "undated"];

export function conflictsOf(assessment: Assessment): ConflictCode[] {
  const { interest, progress, need } = assessment.answers;
  const found: ConflictCode[] = [];
  if (interest === "no_contact" && HAS_ACTION.includes(progress as string)) found.push("no_contact_with_action");
  if (interest === "no_contact" && need === "confirmed") found.push("no_contact_with_need");
  return found.filter((code) => !assessment.confirmedConflicts.includes(code));
}

/** Avalia uma oportunidade. `today` é a data dos dados (`meta.as_of`), não o relógio do computador. */
export function evaluate(assessment: Assessment, today: string): Evaluation {
  const { answers } = assessment;
  const breakdown = DIMENSIONS.map((dimension) => {
    const answer = answers[dimension] ?? null;
    const points = answer === null ? 0 : (POINTS[dimension] as Record<string, number>)[answer];
    return { dimension, answer, points, weight: WEIGHTS[dimension] };
  });
  const confirmed = breakdown.reduce((sum, row) => sum + row.points, 0);
  const unknown = breakdown.filter((row) => row.answer === "unknown").map((row) => row.dimension);
  const missing = breakdown.filter((row) => row.answer === null).map((row) => row.dimension);
  const potential = confirmed + unknown.reduce((sum, dimension) => sum + WEIGHTS[dimension], 0);
  const conflicts = conflictsOf(assessment);
  const status: Status = conflicts.length ? "conflict" : missing.length ? "incomplete" : "complete";
  const base = {
    opportunityId: assessment.opportunityId, status, confirmed, potential, breakdown, unknown, missing, conflicts,
  };

  if (status === "incomplete") return { ...base, category: null, notes: [], aside: false };

  const { interest, need, authority, progress } = answers;
  const notes: Note[] = [];
  let category: CategoryCode;
  if (status === "conflict") {
    category = "review_answers";
  } else if (progress === "within_7") {
    category = "commitment_due";
  } else if (progress === "undated") {
    category = "commitment_to_organize";
  } else if (progress === "within_30" || progress === "later") {
    // Depois da janela de 7 dias: não é urgente, a categoria vem das outras respostas.
    notes.push({ code: "future_commitment" });
    category = classify();
  } else {
    category = classify();
  }

  function classify(): CategoryCode {
    if (need === "confirmed" && interest === "replied" && progress === "none") return "define_continuity";
    if (need === "confirmed" && (authority === "no_access" || authority === "not_identified")) return "advance_qualification";
    if ((interest === "no_reply" || interest === "no_contact") && progress === "none") return "resume_or_reassess";
    if (unknown.length >= UNKNOWN_LIMIT) return "investigate_first";
    if (need === "none") return "qualify_need";
    return "advance_qualification";
  }

  if ((authority === "no_access" || authority === "not_identified") && category !== "advance_qualification") {
    notes.push({ code: "authority_gap" });
  }
  return { ...base, category, notes, aside: status === "complete" && unknown.length >= UNKNOWN_LIMIT };
}

export type Ranked = {
  evaluation: Evaluation;
  /** Posição na ordem sugerida; empatadas repartem a mesma posição, a menos que o vendedor tenha reordenado. */
  position: number;
  /** Outra oportunidade da lista tem os mesmos pontos confirmados. */
  tied: boolean;
  /** O vendedor mudou esta posição em relação à calculada. */
  manual: boolean;
};

export type Ranking = {
  ordered: Ranked[];
  /** Quase tudo desconhecido: sem posição. */
  aside: Evaluation[];
  /** Incompletas ou com contradição: ficam fora da ordem até serem concluídas. */
  pending: Evaluation[];
};

/** Ordena por pontos confirmados (maior primeiro). Pontos iguais ficam empatados, em ordem de ID só para a leitura.
 * `manualOrder` é a ordem escolhida pelo vendedor; só vale se cobrir exatamente as oportunidades ordenáveis. */
export function rank(evaluations: Evaluation[], manualOrder: string[] | null = null): Ranking {
  const eligible = evaluations.filter((e) => e.status === "complete" && !e.aside);
  const sorted = [...eligible].sort(
    (a, b) => b.confirmed - a.confirmed || a.opportunityId.localeCompare(b.opportunityId),
  );
  const computed: Ranked[] = sorted.map((evaluation, index) => {
    const first = sorted.findIndex((other) => other.confirmed === evaluation.confirmed);
    return {
      evaluation, position: first + 1, manual: false,
      tied: sorted.some((other, i) => i !== index && other.confirmed === evaluation.confirmed),
    };
  });
  const ids = sorted.map((e) => e.opportunityId);
  const valid = manualOrder && manualOrder.length === ids.length && ids.every((id) => manualOrder.includes(id));
  const ordered = valid
    ? manualOrder.map((id, index) => {
        const item = computed.find((c) => c.evaluation.opportunityId === id)!;
        return { evaluation: item.evaluation, position: index + 1, tied: false, manual: ids[index] !== id };
      })
    : computed;
  return {
    ordered,
    aside: evaluations.filter((e) => e.aside),
    pending: evaluations.filter((e) => e.status !== "complete"),
  };
}

/** Move um ID uma posição para cima (-1) ou para baixo (+1). */
export function move(order: string[], id: string, delta: -1 | 1): string[] {
  const index = order.indexOf(id);
  const target = index + delta;
  if (index < 0 || target < 0 || target >= order.length) return order;
  const next = [...order];
  [next[index], next[target]] = [next[target], next[index]];
  return next;
}

/** A pergunta e as respostas válidas de cada dimensão, para validar o que vem do navegador. */
export const isOption = (dimension: Dimension, value: unknown): boolean =>
  typeof value === "string" && (OPTIONS[dimension] as readonly string[]).includes(value);
