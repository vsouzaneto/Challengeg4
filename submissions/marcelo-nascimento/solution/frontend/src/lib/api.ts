import type {
  ApplicationUser,
  DashboardData,
  FilterOptions,
  OpportunityDetail,
  PaginatedOpportunities,
  ReportData,
  User,
} from "../types.js";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const externalSignal = options.signal;
  let timedOut = false;
  const abortFromExternal = () => controller.abort();
  externalSignal?.addEventListener("abort", abortFromExternal, { once: true });
  const timeout = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, 20_000);

  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      signal: controller.signal,
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(0, timedOut ? "A conexão demorou demais. Tente novamente." : "A solicitação foi cancelada.");
    }
    throw new ApiError(0, "Não foi possível conectar ao servidor.");
  } finally {
    window.clearTimeout(timeout);
    externalSignal?.removeEventListener("abort", abortFromExternal);
  }

  const payload = await response.json().catch(() => ({ error: "Resposta inválida do servidor." })) as { error?: string } & T;
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/auth/login")) {
      window.dispatchEvent(new Event("leadscore:unauthorized"));
    }
    throw new ApiError(response.status, payload.error ?? "Não foi possível concluir a operação.");
  }
  return payload;
}

export const api = {
  session: () => request<{ user: User | null }>("/auth/session"),
  login: (email: string, password: string) => request<{ user: User }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  }),
  logout: () => request<{ success: boolean }>("/auth/logout", { method: "POST" }),
  dashboard: (signal?: AbortSignal) => request<DashboardData>("/dashboard", { signal }),
  opportunityFilters: (signal?: AbortSignal) => request<FilterOptions>("/opportunities/filters", { signal }),
  opportunities: (query: URLSearchParams, signal?: AbortSignal) => request<PaginatedOpportunities>(`/opportunities?${query.toString()}`, { signal }),
  opportunity: (id: string, signal?: AbortSignal) => request<{ data: OpportunityDetail }>(`/opportunities/${encodeURIComponent(id)}`, { signal }),
  reports: (query: URLSearchParams, signal?: AbortSignal) => request<ReportData>(`/reports?${query.toString()}`, { signal }),
  users: () => request<{ data: ApplicationUser[] }>("/users"),
  createUser: (input: { name: string; email: string; password: string }) => request<{ data: ApplicationUser }>("/users", {
    method: "POST",
    body: JSON.stringify(input),
  }),
  updateUser: (id: number, input: { name: string; email: string; isActive: boolean }) => request<{ data: ApplicationUser }>(`/users/${id}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  }),
  resetPassword: (id: number, password: string) => request<{ success: boolean }>(`/users/${id}/password`, {
    method: "POST",
    body: JSON.stringify({ password }),
  }),
};
