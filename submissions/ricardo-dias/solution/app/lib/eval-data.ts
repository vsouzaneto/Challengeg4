// Leitura dos artefatos de avaliação (analysis/artifacts) para scripts e testes. Não é usado pelo app.
import { readFileSync } from "node:fs";
import path from "node:path";
import type { Doc } from "./classifier";
import { parseModel, parsePolicyRules, type Model, type PolicyRules } from "./model-schema";
import type { ReasonCode, Route } from "./types";
import rulesJson from "./policy-rules.json";

const appDir = path.resolve(__dirname, "..");
const artifactsDir = path.resolve(appDir, "../analysis/artifacts");
const readJson = (file: string): unknown => JSON.parse(readFileSync(file, "utf-8"));

export interface PythonPrediction {
  id: number;
  label: string;
  confidence: number;
  route: Route;
  reasonCode: ReasonCode;
}

export const dataPath = (file: string) => path.join(appDir, "data", file);
export const readModelJson = (): unknown => readJson(dataPath("model.json"));
export const loadModel = (): Model => parseModel(readModelJson());
export const loadRules = (): PolicyRules => parsePolicyRules(rulesJson);
export const loadSplit = (name: "val" | "test"): Doc[] =>
  (readJson(path.join(artifactsDir, `${name}_split.json`)) as { items: Doc[] }).items;
export const loadPythonPredictions = () =>
  readJson(path.join(artifactsDir, "python_predictions.json")) as {
    validation: PythonPrediction[];
    test: PythonPrediction[];
  };
