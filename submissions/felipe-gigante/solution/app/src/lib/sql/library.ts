// Biblioteca de consultas para quando não há LLM configurado: casa a pergunta com intenções
// conhecidas e monta o SQL (com período). Com LLM, a pergunta livre vira SQL via modelo.
export type LibraryHit = { sql: string; explanation: string };

const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

function period(q: string): { where: string; label: string } {
  const m = q.match(/(\d+)\s*(dia|d\b)/);
  let days = m ? Number(m[1]) : /\bhoje|24 ?h/.test(q) ? 1 : /semana/.test(q) ? 7 : /trimestre/.test(q) ? 90 : /\bmes\b/.test(q) ? 30 : /(tudo|todo|historico|sempre)/.test(q) ? 0 : 30;
  days = Math.min(days, 3650);
  return days
    ? { where: `created_at >= (CAST(strftime('%s','now') AS INTEGER) - ${days} * 86400) * 1000`, label: `nos últimos ${days} dia${days > 1 ? "s" : ""}` }
    : { where: "1=1", label: "em todo o histórico" };
}

// Mesma taxonomia canônica do dashboard (risk.ts → ESCALATION_CATEGORIES), em SQL.
const REASON_CASE = `CASE
  WHEN j.value LIKE '%reembolso%' OR j.value LIKE '%chargeback%' THEN 'Reembolso / chargeback'
  WHEN j.value LIKE '%cancelamento%' OR j.value LIKE '%churn%' THEN 'Cancelamento (churn)'
  WHEN j.value LIKE '%urídico%' OR j.value LIKE '%regulat%' THEN 'Jurídico / regulatório'
  WHEN j.value LIKE '%fraude%' OR j.value LIKE '%comprometida%' THEN 'Fraude / conta comprometida'
  WHEN j.value LIKE '%perda de dados%' THEN 'Perda de dados'
  WHEN j.value LIKE '%LGPD%' OR j.value LIKE '%dados pessoais%' THEN 'Dados pessoais (LGPD)'
  WHEN j.value LIKE '%emocional%' OR j.value LIKE '%frustra%' THEN 'Cliente irritado / frustração'
  WHEN j.value LIKE '%cobrança%' THEN 'Cobrança'
  ELSE j.value END`;

type Intent = { test: (q: string) => boolean; build: (w: string, label: string) => LibraryHit };

