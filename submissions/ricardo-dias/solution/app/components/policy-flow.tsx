import type { RoutingEval } from "@/lib/types";
import { percent } from "./format";
import { Badge } from "./ui";
import { Icon } from "./icons";

export function PolicyFlow({
  thresholds,
}: {
  thresholds: RoutingEval["thresholds"];
}) {
  const gates = [
    {
      label: "Sinal de risco ou urgência?",
      outcome: "Sim → escalar para atendente sênior",
      tone: "danger",
    },
    {
      label: `Vocabulário conhecido abaixo de ${percent(thresholds.ood, 0)}?`,
      outcome: "Sim → revisão humana",
      tone: "warning",
    },
    {
      label: `Confiança abaixo de ${percent(thresholds.confidence, 0)}?`,
      outcome: "Sim → revisão humana",
      tone: "warning",
    },
    {
      label: "Categoria exige decisão humana?",
      outcome: "Sim → revisão humana",
      tone: "warning",
    },
    ...(thresholds.adminRights === null
      ? []
      : [
          {
            label: `Chance de privilégio administrativo ≥ ${percent(thresholds.adminRights, 0)}?`,
            outcome: "Sim → aprovação humana",
            tone: "warning",
          },
        ]),
  ];
  return (
    <div className="panel section">
      <div className="panel-header">
        <div>
          <h3>Como o destino é decidido</h3>
          <p>
            As verificações seguem esta ordem. Se a resposta for não, o ticket
            avança.
          </p>
        </div>
        <Icon name="flow" />
      </div>
      <div className="panel-body">
        <ol
          className="policy-gates"
          aria-label="Ordem das verificações de roteamento"
        >
          {gates.map((gate, i) => (
            <li key={gate.label}>
              <span className="gate-number">{i + 1}</span>
              <strong>{gate.label}</strong>
              <Badge tone={gate.tone}>{gate.outcome}</Badge>
            </li>
          ))}
        </ol>
        <div className="policy-result">
          <Icon name="check" />
          <p>
            <strong>
              Todas as verificações atendidas → encaminhamento automático.
            </strong>
            <br />
            Rascunhos permitidos pela política continuam sujeitos à revisão do
            agente. Casos escalados não geram rascunho.
          </p>
        </div>
      </div>
    </div>
  );
}
