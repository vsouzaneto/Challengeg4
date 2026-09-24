import { useEffect, useRef, useState } from 'react';
import { ApiError } from '../api/client';
import { t } from '../i18n/pt-BR';

export function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <>
      <button
        type="button"
        className="btn-action h-8 px-3 text-xs"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          } catch {
            /* clipboard unavailable: nothing to do */
          }
        }}
      >
        {t.states.copy}
      </button>
      <span role="status" aria-live="polite" className="ml-2 text-xs font-medium text-g4-secondary">
        {copied ? t.states.copied : ''}
      </span>
    </>
  );
}

/** 503 / artifacts missing (ux-spec §7): navy card with the exact command, copyable. */
export function ArtifactsMissing({
  title = t.states.artifactsTitle,
  body = t.states.artifactsBody,
}: {
  title?: string;
  body?: string;
}) {
  return (
    <div role="status" className="rounded-lg bg-g4-primary p-6 text-white shadow-card">
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="mt-2 text-sm text-white/90">{body}</p>
      <pre className="mt-4 overflow-x-auto rounded bg-g4-navy700 p-3 text-sm">
        <code>{t.states.artifactsCmd}</code>
      </pre>
      <CopyButton text={t.states.artifactsCmd} />
      <p className="mt-4 text-xs font-medium text-white/80">{t.states.artifactsAlt}</p>
      <pre className="mt-1 overflow-x-auto rounded bg-g4-navy700 p-3 text-sm">
        <code>{t.states.artifactsCmdDocker}</code>
      </pre>
      <CopyButton text={t.states.artifactsCmdDocker} />
      <p className="mt-4 text-xs font-medium text-white/80">{t.states.artifactsNote}</p>
    </div>
  );
}

export function EmptyState({
  title,
  body,
  actionLabel,
  onAction,
}: {
  title: string;
  body?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div role="status" className="card rounded-lg p-8 text-center">
      <h2 className="text-xl font-semibold">{title}</h2>
      {body && <p className="mt-2 text-sm text-g4-muted">{body}</p>}
      {actionLabel && onAction && (
        <button type="button" className="btn-primary mt-4" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}

/** Error strip. `standalone` = it replaces the content, so the retry button takes focus. */
export function ApiErrorBanner({
  error,
  onRetry,
  title = t.states.apiErrorTitle,
  standalone = false,
}: {
  error: unknown;
  onRetry?: () => void;
  title?: string;
  standalone?: boolean;
}) {
  const ref = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (standalone) ref.current?.focus();
  }, [standalone]);
  const status = error instanceof ApiError ? error.status : 'rede';
  return (
    <div role="alert" className="rounded bg-g4-risk p-4 text-white shadow-card">
      <p className="font-semibold">{title}</p>
      <p className="mt-1 text-sm">{t.states.apiErrorBody(status)}</p>
      {onRetry && (
        <button
          ref={ref}
          type="button"
          className="btn-secondary mt-3 h-8 text-xs"
          onClick={onRetry}
        >
          {t.states.retry}
        </button>
      )}
    </div>
  );
}

/** Route a query error to the right state component. */
export function QueryError({
  error,
  onRetry,
  title,
}: {
  error: unknown;
  onRetry?: () => void;
  title?: string;
}) {
  if (error instanceof ApiError && error.artifactsMissing) return <ArtifactsMissing />;
  return <ApiErrorBanner error={error} onRetry={onRetry} title={title} standalone />;
}
