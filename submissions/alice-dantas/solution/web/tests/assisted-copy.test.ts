// Textos da priorização assistida: cobertura, vocabulário e a regra de nunca parecer previsão de fechamento.
import { describe, expect, test } from "vitest";

import {
  CATEGORY_ACTIONS, CATEGORY_LABELS, CONFLICT_TEXTS, QUESTIONS, ANSWER_LABELS, ANSWER_SHORT, whyText,
} from "@/copy/assisted";
import { DIMENSIONS, OPTIONS } from "@/lib/assisted/model";

import { assistedTexts, evaluations } from "./assisted-texts";

describe("cobertura", () => {
  test("toda pergunta, resposta e categoria tem texto", () => {
    expect(Object.keys(QUESTIONS).sort()).toEqual([...DIMENSIONS].sort());
    for (const dimension of DIMENSIONS) {
      expect(Object.keys(ANSWER_LABELS[dimension]).sort(), dimension).toEqual([...OPTIONS[dimension]].sort());
      expect(Object.keys(ANSWER_SHORT[dimension]).sort(), dimension).toEqual([...OPTIONS[dimension]].sort());
    }
    expect(Object.keys(CATEGORY_ACTIONS).sort()).toEqual(Object.keys(CATEGORY_LABELS).sort());
    expect(Object.keys(CONFLICT_TEXTS)).toHaveLength(2);
  });
  test("as amostras percorrem todas as categorias de trabalho", () => {
    const seen = new Set(evaluations().map((e) => e.category).filter(Boolean));
    expect([...seen].sort()).toEqual(Object.keys(CATEGORY_LABELS).sort());
  });
});

describe("o motivo de \"Avançar qualificação\" combina com as respostas", () => {
  const advance = () => evaluations().filter((e) => e.category === "advance_qualification");
  const answerOf = (e: ReturnType<typeof evaluations>[number], dimension: string) =>
    e.breakdown.find((row) => row.dimension === dimension)?.answer;

  test("só fala em falta de acesso ao decisor quando o vendedor respondeu que não tem", () => {
    expect(advance().length).toBeGreaterThan(2);
    for (const e of advance()) {
      const mentionsGap = /não há acesso à pessoa que decide/.test(whyText(e));
      const hasGap = ["no_access", "not_identified"].includes(String(answerOf(e, "authority")));
      expect(mentionsGap, e.opportunityId).toBe(hasGap && answerOf(e, "need") === "confirmed");
    }
  });
  test("necessidade confirmada com acesso ao decisor: o motivo é a ação para os próximos dias", () => {
    const e = advance().find((item) => answerOf(item, "authority") === "access");
    expect(e).toBeDefined();
    expect(whyText(e!)).toMatch(/há acesso a quem decide, mas não há ação combinada/);
  });
});

describe("a ferramenta nunca parece prever o fechamento", () => {
  const texts = assistedTexts();
  test("há textos para varrer", () => {
    expect(texts.length).toBeGreaterThan(80);
  });
  test("nenhuma porcentagem, probabilidade, chance nem \"melhor oportunidade\"", () => {
    for (const text of texts) {
      expect(text, text).not.toMatch(/%|probabilidade|chance|melhor oportunidade|garant/i);
    }
  });
  test("o aviso de que não é previsão de fechamento acompanha o resultado", () => {
    expect(texts.some((t) => /não é previsão de fechamento/.test(t))).toBe(true);
  });
  test("nenhum texto sai com valor faltando", () => {
    for (const text of texts) expect(text).not.toMatch(/undefined|null|NaN|\[object/);
  });
  test("nenhum texto usa ponto e vírgula", () => {
    for (const text of texts) expect(text, text).not.toContain(";");
  });
});
