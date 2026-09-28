import type { Dataset } from "./dataset.ts"

/*
 * Conversão Prospecting → Engaging (c), aprendida comparando fotos sucessivas da base.
 * Um deal que estava sem data de entrada numa foto e aparece com data de entrada na seguinte
 * converteu; se sumiu ou foi encerrado sem entrar, não converteu; se continua igual, ainda não se sabe.
 * c = (convertidos + 1) / (resolvidos + 2): sem nenhuma observação, 50% (estimativa neutra).
 */

export interface Snapshot {
  fingerprint: string
  refDay: number
  prospecting: string[] // abertos sem data de entrada
  engaged: string[] // com data de entrada (abertos ou encerrados)
}

export interface Conversion {
  c: number
  converted: number
  failed: number
  snapshots: number
}

export function snapshotOf(ds: Dataset, fingerprint: string): Snapshot {
  return {
    fingerprint,
    refDay: ds.refDay,
    prospecting: ds.deals.filter((d) => d.engage === null && d.outcome === null).map((d) => d.id),
    engaged: ds.deals.filter((d) => d.engage !== null).map((d) => d.id),
  }
}

export function learnConversion(snapshots: Snapshot[]): Conversion {
  // Uma foto por data de referência; a mais recente de cada data prevalece.
  const byDay = new Map(snapshots.map((s) => [s.refDay, s]))
  const ordered = [...byDay.values()].sort((a, b) => a.refDay - b.refDay)
  const resolved = new Map<string, boolean>()
  for (let i = 0; i + 1 < ordered.length; i++) {
    const next = ordered[i + 1]
    const stillProspecting = new Set(next.prospecting)
    const engaged = new Set(next.engaged)
    for (const id of ordered[i].prospecting) {
      if (resolved.has(id)) continue
      if (engaged.has(id)) resolved.set(id, true)
      else if (!stillProspecting.has(id)) resolved.set(id, false)
    }
  }
  let converted = 0
  for (const ok of resolved.values()) if (ok) converted++
  const failed = resolved.size - converted
  return { c: (converted + 1) / (resolved.size + 2), converted, failed, snapshots: ordered.length }
}
