/**
 * Estado compartilhado entre as views.
 *
 * O relatorio de suporte e caro de produzir (um lote por chamada ao Ollama),
 * entao ele vive aqui e e reaproveitado pela view de Custo em vez de ser
 * pedido de novo. A persistencia em localStorage e best-effort: o payload
 * traz a extracao de todos os lotes e pode estourar a cota, e nesse caso
 * guardamos so a parte enxuta.
 */

const KEY = "si.report";

const state = {
  report: null,        // resposta completa de POST /reports/support
  reportAt: null,      // timestamp de quando ela chegou
  reportParams: null,  // { dataset, chunk_size, hourly_cost }
  health: null,        // resposta de GET /health
  healthAt: null,
};

const listeners = new Set();

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function emit(keys) {
  for (const fn of listeners) fn(keys, state);
}

export function get(key) {
  return state[key];
}

export function set(patch) {
  Object.assign(state, patch);
  emit(Object.keys(patch));
}

/* -- Relatorio ----------------------------------------------------------- */

export function setReport(report, params) {
  const previous = state.report;
  const merged = mergeMissing(previous, report);
  set({ report: merged, reportAt: Date.now(), reportParams: params });
  persist();
}

function isEmpty(value) {
  return value === null || value === undefined || value === ""
    || (Array.isArray(value) && value.length === 0)
    || (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
}

// Preserva o relatório já carregado e só preenche campos que vieram ausentes.
function mergeMissing(previous, incoming) {
  if (!previous || typeof previous !== "object") return incoming;
  if (!incoming || typeof incoming !== "object") return previous;
  const result = structuredClone(previous);
  for (const [key, value] of Object.entries(incoming)) {
    if (!(key in result) || isEmpty(result[key])) {
      result[key] = value;
    } else if (value && typeof value === "object" && !Array.isArray(value)) {
      result[key] = mergeMissing(result[key], value);
    }
  }
  return result;
}

export function clearReport() {
  set({ report: null, reportAt: null, reportParams: null });
  try { localStorage.removeItem(KEY); } catch { /* storage indisponivel */ }
}

function persist() {
  const snapshot = {
    reportAt: state.reportAt,
    reportParams: state.reportParams,
    report: state.report,
  };
  try {
    localStorage.setItem(KEY, JSON.stringify(snapshot));
  } catch {
    // Cota estourada: guarda a versao sem a extracao por lote, que e o que
    // realmente pesa. As metricas e a consolidacao continuam disponiveis.
    try {
      const slim = structuredClone(snapshot);
      if (slim.report?.extraction) {
        slim.report.extraction = { chunks: slim.report.extraction.chunks, items: [], trimmed: true };
      }
      localStorage.setItem(KEY, JSON.stringify(slim));
    } catch { /* segue apenas em memoria */ }
  }
}

/** Recupera o ultimo relatorio salvo. Chamado uma vez no boot. */
export function restore() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (saved?.report?.metrics) {
      set({ report: saved.report, reportAt: saved.reportAt, reportParams: saved.reportParams });
    }
  } catch { /* payload corrompido: ignora */ }
}
