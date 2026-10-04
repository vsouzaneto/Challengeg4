// Classificador TF-IDF + Logistic Regression treinado em Python (analysis/train_classifier.py)
// no Dataset 2 e exportado como JSON. Inferência 100% local: ~1ms por ticket, custo zero.
import model from "../../../data/generated/classifier.json";
import { normalizeToEnglish, sklearnTokens } from "./text";

type Model = {
  version: string;
  classes: string[];
  terms: string[];
  idf: number[];
  coef: number[][];
  intercept: number[];
};

const M = model as Model;
const index = new Map<string, number>(M.terms.map((t, i) => [t, i]));

export const CLASSIFIER_VERSION = M.version;
export const CATEGORIES = M.classes;

export type Classification = {
  category: string;
  confidence: number;
  probabilities: Record<string, number>;
  topTerms: string[];
};

function vectorize(text: string): Map<number, number> {
  const toks = sklearnTokens(text);
  const grams: string[] = [...toks];
  for (let i = 0; i < toks.length - 1; i++) grams.push(`${toks[i]} ${toks[i + 1]}`);
  const tf = new Map<number, number>();
  for (const g of grams) {
    const j = index.get(g);
    if (j !== undefined) tf.set(j, (tf.get(j) ?? 0) + 1);
  }
  // sublinear_tf + idf + normalização L2 (igual ao TfidfVectorizer)
  let norm = 0;
  for (const [j, c] of tf) {
    const v = (1 + Math.log(c)) * M.idf[j];
    tf.set(j, v);
    norm += v * v;
  }
  norm = Math.sqrt(norm) || 1;
  for (const [j, v] of tf) tf.set(j, v / norm);
  return tf;
}

export function classify(text: string, opts: { normalize?: boolean } = {}): Classification {
  const input = opts.normalize === false ? text : normalizeToEnglish(text);
  const x = vectorize(input);
  const logits = M.classes.map((_, k) => {
    let s = M.intercept[k];
    for (const [j, v] of x) s += M.coef[k][j] * v;
    return s;
  });
  const max = Math.max(...logits);
  const exps = logits.map((l) => Math.exp(l - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  const probs = exps.map((e) => e / sum);
  const best = probs.indexOf(Math.max(...probs));

  // Explicabilidade: termos que mais contribuíram para a classe vencedora.
  const contrib = [...x].map(([j, v]) => [M.terms[j], M.coef[best][j] * v] as const);
  contrib.sort((a, b) => b[1] - a[1]);

  return {
    category: M.classes[best],
    confidence: probs[best],
    probabilities: Object.fromEntries(M.classes.map((c, k) => [c, probs[k]])),
    topTerms: contrib.slice(0, 5).filter(([, w]) => w > 0).map(([t]) => t),
  };
}

/** Roteamento: categoria → fila/time responsável. */
export const TEAM_BY_CATEGORY: Record<string, string> = {
  Access: "Identity & Access",
  "Administrative rights": "Identity & Access",
  Hardware: "Hardware & Devices",
  Storage: "Infra & Storage",
  Purchase: "Billing & Purchase",
  "HR Support": "People Ops",
  "Internal Project": "Projects",
  Miscellaneous: "General Support",
};
