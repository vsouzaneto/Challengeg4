import { describe, expect, it } from "vitest";
import {
	chi2Sf,
	chiSquare,
	pairedTest,
	permutationRange,
	quantile,
	spearman,
	wilson,
} from "./stats.ts";

describe("valores conhecidos", () => {
	it("qui-quadrado: com 2 g.l. a cauda é exp(−x/2); 3,841 com 1 g.l. dá 0,05", () => {
		for (const x of [0.5, 2, 5.991464547107979, 20])
			expect(chi2Sf(x, 2)).toBeCloseTo(Math.exp(-x / 2), 14);
		expect(chi2Sf(3.841458820694124, 1)).toBeCloseTo(0.05, 12);
	});

	it("tabela 2×2 feita à mão", () => {
		// [[10, 20], [20, 10]]: esperado 15 em todas as células; estatística = 4 × 25/15
		const r = chiSquare([
			[10, 20],
			[20, 10],
		]);
		expect(r.statistic).toBeCloseTo(100 / 15, 12);
		expect(r.df).toBe(1);
	});

	it("Wilson 5/10", () => {
		const [lo, hi] = wilson(5, 10);
		expect(lo).toBeCloseTo(0.236593, 6);
		expect(hi).toBeCloseTo(0.763407, 6);
	});

	it("Spearman com empates", () => {
		expect(spearman([1, 2, 3, 4], [10, 20, 30, 40])).toBeCloseTo(1, 14);
		expect(spearman([1, 2, 3, 4], [4, 3, 2, 1])).toBeCloseTo(-1, 14);
	});

	it("quantil linear como o numpy", () => {
		expect(quantile([0, 10], 0.25)).toBe(2.5);
	});

	it("embaralhamento é determinístico com a mesma semente", () => {
		const g = [0, 0, 0, 1, 1, 1];
		const y = [1, 1, 0, 0, 0, 1];
		expect(permutationRange(g, y, { iterations: 500 })).toEqual(
			permutationRange(g, y, { iterations: 500 }),
		);
	});

	it("teste pareado: diferença nula dá IC que cobre 0 e p = 1", () => {
		const r = pairedTest(
			[
				{ a: 5, b: 5, den: 10 },
				{ a: 3, b: 3, den: 10 },
			],
			{ iterations: 200 },
		);
		expect(r.difference).toBe(0);
		expect(r.pSignFlip).toBe(1);
	});
});
