// Os textos da priorização assistida que a tela monta, para o teste de vocabulário e o de cobertura.
import {
  ANSWER_LABELS, ANSWER_SHORT, ASSISTED, CATEGORY_ACTIONS, CATEGORY_LABELS, CONFLICT_TEXTS, CRITERIA_LABELS, QUESTIONS,
  breakdownText, markText, noteText, summaryText, unknownText, whyText,
} from "@/copy/assisted";
import { DIMENSIONS, emptyAssessment, type Answers, type Assessment } from "@/lib/assisted/model";
import { evaluate, rank, type Evaluation } from "@/lib/assisted/policy";
import type { Item } from "@/lib/contract";

export const TODAY = "2017-12-31";

const FULL: Answers = {
  interest: "replied", timing: "within_30", need: "confirmed", urgency: "concrete", budget: "confirmed",
  authority: "access", progress: "within_7",
};
const REST: Answers = { timing: "no_forecast", urgency: "none", budget: "none" };
const ALL_UNKNOWN = Object.fromEntries(DIMENSIONS.map((d) => [d, "unknown"])) as Answers;

type Sample = { name: string; answers: Answers; extra?: Partial<Assessment> };

/** Uma avaliação para cada caminho da política. */
export const SAMPLES: Sample[] = [
  { name: "due", answers: FULL },
  { name: "future", answers: { ...FULL, authority: "no_access", progress: "within_30" } },
  { name: "organize", answers: { ...FULL, progress: "undated" } },
  { name: "continuity", answers: { ...FULL, ...REST, progress: "none", authority: "no_access" } },
  { name: "qualification", answers: { ...FULL, ...REST, interest: "no_reply", progress: "none", authority: "not_identified" } },
  { name: "qualification-access", answers: { ...FULL, authority: "access", progress: "within_30" } },
  { name: "qualification-open", answers: { ...FULL, ...REST, need: "investigating", progress: "none", authority: "not_identified" } },
  { name: "resume", answers: { ...FULL, ...REST, interest: "no_reply", need: "investigating", progress: "none" } },
  { name: "need", answers: { ...FULL, ...REST, need: "none", progress: "none" } },
  { name: "unknown", answers: ALL_UNKNOWN },
  { name: "conflict", answers: { ...FULL, interest: "no_contact", need: "investigating", progress: "undated" } },
  { name: "partial", answers: { interest: "replied" } },
];

const evaluateSample = (sample: Sample): Evaluation =>
  evaluate({ ...emptyAssessment(sample.name, new Date("2018-01-02T10:00:00Z")), answers: sample.answers, ...sample.extra }, TODAY);

export const evaluations = (): Evaluation[] => SAMPLES.map(evaluateSample);

const ITEM = { opportunity_id: "X", product: "GTX Plus Pro", account: "Inity", sales_price: 5482 } as Item;

export function assistedTexts(): string[] {
  const all = evaluations();
  const ranking = rank(all);
  const texts: string[] = [];
  const add = (value: unknown): void => {
    if (typeof value === "string") texts.push(value);
    else if (value && typeof value === "object") Object.values(value).forEach(add);
  };
  [ASSISTED, CRITERIA_LABELS, QUESTIONS, ANSWER_LABELS, ANSWER_SHORT, CATEGORY_LABELS, CATEGORY_ACTIONS, CONFLICT_TEXTS]
    .forEach(add);
  texts.push(
    ASSISTED.points(72), ASSISTED.potential(87), ASSISTED.select.counter(3), ASSISTED.ask.progress(2, 3),
    ASSISTED.ask.answered(4), ASSISTED.ask.form("X"), ASSISTED.result.partialBody(["A", "B"]),
    ASSISTED.result.position(2, true), ASSISTED.result.position(1, false), ASSISTED.result.unknownBody("Orçamento"),
    ASSISTED.result.assessedOn("31/12/2017"), ASSISTED.result.up("X"), ASSISTED.result.down("X"),
    ASSISTED.mark.done(CATEGORY_LABELS.define_continuity), ASSISTED.result.pointsOf(15, 20),
  );
  for (const evaluation of all) {
    texts.push(whyText(evaluation), markText(evaluation), ...evaluation.breakdown.map(breakdownText),
      ...evaluation.notes.map(noteText));
    const unknown = unknownText(evaluation);
    if (unknown) texts.push(unknown);
  }
  texts.push(summaryText({
    seller: "Ana Alfa", asOf: TODAY, items: { X: ITEM }, ranked: ranking.ordered, aside: ranking.aside,
    pending: ranking.pending,
  }));
  return texts;
}
