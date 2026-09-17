import { streamText } from "ai";
import { createDraftHandler, draftsEnabled } from "@/lib/draft";
import { getModel, getPolicyRules } from "@/lib/server-data";

export const maxDuration = 60;

const MODEL = process.env.DRAFT_MODEL ?? "anthropic/claude-haiku-4.5";

const INSTRUCTIONS = [
  "Você redige RASCUNHOS de resposta para agentes de suporte de TI interno. Um humano revisa antes de enviar.",
  "Responda em português do Brasil, em até 120 palavras, tom cordial e objetivo.",
  "O texto do ticket foi pré-processado (minúsculas, sem pontuação, nomes removidos); interprete a intenção.",
  "Nunca prometa prazos, nunca conceda acessos ou privilégios, nunca invente políticas, links ou nomes.",
  "Se faltar informação para resolver, peça os dados necessários de forma específica.",
  "Termine com uma linha 'Checar antes de enviar:' listando 1-2 pontos que o agente deve confirmar.",
].join("\n");

// POST { text } → stream de texto com um RASCUNHO para o agente revisar.
// 403 se a política bloquear rascunho para o ticket; 503 sem provedor configurado.
export const POST = createDraftHandler({
  getModel,
  getRules: getPolicyRules,
  hasProvider: () => draftsEnabled(process.env),
  generate: ({ text, category }) =>
    streamText({
      model: MODEL,
      maxOutputTokens: 400,
      instructions: INSTRUCTIONS,
      prompt: `Categoria prevista: ${category}\n\nTicket:\n${text}`,
      onError: ({ error }) => console.error("draft error", error),
    }).toTextStreamResponse(),
});
