import { describe, expect, it } from "vitest";
import { decideRoute, tokenize, type Prediction } from "@/lib/classifier";
import { loadModel, loadPythonPredictions, loadRules, loadSplit } from "@/lib/eval-data";
import { evaluatePartition } from "@/lib/routing-eval";
import { CATEGORIES, type Category } from "@/lib/types";

const model = loadModel();
const rules = loadRules();
const { confidence, ood, adminRights } = model.thresholds;

function fakePrediction(over: Partial<Prediction> & { text?: string; pAdmin?: number } = {}): Prediction {
  const category: Category = over.category ?? "Hardware";
  const pAdmin = over.pAdmin ?? 0;
  const conf = over.confidence ?? 0.99;
  return {
    tokens: tokenize(over.text ?? "laptop screen broken"),
    vec: new Map(),
    category,
    confidence: conf,
    knownShare: over.knownShare ?? 1,
    probabilities: CATEGORIES.map((label) => ({
      label,
      p: label === category ? conf : label === "Administrative rights" ? pAdmin : 0,
    })),
    topTerms: [],
  };
}

describe("decideRoute: cada ramo da política", () => {
  it("termo de risco escala e bloqueia rascunho, mesmo com confiança alta", () => {
    const d = decideRoute(fakePrediction({ text: "urgent laptop broken" }), model, rules);
    expect(d).toMatchObject({ route: "escalar", reasonCode: "escalation_terms", draftAllowed: false });
  });

  it("vocabulário desconhecido vai para revisão humana", () => {
    const d = decideRoute(fakePrediction({ knownShare: ood - 0.01 }), model, rules);
    expect(d).toMatchObject({ route: "revisao_humana", reasonCode: "out_of_domain", draftAllowed: true });
  });

  it("confiança abaixo do limiar vai para revisão humana", () => {
    const d = decideRoute(fakePrediction({ confidence: confidence - 0.01 }), model, rules);
    expect(d).toMatchObject({ route: "revisao_humana", reasonCode: "low_confidence" });
  });

  it("previsão de privilégio administrativo nunca é automática", () => {
    const d = decideRoute(fakePrediction({ category: "Administrative rights" }), model, rules);
    expect(d).toMatchObject({ route: "revisao_humana", reasonCode: "always_human" });
  });

  it("probabilidade de privilégio acima do limiar exige aprovação, mesmo prevendo outra categoria", () => {
    expect(adminRights).not.toBeNull();
    const d = decideRoute(fakePrediction({ category: "Access", pAdmin: adminRights! }), model, rules);
    expect(d).toMatchObject({ route: "revisao_humana", reasonCode: "admin_rights_risk" });
  });

  it("caso limpo e confiante é automático", () => {
    const d = decideRoute(fakePrediction({ confidence: confidence }), model, rules);
    expect(d).toMatchObject({ route: "auto", reasonCode: "auto", draftAllowed: true });
  });
});

describe("roteamento medido no teste", () => {
  const python = loadPythonPredictions();
  const test = evaluatePartition(loadSplit("test"), model, rules, python.test);

  it("a política TS concorda 100% com a réplica Python usada na seleção", () => {
    expect(test.pythonAgreement.route).toBe(1);
    expect(test.pythonAgreement.label).toBe(1);
  });

  it("as rotas somam o total e a cobertura automática é parcial (nunca 100%)", () => {
    expect(test.routes.reduce((s, r) => s + r.n, 0)).toBe(test.n);
    expect(test.auto.share).toBeGreaterThan(0.3);
    expect(test.auto.share).toBeLessThan(0.9);
  });

  it("vazamento de pedidos de privilégio para filas automáticas é reportado e baixo", () => {
    expect(test.adminRightsLeak.trueAdminRights).toBeGreaterThan(200);
    expect(test.adminRightsLeak.share).toBeLessThanOrEqual(0.05);
  });
});
