import type { ReactNode } from "react";

export function PageHeader({ kicker, title, children, actions }: { kicker?: string; title: string; children?: ReactNode; actions?: ReactNode }) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line bg-white px-8 py-6">
      <div className="max-w-3xl">
        {kicker && <div className="kicker mb-1">{kicker}</div>}
        <h1 className="h-display text-2xl font-extrabold text-navy">{title}</h1>
        {children && <div className="mt-1.5 text-sm text-muted">{children}</div>}
      </div>
      {actions}
    </header>
  );
}

export function Stat({ label, value, sub, tone = "default", hint }: { label: string; value: ReactNode; sub?: ReactNode; tone?: "default" | "gold" | "good" | "bad"; hint?: string }) {
  const color = tone === "gold" ? "text-gold" : tone === "good" ? "text-emerald-700" : tone === "bad" ? "text-red-700" : "text-navy";
  return (
    <div className="card p-4" title={hint}>
      <div className="text-[11px] font-semibold uppercase tracking-wide text-muted">{label}</div>
      <div className={`h-display mt-1 text-2xl font-extrabold ${color}`}>{value}</div>
      {sub && <div className="mt-0.5 text-xs text-muted">{sub}</div>}
    </div>
  );
}

export function Section({ title, kicker, children, right, className = "" }: { title: string; kicker?: string; children: ReactNode; right?: ReactNode; className?: string }) {
  return (
    <section className={`card p-5 ${className}`}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          {kicker && <div className="kicker">{kicker}</div>}
          <h2 className="h-display text-base font-bold text-navy">{title}</h2>
        </div>
        {right}
      </div>
      {children}
    </section>
  );
}

const PILL: Record<string, string> = {
  auto: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  suggest: "bg-amber-50 text-amber-800 ring-amber-200",
  human: "bg-rose-50 text-rose-800 ring-rose-200",
  Critical: "bg-rose-600 text-white ring-rose-600",
  High: "bg-orange-50 text-orange-800 ring-orange-200",
  Medium: "bg-sky-50 text-sky-800 ring-sky-200",
  Low: "bg-slate-50 text-slate-700 ring-slate-200",
  Positive: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  Neutral: "bg-slate-50 text-slate-700 ring-slate-200",
  Frustrated: "bg-amber-50 text-amber-800 ring-amber-200",
  Angry: "bg-rose-50 text-rose-800 ring-rose-200",
  HIGH: "bg-rose-50 text-rose-800 ring-rose-200",
  MEDIUM: "bg-amber-50 text-amber-800 ring-amber-200",
  LOW: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  new: "bg-sky-50 text-sky-800 ring-sky-200",
  open: "bg-sky-50 text-sky-800 ring-sky-200",
  escalated: "bg-rose-50 text-rose-800 ring-rose-200",
  pending: "bg-amber-50 text-amber-800 ring-amber-200",
  resolved: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  closed: "bg-slate-100 text-slate-600 ring-slate-200",
};
export const LABEL: Record<string, string> = {
  auto: "AUTO", suggest: "SUGESTÃO", human: "HUMANO", new: "Novo", open: "Aberto", escalated: "Escalado", pending: "Aguardando cliente",
  resolved: "Resolvido", closed: "Fechado", Positive: "Positivo", Neutral: "Neutro", Frustrated: "Frustrado", Angry: "Irritado",
  HIGH: "Risco alto", MEDIUM: "Risco médio", LOW: "Risco baixo",
};

export function Pill({ v, children }: { v: string; children?: ReactNode }) {
  return <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ring-inset ${PILL[v] ?? "bg-slate-50 text-slate-700 ring-slate-200"}`}>{children ?? LABEL[v] ?? v}</span>;
}

export function Bar({ value, max = 100, color = "bg-gold" }: { value: number; max?: number; color?: string }) {
  return <div className="h-2 w-full overflow-hidden rounded-full bg-offwhite"><div className={`h-full rounded-full ${color}`} style={{ width: `${Math.max(0, Math.min(100, (value / max) * 100))}%` }} /></div>;
}

export const fmt = {
  n: (v: number | null | undefined, d = 0) => (v === null || v === undefined || Number.isNaN(v) ? "—" : v.toLocaleString("pt-BR", { maximumFractionDigits: d, minimumFractionDigits: d })),
  pct: (v: number | null | undefined, d = 0) => (v === null || v === undefined || Number.isNaN(v) ? "—" : `${v.toLocaleString("pt-BR", { maximumFractionDigits: d, minimumFractionDigits: d })}%`),
  brl: (v: number) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 }),
  delta: (cur: number, prev: number) => (prev ? `${cur >= prev ? "▲" : "▼"} ${Math.abs(((cur - prev) / prev) * 100).toFixed(0)}% vs período anterior` : "sem período anterior"),
  ago: (ms: number) => {
    const s = (Date.now() - ms) / 1000;
    if (s < 60) return "agora";
    if (s < 3600) return `${Math.floor(s / 60)} min`;
    if (s < 86400) return `${Math.floor(s / 3600)} h`;
    return `${Math.floor(s / 86400)} d`;
  },
};
