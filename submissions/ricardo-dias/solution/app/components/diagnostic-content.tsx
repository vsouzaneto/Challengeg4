import type { AuditReport, DiagnosticoReport } from "@/lib/types";
import { number, percent } from "./format";
import { Badge, Notice, SectionHeading, SourceNote } from "./ui";
import { Icon } from "./icons";
import { WasteCalculator } from "./waste-calculator";

const statusLabels: Record<string, string> = {
  Open: "Abertos",
  Closed: "Fechados",
  "Pending Customer Response": "Aguardando o cliente",
};
const channelLabels: Record<string, string> = {
  Chat: "Chat",
  Email: "E-mail",
  Phone: "Telefone",
  "Social media": "Redes sociais",
};
const priorityLabels: Record<string, string> = {
  Low: "Baixa",
  Medium: "Média",
  High: "Alta",
  Critical: "Crítica",
};
const variableLabels: Record<string, string> = {
  canal: "Canal",
  prioridade: "Prioridade",
  tipo: "Tipo de ticket",
  gênero: "Gênero",
  "canal × prioridade": "Canal × prioridade",
  "Ticket Type": "Tipo de ticket",
  "Ticket Priority": "Prioridade",
  "Ticket Channel": "Canal",
  "Customer Gender": "Gênero",
  "Product Purchased": "Produto",
  "Customer Age": "Idade",
};

export function AuditSummary({ audit }: { audit: AuditReport }) {
  const order = { bloqueante: 0, alerta: 1, info: 2 };
  return (
    <details className="audit-summary">
      <summary>
        <Icon name="shield" width={19} />
        <span>
          <strong>Antes de ler os números</strong>
          <span className="audit-preview">
            O Dataset 1 tem limitações que afetam as conclusões.
          </span>
        </span>
        <Badge tone="gold">Ver auditoria</Badge>
        <Icon name="chevron" width={15} />
      </summary>
      <div className="audit-findings">
        {[...audit.findings]
          .sort((a, b) => order[a.severity] - order[b.severity])
          .map((finding) => (
            <article className="finding" key={finding.id}>
              <Badge
                tone={finding.severity === "bloqueante" ? "warning" : "neutral"}
              >
                {finding.dataset} ·{" "}
                {finding.severity === "bloqueante"
                  ? "Limitação da análise"
                  : finding.severity === "alerta"
                    ? "Ponto de atenção"
                    : "Observação"}
              </Badge>
              <h3>{finding.title}</h3>
              <p>{finding.evidence}</p>
              <p className="finding-implication">{finding.implication}</p>
            </article>
          ))}
      </div>
    </details>
  );
}

export function StatusMix({ audit }: { audit: AuditReport }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Uma fotografia dos tickets</h2>
          <p>Distribuição dos registros por status.</p>
        </div>
        <Badge>D1 · Observado</Badge>
      </div>
      <div className="panel-body">
        {audit.d1.statusMix.map((item, index) => (
          <div className="mix-row" key={item.status}>
            <div className="mix-label">
              <span>{statusLabels[item.status] ?? item.status}</span>
              <strong>
                {percent(item.share)}{" "}
                <span className="muted" style={{ fontWeight: 400 }}>
                  · {number(item.n)}
                </span>
              </strong>
            </div>
            <div className="progress-track" aria-hidden="true">
              <span
                className={`progress-fill ${index === 0 ? "gold" : index === 2 ? "green" : ""}`}
                style={{ width: `${item.share * 100}%` }}
              />
            </div>
          </div>
        ))}
        <p className="field-hint" style={{ marginTop: 24 }}>
          Contagens do arquivo sintético. Os status, isoladamente, não medem
          tempo de espera ou produtividade.
        </p>
        <SourceNote
          source="Dataset 1 · Customer Support Tickets"
          generatedAt={audit.generatedAt}
        />
      </div>
    </section>
  );
}

