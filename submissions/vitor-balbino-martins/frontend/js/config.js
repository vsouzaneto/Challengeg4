/**
 * Configuracao do cliente.
 *
 * A base da API e resolvida nesta ordem:
 *   1. valor salvo pelo usuario no dialogo "Configurar API" (localStorage);
 *   2. `?api=` na query string (util para demo sem mexer no storage);
 *   3. mesma origem, quando o frontend e servido pelo proprio backend;
 *   4. http://localhost:8000/api/v1 (padrao do `python manage.py run`).
 */

const STORAGE_KEY = "si.apiBase";
const DEFAULT_PORT = "8000";
const API_PREFIX = "/api/v1";

/** Datasets presentes em `assets/`. O backend nao expoe listagem. */
export const DATASETS = [
  { value: "customer_support_tickets.csv", label: "customer_support_tickets.csv" },
  { value: "all_tickets_processed_improved_v3.csv", label: "all_tickets_processed_improved_v3.csv" },
];

/** Endpoints que rodam agentes/embeddings e podem levar minutos. */
export const TIMEOUTS = {
  health: 8_000,
  ragStatus: 8_000,
  ragSearch: 60_000,
  ragIndex: 30_000,
  clustering: 20 * 60_000,
  satisfaction: 20 * 60_000,
  report: 0, // sem limite: depende do numero de lotes enviados ao Ollama
};

function normalize(base) {
  return String(base || "").trim().replace(/\/+$/, "");
}

function fallbackBase() {
  const { protocol, hostname, port, origin } = window.location;
  if (protocol === "file:") return `http://localhost:${DEFAULT_PORT}${API_PREFIX}`;
  // Servido pelo proprio backend (uvicorn na 8000) -> mesma origem.
  if (port === DEFAULT_PORT) return `${origin}${API_PREFIX}`;
  // Servido por um estatico separado (ex.: python -m http.server 5500).
  return `${protocol}//${hostname}:${DEFAULT_PORT}${API_PREFIX}`;
}

let apiBase = (() => {
  const fromQuery = new URLSearchParams(window.location.search).get("api");
  if (fromQuery) return normalize(fromQuery);
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return normalize(saved);
  } catch {
    /* storage bloqueado (janela privada) - segue com o fallback */
  }
  return fallbackBase();
})();

export function getApiBase() {
  return apiBase;
}

export function setApiBase(next) {
  apiBase = normalize(next) || fallbackBase();
  try {
    localStorage.setItem(STORAGE_KEY, apiBase);
  } catch {
    /* sem persistencia: vale para a sessao atual */
  }
  return apiBase;
}

export function defaultApiBase() {
  return fallbackBase();
}
