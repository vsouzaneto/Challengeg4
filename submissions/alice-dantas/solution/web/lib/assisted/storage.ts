// As respostas ficam só neste navegador (ADR-010): nada vai ao servidor. Molde do `rankio.vendedor`: tudo em try/catch,
// porque janela privada ou dados bloqueados fazem o acesso falhar.
import {
  ASSESSMENT_VERSION, DIMENSIONS, POLICY_VERSION, type Answers, type Assessment, type ConflictCode,
} from "./model";
import { isOption } from "./policy";

const KEY = "rankio.avaliacoes.v1";
const CONFLICTS: ConflictCode[] = ["no_contact_with_action", "no_contact_with_need"];

export type Store = {
  /** vendedor → oportunidade → avaliação */
  assessments: Record<string, Record<string, Assessment>>;
  /** vendedor → conjunto de oportunidades → ordem escolhida pelo vendedor */
  orders: Record<string, Record<string, string[]>>;
};

const EMPTY: Store = { assessments: {}, orders: {} };

/** A chave de um conjunto de oportunidades, igual qualquer que seja a ordem em que foram marcadas. */
export const setKey = (ids: string[]): string => [...ids].sort().join("|");

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

function cleanAssessment(id: string, raw: unknown): Assessment | null {
  if (!isRecord(raw) || !isRecord(raw.answers)) return null;
  const answers: Answers = {};
  for (const dimension of DIMENSIONS) {
    // Avaliações antigas tinham "com data": a data se perdeu, então viram "sem prazo".
    const value = dimension === "progress" && raw.answers[dimension] === "dated" ? "undated" : raw.answers[dimension];
    if (isOption(dimension, value)) (answers as Record<string, unknown>)[dimension] = value;
  }
  const confirmed = Array.isArray(raw.confirmedConflicts)
    ? raw.confirmedConflicts.filter((code): code is ConflictCode => CONFLICTS.includes(code as ConflictCode)) : [];
  return {
    opportunityId: id, answers, confirmedConflicts: confirmed,
    assessedAt: typeof raw.assessedAt === "string" ? raw.assessedAt : new Date(0).toISOString(),
    policyVersion: typeof raw.policyVersion === "string" ? raw.policyVersion : POLICY_VERSION,
    version: typeof raw.version === "number" ? raw.version : ASSESSMENT_VERSION,
  };
}

export function readStore(): Store {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return structuredClone(EMPTY);
    const parsed: unknown = JSON.parse(raw);
    if (!isRecord(parsed)) return structuredClone(EMPTY);
    const store: Store = structuredClone(EMPTY);
    if (isRecord(parsed.assessments)) {
      for (const [seller, byId] of Object.entries(parsed.assessments)) {
        if (!isRecord(byId)) continue;
        for (const [id, value] of Object.entries(byId)) {
          const clean = cleanAssessment(id, value);
          if (clean) (store.assessments[seller] ??= {})[id] = clean;
        }
      }
    }
    if (isRecord(parsed.orders)) {
      for (const [seller, bySet] of Object.entries(parsed.orders)) {
        if (!isRecord(bySet)) continue;
        for (const [key, ids] of Object.entries(bySet)) {
          if (Array.isArray(ids) && ids.every((id) => typeof id === "string")) (store.orders[seller] ??= {})[key] = ids;
        }
      }
    }
    return store;
  } catch {
    return structuredClone(EMPTY);
  }
}

export function writeStore(store: Store): boolean {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(store));
    return true;
  } catch {
    return false; // sem armazenamento: a avaliação vale só até fechar a página
  }
}
