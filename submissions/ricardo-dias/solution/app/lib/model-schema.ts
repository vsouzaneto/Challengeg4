// Formato do model.json e das regras de política, validados ao carregar.
// Se analysis/03_classifier.py mudar o formato, MODEL_VERSION muda junto e o app falha com
// mensagem clara em vez de um erro opaco no meio da inferência.

import { z } from "zod";
import { CATEGORIES, type Category } from "./types";

export const MODEL_VERSION = 2;

const unit = z.number().min(0).max(1);

const modelFileSchema = z
  .object({
    version: z.number(),
    classes: z.array(z.enum(CATEGORIES)).length(CATEGORIES.length),
    thresholds: z.object({ confidence: unit, ood: unit, adminRights: unit.nullable() }),
    stopWords: z.array(z.string()).min(1),
    idf: z.record(z.string(), z.number().positive()),
    weights: z.record(z.string(), z.array(z.number()).length(CATEGORIES.length)),
    intercept: z.array(z.number()).length(CATEGORIES.length),
  })
  .superRefine((m, ctx) => {
    const missing = Object.keys(m.weights).find((t) => m.idf[t] === undefined);
    if (missing) ctx.addIssue({ code: "custom", message: `termo com peso sem idf: "${missing}"` });
  });

export type ModelFile = z.infer<typeof modelFileSchema>;
export type Model = ModelFile & { classes: Category[]; stopWordSet: Set<string> };

const policyRulesSchema = z.object({
  version: z.literal(1),
  escalationTerms: z.array(z.string().regex(/^[a-z]{2,}$/)).min(1),
  alwaysHuman: z.array(z.object({ category: z.enum(CATEGORIES), reason: z.string().min(1) })),
  adminRightsCategory: z.enum(CATEGORIES),
});
export type PolicyRules = z.infer<typeof policyRulesSchema>;

export class ModelFormatError extends Error {}

export function parseModel(json: unknown): Model {
  const version = (json as { version?: unknown } | null)?.version;
  if (version !== MODEL_VERSION) {
    throw new ModelFormatError(
      `model.json versão ${String(version)} incompatível com o app (esperado ${MODEL_VERSION}); rode analysis/03_classifier.py.`,
    );
  }
  const parsed = modelFileSchema.safeParse(json);
  if (!parsed.success) {
    throw new ModelFormatError(`model.json inválido: ${z.prettifyError(parsed.error)}; rode analysis/03_classifier.py.`);
  }
  return { ...parsed.data, stopWordSet: new Set(parsed.data.stopWords) };
}

export function parsePolicyRules(json: unknown): PolicyRules {
  const parsed = policyRulesSchema.safeParse(json);
  if (!parsed.success) throw new ModelFormatError(`policy-rules.json inválido: ${z.prettifyError(parsed.error)}`);
  return parsed.data;
}
