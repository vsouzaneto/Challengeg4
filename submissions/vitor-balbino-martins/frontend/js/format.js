/** Formatadores pt-BR. Toda saida numerica do painel passa por aqui. */

const int = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const dec1 = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const dec2 = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
const brlCents = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

const isNum = (v) => typeof v === "number" && Number.isFinite(v);

/** Placeholder unico para "a API nao mandou esse numero". */
export const EMPTY = "—";

export function num(value) {
  return isNum(value) ? int.format(value) : EMPTY;
}


export function decimal(value, places = 2) {
  if (!isNum(value)) return EMPTY;
  if (places === 1) return dec1.format(value);
  if (places === 2) return dec2.format(value);
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: places,
    maximumFractionDigits: places,
  }).format(value);
}

/** Horas como a API as devolve (fracionarias). */
export function hours(value, places = 1) {
  return isNum(value) ? `${(places === 1 ? dec1 : dec2).format(value)} h` : EMPTY;
}

/** Horas em forma legivel para totais grandes. */
export function hoursCompact(value) {
  if (!isNum(value)) return EMPTY;
  if (Math.abs(value) >= 10_000) return `${dec1.format(value / 1000)} mil h`;
  return `${int.format(Math.round(value))} h`;
}

export function money(value, cents = false) {
  if (!isNum(value)) return EMPTY;
  return (cents ? brlCents : brl).format(value);
}

/** Moeda compacta para stat tiles e figuras heroi. */
export function moneyCompact(value) {
  if (!isNum(value)) return EMPTY;
  const abs = Math.abs(value);
  if (abs >= 1_000_000) return `R$ ${dec1.format(value / 1_000_000)} mi`;
  if (abs >= 10_000) return `R$ ${dec1.format(value / 1000)} mil`;
  return brl.format(value);
}

export function percent(value, places = 1) {
  if (!isNum(value)) return EMPTY;
  return `${(places === 1 ? dec1 : dec2).format(value * 100)}%`;
}

/** Nota 0-5 com uma casa. */
export function rating(value) {
  return isNum(value) ? dec1.format(value) : EMPTY;
}

/** Correlacao de Pearson: sempre com sinal explicito. */
export function signed(value, places = 2) {
  if (!isNum(value)) return EMPTY;
  const body = decimal(Math.abs(value), places);
  if (value > 0) return `+${body}`;
  if (value < 0) return `-${body}`;
  return body;
}

/** Duracao decorrida, para os contadores de execucao. */
export function elapsed(ms) {
  const total = Math.max(0, Math.round(ms / 1000));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return m > 0 ? `${m}min ${String(s).padStart(2, "0")}s` : `${s}s`;
}

/** "ha 8 minutos" a partir de um timestamp. */
export function since(timestamp) {
  if (!timestamp) return EMPTY;
  const value = timestamp instanceof Date ? timestamp.getTime() : new Date(timestamp).getTime();
  if (!Number.isFinite(value)) return EMPTY;
  const delta = Math.max(0, Date.now() - value);
  if (delta < 60_000) return "agora ha pouco";
  const minutes = Math.floor(delta / 60_000);
  if (minutes < 60) return `ha ${minutes} min`;
  const h = Math.floor(minutes / 60);
  if (h < 24) return `ha ${h} h`;
  return `ha ${Math.floor(h / 24)} d`;
}

/** Rotulo legivel para uma chave vinda do CSV. */
export function label(value) {
  const text = String(value ?? "").trim();
  if (!text) return "Sem informacao";
  if (text === "unknown") return "Nao informado";
  return text.replace(/[_-]+/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

/** Descreve a forca de uma correlacao para acompanhar o numero. */
export function correlationStrength(value) {
  if (!isNum(value)) return EMPTY;
  const a = Math.abs(value);
  if (a < 0.1) return "sem relacao pratica";
  if (a < 0.3) return "relacao fraca";
  if (a < 0.5) return "relacao moderada";
  return "relacao forte";
}
