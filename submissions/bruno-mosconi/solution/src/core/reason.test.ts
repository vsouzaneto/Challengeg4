import { describe, expect, it } from "vitest";
import {
	chancePhrase,
	deadline,
	priceRanks,
	shownPercent,
	shownWeighted,
} from "./reason.ts";
import type { BandChance, ScoredDeal } from "./rules.ts";

describe("prazo (D30): só os dois limites, sem prever queda de chance", () => {
	it("esfria aos 90 dias", () => {
		expect(deadline(0)).toEqual({ kind: "esfria", days: 90 });
		expect(deadline(89)).toEqual({ kind: "esfria", days: 1 });
	});

	it("fica parado depois de 138 dias", () => {
		expect(deadline(90)).toEqual({ kind: "parado", days: 49 });
		expect(deadline(138)).toEqual({ kind: "parado", days: 1 });
	});

	it("parado não tem prazo", () => {
		expect(deadline(139)).toBeNull();
	});
});

describe("frase da chance (D28, D40): histórico, não previsão", () => {
	const band = (from: number, won: number, atRisk: number): BandChance => ({
		from,
		won,
		atRisk,
		chance: won / atRisk,
	});

	it("N é o início da faixa e X é a mesma % inteira da conta", () => {
		const b = band(90, 308, 1000);
		expect(shownPercent(b.chance)).toBe(31);
		expect(chancePhrase(b)).toBe(
			"De cada 100 negócios que chegaram aos 90 dias ainda em andamento, 31 fecharam venda.",
		);
	});

	it("faixa 0 e singular", () => {
		expect(chancePhrase(band(0, 473, 1000))).toBe(
			"De cada 100 negócios iniciados, 47 fecharam venda.",
		);
		expect(chancePhrase(band(120, 10, 1000))).toBe(
			"De cada 100 negócios que chegaram aos 120 dias ainda em andamento, 1 fechou venda.",
		);
	});

	it("menos de meio em 100", () => {
		expect(chancePhrase(band(120, 4, 1000))).toBe(
			"De cada 100 negócios que chegaram aos 120 dias ainda em andamento, menos de 1 fechou venda.",
		);
	});

	it("frio: sem faixa", () => {
		expect(chancePhrase(null)).toBe(
			"Nenhum negócio da base fechou venda depois de 138 dias em andamento.",
		);
	});
});

describe("conta do painel e ordem por preço", () => {
	const scored = (id: string, price: number, chance: number): ScoredDeal => ({
		deal: {
			id,
			agent: "Ana",
			product: "P",
			account: null,
			stage: "Engaging",
			engage: 0,
			close: null,
			closeValue: null,
		},
		age: 10,
		price,
		chance,
		weighted: price * chance,
	});

	it("potencial exibido = preço × chance inteira", () => {
		expect(shownWeighted(scored("A", 5482, 0.428_57))).toBe(2357); // 5.482 × 43%
		expect(shownWeighted(scored("B", 5482, 0.473))).toBe(2577); // 5.482 × 47%
	});

	it("posição pela ordem de preço, com desempate pelo ID", () => {
		const r = priceRanks([
			scored("B", 100, 0.5),
			scored("A", 100, 0.1),
			scored("C", 500, 0.05),
		]);
		expect([...r]).toEqual([
			["C", 1],
			["A", 2],
			["B", 3],
		]);
	});
});
