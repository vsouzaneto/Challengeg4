import type { Metadata } from "next";
import Link from "next/link";
import { readModelMetrics, readRouting } from "@/lib/data";
import {
  categoryLabels,
  number,
  percent,
  routeLabels,
  routeTone,
} from "@/components/format";
import {
  Badge,
  Notice,
  PageHeading,
  SectionHeading,
  SourceNote,
  Stat,
  Unavailable,
} from "@/components/ui";
import { Icon } from "@/components/icons";
import { RoutingDetails } from "@/components/model-routing";

export const metadata: Metadata = { title: "Avaliação do modelo" };
const splitLabels = {
  treino: "Treino",
  validacao: "Validação",
  teste: "Teste",
};
export default async function ModelPage() {
  const [model, routing] = await Promise.all([
    readModelMetrics(),
    readRouting(),
  ]);
  return (
    <>
      <PageHeading
        eyebrow="Evidências da solução"
        title="Confiança se constrói com avaliação."
        description="Resultados de classificação e roteamento, com os limites e as decisões que acompanham cada número."
        action={
          <Link className="button secondary" href="/triagem">
            Testar um ticket
            <Icon name="arrow" width={16} />
          </Link>
        }
      />
      {!model ? (
        <Unavailable title="A avaliação do modelo está em atualização." />
      ) : (
        <>
          <Notice title="Treino, escolha e avaliação têm papéis distintos.">
            Os candidatos abaixo são comparados na validação. Os indicadores de
            desempenho publicados vêm do teste. Os resultados exploratórios
            anteriores permanecem identificados como histórico.
          </Notice>
          <div className="stats-grid">
            <Stat
              label="Acerto de classificação · teste"
              value={percent(model.test.accuracy)}
              detail={`IC 95%: ${percent(model.test.accuracyCI.low)}–${percent(model.test.accuracyCI.high)}`}
              icon="check"
            />
            <Stat
              label="F1 macro · teste"
              value={number(model.test.macroF1, 3)}
              detail={`IC 95%: ${number(model.test.macroF1CI.low, 3)}–${number(model.test.macroF1CI.high, 3)}`}
              icon="chart"
            />
            <Stat
              label="Referência majoritária · teste"
              value={percent(model.test.baselineAccuracy)}
              detail="Acerto ao prever sempre a classe mais frequente"
              icon="model"
            />
            <Stat
              label="Acerto na rota automática"
              value={routing ? percent(routing.test.auto.accuracy) : "—"}
              detail={
                routing
                  ? `Cobertura de ${percent(routing.test.auto.share)} dos tickets de teste`
                  : "Avaliação completa do roteamento pendente"
              }
              icon="flow"
              tone="gold"
            />
          </div>
          <section className="section panel">
            <div className="panel-header">
              <h2>Como os dados foram separados</h2>
              <Badge>D2 · Partições estratificadas</Badge>
            </div>
            <div className="panel-body">
              <div className="split-bar" aria-hidden="true">
                {model.splits.map((split) => (
                  <span
                    key={split.name}
                    style={{ width: `${split.share * 100}%` }}
                  />
                ))}
              </div>
              <div className="split-labels">
                {model.splits.map((split) => (
                  <div key={split.name}>
                    <h3>{splitLabels[split.name]}</h3>
                    <strong>
                      {number(split.n)}{" "}
                      <span className="field-hint">
                        · {percent(split.share, 0)}
                      </span>
                    </strong>
                    <p>{split.purpose}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
          <section className="section">
            <SectionHeading
              eyebrow="Seleção do modelo"
              title="A escolha precisa ter uma justificativa."
              description={model.selection.model}
            />
            <div className="two-columns">
              <div
                className="panel table-scroll"
                tabIndex={0}
                role="region"
                aria-label="Comparação dos modelos na validação"
              >
                <table>
                  <thead>
                    <tr>
                      <th>Candidato</th>
                      <th className="numeric">Acurácia</th>
                      <th className="numeric">F1 macro</th>
                    </tr>
                  </thead>
                  <tbody>
                    {model.selection.candidates.map((candidate) => (
                      <tr key={candidate.name}>
                        <td>{candidate.name}</td>
                        <td className="numeric">
                          {percent(candidate.accuracy)}
                        </td>
                        <td className="numeric">
                          {number(candidate.macroF1, 3)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="panel panel-padding">
                <p className="eyebrow">Critérios de escolha · validação</p>
                <ul className="review-list">
                  {model.selection.criteria.map((criterion) => (
                    <li key={criterion}>
                      <Icon name="check" />
                      <span>{criterion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
          <section className="section">
            <SectionHeading
              eyebrow="Desempenho por categoria"
              title="A média não conta toda a história."
              description="Precisão, recall e F1 no conjunto de teste. Categorias menos frequentes também precisam funcionar."
            />
            <div
              className="panel table-scroll"
              tabIndex={0}
              role="region"
              aria-label="Métricas por categoria"
            >
              <table>
                <thead>
                  <tr>
                    <th>Categoria</th>
                    <th>F1</th>
                    <th className="numeric">Precisão</th>
                    <th className="numeric">Recall</th>
                    <th className="numeric">Tickets</th>
                  </tr>
                </thead>
                <tbody>
                  {model.test.perClass.map((item) => (
                    <tr key={item.label}>
                      <td className="row-label">
                        {categoryLabels[item.label]}
                      </td>
                      <td>
                        <div className="metric-bar">
                          <div className="progress-track" aria-hidden="true">
                            <span
                              className="progress-fill"
                              style={{ width: `${item.f1 * 100}%` }}
                            />
                          </div>
                          <span>{number(item.f1, 3)}</span>
                        </div>
                      </td>
                      <td className="numeric">{percent(item.precision)}</td>
                      <td className="numeric">{percent(item.recall)}</td>
                      <td className="numeric">{number(item.support)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <section className="section panel">
            <div className="panel-header">
              <div>
                <h2>Onde as categorias se confundem</h2>
                <p>
                  Linhas: rótulo real. Colunas: previsão. A diagonal representa
                  os acertos.
                </p>
              </div>
              <Badge>Matriz de confusão · teste</Badge>
            </div>
            <div className="panel-body">
              <div
                className="table-scroll"
                tabIndex={0}
                role="region"
                aria-label="Matriz de confusão com contagens por categoria"
              >
                <table className="confusion-table">
                  <thead>
                    <tr>
                      <th scope="col">Real / Previsto</th>
                      {model.test.confusion.labels.map((label) => (
                        <th scope="col" key={label}>
                          {categoryLabels[label]}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {model.test.confusion.matrix.map((row, i) => {
                      const total = row.reduce((sum, n) => sum + n, 0);
                      return (
                        <tr key={model.test.confusion.labels[i]}>
                          <th scope="row">
                            {categoryLabels[model.test.confusion.labels[i]]}
                          </th>
                          {row.map((count, j) => (
                            <td
                              key={j}
                              style={{
                                background: count
                                  ? `rgba(${i === j ? "63,116,141" : "185,145,91"},${0.04 + (count / Math.max(total, 1)) * 0.35})`
                                  : "#fafbfc",
                                fontWeight: i === j ? 650 : 400,
                              }}
                              title={`${percent(count / Math.max(total, 1))} da categoria real`}
                            >
                              {number(count)}
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </>
      )}
      {routing && (
        <section className="section">
          <SectionHeading
            eyebrow="Avaliação do fluxo completo"
            title="Automatizar também é saber encaminhar."
            description={routing.note}
          />
          <div className="two-columns">
            <div className="panel">
              <div className="panel-header">
                <h3>Destinos no conjunto de teste</h3>
                <Badge>{number(routing.test.n)} tickets</Badge>
              </div>
              <div className="panel-body">
                {routing.test.routes.map((item) => (
                  <div className="mix-row" key={item.route}>
                    <div className="mix-label">
                      <Badge tone={routeTone[item.route]}>
                        {routeLabels[item.route]}
                      </Badge>
                      <strong>
                        {percent(item.share)} · {number(item.n)}
                      </strong>
                    </div>
                    <div className="progress-track" aria-hidden="true">
                      <span
                        className={`progress-fill ${item.route === "auto" ? "green" : item.route === "escalar" ? "red" : "gold"}`}
                        style={{ width: `${item.share * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="panel panel-padding">
              <p className="eyebrow">Limiares escolhidos na validação</p>
              <div className="mix-label">
                <span>Confiança mínima</span>
                <strong>{percent(routing.thresholds.confidence, 0)}</strong>
              </div>
              <div className="mix-label">
                <span>Vocabulário conhecido</span>
                <strong>{percent(routing.thresholds.ood, 0)}</strong>
              </div>
              <div className="mix-label">
                <span>Alerta de privilégio administrativo</span>
                <strong>
                  {routing.thresholds.adminRights === null
                    ? "Desativado"
                    : percent(routing.thresholds.adminRights, 0)}
                </strong>
              </div>
              <p className="small-copy muted" style={{ marginTop: 20 }}>
                O limiar de confiança atua junto com as regras de risco, domínio
                e aprovação humana. Os indicadores acima já incluem essa
                política completa.
              </p>
            </div>
          </div>
          <div style={{ marginTop: 18 }}>
            <Notice
              title="Pedidos de privilégio exigem acompanhamento."
              tone="warning"
            >
              No teste,{" "}
              {number(routing.test.adminRightsLeak.autoRoutedElsewhere)} de{" "}
              {number(routing.test.adminRightsLeak.trueAdminRights)} tickets
              rotulados como privilégio administrativo foram encaminhados
              automaticamente a outra categoria. Classificar ou encaminhar um
              ticket não concede acesso.
            </Notice>
          </div>
          <RoutingDetails report={routing} />
          <SourceNote
            source="Avaliação das funções de roteamento utilizadas pela API"
            generatedAt={routing.generatedAt}
          />
        </section>
      )}
      {model && (
        <>
          <section className="section">
            <SectionHeading
              eyebrow="Limites de aplicação"
              title="Outro contexto exige uma nova validação."
            />
            <Notice
              title="O resultado em TI interna não se transfere automaticamente para outra operação."
              tone="warning"
            >
              {model.crossDomain.note}
            </Notice>
          </section>
          <details className="audit-summary">
            <summary>
              <Icon name="book" width={18} />
              <strong>Histórico da avaliação exploratória</strong>
              <Icon name="chevron" width={15} />
            </summary>
            <div className="panel-body">
              <p className="small-copy muted">{model.exploratory.note}</p>
              <p className="source-note">
                Acurácia exploratória: {percent(model.exploratory.accuracy)} ·
                F1 macro: {number(model.exploratory.macroF1, 3)}. Estes não são
                os resultados atuais de teste.
              </p>
            </div>
          </details>
          <SourceNote
            source="Dataset 2 · IT Service Ticket Classification"
            generatedAt={model.generatedAt}
          />
        </>
      )}
    </>
  );
}
