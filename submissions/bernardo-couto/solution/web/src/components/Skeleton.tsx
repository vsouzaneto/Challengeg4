import { t } from '../i18n/pt-BR';

export function Skeleton({ className = '' }: { className?: string }) {
  return <div aria-hidden="true" className={`animate-pulse rounded bg-tier-Cbg ${className}`} />;
}

export function QueueSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div aria-busy="true" role="status">
      <span className="sr-only">{t.states.loading}</span>
      <div className="mb-6 grid gap-3 sm:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
    </div>
  );
}

export function BlockSkeleton({ className = 'h-40' }: { className?: string }) {
  return (
    <div aria-busy="true" role="status">
      <span className="sr-only">{t.states.loadingGeneric}</span>
      <Skeleton className={className} />
    </div>
  );
}
