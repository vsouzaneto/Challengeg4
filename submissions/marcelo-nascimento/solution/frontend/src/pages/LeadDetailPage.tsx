import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ErrorState, LoadingState, ScoreBadge } from "../components/Common.js";
import { api } from "../lib/api.js";
import { formatCurrency, formatDate, formatMillions, formatNumber, formatPoints } from "../lib/format.js";
import type { OpportunityDetail, ScoreFactor } from "../types.js";

function evidenceNumber(factor: ScoreFactor, key: string): number | null {
  const value = factor.evidence[key];
  return typeof value === "number" ? value : null;
}

function evidenceText(factor: ScoreFactor, key: string): string | null {
  const value = factor.evidence[key];
  return typeof value === "string" ? value : null;
}

function FactorEvidence({ factor }: { factor: ScoreFactor }) {
  if (factor.id === "account_product_fit") {
    return <span>Produto exato: {evidenceNumber(factor, "exactWon") ?? 0} Won / {evidenceNumber(factor, "exactLost") ?? 0} Lost · Família: {evidenceNumber(factor, "seriesWon") ?? 0} Won / {evidenceNumber(factor, "seriesLost") ?? 0} Lost</span>;
  }
  if (factor.id === "sector_product_fit") {
    return <span>{evidenceText(factor, "sector") ?? "Setor não informado"}: {evidenceNumber(factor, "won") ?? 0} Won / {evidenceNumber(factor, "lost") ?? 0} Lost</span>;
  }
  if (factor.id === "company_profile_fit") {
    return <span>Medianas históricas: {formatNumber(evidenceNumber(factor, "medianEmployees"))} funcionários · {formatMillions(evidenceNumber(factor, "medianRevenue"))}</span>;
  }
  return <span>Faixa histórica: {formatMillions(evidenceNumber(factor, "q1"))} a {formatMillions(evidenceNumber(factor, "q3"))} · {evidenceNumber(factor, "sampleSize") ?? 0} clientes distintos</span>;
}

export default function LeadDetailPage() {
  const { id } = useParams();
  const [opportunity, setOpportunity] = useState<OpportunityDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const requestVersion = useRef(0);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    if (!id) {
      return;
    }
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    try {
      const result = await api.opportunity(id);
      if (version === requestVersion.current) {
        setOpportunity(result.data);
      }
    } catch (requestError) {
      if (version === requestVersion.current) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao carregar o detalhamento.");
      }
    } finally {
      if (version === requestVersion.current) {
        setLoading(false);
      }
    }
  }, [id]);

  useEffect(() => {
    void load();
    return () => {
      requestVersion.current += 1;
    };
  }, [load]);

  if (loading) {
    return <LoadingState label="Carregando evidências da oportunidade..." />;
  }

  if (error || !opportunity) {
    return <ErrorState message={error || "Oportunidade indisponível."} onRetry={() => void load()} />;
  }

  const score = opportunity.score;
  return (
    <div className="page-stack">
      <button className="btn btn-sm back-button" type="button" onClick={() => navigate("/leads")}><i className="fa-solid fa-arrow-left" aria-hidden="true" /> Voltar para oportunidades</button>
      <section className="detail-hero panel">
        <div>
          <span className="eyebrow">Oportunidade {opportunity.id}</span>
          <h2>{opportunity.account ?? "Cliente não informado"}</h2>
          <p>{opportunity.product} · {opportunity.series ?? "Série não informada"}</p>
          <div className="detail-tags">
            <span className={`stage stage-${opportunity.dealStage.toLowerCase()}`}>{opportunity.dealStage}</span>
            <span><i className="fa-regular fa-user" aria-hidden="true" /> {opportunity.salesAgent}</span>
            {opportunity.sector ? <span><i className="fa-solid fa-building" aria-hidden="true" /> {opportunity.sector}</span> : null}
          </div>
        </div>
        <div className="score-hero">
          <ScoreBadge score={score.score} hot={opportunity.isHotLead} />
          <span>de 100</span>
          <small>Score bruto {formatPoints(score.rawScore)}</small>
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel context-panel">
          <div className="panel-heading compact"><h2>Contexto da oportunidade</h2></div>
          <dl className="context-list">
            <div><dt>Cliente</dt><dd>{opportunity.account ?? "Não informado"}</dd></div>
            <div><dt>Produto</dt><dd>{opportunity.product}</dd></div>
            <div><dt>Setor</dt><dd>{opportunity.sector ?? "Não informado"}</dd></div>
            <div><dt>Funcionários</dt><dd>{formatNumber(opportunity.employees)}</dd></div>
            <div><dt>Receita anual</dt><dd>{formatMillions(opportunity.revenue)}</dd></div>
            <div><dt>Preço do produto</dt><dd>{formatCurrency(opportunity.salesPrice)}</dd></div>
            <div><dt>Vendedor</dt><dd>{opportunity.salesAgent}</dd></div>
            <div><dt>Manager</dt><dd>{opportunity.manager ?? "Não informado"}</dd></div>
            <div><dt>Escritório</dt><dd>{opportunity.regionalOffice ?? "Não informado"}</dd></div>
            <div><dt>Data de engajamento</dt><dd>{formatDate(opportunity.engageDate)}</dd></div>
            <div><dt>Data de fechamento</dt><dd>{formatDate(opportunity.closeDate)}</dd></div>
            <div><dt>Valor de fechamento</dt><dd>{formatCurrency(opportunity.closeValue)}</dd></div>
          </dl>
        </div>

        <div className="panel breakdown-panel">
          <div className="panel-heading compact"><div><span className="eyebrow">Explicabilidade</span><h2>Composição do score</h2></div></div>
          <div className="factor-list">
            {score.factors.map((factor) => (
              <article className="factor-card" key={factor.id}>
                <div className="factor-heading">
                  <div><strong>{factor.label}</strong><span className={`strength strength-${factor.strength.replace(" ", "-")}`}>{factor.strength}</span></div>
                  <b>{formatPoints(factor.points)} / {factor.maxPoints}</b>
                </div>
                <div className="progress" role="progressbar" aria-label={factor.label} aria-valuemin={0} aria-valuemax={factor.maxPoints} aria-valuenow={factor.points}>
                  <div className="progress-bar" style={{ width: `${factor.points / factor.maxPoints * 100}%` }} />
                </div>
                <p>{factor.reason}</p>
                <small><i className="fa-solid fa-database" aria-hidden="true" /> <FactorEvidence factor={factor} /></small>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="panel justification-panel">
        <span className="justification-icon"><i className="fa-solid fa-comment-dots" aria-hidden="true" /></span>
        <div><span className="eyebrow">Justificativa do backend</span><h2>Por que este score?</h2><p>{score.justification}</p></div>
      </section>

      <div className="info-banner">
        <i className="fa-solid fa-circle-info" aria-hidden="true" />
        <span>Calculado em {new Date(score.calculatedAt).toLocaleString("pt-BR")}. O score não representa probabilidade de fechamento.</span>
      </div>
    </div>
  );
}
