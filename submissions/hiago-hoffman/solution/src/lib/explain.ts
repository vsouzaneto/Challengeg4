import type { AgeState, Thresholds } from "@/lib/scoring/model"

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

export const STATE_META: Record<AgeState, { label: string; tone: Tone; action: (t: Thresholds) => string }> = {
  entrada: {
    label: "Sem data de entrada",
    tone: "muted",
    action: () =>
      "Faça o primeiro contato e registre a entrada em Engaging. Sem essa data, a chance combina a de um deal recém-engajado com a conversão Prospecting → Engaging aprendida.",
  },
  inicio: {
    label: "Início",
    tone: "neutral",
    action: (t) => `Qualifique rápido: metade das perdas da base acontece até ${fmtDays(t.inicio)}.`,
  },
  andamento: {
    label: "Em andamento",
    tone: "neutral",
    action: (t) => `Avance para o fechamento: 75% dos ganhos da base fecham até ${fmtDays(t.andamento)}.`,
  },
  esfriando: {
    label: "Esfriando",
    tone: "warning",
    action: (t) =>
      `Aja esta semana: o deal passou de ${fmtDays(t.andamento)}, tempo em que 75% dos ganhos já tinham fechado, e a chance cai rápido daqui em diante.`,
  },
  tardio: {
    label: "Tardio",
    tone: "danger",
    action: (t) => `Última janela: 95% dos ganhos da base fecharam até ${fmtDays(t.esfriando)}. Confirme se o cliente ainda decide.`,
  },
  fora: {
    label: "Revalidar",
    tone: "muted",
    action: (t) =>
      `Revalide com o cliente ou encerre: 99% dos ganhos da base fecharam até ${fmtDays(t.tardio)}. A chance vem só dos raros ganhos depois dessa idade.`,
  },
}

export const FLAG_LABEL: Record<string, string> = {
  sem_conta: "Vincular a conta do cliente",
  produto_fora_catalogo: "Produto fora do catálogo: cadastrar preço",
  vendedor_sem_cadastro: "Vendedor sem time cadastrado",
  estimativa_entrada: "Registrar data de entrada em Engaging",
}

export function scoreTier(score: number | null): "alta" | "media" | "baixa" | null {
  if (score === null) return null
  return score >= 80 ? "alta" : score >= 50 ? "media" : "baixa"
}
