"use client"

import { useEffect, useState } from "react"
import { CircleAlertIcon, RotateCwIcon } from "lucide-react"

import { ScoreBadge, StatePill } from "@/components/pipeline/deal-card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { fmtChance, fmtDays, fmtDec, fmtInt, fmtMoney, fmtMoneyFull, fmtPct } from "@/lib/explain"
import type { DetailDTO } from "@/lib/server/view"
import { cn } from "@/lib/utils"

type Load = { status: "loading" } | { status: "error"; message: string } | { status: "ok"; data: DetailDTO }

export function DealSheet({ id, onClose }: { id: string | null; onClose: () => void }) {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState<{ key: string; load: Load } | null>(null)
  const key = `${id}#${attempt}`
  // Resultado de outra oportunidade (ou de outra tentativa) conta como carregando.
  const load: Load = result?.key === key ? result.load : { status: "loading" }

  useEffect(() => {
    if (!id) return
    const ctrl = new AbortController()
    fetch(`/api/oportunidades/${encodeURIComponent(id)}`, { signal: ctrl.signal })
      .then(async (r) => {
        const body = await r.json()
        if (!r.ok) throw new Error(body.error ?? "Falha ao carregar o detalhamento.")
        setResult({ key, load: { status: "ok", data: body } })
      })
      .catch((e: Error) => {
        if (e.name !== "AbortError") setResult({ key, load: { status: "error", message: e.message } })
      })
    return () => ctrl.abort()
  }, [id, key])

  const data = load.status === "ok" ? load.data : null
  return (
    <Sheet open={id !== null} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-lg">
        <SheetHeader className="border-b">
          <SheetTitle>{data ? `${data.account ?? "Conta não informada"} · ${data.product}` : "Detalhamento do score"}</SheetTitle>
          <SheetDescription>
            {data ? `${data.id} · ${data.stage} · ${data.agent}${data.region ? ` (${data.region})` : ""}` : id}
          </SheetDescription>
        </SheetHeader>

        {load.status === "loading" && (
          <div className="flex flex-col gap-4 p-4" aria-busy="true" aria-label="Carregando detalhamento">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        )}
        {load.status === "error" && (
          <div className="p-4">
            <Alert variant="destructive">
              <CircleAlertIcon />
              <AlertTitle>Não foi possível carregar o detalhamento</AlertTitle>
              <AlertDescription className="flex flex-col items-start gap-2">
                {load.message}
                <Button variant="outline" size="sm" onClick={() => setAttempt((a) => a + 1)}>
                  <RotateCwIcon data-icon="inline-start" />
                  Tentar novamente
                </Button>
              </AlertDescription>
            </Alert>
          </div>
        )}
        {data && <DetailBody d={data} />}
      </SheetContent>
    </Sheet>
  )
}

