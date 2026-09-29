"use client"

import { useState } from "react"
import Link from "next/link"
import { ChevronDownIcon, ChevronLeftIcon, ChevronRightIcon, SearchXIcon } from "lucide-react"

import { PageHeader } from "@/components/page-header"
import { ClosedCard, DealCard } from "@/components/pipeline/deal-card"
import { DealSheet } from "@/components/pipeline/deal-sheet"
import { FilterBar } from "@/components/pipeline/filter-bar"
import { Badge } from "@/components/ui/badge"
import { Button, buttonVariants } from "@/components/ui/button"
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/components/ui/empty"
import { fmtInt, fmtMoney } from "@/lib/explain"
import type { BoardDTO, LaneDTO } from "@/lib/server/view"
import { cn } from "@/lib/utils"

const PAGE = 15

export function PipelineView({ board }: { board: BoardDTO }) {
  const [openId, setOpenId] = useState<string | null>(null)
  const f = board.filters
  const scope = f.vendedor ?? f.manager ?? f.regiao
  const showAgent = !f.vendedor
  const firstId = board.lanes.flatMap((l) => l.cards).find((c) => c.rank === 1)?.id
  const empty = board.lanes.every((l) => l.count === 0)

  return (
    <div className="flex min-w-0 flex-col gap-5">
      <PageHeader
        title={scope ? `Pipeline · ${scope}` : "Pipeline"}
        description="Um score para todas as oportunidades: valor × chance da situação × demais fatores aprendidos. Comece pelo #1 e desça a lista."
        actions={
          <Link href="/modelo" className={buttonVariants({ variant: "outline", size: "sm" })}>
            Modelo v{board.version} · base até {board.refDay}
          </Link>
        }
      />

      <FilterBar options={board.options} filters={f} />

      {empty ? (
        <Empty className="border">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <SearchXIcon />
            </EmptyMedia>
            <EmptyTitle>Nenhuma oportunidade neste filtro</EmptyTitle>
            <EmptyDescription>Troque a região, o manager ou o vendedor, ou limpe os filtros.</EmptyDescription>
          </EmptyHeader>
          <EmptyContent>
            <Link href="/" className={buttonVariants({ variant: "outline" })}>
              Limpar filtros
            </Link>
          </EmptyContent>
        </Empty>
      ) : (
        <>
          <dl className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <Stat label="vivos para trabalhar" value={board.summary.vivos} />
            <Stat label="esfriando ou tardios: agir esta semana" value={board.summary.esfriando} tone="warning" />
            <Stat label="parados além do histórico: revalidar" value={board.summary.revalidar} />
            <Stat label="com pendência de cadastro" value={board.summary.pendencias} />
          </dl>

          <div className="-mx-4 flex gap-4 overflow-x-auto px-4 pb-4 md:-mx-6 md:px-6" role="list" aria-label="Raias do pipeline">
            {board.lanes.map((lane) =>
              lane.count === 0 ? (
                <div
                  key={lane.stage}
                  role="listitem"
                  aria-label={`Raia ${lane.stage}: nenhuma oportunidade neste filtro`}
                  className="flex w-14 shrink-0 flex-col items-center rounded-2xl border border-dashed py-4 text-muted-foreground"
                >
                  <span className="text-sm font-semibold [writing-mode:vertical-rl]">{lane.stage} · 0</span>
                </div>
              ) : lane.kind === "aberta" ? (
                <OpenLane
                  key={lane.stage}
                  lane={lane}
                  start={lane.stage === board.startStage}
                  firstId={firstId}
                  showAgent={showAgent}
                  onOpen={setOpenId}
                />
              ) : (
                <ClosedLane key={lane.stage} lane={lane} />
              ),
            )}
          </div>
        </>
      )}

      <DealSheet id={openId} onClose={() => setOpenId(null)} />
    </div>
  )
}

function Stat({ label, value, tone }: { label: string; value: number; tone?: "warning" }) {
  return (
    <div className="flex items-baseline gap-1.5">
      <dt className="sr-only">{label}</dt>
      <dd className={cn("text-lg font-semibold tabular-nums", tone === "warning" && value > 0 && "text-foreground underline decoration-warning decoration-2 underline-offset-4")}>
        {fmtInt(value)}
      </dd>
      <span aria-hidden className="text-muted-foreground">
        {label}
      </span>
    </div>
  )
}

