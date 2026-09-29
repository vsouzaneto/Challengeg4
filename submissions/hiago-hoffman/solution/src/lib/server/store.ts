import { createHash } from "node:crypto"
import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises"
import path from "node:path"

import { type Backtest, configKey, runBacktest } from "@/lib/scoring/backtest"
import { type Conversion, type Snapshot, learnConversion, snapshotOf } from "@/lib/scoring/conversion"
import { type Dataset, type RawFiles, formatDay, prepareDataset } from "@/lib/scoring/dataset"
import { type Config, LEVELS, type LevelFit, type Model, type ScoredDeal, fitModel, scorePipeline } from "@/lib/scoring/model"

/*
 * Estado do sistema: lê a base (CSVs do CRM), reaprende o modelo quando a base muda
 * e guarda o histórico de versões. Base padrão em ./data; uploads e versões em ./storage.
 */

const DATA_DIR = process.env.LEAD_SCORER_DATA_DIR ?? path.join(process.cwd(), "data")
const STORAGE_DIR = process.env.LEAD_SCORER_STORAGE_DIR ?? path.join(process.cwd(), "storage")
const UPLOAD_DIR = path.join(STORAGE_DIR, "base")
const VERSIONS_FILE = path.join(STORAGE_DIR, "versions.json")
const SNAPSHOTS_DIR = path.join(STORAGE_DIR, "snapshots") // uma foto de estágios por base, para aprender c
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
  K?: number | null // referência da escala do score nesta versão
  conversion?: number // c vigente quando a versão foi criada
}

export interface AppState {
  ds: Dataset
  model: Model
  groupDiagnostics: LevelFit[] // pesos aprendidos por grupo, mesmo quando o backtest descarta os grupos
  backtest: Backtest
  scored: ScoredDeal[]
  K: number | null
  conversion: Conversion
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

async function readSnapshots(): Promise<Snapshot[]> {
  try {
    const names = (await readdir(SNAPSHOTS_DIR)).filter((n) => n.endsWith(".json"))
    return Promise.all(names.map(async (n) => JSON.parse(await readFile(path.join(SNAPSHOTS_DIR, n), "utf8"))))
  } catch {
    return []
  }
}

const memorySnapshots: Snapshot[] = []
let memoryVersions: ModelVersion[] | null = null
let cache: { fingerprint: string; state: AppState } | null = null
let building: { fingerprint: string; promise: Promise<AppState> } | null = null

async function build(files: RawFiles, source: ModelVersion["source"], fingerprint: string): Promise<AppState> {
  const ds = prepareDataset(files)
  const versions = memoryVersions ?? (await readVersions())
  const known = versions.find((v) => v.fingerprint === fingerprint)
  const last = versions.at(-1)
  // Base já vista: mantém a configuração daquela versão. Base nova: candidata disputa com a vigente.
  // Versões gravadas com um formato de configuração antigo são ignoradas.
  const valid = (c?: Config) => (c && Array.isArray(c.levels) && c.urgency ? c : null)
  const backtest = runBacktest(ds, valid(known?.config) ?? valid(last?.config))
  const config = valid(known?.config) ?? backtest.chosen.config
  const model = fitModel(ds, ds.refDay, config)

  const snapshot = snapshotOf(ds, fingerprint)
  const stored = [...(await readSnapshots()), ...memorySnapshots]
  const conversion = learnConversion([...stored.filter((x) => x.fingerprint !== fingerprint), snapshot])
  if (!stored.some((x) => x.fingerprint === fingerprint)) {
    try {
      await mkdir(SNAPSHOTS_DIR, { recursive: true })
      await writeFile(path.join(SNAPSHOTS_DIR, `${fingerprint}.json`), JSON.stringify(snapshot))
    } catch {
      memorySnapshots.push(snapshot)
    }
  }
  const { deals: scored, K } = scorePipeline(ds, model, { calibrator: backtest.calibrator, conversion: conversion.c })

  let version = known
  let persisted = true
  if (!version) {
    version = {
      version: (last?.version ?? 0) + 1,
      createdAt: new Date().toISOString(),
      fingerprint,
      refDay: formatDay(ds.refDay),
      config,
      configKey: configKey(config),
      brier: backtest.chosen.brier,
      calibratedBrier: backtest.calibratedBrier,
      capture: backtest.chosen.capture,
      baseline: backtest.baseline,
      promoted: backtest.promoted,
      reason: backtest.reason,
      deals: ds.deals.length,
      closed: model.counts.closed,
      source,
      K,
      conversion: conversion.c,
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
    groupDiagnostics: fitModel(ds, ds.refDay, { ...config, levels: LEVELS.map((l) => l.id) }).levels,
    backtest,
    scored,
    K,
    conversion,
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