const INTENTS: Intent[] = [
  { test: (q) => /(csat|satisfa|nota)/.test(q) && /canal/.test(q), build: (w, l) => ({ explanation: `CSAT médio por canal ${l}.`, sql: `SELECT channel AS canal, ROUND(AVG(csat), 2) AS csat_medio, COUNT(csat) AS avaliacoes FROM tickets WHERE csat IS NOT NULL AND ${w} GROUP BY channel ORDER BY csat_medio DESC` }) },
  { test: (q) => /(csat|satisfa|nota)/.test(q) && /(decisao|automa|ia\b)/.test(q), build: (w, l) => ({ explanation: `CSAT por decisão do gate ${l} — automação está melhorando a experiência?`, sql: `SELECT decision AS decisao, ROUND(AVG(csat), 2) AS csat_medio, COUNT(csat) AS avaliacoes FROM tickets WHERE csat IS NOT NULL AND ${w} GROUP BY decision` }) },
  { test: (q) => /(csat|satisfa|nota)/.test(q), build: (w, l) => ({ explanation: `CSAT médio por assunto ${l}.`, sql: `SELECT topic AS assunto, ROUND(AVG(csat), 2) AS csat_medio, COUNT(csat) AS avaliacoes FROM tickets WHERE csat IS NOT NULL AND ${w} GROUP BY topic ORDER BY csat_medio` }) },
  { test: (q) => /(escal|humano)/.test(q) && /(motivo|por que|porque|razao)/.test(q), build: (w, l) => ({ explanation: `Motivos de escalonamento para humano ${l}.`, sql: `SELECT ${REASON_CASE} AS motivo, COUNT(DISTINCT tickets.id) AS tickets FROM tickets, json_each(tickets.risk_reasons) j WHERE decision = 'human' AND risk_level = 'HIGH' AND ${w} GROUP BY motivo ORDER BY tickets DESC` }) },
  { test: (q) => /(automa|decisao|gate)/.test(q) && /(assunto|categoria|topico|tema)/.test(q), build: (w, l) => ({ explanation: `% de cada decisão do gate por assunto ${l}.`, sql: `SELECT topic AS assunto, COUNT(*) AS tickets, ROUND(100.0 * SUM(decision='auto') / COUNT(*), 1) AS pct_auto, ROUND(100.0 * SUM(decision='suggest') / COUNT(*), 1) AS pct_sugestao, ROUND(100.0 * SUM(decision='human') / COUNT(*), 1) AS pct_humano FROM tickets WHERE ${w} GROUP BY topic ORDER BY pct_humano DESC` }) },
  { test: (q) => /(automa|decisao|gate|escal)/.test(q), build: (w, l) => ({ explanation: `Distribuição das decisões do gate ${l}.`, sql: `SELECT decision AS decisao, COUNT(*) AS tickets, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct FROM tickets WHERE ${w} GROUP BY decision ORDER BY tickets DESC` }) },
  { test: (q) => /(volume|tickets|chamados).*(dia|diario)|por dia/.test(q), build: (w, l) => ({ explanation: `Volume de tickets por dia ${l}.`, sql: `SELECT date(created_at / 1000, 'unixepoch') AS dia, COUNT(*) AS tickets FROM tickets WHERE ${w} GROUP BY dia ORDER BY dia` }) },
  { test: (q) => /(gap|sem resposta|nao respond|knowledge|lacuna)/.test(q), build: () => ({ explanation: "Knowledge Gaps pendentes, ordenados por ocorrências.", sql: `SELECT question AS pergunta, occurrences AS ocorrencias, topic AS intencao FROM kb_gaps WHERE status = 'pending' ORDER BY occurrences DESC` }) },
  { test: (q) => /(artigo|kb\b|base de conhecimento)/.test(q), build: (w, l) => ({ explanation: `Artigos da KB mais usados pelos tickets ${l}.`, sql: `SELECT a.title AS artigo, COUNT(t.id) AS tickets FROM kb_articles a LEFT JOIN tickets t ON t.kb_article_id = a.id AND ${w.replace("created_at", "t.created_at")} GROUP BY a.id ORDER BY tickets DESC` }) },
  { test: (q) => /sentimento/.test(q) && /canal/.test(q), build: (w, l) => ({ explanation: `Sentimento por canal ${l}.`, sql: `SELECT channel AS canal, ROUND(AVG(sentiment_score), 1) AS sentimento_medio, SUM(sentiment IN ('Frustrated','Angry')) AS negativos, COUNT(*) AS tickets FROM tickets WHERE ${w} GROUP BY channel ORDER BY sentimento_medio` }) },
  { test: (q) => /sentimento|frustr|irritad|raiva/.test(q), build: (w, l) => ({ explanation: `Distribuição de sentimento ${l}.`, sql: `SELECT sentiment AS sentimento, COUNT(*) AS tickets FROM tickets WHERE ${w} GROUP BY sentiment ORDER BY tickets DESC` }) },
  { test: (q) => /(critic|urgente)/.test(q) && /(abert|pendente|sem resposta|parad|fila)/.test(q), build: (w, l) => ({ explanation: `Tickets Critical ainda em aberto ${l}.`, sql: `SELECT id, customer_name AS cliente, subject AS assunto, status, assignee AS responsavel FROM tickets WHERE priority = 'Critical' AND status IN ('new','open','escalated','pending') AND ${w} ORDER BY created_at DESC` }) },
  { test: (q) => /(tempo|resolu|ttr|demora)/.test(q), build: (w, l) => ({ explanation: `Tempo médio de resolução (horas) por prioridade ${l} — só tickets com duração válida.`, sql: `SELECT priority AS prioridade, ROUND(AVG((resolved_at - created_at) / 3600000.0), 1) AS horas_media, COUNT(*) AS tickets FROM tickets WHERE resolved_at IS NOT NULL AND ${w} GROUP BY priority ORDER BY horas_media DESC` }) },
  { test: (q) => /(categoria|time|roteament|equipe)/.test(q), build: (w, l) => ({ explanation: `Tickets por categoria e time ${l}.`, sql: `SELECT category AS categoria, team AS time, COUNT(*) AS tickets FROM tickets WHERE ${w} GROUP BY category, team ORDER BY tickets DESC` }) },
  { test: (q) => /canal/.test(q), build: (w, l) => ({ explanation: `Tickets por canal ${l}.`, sql: `SELECT channel AS canal, COUNT(*) AS tickets FROM tickets WHERE ${w} GROUP BY channel ORDER BY tickets DESC` }) },
  { test: (q) => /produto/.test(q), build: (w, l) => ({ explanation: `Produtos com mais tickets ${l}.`, sql: `SELECT product AS produto, COUNT(*) AS tickets FROM tickets WHERE product IS NOT NULL AND ${w} GROUP BY product ORDER BY tickets DESC LIMIT 15` }) },
  { test: (q) => /prioridade/.test(q), build: (w, l) => ({ explanation: `Tickets por prioridade calculada pela IA ${l}.`, sql: `SELECT priority AS prioridade, COUNT(*) AS tickets FROM tickets WHERE ${w} GROUP BY priority ORDER BY tickets DESC` }) },
  { test: (q) => /(assunto|topico|tema|pergunta|duvida|motivo)/.test(q), build: (w, l) => ({ explanation: `Principais assuntos ${l}.`, sql: `SELECT topic AS assunto, COUNT(*) AS tickets FROM tickets WHERE ${w} GROUP BY topic ORDER BY tickets DESC` }) },
];

export function matchLibrary(question: string): LibraryHit | null {
  const q = norm(question);
  const hit = INTENTS.find((i) => i.test(q));
  if (!hit) return null;
  const p = period(q);
  return hit.build(p.where, p.label);
}

export const SUGGESTED_QUESTIONS = [
  "Quais os principais assuntos nos últimos 7 dias?",
  "Por que a IA escalou para humano nos últimos 30 dias?",
  "% de automação por assunto",
  "CSAT médio por canal",
  "Volume de tickets por dia nos últimos 30 dias",
  "Tickets críticos em aberto",
  "Perguntas sem resposta (knowledge gaps)",
  "Sentimento por canal na última semana",
  "Tempo de resolução por prioridade em todo o histórico",
  "Artigos da KB mais usados",
];
