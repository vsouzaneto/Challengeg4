import { useMemo, useState } from "react";
import { G4SectionIcon } from "./G4Mark";
import { displayLabel } from "../lib/labels";
import { formatMonthLabel, lastNMonthsRange } from "../lib/period";
import type { Bundle, FilterState } from "../types";

function asStrings(v: string[] | string | undefined): string[] {
  if (Array.isArray(v)) return v;
  return [];
}

type Props = {
  bundle: Bundle;
  state: FilterState;
  onChange: (s: FilterState) => void;
  onReset: () => void;
  onExport: () => void;
};

function activeCount(state: FilterState): number {
  let n = state.status_conta.length + state.industria.length + state.canal_aquisicao.length;
  n += state.plano_atual.length + state.faixa_risco.length;
  if (state.em_trial) n += 1;
  if (state.escalacao_acima) n += 1;
  if (state.periodo_inicio || state.periodo_fim) n += 1;
  return n;
}

function toggle(arr: string[], val: string): string[] {
  return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val];
}

function ChipGroup({
  label,
  options,
  selected,
  onToggle,
  onSetSelected,
}: {
  label: string;
  options: string[];
  selected: string[];
  onToggle: (v: string) => void;
  onSetSelected: (values: string[]) => void;
}) {
  const allSelected = options.length > 0 && options.every((o) => selected.includes(o));

  return (
    <div className="filter-group">
      <label>{label}</label>
      <div className="chips">
        <button
          type="button"
          className={`chip chip-select-all ${allSelected ? "active" : ""}`}
          onClick={() => onSetSelected(allSelected ? [] : [...options])}
        >
          Selecionar todos
        </button>
        {options.map((o) => (
          <button
            key={o}
            type="button"
            className={`chip ${selected.includes(o) ? "active" : ""}`}
            onClick={() => onToggle(o)}
          >
            {displayLabel(o)}
          </button>
        ))}
      </div>
    </div>
  );
}

