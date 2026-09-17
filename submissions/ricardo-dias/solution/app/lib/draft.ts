// Rascunho de resposta com a política aplicada NO SERVIDOR.
// O cliente envia só o texto; categoria e permissão são recalculadas aqui, antes de qualquer
// chamada ao provedor de LLM. A categoria enviada pelo cliente é ignorada.

import { classifyTicket } from "./classifier";
import type { Model, PolicyRules } from "./model-schema";
import type { Category } from "./types";
import { readJsonObject, validateText } from "./validation";

// Rascunho só liga com opt-in explícito. Na Vercel o token OIDC pode existir automaticamente;
// sem DRAFTS_ENABLED=true um link público nunca gera chamadas pagas ao LLM.
export function draftsEnabled(env: Record<string, string | undefined>): boolean {
  return env.DRAFTS_ENABLED === "true" && Boolean(env.AI_GATEWAY_API_KEY || env.VERCEL_OIDC_TOKEN);
}

export interface DraftDeps {
  getModel: () => Model;
  getRules: () => PolicyRules;
  hasProvider: () => boolean;
  generate: (input: { text: string; category: Category }) => Response | Promise<Response>;
}

export function createDraftHandler(deps: DraftDeps) {
  return async function POST(request: Request): Promise<Response> {
    const parsed = await readJsonObject(request);
    if (!parsed.ok) return Response.json({ error: parsed.error }, { status: parsed.status });
    const input = validateText(parsed.body.text);
    if (!input.ok) return Response.json({ error: input.error }, { status: input.status });

    const result = classifyTicket(deps.getModel(), deps.getRules(), input.text, null);
    if (!result.draftAllowed) {
      return Response.json(
        {
          error: "Rascunho bloqueado pela política: este ticket é respondido por um atendente sênior.",
          route: result.route,
          routeReason: result.routeReason,
        },
        { status: 403 },
      );
    }
    if (!deps.hasProvider()) {
      return Response.json(
        {
          error:
            "Rascunho com IA desativado nesta versão de demonstração. A classificação e o roteamento funcionam sem LLM.",
        },
        { status: 503 },
      );
    }
    const response = await deps.generate({ text: input.text, category: result.category });
    response.headers.set("X-Draft-Category", result.category);
    return response;
  };
}
