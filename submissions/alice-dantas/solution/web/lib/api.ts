// Cliente da API: toda resposta passa pela validação gerada do contrato antes de chegar à tela.
import type { ZodType } from "zod";

import { CONTRACT_ERROR, errorText, httpError, networkError } from "@/copy/pt-BR";
import type {
  Evidence, Intelligence, IntelligenceDeals, IntelligenceFilter, Meta, Rules, SellerList, SellerPipeline, TeamPipeline,
} from "@/lib/contract";
import {
  zErrorBody, zEvidence, zIntelligence, zIntelligenceDeals, zMeta, zRules, zSellerList, zSellerPipeline, zTeamPipeline,
} from "@/lib/contract/zod.gen";
import { type DealOutcome, apiQuery } from "@/lib/intelligence";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {}

/** Busca e valida. O tipo de retorno é o do contrato: o schema zod foi gerado do mesmo openapi.json. */
async function getJson<T>(path: string, schema: ZodType): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`);
  } catch {
    throw new ApiError(networkError(API_URL));
  }
  const body: unknown = await response.json().catch(() => undefined);
  if (!response.ok) {
    const error = zErrorBody.safeParse(body);
    throw new ApiError(error.success ? errorText(error.data) : httpError(response.status));
  }
  const parsed = schema.safeParse(body);
  if (!parsed.success) throw new ApiError(CONTRACT_ERROR);
  return parsed.data as T;
}

export const api = {
  sellers: () => getJson<SellerList>("/api/sellers", zSellerList),
  meta: () => getJson<Meta>("/api/meta", zMeta),
  sellerPipeline: (seller: string) =>
    getJson<SellerPipeline>(`/api/sellers/${encodeURIComponent(seller)}/pipeline`, zSellerPipeline),
  teamPipeline: (filter: { manager?: string | null; office?: string | null }) => {
    const query = new URLSearchParams();
    if (filter.manager) query.set("manager", filter.manager);
    if (filter.office) query.set("office", filter.office);
    const suffix = query.toString();
    return getJson<TeamPipeline>(`/api/pipeline${suffix ? `?${suffix}` : ""}`, zTeamPipeline);
  },
  rules: () => getJson<Rules>("/api/rules", zRules),
  evidence: () => getJson<Evidence>("/api/evidence", zEvidence),
  intelligence: (filter: IntelligenceFilter) => {
    const suffix = apiQuery(filter).toString();
    return getJson<Intelligence>(`/api/intelligence${suffix ? `?${suffix}` : ""}`, zIntelligence);
  },
  intelligenceDeals: (filter: IntelligenceFilter, outcome: DealOutcome, group?: string | null) => {
    const query = apiQuery(filter);
    query.set("outcome", outcome);
    if (group) query.set("group", group);
    return getJson<IntelligenceDeals>(`/api/intelligence/deals?${query}`, zIntelligenceDeals);
  },
};