export function FilterBar({ bundle, state, onChange, onReset, onExport }: Props) {
  const f = bundle.filtros_disponiveis;
  const set = (patch: Partial<FilterState>) => onChange({ ...state, ...patch });
  const [open, setOpen] = useState(true);
  const active = useMemo(() => activeCount(state), [state]);

  const months = asStrings(f.periodo_meses);
  const trialOptions = asStrings(f.em_trial).length ? asStrings(f.em_trial) : ["Sim", "Não"];
  const periodActive = Boolean(state.periodo_inicio || state.periodo_fim);

  return (
    <section className="filters-panel">
      <div className="filters-head">
        <div>
          <h3 className="section-title">
            <G4SectionIcon />
            Filtros globais
          </h3>
          <p className="hint">
            Um clique recalcula KPIs, gráficos e fila CS. Clique nos gráficos para filtrar também.
          </p>
        </div>
        <div className="filters-meta">
          {active > 0 && <span className="filter-badge">{active} ativos</span>}
          <button type="button" className="btn-ghost btn-compact" onClick={() => setOpen((v) => !v)}>
            {open ? "Recolher" : "Expandir"}
          </button>
        </div>
      </div>
      {!open && active > 0 && (
        <p className="filter-summary">
          Recorte personalizado. Expanda para ajustar status, indústria, canal, plano e risco.
        </p>
      )}
      {open && (
        <>
          <div className="filter-group">
            <label>Período (cadastro, churn ou último uso)</label>
            <div className="date-row">
              <select
                className="date-select"
                value={state.periodo_inicio}
                onChange={(e) => set({ periodo_inicio: e.target.value })}
                aria-label="Mês inicial"
              >
                <option value="">Início</option>
                {months.map((m) => (
                  <option key={`i-${m}`} value={m}>
                    {formatMonthLabel(m)}
                  </option>
                ))}
              </select>
              <span className="date-sep">até</span>
              <select
                className="date-select"
                value={state.periodo_fim}
                onChange={(e) => set({ periodo_fim: e.target.value })}
                aria-label="Mês final"
              >
                <option value="">Fim</option>
                {months.map((m) => (
                  <option key={`f-${m}`} value={m}>
                    {formatMonthLabel(m)}
                  </option>
                ))}
              </select>
            </div>
            <div className="chips">
              <button
                type="button"
                className={`chip chip-select-all ${!periodActive ? "active" : ""}`}
                onClick={() => set({ periodo_inicio: "", periodo_fim: "" })}
              >
                Todo o período
              </button>
              <button
                type="button"
                className="chip"
                onClick={() => {
                  const r = lastNMonthsRange(months, 6);
                  set({ periodo_inicio: r.inicio, periodo_fim: r.fim });
                }}
              >
                Últimos 6 meses
              </button>
              <button
                type="button"
                className="chip"
                onClick={() => {
                  const r = lastNMonthsRange(months, 12);
                  set({ periodo_inicio: r.inicio, periodo_fim: r.fim });
                }}
              >
                Últimos 12 meses
              </button>
            </div>
          </div>

          <ChipGroup
            label="Status"
            options={asStrings(f.status_conta)}
            selected={state.status_conta}
            onToggle={(v) => set({ status_conta: toggle(state.status_conta, v) })}
            onSetSelected={(values) => set({ status_conta: values })}
          />
          <ChipGroup
            label="Indústria"
            options={asStrings(f.industria)}
            selected={state.industria}
            onToggle={(v) => set({ industria: toggle(state.industria, v) })}
            onSetSelected={(values) => set({ industria: values })}
          />
          <ChipGroup
            label="Canal"
            options={asStrings(f.canal_aquisicao)}
            selected={state.canal_aquisicao}
            onToggle={(v) => set({ canal_aquisicao: toggle(state.canal_aquisicao, v) })}
            onSetSelected={(values) => set({ canal_aquisicao: values })}
          />
          <ChipGroup
            label="Plano"
            options={asStrings(f.plano_atual)}
            selected={state.plano_atual}
            onToggle={(v) => set({ plano_atual: toggle(state.plano_atual, v) })}
            onSetSelected={(values) => set({ plano_atual: values })}
          />
          <ChipGroup
            label="Faixa de risco"
            options={asStrings(f.faixa_risco)}
            selected={state.faixa_risco}
            onToggle={(v) => set({ faixa_risco: toggle(state.faixa_risco, v) })}
            onSetSelected={(values) => set({ faixa_risco: values })}
          />

          <div className="filter-group">
            <label>Trial</label>
            <div className="chips">
              <button
                type="button"
                className={`chip chip-select-all ${!state.em_trial ? "active" : ""}`}
                onClick={() => set({ em_trial: "" })}
              >
                Selecionar todos
              </button>
              {trialOptions.map((o) => (
                <button
                  key={o}
                  type="button"
                  className={`chip ${state.em_trial === o ? "active" : ""}`}
                  onClick={() => set({ em_trial: o })}
                >
                  {displayLabel(o)}
                </button>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <label>Escalação</label>
            <div className="chips">
              <button
                type="button"
                className={`chip chip-select-all ${!state.escalacao_acima ? "active" : ""}`}
                onClick={() => set({ escalacao_acima: false })}
              >
                Selecionar todos
              </button>
              <button
                type="button"
                className={`chip ${state.escalacao_acima ? "active" : ""}`}
                onClick={() => set({ escalacao_acima: true })}
              >
                Acima da mediana
              </button>
            </div>
          </div>

          <div className="filter-actions">
            <button type="button" className="btn-ghost" onClick={onReset}>
              Limpar filtros
            </button>
            <button type="button" className="btn-primary" onClick={onExport}>
              Exportar fila (CSV)
            </button>
          </div>
        </>
      )}
    </section>
  );
}
