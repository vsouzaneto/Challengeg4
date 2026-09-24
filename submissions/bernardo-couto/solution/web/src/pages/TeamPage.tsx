import { Link } from 'react-router-dom';
import type { PipelineGroup, ScoredDeal } from '../api/client';
import { useDeals, useMeta, usePipelineSummary } from '../api/queries';
import { DealDrawer } from '../components/DealDrawer';
import { MainReason } from '../components/ReasonLine';
import { mainReason } from '../lib/reasons';
import { BlockSkeleton } from '../components/Skeleton';
import { StackedBar } from '../components/StackedBar';
import { QueryError } from '../components/States';
import { Tile } from '../components/Tile';
import { t } from '../i18n/pt-BR';
import { fmtBRL, fmtBRLCompact, fmtDate, fmtInt, fmtPct, median } from '../lib/format';
import { useUrlState, writeState, type UrlState } from '../lib/urlState';

type GroupBy = 'sales_agent' | 'manager' | 'regional_office';

function groupByFor(s: UrlState): GroupBy {
  if (s.agent || s.manager) return 'sales_agent';
  if (s.region) return 'manager';
  return 'manager';
}

/** Link to the seller queue for a group row, keeping as_of and the parent filters. */
function queueLink(s: UrlState, groupBy: GroupBy, key: string, extra?: Partial<UrlState>) {
  const next: UrlState = { ...s, offset: 0, deal: undefined, ...extra };
  if (groupBy === 'sales_agent') next.agent = key;
  if (groupBy === 'manager') {
    next.manager = key;
    next.agent = undefined;
  }
  if (groupBy === 'regional_office') {
    next.region = key;
    next.manager = undefined;
    next.agent = undefined;
  }
  return `/?${writeState(next).toString()}`;
}

