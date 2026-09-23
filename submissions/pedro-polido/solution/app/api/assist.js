// Vercel Function: as duas tarefas em que o LLM agrega ao classificador.
//   translate: ticket em qualquer idioma -> inglês, para entrar no mesmo classificador (treinado em inglês)
//   draft:     rascunho de resposta em PT-BR + resumo interno + perguntas, sempre para revisão humana
// GET devolve se o Gemini está configurado (o front desliga os botões quando não está).

const MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
const ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
const MAX_CHARS = 4000;
const QUEUES = ['Access', 'Administrative rights', 'HR Support', 'Hardware', 'Internal Project', 'Miscellaneous', 'Purchase', 'Storage'];

// Limite simples por IP (melhor esforço: cada instância serverless tem a própria memória).
const WINDOW_MS = 10 * 60 * 1000;
const MAX_REQUESTS = 20;
const hits = new Map();
function rateLimited(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  recent.push(now);
  hits.set(ip, recent);
  return recent.length > MAX_REQUESTS;
}

const TASKS = {
  translate: {
    system: 'Você traduz tickets de suporte de TI para o inglês. A tradução alimenta um classificador treinado com '
      + 'tickets corporativos em inglês. Traduza fielmente o pedido, com o vocabulário técnico usual de TI em inglês '
      + '(laptop, password, access, mailbox, purchase order, license, install). Não acrescente detalhes. Responda só o JSON.',
    schema: {
      type: 'OBJECT',
      properties: { idioma: { type: 'STRING' }, traducao_en: { type: 'STRING' } },
      required: ['idioma', 'traducao_en'],
    },
    prompt: (b) => b.text,
  },
  draft: {
    system: 'Você é atendente do suporte interno de TI de uma empresa brasileira e escreve RASCUNHOS que um atendente '
      + 'humano revisa antes de enviar. Regras: (1) nunca prometa prazo e nunca diga que um acesso ou direito de '
      + 'administrador foi concedido, porque concessão exige aprovação humana; (2) se o pedido estiver vago, agradeça e '
      + 'peça exatamente o que falta; (3) se o tema for sensível, seja acolhedor, não peça detalhes pessoais por este canal '
      + 'e diga que uma pessoa do time vai tratar diretamente; (4) se for senha ou bloqueio, oriente o autoatendimento de '
      + 'redefinição usando o marcador [link do portal], sem inventar URL; (5) no máximo 110 palavras, tom cordial e direto, '
      + 'em português do Brasil. Inclua um resumo interno de uma frase e até 3 perguntas ao solicitante, se faltar informação.',
    schema: {
      type: 'OBJECT',
      properties: {
        resumo_interno: { type: 'STRING' },
        resposta_cliente: { type: 'STRING' },
        perguntas: { type: 'ARRAY', items: { type: 'STRING' } },
      },
      required: ['resumo_interno', 'resposta_cliente', 'perguntas'],
    },
    prompt: (b) => [
      `Fila prevista pelo classificador: ${QUEUES.includes(b.fila) ? b.fila : 'desconhecida'}`,
      `Faixa de decisão: ${String(b.faixa || '').slice(0, 40)}`,
      `Tema sensível: ${b.sensivel ? 'sim' : 'não'} | Pedido vago: ${b.vazio ? 'sim' : 'não'} | Senha ou bloqueio: ${b.autoatendimento ? 'sim' : 'não'}`,
      'Ticket (pode estar pré-processado, sem pontuação):',
      b.text,
    ].join('\n'),
  },
};

async function gemini(task, body, key) {
  const r = await fetch(ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key },
    body: JSON.stringify({
      systemInstruction: { parts: [{ text: task.system }] },
      contents: [{ role: 'user', parts: [{ text: task.prompt(body) }] }],
      generationConfig: { temperature: 0.2, maxOutputTokens: 2048, responseMimeType: 'application/json', responseSchema: task.schema },
    }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error?.message || `Gemini respondeu ${r.status}`);
  const text = data.candidates?.[0]?.content?.parts?.map((p) => p.text || '').join('') || '';
  return { ...JSON.parse(text), modelo: MODEL, tokens: data.usageMetadata?.totalTokenCount ?? 0 };
}

export default async function handler(req, res) {
  const key = process.env.GEMINI_API_KEY;
  if (req.method === 'GET') return res.status(200).json({ ok: Boolean(key), modelo: MODEL });
  if (req.method !== 'POST') return res.status(405).json({ error: 'use POST' });
  if (!key) return res.status(503).json({ error: 'GEMINI_API_KEY não configurada' });

  const ip = String(req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '').split(',')[0].trim();
  if (rateLimited(ip)) return res.status(429).json({ error: 'muitas requisições; tente de novo em alguns minutos' });

  const body = req.body || {};
  const task = TASKS[body.mode];
  if (!task) return res.status(400).json({ error: 'mode deve ser translate ou draft' });
  if (typeof body.text !== 'string' || !body.text.trim() || body.text.length > MAX_CHARS) {
    return res.status(400).json({ error: `text obrigatório, até ${MAX_CHARS} caracteres` });
  }
  try {
    return res.status(200).json(await gemini(task, body, key));
  } catch (e) {
    return res.status(502).json({ error: e.message });
  }
}
