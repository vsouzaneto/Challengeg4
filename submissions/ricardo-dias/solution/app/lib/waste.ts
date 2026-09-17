// Calculadora de desperdício: espelho exato de compute_waste() em analysis/02_diagnostico.py.
// A UI chama computeWaste() com as premissas editadas pelo usuário.
// tests/waste.test.ts garante que o resultado bate com data/diagnostico.json.

import type { Assumption, WasteLine } from "./types";

export type AssumptionValues = Record<string, number>;

export const FTE_HOURS_PER_YEAR = 1_760;

export function assumptionValues(assumptions: Assumption[]): AssumptionValues {
  return Object.fromEntries(assumptions.map((a) => [a.id, a.value]));
}

const round = (x: number, digits: number) => Math.round(x * 10 ** digits) / 10 ** digits;

export function computeWaste(a: AssumptionValues): WasteLine[] {
  const v = a.annual_volume;
  const auto = a.auto_share;

  const triage = (v * a.triage_minutes) / 60;
  const triageRec = (v * auto * (a.triage_minutes - a.auto_check_minutes)) / 60;

  const rework = (v * a.misroute_rate * a.rework_minutes) / 60;
  const reworkAfter = (v * ((1 - auto) * a.misroute_rate + auto * (1 - a.auto_accuracy)) * a.rework_minutes) / 60;

  const followup = (v * a.pending_share * a.followups_per_pending * a.followup_minutes) / 60;
  const followupRec = followup * a.followup_automation;

  const drafting = (v * a.draft_minutes) / 60;
  const eligible = Math.max(0, 1 - a.human_only_share - a.escalation_share);
  const draftingRec = (v * eligible * a.draft_minutes * a.draft_net_saving) / 60;

  const lines: [WasteLine["id"], string, number, number, string][] = [
    ["triage", "Triagem manual (ler, classificar, rotear)", triage, triageRec,
      "Só nos tickets roteados automaticamente, descontando a conferência rápida que continua existindo."],
    ["rework", "Retrabalho por roteamento errado", rework, rework - reworkAfter,
      "Nos automáticos, a taxa de erro manual é trocada pelo erro medido do roteamento; o restante continua manual. " +
        "Fica negativo se o erro automático superar o manual."],
    ["followup", "Follow-up de tickets aguardando o cliente", followup, followupRec,
      "Lembretes e fechamento por inatividade. Cenário sem evidência nos dados: validar em piloto."],
    ["drafting", "Redação de respostas", drafting, draftingRec,
      "Economia líquida (já descontada a revisão) apenas nos tickets elegíveis a rascunho: exclui casos só-humanos e escalações."],
  ];

  return lines.map(([id, step, hours, recoverable, rationale]) => ({
    id,
    step,
    hoursPerYear: round(hours, 1),
    recoverableHoursPerYear: round(recoverable, 1),
    rationale,
  }));
}

export function wasteTotals(lines: WasteLine[], a: AssumptionValues) {
  const hoursPerYear = lines.reduce((s, l) => s + l.hoursPerYear, 0);
  const recoverableHoursPerYear = lines.reduce((s, l) => s + l.recoverableHoursPerYear, 0);
  return {
    hoursPerYear,
    recoverableHoursPerYear,
    recoverableCost: recoverableHoursPerYear * a.hourly_cost,
    fte: recoverableHoursPerYear / FTE_HOURS_PER_YEAR,
  };
}
