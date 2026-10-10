// O motivo de cada posição, dito ao vendedor. Sai das mesmas funções que dão o score.

import {
	type AgentLists,
	type BandChance,
	COOLING_FROM,
	REFERENCE_DATE,
	type ScoredDeal,
	STALE_AFTER,
} from "./rules.ts";

export interface Deadline {
	kind: "esfria" | "parado";
	days: number;
}

/**
 * D30: só os dois limites com significado, "Esfria em N dias" (90) e "Fica parado em N dias"
 * (depois de 138, o maior ciclo observado). Não prevê queda de chance e não muda a ordem.
 */
export function deadline(age: number): Deadline | null {
	if (age < COOLING_FROM) return { kind: "esfria", days: COOLING_FROM - age };
	if (age <= STALE_AFTER)
		return { kind: "parado", days: STALE_AFTER + 1 - age };
	return null;
}

/**
 * A chance exibida, em % inteira (47%). É o mesmo número da frase "De cada 100" e o que multiplica
 * o preço na conta do painel (D40). A ordem continua pelo valor exato; um teste com os dados reais
 * garante que o potencial exibido nunca inverte a ordem.
 */
export const shownPercent = (chance: number): number =>
	Math.round(chance * 100);
export const shownChance = (chance: number): number =>
	shownPercent(chance) / 100;
export const shownWeighted = (s: Pick<ScoredDeal, "price" | "chance">) =>
	Math.round(s.price * shownChance(s.chance));

/** D28 e D40: a chance como histórico, com o mesmo número da conta. `band` null = frio (sem faixa). */
export function chancePhrase(band: BandChance | null): string {
	if (band === null)
		return `Nenhum negócio da base fechou venda depois de ${STALE_AFTER} dias em andamento.`;
	const who =
		band.from === 0
			? "De cada 100 negócios iniciados"
			: `De cada 100 negócios que chegaram aos ${band.from} dias ainda em andamento`;
	const x = shownPercent(band.chance);
	const howMany =
		x === 0
			? "menos de 1 fechou venda"
			: `${x} ${x === 1 ? "fechou" : "fecharam"} venda`;
	return `${who}, ${howMany}.`;
}

/** Posição de cada negócio se a lista fosse ordenada só por preço (H10: mostrar quando diverge). */
export function priceRanks(list: readonly ScoredDeal[]): Map<string, number> {
	const byPrice = [...list].sort(
		(a, b) =>
			b.price - a.price ||
			(a.deal.id < b.deal.id ? -1 : a.deal.id > b.deal.id ? 1 : 0),
	);
	return new Map(byPrice.map((s, i) => [s.deal.id, i + 1]));
}

/**
 * A empresa só aparece na data padrão. Antes dela, "sem empresa" entrega o futuro: nas fotos de
 * 31/07, 31/08 e 30/09, todo negócio em andamento sem empresa ainda estava em andamento em 31/12.
 */
export const showAccount = (t: number): boolean => t === REFERENCE_DATE;

/** O que a "Foque agora" vazia manda fazer (CA5). null = a lista tem negócios. */
export type EmptyFocus = "sem-negocios" | "revisar" | "iniciar" | "nada-aberto";

export function emptyFocus(
	lists: AgentLists,
	hasDeals: boolean,
): EmptyFocus | null {
	if (lists.focus.length > 0) return null;
	if (!hasDeals) return "sem-negocios";
	if (lists.review.length > 0) return "revisar";
	if (lists.prospect.length > 0) return "iniciar";
	return "nada-aberto";
}
