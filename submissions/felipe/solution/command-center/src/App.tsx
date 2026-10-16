import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { FilterBar } from "./components/FilterBar";
import { G4SectionIcon } from "./components/G4Mark";
import { noDash } from "./lib/copy";
import { AccountDrawer } from "./components/AccountDrawer";
import { DataQualityCard } from "./components/DataQualityCard";
import { IndustryChurnChart, StatusChart, UsageTrendChart } from "./components/Charts";
import { applyFilters, patchMultiFilter, type MultiFilterKey } from "./lib/filters";
import { displayLabel } from "./lib/labels";
import type { Bundle, Conta, FilterState } from "./types";
import { emptyFilters } from "./types";

function fmtUsd(n: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

function tagClass(faixa: string | null | undefined) {
  if (!faixa) return "low";
  if (faixa.includes("Ligar")) return "high";
  if (faixa.includes("média")) return "mid";
  return "low";
}

export default function App() {
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [filters, setFilters] = useState<FilterState>(emptyFilters());
  const [error, setError] = useState<string | null>(null);
  const [drawerConta, setDrawerConta] = useState<Conta | null>(null);

  useEffect(() => {
    fetch("/data/bundle.json")
      .then((r) => {
        if (!r.ok) throw new Error("bundle.json ausente. Rode python run_analysis.py");
        return r.json();
      })
      .then((b: Bundle) => {
        setBundle(b);
        const params = new URLSearchParams(window.location.search);
        const id = params.get("conta");
        if (id) {
          const c = b.contas.find((x) => x.conta_id === id);
          if (c) setDrawerConta(c);
        }
      })
      .catch((e) => setError(String(e.message)));
  }, []);

  function openConta(c: Conta) {
    setDrawerConta(c);
    const url = new URL(window.location.href);
    url.searchParams.set("conta", c.conta_id);
    window.history.replaceState({}, "", url.toString());
  }

  function closeDrawer() {
    setDrawerConta(null);
    const url = new URL(window.location.href);
    url.searchParams.delete("conta");
    window.history.replaceState({}, "", url.toString());
  }

  const medEsc = bundle?.kpis_globais.mediana_taxa_escalacao ?? 0;

  const filtered = useMemo(() => {
    if (!bundle) return [];
    return applyFilters(bundle.contas, filters, medEsc);
  }, [bundle, filters, medEsc]);

  const kpis = useMemo(() => {
    const churn = filtered.filter((c) => c.churn_liquido).length;
    const revolving = filtered.filter((c) => c.status_conta === "Ativa (revolving)").length;
    const mrrRev = filtered
      .filter((c) => c.status_conta === "Ativa (revolving)")
      .reduce((s, c) => s + (c.mrr_usd || 0), 0);
    const mrrLost = filtered.filter((c) => c.churn_liquido).reduce((s, c) => s + (c.mrr_usd || 0), 0);
    const events = filtered.reduce((s, c) => s + (c.eventos_churn || 0), 0);
    return { churn, revolving, mrrRev, mrrLost, events, n: filtered.length };
  }, [filtered]);

  const queue = useMemo(
    () =>
      filtered
        .filter((c) => !c.churn_liquido && c.score_risco != null)
        .sort((a, b) => (b.prioridade_mrr ?? 0) - (a.prioridade_mrr ?? 0))
        .slice(0, 80),
    [filtered],
  );

  function pickFilter(key: MultiFilterKey, value: string) {
    setFilters((prev) => patchMultiFilter(prev, key, value));
  }

  function exportCsv() {
    if (!queue.length) return;
    const keys = Object.keys(queue[0]) as (keyof (typeof queue)[0])[];
    const lines = [keys.join(",")].concat(
      queue.map((r) => keys.map((k) => JSON.stringify(r[k] ?? "")).join(",")),
    );
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "fila_cs_filtrada.csv";
    a.click();
  }

  if (error) {
    return (
      <div className="app">
        <p style={{ color: "#ef4444" }}>{error}</p>
      </div>
    );
  }
  if (!bundle) {
    return <div className="app">Carregando intelligence...</div>;
  }

  return (
    <div className="app g4-shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">RavenStack · Challenge 001 · Felipe de Lima Santiago</p>
          <h1>{bundle.meta.produto.toUpperCase()}</h1>
          <p>Command Center executivo para diagnóstico de churn e fila CS.</p>
        </div>
        <div className="badge-count">{kpis.n} contas no recorte</div>
      </header>

      <section className="insight-card">
        <h2 className="section-title">
          <G4SectionIcon />
          {noDash(bundle.narrativa_executiva.headline)}
        </h2>
        <ul>
          {bundle.narrativa_executiva.bullets.map((b) => (
            <li key={b}>{noDash(b)}</li>
          ))}
        </ul>
      </section>

      {bundle.recomendacao_destaque && (
        <section className="reco-strip">
          <strong>Recomendação #1:</strong> {bundle.recomendacao_destaque.acao} — impacto MRR{" "}
          {fmtUsd(bundle.recomendacao_destaque.impacto_mrr_usd)} ({bundle.recomendacao_destaque.confianca})
        </section>
      )}

      <DataQualityCard data={bundle.qualidade_dados} />

      <FilterBar
        bundle={bundle}
        state={filters}
        onChange={setFilters}
        onReset={() => setFilters(emptyFilters())}
        onExport={exportCsv}
      />

      <section className="kpi-grid">
        <div className="kpi">
          <div className="label">Churn líquido</div>
          <div className="value">{kpis.churn}</div>
        </div>
        <div className="kpi">
          <div className="label">Revolving</div>
          <div className="value">{kpis.revolving}</div>
        </div>
        <div className="kpi">
          <div className="label">MRR revolving</div>
          <div className="value">{fmtUsd(kpis.mrrRev)}</div>
        </div>
        <div className="kpi">
          <div className="label">MRR perdido</div>
          <div className="value">{fmtUsd(kpis.mrrLost)}</div>
        </div>
        <div className="kpi">
          <div className="label">Eventos churn</div>
          <div className="value">{kpis.events}</div>
        </div>
        <div className="kpi" title="AUC hold-out 25% — triagem CS, não decisão automática. Ver reports/model_and_limits.md">
          <div className="label">AUC modelo</div>
          <div className="value">{bundle.kpis_globais.auc_modelo.toFixed(2)}</div>
        </div>
      </section>

      <section className="charts">
        <div className="chart-card">
          <h3 className="section-title">
            <G4SectionIcon />
            Composição do recorte
          </h3>
          <p className="chart-hint">Clique em um status para filtrar o painel.</p>
          <StatusChart rows={filtered} onPickStatus={(s) => pickFilter("status_conta", s)} />
        </div>
        <div className="chart-card">
          <h3 className="section-title">
            <G4SectionIcon />
            Churn líquido por indústria (%)
          </h3>
          <p className="chart-hint">Clique em uma barra para filtrar por indústria.</p>
          <IndustryChurnChart rows={filtered} onPickIndustry={(i) => pickFilter("industria", i)} />
        </div>
        <div className="chart-card wide">
          <h3 className="section-title">
            <G4SectionIcon />
            Tendência de uso (top indústrias do recorte)
          </h3>
          <p className="chart-hint">Clique na legenda ou no ponto da série para filtrar.</p>
          <UsageTrendChart
            bundle={bundle}
            industries={filters.industria}
            periodoInicio={filters.periodo_inicio}
            periodoFim={filters.periodo_fim}
            onPickIndustry={(i) => pickFilter("industria", i)}
          />
        </div>
      </section>

      <section className="table-section">
        <div className="table-head">
          <h3 className="section-title">
            <G4SectionIcon />
            Fila CS: prioridade MRR e risco
          </h3>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Conta</th>
                <th>Indústria</th>
                <th>MRR</th>
                <th>Score</th>
                <th>Faixa</th>
                <th>Motivo</th>
              </tr>
            </thead>
            <tbody>
              {queue.map((r) => (
                <tr key={r.conta_id} className="row-click" onClick={() => openConta(r)}>
                  <td>
                    <strong>{r.nome_conta}</strong>
                    <br />
                    <span style={{ color: "#737373", fontSize: "0.75rem" }}>{r.conta_id}</span>
                  </td>
                  <td>{displayLabel(r.industria)}</td>
                  <td>{fmtUsd(r.mrr_usd)}</td>
                  <td>{r.score_risco?.toFixed(1)}</td>
                  <td>
                    <span className={`tag ${tagClass(r.faixa_risco)}`}>{r.faixa_risco}</span>
                  </td>
                  <td style={{ maxWidth: 280 }}>{r.motivo_risco}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="foot">
        React + Recharts · Pipeline Python · Felipe de Lima Santiago
      </footer>

      <AccountDrawer
        conta={drawerConta}
        investigacao={
          drawerConta && bundle.investigacoes
            ? bundle.investigacoes[drawerConta.conta_id] ?? null
            : null
        }
        onClose={closeDrawer}
      />
    </div>
  );
}
