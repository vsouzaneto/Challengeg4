import type { IncomingMessage, ServerResponse } from "node:http";
import {
  applyOpportunityFilters,
  average,
  groupAverages,
  roundOne,
  scoreDistribution,
  sortOpportunities,
  type OpportunityFilters,
  type OpportunitySort,
  type SortOrder,
} from "./analytics.js";
import {
  authenticateUser,
  clearLoginAttempts,
  createSession,
  deleteSession,
  getSessionUser,
  LoginRateLimitError,
  reserveLoginAttempt,
  type SessionUser,
} from "./auth.js";
import { config } from "./config.js";
import {
  HttpError,
  readJson,
  requireBoolean,
  requirePassword,
  requireString,
  sendJson,
} from "./http-utils.js";
import { getScoredOpportunities, loadScoringOpportunities } from "./scoring/scoring-service.js";
import type { ScoredOpportunity } from "./scoring/types.js";
import {
  createUser,
  listUsers,
  resetUserPassword,
  SelfDeactivationError,
  updateUser,
  UserConflictError,
} from "./users.js";

const sessionCookie = "lead_session";
const stages = new Set(["Prospecting", "Engaging", "Won", "Lost"]);
const scoreBandIds = new Set(["0-24", "25-49", "50-74", "75-100"]);
const sortFields = new Set<OpportunitySort>(["score", "account", "product", "stage"]);
const sortOrders = new Set<SortOrder>(["asc", "desc"]);

function parseCookies(request: IncomingMessage): Map<string, string> {
  const header = request.headers.cookie ?? "";
  return new Map(header.split(";").flatMap((part) => {
    const [name, ...value] = part.trim().split("=");
    if (!name || value.length === 0) {
      return [];
    }
    try {
      return [[name, decodeURIComponent(value.join("="))]];
    } catch {
      return [];
    }
  }));
}

function sessionToken(request: IncomingMessage): string | null {
  return parseCookies(request).get(sessionCookie) ?? null;
}

function cookieHeader(token: string, maxAge: number): string {
  const secure = config.secureCookies ? "; Secure" : "";
  return `${sessionCookie}=${encodeURIComponent(token)}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAge}${secure}`;
}

async function requireUser(request: IncomingMessage): Promise<SessionUser> {
  const token = sessionToken(request);
  const user = token ? await getSessionUser(token) : null;
  if (!user) {
    throw new HttpError(401, "Sessão inválida ou expirada.");
  }
  return user;
}

function requireMethod(request: IncomingMessage, methods: string[]): void {
  if (!methods.includes(request.method ?? "GET")) {
    throw new HttpError(405, "Método não permitido.");
  }
}

function queryValue(url: URL, key: string): string | undefined {
  const value = url.searchParams.get(key)?.trim();
  return value ? value : undefined;
}

function opportunityFilters(url: URL): OpportunityFilters {
  const stage = queryValue(url, "stage");
  const scoreBand = queryValue(url, "scoreBand");
  if (stage && !stages.has(stage)) {
    throw new HttpError(400, "Estágio inválido.");
  }
  if (scoreBand && !scoreBandIds.has(scoreBand)) {
    throw new HttpError(400, "Faixa de score inválida.");
  }
  return {
    search: queryValue(url, "search"),
    stage,
    product: queryValue(url, "product"),
    sector: queryValue(url, "sector"),
    seller: queryValue(url, "seller"),
    scoreBand,
  };
}

function compactOpportunity(item: ScoredOpportunity) {
  return {
    id: item.id,
    account: item.accountName,
    product: item.product,
    dealStage: item.dealStage,
    salesAgent: item.salesAgent,
    score: item.scoreResult.score,
    isHotLead: item.isHotLead,
  };
}

function detailedOpportunity(item: ScoredOpportunity) {
  return {
    id: item.id,
    account: item.accountName,
    sector: item.sector,
    employees: item.employees,
    revenue: item.revenue,
    product: item.product,
    series: item.series,
    salesPrice: item.salesPrice,
    dealStage: item.dealStage,
    salesAgent: item.salesAgent,
    manager: item.manager,
    regionalOffice: item.regionalOffice,
    engageDate: item.engageDate,
    closeDate: item.closeDate,
    closeValue: item.closeValue,
    isHotLead: item.isHotLead,
    score: item.scoreResult,
  };
}

async function dashboard() {
  const scored = await getScoredOpportunities();
  const open = scored.filter((item) => item.dealStage === "Prospecting" || item.dealStage === "Engaging");
  const availableValues = open.flatMap((item) => item.closeValue === null ? [] : [item.closeValue]);
  return {
    metrics: {
      openOpportunities: open.length,
      hotLeads: open.filter((item) => item.isHotLead).length,
      averageOpenScore: average(open),
      pipelineValue: availableValues.length ? roundOne(availableValues.reduce((total, value) => total + value, 0)) : null,
    },
    priorityOpportunities: sortOpportunities(open, "score", "desc").slice(0, 8).map(compactOpportunity),
    scoreDistribution: scoreDistribution(open),
    calculatedAt: open[0]?.scoreResult.calculatedAt ?? scored[0]?.scoreResult.calculatedAt ?? new Date().toISOString(),
  };
}