function DetailBody({ d }: { d: DetailDTO }) {
  const mult = (x: number) => `×${x.toFixed(2).replace(".", ",")}`
  const sit = d.situation
  // Cada passo é um termo da conta que gera a posição; nada que não entrou no cálculo aparece.
  const steps: { title: string; value: string; body: React.ReactNode }[] = [
    {
      title: "Valor se ganhar",
      value: fmtMoney(d.value.value),
      body: `Preço de tabela ${fmtMoneyFull(d.value.price)} × ${fmtDec(d.value.rho)}, a razão histórica entre valor fechado e preço.`,
    },
    {
      title: `Situação: ${sit.label}`,
      value: fmtChance(sit.factor),
      body: sit.conversion
        ? `${sit.meaning} Chance de um deal em Início (${fmtChance(sit.chance)}) × ${fmtPct(sit.conversion.c)} de conversão para Engaging${
            sit.conversion.converted + sit.conversion.failed === 0
              ? " (estimativa neutra até haver uploads sucessivos para comparar)."
              : ` (${fmtInt(sit.conversion.converted)} de ${fmtInt(sit.conversion.converted + sit.conversion.failed)} deals acompanhados converteram).`
          }`
        : `${sit.meaning} Entre os ${fmtInt(sit.reached)} deals da base que chegaram a esta situação, a chance de terminar ganho é ${fmtChance(sit.chance)}.`,
    },
    ...d.factors.map((f) => ({ title: f.label, value: mult(f.factor), body: f.reason })),
    ...(d.urgency
      ? [
          {
            title: "Urgência",
            value: mult(d.urgency.factor),
            body: `A chance deste deal cai ${fmtPct(d.urgency.drop)} nos próximos ${d.urgency.horizonDays} dias se nada for feito.`,
          },
        ]
      : []),
    {
      title: "Prioridade",
      value: fmtMoney(d.priority),
      body:
        d.priority === null
          ? "Sem prioridade: o produto não tem preço no catálogo."
          : `${fmtMoney(d.value.value)} × ${fmtChance(d.p)} de chance${d.urgency ? ` × ${mult(d.urgency.factor)} de urgência` : ""}.`,
    },
  ]
  if (d.score !== null && d.K !== null && d.priority !== null) {
    const ratio = d.priority / d.K
    steps.push({
      title: "Score",
      value: String(d.score),
      body: `100 × prioridade ÷ (prioridade + ${fmtMoney(d.K)}), onde ${fmtMoney(d.K)} é a prioridade mediana dos deals vivos. Este deal está em ${fmtDec(ratio, ratio < 10 ? 2 : 0)}× a mediana.`,
    })
  }

  return (
    <div className="flex flex-col gap-6 p-4">
      <div className="flex items-center gap-4">
        <ScoreBadge score={d.score} className="size-14 text-xl" />
        <div className="flex flex-col gap-1">
          <span className="font-medium">
            {d.score === null ? "Sem score" : `#${d.rank} de ${fmtInt(d.nScored)} oportunidades abertas`}
          </span>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <StatePill state={d.state} />
            {d.age !== null && `${fmtDays(d.age)} desde a entrada em Engaging`}
          </div>
        </div>
      </div>

      <section className="flex flex-col gap-3" aria-labelledby="calc">
        <h3 id="calc" className="font-semibold">
          Por que está nesta posição
        </h3>
        <ol className="flex flex-col gap-3 text-sm">
          {steps.map((st, i) => (
            <Step key={st.title} n={i + 1} title={st.title} value={st.value}>
              {st.body}
            </Step>
          ))}
        </ol>
      </section>

      {d.age !== null && <AgeTimeline d={d} />}
    </div>
  )
}

function Step({ n, title, value, children }: { n: number; title: string; value: string; children: React.ReactNode }) {
  return (
    <li className="flex gap-3">
      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-secondary text-xs font-semibold">{n}</span>
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        <div className="flex items-baseline justify-between gap-2">
          <span className="font-medium">{title}</span>
          <span className="font-semibold tabular-nums">{value}</span>
        </div>
        <div className="text-muted-foreground">{children}</div>
      </div>
    </li>
  )
}

// Linha do tempo com os limiares aprendidos e a posição do deal.
function AgeTimeline({ d }: { d: DetailDTO }) {
  const t = d.thresholds
  const max = Math.max(t.tardio * 1.15, (d.age ?? 0) * 1.05)
  const pct = (v: number) => `${Math.min(100, (v / max) * 100)}%`
  const segments = [
    { from: 0, to: t.inicio, label: "Início", cls: "bg-secondary" },
    { from: t.inicio, to: t.andamento, label: "Em andamento", cls: "bg-success/40" },
    { from: t.andamento, to: t.esfriando, label: "Esfriando", cls: "bg-warning/50" },
    { from: t.esfriando, to: t.tardio, label: "Tardio", cls: "bg-destructive/30" },
    { from: t.tardio, to: max, label: "Revalidar", cls: "bg-muted" },
  ]
  return (
    <section className="flex flex-col gap-2" aria-labelledby="age">
      <h3 id="age" className="font-semibold">
        Idade do deal
      </h3>
      <div className="relative pt-5">
        <div
          className="absolute top-0 -translate-x-1/2 text-xs font-semibold whitespace-nowrap"
          style={{ left: pct(d.age ?? 0) }}
        >
          {d.age}d
        </div>
        <div className="flex h-3 overflow-hidden rounded-full" role="img" aria-label={`Deal com ${d.age} dias`}>
          {segments.map((s) => (
            <div key={s.label} className={s.cls} style={{ width: `${((s.to - s.from) / max) * 100}%` }} />
          ))}
        </div>
        <div className="absolute top-4 h-5 w-0.5 -translate-x-1/2 bg-foreground" style={{ left: pct(d.age ?? 0) }} />
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
        {segments.map((s) => (
          <span key={s.label} className="flex items-center gap-1">
            <span className={cn("size-2 rounded-full", s.cls)} />
            {s.label} {s.label === "Revalidar" ? `> ${s.from}d` : `${Math.round(s.from)}–${s.to}d`}
          </span>
        ))}
      </div>
      <p className="text-xs text-muted-foreground">Limiares aprendidos da {t.source}; mudam quando a base muda.</p>
    </section>
  )
}
