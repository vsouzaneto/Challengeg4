import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Props = {
  /** A diferença curta ("−4,6 pontos"). */
  short: string;
  /** A faixa curta, embaixo ("entre −6,8 e −2,5"). */
  range?: string;
  /** A frase completa: é o que o leitor de tela ouve. */
  full: string;
  /** `chip`: badge neutro; `text`: número e faixa em linhas. */
  variant?: "chip" | "text";
  /** Ação ao lado do chip (ex.: um InfoPopover com a faixa). */
  extra?: ReactNode;
  className?: string;
};

/** Diferença curta e neutra (sem verde nem vermelho), com a frase inteira em `sr-only`. */
export function DeltaValue({ short, range, full, variant = "text", extra, className }: Props) {
  return (
    <span className={cn("flex flex-col gap-0.5", variant === "chip" ? "items-start" : "items-end", className)}>
      <span className="sr-only">{full}</span>
      {variant === "chip" ? (
        <span className="flex items-center gap-1">
          <Badge variant="outline" className="tabular-nums" aria-hidden>{short}</Badge>
          {extra}
        </span>
      ) : (
        <span aria-hidden className="text-sm font-medium tabular-nums">{short}</span>
      )}
      {range && <span aria-hidden className="text-xs text-muted-foreground tabular-nums">{range}</span>}
    </span>
  );
}