async function listOpportunities(url: URL) {
  const all = await getScoredOpportunities();
  const filtered = applyOpportunityFilters(all, opportunityFilters(url));
  const sortValue = queryValue(url, "sort") ?? "score";
  const orderValue = queryValue(url, "order") ?? "desc";
  if (!sortFields.has(sortValue as OpportunitySort) || !sortOrders.has(orderValue as SortOrder)) {
    throw new HttpError(400, "Ordenação inválida.");
  }
  const page = Math.max(1, Number(queryValue(url, "page") ?? 1));
  const pageSize = Math.min(100, Math.max(1, Number(queryValue(url, "pageSize") ?? 20)));
  if (!Number.isInteger(page) || !Number.isInteger(pageSize)) {
    throw new HttpError(400, "Paginação inválida.");
  }
  const sorted = sortOpportunities(filtered, sortValue as OpportunitySort, orderValue as SortOrder);
  const offset = (page - 1) * pageSize;
  return {
    data: sorted.slice(offset, offset + pageSize).map(compactOpportunity),
    pagination: {
      page,
      pageSize,
      total: filtered.length,
      totalPages: Math.max(1, Math.ceil(filtered.length / pageSize)),
    },
    calculatedAt: all[0]?.scoreResult.calculatedAt ?? new Date().toISOString(),
  };
}

async function filterOptions() {
  const opportunities = await loadScoringOpportunities();
  const unique = (values: Array<string | null>) => [...new Set(values.filter((value): value is string => value !== null))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  const sectors = unique(opportunities.map((item) => item.sector));
  if (opportunities.some((item) => item.sector === null)) {
    sectors.push("Não informado");
  }
  return {
    stages: [...stages],
    products: unique(opportunities.map((item) => item.product)),
    sectors: sectors.map((sector) => ({ id: sector === "Não informado" ? "unknown" : sector, label: sector })),
    sellers: unique(opportunities.map((item) => item.salesAgent)),
    scoreBands: [
      { id: "0-24", label: "0–24" },
      { id: "25-49", label: "25–49" },
      { id: "50-74", label: "50–74" },
      { id: "75-100", label: "75–100" },
    ],
  };
}

async function reports(url: URL) {
  const filters = opportunityFilters(url);
  delete filters.search;
  delete filters.scoreBand;
  const scored = applyOpportunityFilters(await getScoredOpportunities(), filters);
  const stageNames = ["Prospecting", "Engaging", "Won", "Lost"];
  const conversion = groupAverages(scored.filter((item) => item.dealStage === "Won" || item.dealStage === "Lost"), (item) => item.product)
    .map((product) => {
      const group = scored.filter((item) => item.product === product.name && (item.dealStage === "Won" || item.dealStage === "Lost"));
      const won = group.filter((item) => item.dealStage === "Won").length;
      const lost = group.length - won;
      return { ...product, won, lost, conversionRate: group.length ? roundOne((won / group.length) * 100) : 0 };
    })
    .sort((left, right) => right.conversionRate - left.conversionRate || left.name.localeCompare(right.name, "pt-BR"));

  return {
    distribution: scoreDistribution(scored),
    averageByProduct: groupAverages(scored, (item) => item.product),
    averageBySector: groupAverages(scored, (item) => item.sector ?? "Não informado"),
    pipelineByStage: stageNames.map((stage) => ({
      stage,
      count: scored.filter((item) => item.dealStage === stage).length,
    })),
    historicalConversionByProduct: conversion,
    total: scored.length,
    calculatedAt: scored[0]?.scoreResult.calculatedAt ?? new Date().toISOString(),
  };
}

function validateEmail(email: string): string {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/u.test(email)) {
    throw new HttpError(400, "E-mail inválido.");
  }
  return email;
}

