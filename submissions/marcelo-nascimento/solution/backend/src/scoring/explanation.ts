import type { EvidenceStrength, FactorId, ScoreEvidence, ScoreFactor } from "./types.js";

export type FactorDraft = Omit<ScoreFactor, "reason">;

const unavailableStates = new Set([
  "missing_account",
  "missing_sector",
  "missing_target_data",
  "no_historical_evidence",
  "insufficient_history",
]);

function numberEvidence(evidence: ScoreEvidence, key: string): number {
  const value = evidence[key];
  return typeof value === "number" ? value : 0;
}

function textEvidence(evidence: ScoreEvidence, key: string): string | null {
  const value = evidence[key];
  return typeof value === "string" ? value : null;
}

function accountProductReason(evidence: ScoreEvidence): string {
  if (textEvidence(evidence, "evidenceState") === "missing_account") {
    return "A oportunidade não possui cliente associado, portanto não há evidência produto × cliente.";
  }

  const exactWon = numberEvidence(evidence, "exactWon");
  const exactLost = numberEvidence(evidence, "exactLost");
  const seriesWon = numberEvidence(evidence, "seriesWon");
  const seriesLost = numberEvidence(evidence, "seriesLost");

  if (textEvidence(evidence, "evidenceState") === "no_historical_evidence") {
    return `Não há histórico encerrado do produto ou de outro produto da família ${textEvidence(evidence, "series") ?? "associada"} para este cliente.`;
  }

  const parts: string[] = [];
  if (exactWon + exactLost > 0) {
    parts.push(`o produto exato apresenta ${exactWon} vitória${exactWon === 1 ? "" : "s"} e ${exactLost} derrota${exactLost === 1 ? "" : "s"}`);
  }
  if (seriesWon + seriesLost > 0) {
    parts.push(`outros produtos da família apresentam ${seriesWon} vitória${seriesWon === 1 ? "" : "s"} e ${seriesLost} derrota${seriesLost === 1 ? "" : "s"}`);
  }
  return `Histórico do cliente: ${parts.join("; ")}.`;
}

function sectorReason(evidence: ScoreEvidence): string {
  const sector = textEvidence(evidence, "sector");
  if (textEvidence(evidence, "evidenceState") === "missing_sector") {
    return "O cliente não possui setor informado, portanto não há evidência produto × setor.";
  }

  const won = numberEvidence(evidence, "won");
  const lost = numberEvidence(evidence, "lost");
  if (textEvidence(evidence, "evidenceState") === "no_historical_evidence") {
    return `Não há negócios encerrados deste produto no setor ${sector}.`;
  }
  return `No setor ${sector}, o produto tem ${won} vitória${won === 1 ? "" : "s"} e ${lost} derrota${lost === 1 ? "" : "s"} no histórico analisado.`;
}

function companyReason(evidence: ScoreEvidence): string {
  const state = textEvidence(evidence, "evidenceState");
  if (state === "missing_target_data") {
    return "A empresa não possui funcionários nem receita válidos para a comparação de perfil.";
  }
  if (state === "no_historical_evidence") {
    return "Não há compradores Won anteriores à data de referência para calcular as medianas de perfil.";
  }

  const parts: string[] = [];
  const employeeState = textEvidence(evidence, "employeeEvidenceState");
  const revenueState = textEvidence(evidence, "revenueEvidenceState");
  if (employeeState === "missing_target_data") {
    parts.push("funcionários da empresa não informados");
  } else if (employeeState === "no_historical_evidence") {
    parts.push("sem histórico válido de funcionários");
  } else {
    parts.push(`mediana histórica de ${numberEvidence(evidence, "medianEmployees")} funcionários`);
  }
  if (revenueState === "missing_target_data") {
    parts.push("receita da empresa não informada");
  } else if (revenueState === "no_historical_evidence") {
    parts.push("sem histórico válido de receita");
  } else {
    parts.push(`mediana histórica de receita ${numberEvidence(evidence, "medianRevenue")}`);
  }
  return `Comparação do perfil da empresa com ${parts.join(" e ")} entre compradores distintos do produto.`;
}

