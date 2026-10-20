// Política assistida v1: pontos, faixa, categoria, conflito e ordem. Tudo puro e determinístico.
import { describe, expect, test } from "vitest";

import {
  DIMENSIONS, OPTIONS, POINTS, UNKNOWN_LIMIT, WEIGHTS, emptyAssessment, type Answers, type Assessment,
} from "@/lib/assisted/model";
import { conflictsOf, evaluate, move, rank } from "@/lib/assisted/policy";

const TODAY = "2017-12-31";
const NOW = new Date("2018-01-02T10:00:00Z");

const FULL: Answers = {
  interest: "replied", timing: "within_30", need: "confirmed", urgency: "concrete", budget: "confirmed",
  authority: "access", progress: "within_7",
};
const UNKNOWN: Answers = Object.fromEntries(DIMENSIONS.map((d) => [d, "unknown"])) as Answers;

const make = (id: string, answers: Answers, extra: Partial<Assessment> = {}): Assessment =>
  ({ ...emptyAssessment(id, NOW), answers, ...extra });
const run = (answers: Answers, extra: Partial<Assessment> = {}) => evaluate(make("X", answers, extra), TODAY);

describe("pesos e pontos", () => {
  test("os pesos somam 100 e a melhor resposta de cada pergunta vale o peso", () => {
    expect(DIMENSIONS.reduce((sum, d) => sum + WEIGHTS[d], 0)).toBe(100);
    for (const d of DIMENSIONS) expect(Math.max(...Object.values(POINTS[d])), d).toBe(WEIGHTS[d]);
  });
  test("toda pergunta oferece \"Não sei\" por último, e ele vale 0", () => {
    for (const d of DIMENSIONS) {
      expect(OPTIONS[d].at(-1), d).toBe("unknown");
      expect((POINTS[d] as Record<string, number>).unknown, d).toBe(0);
    }
  });
});

describe("pontos confirmados e faixa", () => {
  test("todas as melhores respostas somam 100", () => {
    const e = run(FULL);
    expect(e.confirmed).toBe(100);
    expect(e.potential).toBe(100);
  });
  test("\"Não sei\" não vira \"não\": os dois valem 0 confirmado, mas só ele deixa potencial", () => {
    const base: Answers = { ...FULL, budget: "none" };
    const unknown = run({ ...FULL, budget: "unknown" });
    const no = run(base);
    expect(unknown.confirmed).toBe(no.confirmed);
    expect(no.potential).toBe(no.confirmed);
    expect(unknown.potential).toBe(unknown.confirmed + WEIGHTS.budget);
    expect(unknown.unknown).toEqual(["budget"]);
  });
  test("o caso do I3KQNE9V: 47 confirmados, até 62", () => {
    const e = run({
      interest: "replied", timing: "unknown", need: "confirmed", urgency: "possible", budget: "none",
      authority: "no_access", progress: "none",
    });
    expect(e.confirmed).toBe(20 + 15 + 7 + 5);
    expect(e.potential).toBe(47 + 20);
  });
});

describe("avaliação incompleta, conflito e conclusão", () => {
  test("pergunta sem resposta mantém a avaliação incompleta e sem categoria", () => {
    const e = run({ interest: "replied" });
    expect(e.status).toBe("incomplete");
    expect(e.category).toBeNull();
    expect(e.missing).toHaveLength(6);
    expect(e.aside).toBe(false);
  });
  test("\"ainda sem contato\" com ação combinada é contradição: pede revisão, sem escolher um lado", () => {
    const answers: Answers = { ...FULL, interest: "no_contact", need: "investigating", progress: "undated" };
    expect(conflictsOf(make("X", answers))).toEqual(["no_contact_with_action"]);
    const e = run(answers);
    expect(e.status).toBe("conflict");
    expect(e.category).toBe("review_answers");
  });
  test("\"sem contato\" com necessidade confirmada também é contradição", () => {
    expect(run({ ...FULL, interest: "no_contact", progress: "none" }).conflicts).toEqual(["no_contact_with_need"]);
  });
  test("quando o vendedor confirma a contradição, ela deixa de bloquear", () => {
    const answers: Answers = { ...FULL, interest: "no_contact", progress: "undated" };
    const e = run(answers, { confirmedConflicts: ["no_contact_with_action", "no_contact_with_need"] });
    expect(e.status).toBe("complete");
    expect(e.category).toBe("commitment_to_organize");
  });
});

describe("categoria de trabalho", () => {
  const category = (answers: Answers, extra: Partial<Assessment> = {}) => run(answers, extra).category;
  const rest: Answers = { timing: "no_forecast", urgency: "none", budget: "none" };

  test("ação combinada para os próximos 7 dias: compromisso a cumprir", () => {
    expect(category(FULL)).toBe("commitment_due");
  });
  test("ação para depois dos 7 dias não é urgente: a categoria vem das outras respostas, com a nota de compromisso futuro", () => {
    for (const progress of ["within_30", "later"] as const) {
      const e = run({ ...FULL, authority: "no_access", progress });
      expect(e.category).toBe("advance_qualification");
      expect(e.notes).toContainEqual({ code: "future_commitment" });
    }
  });
  test("ação combinada sem prazo: compromisso a organizar", () => {
    expect(category({ ...FULL, progress: "undated" })).toBe("commitment_to_organize");
  });
  test("necessidade confirmada, interesse recente e nada combinado: definir continuidade", () => {
    expect(category({ ...FULL, ...rest, progress: "none", authority: "access" })).toBe("define_continuity");
  });
  test("a lacuna do decisor vira nota, sem tirar a categoria", () => {
    const e = run({ ...FULL, ...rest, progress: "none", authority: "no_access" });
    expect(e.category).toBe("define_continuity");
    expect(e.notes).toContainEqual({ code: "authority_gap" });
  });
  test("necessidade confirmada sem acesso ao decisor e sem interesse recente: avançar qualificação", () => {
    expect(category({ ...FULL, ...rest, interest: "no_reply", progress: "none", authority: "not_identified" }))
      .toBe("advance_qualification");
  });
  test("sem resposta e sem ação: retomar ou reavaliar", () => {
    expect(category({ ...FULL, ...rest, interest: "no_reply", need: "investigating", progress: "none" }))
      .toBe("resume_or_reassess");
  });
  test("necessidade não identificada: qualificar necessidade", () => {
    expect(category({ ...FULL, ...rest, need: "none", progress: "none", authority: "access" })).toBe("qualify_need");
  });
  test("necessidade em análise e o resto em andamento: avançar qualificação", () => {
    expect(category({ ...FULL, ...rest, need: "investigating", progress: "none", authority: "not_identified" }))
      .toBe("advance_qualification");
  });
});

