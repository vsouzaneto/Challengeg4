// Rodar: npm test  (node --test, sem dependências)
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { join } from "node:path"
import { runBacktest } from "./backtest.ts"
import { learnConversion } from "./conversion.ts"
import { parseCsv } from "./csv.ts"
import { formatDay, prepareDataset, type Deal } from "./dataset.ts"
import { type Config, LEVELS, calibrate, fitCalibrator, fitModel, hasHistory, scoreDeal, scorePipeline } from "./model.ts"

const dir = join(import.meta.dirname, "../../../data")
const read = (f: string) => readFileSync(join(dir, f), "utf8")
const ds = prepareDataset({
  accounts: read("accounts.csv"),
  products: read("products.csv"),
  sales_teams: read("sales_teams.csv"),
  sales_pipeline: read("sales_pipeline.csv"),
})
const allGroups: Config = { halfLife: null, seriesPrior: null, levels: LEVELS.map((l) => l.id), urgency: { lambda: 0, horizonDays: 14 } }
const model = fitModel(ds, ds.refDay, allGroups)
const deal = (over: Partial<Deal>): Deal => ({
  id: "X", stage: "Engaging", agent: "Vendedor Novo", manager: null, region: null, product: "Produto Novo",
  series: null, price: 1000, account: null, engage: ds.refDay - 30, close: null, closeValue: null, outcome: null, ...over,
})

test("CSV: aspas, vírgula e aspas escapadas", () => {
  assert.deepEqual(parseCsv('a,b\n"x, y","diz ""oi"""\n'), [{ a: "x, y", b: 'diz "oi"' }])
})

test("base: grafia de produto normalizada e data de referência", () => {
  assert.equal(ds.deals.length, 8800)
  assert.equal(formatDay(ds.refDay), "2017-12-31")
  assert.equal(ds.deals.filter((d) => d.product === "GTXPro").length, 0)
  assert.equal(ds.issues.find((i) => i.id === "conta")?.count, 1425)
})

test("curva de sobrevivência bate com a análise em Python", () => {
  const p = model.curves.global.pFrom
  assert.ok(Math.abs(p[0] - 0.519) < 0.002, `p(0)=${p[0]}`)
  assert.ok(Math.abs(p[Math.floor(90 / 7)] - 0.388) < 0.002, `p(90d)=${p[12]}`)
  assert.equal(model.curves.global.lastEventWeek, 19)
})

test("limiares das situações aprendidos", () => {
  const t = model.thresholds.global
  assert.deepEqual([t.inicio, t.andamento, t.esfriando, t.tardio], [14, 88, 116, 130])
})

test("fator da situação: mesmo método para todas e decrescente com o tempo", () => {
  const s = model.situations.global
  const order = [s.inicio.p, s.andamento.p, s.esfriando.p, s.tardio.p, s.fora.p]
  assert.ok(order.every((p, i) => p > 0 && (i === 0 || p <= order[i - 1])), order.join(" > "))
  // Revalidar vem da cauda: nenhum ganho depois da semana 19 entre 1.273 deals
  assert.ok(Math.abs(model.curves.global.tailP[20] - 1 / (1273 + 2)) < 1e-9)
})

test("encolhimento: dimensões sem sinal ficam com peso zero", () => {
  for (const id of ["serie", "produto", "regiao", "manager"]) {
    assert.equal(model.levels.find((l) => l.id === id)?.k, null, id)
  }
})

test("entidade nova herda o nível acima, sem erro nem chance zero", () => {
  const s = scoreDeal(deal({}), model, ds.refDay)
  assert.ok(s.p > 0.3 && s.p < 0.7, `p=${s.p}`)
  assert.ok(!s.factors.some((f) => /vendedor|produto/.test(f.level) && f.factor !== 1))
  assert.ok(s.flags.includes("sem_conta"))
})

