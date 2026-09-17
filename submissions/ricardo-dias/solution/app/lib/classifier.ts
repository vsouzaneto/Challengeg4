// Inferência do classificador exportado por analysis/03_classifier.py + política de roteamento.
// Reproduz o TfidfVectorizer do scikit-learn: tokens [a-z]{2,}, unigramas + bigramas,
// tf sublinear (1 + ln tf), idf suavizado (já calculado), normalização L2.
// Funções puras, sem dependências de Node: usadas pela API, pelos testes e por scripts/evaluate-routing.ts.
// A política é replicada em analysis/policy.py apenas para seleção de limiares na validação;
// tests/routing.test.ts exige concordância de 100% entre as duas.

import type { Category, ClassifyResponse, ReasonCode, Route } from "./types";
import type { Model, PolicyRules } from "./model-schema";

type SparseVec = Map<string, number>;

export interface Doc {
  id: number;
  text: string;
  label: Category;
}

export function normalize(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function tokenize(text: string): string[] {
  return normalize(text).match(/\b[a-z]{2,}\b/g) ?? [];
}

export function vectorize(tokens: string[], idf: Record<string, number>): SparseVec {
  const counts = new Map<string, number>();
  const add = (term: string) => {
    if (idf[term] !== undefined) counts.set(term, (counts.get(term) ?? 0) + 1);
  };
  tokens.forEach((t, i) => {
    add(t);
    if (i + 1 < tokens.length) add(`${t} ${tokens[i + 1]}`);
  });

  const vec: SparseVec = new Map();
  let norm = 0;
  for (const [term, tf] of counts) {
    const v = (1 + Math.log(tf)) * idf[term];
    vec.set(term, v);
    norm += v * v;
  }
  norm = Math.sqrt(norm);
  if (norm > 0) for (const [term, v] of vec) vec.set(term, v / norm);
  return vec;
}

function softmax(z: number[]): number[] {
  const max = Math.max(...z);
  const e = z.map((v) => Math.exp(v - max));
  const sum = e.reduce((a, b) => a + b, 0);
  return e.map((v) => v / sum);
}

// Fração das palavras de conteúdo (sem stopwords) que o modelo conhece.
// Mesma regra de known_share no Python.
export function knownShare(tokens: string[], model: Model): number {
  const content = tokens.filter((t) => !model.stopWordSet.has(t));
  if (content.length === 0) return 0;
  return content.filter((t) => model.idf[t] !== undefined).length / content.length;
}

export interface Prediction {
  tokens: string[];
  vec: SparseVec;
  category: Category;
  confidence: number;
  knownShare: number;
  probabilities: { label: Category; p: number }[];
  topTerms: { term: string; weight: number }[];
}

export function predict(model: Model, text: string): Prediction {
  const tokens = tokenize(text);
  const vec = vectorize(tokens, model.idf);
  const z = [...model.intercept];
  for (const [term, x] of vec) {
    const w = model.weights[term];
    if (w) for (let k = 0; k < z.length; k++) z[k] += x * w[k];
  }
  const probs = softmax(z);
  let best = 0;
  for (let k = 1; k < probs.length; k++) if (probs[k] > probs[best]) best = k;

  const topTerms = [...vec]
    .map(([term, x]) => ({ term, weight: x * (model.weights[term]?.[best] ?? 0) }))
    .filter((t) => t.weight > 0)
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 8)
    .map((t) => ({ term: t.term, weight: Math.round(t.weight * 1000) / 1000 }));

  return {
    tokens,
    vec,
    category: model.classes[best],
    confidence: probs[best],
    knownShare: knownShare(tokens, model),
    probabilities: model.classes.map((label, k) => ({ label, p: probs[k] })).sort((a, b) => b.p - a.p),
    topTerms,
  };
}

// ---- Política de roteamento (docs/automacao.md) ----
// Ordem: escalação → guarda de domínio → confiança → categoria sempre-humana → risco de privilégio → automático.

export interface RouteDecision {
  route: Route;
  reasonCode: ReasonCode;
  routeReason: string;
  draftAllowed: boolean;
}