function financialReason(evidence: ScoreEvidence): string {
  const state = textEvidence(evidence, "evidenceState");
  if (state === "missing_target_data") {
    return "A conta avaliada não possui receita válida para comparar com a faixa financeira histórica.";
  }
  if (state === "insufficient_history") {
    return "Há menos de quatro clientes distintos com receita válida e negócio ganho para estabelecer a faixa financeira.";
  }
  return `A faixa financeira histórica é ${numberEvidence(evidence, "q1")} a ${numberEvidence(evidence, "q3")}, calculada com ${numberEvidence(evidence, "sampleSize")} clientes distintos que compraram o produto.`;
}

const reasonBuilders: Record<FactorId, (evidence: ScoreEvidence) => string> = {
  account_product_fit: accountProductReason,
  sector_product_fit: sectorReason,
  company_profile_fit: companyReason,
  financial_fit: financialReason,
};

export function addFactorReasons(factors: FactorDraft[]): ScoreFactor[] {
  return factors.map((factor) => ({
    ...factor,
    reason: reasonBuilders[factor.id](factor.evidence),
  }));
}

function strengthPhrase(factor: ScoreFactor): string {
  const label = factor.label.toLocaleLowerCase("pt-BR");
  if (factor.strength === "forte") {
    return `forte evidência em ${label}`;
  }
  if (factor.strength === "moderada") {
    return `aderência moderada em ${label}`;
  }
  return `evidência fraca em ${label}`;
}

function missingFactorsText(factors: ScoreFactor[]): string {
  const unavailable = factors.filter((factor) => {
    const state = factor.evidence.evidenceState;
    return typeof state === "string" && unavailableStates.has(state);
  }).length;
  if (unavailable === 0) {
    return "";
  }
  return ` ${unavailable === 1 ? "Um fator não foi avaliado por falta de dados ou evidência" : `${unavailable} fatores não foram avaliados por falta de dados ou evidência`}.`;
}

export function buildJustification(score: number, factors: ScoreFactor[]): string {
  const positiveFactors = factors
    .filter((factor) => factor.points > 0)
    .sort((left, right) => right.points - left.points || left.id.localeCompare(right.id));
  const prefix = `Score ${score}.`;
  const missingText = missingFactorsText(factors);

  if (positiveFactors.length === 0) {
    const calculatedEvidence = factors.some((factor) => factor.evidence.evidenceState === "calculated");
    const text = calculatedEvidence
      ? "Os fatores com dados históricos não produziram pontos positivos para esta oportunidade."
      : "O histórico e os dados disponíveis não sustentam pontos para esta oportunidade.";
    return `${prefix} ${text}${missingText} O score representa a força relativa das evidências, não uma probabilidade de fechamento.`;
  }

  if (positiveFactors.length === 1) {
    const onlyFactor = positiveFactors[0];
    if (!onlyFactor) {
      return `${prefix} A evidência disponível não pôde ser detalhada.${missingText} O score não representa uma probabilidade de fechamento.`;
    }
    return `${prefix} A evidência disponível está concentrada em ${strengthPhrase(onlyFactor)}.${missingText} O score não representa uma probabilidade de fechamento.`;
  }

  const highlights = positiveFactors
    .slice(0, 2)
    .map((factor) => strengthPhrase(factor))
    .join(" e ");
  return `${prefix} Há ${highlights}.${missingText} O score representa a força relativa das evidências históricas, não uma probabilidade de fechamento.`;
}

export function classifyFactor(points: number, maxPoints: number): EvidenceStrength {
  const ratio = maxPoints > 0 ? points / maxPoints : 0;
  if (ratio >= 0.75) {
    return "forte";
  }
  if (ratio >= 0.5) {
    return "moderada";
  }
  if (ratio > 0) {
    return "fraca";
  }
  return "sem evidência";
}
