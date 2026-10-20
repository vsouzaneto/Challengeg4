"use client";

import type { ReactNode } from "react";

import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

/** Uma linha do tooltip: o quadrado na cor da série, o nome e o valor já formatado em pt-BR (o padrão do shadcn usa
 * `toLocaleString()` do navegador). `extra` é uma segunda linha, como a diferença para a regra atual. */
export function tipRow(color: string | undefined, name: ReactNode, value: ReactNode, extra?: ReactNode) {
  return (
    <div className="flex w-full flex-col gap-0.5">
      <div className="flex items-center justify-between gap-4">
        <span className="flex items-center gap-1.5 text-muted-foreground">
          <svg aria-hidden viewBox="0 0 10 10" className="size-2.5 shrink-0">
            <rect width="10" height="10" rx="2" fill={color ?? "currentColor"} />
          </svg>
          {name}
        </span>
        <span className="font-medium text-foreground tabular-nums">{value}</span>
      </div>
      {extra && <span className="text-muted-foreground">{extra}</span>}
    </div>
  );
}

type Item = { color?: string; payload?: { fill?: string } };
export const tipColor = (item: Item) => item.payload?.fill ?? item.color;

/** O tooltip do shadcn (`ChartTooltip` + `ChartTooltipContent`) já ligado ao formato das linhas acima. */
export function ChartTip({ render, cursor = true, hideLabel = false }: {
  render: (value: number, name: string, item: Item & { payload?: Record<string, unknown> }) => ReactNode;
  cursor?: boolean;
  /** Sem o título da categoria: nas barras de uma linha só, ele repetiria a primeira série. */
  hideLabel?: boolean;
}) {
  return (
    <ChartTooltip cursor={cursor} allowEscapeViewBox={{ x: true, y: true }} wrapperStyle={{ zIndex: 50 }}
                  content={<ChartTooltipContent hideIndicator hideLabel={hideLabel}
                                                formatter={(value, name, item) => render(Number(value), String(name), item as never)} />} />
  );
}
