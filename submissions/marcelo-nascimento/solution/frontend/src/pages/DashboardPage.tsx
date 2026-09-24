import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BarList, EmptyState, ErrorState, LoadingState, MetricCard, ScoreBadge } from "../components/Common.js";
import { api } from "../lib/api.js";
import { formatCurrency, formatDecimal, formatNumber } from "../lib/format.js";
import type { DashboardData } from "../types.js";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const requestVersion = useRef(0);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    try {
      const result = await api.dashboard();
      if (version === requestVersion.current) {
        setData(result);
      }
    } catch (requestError) {
      if (version === requestVersion.current) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao carregar o dashboard.");
      }
    } finally {
      if (version === requestVersion.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void load();
    return () => {
      requestVersion.current += 1;
    };
  }, [load]);

  if (loading) {
    return <LoadingState label="Carregando indicadores do pipeline..." />;
  }

  if (error || !data) {
    return <ErrorState message={error || "Dados indisponíveis."} onRetry={() => void load()} />;
  }

  return (
    <div className="page-stack">
      <div className="metric-grid">
        <MetricCard icon="fa-briefcase" label="Oportunidades abertas" value={formatNumber(data.metrics.openOpportunities)} detail="Prospecting e Engaging" />
        <MetricCard icon="fa-fire" label="Hot Leads" value={formatNumber(data.metrics.hotLeads)} detail="Score igual ou superior a 75" accent="teal" />
        <MetricCard icon="fa-bullseye" label="Score médio aberto" value={data.metrics.averageOpenScore === null ? "Não disponível" : formatDecimal(data.metrics.averageOpenScore)} detail="Média dos scores calculados pelo backend" accent="teal" />
        <MetricCard icon="fa-dollar-sign" label="Valor do pipeline" value={formatCurrency(data.metrics.pipelineValue)} detail="Somente valores disponíveis" />
      </div>

      <section className="panel">
        <div className="panel-heading">
          <div><span className="eyebrow">Onde focar</span><h2>Oportunidades prioritárias</h2></div>
          <button className="btn btn-sm btn-outline-info" type="button" onClick={() => navigate("/leads")}>Ver pipeline <i className="fa-solid fa-arrow-right" aria-hidden="true" /></button>
        </div>
        {data.priorityOpportunities.length === 0 ? (
          <EmptyState title="Nenhuma oportunidade aberta" message="Não há oportunidades abertas para priorização." />
        ) : (
          <div className="priority-grid">
            {data.priorityOpportunities.map((opportunity) => (
              <button className="priority-card" type="button" key={opportunity.id} onClick={() => navigate(`/leads/${opportunity.id}`)}>
                <div className="priority-top">
                  <ScoreBadge score={opportunity.score} hot={opportunity.isHotLead} />
                  <span className={`stage stage-${opportunity.dealStage.toLowerCase()}`}>{opportunity.dealStage}</span>
                </div>
                <strong>{opportunity.account ?? "Cliente não informado"}</strong>
                <span>{opportunity.product}</span>
                <small>{opportunity.salesAgent}</small>
                <i className="fa-solid fa-chevron-right" aria-hidden="true" />
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div><span className="eyebrow">Distribuição</span><h2>Scores das oportunidades abertas</h2></div>
        </div>
        <BarList
          items={data.scoreDistribution.map((band) => ({ name: band.label, value: band.count }))}
          valueLabel={(value) => `${value} oportunidade${value === 1 ? "" : "s"}`}
          emptyMessage="Não há scores para exibir."
        />
      </section>

      <div className="info-banner">
        <i className="fa-solid fa-circle-info" aria-hidden="true" />
        <span>O score representa a força relativa das evidências históricas de aderência. Ele não é uma probabilidade de fechamento.</span>
      </div>
    </div>
  );
}
