// Rodar: npm test  (node --test, sem dependências)
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { join } from "node:path"
import { parseCsv } from "./csv.ts"
import { formatDay, prepareDataset, type Deal } from "./dataset.ts"
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

test("pipeline: deals fora do histórico não recebem score; score é percentil 0–100", () => {
  const scored = scorePipeline(ds, model)
  const fora = scored.filter((s) => s.state === "fora")
  assert.ok(fora.length > 1200 && fora.every((s) => s.score === null))
  const withScore = scored.filter((s) => s.score !== null)
  assert.ok(withScore.every((s) => s.score! >= 0 && s.score! <= 100))
  assert.equal(Math.max(...withScore.map((s) => s.score!)), 100)
})
