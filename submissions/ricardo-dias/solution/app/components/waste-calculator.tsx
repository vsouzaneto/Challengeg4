"use client";

import { useState } from "react";
import type { DiagnosticoReport } from "@/lib/types";
import { assumptionValues, computeWaste, wasteTotals } from "@/lib/waste";
import { currency, number, percent } from "./format";
import { Badge, Notice } from "./ui";
import { Icon } from "./icons";

type Scenario = DiagnosticoReport["scenario"];
const kindLabels = {
  medido: "Observado no D1",
  referencia: "Referência do D2",
  premissa: "Premissa",
};

export function WasteCalculator({ scenario }: { scenario: Scenario }) {
  const initial = Object.fromEntries(
    scenario.assumptions.map((a) => [
      a.id,
      String(Number((a.value * (a.unit === "fração" ? 100 : 1)).toFixed(6))),
    ]),
  );
  const [inputs, setInputs] = useState<Record<string, string>>(initial);
  const values = assumptionValues(scenario.assumptions);
  let invalid = false;
  for (const assumption of scenario.assumptions) {
    const raw = inputs[assumption.id];
    if (!assumption.editable) continue;
    const n = Number(raw);
    if (
      raw === "" ||
      !Number.isFinite(n) ||
      n < 0 ||
      n > (assumption.unit === "fração" ? 100 : 1_000_000_000)
    )
      invalid = true;
    values[assumption.id] = n / (assumption.unit === "fração" ? 100 : 1);
  }
  const changed = scenario.assumptions.some(
    (a) => inputs[a.id] !== initial[a.id],
  );
  const lines = invalid ? [] : computeWaste(values);
  const totals = invalid
    ? null
    : changed
      ? wasteTotals(lines, values)
      : scenario.totals;
  const finite =
    totals !== null && Object.values(totals).every(Number.isFinite);

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2>Quanto tempo pode ser recuperado?</h2>
          <p>Ajuste as premissas e acompanhe o cenário.</p>
        </div>
        <button
          className="button secondary small"
          onClick={() => setInputs(initial)}
          disabled={!changed}
        >
          <Icon name="refresh" width={14} />
          Restaurar
        </button>
      </div>
      <div className="panel-body">
        <Notice title="Uma projeção, com premissas explícitas." tone="warning">
          {scenario.note}
        </Notice>
        <div className="calculator-grid" style={{ marginTop: 24 }}>
          <div>
            <div className="assumptions">
              {scenario.assumptions
                .filter((a) => a.editable)
                .map((a) => (
                  <div className="assumption-field" key={a.id}>
                    <label htmlFor={`assumption-${a.id}`}>{a.label}</label>
                    <div className="input-unit">
                      <input
                        id={`assumption-${a.id}`}
                        type="number"
                        min="0"
                        max={a.unit === "fração" ? 100 : 1_000_000_000}
                        step="any"
                        value={inputs[a.id]}
                        aria-describedby={`assumption-source-${a.id}`}
                        onChange={(event) =>
                          setInputs((previous) => ({
                            ...previous,
                            [a.id]: event.target.value,
                          }))
                        }
                      />
                      <span>{a.unit === "fração" ? "%" : a.unit}</span>
                    </div>
                    <small id={`assumption-source-${a.id}`}>
                      <strong>{kindLabels[a.kind]}.</strong> {a.source}
                    </small>
                  </div>
                ))}
            </div>
            {scenario.assumptions.some((a) => !a.editable) && (
              <details className="measured-values">
                <summary>Referências mantidas no cenário</summary>
                <ul>
                  {scenario.assumptions
                    .filter((a) => !a.editable)
                    .map((a) => (
                      <li key={a.id}>
                        <strong>
                          {a.label}:{" "}
                          {a.unit === "fração"
                            ? percent(a.value)
                            : `${number(a.value, 2)} ${a.unit}`}
                        </strong>
                        <p>{a.source}</p>
                      </li>
                    ))}
                </ul>
              </details>
            )}
          </div>
          <div
            className="scenario-result"
            aria-live="polite"
            aria-atomic="true"
          >
            <p className="eyebrow">
              {changed ? "Seu cenário" : "Cenário de referência"}
            </p>
            {finite && totals ? (
              <>
                <div className="scenario-value">
                  {number(totals.recoverableHoursPerYear)}{" "}
                  <span style={{ fontSize: 22 }}>h/ano</span>
                </div>
                <p>
                  {totals.recoverableHoursPerYear >= 0
                    ? "Capacidade potencialmente recuperável, com o trabalho residual descontado."
                    : "Aumento estimado de trabalho neste cenário. Revise as premissas."}
                </p>
                <div className="scenario-secondary">
                  <div>
                    <strong>{currency(totals.recoverableCost)}</strong>
                    <small>valor equivalente por ano</small>
                  </div>
                  <div>
                    <strong>{number(totals.fte, 2)}</strong>
                    <small>equivalentes de capacidade anual</small>
                  </div>
                </div>
                <p style={{ marginTop: 20, fontSize: 10 }}>
                  Capacidade liberada não significa redução realizada de
                  despesas ou de equipe. O resultado depende de validação na
                  operação.
                </p>
              </>
            ) : (
              <p role="status">
                Informe valores válidos e não negativos. Percentuais devem ficar
                entre 0 e 100.
              </p>
            )}
          </div>
        </div>
        {finite && (
          <div
            className="section table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Detalhamento da estimativa de desperdício"
          >
            <table>
              <thead>
                <tr>
                  <th>Etapa do atendimento</th>
                  <th className="numeric">Base anual</th>
                  <th className="numeric">Recuperável</th>
                </tr>
              </thead>
              <tbody>
                {lines.map((line) => (
                  <tr key={line.id}>
                    <td>
                      <strong className="row-label">{line.step}</strong>
                      <p className="field-hint">{line.rationale}</p>
                    </td>
                    <td className="numeric">
                      {number(line.hoursPerYear, 1)} h
                    </td>
                    <td className="numeric">
                      <Badge
                        tone={
                          line.recoverableHoursPerYear < 0
                            ? "danger"
                            : "success"
                        }
                      >
                        {number(line.recoverableHoursPerYear, 1)} h
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
