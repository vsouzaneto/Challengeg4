import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError, type FeedbackCreate } from './client';

export const keys = {
  health: ['health'] as const,
  meta: ['meta'] as const,
  regions: (asOf?: string) => ['regions', asOf] as const,
  managers: (asOf?: string) => ['managers', asOf] as const,
  agents: (asOf?: string) => ['agents', asOf] as const,
  deals: (q: DealsQuery) => ['deals', q] as const,
  deal: (id: string, asOf?: string) => ['deal', id, asOf] as const,
  summary: (q: SummaryQuery) => ['summary', q] as const,
  metrics: ['metrics'] as const,
};

export type DealsQuery = NonNullable<Parameters<typeof api.deals>[0]>;
export type SummaryQuery = NonNullable<Parameters<typeof api.pipelineSummary>[0]>;

/** Do not retry 4xx/503: the answer will not change without user action. */
export function retryPolicy(failureCount: number, error: unknown) {
  if (error instanceof ApiError && (error.status < 500 || error.status === 503)) return false;
  return failureCount < 1;
}

export const useHealth = () =>
  useQuery({ queryKey: keys.health, queryFn: api.health, retry: false, refetchInterval: 30_000 });

export const useMeta = () =>
  useQuery({ queryKey: keys.meta, queryFn: api.meta, retry: retryPolicy });

export const useRegions = (asOf?: string) =>
  useQuery({ queryKey: keys.regions(asOf), queryFn: () => api.regions(asOf), retry: retryPolicy });
export const useManagers = (asOf?: string) =>
  useQuery({
    queryKey: keys.managers(asOf),
    queryFn: () => api.managers(asOf),
    retry: retryPolicy,
  });
export const useAgents = (asOf?: string) =>
  useQuery({ queryKey: keys.agents(asOf), queryFn: () => api.agents(asOf), retry: retryPolicy });

export const useDeals = (q: DealsQuery, enabled = true) =>
  useQuery({
    queryKey: keys.deals(q),
    queryFn: () => api.deals(q),
    enabled,
    retry: retryPolicy,
    placeholderData: (prev) => prev,
  });

export const useDeal = (id: string | null, asOf?: string) =>
  useQuery({
    queryKey: keys.deal(id ?? '', asOf),
    queryFn: () => api.deal(id!, asOf),
    enabled: !!id,
    retry: retryPolicy,
  });

export const usePipelineSummary = (q: SummaryQuery, enabled = true) =>
  useQuery({
    queryKey: keys.summary(q),
    queryFn: () => api.pipelineSummary(q),
    enabled,
    retry: retryPolicy,
    placeholderData: (prev) => prev,
  });

export const useModelMetrics = () =>
  useQuery({ queryKey: keys.metrics, queryFn: api.modelMetrics, retry: retryPolicy });

export function useCreateFeedback(asOf?: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: FeedbackCreate) => api.createFeedback(body, asOf),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['feedback'] }),
  });
}
