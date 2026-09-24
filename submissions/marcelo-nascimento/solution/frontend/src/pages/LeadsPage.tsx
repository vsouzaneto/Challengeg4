import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { EmptyState, ErrorState, LoadingState, ScoreBadge } from "../components/Common.js";
import { api } from "../lib/api.js";
import { formatNumber } from "../lib/format.js";
import type { FilterOptions, PaginatedOpportunities } from "../types.js";

interface Filters {
  search: string;
  stage: string;
  product: string;
  sector: string;
  seller: string;
  scoreBand: string;
}

type SortField = "score" | "account" | "product" | "stage";
type SortOrder = "asc" | "desc";

const emptyFilters: Filters = { search: "", stage: "", product: "", sector: "", seller: "", scoreBand: "" };

function pageNumbers(current: number, total: number): number[] {
  const start = Math.max(1, Math.min(current - 2, total - 4));
  const end = Math.min(total, start + 4);
  return Array.from({ length: Math.max(0, end - start + 1) }, (_, index) => start + index);
}

export default function LeadsPage() {
  const [filters, setFilters] = useState<Filters>(emptyFilters);
  const [searchInput, setSearchInput] = useState("");
  const [options, setOptions] = useState<FilterOptions | null>(null);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [optionsError, setOptionsError] = useState("");
  const [result, setResult] = useState<PaginatedOpportunities | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [sort, setSort] = useState<SortField>("score");
  const [order, setOrder] = useState<SortOrder>("desc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const requestVersion = useRef(0);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    try {
      const query = new URLSearchParams({ page: String(page), pageSize: String(pageSize), sort, order });
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          query.set(key, value);
        }
      });
      const response = await api.opportunities(query);
      if (version === requestVersion.current) {
        setResult(response);
      }
    } catch (requestError) {
      if (version === requestVersion.current) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao carregar as oportunidades.");
      }
    } finally {
      if (version === requestVersion.current) {
        setLoading(false);
      }
    }
  }, [filters, order, page, pageSize, sort]);

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

  const activeFilters = useMemo(
    () => Object.values(filters).filter(Boolean).length,
    [filters],
  );

  function updateFilter(key: keyof Filters, value: string): void {
    setPage(1);
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function submitSearch(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    updateFilter("search", searchInput.trim());
  }

  function changeSort(field: SortField): void {
    if (sort === field) {
      setOrder((current) => current === "asc" ? "desc" : "asc");
    } else {
      setSort(field);
      setOrder(field === "score" ? "desc" : "asc");
    }
    setPage(1);
  }

  function clearFilters(): void {
    setFilters(emptyFilters);
    setSearchInput("");
    setPage(1);
  }

  return (
    <div className="page-stack">
      <section className="panel filters-panel">
        <div className="panel-heading compact">
          <div><span className="eyebrow">Filtros</span><h2>Localizar oportunidades</h2></div>
          {activeFilters > 0 ? <button className="btn btn-sm btn-outline-secondary" type="button" onClick={clearFilters}>Limpar filtros</button> : null}
        </div>
        {optionsError ? <div className="filter-error"><ErrorState message={optionsError} onRetry={() => void loadOptions()} /></div> : null}
        <form className="filters-grid" onSubmit={submitSearch}>
          <div className="filter-search">
            <label htmlFor="lead-search">Buscar por cliente ou produto</label>
            <div className="input-shell">
              <i className="fa-solid fa-magnifying-glass" aria-hidden="true" />
              <input id="lead-search" value={searchInput} onChange={(event) => setSearchInput(event.target.value)} placeholder="Ex.: Acme ou GTX Pro" />
            </div>
          </div>
          <label>Estágio
            <select disabled={optionsLoading || Boolean(optionsError)} value={filters.stage} onChange={(event) => updateFilter("stage", event.target.value)}>
              <option value="">Todos</option>
              {options?.stages.map((stage) => <option value={stage} key={stage}>{stage}</option>)}
            </select>
          </label>
          <label>Produto
            <select disabled={optionsLoading || Boolean(optionsError)} value={filters.product} onChange={(event) => updateFilter("product", event.target.value)}>
              <option value="">Todos</option>
              {options?.products.map((product) => <option value={product} key={product}>{product}</option>)}
            </select>
          </label>
          <label>Setor
            <select disabled={optionsLoading || Boolean(optionsError)} value={filters.sector} onChange={(event) => updateFilter("sector", event.target.value)}>
              <option value="">Todos</option>
              {options?.sectors.map((sector) => <option value={sector.id} key={sector.id}>{sector.label}</option>)}
            </select>
          </label>
          <label>Vendedor
            <select disabled={optionsLoading || Boolean(optionsError)} value={filters.seller} onChange={(event) => updateFilter("seller", event.target.value)}>
              <option value="">Todos</option>
              {options?.sellers.map((seller) => <option value={seller} key={seller}>{seller}</option>)}
            </select>
          </label>
          <label>Faixa de score
            <select disabled={optionsLoading || Boolean(optionsError)} value={filters.scoreBand} onChange={(event) => updateFilter("scoreBand", event.target.value)}>
              <option value="">Todas</option>
              {options?.scoreBands.map((band) => <option value={band.id} key={band.id}>{band.label}</option>)}
            </select>
          </label>
          <button className="btn btn-primary align-self-end" type="submit"><i className="fa-solid fa-magnifying-glass" aria-hidden="true" /> Buscar</button>
        </form>
        {activeFilters > 0 ? <div className="active-filters"><i className="fa-solid fa-sliders" aria-hidden="true" /> {activeFilters} filtro{activeFilters === 1 ? "" : "s"} ativo{activeFilters === 1 ? "" : "s"}</div> : null}
      </section>

      {loading ? <LoadingState label="Calculando e organizando as oportunidades..." /> : null}
      {error ? <ErrorState message={error} onRetry={() => void load()} /> : null}

      {!loading && !error && result ? (
        <section className="panel table-panel">
          <div className="panel-heading compact">
            <div><h2>Pipeline</h2><p>{formatNumber(result.pagination.total)} oportunidade{result.pagination.total === 1 ? "" : "s"} encontrada{result.pagination.total === 1 ? "" : "s"}</p></div>
            <label className="page-size">Itens por página
              <select disabled={optionsLoading || Boolean(optionsError)} value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); setPage(1); }}>
                <option value={20}>20</option><option value={50}>50</option><option value={100}>100</option>
              </select>
            </label>
          </div>
          {result.data.length === 0 ? (
            <EmptyState title="Nenhuma oportunidade encontrada" message="Ajuste ou limpe os filtros selecionados." />
          ) : (
            <>
              <div className="desktop-table table-responsive">
                <table className="table leads-table">
                  <thead>
                    <tr>
                      <th aria-sort={ariaSort(sort, order, "account")}><button type="button" onClick={() => changeSort("account")}>Cliente {sortIcon(sort, order, "account")}</button></th>
                      <th aria-sort={ariaSort(sort, order, "product")}><button type="button" onClick={() => changeSort("product")}>Produto {sortIcon(sort, order, "product")}</button></th>
                      <th aria-sort={ariaSort(sort, order, "stage")}><button type="button" onClick={() => changeSort("stage")}>Estágio {sortIcon(sort, order, "stage")}</button></th>
                      <th>Vendedor</th>
                      <th aria-sort={ariaSort(sort, order, "score")}><button type="button" onClick={() => changeSort("score")}>Score {sortIcon(sort, order, "score")}</button></th>
                      <th><span className="visually-hidden">Ação</span></th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.data.map((opportunity) => (
                      <tr key={opportunity.id}>
                        <td data-label="Cliente"><strong>{opportunity.account ?? "Cliente não informado"}</strong><small>{opportunity.id}</small></td>
                        <td data-label="Produto">{opportunity.product}</td>
                        <td data-label="Estágio"><span className={`stage stage-${opportunity.dealStage.toLowerCase()}`}>{opportunity.dealStage}</span></td>
                        <td data-label="Vendedor">{opportunity.salesAgent}</td>
                        <td data-label="Score"><ScoreBadge score={opportunity.score} hot={opportunity.isHotLead} /></td>
                        <td data-label="Ação"><button className="btn btn-sm btn-outline-info" type="button" onClick={() => navigate(`/leads/${opportunity.id}`)}>Detalhes <i className="fa-solid fa-arrow-right" aria-hidden="true" /></button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mobile-lead-list">
                {result.data.map((opportunity) => (
                  <article className="lead-card" key={opportunity.id}>
                    <div className="lead-card-header">
                      <ScoreBadge score={opportunity.score} hot={opportunity.isHotLead} />
                      <span className={`stage stage-${opportunity.dealStage.toLowerCase()}`}>{opportunity.dealStage}</span>
                    </div>
                    <strong>{opportunity.account ?? "Cliente não informado"}</strong>
                    <span>{opportunity.product}</span>
                    <small>{opportunity.salesAgent} · {opportunity.id}</small>
                    <button className="btn btn-sm btn-outline-info" type="button" onClick={() => navigate(`/leads/${opportunity.id}`)}>Ver detalhes <i className="fa-solid fa-arrow-right" aria-hidden="true" /></button>
                  </article>
                ))}
              </div>
              <div className="pagination-bar">
                <span>Página {result.pagination.page} de {result.pagination.totalPages}</span>
                <nav aria-label="Paginação">
                  <button className="btn btn-sm btn-outline-secondary" disabled={page <= 1} onClick={() => setPage((current) => current - 1)} type="button" aria-label="Página anterior"><i className="fa-solid fa-chevron-left" aria-hidden="true" /></button>
                  {pageNumbers(result.pagination.page, result.pagination.totalPages).map((number) => <button className={`btn btn-sm ${number === page ? "btn-primary" : "btn-outline-secondary"}`} type="button" onClick={() => setPage(number)} key={number} aria-current={number === page ? "page" : undefined} aria-label={`Página ${number}`}>{number}</button>)}
                  <button className="btn btn-sm btn-outline-secondary" disabled={page >= result.pagination.totalPages} onClick={() => setPage((current) => current + 1)} type="button" aria-label="Próxima página"><i className="fa-solid fa-chevron-right" aria-hidden="true" /></button>
                </nav>
              </div>
            </>
          )}
        </section>
      ) : null}
    </div>
  );
}

function ariaSort(sort: SortField, order: SortOrder, field: SortField): "ascending" | "descending" | "none" {
  if (sort !== field) {
    return "none";
  }
  return order === "asc" ? "ascending" : "descending";
}

function sortIcon(sort: SortField, order: SortOrder, field: SortField) {
  if (sort !== field) {
    return <i className="fa-solid fa-sort" aria-hidden="true" />;
  }
  return <i className={`fa-solid fa-sort-${order === "asc" ? "up" : "down"}`} aria-hidden="true" />;
}
