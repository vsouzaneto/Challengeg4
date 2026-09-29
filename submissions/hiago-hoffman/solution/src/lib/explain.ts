import type { AgeState } from "@/lib/scoring/model"

// Textos e rótulos derivados dos componentes do cálculo. Nenhum número é escrito à mão:
// limiares e percentuais vêm do modelo treinado.

// Formatação manual (sem Intl): servidor e navegador podem ter ICU diferentes e quebrar a hidratação.
export const fmtInt = (n: number) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")
const oneDecimal = (n: number) => n.toFixed(1).replace(/\.0$/, "").replace(".", ",")

export function fmtMoney(v: number | null) {
  if (v === null) return "—"
  const a = Math.abs(v)
  if (a >= 1e6) return `US$ ${oneDecimal(v / 1e6)} mi`
  if (a >= 1e3) return `US$ ${oneDecimal(v / 1e3)} mil`
  return `US$ ${Math.round(v)}`
}
export const fmtMoneyFull = (v: number | null) => (v === null ? "—" : `US$ ${fmtInt(v)}`)
export const fmtPct = (p: number | null, digits = 0) => (p === null ? "—" : `${(p * 100).toFixed(digits).replace(".", ",")}%`)
// Chances pequenas com duas casas, para "0,08%" não virar "0%".
export const fmtChance = (p: number | null) => (p !== null && p > 0 && p < 0.01 ? fmtPct(p, 2) : fmtPct(p))
export const fmtDec = (n: number, digits = 3) => n.toFixed(digits).replace(".", ",")
export const fmtDays = (d: number | null) => (d === null ? "sem data" : `${d} ${d === 1 ? "dia" : "dias"}`)

export type Tone = "neutral" | "warning" | "danger" | "muted"

export const STATE_META: Record<AgeState, { label: string; tone: Tone }> = {
  entrada: { label: "Sem data de entrada", tone: "muted" },
  inicio: { label: "Início", tone: "neutral" },
  andamento: { label: "Em andamento", tone: "neutral" },
  esfriando: { label: "Esfriando", tone: "warning" },
  tardio: { label: "Tardio", tone: "danger" },
  fora: { label: "Revalidar", tone: "muted" },
}

export function scoreTier(score: number | null): "alta" | "media" | "baixa" | null {
  if (score === null) return null
  return score >= 80 ? "alta" : score >= 50 ? "media" : "baixa"
}
