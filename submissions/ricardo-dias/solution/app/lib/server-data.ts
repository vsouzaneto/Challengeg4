// Carrega os artefatos gerados pela análise (data/*.json) uma vez por instância, validando o formato.
// Leitura via fs (não import) para não fazer o TypeScript inferir tipos de um JSON de MBs.
import "server-only";
import { readFileSync } from "node:fs";
import path from "node:path";
import type { Doc } from "./classifier";
import { parseModel, parsePolicyRules, type Model, type PolicyRules } from "./model-schema";
import rulesJson from "./policy-rules.json";

const dataDir = path.join(process.cwd(), "data");
const cache = new Map<string, unknown>();

function load<T>(file: string, parse: (json: unknown) => T): T {
  if (!cache.has(file)) cache.set(file, parse(JSON.parse(readFileSync(path.join(dataDir, file), "utf-8"))));
  return cache.get(file) as T;
}

const docs = (json: unknown) => (json as { items: Doc[] }).items;

let rules: PolicyRules | null = null;

export const getModel = (): Model => load("model.json", parseModel);
export const getPolicyRules = (): PolicyRules => (rules ??= parsePolicyRules(rulesJson));
export const getNeighbors = (): Doc[] => load("neighbors.json", docs);
export const getHoldout = (): Doc[] => load("holdout.json", docs);
