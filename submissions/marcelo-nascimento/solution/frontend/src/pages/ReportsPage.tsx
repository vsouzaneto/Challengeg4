import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BarList, EmptyState, ErrorState, LoadingState } from "../components/Common.js";
import { api } from "../lib/api.js";
import { formatDecimal, formatNumber, formatPercent } from "../lib/format.js";
import type { FilterOptions, ReportData } from "../types.js";

export default function ReportsPage() {
  const [filters, setFilters] = useState({ product: "", sector: "", seller: "", stage: "" });
  const [options, setOptions] = useState<FilterOptions | null>(null);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [optionsError, setOptionsError] = useState("");
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const requestVersion = useRef(0);
  const activeFilters = useMemo(() => Object.values(filters).filter(Boolean).length, [filters]);

  const load = useCallback(async () => {
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    try {
      const query = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          query.set(key, value);
        }
      });
      const response = await api.reports(query);
      if (version === requestVersion.current) {
        setData(response);
      }
    } catch (requestError) {
      if (version === requestVersion.current) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao carregar os relatórios.");
      }
    } finally {
      if (version === requestVersion.current) {
        setLoading(false);
      }
    }
  }, [filters]);

  const loadOptions = useCallback(async () => {
    setOptionsLoading(true);
    setOptionsError("");
    try {
      setOptions(await api.opportunityFilters());
    } catch (requestError) {
      setOptionsError(requestError instanceof Error ? requestError.message : "Falha ao carregar os filtros.");
    } finally {
      setOptionsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadOptions();
  }, [loadOptions]);

  useEffect(() => {
    void load();
    return () => {
      requestVersion.current += 1;
    };
  }, [load]);

  function updateFilter(key: keyof typeof filters, value: string): void {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  return (
    <div className="page-stack">
      <section className="panel filters-panel">
        <div className="panel-heading compact">
          <div><span className="eyebrow">Visão analítica</span><h2>Filtros dos relatórios</h2></div>
          {activeFilters > 0 ? <button className="btn btn-sm btn-outline-secondary" type="button" onClick={() => setFilters({ product: "", sector: "", seller: "", stage: "" })}>Limpar filtros</button> : null}
        </div>
        {optionsError ? <div className="filter-error"><ErrorState message={optionsError} onRetry={() => void loadOptions()} /></div> : null}
        {activeFilters > 0 ? <div className="active-filters"><i className="fa-solid fa-sliders" aria-hidden="true" /> {activeFilters} filtro{activeFilters === 1 ? "" : "s"} ativo{activeFilters === 1 ? "" : "s"}</div> : null}
        <div className="report-filters">
          <label>Produto<select disabled={optionsLoading || Boolean(optionsError)} value={filters.product} onChange={(event) => updateFilter("product", event.target.value)}><option value="">Todos</option>{options?.products.map((product) => <option key={product}>{product}</option>)}</select></label>
          <label>Setor<select disabled={optionsLoading || Boolean(optionsError)} value={filters.sector} onChange={(event) => updateFilter("sector", event.target.value)}><option value="">Todos</option>{options?.sectors.map((sector) => <option value={sector.id} key={sector.id}>{sector.label}</option>)}</select></label>
          <label>Vendedor<select disabled={optionsLoading || Boolean(optionsError)} value={filters.seller} onChange={(event) => updateFilter("seller", event.target.value)}><option value="">Todos</option>{options?.sellers.map((seller) => <option key={seller}>{seller}</option>)}</select></label>
          <label>Estágio<select disabled={optionsLoading || Boolean(optionsError)} value={filters.stage} onChange={(event) => updateFilter("stage", event.target.value)}><option value="">Todos</option>{options?.stages.map((stage) => <option key={stage}>{stage}</option>)}</select></label>
        </div>
      </section>

      {loading ? <LoadingState label="Agregando relatórios..." /> : null}
      {error ? <ErrorState message={error} onRetry={() => void load()} /> : null}
      {!loading && !error && data ? (
        data.total === 0 ? <EmptyState title="Nenhum resultado" message="Nenhuma oportunidade corresponde aos filtros selecionados." /> : (
          <div className="report-grid">
            <section className="panel report-card">
              <div className="panel-heading compact"><div><span className="eyebrow">Priorização</span><h2>Distribuição de scores</h2></div></div>
              <BarList items={data.distribution.map((item) => ({ name: item.label, value: item.count }))} valueLabel={(value) => `${value} opções`} emptyMessage="Sem distribuição." />
            </section>
            <section className="panel report-card">
              <div className="panel-heading compact"><div><span className="eyebrow">Produtos</span><h2>Score médio por produto</h2></div></div>
              <BarList items={data.averageByProduct.map((item) => ({ name: item.name, value: item.averageScore ?? 0, secondary: `${formatNumber(item.count)} oportunidades` }))} valueLabel={formatDecimal} emptyMessage="Sem produtos." />
            </section>
            <section className="panel report-card">
              <div className="panel-heading compact"><div><span className="eyebrow">Setores</span><h2>Score médio por setor</h2></div></div>
              <BarList items={data.averageBySector.map((item) => ({ name: item.name, value: item.averageScore ?? 0, secondary: `${formatNumber(item.count)} oportunidades` }))} valueLabel={formatDecimal} emptyMessage="Sem setores." />
            </section>
            <section className="panel report-card">
              <div className="panel-heading compact"><div><span className="eyebrow">Funil</span><h2>Pipeline por estágio</h2></div></div>
              <BarList items={data.pipelineByStage.map((item) => ({ name: item.stage, value: item.count }))} valueLabel={(value) => `${value} oportunidades`} emptyMessage="Sem pipeline." />
            </section>
            <section className="panel report-card report-wide">
              <div className="panel-heading compact"><div><span className="eyebrow">Histórico</span><h2>Conversão por produto</h2></div></div>
              <BarList items={data.historicalConversionByProduct.map((item) => ({ name: item.name, value: item.conversionRate, secondary: `${formatNumber(item.won)} Won · ${formatNumber(item.lost)} Lost · ${formatNumber(item.count)} encerradas` }))} valueLabel={formatPercent} emptyMessage="Sem negócios encerrados." />
            </section>
          </div>
        )
      ) : null}
      <div className="info-banner"><i className="fa-solid fa-circle-info" aria-hidden="true" /><span>A conversão por produto usa apenas oportunidades Won e Lost e representa um dado histórico, não uma previsão.</span></div>
    </div>
  );
}
