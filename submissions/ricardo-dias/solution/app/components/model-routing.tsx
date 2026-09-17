import type { ReasonCode, RoutingEval } from "@/lib/types";
import { categoryLabels, number, percent } from "./format";

const reasonLabels: Record<ReasonCode, string> = {
  auto: "Todas as verificações atendidas",
  low_confidence: "Confiança insuficiente",
  out_of_domain: "Vocabulário fora do domínio",
  always_human: "Categoria exige decisão humana",
  admin_rights_risk: "Risco de privilégio administrativo",
  escalation_terms: "Sinal de risco ou urgência",
};

export function RoutingDetails({ report }: { report: RoutingEval }) {
  const { test } = report;
  return (
    <details className="audit-summary">
      <summary>
        <strong>Ver motivos e encaminhamentos por categoria</strong>
      </summary>
      <div className="panel-body">
        <p className="small-copy muted">
          Cobertura automática: {percent(test.auto.share)} (IC 95%:{" "}
          {percent(test.auto.shareCI.low)}–{percent(test.auto.shareCI.high)}).
          Acerto nessa rota: {percent(test.auto.accuracy)} (IC 95%:{" "}
          {percent(test.auto.accuracyCI.low)}–
          {percent(test.auto.accuracyCI.high)}).
        </p>
        <div
          className="table-scroll section"
          role="region"
          aria-label="Motivos de encaminhamento no teste"
          tabIndex={0}
        >
          <table>
            <thead>
              <tr>
                <th>Motivo aplicado</th>
                <th className="numeric">Tickets</th>
                <th className="numeric">Participação</th>
              </tr>
            </thead>
            <tbody>
              {test.reasons.map((item) => (
                <tr key={item.reasonCode}>
                  <td>{reasonLabels[item.reasonCode]}</td>
                  <td className="numeric">{number(item.n)}</td>
                  <td className="numeric">{percent(item.share)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div
          className="table-scroll section"
          role="region"
          aria-label="Encaminhamentos por categoria real"
          tabIndex={0}
        >
          <table>
            <thead>
              <tr>
                <th>Categoria real</th>
                <th className="numeric">Tickets</th>
                <th className="numeric">Automáticos</th>
                <th className="numeric">Revisão humana</th>
                <th className="numeric">Escalação</th>
                <th className="numeric">Acerto nos automáticos</th>
              </tr>
            </thead>
            <tbody>
              {test.byTrueCategory.map((item) => (
                <tr key={item.label}>
                  <td className="row-label">{categoryLabels[item.label]}</td>
                  <td className="numeric">{number(item.n)}</td>
                  <td className="numeric">{number(item.auto)}</td>
                  <td className="numeric">{number(item.revisao_humana)}</td>
                  <td className="numeric">{number(item.escalar)}</td>
                  <td className="numeric">
                    {item.autoAccuracy === null
                      ? "Sem casos"
                      : percent(item.autoAccuracy)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </details>
  );
}
