// Rodar: npm test  (node --test, sem dependências)
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { join } from "node:path"
import { parseCsv } from "./csv.ts"
import { formatDay, prepareDataset, type Deal } from "./dataset.ts"
import { learnConversion } from "./conversion.ts"
import { fitModel, scoreDeal, scorePipeline } from "./model.ts"

const dir = join(import.meta.dirname, "../../../data")
const read = (f: string) => readFileSync(join(dir, f), "utf8")
const ds = prepareDataset({
  accounts: read("accounts.csv"),
  products: read("products.csv"),
  sales_teams: read("sales_teams.csv"),
  sales_pipeline: read("sales_pipeline.csv"),
})
const noRecency = { halfLife: null, seriesPrior: null, levels: "completo" } as const
const model = fitModel(ds, ds.refDay, noRecency)

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

test("limiares de idade aprendidos", () => {
  const t = model.thresholds.global
  assert.deepEqual([t.inicio, t.andamento, t.esfriando, t.tardio], [14, 88, 116, 130])
})

test("encolhimento: dimensões sem sinal ficam com peso zero", () => {
  for (const id of ["serie", "produto", "regiao", "manager"]) {
    assert.equal(model.levels.find((l) => l.id === id)?.k, null, id)
  }
  assert.ok(model.levels.find((l) => l.id === "vendedor")!.k! > 100)
})

test("entidade nova herda o nível acima, sem erro nem chance zero", () => {
  const novo: Deal = {
    id: "X", stage: "Engaging", agent: "Vendedor Novo", manager: null, region: null,
    product: "Produto Novo", series: null, price: 1000, account: null,
    engage: ds.refDay - 30, close: null, closeValue: null, outcome: null,
  }
  const s = scoreDeal(novo, model, ds.refDay)
  assert.ok(s.p! > 0.3 && s.p! < 0.7)
  assert.ok(!s.adjustments.some((a) => a.level.includes("vendedor") || a.level.includes("produto")))
  assert.ok(s.flags.includes("sem_conta"))
})

test("Revalidar também tem score: chance da cauda pequena e que não sobe com a idade", () => {
  const { deals } = scorePipeline(ds, model, { conversion: 0.5 })
  const fora = deals.filter((s) => s.state === "fora")
  assert.ok(fora.length > 1200)
  const tail = model.curves.global.tailP
  const boundary = tail[Math.floor(model.thresholds.global.tardio / 7)] // chance na fronteira do histórico
  assert.ok(fora.every((s) => s.score !== null && s.p! > 0 && s.p! <= boundary))
  assert.ok(tail.every((p, k) => k === 0 || p <= tail[k - 1]))
  // Hoje: nenhum ganho depois da semana 19 entre 1.273 deals → (0 + 1) / (1.273 + 2)
  assert.ok(Math.abs(tail[20] - 1 / (1273 + 2)) < 1e-9)
})

test("Prospecting: conversão aplicada; não fica acima dos deals engajados nem trava em 100", () => {
  const { deals } = scorePipeline(ds, model, { conversion: 0.5 })
  const prosp = deals.filter((s) => s.state === "entrada")
  const live = deals.filter((s) => s.state !== "fora" && s.state !== "entrada")
  assert.ok(Math.max(...prosp.map((s) => s.p!)) < Math.max(...live.map((s) => s.p!)))
  assert.ok(prosp.every((s) => s.score! < 100))
})

test("escala do score: receita esperada igual a K vale 50, o triplo vale 75", () => {
  const { deals, K } = scorePipeline(ds, model, { conversion: 0.5 })
  assert.ok(K! > 0)
  const s = deals.find((x) => x.expected !== null)!
  const score = (r: number) => Math.round((100 * r) / (r + K!))
  assert.equal(score(K!), 50)
  assert.equal(score(3 * K!), 75)
  assert.equal(s.score, score(s.expected!))
  assert.ok(deals.every((x) => x.score === null || (x.score >= 0 && x.score <= 100)))
})

test("conversão Prospecting → Engaging aprendida entre bases", () => {
  assert.equal(learnConversion([]).c, 0.5)
  const antes = { fingerprint: "a", refDay: 1, prospecting: ["p1", "p2", "p3", "p4"], engaged: [] }
  const depois = { fingerprint: "b", refDay: 2, prospecting: ["p4"], engaged: ["p1", "p2"] } // p3 sumiu, p4 pendente
  const conv = learnConversion([depois, antes])
  assert.deepEqual([conv.converted, conv.failed], [2, 1])
  assert.equal(conv.c, 3 / 5)
})