const pct = (x: number) => `${(x * 100).toFixed(0)}%`;

export function decideRoute(prediction: Prediction, model: Model, rules: PolicyRules): RouteDecision {
  const { confidence: conf, ood, adminRights } = model.thresholds;
  const tokenSet = new Set(prediction.tokens);
  const hits = rules.escalationTerms.filter((t) => tokenSet.has(t));
  if (hits.length > 0) {
    return {
      route: "escalar",
      reasonCode: "escalation_terms",
      routeReason: `Sinal de risco/urgência no texto (${hits.join(", ")}): vai direto para atendente sênior.`,
      draftAllowed: false,
    };
  }
  // Medido: fora do domínio o modelo erra com confiança alta. Vocabulário desconhecido → humano.
  if (prediction.knownShare < ood) {
    return {
      route: "revisao_humana",
      reasonCode: "out_of_domain",
      routeReason: `Só ${pct(prediction.knownShare)} das palavras são conhecidas pelo modelo (mínimo ${pct(ood)}): texto fora do padrão do treino, triagem humana.`,
      draftAllowed: true,
    };
  }
  if (prediction.confidence < conf) {
    return {
      route: "revisao_humana",
      reasonCode: "low_confidence",
      routeReason: `Confiança ${pct(prediction.confidence)} abaixo do limiar de ${pct(conf)}: triagem humana confirma a categoria.`,
      draftAllowed: true,
    };
  }
  const human = rules.alwaysHuman.find((r) => r.category === prediction.category);
  if (human) {
    return { route: "revisao_humana", reasonCode: "always_human", routeReason: human.reason, draftAllowed: true };
  }
  if (adminRights !== null) {
    const pAdmin = prediction.probabilities.find((p) => p.label === rules.adminRightsCategory)?.p ?? 0;
    if (pAdmin >= adminRights) {
      return {
        route: "revisao_humana",
        reasonCode: "admin_rights_risk",
        routeReason: `Probabilidade de ser pedido de privilégio administrativo (${pct(pAdmin)}) acima de ${pct(adminRights)}: aprovação humana.`,
        draftAllowed: true,
      };
    }
  }
  return {
    route: "auto",
    reasonCode: "auto",
    routeReason: `Confiança ${pct(prediction.confidence)} ≥ limiar de ${pct(conf)}: roteado automaticamente para a fila ${prediction.category}.`,
    draftAllowed: true,
  };
}

// ---- Tickets similares (cosseno TF-IDF sobre amostra do treino) ----

const neighborVecs = new WeakMap<Doc[], SparseVec[]>();

export function similar(model: Model, docs: Doc[], query: SparseVec, k = 3) {
  let vecs = neighborVecs.get(docs);
  if (!vecs) {
    vecs = docs.map((d) => vectorize(tokenize(d.text), model.idf));
    neighborVecs.set(docs, vecs);
  }
  const scored: { text: string; label: Category; score: number }[] = [];
  vecs.forEach((v, i) => {
    let dot = 0;
    const [small, large] = query.size < v.size ? [query, v] : [v, query];
    for (const [term, x] of small) {
      const y = large.get(term);
      if (y) dot += x * y;
    }
    if (dot > 0) scored.push({ text: docs[i].text, label: docs[i].label, score: Math.round(dot * 1000) / 1000 });
  });
  return scored.sort((a, b) => b.score - a.score).slice(0, k);
}

// Caminho único para chamadas unitárias e em lote: o lote só não calcula "similar".
export function classifyTicket(
  model: Model,
  rules: PolicyRules,
  text: string,
  neighbors: Doc[] | null,
): ClassifyResponse {
  const prediction = predict(model, text);
  const decision = decideRoute(prediction, model, rules);
  return {
    category: prediction.category,
    confidence: prediction.confidence,
    knownShare: prediction.knownShare,
    probabilities: prediction.probabilities,
    topTerms: prediction.topTerms,
    ...decision,
    similar: neighbors ? similar(model, neighbors, prediction.vec) : [],
  };
}
