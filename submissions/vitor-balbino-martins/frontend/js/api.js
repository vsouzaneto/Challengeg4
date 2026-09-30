/**
 * Cliente HTTP da API v1.
 *
 * Todas as chamadas vao sem credenciais: o backend responde
 * `Access-Control-Allow-Origin: *`, que o navegador recusa em requisicoes
 * credenciadas. Nao adicione `credentials: "include"` sem antes fixar
 * `CORS_ORIGINS` em uma origem explicita no backend.
 */

import { getApiBase, TIMEOUTS } from "./config.js";

/** Erro com a mensagem ja normalizada para exibicao. */
export class ApiError extends Error {
  constructor(message, { status = 0, code = null, detail = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

/**
 * Converte o corpo de erro do FastAPI em uma frase unica.
 * Formatos possiveis:
 *   { detail: "texto" }                      -> HTTPException
 *   { code, detail: "texto" }                -> AppException
 *   { code, detail: [{ field, msg }] }       -> RequestValidationError
 *   { detail: [{ loc, msg }] }               -> validacao sem handler
 */
function describe(payload, status) {
  const detail = payload?.detail;

  if (typeof detail === "string" && detail.trim()) return detail;

  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((item) => {
        const field = item?.field ?? (Array.isArray(item?.loc) ? item.loc.join(".") : null);
        const msg = item?.msg ?? JSON.stringify(item);
        return field ? `${field}: ${msg}` : msg;
      })
      .join(" | ");
  }

  if (typeof payload?.message === "string" && payload.message.trim()) return payload.message;

  return `A API respondeu ${status}.`;
}

/**
 * @param {string} path            caminho relativo ao prefixo, ex. "/rag/search"
 * @param {object} options
 * @param {"GET"|"POST"} [options.method]
 * @param {object}  [options.body]     serializado como JSON
 * @param {number}  [options.timeout]  ms; 0 ou omitido = sem limite
 * @param {AbortSignal} [options.signal] permite cancelamento pelo usuario
 */
export async function request(path, { method = "GET", body, timeout = 0, signal } = {}) {
  const url = `${getApiBase()}${path}`;
  const controller = new AbortController();

  const onAbort = () => controller.abort(signal?.reason);
  if (signal) {
    if (signal.aborted) controller.abort(signal.reason);
    else signal.addEventListener("abort", onAbort, { once: true });
  }

  const timer = timeout > 0 ? setTimeout(() => controller.abort(new Error("timeout")), timeout) : null;

  let response;
  try {
    response = await fetch(url, {
      method,
      signal: controller.signal,
      headers: body === undefined ? { Accept: "application/json" }
                                  : { Accept: "application/json", "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (error) {
    if (controller.signal.aborted) {
      // Cancelamento pelo usuario propaga como AbortError para o chamador ignorar.
      if (signal?.aborted) throw error;
      throw new ApiError(
        `A requisicao excedeu ${Math.round(timeout / 1000)}s e foi interrompida.`,
        { code: "TIMEOUT" },
      );
    }
    throw new ApiError(
      `Nao foi possivel falar com ${url}. Verifique se o backend esta no ar e se a origem do frontend e aceita pelo CORS.`,
      { code: "NETWORK" },
    );
  } finally {
    if (timer) clearTimeout(timer);
    if (signal) signal.removeEventListener("abort", onAbort);
  }

  const raw = await response.text();
  let payload = null;
  if (raw) {
    try { payload = JSON.parse(raw); } catch { payload = null; }
  }

  if (!response.ok) {
    throw new ApiError(describe(payload, response.status), {
      status: response.status,
      code: payload?.code ?? null,
      detail: payload?.detail ?? raw.slice(0, 400) ?? null,
    });
  }

  return payload;
}

/* -- Endpoints ---------------------------------------------------------- */

export const api = {
  health: () => request("/health", { timeout: TIMEOUTS.health }),

  dashboard: () => request("/dashboard", { timeout: TIMEOUTS.health }),

  syncDashboard: (body) => request("/dashboard/sync", { method: "POST", body, timeout: 120_000 }),

  tickets: (stage) => request(`/dashboard/tickets${stage ? `?stage=${encodeURIComponent(stage)}` : ""}`, { timeout: TIMEOUTS.health }),

  moveTicket: (ticketId, stage) => request(`/dashboard/tickets/${encodeURIComponent(ticketId)}/stage`, { method: "PATCH", body: { stage }, timeout: TIMEOUTS.health }),

  supportReport: (body, signal) =>
    request("/reports/support", { method: "POST", body, timeout: TIMEOUTS.report, signal }),

  satisfaction: (signal) =>
    request("/reports/satisfaction", { method: "POST", timeout: TIMEOUTS.satisfaction, signal }),

  improvements: (body, signal) =>
    request("/reports/improvements", { method: "POST", body, timeout: TIMEOUTS.report, signal }),

  clustering: (body, signal) =>
    request("/clustering", { method: "POST", body, timeout: TIMEOUTS.clustering, signal }),

  ragSearch: (body, signal) =>
    request("/rag/search", { method: "POST", body, timeout: TIMEOUTS.ragSearch, signal }),

  ragIndex: () => request("/rag/index", { method: "POST", timeout: TIMEOUTS.ragIndex }),

  ragIndexStatus: () => request("/rag/index/status", { timeout: TIMEOUTS.ragStatus }),
};
