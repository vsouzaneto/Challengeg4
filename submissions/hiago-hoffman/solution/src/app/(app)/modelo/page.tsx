import type { Metadata } from "next"

import { PageHeader } from "@/components/page-header"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { fmtChance, fmtDec, fmtInt, fmtMoney, fmtPct } from "@/lib/explain"
import { formatDay } from "@/lib/scoring/dataset"
import { POLICY, calibrate } from "@/lib/scoring/model"
import { getState } from "@/lib/server/store"
import { cn } from "@/lib/utils"
import { UploadForm } from "./upload-form"

export const metadata: Metadata = { title: "Modelo e base" }
// Lê o estado vivo (base e versões): nunca pré-renderizar no build.
export const dynamic = "force-dynamic"

const AGES = [0, 14, 30, 60, 90, 120]
const IMPACT_LABEL = { bloqueia: "Impede o score", tarefa: "Vira pendência", info: "Informativo" }

export default async function ModeloPage() {
  const s = await getState()
  const { model, backtest: bt, version: v } = s
  const curve = model.curves.global
  const t = model.thresholds.global
  const results = [...bt.results].sort((a, b) => a.brier - b.brier)
  const conv = s.conversion
  const boundaryWeek = Math.floor(t.tardio / POLICY.weekDays)
  const tailRange = [curve.tailP[boundaryWeek], curve.tailP.at(-1)!]
  const best = results[0]

  return (
    <div className="flex max-w-5xl flex-col gap-6">
      <PageHeader
        title="Modelo e base"
        description="O score é recalculado e o modelo reaprende sempre que a base muda. Aqui está o que ele aprendeu e como foi testado."
      />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Modelo v{v.version}
            <Badge variant={v.promoted ? "default" : "secondary"}>{v.promoted ? "configuração promovida" : "configuração mantida"}</Badge>
          </CardTitle>
          <CardDescription>{v.reason}</CardDescription>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-x-8 gap-y-3 text-sm sm:grid-cols-3">
            <Info label="Base" value={v.source === "upload" ? "enviada por upload" : "padrão (dataset do challenge)"} />
            <Info label="Data de referência" value={v.refDay} />
            <Info label="Oportunidades" value={`${fmtInt(v.deals)} (${fmtInt(v.closed)} encerradas)`} />
            <Info label="Configuração" value={v.configKey} className="sm:col-span-2" />
            <Info label="Treinado em" value={new Date(v.createdAt).toISOString().slice(0, 16).replace("T", " ")} />
            <Info
              label="Escala do score (K)"
              value={s.K === null ? "—" : `${fmtMoney(s.K)}: receita esperada mediana dos deals vivos = score 50`}
              className="sm:col-span-2"
            />
            <Info
              label="Conversão Prospecting → Engaging"
              value={`${fmtPct(conv.c)} (${conv.converted + conv.failed === 0 ? "sem deals acompanhados ainda" : `${fmtInt(conv.converted)} de ${fmtInt(conv.converted + conv.failed)} acompanhados`}; ${fmtInt(conv.snapshots)} ${conv.snapshots === 1 ? "base" : "bases"})`}
            />
          </dl>
          {!s.persisted && (
            <p className="mt-3 text-xs text-muted-foreground">Disco somente leitura: o histórico de versões está só em memória.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Teste em datas passadas</CardTitle>
          <CardDescription>
            Em cada fim de mês de {formatDay(bt.cutoffs[0])} a {formatDay(bt.cutoffs.at(-1)!)}, o modelo só enxergou o que se sabia
            naquela data e foi avaliado pelo que aconteceu depois. Erro de probabilidade: quanto menor, melhor. Receita no topo:
            parcela da receita ganha que estava nos {fmtPct(POLICY.topShare)} primeiros da lista.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Configuração</TableHead>
                <TableHead className="text-right">Erro de probabilidade</TableHead>
                <TableHead className="text-right">Receita no topo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="text-muted-foreground">Sem modelo: taxa histórica e ordenação só por preço</TableCell>
                <TableCell className="text-right tabular-nums">{fmtDec(bt.baseline.brier)}</TableCell>
                <TableCell className="text-right tabular-nums">{fmtPct(bt.baseline.capture, 1)}</TableCell>
              </TableRow>
              {results.slice(0, 6).map((r) => (
                <TableRow key={r.key} className={cn(r.key === bt.chosen.key && "bg-muted/60 font-medium")}>
                  <TableCell>
                    {r.key}
                    {r.key === bt.chosen.key && <Badge className="ml-2">em uso</Badge>}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{fmtDec(r.brier)}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtPct(r.capture, 1)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <p className="text-sm text-muted-foreground">
            Depois da calibração, o erro da configuração em uso cai de {fmtDec(bt.chosen.brier)} para{" "}
            {fmtDec(bt.calibratedBrier)} (medido deixando cada mês de fora do ajuste). {results.length} configurações testadas.{" "}
            {best.config.levels === "tempo"
              ? "Usar produto, região e vendedor não melhorou a previsão."
              : "Usar produto, região e vendedor melhorou a previsão."}
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Chance de ganho pela idade</CardTitle>
            <CardDescription>
              Já calibrada. É o principal componente da chance nesta versão. Além do histórico, a chance é (ganhos + 1) ÷ (deals
              + 2) entre os deals que chegaram àquela idade, sem nunca subir com a idade.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Aberto há</TableHead>
                  <TableHead className="text-right">Chance de ganhar</TableHead>
                  <TableHead className="text-right">Deals que chegaram lá</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {AGES.map((age) => {
                  const w = Math.floor(age / POLICY.weekDays)
                  const p = w > curve.lastEventWeek ? null : calibrate(curve.pFrom[w], bt.calibrator)
                  return (
                    <TableRow key={age}>
                      <TableCell>{age} dias</TableCell>
                      <TableCell className="text-right tabular-nums">{fmtPct(p)}</TableCell>
                      <TableCell className="text-right tabular-nums">{fmtInt(curve.support[w] ?? 0)}</TableCell>
                    </TableRow>
                  )
                })}
                <TableRow>
                  <TableCell>mais de {t.tardio} dias</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {fmtChance(tailRange[0])} a {fmtChance(tailRange[1])}
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">revalidar</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Estados do deal</CardTitle>
            <CardDescription>Percentis fixos por política; os dias são reaprendidos a cada base.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableBody>
                <StateRow label="Início" rule="antes da mediana do ciclo das perdas" days={`até ${t.inicio} dias`} />
                <StateRow label="Em andamento" rule="até 75% dos ganhos" days={`${t.inicio}–${t.andamento} dias`} />
                <StateRow label="Esfriando" rule="entre 75% e 95% dos ganhos" days={`${t.andamento}–${t.esfriando} dias`} />
                <StateRow label="Tardio" rule="entre 95% e 99% dos ganhos" days={`${t.esfriando}–${t.tardio} dias`} />
                <StateRow label="Revalidar" rule="depois de 99% dos ganhos" days={`mais de ${t.tardio} dias`} />
              </TableBody>
            </Table>
            <p className="mt-3 text-sm text-muted-foreground">
              Valor se ganhar = preço de tabela × {fmtDec(model.rho.mean)} (razão média entre valor fechado e
              preço).
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Peso aprendido por grupo</CardTitle>
          <CardDescription>
            Cada grupo só ganha peso se variar mais do que o acaso explicaria. Nenhum nome é regra fixa: vendedor, produto ou região
            novos começam com peso zero e herdam o nível acima.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Grupo</TableHead>
                <TableHead className="text-right">Grupos</TableHead>
                <TableHead className="text-right">Peso de um grupo típico</TableHead>
                <TableHead>Leitura</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {s.groupDiagnostics.map((l) => {
                const groups = Object.values(l.groups)
                const typical = groups.map((g) => g.w).sort((a, b) => a - b)[Math.floor(groups.length / 2)] ?? 0
                return (
                  <TableRow key={l.id}>
                    <TableCell>{l.label}</TableCell>
                    <TableCell className="text-right tabular-nums">{groups.length}</TableCell>
                    <TableCell className="text-right tabular-nums">{fmtPct(typical)}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {l.k === null ? "Sem diferença além do acaso" : typical < 0.15 ? "Sinal fraco" : "Sinal relevante"}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
          {model.config.levels === "tempo" && (
            <p className="mt-3 text-sm text-muted-foreground">
              Mesmo com esses pesos, o teste em datas passadas mostrou que os grupos não melhoram a previsão; por isso a versão em
              uso considera só o tempo. Se isso mudar com novos resultados, a configuração muda sozinha.
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Qualidade da base</CardTitle>
          <CardDescription>Problemas encontrados na leitura. A base nunca é alterada; as correções valem só para o cálculo.</CardDescription>
        </CardHeader>
        <CardContent>
          {s.ds.issues.length === 0 ? (
            <p className="text-sm text-muted-foreground">Nenhum problema encontrado.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Problema</TableHead>
                  <TableHead className="text-right">Registros</TableHead>
                  <TableHead>Efeito</TableHead>
                  <TableHead>Exemplos</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {s.ds.issues.map((i) => (
                  <TableRow key={i.id}>
                    <TableCell className="whitespace-normal">{i.label}</TableCell>
                    <TableCell className="text-right tabular-nums">{fmtInt(i.count)}</TableCell>
                    <TableCell>{IMPACT_LABEL[i.impact]}</TableCell>
                    <TableCell className="max-w-56 truncate text-muted-foreground">{i.examples.join(", ")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card id="atualizar">
        <CardHeader>
          <CardTitle>Atualizar a base</CardTitle>
          <CardDescription>
            Envie os quatro CSVs exportados do CRM, no mesmo formato. A base é validada antes de substituir a atual; em seguida o
            modelo reaprende, disputa com a versão vigente no teste em datas passadas e os scores são recalculados.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <UploadForm needsToken={!!process.env.LEAD_SCORER_ADMIN_TOKEN} usingUpload={v.source === "upload"} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Histórico de versões</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Versão</TableHead>
                <TableHead>Base até</TableHead>
                <TableHead className="text-right">Oportunidades</TableHead>
                <TableHead className="text-right">Erro</TableHead>
                <TableHead className="text-right">Receita no topo</TableHead>
                <TableHead>Configuração</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {s.versions.map((ver) => (
                <TableRow key={ver.version}>
                  <TableCell className="font-medium">v{ver.version}</TableCell>
                  <TableCell>{ver.refDay}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtInt(ver.deals)}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtDec(ver.calibratedBrier)}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtPct(ver.capture, 1)}</TableCell>
                  <TableCell className="max-w-72 truncate text-muted-foreground">{ver.configKey}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

function Info({ label, value, className }: { label: string; value: string; className?: string }) {
  return (
    <div className={cn("flex flex-col gap-0.5", className)}>
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  )
}

function StateRow({ label, rule, days }: { label: string; rule: string; days: string }) {
  return (
    <TableRow>
      <TableCell className="font-medium">{label}</TableCell>
      <TableCell className="text-muted-foreground">{rule}</TableCell>
      <TableCell className="text-right tabular-nums">{days}</TableCell>
    </TableRow>
  )
}
