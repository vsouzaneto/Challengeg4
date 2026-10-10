import { describe, expect, it } from "vitest";
import { runBacktest } from "./backtest.ts";
import type { Dataset, Deal } from "./data.ts";
import { day } from "./data.ts";

const t = day("2017-09-30");

// 12 negócios abertos em t, todos com 10 dias (coorte vazia → chance 0 → valor ponderado empata).
// D012 (o mais caro) ganha em t+30 por 50; D001 (o mais barato) ganha em t+30 por 70;
// D005 ganha em t+100, fora da janela de 90 dias.
const deals: Deal[] = Array.from({ length: 12 }, (_, i) => {
	const n = i + 1;
	const id = `D${String(n).padStart(3, "0")}`;
	const won = n === 12 || n === 1 || n === 5;
	const close = n === 5 ? t + 100 : won ? t + 30 : null;
	const value = n === 12 ? 50 : n === 1 ? 70 : n === 5 ? 999 : null;
	return {
		id,
		agent: "Ana",
		product: `P${n}`,
		account: null,
		stage: won ? "Won" : "Engaging",
		engage: t - 10,
		close,
		closeValue: value,
	};
});

const ds: Dataset = {
	deals,
	accounts: new Map(),
	prices: new Map(deals.map((d, i) => [d.product, (i + 1) * 100])),
	agents: [{ name: "Ana", manager: "M", regional: "R" }],
};

describe("backtest", () => {
	const r = runBacktest(ds, { snapshots: [t], onlyEligible: false });
	const u = r.units[0];

	it("denominador = receita ganha na janela pelos abertos em t", () => {
		expect(u?.denominator).toBe(120);
		expect(u?.candidates).toBe(12);
	});

	it("só preço pega os 10 mais caros: perde o D001", () => {
		expect(u?.captured.price).toBe(50);
	});

	it("situação e preço: todos no prazo, então vale o preço", () => {
		expect(u?.captured.situationThenPrice).toBe(50);
	});

	it("situação e preço: no prazo vem antes de esfriando, mesmo mais barato", () => {
		const cooling = { ...deals[11], id: "D013", engage: t - 95 } as Deal; // o mais caro, esfriando
		const r2 = runBacktest(
			{ ...ds, deals: [...deals.slice(0, 11), cooling], prices: ds.prices },
			{ snapshots: [t], onlyEligible: false },
		);
		// D013 (o mais caro, ganho de 50) está esfriando e vai para o fim. Os 10 primeiros são os
		// 11 no prazo menos o D001, então nada é capturado (D005 ganha fora da janela).
		expect(r2.units[0]?.captured.situationThenPrice).toBe(0);
		expect(r2.units[0]?.captured.price).toBe(50); // só preço escolhe o D013
	});

	it("empate total cai no desempate pelo ID: pega D001..D010", () => {
		expect(u?.captured.weighted).toBe(70);
	});

	it("aleatório = esperança exata: min(1, 10/n) × receita", () => {
		expect(u?.randomExpected).toBe(100);
		expect(r.share.random).toBeCloseTo(100 / 120, 12);
	});
});