export function TeamPage() {
  const { state, update } = useUrlState();
  const meta = useMeta();
  const groupBy = groupByFor(state);
  const ready = !!state.asOf || meta.isFetched;
  const summary = usePipelineSummary(
    {
      group_by: groupBy,
      as_of: state.asOf,
      regional_office: state.region,
      manager: state.manager,
      sales_agent: state.agent,
    },
    ready,
  );
  const zombies = useDeals(
    {
      as_of: state.asOf,
      regional_office: state.region,
      manager: state.manager,
      sales_agent: state.agent,
      queue: 'confirm',
      sort: '-expected_value,days_in_engaging',
      limit: 10,
    },
    ready,
  );

  const data = summary.data;
  const groups = data ? [...data.groups].sort((a, b) => b.zombie_value - a.zombie_value) : [];
  const med = median(groups.map((g) => g.open_deals));
  const threshold = data?.zombie_threshold_days ?? 138;
  const zombieList: ScoredDeal[] = zombies.data?.items ?? [];

  const title = state.manager
    ? t.team.title(state.manager)
    : state.region
      ? t.team.titleRegion(state.region)
      : t.team.titleAll;
  const colLabel =
    groupBy === 'sales_agent'
      ? t.team.columns.agent
      : groupBy === 'manager'
        ? t.team.columns.manager
        : t.team.columns.region;
  const sectionTitle =
    groupBy === 'sales_agent'
      ? t.team.byAgent
      : groupBy === 'manager'
        ? t.team.byManager
        : t.team.byRegion;
  const asOfLabel = fmtDate(data?.as_of ?? state.asOf ?? meta.data?.default_as_of);
  const daysLink = queueLink(state, groupBy, '', { queue: 'confirm' });
  const coolingLink = queueLink(state, groupBy, '', { sort: 'days' });
  const selected = state.deal;

  return (
    <div>
      <h1 className="font-serif text-2xl font-bold">{title}</h1>
      {data && (
        <p className="mt-1 text-sm text-g4-muted">
          {t.team.subtitleGroups(
            data.groups.length,
            t.team.groupLabel[groupBy],
            data.total.open_deals,
            asOfLabel,
          )}
        </p>
      )}

      {summary.isError && !data && (
        <div className="mt-6">
          <QueryError
            error={summary.error}
            onRetry={() => summary.refetch()}
            title={t.states.apiErrorTitleGeneric}
          />
        </div>
      )}
      {summary.isPending && !summary.isError && (
        <div className="mt-6 space-y-6">
          <BlockSkeleton className="h-28" />
          <BlockSkeleton className="h-64" />
        </div>
      )}

      {data && (
        <>
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Tile value={fmtBRLCompact(data.total.expected_value)} label={t.team.tiles.expected} />
            <Tile
              value={fmtInt(data.total.cooling_count)}
              label={t.team.tiles.cooling}
              hint={t.team.tiles.coolingValue(fmtBRLCompact(data.total.cooling_value))}
              to={coolingLink}
              linkLabel={t.team.tiles.seeDeals}
            />
            <Tile
              value={
                data.total.nominal_zombie_value != null
                  ? fmtBRLCompact(data.total.nominal_zombie_value)
                  : '—'
              }
              label={t.team.tiles.atRisk}
              hint={t.team.tiles.zombiesHint(threshold)}
              to={daysLink}
              linkLabel={t.team.tiles.seeDeals}
            />
            <Tile
              value={fmtInt(data.total.zombie_count)}
              label={t.team.tiles.zombies}
              hint={t.team.tiles.zombiesHint(threshold)}
              to={daysLink}
              linkLabel={t.team.tiles.seeDeals}
            />
            <Tile
              value={`${fmtPct(data.total.account_coverage)} %`}
              label={t.team.tiles
                .coverage(Number(fmtPct(data.total.account_coverage)))
                .replace(/^\d+\s%\s/, '')}
            />
          </div>

          <section className="card mt-6 p-4">
            <StackedBar distribution={data.total.tier_distribution} />
          </section>

          <section aria-labelledby="by-group" className="card mt-6 overflow-x-auto p-4">
            <h2 id="by-group" className="text-xl font-semibold">
              {sectionTitle}
            </h2>
            <table className="mt-3 w-full text-sm tabular-nums">
              <caption className="sr-only">{t.team.caption(sectionTitle)}</caption>
              <thead>
                <tr className="text-left text-xs font-semibold text-g4-muted">
                  <th scope="col" className="py-2 pr-3">
                    {colLabel}
                  </th>
                  <th scope="col" className="py-2 pr-3 text-right">
                    {t.team.columns.open}
                  </th>
                  <th scope="col" className="py-2 pr-3 text-right">
                    {t.team.columns.tierA}
                  </th>
                  <th scope="col" className="py-2 pr-3 text-right">
                    {t.team.columns.expected}
                  </th>
                  <th scope="col" className="py-2 pr-3 text-right">
                    {t.team.columns.atRisk}
                  </th>
                  <th scope="col" className="py-2 pr-3 text-right">
                    {t.team.columns.zombies}
                  </th>
                  <th scope="col" className="py-2 pr-3 text-right">
                    {t.team.columns.accountKnown}
                  </th>
                  <th scope="col" className="py-2 text-right">
                    {t.team.columns.load}
                  </th>
                </tr>
              </thead>
              <tbody>
                {groups.map((g, i) => (
                  <GroupRow
                    key={g.key}
                    group={g}
                    median={med}
                    zebra={i % 2 === 1}
                    to={queueLink(state, groupBy, g.key)}
                  />
                ))}
              </tbody>
            </table>
          </section>

          <section aria-labelledby="zombies" className="mt-6">
            <h2 id="zombies" className="text-xl font-semibold">
              {t.team.zombiesTitle}
            </h2>
            {zombies.isPending && <BlockSkeleton className="mt-3 h-24" />}
            {zombies.data && zombieList.length === 0 && (
              <p className="mt-3 text-sm text-g4-muted">{t.team.zombiesEmpty}</p>
            )}
            {zombieList.length > 0 && (
              <ol aria-label={t.team.zombiesTitle} className="mt-3 space-y-2">
                {zombieList.map((d) => (
                  <li key={d.opportunity_id}>
                    <article className="card flex flex-wrap items-center gap-3 p-3 text-sm">
                      <button
                        type="button"
                        className="rounded font-semibold"
                        aria-label={t.deal.openDetail(
                          d.account ?? t.deal.accountUnknown,
                          d.product,
                        )}
                        onClick={() => update({ deal: d.opportunity_id })}
                      >
                        {d.account ?? (
                          <span className="italic text-g4-muted">{t.deal.accountUnknown}</span>
                        )}{' '}
                        · {d.product}
                      </button>
                      <span className="text-g4-muted">{d.sales_agent}</span>
                      <span className="tabular-nums text-g4-risk">
                        <span aria-hidden="true">⏳ </span>
                        {t.deal.days(d.days_in_engaging ?? 0)}
                      </span>
                      <span className="tabular-nums font-semibold">
                        {d.sales_price != null ? fmtBRL(d.sales_price) : fmtBRL(d.expected_value)}{' '}
                        <span className="text-xs font-medium text-g4-muted">
                          {d.sales_price != null ? t.deal.nominalOutOfForecast : t.deal.expected}
                        </span>
                      </span>
                      <span className="min-w-0 flex-1">
                        {mainReason(d) && <MainReason reason={mainReason(d)!} />}
                      </span>
                    </article>
                  </li>
                ))}
              </ol>
            )}
          </section>

          <p className="mt-6 text-xs font-medium text-g4-muted">{t.team.definitions}</p>
        </>
      )}

      {selected && (
        <DealDrawer
          dealId={selected}
          asOf={state.asOf}
          initial={zombieList.find((d) => d.opportunity_id === selected)}
          onClose={() => update({ deal: undefined })}
          returnFocus={() => document.getElementById('zombies')}
        />
      )}
    </div>
  );
}

