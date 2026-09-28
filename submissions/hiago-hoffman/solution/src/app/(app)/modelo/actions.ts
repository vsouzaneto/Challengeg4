"use server"

import { revalidatePath } from "next/cache"

import { DataError, type RawFiles } from "@/lib/scoring/dataset"
import { FILE_NAMES, restoreDefaultBase, saveBase } from "@/lib/server/store"

export type UploadResult = { ok: true; message: string } | { ok: false; error: string } | null

const MAX_BYTES = 50 * 1024 * 1024

// Se LEAD_SCORER_ADMIN_TOKEN estiver definido, só quem tem o token troca a base.
function authorized(form: FormData) {
  const token = process.env.LEAD_SCORER_ADMIN_TOKEN
  return !token || form.get("token") === token
}

export async function atualizarBase(_prev: UploadResult, form: FormData): Promise<UploadResult> {
  if (!authorized(form)) return { ok: false, error: "Token de administrador inválido." }
  const files: Partial<RawFiles> = {}
  for (const name of FILE_NAMES) {
    const file = form.get(name)
    if (!(file instanceof File) || file.size === 0) return { ok: false, error: `Selecione o arquivo ${name}.csv.` }
    if (!file.name.toLowerCase().endsWith(".csv")) return { ok: false, error: `${file.name} não é um arquivo .csv.` }
    if (file.size > MAX_BYTES) return { ok: false, error: `${file.name} passa do limite de 50 MB.` }
    files[name] = await file.text()
  }
  try {
    const state = await saveBase(files as RawFiles)
    revalidatePath("/", "layout")
    const v = state.version
    return {
      ok: true,
      message: `Base carregada: ${state.ds.deals.length} oportunidades até ${v.refDay}. Modelo v${v.version}: ${v.reason}`,
    }
  } catch (e) {
    if (e instanceof DataError) return { ok: false, error: e.message }
    console.error(e)
    return { ok: false, error: e instanceof Error ? e.message : "Falha ao processar a base." }
  }
}

export async function restaurarBase(_prev: UploadResult, form: FormData): Promise<UploadResult> {
  if (!authorized(form)) return { ok: false, error: "Token de administrador inválido." }
  const state = await restoreDefaultBase()
  revalidatePath("/", "layout")
  return { ok: true, message: `Base padrão restaurada. Modelo v${state.version.version}.` }
}
