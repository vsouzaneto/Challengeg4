"use client"

import { useEffect, useState } from "react"
import { CircleAlertIcon, RotateCwIcon } from "lucide-react"

import { ScoreBadge, StatePill } from "@/components/pipeline/deal-card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { fmtDays, fmtInt, fmtMoney, fmtMoneyFull, fmtPct } from "@/lib/explain"
import type { DetailDTO } from "@/lib/server/view"
import { cn } from "@/lib/utils"

type Load = { status: "loading" } | { status: "error"; message: string } | { status: "ok"; data: DetailDTO }

export function DealSheet({ id, onClose }: { id: string | null; onClose: () => void }) {
  const [load, setLoad] = useState<Load>({ status: "loading" })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    if (!id) return
    const ctrl = new AbortController()
    setLoad({ status: "loading" })
    fetch(`/api/oportunidades/${encodeURIComponent(id)}`, { signal: ctrl.signal })
      .then(async (r) => {
        const body = await r.json()
        if (!r.ok) throw new Error(body.error ?? "Falha ao carregar o detalhamento.")
        setLoad({ status: "ok", data: body })
      })
      .catch((e: Error) => {
        if (e.name !== "AbortError") setLoad({ status: "error", message: e.message })
      })
    return () => ctrl.abort()
  }, [id, attempt])

  const data = load.status === "ok" ? load.data : null
  return (
    <Sheet open={id !== null} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto sm:max-w-lg">
        <SheetHeader className="border-b">
          <SheetTitle>{data ? `${data.account?.name ?? "Conta não informada"} · ${data.product}` : "Detalhamento do score"}</SheetTitle>
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
  const calibrated = d.calibration.before !== null && d.calibration.after !== null
  return (
    <div className="flex flex-col gap-6 p-4">
      <div className="flex items-center gap-4">
        <ScoreBadge score={d.score} className="size-14 text-xl" />
        <div className="flex flex-col gap-1">
          <span className="font-medium">
            {d.score === null
              ? "Sem score"
              : `#${d.rankGlobal} de ${fmtInt(d.nScored)} oportunidades abertas com score`}
          </span>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <StatePill state={d.state} />
            {d.age === null ? "sem data de entrada" : `${fmtDays(d.age)} desde a entrada em Engaging`}
          </div>
        </div>
      </div>

      <Alert variant={d.state === "esfriando" || d.state === "tardio" ? "destructive" : "default"}>
        <AlertTitle>O que fazer</AlertTitle>
        <AlertDescription>{d.action}</AlertDescription>
      </Alert>

      <section className="flex flex-col gap-3" aria-labelledby="calc">
        <h3 id="calc" className="font-semibold">
          Como o score foi calculado
        </h3>
        <ol className="flex flex-col gap-3 text-sm">
          <Step n={1} title="Chance pela idade do deal" value={fmtPct(d.base.p)}>
            {d.base.p === null
              ? "Sem estimativa: o deal está além de todo o histórico de ganhos da base."
              : d.base.prospecting
                ? "Sem data de entrada: usa a chance de um deal que acabou de entrar em Engaging. É uma estimativa otimista, porque ainda não se sabe quantos deals de Prospecting chegam a Engaging."
                : `Entre os ${fmtInt(d.base.support)} deals da base que chegaram a esta idade ainda abertos, esta é a parcela que terminou ganha (${d.base.curve}).`}
          </Step>
          <Step
            n={2}
            title="Ajustes por grupo"
            value={
              d.adjustments.length
                ? `${d.adjustments.reduce((s, a) => s + a.impact, 0) >= 0 ? "+" : ""}${fmtPct(d.adjustments.reduce((s, a) => s + a.impact, 0), 1)}`
                : "nenhum"
            }
          >
            {d.adjustments.length > 0 && (
              <ul className="mb-1 flex flex-col gap-1">
                {d.adjustments.map((a) => (
                  <li key={a.label}>
                    {a.label} ({a.group}): {a.impact >= 0 ? "+" : ""}
                    {fmtPct(a.impact, 1)}, com peso {fmtPct(a.weight)} por ter {Math.round(a.n)} deals de histórico
                  </li>
                ))}
              </ul>
            )}
            {d.groupsNote}
          </Step>
          {calibrated && (
            <Step n={3} title="Calibração pelo histórico de acertos" value={fmtPct(d.calibration.after)}>
              O modelo foi testado em datas passadas; esta etapa corrige o viés observado: {fmtPct(d.calibration.before)} →{" "}
              {fmtPct(d.calibration.after)}.
            </Step>
          )}
          <Step n={calibrated ? 4 : 3} title="Valor se ganhar" value={fmtMoney(d.value.value)}>
            Preço de tabela {fmtMoneyFull(d.value.price)} × {d.value.rho.toFixed(3).replace(".", ",")} (razão histórica entre valor
            fechado e preço de tabela).
          </Step>
          <Step n={calibrated ? 5 : 4} title="Receita esperada" value={fmtMoney(d.expected)}>
            {d.expected === null
              ? "Sem receita esperada: falta a chance ou o valor."
              : `${fmtPct(d.calibration.after)} × ${fmtMoney(d.value.value)}. O score ${d.score} indica que esta receita esperada é maior que a de ${d.score}% das oportunidades abertas com score.`}
          </Step>
        </ol>
      </section>

      {d.age !== null && <AgeTimeline d={d} />}

      {d.tasks.length > 0 && (
        <section className="flex flex-col gap-2" aria-labelledby="tasks">
          <h3 id="tasks" className="font-semibold">
            Pendências de cadastro
          </h3>
          <ul className="flex list-disc flex-col gap-1 pl-5 text-sm">
            {d.tasks.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
          <p className="text-xs text-muted-foreground">Pendências não reduzem o score; são tarefas para manter a base confiável.</p>
        </section>
      )}

      {d.account && (d.account.sector || d.account.location) && (
        <section className="flex flex-col gap-1 text-sm" aria-labelledby="acc">
          <h3 id="acc" className="font-semibold">
            Conta
          </h3>
          <span className="text-muted-foreground">
            {[d.account.sector, d.account.employees && `${fmtInt(d.account.employees)} funcionários`, d.account.location]
              .filter(Boolean)
              .join(" · ")}
          </span>
        </section>
      )}

      <Separator />
      <p className="text-xs text-muted-foreground">
        Modelo v{d.model.version} · base até {d.model.refDay} · {d.model.configKey}
      </p>
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
