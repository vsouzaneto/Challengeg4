// Contratos entre a análise (Python/TS → data/*.json) e a UI. Versão 3.
// Dono: Claude Code. Para mudar, registrar o pedido em ../../../HANDOFF.md.

export const CATEGORIES = [
  "Hardware",
  "HR Support",
  "Access",
  "Miscellaneous",
  "Storage",
  "Purchase",
  "Internal Project",
  "Administrative rights",
] as const;
export type Category = (typeof CATEGORIES)[number];

export type Severity = "bloqueante" | "alerta" | "info";
export interface Interval {
  low: number;
  high: number;
}

// ---------------- data/audit.json ----------------
export interface AuditFinding {
  id: string;
  dataset: "D1" | "D2";
  title: string;
  evidence: string; // frase curta com o número que prova o achado
  metric?: number | string;
  implication: string; // o que isso muda na análise
  severity: Severity;
}
export interface AuditReport {
  generatedAt: string;
  d1: { rows: number; columns: number; statusMix: { status: string; n: number; share: number }[] };
  d2: { rows: number; classes: { label: Category; n: number; share: number }[] };
  findings: AuditFinding[];
}

// ---------------- data/model_metrics.json (Python) ----------------
export interface SplitInfo {
  name: "treino" | "validacao" | "teste";
  n: number;
  share: number;
  purpose: string;
}
export interface ClassMetrics {
  label: Category;
  precision: number;
  recall: number;
  f1: number;
  support: number;
}
export interface ModelMetrics {
  generatedAt: string;
  seed: number;
  splits: SplitInfo[];
  // Tudo aqui foi escolhido olhando SÓ a validação e congelado antes da avaliação no teste.
  selection: {
    model: string;
    C: number;
    coefEps: number;
    confidenceThreshold: number;
    oodThreshold: number;
    adminRightsThreshold: number | null;
    criteria: string[];
    candidates: { name: string; accuracy: number; macroF1: number }[]; // métricas de VALIDAÇÃO
  };
  test: {
    accuracy: number;
    accuracyCI: Interval;
    macroF1: number;
    macroF1CI: Interval;
    baselineAccuracy: number;
    perClass: ClassMetrics[];
    confusion: { labels: Category[]; matrix: number[][] };
  };
  // Números anteriores, medidos no mesmo conjunto usado para ajustar parâmetros. Só histórico.
  exploratory: { note: string; accuracy: number; macroF1: number; autoCoverage: number; autoAccuracy: number };
  crossDomain: {
    note: string;
    n: number;
    confidentShare: number; // D1 com confiança ≥ limiar
    confidentPredictedHardware: number; // desses, fração prevista como Hardware (erro confiante)
    oodFlagged: number; // D1 barrado pelo guarda de domínio
    inDomainOodFlagged: number; // teste do D2 barrado pelo guarda
    routes: { route: Route; share: number }[]; // política completa aplicada ao D1
  };
}

// ---------------- data/routing_eval.json (TS: funções reais da API) ----------------
export type Route = "auto" | "revisao_humana" | "escalar";
export type ReasonCode =
  | "escalation_terms"
  | "out_of_domain"
  | "low_confidence"
  | "always_human"
  | "admin_rights_risk"
  | "auto";

export interface RoutingPartition {
  n: number;
  modelAccuracy: number; // categoria prevista = real, em todos os tickets
  routes: { route: Route; n: number; share: number }[];
  reasons: { reasonCode: ReasonCode; n: number; share: number }[];
  auto: { n: number; share: number; shareCI: Interval; accuracy: number; accuracyCI: Interval; errors: number };
  byTrueCategory: { label: Category; n: number; auto: number; revisao_humana: number; escalar: number; autoAccuracy: number | null }[];
  adminRightsLeak: {
    trueAdminRights: number;
    autoRoutedElsewhere: number; // rótulo real AR, previsto como outra categoria e roteado automaticamente
    share: number;
    toQueues: { label: Category; n: number }[];
  };
  pythonAgreement: { route: number; label: number; maxConfidenceDiff: number };
}
export interface RoutingEval {
  generatedAt: string;
  note: string;
  thresholds: { confidence: number; ood: number; adminRights: number | null };
  validation: RoutingPartition;
  test: RoutingPartition; // números publicados
}

// ---------------- data/diagnostico.json ----------------
export interface Assumption {
  id: string;
  label: string;
  value: number;
  unit: string;
  kind: "medido" | "premissa" | "referencia"; // referencia = medido em outro contexto (D2)
  source: string; // de onde veio e como validar
  editable: boolean;
}
export interface Observation {
  id: string;
  label: string;
  value: string;
  detail: string; // descritivo do arquivo; NÃO é evidência de gargalo por si só
}
export interface SegmentCell {
  channel: string;
  priority: string;
  n: number;
  backlogShare: number; // Open + Pending / total — descritivo
  backlogCI: Interval; // Wilson 95%
  pendingCustomerShare: number;
  csatMean: number | null;
}
export interface SegmentTest {
  variable: string;
  test: string;
  pValue: number;
  significant: boolean;
  conclusion: string;
}
export interface CsatDriver {
  variable: string;
  test: string;
  pValue: number;
  effectSize: number; // ε² de Kruskal-Wallis
  detectableDiff: number; // meia-largura do IC 95% da diferença entre dois grupos típicos (pontos de CSAT)
  conclusion: string;
  groups: { label: string; mean: number; ci: Interval; n: number }[];
}
export interface WasteLine {
  id: "triage" | "rework" | "followup" | "drafting";
  step: string;
  hoursPerYear: number; // linha de base (sem automação)
  recoverableHoursPerYear: number; // já descontado o trabalho residual; pode ser negativo
  rationale: string;
}
export interface DiagnosticoReport {
  generatedAt: string;
  nTickets: number;
  observations: Observation[];
  segments: SegmentCell[];
  tests: { segmentTests: SegmentTest[]; csatDrivers: CsatDriver[] };
  limitations: { id: string; text: string }[];
  scenario: {
    note: string;
    assumptions: Assumption[];
    waste: WasteLine[];
    totals: { hoursPerYear: number; recoverableHoursPerYear: number; recoverableCost: number; fte: number };
    sensitivity: { autoShare: number; draftSaving: number; recoverableHoursPerYear: number }[];
  };
}

// ---------------- APIs ----------------
// POST /api/classify { text } → ClassifyResponse
// POST /api/classify { texts: string[] } (1..500) → { results: ClassifyResponse[] } com similar = []
// Erros: 400 { error, errors?: {index, status, error}[] } | 413 { error }
export interface ClassifyResponse {
  category: Category;
  confidence: number;
  knownShare: number; // fração das palavras de conteúdo conhecidas pelo modelo (guarda de domínio)
  probabilities: { label: Category; p: number }[];
  topTerms: { term: string; weight: number }[]; // explicação: contribuição por termo
  route: Route;
  reasonCode: ReasonCode;
  routeReason: string; // já redigido em PT-BR para o usuário final
  draftAllowed: boolean; // false em escalações; o servidor também bloqueia /api/draft
  similar: { text: string; label: Category; score: number }[];
}

// GET /api/sample?n=200 → tickets do conjunto de TESTE (nunca usados em treino ou seleção)
export interface SampleResponse {
  items: { id: number; text: string; label: Category }[];
}

// POST /api/draft { text } → stream de texto (rascunho para o agente aprovar)
// A categoria é recalculada no servidor (header X-Draft-Category). 403 se a política bloquear; 503 sem provedor.
export interface DraftRequest {
  text: string;
}
