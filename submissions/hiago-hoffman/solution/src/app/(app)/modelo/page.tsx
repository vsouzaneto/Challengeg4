import type { Metadata } from "next"

import { PageHeader } from "@/components/page-header"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { STATE_META, fmtChance, fmtDec, fmtInt, fmtMoney, fmtPct } from "@/lib/explain"
import { formatDay } from "@/lib/scoring/dataset"
import { FACTOR_LABEL, type FactorKind, LEVELS, POLICY, type Situation, calibrate } from "@/lib/scoring/model"
import { getState } from "@/lib/server/store"
import { cn } from "@/lib/utils"
import { UploadForm } from "./upload-form"

export const metadata: Metadata = { title: "Modelo e base" }
// Lê o estado vivo (base e versões): nunca pré-renderizar no build.
export const dynamic = "force-dynamic"

const SITUATIONS: Situation[] = ["inicio", "andamento", "esfriando", "tardio", "fora"]
const KINDS: FactorKind[] = ["afinidade", "relacionamento", "produto", "time", "calendario"]
const IMPACT_LABEL = { bloqueia: "Impede o score", tarefa: "Vira pendência", info: "Informativo" }

export default async function ModeloPage() {
  const s = await getState()
  const { model, backtest: bt, version: v } = s
  const conv = s.conversion
  const cfg = model.config
  const base = bt.bases.reduce((best, r) => (r.capture > best.capture ? r : best))
  const bestUrgency = [...bt.urgencyTests].sort((a, b) => b.capture - a.capture)[0]

  return (
    <div className="flex max-w-5xl flex-col gap-6">
      <PageHeader
        title="Modelo e base"
        description="Um score para todas as oportunidades. A estrutura da fórmula é fixa; cada fator é reaprendido e testado sempre que a base muda."
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
            <Info label="Configuração" value={v.configKey} className="sm:col-span-3" />
            <Info label="Escala do score (K)" value={s.K === null ? "—" : `${fmtMoney(s.K)}: prioridade mediana dos deals vivos = score 50`} className="sm:col-span-2" />
            <Info label="Treinado em" value={new Date(v.createdAt).toISOString().slice(0, 16).replace("T", " ")} />
          </dl>
          {!s.persisted && <p className="mt-3 text-xs text-muted-foreground">Disco somente leitura: o histórico de versões está só em memória.</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>A fórmula</CardTitle>
          <CardDescription>
            Prioridade = Valor × Situação × Afinidade × Relacionamento × Produto × Time × Calendário × Urgência. Score = 100 ×
            Prioridade ÷ (Prioridade + K). Fator sem sinal nos dados vale ×1,00 e sobe sozinho quando a base mostrar efeito.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fator</TableHead>
                <TableHead>Como é aprendido</TableHead>
                <TableHead>Nesta versão</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <FormulaRow name="Valor" how="Preço de tabela × razão histórica entre valor fechado e preço" now={`× ${fmtDec(model.rho.mean)} em média`} />
              <FormulaRow
                name="Situação"
                how="Chance de ganho dos deals da base que passaram por cada situação (curva de sobrevivência, calibrada)"
                now="Tabela abaixo"
              />
              <FormulaRow
                name="Conversão de Prospecting"
                how="Comparando uploads sucessivos: (convertidos + 1) ÷ (acompanhados + 2)"
                now={`${fmtPct(conv.c)} · ${conv.converted + conv.failed === 0 ? "sem deals acompanhados ainda" : `${fmtInt(conv.converted)} de ${fmtInt(conv.converted + conv.failed)}`} · ${fmtInt(conv.snapshots)} ${conv.snapshots === 1 ? "base" : "bases"}`}
              />
              {KINDS.map((kind) => {
                const levels = LEVELS.filter((l) => l.kind === kind)
                const inUse = levels.filter((l) => cfg.levels.includes(l.id))
                return (
                  <FormulaRow
                    key={kind}
                    name={FACTOR_LABEL[kind]}
                    how="Diferença de conversão do grupo, com peso n ÷ (n + k); só entra se o teste mostrar ganho de receita"
                    now={inUse.length ? `Em uso: ${inUse.map((l) => l.label).join(", ")}` : "Fora: não aumentou a receita capturada"}
                  />
                )
              })}
              <FormulaRow
                name="Urgência"
                how="1 + força × queda prevista da chance na janela; força e janela escolhidas pelo teste"
                now={cfg.urgency.lambda > 0 ? `Força ${fmtDec(cfg.urgency.lambda, 1)} em ${cfg.urgency.horizonDays} dias` : "Desligada: não aumentou a receita capturada"}
              />
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Fator da situação</CardTitle>
          <CardDescription>Os dias de cada situação e a chance são reaprendidos a cada base. Prospecting = Início × conversão.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Situação</TableHead>
                <TableHead>Dias desde a entrada</TableHead>
                <TableHead className="text-right">Chance de ganho</TableHead>
                <TableHead className="text-right">Deals que chegaram lá</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">{STATE_META.entrada.label}</TableCell>
                <TableCell className="text-muted-foreground">sem data de entrada</TableCell>
                <TableCell className="text-right tabular-nums">
                  {fmtChance(calibrate(model.situations.global.inicio.p, bt.calibrator) * conv.c)}
                </TableCell>
                <TableCell className="text-right text-muted-foreground">—</TableCell>
              </TableRow>
              {SITUATIONS.map((sit) => {
                const row = model.situations.global[sit]
                return (
                  <TableRow key={sit}>
                    <TableCell className="font-medium">{STATE_META[sit].label}</TableCell>
                    <TableCell>{row.toDays === null ? `mais de ${row.fromDays}` : `${Math.round(row.fromDays)}–${row.toDays}`}</TableCell>
                    <TableCell className="text-right tabular-nums">{fmtChance(calibrate(row.p, bt.calibrator))}</TableCell>
                    <TableCell className="text-right tabular-nums">{fmtInt(row.reached)}</TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Teste em datas passadas</CardTitle>
          <CardDescription>
            Em cada fim de mês de {formatDay(bt.cutoffs[0])} a {formatDay(bt.cutoffs.at(-1)!)}, o modelo só enxergou o que se sabia
            naquela data e foi avaliado pelo que aconteceu depois. Critério principal: receita ganha que estava nos{" "}
            {fmtPct(POLICY.topShare)} primeiros da lista (deals maiores pesam mais). O erro de probabilidade desempata.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Etapa</TableHead>
                <TableHead className="text-right">Receita no topo</TableHead>
                <TableHead className="text-right">Erro de probabilidade</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <ResultRow label="Sem modelo: taxa histórica e ordenação só por preço" capture={bt.baseline.capture} brier={bt.baseline.brier} muted />
              <ResultRow label={`Situação, sem grupos (${base.key.split(" · grupos")[0]})`} capture={base.capture} brier={base.brier} />
              <ResultRow label="Configuração em uso" capture={bt.chosen.capture} brier={bt.chosen.brier} strong />
            </TableBody>
          </Table>
          <p className="text-sm text-muted-foreground">
            Depois da calibração, o erro da configuração em uso fica em {fmtDec(bt.calibratedBrier)} (medido deixando cada mês de
            fora do ajuste).
          </p>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Grupo testado sozinho</TableHead>
                <TableHead className="text-right">Receita no topo</TableHead>
                <TableHead className="text-right">Erro</TableHead>
                <TableHead>Resultado</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {bt.levelTests.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{t.label}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtPct(t.capture, 1)}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtDec(t.brier)}</TableCell>
                  <TableCell>{t.included ? <Badge>entra</Badge> : <span className="text-muted-foreground">fora</span>}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <p className="text-sm text-muted-foreground">
            Referência sem grupos: {fmtPct(base.capture, 1)}. Um grupo entra se capturar pelo menos essa receita.
          </p>

          <p className="text-sm text-muted-foreground">
            Urgência: {bt.urgencyTests.length} combinações de força ({POLICY.candidates.urgencyLambda.map((l) => fmtDec(l, 1)).join("; ")}) e janela (
            {POLICY.candidates.urgencyHorizonDays.join(", ")} dias). Melhor: força {fmtDec(bestUrgency.config.urgency.lambda, 1)} em{" "}
            {bestUrgency.config.urgency.horizonDays} dias, com {fmtPct(bestUrgency.capture, 1)} da receita no topo.{" "}
            {cfg.urgency.lambda > 0 ? "Ficou acima da versão sem urgência e está em uso." : "Não superou a versão sem urgência, então fica desligada."}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Peso aprendido por grupo</CardTitle>
          <CardDescription>
            Cada grupo só ganha peso se variar mais do que o acaso explicaria. Nenhum nome é regra fixa: vendedor, produto, região
            ou cliente novos começam com peso zero e herdam o nível acima.
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
            modelo reaprende, disputa com a versão vigente no teste em datas passadas e os scores são recalculados. Cada upload também
            ensina a conversão de Prospecting.
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
                <TableHead className="text-right">Receita no topo</TableHead>
                <TableHead className="text-right">Erro</TableHead>
                <TableHead>Configuração</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {s.versions.map((ver) => (
                <TableRow key={ver.version}>
                  <TableCell className="font-medium">v{ver.version}</TableCell>
                  <TableCell>{ver.refDay}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtInt(ver.deals)}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtPct(ver.capture, 1)}</TableCell>
                  <TableCell className="text-right tabular-nums">{fmtDec(ver.calibratedBrier)}</TableCell>
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

function FormulaRow({ name, how, now }: { name: string; how: string; now: string }) {
  return (
    <TableRow>
      <TableCell className="font-medium whitespace-normal">{name}</TableCell>
      <TableCell className="whitespace-normal text-muted-foreground">{how}</TableCell>
      <TableCell className="whitespace-normal">{now}</TableCell>
    </TableRow>
  )
}

function ResultRow({ label, capture, brier, muted, strong }: { label: string; capture: number; brier: number; muted?: boolean; strong?: boolean }) {
  return (
    <TableRow className={cn(strong && "bg-muted/60 font-medium")}>
      <TableCell className={cn("whitespace-normal", muted && "text-muted-foreground")}>{label}</TableCell>
      <TableCell className="text-right tabular-nums">{fmtPct(capture, 1)}</TableCell>
      <TableCell className="text-right tabular-nums">{fmtDec(brier)}</TableCell>
    </TableRow>
  )
}
