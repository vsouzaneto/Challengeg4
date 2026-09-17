// Avaliação do roteamento completo (predict + decideRoute) numa partição rotulada.
// Usado por scripts/evaluate-routing.ts e pelos testes.
import { decideRoute, predict, type Doc } from "./classifier";
import type { PythonPrediction } from "./eval-data";
import type { Model, PolicyRules } from "./model-schema";
import { CATEGORIES, type Interval, type ReasonCode, type Route, type RoutingPartition } from "./types";

const BOOTSTRAP = 1_000;
const ROUTES: Route[] = ["auto", "revisao_humana", "escalar"];
const REASONS: ReasonCode[] = ["auto", "low_confidence", "out_of_domain", "always_human", "admin_rights_risk", "escalation_terms"];
const r4 = (x: number) => Math.round(x * 10_000) / 10_000;

// PRNG determinístico (mulberry32) para o bootstrap ser reproduzível.
function rng(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function ci(values: number[]): Interval {
  const s = [...values].sort((a, b) => a - b);
  const at = (q: number) => s[Math.min(s.length - 1, Math.floor(q * s.length))];
  return { low: r4(at(0.025)), high: r4(at(0.975)) };
}

export function evaluatePartition(docs: Doc[], model: Model, rules: PolicyRules, python: PythonPrediction[]): RoutingPartition {
  const pyById = new Map(python.map((p) => [p.id, p]));
  const rows = docs.map((doc) => {
    const prediction = predict(model, doc.text);
    const decision = decideRoute(prediction, model, rules);
    const py = pyById.get(doc.id);
    if (!py) throw new Error(`sem predição Python para o ticket ${doc.id}`);
    return {
      label: doc.label,
      pred: prediction.category,
      route: decision.route,
      reason: decision.reasonCode,
      sameRoute: py.route === decision.route && py.reasonCode === decision.reasonCode,
      sameLabel: py.label === prediction.category,
      confDiff: Math.abs(py.confidence - prediction.confidence),
    };
  });
  const n = rows.length;
  const auto = rows.filter((x) => x.route === "auto");
  const autoCorrect = auto.filter((x) => x.pred === x.label).length;

  const random = rng(42);
  const shares: number[] = [];
  const accs: number[] = [];
  for (let b = 0; b < BOOTSTRAP; b++) {
    let a = 0;
    let ok = 0;
    for (let i = 0; i < n; i++) {
      const x = rows[Math.floor(random() * n)];
      if (x.route === "auto") {
        a++;
        if (x.pred === x.label) ok++;
      }
    }
    shares.push(a / n);
    accs.push(a ? ok / a : 0);
  }

  const admin = rows.filter((x) => x.label === rules.adminRightsCategory);
  const leaked = admin.filter((x) => x.route === "auto");
  const count = <K extends string>(key: "route" | "reason", value: K) => rows.filter((x) => x[key] === value).length;

  return {
    n,
    modelAccuracy: r4(rows.filter((x) => x.pred === x.label).length / n),
    routes: ROUTES.map((route) => ({ route, n: count("route", route), share: r4(count("route", route) / n) })),
    reasons: REASONS.map((reasonCode) => ({
      reasonCode,
      n: count("reason", reasonCode),
      share: r4(count("reason", reasonCode) / n),
    })),
    auto: {
      n: auto.length,
      share: r4(auto.length / n),
      shareCI: ci(shares),
      accuracy: r4(autoCorrect / auto.length),
      accuracyCI: ci(accs),
      errors: auto.length - autoCorrect,
    },
    byTrueCategory: CATEGORIES.map((label) => {
      const g = rows.filter((x) => x.label === label);
      const ga = g.filter((x) => x.route === "auto");
      return {
        label,
        n: g.length,
        auto: ga.length,
        revisao_humana: g.filter((x) => x.route === "revisao_humana").length,
        escalar: g.filter((x) => x.route === "escalar").length,
        autoAccuracy: ga.length ? r4(ga.filter((x) => x.pred === label).length / ga.length) : null,
      };
    }),
    adminRightsLeak: {
      trueAdminRights: admin.length,
      autoRoutedElsewhere: leaked.length,
      share: r4(leaked.length / admin.length),
      toQueues: CATEGORIES.map((label) => ({ label, n: leaked.filter((x) => x.pred === label).length })).filter((q) => q.n > 0),
    },
    pythonAgreement: {
      route: r4(rows.filter((x) => x.sameRoute).length / n),
      label: r4(rows.filter((x) => x.sameLabel).length / n),
      maxConfidenceDiff: Math.max(...rows.map((x) => x.confDiff)),
    },
  };
}