export async function handleRequest(request: IncomingMessage, response: ServerResponse): Promise<void> {
  response.setHeader("X-Content-Type-Options", "nosniff");
  response.setHeader("Cache-Control", "no-store");

  try {
    const url = new URL(request.url ?? "/", "http://localhost");
    const path = url.pathname;

    if (path === "/api/health" && request.method === "GET") {
      const { pool } = await import("./database/pool.js");
      const { rows } = await pool.query("SELECT NOW() AS time, to_regclass('public.opportunities') AS opportunities");
      if (!rows[0]?.opportunities) {
        throw new HttpError(503, "Banco de dados ainda não está pronto.");
      }
      sendJson(response, 200, { status: "ok", database: "ok", time: rows[0].time });
      return;
    }

    if (path === "/api/auth/login" && request.method === "POST") {
      const body = await readJson<{ email?: unknown; password?: unknown }>(request);
      const email = validateEmail(requireString(body.email, "E-mail", { max: 256 }));
      const password = requirePassword(body.password);
      const source = request.socket.remoteAddress ?? "unknown";
      reserveLoginAttempt(email, source);
      const user = await authenticateUser(email, password);
      if (!user) {
        throw new HttpError(401, "E-mail ou senha inválidos.");
      }
      clearLoginAttempts(email, source);
      const session = await createSession(user.id, sessionToken(request) ?? undefined);
      sendJson(response, 200, { user }, { "Set-Cookie": cookieHeader(session.token, session.maxAge) });
      return;
    }

    if (path === "/api/auth/logout" && request.method === "POST") {
      const token = sessionToken(request);
      if (token) {
        await deleteSession(token);
      }
      sendJson(response, 200, { success: true }, { "Set-Cookie": cookieHeader("", 0) });
      return;
    }

    if (path === "/api/auth/session" && request.method === "GET") {
      const token = sessionToken(request);
      const user = token ? await getSessionUser(token) : null;
      sendJson(response, 200, { user });
      return;
    }

    const actor = await requireUser(request);

    if (path === "/api/dashboard" && request.method === "GET") {
      sendJson(response, 200, await dashboard());
      return;
    }

    if (path === "/api/opportunities" && request.method === "GET") {
      sendJson(response, 200, await listOpportunities(url));
      return;
    }

    if (path === "/api/opportunities/filters" && request.method === "GET") {
      sendJson(response, 200, await filterOptions());
      return;
    }

    const detailMatch = path.match(/^\/api\/opportunities\/([^/]+)$/u);
    if (detailMatch && request.method === "GET") {
      const opportunityId = detailMatch[1];
      if (!opportunityId) {
        throw new HttpError(404, "Oportunidade não encontrada.");
      }
      const opportunity = (await getScoredOpportunities({ ids: [decodeURIComponent(opportunityId)] }))[0];
      if (!opportunity) {
        throw new HttpError(404, "Oportunidade não encontrada.");
      }
      sendJson(response, 200, { data: detailedOpportunity(opportunity) });
      return;
    }

    if (path === "/api/reports" && request.method === "GET") {
      sendJson(response, 200, await reports(url));
      return;
    }

    if (path === "/api/users" && request.method === "GET") {
      sendJson(response, 200, { data: await listUsers() });
      return;
    }

    if (path === "/api/users" && request.method === "POST") {
      const body = await readJson<{ name?: unknown; email?: unknown; password?: unknown }>(request);
      const created = await createUser({
        name: requireString(body.name, "Nome", { min: 2, max: 120 }),
        email: validateEmail(requireString(body.email, "E-mail", { max: 256 })),
        password: requirePassword(body.password),
      });
      sendJson(response, 201, { data: created });
      return;
    }

    const userMatch = path.match(/^\/api\/users\/(\d+)$/u);
    if (userMatch && request.method === "PATCH") {
      const body = await readJson<{ name?: unknown; email?: unknown; isActive?: unknown }>(request);
      const updated = await updateUser(actor.id, Number(userMatch[1]), {
        name: requireString(body.name, "Nome", { min: 2, max: 120 }),
        email: validateEmail(requireString(body.email, "E-mail", { max: 256 })),
        isActive: requireBoolean(body.isActive, "Status"),
      });
      if (!updated) {
        throw new HttpError(404, "Usuário não encontrado.");
      }
      sendJson(response, 200, { data: updated });
      return;
    }

    const passwordMatch = path.match(/^\/api\/users\/(\d+)\/password$/u);
    if (passwordMatch && request.method === "POST") {
      const body = await readJson<{ password?: unknown }>(request);
      const updated = await resetUserPassword(Number(passwordMatch[1]), requirePassword(body.password));
      if (!updated) {
        throw new HttpError(404, "Usuário não encontrado.");
      }
      sendJson(response, 200, { success: true });
      return;
    }

    requireMethod(request, ["GET"]);
    throw new HttpError(404, "Recurso não encontrado.");
  } catch (error) {
    if (error instanceof HttpError) {
      sendJson(response, error.status, { error: error.message });
      return;
    }
    if (error instanceof UserConflictError) {
      sendJson(response, 409, { error: error.message });
      return;
    }
    if (error instanceof SelfDeactivationError) {
      sendJson(response, 400, { error: error.message });
      return;
    }
    if (error instanceof LoginRateLimitError) {
      sendJson(response, 429, { error: error.message });
      return;
    }
    console.error(error);
    sendJson(response, 500, { error: "Erro interno do servidor." });
  }
}
