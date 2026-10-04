// Knowledge Base: retrieval semântico leve + detecção de Knowledge Gaps (PRD §19–21).
// Retrieval: TF-IDF/cosseno sobre título+tags+corpo e, separadamente, sobre cada pergunta-exemplo
// do artigo (padrão Q&A do Botpress). Quando um gap é resolvido, a pergunta original vira
// pergunta-exemplo do novo artigo — por isso a próxima pergunta igual/similar é respondida.
import { all, one, run } from "../db";
import { cosine, searchTokens, termFreq, type SparseVec } from "./text";

export type Article = { id: number; title: string; body: string; body_en: string; questions: string; tags: string; topic: string | null; uses: number; source: string };
export type Retrieval = {
  article: Article | null; score: number; similarity: number; coverage: number; missing: string[];
  via: "question" | "document" | "subject" | null; candidates: { id: number; title: string; score: number }[];
};

type Indexed = { a: Article; doc: SparseVec; qs: SparseVec[]; vocab: Set<string> };
let cache: { key: string; at: number; items: Indexed[]; idf: Map<string, number>; maxIdf: number } | null = null;

function weigh(tokens: string[], idf: Map<string, number>, maxIdf: number): SparseVec {
  const tf = termFreq(tokens);
  for (const [k, v] of tf) tf.set(k, (1 + Math.log(v)) * (idf.get(k) ?? maxIdf));
  return tf;
}

async function index(): Promise<{ items: Indexed[]; idf: Map<string, number>; maxIdf: number }> {
  // Com banco remoto (Turso), checar a versão da KB a cada ticket custa um round-trip: cache de 5s.
  if (cache && Date.now() - cache.at < 5000) return cache;
  const stamp = await one<{ n: number; m: number }>("SELECT COUNT(*) n, COALESCE(MAX(updated_at),0) m FROM kb_articles");
  const key = `${stamp?.n}-${stamp?.m}`;
  if (cache?.key === key) { cache.at = Date.now(); return cache; }
  const arts = await all<Article>("SELECT * FROM kb_articles");
  const docs = arts.map((a) => searchTokens(`${a.title} ${a.title} ${a.tags} ${a.body} ${a.questions}`));
  const df = new Map<string, number>();
  for (const d of docs) for (const t of new Set(d)) df.set(t, (df.get(t) ?? 0) + 1);
  const idf = new Map<string, number>();
  for (const [t, n] of df) idf.set(t, Math.log((arts.length + 1) / (n + 1)) + 1);
  const maxIdf = Math.log(arts.length + 1) + 1;
  const items = arts.map((a, i) => ({
    a,
    doc: weigh(docs[i], idf, maxIdf),
    qs: a.questions.split("\n").map((q) => q.trim()).filter(Boolean).map((q) => weigh(searchTokens(q), idf, maxIdf)),
    vocab: new Set(docs[i]),
  }));
  cache = { key, at: Date.now(), items, idf, maxIdf };
  return cache;
}

export function invalidateKbCache() { cache = null; }

/**
 * score = similaridade (cosseno) × cobertura.
 * Cobertura = fração do "peso informativo" (IDF) da pergunta que o artigo contém. Evita o falso
 * positivo clássico de busca lexical: "alterar endereço de cobrança na nota emitida" casando com
 * "formas de pagamento" só porque ambos falam de cobrança — os termos raros (endereço, emitida)
 * não estão no artigo, então a cobertura cai e o sistema admite que não sabe.
 */
export async function retrieve(query: string): Promise<Retrieval> {
  const { items, idf, maxIdf } = await index();
  const toks = searchTokens(query);
  const q = weigh(toks, idf, maxIdf);
  const uniq = [...new Set(toks)];
  const totalW = uniq.reduce((s, t) => s + (idf.get(t) ?? maxIdf), 0) || 1;
  const scored = items.map(({ a, doc, qs, vocab }) => {
    const d = cosine(q, doc);
    const qq = Math.max(0, ...qs.map((v) => cosine(q, v)));
    const sim = Math.max(d, qq);
    const covered = uniq.filter((t) => vocab.has(t));
    const coverage = covered.reduce((s, t) => s + (idf.get(t) ?? maxIdf), 0) / totalW;
    return { a, sim, coverage, score: sim * Math.sqrt(coverage), via: qq >= d ? ("question" as const) : ("document" as const), missing: uniq.filter((t) => !vocab.has(t)) };
  }).sort((x, y) => y.score - x.score);
  const best = scored[0];
  return {
    article: best && best.score > 0 ? best.a : null,
    score: best?.score ?? 0,
    similarity: best?.sim ?? 0,
    coverage: best?.coverage ?? 0,
    missing: best?.missing.slice(0, 6) ?? [],
    via: best ? best.via : null,
    candidates: scored.slice(0, 3).map((s) => ({ id: s.a.id, title: s.a.title, score: Number(s.score.toFixed(3)) })),
  };
}

/** Similaridade usada para agrupar perguntas (clustering de gaps / duplicatas). */
export function similarity(a: string, b: string): number {
  return cosine(termFreq(searchTokens(a)), termFreq(searchTokens(b)));
}

const GAP_CLUSTER_THRESHOLD = 0.4;

/** Registra (ou incrementa, se similar a um gap existente) um Knowledge Gap pendente. */
export async function registerGap(question: string, ticketId: string, topic: string, category: string, score: number, at = Date.now()) {
  const pending = await all<{ id: number; question: string; ticket_ids: string; examples: string }>(
    "SELECT id, question, ticket_ids, examples FROM kb_gaps WHERE status='pending'");
  let best: (typeof pending)[number] | null = null, bestSim = 0;
  // Single-linkage: compara com todas as variações já agrupadas no gap, não só a primeira.
  for (const g of pending) {
    const variants = [g.question, ...(JSON.parse(g.examples) as string[])];
    const s = Math.max(...variants.map((v) => similarity(question, v)));
    if (s > bestSim) { bestSim = s; best = g; }
  }
  if (best && bestSim >= GAP_CLUSTER_THRESHOLD) {
    const ids: string[] = JSON.parse(best.ticket_ids);
    const ex: string[] = JSON.parse(best.examples);
    if (!ids.includes(ticketId)) ids.push(ticketId);
    if (ex.length < 10 && !ex.includes(question)) ex.push(question);
    await run("UPDATE kb_gaps SET occurrences=occurrences+1, ticket_ids=?, examples=?, updated_at=? WHERE id=?",
      [JSON.stringify(ids.slice(-50)), JSON.stringify(ex), at, best.id]);
    return { id: best.id, clustered: true, similarity: bestSim };
  }
  const r = await run(
    "INSERT INTO kb_gaps (question, topic, category, occurrences, best_score, ticket_ids, examples, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
    [question, topic, category, 1, score, JSON.stringify([ticketId]), JSON.stringify([question]), at, at]);
  return { id: Number(r.lastInsertRowid), clustered: false, similarity: bestSim };
}
