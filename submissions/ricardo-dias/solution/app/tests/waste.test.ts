import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { dataPath } from "@/lib/eval-data";
import type { DiagnosticoReport, RoutingEval } from "@/lib/types";
import { assumptionValues, computeWaste, wasteTotals } from "@/lib/waste";

const report: DiagnosticoReport = JSON.parse(readFileSync(dataPath("diagnostico.json"), "utf-8"));
const routing: RoutingEval = JSON.parse(readFileSync(dataPath("routing_eval.json"), "utf-8"));
const values = assumptionValues(report.scenario.assumptions);

describe("calculadora de desperdício", () => {
  it("TypeScript reproduz o cenário do Python linha a linha", () => {
    const ts = computeWaste(values);
    report.scenario.waste.forEach((py, i) => {
      expect(ts[i].id).toBe(py.id);
      expect(ts[i].hoursPerYear).toBeCloseTo(py.hoursPerYear, 0);
      expect(ts[i].recoverableHoursPerYear).toBeCloseTo(py.recoverableHoursPerYear, 0);
    });
    expect(wasteTotals(ts, values).recoverableHoursPerYear).toBeCloseTo(report.scenario.totals.recoverableHoursPerYear, 0);
  });

  it("usa a cobertura FINAL do roteamento medido no teste", () => {
    expect(values.auto_share).toBe(routing.test.auto.share);
    expect(values.auto_accuracy).toBe(routing.test.auto.accuracy);
  });

  it("sem automação não há economia de triagem nem de retrabalho", () => {
    const [triage, rework] = computeWaste({ ...values, auto_share: 0 });
    expect(triage.recoverableHoursPerYear).toBe(0);
    expect(rework.recoverableHoursPerYear).toBe(0);
  });

  it("conferência residual igual ao tempo de triagem zera a economia de triagem", () => {
    const [triage] = computeWaste({ ...values, auto_check_minutes: values.triage_minutes });
    expect(triage.recoverableHoursPerYear).toBe(0);
  });

  it("se o erro automático supera o manual, o retrabalho aparece como perda (negativo)", () => {
    const [, rework] = computeWaste({ ...values, auto_accuracy: 0.5, misroute_rate: 0.1 });
    expect(rework.recoverableHoursPerYear).toBeLessThan(0);
  });

  it("economia nunca excede a linha de base de cada etapa", () => {
    for (const line of computeWaste(values)) expect(line.recoverableHoursPerYear).toBeLessThanOrEqual(line.hoursPerYear);
  });
});
