import { createHash } from "node:crypto"
import { mkdir, readFile, rm, writeFile } from "node:fs/promises"
import path from "node:path"

import { type Backtest, runBacktest } from "@/lib/scoring/backtest"
import { type Dataset, type RawFiles, formatDay, prepareDataset } from "@/lib/scoring/dataset"
import { type Config, type LevelFit, type Model, type ScoredDeal, fitModel, scorePipeline } from "@/lib/scoring/model"

/*
 * Estado do sistema: lê a base (CSVs do CRM), reaprende o modelo quando a base muda
 * e guarda o histórico de versões. Base padrão em ./data; uploads e versões em ./storage.
 */

const DATA_DIR = process.env.LEAD_SCORER_DATA_DIR ?? path.join(process.cwd(), "data")
const STORAGE_DIR = process.env.LEAD_SCORER_STORAGE_DIR ?? path.join(process.cwd(), "storage")
const UPLOAD_DIR = path.join(STORAGE_DIR, "base")
const VERSIONS_FILE = path.join(STORAGE_DIR, "versions.json")
export const FILE_NAMES = ["accounts", "products", "sales_teams", "sales_pipeline"] as const

export interface ModelVersion {
  version: number
  createdAt: string
  fingerprint: string
  refDay: string
  config: Config
  configKey: string
  brier: number
  calibratedBrier: number
  capture: number
  baseline: { brier: number; capture: number }
  promoted: boolean
  reason: string
  deals: number
  closed: number
  source: "padrão" | "upload"
}

export interface AppState {
  ds: Dataset
  model: Model
  groupDiagnostics: LevelFit[] // pesos aprendidos por grupo, mesmo quando o backtest descarta os grupos
  backtest: Backtest
  scored: ScoredDeal[]
  byId: Map<string, ScoredDeal>
  version: ModelVersion
  versions: ModelVersion[]
  persisted: boolean
}

async function readBase(): Promise<{ files: RawFiles; source: ModelVersion["source"] }> {
  const read = (dir: string) =>
    Promise.all(FILE_NAMES.map((f) => readFile(path.join(dir, `${f}.csv`), "utf8"))).then(
      (texts) => Object.fromEntries(FILE_NAMES.map((f, i) => [f, texts[i]])) as unknown as RawFiles,
    )
  try {
    return { files: await read(UPLOAD_DIR), source: "upload" }
  } catch {
    return { files: await read(DATA_DIR), source: "padrão" }
  }
}

async function readVersions(): Promise<ModelVersion[]> {
  try {
    return JSON.parse(await readFile(VERSIONS_FILE, "utf8"))
  } catch {
    return []
  }
}

let memoryVersions: ModelVersion[] | null = null
let cache: { fingerprint: string; state: AppState } | null = null
let building: { fingerprint: string; promise: Promise<AppState> } | null = null

async function build(files: RawFiles, source: ModelVersion["source"], fingerprint: string): Promise<AppState> {
  const ds = prepareDataset(files)
  const versions = memoryVersions ?? (await readVersions())
  const known = versions.find((v) => v.fingerprint === fingerprint)
  const last = versions.at(-1)
  // Base já vista: mantém a configuração daquela versão. Base nova: candidata disputa com a vigente.
  const backtest = runBacktest(ds, known?.config ?? last?.config ?? null)
  const config = known ? known.config : backtest.chosen.config
  const model = fitModel(ds, ds.refDay, config)
  const scored = scorePipeline(ds, model, backtest.calibrator)

  let version = known
  let persisted = true
  if (!version) {
    version = {
      version: (last?.version ?? 0) + 1,
      createdAt: new Date().toISOString(),
      fingerprint,
      refDay: formatDay(ds.refDay),
      config,
      configKey: backtest.chosen.key,
      brier: backtest.chosen.brier,
      calibratedBrier: backtest.calibratedBrier,
      capture: backtest.chosen.capture,
      baseline: backtest.baseline,
      promoted: backtest.promoted,
      reason: backtest.reason,
      deals: ds.deals.length,
      closed: model.counts.closed,
      source,
    }
    versions.push(version)
    try {
      await mkdir(STORAGE_DIR, { recursive: true })
      await writeFile(VERSIONS_FILE, JSON.stringify(versions, null, 2))
      memoryVersions = null
    } catch {
      memoryVersions = versions // disco somente leitura: mantém o histórico em memória
      persisted = false
    }
  }

  return {
    ds,
    model,
    groupDiagnostics: fitModel(ds, ds.refDay, { ...config, levels: "completo" }).levels,
    backtest,
    scored,
    byId: new Map(scored.map((s) => [s.deal.id, s])),
    version,
    versions: [...versions].reverse(),
    persisted,
  }
}

export async function getState(): Promise<AppState> {
  const { files, source } = await readBase()
  const fingerprint = createHash("sha1").update(JSON.stringify(files)).digest("hex")
  if (cache?.fingerprint === fingerprint) return cache.state
  if (building?.fingerprint !== fingerprint) {
    const promise = build(files, source, fingerprint)
    building = { fingerprint, promise }
    promise.then(
      (state) => {
        cache = { fingerprint, state }
        if (building?.promise === promise) building = null
      },
      () => {
        if (building?.promise === promise) building = null
      },
    )
  }
  return building!.promise
}

// Valida antes de gravar: uma base inválida nunca substitui a vigente.
export async function saveBase(files: RawFiles): Promise<AppState> {
  prepareDataset(files)
  await mkdir(UPLOAD_DIR, { recursive: true })
  await Promise.all(FILE_NAMES.map((f) => writeFile(path.join(UPLOAD_DIR, `${f}.csv`), files[f])))
  return getState()
}

export async function restoreDefaultBase(): Promise<AppState> {
  await rm(UPLOAD_DIR, { recursive: true, force: true })
  return getState()
}
