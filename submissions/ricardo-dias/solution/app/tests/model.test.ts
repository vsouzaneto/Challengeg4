import { describe, expect, it } from "vitest";
import { predict } from "@/lib/classifier";
import { loadModel, loadPythonPredictions, loadSplit, readModelJson } from "@/lib/eval-data";
import { MODEL_VERSION, ModelFormatError, parseModel } from "@/lib/model-schema";

describe("formato do model.json", () => {
  it("o artefato atual é válido e da versão esperada", () => {
    const model = loadModel();
    expect(model.version).toBe(MODEL_VERSION);
    expect(model.stopWordSet.size).toBeGreaterThan(0);
  });

  it("versão diferente falha com mensagem clara", () => {
    const json = { ...(readModelJson() as object), version: 1 };
    expect(() => parseModel(json)).toThrow(ModelFormatError);
    expect(() => parseModel(json)).toThrow(/versão 1 incompatível .*esperado 2.*03_classifier\.py/);
  });

  it("campo obrigatório ausente falha com mensagem clara (não um erro opaco na inferência)", () => {
    const { stopWords: _omit, ...json } = readModelJson() as Record<string, unknown>;
    void _omit;
    expect(() => parseModel(json)).toThrow(/model\.json inválido[\s\S]*stopWords/);
  });

  it("vetor de pesos com tamanho errado é recusado", () => {
    const json = readModelJson() as { weights: Record<string, number[]> };
    const [term] = Object.keys(json.weights);
    const broken = { ...json, weights: { ...json.weights, [term]: [1, 2, 3] } };
    expect(() => parseModel(broken)).toThrow(ModelFormatError);
  });
});

describe("paridade TypeScript × scikit-learn", () => {
  it("reproduz rótulo e confiança do Python em todo o conjunto de teste", () => {
    const model = loadModel();
    const expected = new Map(loadPythonPredictions().test.map((p) => [p.id, p]));
    const docs = loadSplit("test");
    let sameLabel = 0;
    let maxDiff = 0;
    for (const doc of docs) {
      const p = predict(model, doc.text);
      const e = expected.get(doc.id)!;
      if (p.category === e.label) sameLabel++;
      maxDiff = Math.max(maxDiff, Math.abs(p.confidence - e.confidence));
    }
    expect(docs.length).toBeGreaterThan(7_000);
    expect(sameLabel).toBe(docs.length);
    expect(maxDiff).toBeLessThan(1e-3);
  });
});
