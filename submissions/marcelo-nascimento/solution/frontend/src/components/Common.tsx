import type { ReactNode } from "react";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="state-panel state-error" role="alert">
      <i className="fa-solid fa-triangle-exclamation" aria-hidden="true" />
      <div>
        <strong>Não foi possível carregar os dados.</strong>
        <p>{message}</p>
      </div>
      {onRetry ? (
        <button className="btn btn-outline-light btn-sm" type="button" onClick={onRetry}>
          Tentar novamente
        </button>
      ) : null}
    </div>
  );
}

export function LoadingState({ label = "Carregando..." }: { label?: string }) {
  return (
    <div className="state-panel" role="status" aria-live="polite">
      <span className="spinner-border text-info" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="state-panel state-empty">
      <i className="fa-regular fa-folder-open" aria-hidden="true" />
      <strong>{title}</strong>
      <p>{message}</p>
    </div>
  );
}

export function ScoreBadge({ score, hot }: { score: number; hot: boolean }) {
  return (
    <span className={`score-badge ${hot ? "score-hot" : ""}`} aria-label={`Score ${score}${hot ? ", Hot Lead" : ""}`}>
      <strong>{score}</strong>
      {hot ? <span>Hot Lead</span> : null}
    </span>
  );
}

export function MetricCard({ icon, label, value, detail, accent = "violet" }: {
  icon: string;
  label: string;
  value: ReactNode;
  detail: string;
  accent?: "teal" | "violet";
}) {
  return (
    <article className={`metric-card metric-${accent}`}>
      <span className="metric-icon"><i className={`fa-solid ${icon}`} aria-hidden="true" /></span>
      <div>
        <span className="metric-label">{label}</span>
        <strong className="metric-value">{value}</strong>
        <small>{detail}</small>
      </div>
    </article>
  );
}

export function BarList({ items, valueLabel, emptyMessage }: {
  items: Array<{ name: string; value: number; secondary?: string }>;
  valueLabel: (value: number) => string;
  emptyMessage: string;
}) {
  if (items.length === 0) {
    return <p className="text-secondary mb-0">{emptyMessage}</p>;
  }
  const maximum = Math.max(...items.map((item) => item.value), 1);
  return (
    <div className="bar-list">
      {items.map((item) => (
        <div className="bar-row" key={item.name}>
          <div className="bar-label">
            <span>{item.name}</span>
            <strong>{valueLabel(item.value)}</strong>
          </div>
          <div className="bar-track" aria-hidden="true">
            <span style={{ width: `${Math.max(2, item.value / maximum * 100)}%` }} />
          </div>
          {item.secondary ? <small>{item.secondary}</small> : null}
        </div>
      ))}
    </div>
  );
}
