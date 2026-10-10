import { describe, expect, it } from "vitest";
import { loadDataset } from "../node/load.ts";
import { availableDates } from "./analysis.ts";
import type { Deal } from "./data.ts";
import {
	agentLists,
	chanceCurve,
	REFERENCE_DATE,
	type ScoredDeal,
	STALE_AFTER,
	scoreOpen,
} from "./rules.ts";
import { potentialScores } from "./score.ts";

const scored = (id: string, weighted: number, age = 10): ScoredDeal => ({
	deal: { id } as Deal,
	age,
	price: weighted,
	chance: 1,
	weighted,
});

describe("score de 0 a 100 (D39): posição do potencial entre os quentes e esfriando", () => {
	it("score = % dos negócios com potencial menor, arredondado para baixo", () => {
		const s = potentialScores([
			scored("A", 10),
			scored("B", 20),
			scored("C", 20),
			scored("D", 40),
		]);
		expect([...s]).toEqual([
			["A", 0],
			["B", 25],
			["C", 25], // empate: mesmo score
			["D", 75],
		]);
	});

	it("frios ficam fora: não têm score e não contam na base", () => {
		const s = potentialScores([
			scored("A", 10),
			scored("F", 0, STALE_AFTER + 1),
		]);
		expect(s.has("F")).toBe(false);
		expect(s.get("A")).toBe(0);
	});

	it("dados reais: mesma ordem do potencial em toda lista, de 0 a 100, em toda data", () => {
		const ds = loadDataset();
		for (const { t, available } of availableDates(ds)) {
			if (!available) continue;
			const curve = chanceCurve(ds.deals, t);
			const scores = potentialScores(scoreOpen(ds, t, curve));
			for (const { name } of ds.agents) {
				const list = agentLists(ds, t, name, curve).focus.map(
					(s) => scores.get(s.deal.id) as number,
				);
				expect(list).toEqual([...list].sort((a, b) => b - a));
				for (const v of list) expect(v >= 0 && v <= 100).toBe(true);
			}
		}
		const at = potentialScores(
			scoreOpen(ds, REFERENCE_DATE, chanceCurve(ds.deals, REFERENCE_DATE)),
		);
		expect(at.size).toBe(298); // 110 quentes + 188 esfriando em 31/12/2017
		expect(Math.max(...at.values())).toBe(99);
	});
});