test("um score só: prioridade = valor × chance × urgência para todo deal aberto", () => {
  const { deals } = scorePipeline(ds, model, { conversion: 0.5 })
  for (const s of deals.filter((x) => x.priority !== null)) {
    assert.ok(Math.abs(s.priority! - s.value! * s.p * s.urgency.factor) < 1e-9)
    assert.ok(s.score !== null && s.score >= 0 && s.score <= 100)
  }
  const fora = deals.filter((x) => x.state === "fora")
  assert.ok(fora.length > 1200 && fora.every((x) => x.score !== null && x.p > 0))
})

test("Prospecting: chance de Início × conversão; não passa dos engajados nem trava em 100", () => {
  const { deals } = scorePipeline(ds, model, { conversion: 0.5 })
  const prosp = deals.filter((s) => s.state === "entrada")
  const live = deals.filter((s) => s.state !== "fora" && s.state !== "entrada")
  assert.ok(Math.max(...prosp.map((s) => s.p)) < Math.max(...live.map((s) => s.p)))
  assert.ok(prosp.every((s) => s.score! < 100 && s.situation.conversion === 0.5))
})

test("escala do score: prioridade igual a K vale 50, o triplo vale 75", () => {
  const { deals, K } = scorePipeline(ds, model, { conversion: 0.5 })
  const score = (r: number) => Math.round((100 * r) / (r + K!))
  assert.equal(score(K!), 50)
  assert.equal(score(3 * K!), 75)
  const s = deals.find((x) => x.priority !== null)!
  assert.equal(s.score, score(s.priority!))
})

test("relacionamento: histórico conta só compras anteriores à entrada; sem conta é neutro", () => {
  const ctx = { firstWin: new Map([["Acme", 100]]), at: 500 }
  assert.equal(hasHistory(deal({ account: "Acme", engage: 150 }), ctx), true)
  assert.equal(hasHistory(deal({ account: "Acme", engage: 90 }), ctx), false)
  assert.equal(hasHistory(deal({ account: "Nova", engage: 150 }), ctx), false)
  assert.equal(hasHistory(deal({ account: null }), ctx), null)
})

test("calibração isotônica: monotônica e não infla chances muito pequenas", () => {
  const pts = [
    ...Array.from({ length: 500 }, () => ({ p: 0.002, y: 0 })),
    ...Array.from({ length: 500 }, (_, i) => ({ p: 0.4, y: i % 3 === 0 ? 1 : 0 })),
    ...Array.from({ length: 500 }, (_, i) => ({ p: 0.7, y: i % 2 })),
  ]
  const cal = fitCalibrator(pts)
  const xs = [0.001, 0.002, 0.1, 0.4, 0.55, 0.7, 0.9].map((p) => calibrate(p, cal))
  assert.ok(xs.every((v, i) => i === 0 || v >= xs[i - 1]))
  assert.ok(calibrate(0.002, cal) < 0.005)
})

test("conversão Prospecting → Engaging aprendida entre bases", () => {
  assert.equal(learnConversion([]).c, 0.5)
  const antes = { fingerprint: "a", refDay: 1, prospecting: ["p1", "p2", "p3", "p4"], engaged: [] }
  const depois = { fingerprint: "b", refDay: 2, prospecting: ["p4"], engaged: ["p1", "p2"] } // p3 sumiu, p4 pendente
  const conv = learnConversion([depois, antes])
  assert.deepEqual([conv.converted, conv.failed], [2, 1])
  assert.equal(conv.c, 3 / 5)
})

test("backtest: cada grupo testado sozinho e escolha nunca pior que a melhor base", () => {
  const bt = runBacktest(ds, null)
  assert.equal(bt.levelTests.length, LEVELS.length)
  const bestBase = Math.max(...bt.bases.map((b) => b.capture))
  assert.ok(bt.chosen.capture >= bestBase - 1e-9)
  assert.ok(bt.chosen.capture > bt.baseline.capture)
  for (const t of bt.levelTests) assert.equal(t.included, bt.chosen.config.levels.includes(t.id))
})