describe("quase tudo desconhecido", () => {
  test("todas \"Não sei\": sem pontos, sem posição e sem rótulo de qualidade", () => {
    const e = run(UNKNOWN);
    expect(e.confirmed).toBe(0);
    expect(e.potential).toBe(100);
    expect(e.aside).toBe(true);
    expect(e.category).toBe("investigate_first");
    expect(rank([e]).ordered).toEqual([]);
    expect(rank([e]).aside).toEqual([e]);
  });
  test("o limite é de 4 de 7", () => {
    const some = (n: number): Answers => {
      const answers: Answers = { ...FULL, progress: "none", authority: "access", interest: "no_reply", need: "investigating" };
      DIMENSIONS.slice(0, n).forEach((d) => ((answers as Record<string, string>)[d] = "unknown"));
      return answers;
    };
    expect(run(some(UNKNOWN_LIMIT - 1)).aside).toBe(false);
    expect(run(some(UNKNOWN_LIMIT)).aside).toBe(true);
  });
});

describe("ordem por pontos", () => {
  const a = (id: string, answers: Answers, extra: Partial<Assessment> = {}) => evaluate(make(id, answers, extra), TODAY);
  const high = a("A", FULL);
  const mid = a("B", { ...FULL, timing: "unknown", budget: "none", progress: "none" });
  const low = a("C", { ...FULL, interest: "no_reply", timing: "later", need: "investigating", urgency: "none", budget: "none",
    authority: "not_identified", progress: "none" });

  test("maior pontuação primeiro", () => {
    expect(rank([low, high, mid]).ordered.map((r) => r.evaluation.opportunityId)).toEqual(["A", "B", "C"]);
  });
  test("pontos iguais continuam empatados, repartindo a mesma posição", () => {
    const twin = a("D", { ...FULL, timing: "unknown", budget: "none", progress: "none" });
    const ranked = rank([twin, high, mid]).ordered;
    expect(ranked.map((r) => [r.evaluation.opportunityId, r.position, r.tied])).toEqual([
      ["A", 1, false], ["B", 2, true], ["D", 2, true],
    ]);
  });
  test("incompletas e contraditórias ficam fora da ordem, como pendentes", () => {
    const partial = a("E", { interest: "replied" });
    const conflict = a("F", { ...FULL, interest: "no_contact", progress: "undated" });
    const ranking = rank([partial, high, conflict]);
    expect(ranking.ordered.map((r) => r.evaluation.opportunityId)).toEqual(["A"]);
    expect(ranking.pending.map((e) => e.opportunityId)).toEqual(["E", "F"]);
  });
  test("o vendedor pode reordenar, e a mudança fica identificada", () => {
    const ranking = rank([high, mid, low], ["B", "A", "C"]).ordered;
    expect(ranking.map((r) => [r.evaluation.opportunityId, r.position, r.manual])).toEqual([
      ["B", 1, true], ["A", 2, true], ["C", 3, false],
    ]);
  });
  test("ordem guardada que não cobre as oportunidades de hoje é ignorada", () => {
    expect(rank([high, mid, low], ["B", "A"]).ordered.map((r) => r.evaluation.opportunityId)).toEqual(["A", "B", "C"]);
    expect(rank([high, mid, low], ["B", "A", "Z"]).ordered.every((r) => !r.manual)).toBe(true);
  });
  test("subir e descer não passam das pontas", () => {
    expect(move(["A", "B", "C"], "B", -1)).toEqual(["B", "A", "C"]);
    expect(move(["A", "B", "C"], "A", -1)).toEqual(["A", "B", "C"]);
    expect(move(["A", "B", "C"], "C", 1)).toEqual(["A", "B", "C"]);
  });
});

describe("determinismo e retorno posterior", () => {
  test("as mesmas respostas dão o mesmo resultado, e avaliar não altera o que foi guardado", () => {
    const assessment = make("X", FULL);
    const before = JSON.stringify(assessment);
    expect(evaluate(assessment, TODAY)).toEqual(evaluate(structuredClone(assessment), TODAY));
    expect(JSON.stringify(assessment)).toBe(before);
  });
  test("mudar uma resposta recalcula os pontos e a categoria", () => {
    const before = run({ ...FULL, progress: "none" });
    const after = run({ ...FULL, progress: "none", interest: "no_reply" });
    expect(after.confirmed).toBe(before.confirmed - WEIGHTS.interest);
    expect(after.category).not.toBe(before.category);
  });
});
