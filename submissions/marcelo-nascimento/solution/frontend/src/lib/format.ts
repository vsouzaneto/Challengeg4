const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2,
});

const numberFormatter = new Intl.NumberFormat("pt-BR");
const dateFormatter = new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" });

export function formatCurrency(value: number | null): string {
  return value === null ? "Não disponível" : currencyFormatter.format(value);
}

export function formatNumber(value: number | null): string {
  return value === null ? "Não disponível" : numberFormatter.format(value);
}

export function formatDecimal(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

export function formatPercent(value: number): string {
  return `${formatDecimal(value)}%`;
}

export function formatMillions(value: number | null): string {
  return value === null ? "Não disponível" : `${currencyFormatter.format(value)} mi`;
}

export function formatDate(value: string | null): string {
  if (!value) {
    return "Não disponível";
  }
  const [year, month, day] = value.slice(0, 10).split("-").map(Number);
  if (!year || !month || !day) {
    return "Data inválida";
  }
  return dateFormatter.format(new Date(Date.UTC(year, month - 1, day)));
}

export function formatPoints(value: number): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}