export function SegmentHeatmap({ report }: { report: DiagnosticoReport }) {
  const channels = [...new Set(report.segments.map((s) => s.channel))];
  const priorities = ["Low", "Medium", "High", "Critical"].filter((p) =>
    report.segments.some((s) => s.priority === p),
  );
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Canal e prioridade</h2>
          <p>Proporção de registros não fechados em cada grupo.</p>
        </div>
        <Badge>D1 · Descritivo</Badge>
      </div>
      <div className="panel-body">
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Tickets não fechados por canal e prioridade"
        >
          <table className="heatmap">
            <thead>
              <tr>
                <th scope="col">Canal</th>
                {priorities.map((p) => (
                  <th scope="col" key={p}>
                    {priorityLabels[p]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {channels.map((channel) => (
                <tr key={channel}>
                  <th scope="row">{channelLabels[channel] ?? channel}</th>
                  {priorities.map((priority) => {
                    const cell = report.segments.find(
                      (s) => s.channel === channel && s.priority === priority,
                    );
                    return (
                      <td key={priority}>
                        {cell ? (
                          <span
                            className="heat-cell"
                            style={{
                              background: `rgba(73,119,146,${0.04 + cell.backlogShare * 0.2})`,
                            }}
                          >
                            <strong>{percent(cell.backlogShare)}</strong>
                            <small>{number(cell.n)} tickets</small>
                            <small className="heat-ci">
                              IC 95%
                              <br />
                              {percent(cell.backlogCI.low)}–
                              {percent(cell.backlogCI.high)}
                            </small>
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="chart-legend">
          <span>Menor proporção</span>
          <span className="legend-scale" />
          <span>Maior</span>
        </div>
        <p className="field-hint" style={{ marginTop: 16 }}>
          A cor representa uma contagem, não uma classificação de gargalo. IC
          95% indica o intervalo de confiança da proporção de cada grupo.
        </p>
      </div>
    </section>
  );
}

export function DiagnosticDetails({ report }: { report: DiagnosticoReport }) {
  return (
    <>
      <section className="section">
        <SectionHeading
          eyebrow="O que foi verificado"
          title="Evidências antes de conclusões."
          description="Os testes ajudam a avaliar se as diferenças observadas sustentam uma interpretação operacional."
        />
        <div className="equal-columns">
          <div className="panel">
            <div className="panel-header">
              <h3>Diferenças entre segmentos</h3>
              <Badge>D1</Badge>
            </div>
            <div className="panel-body stack">
              {report.tests.segmentTests.map((test) => (
                <div key={test.variable}>
                  <div className="mix-label">
                    <strong>
                      {variableLabels[test.variable] ?? test.variable}
                    </strong>
                    <Badge tone={test.significant ? "warning" : "neutral"}>
                      p = {number(test.pValue, 3)}
                    </Badge>
                  </div>
                  <p className="small-copy muted">{test.conclusion}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <div className="panel-header">
              <h3>Associação com a satisfação</h3>
              <Badge>CSAT</Badge>
            </div>
            <div>
              {report.tests.csatDrivers.map((driver) => (
                <details className="detail-section" key={driver.variable}>
                  <summary>
                    <span>
                      {variableLabels[driver.variable] ?? driver.variable}
                    </span>
                    <Badge tone={driver.pValue <= 0.05 ? "warning" : "neutral"}>
                      p = {number(driver.pValue, 3)}
                    </Badge>
                    <Icon name="chevron" width={14} />
                  </summary>
                  <div className="detail-content">
                    <p className="small-copy muted">{driver.conclusion}</p>
                    <p className="source-note">
                      {driver.test} · Tamanho de efeito:{" "}
                      {number(driver.effectSize, 4)}
                    </p>
                    <div
                      className="table-scroll"
                      tabIndex={0}
                      role="region"
                      aria-label={`CSAT por grupo: ${variableLabels[driver.variable] ?? driver.variable}`}
                    >
                      <table>
                        <thead>
                          <tr>
                            <th scope="col">Grupo</th>
                            <th scope="col" className="numeric">
                              CSAT médio
                            </th>
                            <th scope="col" className="numeric">
                              IC 95%
                            </th>
                            <th scope="col" className="numeric">
                              n
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {driver.groups.map((group) => (
                            <tr key={group.label}>
                              <td>{group.label}</td>
                              <td className="numeric">
                                {number(group.mean, 2)}
                              </td>
                              <td className="numeric">
                                {number(group.ci.low, 2)}–
                                {number(group.ci.high, 2)}
                              </td>
                              <td className="numeric">{number(group.n)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </details>
              ))}
            </div>
          </div>
        </div>
      </section>
      <section className="section" id="cenario">
        <SectionHeading
          eyebrow="Da análise à decisão"
          title="Explore o potencial de economia."
          description="As premissas podem ser ajustadas ao contexto da sua operação. As referências de classificação vêm de outra base, de TI interna."
        />
        <WasteCalculator scenario={report.scenario} />
        <SourceNote
          source="Cenário estimado · Diagnóstico operacional"
          generatedAt={report.generatedAt}
        />
      </section>
      {report.limitations.length > 0 && (
        <section className="section">
          <Notice title="Limites que acompanham esta análise">
            {report.limitations.map((item) => (
              <p key={item.id} style={{ marginTop: 6 }}>
                {item.text}
              </p>
            ))}
          </Notice>
        </section>
      )}
    </>
  );
}
