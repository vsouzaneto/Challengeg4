"use client"

import { CircleAlertIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { STATE_META, fmtDays, fmtMoney, fmtPct, scoreTier, type Tone } from "@/lib/explain"
import type { AgeState } from "@/lib/scoring/model"
import type { CardDTO } from "@/lib/server/view"
import { cn } from "@/lib/utils"

export function ScoreBadge({ score, className }: { score: number | null; className?: string }) {
  const tier = scoreTier(score)
  return (
    <span
      className={cn(
        "flex size-10 shrink-0 items-center justify-center rounded-lg text-sm font-semibold tabular-nums",
        tier === "alta" && "bg-primary text-primary-foreground",
        tier === "media" && "bg-secondary text-secondary-foreground ring-1 ring-border",
        tier === "baixa" && "bg-background text-muted-foreground ring-1 ring-border",
        tier === null && "bg-muted text-muted-foreground",
        className,
      )}
    >
      {score ?? "—"}
    </span>
  )
}

const toneClass: Record<Tone, string> = {
  neutral: "",
  warning: "border-warning bg-warning/15 text-foreground",
  danger: "",
  muted: "text-muted-foreground",
}
const toneVariant: Record<Tone, "secondary" | "outline" | "destructive"> = {
  neutral: "secondary",
  warning: "outline",
  danger: "destructive",
  muted: "outline",
}

export function StatePill({ state }: { state: AgeState }) {
  const meta = STATE_META[state]
  return (
    <Badge variant={toneVariant[meta.tone]} className={toneClass[meta.tone]}>
      {meta.label}
    </Badge>
  )
}

export function DealCard({
  card,
  first,
  showAgent,
  onOpen,
}: {
  card: CardDTO
  first: boolean
  showAgent: boolean
  onOpen: (id: string) => void
}) {
  return (
    <button
      type="button"
      onClick={() => onOpen(card.id)}
      className={cn(
        "group flex w-full flex-col gap-2 rounded-xl border bg-card p-3 text-left text-card-foreground shadow-xs transition-colors hover:border-foreground/30 focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none",
        first && "border-primary ring-2 ring-primary",
      )}
      aria-label={`${card.account ?? "Conta não informada"}, ${card.product}, score ${card.score ?? "sem score"}. Abrir detalhamento`}
    >
      {first && <span className="text-xs font-semibold text-primary">Comece por este</span>}
      <div className="flex items-start gap-3">
        <Tooltip>
          <TooltipTrigger render={<span />} className="rounded-lg">
            <ScoreBadge score={card.score} />
          </TooltipTrigger>
          <TooltipContent side="right" className="flex-col items-start gap-1 text-left">
            {card.tooltip.map((line, i) => (
              <span key={i} className={i === 0 ? "font-semibold" : undefined}>
                {line}
              </span>
            ))}
            <span className="text-background/70">Clique para ver o detalhamento</span>
          </TooltipContent>
        </Tooltip>
        <div className="flex min-w-0 flex-1 flex-col gap-0.5">
          <div className="flex items-center gap-2">
            {card.rank !== null && <span className="text-xs text-muted-foreground tabular-nums">#{card.rank}</span>}
            <span className={cn("truncate font-medium", !card.account && "text-muted-foreground italic")}>
              {card.account ?? "Conta não informada"}
            </span>
          </div>
          <span className="truncate text-sm text-muted-foreground">
            {card.product} · {fmtMoney(card.value)}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
        {card.p !== null && (
          <span>
            <span className="font-medium text-foreground">{fmtPct(card.p)}</span> de chance
          </span>
        )}
        {card.expected !== null && (
          <span>
            Receita esperada <span className="font-medium text-foreground">{fmtMoney(card.expected)}</span>
          </span>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        {card.state && <StatePill state={card.state} />}
        {card.age !== null && <span>{fmtDays(card.age)}</span>}
        {showAgent && <span className="truncate">· {card.agent}</span>}
      </div>

      {card.flags.length > 0 && (
        <span className="flex items-center gap-1 text-xs text-muted-foreground">
          <CircleAlertIcon className="size-3.5" aria-hidden />
          {card.flags.length === 1 ? "1 pendência de cadastro" : `${card.flags.length} pendências de cadastro`}
        </span>
      )}
    </button>
  )
}

export function ClosedCard({ card, won }: { card: CardDTO; won: boolean }) {
  return (
    <div className="flex flex-col gap-1 rounded-lg border bg-card/60 p-2.5 text-xs text-muted-foreground">
      <span className="truncate text-sm font-medium text-foreground">{card.account ?? "Conta não informada"}</span>
      <span className="truncate">
        {card.product} · {won ? fmtMoney(card.closeValue) : "perdido"}
      </span>
      <span className="truncate">
        {card.closeDate} · {card.agent}
      </span>
    </div>
  )
}
