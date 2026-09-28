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
import type { BoardDTO, CardDTO, LaneDTO } from "@/lib/server/view"
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
        description="Ordenado por receita esperada: chance de ganhar × valor. Comece pelo #1 e desça a lista."
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
          {fmtInt(lane.cards.length)} vivos · receita esperada {fmtMoney(lane.expectedTotal)}
        </span>
      </header>

      {lane.cards.length === 0 && (
        <p className="rounded-xl border border-dashed p-4 text-center text-sm text-muted-foreground">
          Nenhuma oportunidade ativa nesta raia.
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

      {lane.revalidar.count > 0 && <Revalidar lane={lane} showAgent={showAgent} onOpen={onOpen} />}
    </section>
  )
}

function Revalidar({ lane, showAgent, onOpen }: { lane: LaneDTO; showAgent: boolean; onOpen: (id: string) => void }) {
  const { count, value, cards } = lane.revalidar
  return (
    <details className="group rounded-xl border border-dashed bg-background/60">
      <summary className="flex cursor-pointer list-none flex-col gap-0.5 p-3 [&::-webkit-details-marker]:hidden">
        <span className="flex items-center gap-2 text-sm font-medium">
          <ChevronRightIcon className="size-4 transition-transform group-open:rotate-90" aria-hidden />
          Revalidar · {fmtInt(count)}
        </span>
        <span className="pl-6 text-xs text-muted-foreground">
          Abertos há mais tempo que 99% dos ganhos da base, com chance próxima de zero. {fmtMoney(value)} em jogo: confirme com o cliente ou encerre. Ordenados por score.
        </span>
      </summary>
      <ol className="flex flex-col gap-2 p-2 pt-0">
        {cards.map((c: CardDTO) => (
          <li key={c.id}>
            <DealCard card={c} first={false} showAgent={showAgent} onOpen={onOpen} />
          </li>
        ))}
        {count > cards.length && (
          <li className="px-1 pb-1 text-xs text-muted-foreground">
            Mostrando os {cards.length} de maior valor. Filtre por vendedor para ver a lista dele.
          </li>
        )}
      </ol>
    </details>
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