function OpenLane({
  lane,
  start,
  firstId,
  showAgent,
  onOpen,
}: {
  lane: LaneDTO
  start: boolean
  firstId?: string
  showAgent: boolean
  onOpen: (id: string) => void
}) {
  const [visible, setVisible] = useState(PAGE)
  const cards = lane.cards.slice(0, visible)
  return (
    <section
      role="listitem"
      aria-label={`Raia ${lane.stage}`}
      className={cn("flex w-[340px] shrink-0 flex-col gap-3 rounded-2xl bg-muted/50 p-3", start && "bg-muted ring-1 ring-primary/30")}
    >
      <header className="flex flex-col gap-1 px-1">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-semibold">{lane.stage}</h2>
          <span className="text-sm text-muted-foreground tabular-nums">{fmtInt(lane.count)}</span>
          {start && <Badge className="ml-auto">Comece aqui</Badge>}
        </div>
        <span className="text-xs text-muted-foreground">
          prioridade somada {fmtMoney(lane.priorityTotal)}
        </span>
      </header>

      {lane.cards.length === 0 && (
        <p className="rounded-xl border border-dashed p-4 text-center text-sm text-muted-foreground">
          Nenhuma oportunidade aberta nesta raia.
        </p>
      )}
      <ol className="flex flex-col gap-2">
        {cards.map((c) => (
          <li key={c.id}>
            <DealCard card={c} first={c.id === firstId} showAgent={showAgent} onOpen={onOpen} />
          </li>
        ))}
      </ol>
      {lane.cards.length > visible && (
        <Button variant="ghost" onClick={() => setVisible((v) => v + PAGE)}>
          <ChevronDownIcon data-icon="inline-start" />
          Mostrar mais {Math.min(PAGE, lane.cards.length - visible)} de {lane.cards.length - visible}
        </Button>
      )}

    </section>
  )
}

function ClosedLane({ lane }: { lane: LaneDTO }) {
  const [open, setOpen] = useState(false)
  const won = lane.kind === "ganha"
  const summary = won ? `${fmtMoney(lane.closedTotal)} fechados` : "encerrados sem venda"
  if (!open) {
    return (
      <div role="listitem" className="flex shrink-0">
        <button
          type="button"
          onClick={() => setOpen(true)}
          aria-expanded={false}
          aria-label={`Raia ${lane.stage}: ${lane.count} oportunidades, ${summary}. Expandir histórico`}
          className="flex w-14 shrink-0 flex-col items-center gap-3 rounded-2xl border border-dashed py-4 text-muted-foreground transition-colors hover:bg-muted/50"
        >
          <ChevronLeftIcon className="size-4" aria-hidden />
          <span className="text-sm font-semibold [writing-mode:vertical-rl]">
            {lane.stage} · {fmtInt(lane.count)}
          </span>
        </button>
      </div>
    )
  }
  return (
    <section role="listitem" aria-label={`Raia ${lane.stage}`} className="flex w-[280px] shrink-0 flex-col gap-3 rounded-2xl border border-dashed p-3">
      <header className="flex items-start gap-2 px-1">
        <div className="flex flex-col gap-0.5">
          <h2 className="font-semibold text-muted-foreground">
            {lane.stage} <span className="font-normal tabular-nums">{fmtInt(lane.count)}</span>
          </h2>
          <span className="text-xs text-muted-foreground">Histórico · {summary}</span>
        </div>
        <Button variant="ghost" size="icon-sm" className="ml-auto" onClick={() => setOpen(false)} aria-label={`Recolher ${lane.stage}`}>
          <ChevronRightIcon />
        </Button>
      </header>
      <ol className="flex flex-col gap-2">
        {lane.cards.map((c) => (
          <li key={c.id}>
            <ClosedCard card={c} won={won} />
          </li>
        ))}
      </ol>
      {lane.count > lane.cards.length && (
        <p className="px-1 text-xs text-muted-foreground">Mostrando os {lane.cards.length} fechamentos mais recentes.</p>
      )}
    </section>
  )
}
