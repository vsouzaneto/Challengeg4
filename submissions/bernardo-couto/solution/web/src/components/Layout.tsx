import { useState, type ReactNode } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import type { AgentSummary, ManagerSummary, MetaResponse, RegionSummary } from '../api/client';
import { useAgents, useHealth, useManagers, useMeta, useRegions } from '../api/queries';
import { t } from '../i18n/pt-BR';
import { fmtDate } from '../lib/format';
import { activeFilterCount, useUrlState, type UrlState } from '../lib/urlState';
import { Dialog } from './Dialog';

export function Layout({ mockBanner }: { mockBanner?: boolean }) {
  const { state, update, clearFilters, search } = useUrlState();
  const meta = useMeta();
  const regions = useRegions(state.asOf);
  const managers = useManagers(state.asOf);
  const agents = useAgents(state.asOf);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const count = activeFilterCount(state);
  const q = search ? `?${search}` : '';

  const sidebar = (
    <SidebarContent
      state={state}
      update={update}
      clearFilters={clearFilters}
      meta={meta.data}
      regions={regions.data ?? []}
      managers={managers.data ?? []}
      agents={agents.data ?? []}
    />
  );

  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-white focus:px-3 focus:py-2 focus:text-sm focus:font-semibold"
      >
        {t.queue.skipLink}
      </a>
      <header className="bg-g4-primary text-white">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <p className="font-serif text-xl font-bold tracking-tight">{t.brand}</p>
          <nav aria-label={t.a11y.sections} className="flex gap-1 text-sm font-semibold">
            {(
              [
                ['/', t.nav.queue],
                ['/time', t.nav.team],
                ['/qualidade', t.nav.quality],
              ] as const
            ).map(([to, label]) => (
              <NavLink
                key={to}
                to={{ pathname: to, search: q }}
                end={to === '/'}
                className={({ isActive }) =>
                  `rounded px-3 py-2 hover:bg-g4-navy700 ${isActive ? 'bg-g4-navy700 underline decoration-2 underline-offset-4' : ''}`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
          <StatusPill />
        </div>
      </header>
      {mockBanner && (
        <p
          role="status"
          className="bg-g4-highlight px-4 py-1 text-center text-xs font-semibold text-g4-primary"
        >
          {t.states.mockBanner}
        </p>
      )}

      <div className="mx-auto flex w-full max-w-[1400px] flex-1 gap-6 px-4 py-6 sm:px-6">
        <aside aria-label={t.a11y.sidebar} className="hidden w-sidebar shrink-0 lg:block">
          {sidebar}
        </aside>
        <main id="main" className="min-w-0 flex-1" tabIndex={-1}>
          <div className="mb-4 lg:hidden">
            <button type="button" className="btn-secondary" onClick={() => setFiltersOpen(true)}>
              {t.filters.open(count)}
            </button>
          </div>
          <div className="mx-auto max-w-content">
            <Outlet />
          </div>
        </main>
      </div>

      <footer className="border-t border-g4line px-4 py-3 text-center text-xs font-medium text-g4-muted">
        <FooterText meta={meta.data} asOf={state.asOf} />
      </footer>

      {filtersOpen && (
        <Dialog
          labelledBy="filters-title"
          onClose={() => setFiltersOpen(false)}
          side="left"
          className="w-80 p-4"
        >
          <div className="mb-2 flex items-center justify-between">
            <h2 id="filters-title" className="text-xl font-semibold">
              {t.filters.title}
            </h2>
            <button
              type="button"
              className="btn-secondary h-10 w-10 px-0 text-xl"
              aria-label={t.filters.close}
              onClick={() => setFiltersOpen(false)}
            >
              <span aria-hidden="true">×</span>
            </button>
          </div>
          {sidebar}
        </Dialog>
      )}
    </div>
  );
}

function FooterText({ meta, asOf }: { meta?: MetaResponse; asOf?: string }) {
  const model = meta?.model_version ?? '—';
  const dataUntil = fmtDate(meta?.snapshot_date ?? asOf);
  const ref = asOf ?? meta?.default_as_of ?? undefined;
  return (
    <>
      {t.reference.footer(dataUntil, model)}
      {ref ? ` · ${t.reference.footerAsOf(fmtDate(ref))}` : ''}
    </>
  );
}

function StatusPill() {
  const health = useHealth();
  if (health.isPending) {
    return (
      <span role="status" aria-label={t.a11y.apiStatus} className="text-sm text-white/80">
        {t.status.checking}
      </span>
    );
  }
  if (health.isSuccess) {
    return (
      <span
        role="status"
        aria-label={t.a11y.apiStatus}
        className="whitespace-nowrap rounded bg-g4-secondary px-3 py-1 text-xs font-semibold text-g4-primary"
      >
        {t.status.online} · v{health.data.version}
      </span>
    );
  }
  return (
    <span role="alert" className="rounded bg-g4-risk px-3 py-1 text-xs font-semibold text-white">
      {t.status.offline}
    </span>
  );
}

interface SidebarProps {
  state: UrlState;
  update: (patch: Partial<UrlState>) => void;
  clearFilters: () => void;
  meta?: MetaResponse;
  regions: RegionSummary[];
  managers: ManagerSummary[];
  agents: AgentSummary[];
}

function SidebarContent({
  state,
  update,
  clearFilters,
  meta,
  regions,
  managers,
  agents,
}: SidebarProps) {
  const managerOptions = managers.filter(
    (m) => !state.region || m.regional_office === state.region,
  );
  const agentOptions = agents.filter(
    (a) =>
      (!state.region || a.regional_office === state.region) &&
      (!state.manager || a.manager === state.manager),
  );
  const chips: { label: string; onRemove: () => void }[] = [];
  if (state.region)
    chips.push({ label: state.region, onRemove: () => update({ region: undefined }) });
  if (state.manager)
    chips.push({ label: state.manager, onRemove: () => update({ manager: undefined }) });
  if (state.agent) chips.push({ label: state.agent, onRemove: () => update({ agent: undefined }) });
  const asOfOptions = meta?.as_of_available ?? [];
  const asOfValue = state.asOf ?? meta?.default_as_of ?? '';

  return (
    <div className="space-y-6">
      <section aria-labelledby="filters-heading" className="card p-4">
        <h2
          id="filters-heading"
          className="text-sm font-semibold uppercase tracking-wide text-g4-muted"
        >
          {t.filters.title}
        </h2>
        <Field label={t.filters.region} id="f-region">
          <select
            id="f-region"
            className="select"
            value={state.region ?? ''}
            onChange={(e) => update({ region: e.target.value || undefined })}
          >
            <option value="">{t.filters.allFeminine}</option>
            {regions.map((r) => (
              <option key={r.regional_office} value={r.regional_office}>
                {r.regional_office}
              </option>
            ))}
          </select>
        </Field>
        <Field label={t.filters.manager} id="f-manager">
          <select
            id="f-manager"
            className="select"
            value={state.manager ?? ''}
            onChange={(e) => update({ manager: e.target.value || undefined })}
          >
            <option value="">{t.filters.all}</option>
            {managerOptions.map((m) => (
              <option key={m.manager} value={m.manager}>
                {m.manager}
              </option>
            ))}
          </select>
        </Field>
        <Field label={t.filters.agent} id="f-agent">
          <select
            id="f-agent"
            className="select"
            value={state.agent ?? ''}
            onChange={(e) => update({ agent: e.target.value || undefined })}
          >
            <option value="">{t.filters.all}</option>
            {agentOptions.map((a) => (
              <option key={a.sales_agent} value={a.sales_agent}>
                {a.sales_agent}
              </option>
            ))}
          </select>
        </Field>
        {chips.length > 0 && (
          <ul className="mt-3 flex flex-wrap gap-2" aria-label={t.filters.title}>
            {chips.map((c) => (
              <li key={c.label}>
                <span className="inline-flex items-center gap-1 rounded-full bg-g4-tintNavy px-3 py-1 text-xs font-semibold text-g4-primary">
                  {c.label}
                  <button
                    type="button"
                    className="-mr-1 flex h-6 w-6 items-center justify-center rounded-full hover:bg-white"
                    aria-label={t.filters.removeChip(c.label)}
                    onClick={c.onRemove}
                  >
                    <span aria-hidden="true">×</span>
                  </button>
                </span>
              </li>
            ))}
          </ul>
        )}
        <button
          type="button"
          className="btn-secondary mt-4 w-full"
          onClick={clearFilters}
          disabled={chips.length === 0}
        >
          {t.filters.clear}
        </button>
      </section>

      <section aria-labelledby="reference-heading" className="card p-4">
        <h2
          id="reference-heading"
          className="text-sm font-semibold uppercase tracking-wide text-g4-muted"
        >
          {t.reference.title}
        </h2>
        <Field label={t.reference.asOf} id="f-asof">
          <select
            id="f-asof"
            className="select"
            value={asOfValue}
            disabled={asOfOptions.length <= 1}
            onChange={(e) => update({ asOf: e.target.value || undefined })}
          >
            {asOfOptions.length === 0 && <option value="">—</option>}
            {asOfOptions.map((d) => (
              <option key={d} value={d}>
                {fmtDate(d)}
              </option>
            ))}
          </select>
        </Field>
        <dl className="mt-3 text-xs font-medium text-g4-muted">
          <div className="flex justify-between gap-2">
            <dt>{t.reference.model}</dt>
            <dd className="text-right text-g4-text">{meta?.model_version ?? '—'}</dd>
          </div>
        </dl>
        <p className="mt-3 text-xs font-medium text-g4-muted">
          <span aria-hidden="true">ⓘ </span>
          {t.reference.note}
        </p>
      </section>
    </div>
  );
}

function Field({ label, id, children }: { label: string; id: string; children: ReactNode }) {
  return (
    <div className="mt-3">
      <label htmlFor={id} className="mb-1 block text-xs font-semibold text-g4-muted">
        {label}
      </label>
      {children}
    </div>
  );
}
