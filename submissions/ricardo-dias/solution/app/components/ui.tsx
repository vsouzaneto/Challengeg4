import type { ReactNode } from "react";
import { Icon, type IconName } from "./icons";
import { dateLabel } from "./format";

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="section-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2>{title}</h2>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}
export function PageHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="page-description">{description}</p>
      </div>
      {action}
    </div>
  );
}
export function Stat({
  label,
  value,
  detail,
  icon,
  tone,
}: {
  label: string;
  value: string;
  detail: string;
  icon?: IconName;
  tone?: string;
}) {
  return (
    <div className={`stat${tone ? ` stat-${tone}` : ""}`}>
      <div className="stat-label">
        {label}
        {icon && <Icon name={icon} />}
      </div>
      <strong className="stat-value">{value}</strong>
      <p>{detail}</p>
    </div>
  );
}
export function Notice({
  title,
  children,
  tone = "info",
}: {
  title: string;
  children: ReactNode;
  tone?: string;
}) {
  return (
    <div className={`notice notice-${tone}`}>
      <Icon name={tone === "warning" || tone === "danger" ? "alert" : "info"} />
      <div>
        <strong>{title}</strong>
        <div className="notice-copy">{children}</div>
      </div>
    </div>
  );
}
export function Unavailable({
  title = "Este relatório está sendo preparado.",
  children,
}: {
  title?: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty-state panel">
      <span className="empty-icon">
        <Icon name="chart" width={28} height={28} />
      </span>
      <h2>{title}</h2>
      <p>
        {children ??
          "Os resultados aparecerão aqui quando os artefatos da análise estiverem disponíveis e compatíveis com a interface."}
      </p>
    </div>
  );
}
export function SourceNote({
  source,
  generatedAt,
}: {
  source: string;
  generatedAt?: string;
}) {
  return (
    <p className="source-note">
      <Icon name="book" width={14} height={14} />
      {source}
      {generatedAt && <span>· Atualizado em {dateLabel(generatedAt)}</span>}
    </p>
  );
}
