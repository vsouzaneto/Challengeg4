// Formatação para a tela: só apresenta valores que vieram da API, não calcula nenhum.

export const formatInt = (value: number): string => value.toLocaleString("pt-BR");

/** "2017-12-31" → "31/12/2017". */
export const formatDate = (iso: string): string => iso.split("-").reverse().join("/");

export const capitalize = (text: string): string => text.charAt(0).toUpperCase() + text.slice(1);

const decimal = (value: number, digits: number): string =>
  value.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });

/** Fração que veio da API, em porcentagem: 0.569 → "56,9%" (só muda a unidade). */
export const formatPct = (fraction: number): string => `${decimal(fraction * 100, 1)}%`;

/** Diferença entre frações, em pontos percentuais com sinal: −0.031 → "−3,1 pp". */
export function formatPp(fraction: number): string {
  const points = Math.round(fraction * 1000) / 10;
  const sign = points > 0 ? "+" : points < 0 ? "−" : "";
  return `${sign}${decimal(Math.abs(points), 1)} pp`;
}

export const formatDecimal = (value: number, digits = 2): string => decimal(value, digits);

/** Valor grande em forma curta: 10005534 → "10,01 mi"; 950000 → "950 mil" (o Intl põe um espaço fixo antes). */
export const formatCompact = (value: number): string =>
  value.toLocaleString("pt-BR", { notation: "compact", maximumFractionDigits: 2 });

/** Valor sem casas decimais: 2360.91 → "2.361". */
export const formatWhole = (value: number): string => value.toLocaleString("pt-BR", { maximumFractionDigits: 0 });

const MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

/** "2017-11" → "nov/2017". */
export function formatMonth(month: string): string {
  const [year, number] = month.split("-");
  return `${MONTHS[Number(number) - 1]}/${year}`;
}
