import "server-only";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { z } from "zod";
import {
  CATEGORIES,
  type AuditReport,
  type DiagnosticoReport,
  type ModelMetrics,
  type RoutingEval,
} from "./types";

// Presentation-only readers: missing and outdated artifacts never become current metrics.
const num = z.number().finite();
const interval = z.object({ low: num, high: num });
const category = z.enum(CATEGORIES);
const route = z.enum(["auto", "revisao_humana", "escalar"]);
const classMetrics = z.object({
  label: category,
  precision: num,
  recall: num,
  f1: num,
  support: num,
});
const candidate = z.object({ name: z.string(), accuracy: num, macroF1: num });
const auditSchema = z.object({
  generatedAt: z.string(),
  d1: z.object({
    rows: num,
    columns: num,
    statusMix: z.array(z.object({ status: z.string(), n: num, share: num })),
  }),
  d2: z.object({
    rows: num,
    classes: z.array(z.object({ label: category, n: num, share: num })),
  }),
  findings: z.array(
    z.object({
      id: z.string(),
      dataset: z.enum(["D1", "D2"]),
      title: z.string(),
      evidence: z.string(),
      metric: z.union([num, z.string()]).optional(),
      implication: z.string(),
      severity: z.enum(["bloqueante", "alerta", "info"]),
    }),
  ),
});
const diagnosticSchema = z.object({
  generatedAt: z.string(),
  nTickets: num,
  observations: z.array(
    z.object({
      id: z.string(),
      label: z.string(),
      value: z.string(),
      detail: z.string(),
    }),
  ),
  segments: z.array(
    z.object({
      channel: z.string(),
      priority: z.string(),
      n: num,
      backlogShare: num,
      backlogCI: interval,
      pendingCustomerShare: num,
      csatMean: num.nullable(),
    }),
  ),
  tests: z.object({
    segmentTests: z.array(
      z.object({
        variable: z.string(),
        test: z.string(),
        pValue: num,
        significant: z.boolean(),
        conclusion: z.string(),
      }),
    ),
    csatDrivers: z.array(
      z.object({
        variable: z.string(),
        test: z.string(),
        pValue: num,
        effectSize: num,
        detectableDiff: num,
        conclusion: z.string(),
        groups: z.array(
          z.object({ label: z.string(), mean: num, ci: interval, n: num }),
        ),
      }),
    ),
  }),
  limitations: z.array(z.object({ id: z.string(), text: z.string() })),
  scenario: z.object({
    note: z.string(),
    assumptions: z.array(
      z.object({
        id: z.string(),
        label: z.string(),
        value: num,
        unit: z.string(),
        kind: z.enum(["medido", "premissa", "referencia"]),
        source: z.string(),
        editable: z.boolean(),
      }),
    ),
    waste: z.array(
      z.object({
        id: z.enum(["triage", "rework", "followup", "drafting"]),
        step: z.string(),
        hoursPerYear: num,
        recoverableHoursPerYear: num,
        rationale: z.string(),
      }),
    ),
    totals: z.object({
      hoursPerYear: num,
      recoverableHoursPerYear: num,
      recoverableCost: num,
      fte: num,
    }),
    sensitivity: z.array(
      z.object({
        autoShare: num,
        draftSaving: num,
        recoverableHoursPerYear: num,
      }),
    ),
  }),
});
const modelSchema = z.object({
  generatedAt: z.string(),
  seed: num,
  splits: z.array(
    z.object({
      name: z.enum(["treino", "validacao", "teste"]),
      n: num,
      share: num,
      purpose: z.string(),
    }),
  ),
  selection: z.object({
    model: z.string(),
    C: num,
    coefEps: num,
    confidenceThreshold: num,
    oodThreshold: num,
    adminRightsThreshold: num.nullable(),
    criteria: z.array(z.string()),
    candidates: z.array(candidate),
  }),
  test: z.object({
    accuracy: num,
    accuracyCI: interval,
    macroF1: num,
    macroF1CI: interval,
    baselineAccuracy: num,
    perClass: z.array(classMetrics),
    confusion: z.object({
      labels: z.array(category),
      matrix: z.array(z.array(num)),
    }),
  }),
  exploratory: z.object({
    note: z.string(),
    accuracy: num,
    macroF1: num,
    autoCoverage: num,
    autoAccuracy: num,
  }),
  crossDomain: z.object({
    note: z.string(),
    n: num,
    confidentShare: num,
    confidentPredictedHardware: num,
    oodFlagged: num,
    inDomainOodFlagged: num,
    routes: z.array(z.object({ route, share: num })),
  }),
});
const partition = z.object({
  n: num,
  modelAccuracy: num,
  routes: z.array(z.object({ route, n: num, share: num })),
  reasons: z.array(
    z.object({
      reasonCode: z.enum([
        "escalation_terms",
        "out_of_domain",
        "low_confidence",
        "always_human",
        "admin_rights_risk",
        "auto",
      ]),
      n: num,
      share: num,
    }),
  ),
  auto: z.object({
    n: num,
    share: num,
    shareCI: interval,
    accuracy: num,
    accuracyCI: interval,
    errors: num,
  }),
  byTrueCategory: z.array(
    z.object({
      label: category,
      n: num,
      auto: num,
      revisao_humana: num,
      escalar: num,
      autoAccuracy: num.nullable(),
    }),
  ),
  adminRightsLeak: z.object({
    trueAdminRights: num,
    autoRoutedElsewhere: num,
    share: num,
    toQueues: z.array(z.object({ label: category, n: num })),
  }),
  pythonAgreement: z.object({ route: num, label: num, maxConfidenceDiff: num }),
});
const routingSchema = z.object({
  generatedAt: z.string(),
  note: z.string(),
  thresholds: z.object({
    confidence: num,
    ood: num,
    adminRights: num.nullable(),
  }),
  validation: partition,
  test: partition,
});

async function readReport<T>(
  name: string,
  schema: z.ZodType<T>,
): Promise<T | null> {
  try {
    const raw: unknown = JSON.parse(
      await readFile(path.join(process.cwd(), "data", name), "utf8"),
    );
    const result = schema.safeParse(raw);
    if (!result.success) {
      console.warn(
        `[ui] ${name}: relatório incompatível com o contrato atual.`,
      );
      return null;
    }
    return result.data;
  } catch {
    console.warn(`[ui] ${name}: relatório indisponível.`);
    return null;
  }
}
export const readAudit = (): Promise<AuditReport | null> =>
  readReport("audit.json", auditSchema);
export const readDiagnostic = (): Promise<DiagnosticoReport | null> =>
  readReport("diagnostico.json", diagnosticSchema);
export const readModelMetrics = (): Promise<ModelMetrics | null> =>
  readReport("model_metrics.json", modelSchema);
export const readRouting = (): Promise<RoutingEval | null> =>
  readReport("routing_eval.json", routingSchema);
export async function readAutomationDocument(): Promise<string | null> {
  // The generated copy is inside the app root and is included in deployment assets.
  try {
    return await readFile(
      path.join(process.cwd(), "public/docs/automacao.md"),
      "utf8",
    );
  } catch {
    return null;
  }
}
