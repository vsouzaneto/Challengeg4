import type { QualidadeDados } from "../types";

type Props = { data: QualidadeDados | undefined };

export function DataQualityCard({ data }: Props) {
  if (!data) return null;

  return (
    <section className="insight-card data-quality">
      <h2 className="section-title">Integridade dos dados</h2>
      <p className="chart-hint">
        Cadastro vs eventos — leitura CEO em <code>reports/data_quality_ceo.md</code>.
      </p>
      <div className="dq-grid">
        <div className="dq-item">
          <span className="label">Flag churn sem evento</span>
          <span className="value">{data.contas_flag_sem_evento_churn}</span>
        </div>
        <div className="dq-item">
          <span className="label">MRR exposto (USD)</span>
          <span className="value">
            {data.mrr_contratual_flag_sem_evento_usd.toLocaleString("en-US", {
              maximumFractionDigits: 0,
            })}
          </span>
        </div>
        <div className="dq-item">
          <span className="label">Uso antes da assinatura</span>
          <span className="value">{data.pct_uso_antes_assinatura}%</span>
        </div>
        <div className="dq-item">
          <span className="label">Eventos vs contas c/ evento</span>
          <span className="value">
            {data.eventos_churn_total} / {data.contas_com_evento}
          </span>
        </div>
      </div>
    </section>
  );
}
