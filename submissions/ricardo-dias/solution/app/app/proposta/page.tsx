import type { Metadata } from "next";
import Link from "next/link";
import {
  readAutomationDocument,
  readDiagnostic,
  readRouting,
} from "@/lib/data";
import { Document } from "@/components/document";
import { currency, number, percent } from "@/components/format";
import { Icon } from "@/components/icons";
import { PolicyFlow } from "@/components/policy-flow";
import {
  Badge,
  Notice,
  PageHeading,
  SectionHeading,
  SourceNote,
  Stat,
  Unavailable,
} from "@/components/ui";

export const metadata: Metadata = { title: "Proposta de automação" };
const steps = [
  {
    title: "Receber",
    description: "O ticket entra com o contexto da solicitação.",
  },
  {
    title: "Classificar",
    description: "Categoria prevista, confiança e sinais de risco.",
  },
  {
    title: "Encaminhar",
    description: "Fila automática, revisão humana ou escalação.",
  },
  {
    title: "Responder",
    description: "Nos casos elegíveis, um rascunho que o agente revisa.",
  },
  {
    title: "Aprender",
    description: "Correções e resultados orientam a melhoria da operação.",
  },
];

export default async function ProposalPage() {
  const [document, diagnostic, routing] = await Promise.all([
    readAutomationDocument(),
    readDiagnostic(),
    readRouting(),
  ]);
  return (
    <>
      <PageHeading
        eyebrow="Redesign de suporte"
        title="Automação com espaço para o julgamento."
        description="Uma proposta de operação que combina tarefas mensuráveis, limites claros e supervisão humana."
        action={
          <Link className="button" href="/triagem">
            Experimentar o fluxo
            <Icon name="arrow" width={16} />
          </Link>
        }
      />
      <Notice title="Proposta para revisão e validação em piloto.">
        O protótipo demonstra classificação, encaminhamento e rascunhos. Os
        ganhos operacionais são cenários a validar com o histórico e o processo
        da empresa.
      </Notice>
      <section className="section">
        <SectionHeading
          eyebrow="Do ticket à ação"
          title="O atendimento continua tendo um responsável."
          action={<Badge tone="gold">Fluxo proposto</Badge>}
        />
        <div className="flow-steps">
          {steps.map((step, i) => (
            <div className="flow-step" key={step.title}>
              <span className="step-number">
                {String(i + 1).padStart(2, "0")} /
              </span>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          ))}
        </div>
      </section>
      {routing && <PolicyFlow thresholds={routing.thresholds} />}
      <div className="stats-grid">
        <Stat
          label="Roteamento automático · D2"
          value={routing ? percent(routing.test.auto.share) : "—"}
          detail="Cobertura medida no teste com a política completa"
          icon="flow"
        />
        <Stat
          label="Intervenção humana · D2"
          value={routing ? percent(1 - routing.test.auto.share) : "—"}
          detail="Revisões e escalações continuam com pessoas"
          icon="people"
        />
        <Stat
          label="Capacidade recuperável · cenário"
          value={
            diagnostic
              ? `${number(diagnostic.scenario.totals.recoverableHoursPerYear)} h`
              : "—"
          }
          detail="Estimativa anual, descontando o trabalho residual"
          icon="clock"
          tone="gold"
        />
        <Stat
          label="Valor equivalente · cenário"
          value={
            diagnostic
              ? currency(diagnostic.scenario.totals.recoverableCost)
              : "—"
          }
          detail="Projeção anual; não representa economia realizada"
          icon="chart"
          tone="gold"
        />
      </div>
      <section className="section">
        <SectionHeading
          eyebrow="Decisões e responsabilidades"
          title="A proposta, com seus limites explícitos."
          description="Conteúdo da documentação de automação, gerado a partir da análise e sujeito à revisão do responsável pela submissão."
          action={
            <Link href="/#cenario" className="button secondary">
              Ajustar premissas
              <Icon name="arrow" width={16} />
            </Link>
          }
        />
        {document ? (
          <div className="panel">
            <Document text={document} />
          </div>
        ) : (
          <Unavailable title="Documento de automação em preparação.">
            As decisões de implantação serão apresentadas aqui assim que a
            proposta estiver disponível.
          </Unavailable>
        )}
      </section>
      {diagnostic && (
        <SourceNote
          source="Proposta de automação e cenário do diagnóstico"
          generatedAt={diagnostic.generatedAt}
        />
      )}
    </>
  );
}
