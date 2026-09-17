import Link from "next/link";
import { readAudit, readDiagnostic, readRouting } from "@/lib/data";
import { number, percent } from "@/components/format";
import { Icon } from "@/components/icons";
import {
  Badge,
  SectionHeading,
  SourceNote,
  Stat,
  Unavailable,
} from "@/components/ui";
import {
  AuditSummary,
  DiagnosticDetails,
  SegmentHeatmap,
  StatusMix,
} from "@/components/diagnostic-content";

export default async function DiagnosticPage() {
  const [audit, report, routing] = await Promise.all([
    readAudit(),
    readDiagnostic(),
    readRouting(),
  ]);
  const pending = audit?.d1.statusMix.find(
    (item) => item.status === "Pending Customer Response",
  );
  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">Operações & experiência do cliente</p>
          <h1>
            Entenda o suporte.
            <br />
            <em>Decida com clareza.</em>
          </h1>
          <p className="hero-description">
            Dos dados à próxima ação: um diagnóstico transparente e uma triagem
            que sabe quando chamar uma pessoa.
          </p>
          <Link href="/triagem" className="button gold">
            Experimentar a triagem
            <Icon name="arrow" width={17} />
          </Link>
        </div>
        <div className="hero-reference">
          <p className="eyebrow">Duas bases, papéis complementares</p>
          <div className="dataset-row">
            <span className="dataset-icon">
              <Icon name="chart" />
            </span>
            <div>
              <strong>{audit ? number(audit.d1.rows) : "—"}</strong>
              <small>tickets para investigar a operação · D1</small>
            </div>
          </div>
          <div className="dataset-row">
            <span className="dataset-icon">
              <Icon name="model" />
            </span>
            <div>
              <strong>{audit ? number(audit.d2.rows) : "—"}</strong>
              <small>tickets de TI para avaliar a classificação · D2</small>
            </div>
          </div>
          <div className="hero-steps">
            <span>Entender os dados</span>
            <Icon name="arrow" />
            <span>Testar a solução</span>
            <Icon name="arrow" />
            <span>Decidir</span>
          </div>
        </div>
      </section>
      {audit && <AuditSummary audit={audit} />}
      <div className="stats-grid">
        <Stat
          label="Registros analisados · D1"
          value={audit ? number(audit.d1.rows) : "—"}
          detail="Volume presente no arquivo operacional"
          icon="ticket"
        />
        <Stat
          label="Aguardando o cliente · D1"
          value={pending ? percent(pending.share) : "—"}
          detail="Proporção descritiva, sem medir tempo de espera"
          icon="clock"
        />
        <Stat
          label="Roteamento automático · D2"
          value={routing ? percent(routing.test.auto.share) : "—"}
          detail={
            routing
              ? "Cobertura no teste, com todas as regras da API"
              : "Avaliação do roteamento ainda indisponível"
          }
          icon="flow"
        />
        <Stat
          label="Acerto nos automáticos · D2"
          value={routing ? percent(routing.test.auto.accuracy) : "—"}
          detail={
            routing
              ? `IC 95%: ${percent(routing.test.auto.accuracyCI.low)}–${percent(routing.test.auto.accuracyCI.high)}`
              : "Aguardando avaliação compatível"
          }
          icon="shield"
          tone="gold"
        />
      </div>
      <section className="section">
        <SectionHeading
          eyebrow="Leitura da operação"
          title="O que o arquivo mostra."
          description="Os números descrevem estas bases. A aplicação em uma operação real exige dados locais e validação."
          action={<Badge>D1 · Dataset sintético</Badge>}
        />
        <div className="two-columns">
          {audit ? (
            <StatusMix audit={audit} />
          ) : (
            <Unavailable title="Auditoria indisponível." />
          )}
          {report ? (
            <SegmentHeatmap report={report} />
          ) : (
            <Unavailable title="Segmentos em atualização." />
          )}
        </div>
        {report && (
          <div className="panel section">
            <div className="panel-header">
              <h3>Observações do diagnóstico</h3>
              <Badge>Leitura contextual</Badge>
            </div>
            <div className="panel-body equal-columns">
              {report.observations.map((observation) => (
                <div key={observation.id}>
                  <p className="eyebrow">{observation.label}</p>
                  <h3 style={{ fontSize: 23, marginBottom: 8 }}>
                    {observation.value}
                  </h3>
                  <p className="small-copy muted">{observation.detail}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
      {report ? (
        <DiagnosticDetails report={report} />
      ) : (
        <section className="section">
          <Unavailable title="O diagnóstico está sendo atualizado.">
            A auditoria e a triagem continuam disponíveis. As análises por
            segmento e o cenário de economia serão exibidos quando o relatório
            estiver pronto.
          </Unavailable>
        </section>
      )}
      {routing && (
        <SourceNote
          source="Roteamento avaliado no teste do Dataset 2 · Política completa da API"
          generatedAt={routing.generatedAt}
        />
      )}
    </>
  );
}
