import type { Category, Route } from "@/lib/types";

export const number = (value: number, digits = 0) =>
  new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: digits,
    roundingMode: "halfEven",
  }).format(value);
export const percent = (value: number, digits = 1) =>
  new Intl.NumberFormat("pt-BR", {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
export const currency = (value: number) =>
  new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
    roundingMode: "halfEven",
  }).format(value);
export const categoryLabels: Record<Category, string> = {
  Hardware: "Hardware",
  "HR Support": "Suporte de RH",
  Access: "Acesso",
  Miscellaneous: "Outros assuntos",
  Storage: "Armazenamento",
  Purchase: "Compras",
  "Internal Project": "Projetos internos",
  "Administrative rights": "Privilégios administrativos",
};
export const routeLabels: Record<Route, string> = {
  auto: "Roteamento automático",
  revisao_humana: "Revisão humana",
  escalar: "Escalar atendimento",
};
export const routeTone: Record<Route, string> = {
  auto: "success",
  revisao_humana: "warning",
  escalar: "danger",
};
export function dateLabel(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Data indisponível"
    : new Intl.DateTimeFormat("pt-BR", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        timeZone: "America/Sao_Paulo",
      }).format(date);
}
