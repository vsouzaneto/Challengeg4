// Sentimento como sinal operacional em tempo real (não substitui CSAT).
// Léxico bilíngue + sinais de frustração operacional (repetição de contato, tempo esperando, caixa alta).
// Em produção a cascata usa LLM barato; este baseline é determinístico, gratuito e auditável.

export type SentimentLabel = "Positive" | "Neutral" | "Frustrated" | "Angry";
export type Sentiment = { label: SentimentLabel; score: number; signals: string[] };

const POS = ["thanks", "thank you", "great", "awesome", "love", "perfect", "excellent", "resolved", "works now", "appreciate",
  "obrigado", "obrigada", "ótimo", "otimo", "perfeito", "excelente", "adorei", "resolvido", "funcionou", "valeu", "top"];
const NEG = ["not working", "doesn't work", "does not work", "broken", "error", "issue", "problem", "fail", "can't", "cannot", "unable",
  "bad", "slow", "crash", "lost", "wrong", "não funciona", "nao funciona", "não consigo", "nao consigo", "erro", "problema",
  "quebrado", "falha", "lento", "travando", "perdi", "errado", "ruim"];
const ANGRY = ["ridiculous", "unacceptable", "terrible", "worst", "useless", "scam", "fraud", "furious", "angry", "disgusting", "lawyer", "sue",
  "absurdo", "inaceitável", "inaceitavel", "péssimo", "pessimo", "horrível", "horrivel", "palhaçada", "palhacada", "vergonha",
  "golpe", "procon", "reclame aqui", "advogado", "processar", "lixo", "raiva"];
const FRUSTRATION = [
  [/\b(again|still|third time|second time|already (contacted|tried|sent)|every time|days|weeks)\b/i, "contato repetido / espera"],
  [/\b(de novo|novamente|ainda|terceira vez|segunda vez|já (falei|tentei|enviei|liguei)|toda vez|dias|semanas)\b/i, "contato repetido / espera"],
  [/\b(urgent|asap|immediately|urgente|agora|imediatamente)\b/i, "urgência"],
] as const;

// Bug encontrado no seed: "sue" casava como substring de "issue" e marcava ~todos os tickets como ameaça.
// Matching agora respeita fronteira de palavra (Unicode-aware).
const esc = (w: string) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const rx = (words: string[]) => words.map((w) => new RegExp(`(?<![\\p{L}])${esc(w)}(?![\\p{L}])`, "iu"));
const POS_RX = rx(POS), NEG_RX = rx(NEG), ANGRY_RX = rx(ANGRY);
function count(text: string, words: RegExp[]) {
  return words.reduce((n, re) => n + (re.test(text) ? 1 : 0), 0);
}

export function analyzeSentiment(raw: string): Sentiment {
  const text = raw.toLowerCase();
  const signals: string[] = [];
  let score = 60;
  const p = count(text, POS_RX), n = count(text, NEG_RX), a = count(text, ANGRY_RX);
  // Descrever um problema não é estar irritado: termos de problema pesam pouco e são limitados.
  score += p * 12 - Math.min(n * 4, 12) - a * 18;
  if (p) signals.push(`+${p} termos positivos`);
  if (n) signals.push(`${n} termos de problema`);
  if (a) signals.push(`${a} termos de raiva/ameaça`);
  for (const [re, label] of FRUSTRATION) {
    if (re.test(raw)) { score -= 7; if (!signals.includes(label)) signals.push(label); }
  }
  const letters = raw.replace(/[^A-Za-zÀ-ÿ]/g, "");
  const caps = letters.length > 12 ? (raw.replace(/[^A-ZÀ-Ý]/g, "").length / letters.length) : 0;
  if (caps > 0.5) { score -= 12; signals.push("CAIXA ALTA"); }
  const bangs = (raw.match(/!/g) ?? []).length;
  if (bangs >= 2) { score -= Math.min(12, bangs * 3); signals.push("exclamações"); }
  score = Math.max(0, Math.min(100, Math.round(score)));
  const label: SentimentLabel = score >= 65 ? "Positive" : score >= 40 ? "Neutral" : score >= 22 ? "Frustrated" : "Angry";
  return { label, score, signals };
}

/** Tendência na conversa: queda progressiva gera o evento "Customer frustration detected". */
export function frustrationTrend(scores: number[]): { dropping: boolean; delta: number } {
  if (scores.length < 2) return { dropping: false, delta: 0 };
  const last = scores.slice(-3);
  const delta = last[last.length - 1] - last[0];
  const monotonic = last.every((s, i) => i === 0 || s <= last[i - 1]);
  return { dropping: (monotonic && delta <= -15) || last[last.length - 1] < 22, delta };
}
