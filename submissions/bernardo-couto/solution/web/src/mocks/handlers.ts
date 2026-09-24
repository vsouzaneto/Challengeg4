// MSW handlers shared by Vitest (node) and `npm run dev:mock` (browser).
// Filtering/sorting/paging here imitates the API — it is mock behaviour, not client logic.
import { HttpResponse, http } from 'msw';
import type { ErrorResponse, FeedbackCreate, FeedbackRecord, ScoredDeal } from '../api/client';
import {
  AS_OF,
  DEALS,
  META,
  METRICS,
  MODEL_VERSION,
  agents,
  managers,
  pipelineSummary,
  regions,
} from './fixtures';

export type Scenario = 'ok' | 'missing' | 'error' | 'empty';

const DATA_HEADERS = { 'X-As-Of': AS_OF, 'X-Model-Version': MODEL_VERSION };

export const artifactsMissing: ErrorResponse = {
  error: {
    code: 'ARTIFACTS_MISSING',
    message: 'Nenhum score encontrado em data/gold/scores.',
    hint: 'Rode `make pipeline` em solution/ (JDK 17/21).',
  },
};
export const modelMissing: ErrorResponse = {
  error: {
    code: 'MODEL_ARTIFACTS_MISSING',
    message: 'models/latest/metrics.json não encontrado.',
    hint: 'Rode `make pipeline` em solution/ (JDK 17/21).',
  },
};

function filterDeals(url: URL): ScoredDeal[] {
  const q = (k: string) => url.searchParams.get(k);
  let ds = DEALS.filter(
    (d) =>
      (!q('sales_agent') || d.sales_agent === q('sales_agent')) &&
      (!q('manager') || d.manager === q('manager')) &&
      (!q('regional_office') || d.regional_office === q('regional_office')) &&
      (!q('deal_stage') || d.deal_stage === q('deal_stage')) &&
      (!q('tier') || d.tier === q('tier')) &&
      (q('account_known') === null || (q('account_known') === 'true') === (d.account !== null)) &&
      (q('queue') !== 'work' || (d.days_in_engaging ?? 0) <= 138) &&
      (q('queue') !== 'confirm' || (d.days_in_engaging ?? 0) > 138) &&
      (q('min_days_in_engaging') === null ||
        (d.days_in_engaging != null && d.days_in_engaging >= Number(q('min_days_in_engaging')))) &&
      (q('max_days_in_engaging') === null ||
        (d.days_in_engaging != null && d.days_in_engaging <= Number(q('max_days_in_engaging')))),
  );
  const sort = (q('sort') ?? '-priority_score').split(',');
  ds = [...ds].sort((a, b) => {
    for (const s of sort) {
      const desc = s.startsWith('-');
      const key = s.replace(/^-/, '') as keyof ScoredDeal;
      const av = (a[key] as number | null) ?? -1;
      const bv = (b[key] as number | null) ?? -1;
      if (av !== bv)
        return desc ? (bv as number) - (av as number) : (av as number) - (bv as number);
    }
    return 0;
  });
  return ds;
}

export function buildHandlers(scenario: () => Scenario = () => 'ok') {
  const guard = () => {
    const s = scenario();
    if (s === 'missing') return HttpResponse.json(artifactsMissing, { status: 503 });
    if (s === 'error')
      return HttpResponse.json({ error: { code: 'INTERNAL', message: 'boom' } }, { status: 500 });
    return null;
  };

  return [
    http.get('*/api/v1/health', () => HttpResponse.json({ status: 'ok', version: '1.0.0' })),
    http.get('*/api/v1/meta', () =>
      HttpResponse.json(
        scenario() === 'missing'
          ? {
              ...META,
              artifacts_present: false,
              as_of_available: [],
              default_as_of: null,
              model_version: null,
              open_deals: null,
            }
          : META,
      ),
    ),
    http.get(
      '*/api/v1/regions',
      () => guard() ?? HttpResponse.json(regions(), { headers: DATA_HEADERS }),
    ),
    http.get(
      '*/api/v1/managers',
      () => guard() ?? HttpResponse.json(managers(), { headers: DATA_HEADERS }),
    ),
    http.get(
      '*/api/v1/agents',
      () => guard() ?? HttpResponse.json(agents(), { headers: DATA_HEADERS }),
    ),
    http.get('*/api/v1/deals', ({ request }) => {
      const blocked = guard();
      if (blocked) return blocked;
      const url = new URL(request.url);
      const ds = scenario() === 'empty' ? [] : filterDeals(url);
      const limit = Number(url.searchParams.get('limit') ?? 50);
      const offset = Number(url.searchParams.get('offset') ?? 0);
      return HttpResponse.json(
        {
          items: ds.slice(offset, offset + limit),
          total: ds.length,
          limit,
          offset,
          sort: url.searchParams.get('sort') ?? '-priority_score',
          as_of: url.searchParams.get('as_of') ?? AS_OF,
          model_version: MODEL_VERSION,
        },
        { headers: DATA_HEADERS },
      );
    }),
    http.get('*/api/v1/deals/:id', ({ params }) => {
      const blocked = guard();
      if (blocked) return blocked;
      const deal = DEALS.find((d) => d.opportunity_id === params.id);
      return deal
        ? HttpResponse.json(deal, { headers: DATA_HEADERS })
        : HttpResponse.json(
            {
              error: {
                code: 'DEAL_NOT_FOUND',
                message: `Deal ${String(params.id)} não encontrado.`,
              },
            },
            { status: 404 },
          );
    }),
    http.get('*/api/v1/pipeline/summary', ({ request }) => {
      const blocked = guard();
      if (blocked) return blocked;
      const url = new URL(request.url);
      const groupBy = (url.searchParams.get('group_by') ?? 'manager') as
        'sales_agent' | 'manager' | 'regional_office';
      return HttpResponse.json(pipelineSummary(groupBy, filterDeals(url)), {
        headers: DATA_HEADERS,
      });
    }),
    http.get('*/api/v1/model/metrics', () => {
      const s = scenario();
      if (s === 'missing') return HttpResponse.json(modelMissing, { status: 503 });
      if (s === 'error')
        return HttpResponse.json({ error: { code: 'INTERNAL', message: 'boom' } }, { status: 500 });
      return HttpResponse.json(METRICS, { headers: DATA_HEADERS });
    }),
    http.post('*/api/v1/feedback', async ({ request }) => {
      const blocked = guard();
      if (blocked) return blocked;
      const body = (await request.json()) as FeedbackCreate;
      const deal = DEALS.find((d) => d.opportunity_id === body.opportunity_id);
      const record: FeedbackRecord = {
        ...body,
        note: body.note ?? null,
        id: Math.random().toString(16).slice(2).padEnd(32, '0'),
        recorded_at: new Date().toISOString(),
        as_of: AS_OF,
        model_version: MODEL_VERSION,
        priority_score: deal?.priority_score ?? 0,
      };
      return HttpResponse.json(record, { status: 201, headers: DATA_HEADERS });
    }),
    http.get('*/api/v1/feedback', () => HttpResponse.json([])),
  ];
}

export const handlers = buildHandlers();
