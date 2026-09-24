// Typed client over the generated OpenAPI schema (src/api/schema.d.ts, `npm run gen:api`).
// The web never computes scores: it only reads what the API serves.
import createClient, { type Middleware } from 'openapi-fetch';
import type { components, paths } from './schema';

export type ScoredDeal = components['schemas']['ScoredDeal'];
export type Reason = components['schemas']['Reason'];
export type DealsPage = components['schemas']['DealsPage'];
export type MetaResponse = components['schemas']['MetaResponse'];
export type HealthResponse = components['schemas']['HealthResponse'];
export type AgentSummary = components['schemas']['AgentSummary'];
export type ManagerSummary = components['schemas']['ManagerSummary'];
export type RegionSummary = components['schemas']['RegionSummary'];
export type PipelineSummary = components['schemas']['PipelineSummary'];
export type PipelineGroup = components['schemas']['PipelineGroup'];
export type ModelMetricsResponse = components['schemas']['ModelMetricsResponse'];
export type FeedbackCreate = components['schemas']['FeedbackCreate'];
export type FeedbackRecord = components['schemas']['FeedbackRecord'];
export type FeedbackAction = components['schemas']['FeedbackAction'];
export type ErrorResponse = components['schemas']['ErrorResponse'];
export type Tier = ScoredDeal['tier'];
export type Confidence = ScoredDeal['confidence'];
export type Direction = Reason['direction'];

// Schema paths already include `/api/v1`; VITE_API_BASE may point at another origin.
export const API_BASE = import.meta.env.VITE_API_BASE ?? '';

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly code?: string,
    public readonly hint?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
  get artifactsMissing() {
    return this.status === 503;
  }
}

/** Last `X-As-Of` / `X-Model-Version` headers seen on a data response. */
export const responseMeta: { asOf?: string; modelVersion?: string } = {};

const headersMiddleware: Middleware = {
  async onResponse({ response }) {
    const asOf = response.headers.get('X-As-Of');
    const model = response.headers.get('X-Model-Version');
    if (asOf) responseMeta.asOf = asOf;
    if (model) responseMeta.modelVersion = model;
    return response;
  },
};

// Node's fetch (tests) rejects relative URLs; in the browser the origin is the same anyway.
const baseUrl = API_BASE || (typeof window !== 'undefined' ? window.location.origin : '');
export const client = createClient<paths>({
  baseUrl,
  // Resolve fetch lazily so test interceptors installed after import (MSW) are honoured.
  fetch: (input) => globalThis.fetch(input),
});
client.use(headersMiddleware);

type Envelope<T> = { data?: T; error?: unknown; response: Response };

/** Unwrap an openapi-fetch result, converting the API error envelope into ApiError. */
export function unwrap<T>({ data, error, response }: Envelope<T>): T {
  if (error !== undefined || !response.ok) {
    const body = (error ?? {}) as Partial<ErrorResponse>;
    const detail = body.error;
    throw new ApiError(
      response.status,
      detail?.message ?? `${response.status} ${response.statusText}`,
      detail?.code,
      detail?.hint ?? undefined,
    );
  }
  if (data === undefined) throw new ApiError(response.status, 'Empty response');
  return data;
}

export const api = {
  health: async () => unwrap(await client.GET('/api/v1/health')),
  meta: async () => unwrap(await client.GET('/api/v1/meta')),
  regions: async (as_of?: string) =>
    unwrap(await client.GET('/api/v1/regions', { params: { query: { as_of } } })),
  managers: async (as_of?: string) =>
    unwrap(await client.GET('/api/v1/managers', { params: { query: { as_of } } })),
  agents: async (as_of?: string) =>
    unwrap(await client.GET('/api/v1/agents', { params: { query: { as_of } } })),
  deals: async (query: paths['/api/v1/deals']['get']['parameters']['query']) =>
    unwrap(await client.GET('/api/v1/deals', { params: { query } })),
  deal: async (opportunity_id: string, as_of?: string) =>
    unwrap(
      await client.GET('/api/v1/deals/{opportunity_id}', {
        params: { path: { opportunity_id }, query: { as_of } },
      }),
    ),
  pipelineSummary: async (query: paths['/api/v1/pipeline/summary']['get']['parameters']['query']) =>
    unwrap(await client.GET('/api/v1/pipeline/summary', { params: { query } })),
  modelMetrics: async () => unwrap(await client.GET('/api/v1/model/metrics')),
  createFeedback: async (body: FeedbackCreate, as_of?: string) =>
    unwrap(await client.POST('/api/v1/feedback', { body, params: { query: { as_of } } })),
};