function LoadIcon({ n, median: med }: { n: number; median: number }) {
  const ratio = med ? n / med : 1;
  const dots = ratio > 1.2 ? 4 : ratio > 1 ? 3 : ratio >= 0.8 ? 2 : 1;
  return (
    <span
      role="img"
      aria-label={t.team.load(n, med)}
      title={t.team.load(n, med)}
      className="tabular-nums tracking-wider"
    >
      <span aria-hidden="true">
        {'●'.repeat(dots)}
        {'○'.repeat(4 - dots)}
      </span>
    </span>
  );
}

function GroupRow({
  group,
  median: med,
  zebra,
  to,
}: {
  group: PipelineGroup;
  median: number;
  zebra: boolean;
  to: string;
}) {
  return (
    <tr
      className={`h-11 border-t border-g4line hover:bg-g4-rowHover ${zebra ? 'bg-g4-surface' : ''}`}
    >
      <th scope="row" className="py-2 pr-3 text-left font-semibold">
        <Link
          to={to}
          className="rounded underline decoration-1 underline-offset-2 text-g4-navy700"
          aria-label={t.team.rowLink(group.key)}
        >
          {group.key}
        </Link>
      </th>
      <td className="py-2 pr-3 text-right">{fmtInt(group.open_deals)}</td>
      <td className="py-2 pr-3 text-right">{fmtInt(group.tier_distribution.A)}</td>
      <td className="py-2 pr-3 text-right">{fmtBRLCompact(group.expected_value)}</td>
      <td className="py-2 pr-3 text-right">
        {group.nominal_zombie_value != null ? fmtBRLCompact(group.nominal_zombie_value) : '—'}
      </td>
      <td className="py-2 pr-3 text-right">{fmtInt(group.zombie_count)}</td>
      <td className="py-2 pr-3 text-right">{fmtPct(group.account_coverage)} %</td>
      <td className="py-2 text-right">
        <LoadIcon n={group.open_deals} median={med} />
      </td>
    </tr>
  );
}
