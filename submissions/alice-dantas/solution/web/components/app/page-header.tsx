import type { ReactNode } from "react";

/** Abertura de página: título, a pergunta que ela responde e as ações (ex.: escolher vendedor). */
export function PageHeader({ title, description, actions }: { title: string; description: string; actions?: ReactNode }) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {actions}
    </div>
  );
}
