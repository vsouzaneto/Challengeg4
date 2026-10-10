import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { loadDataset } from "../node/load.ts";
import { isoDate } from "./data.ts";
import { evidence } from "./evidence.ts";

// Os números do "Como funciona" batem com a auditoria (analysis/saidas/auditoria-ts.md, regra final).
const ds = loadDataset();
const ml = readFileSync(
	new URL("../../analysis/saidas/ml-por-vendedor.csv", import.meta.url),
	"utf8",
);
const e = evidence(ds, ml);
const pp = (v: number) => Math.round(v * 10_000) / 100;

describe("evidence: o que o Como funciona mostra", () => {
	it("prova 2: a lista no passado, nas 3 datas com histórico suficiente", () => {
		expect(e.backtest.dates.map((d) => isoDate(d.t))).toEqual([
			"2017-07-31",
			"2017-08-31",
			"2017-09-30",
		]);
		expect(pp(e.backtest.weighted)).toBe(40.86);
		expect(pp(e.backtest.price)).toBe(33.2);
		expect(pp(e.backtest.weightedVsPrice.difference)).toBe(7.66);
		expect(pp(e.backtest.weightedVsSituation.difference)).toBe(0.12);
		// "O resultado se repetiu nas três datas": o potencial ganha do preço e do sorteio em cada uma.
		for (const d of e.backtest.dates) {
			expect(d.weighted).toBeGreaterThan(d.price);
			expect(d.price).toBeGreaterThan(d.random);
		}
	});

	it("o modelo de ML, nas mesmas unidades, não difere do potencial além do acaso", () => {
		expect(pp(e.backtest.ml)).toBe(43.18);
		const [lo, hi] = e.backtest.mlVsWeighted.ci95;
		expect(lo).toBeLessThan(0);
		expect(hi).toBeGreaterThan(0);
	});

	it("prova 3: nenhum fator muda a taxa de ganho entre concluídos (p > 0,05)", () => {
		expect(e.factors.map((f) => Math.round(f.p * 1000) / 1000)).toEqual([
			0.264, 0.372, 0.604, 0.971, 0.103, 0.144,
		]);
		// Mas o vendedor muda quanto fica aberto (frio).
		expect(Math.round(e.agentCold.min * 100)).toBe(0);
		expect(Math.round(e.agentCold.max * 100)).toBe(31);
		expect(e.agentCold.p).toBeLessThan(0.001);
	});

	it("limitações: corte da base, calibração e trimestre", () => {
		expect(isoDate(e.truncation.firstClose)).toBe("2017-03-01");
		expect(e.truncation.startedBefore).toBe(358 + 827);
		expect(
			e.calibration.map((c) => [
				Math.round(c.predicted * 1000) / 10,
				Math.round(c.realized * 1000) / 10,
			]),
		).toEqual([
			[52.1, 37.4],
			[47.7, 34.3],
			[46.8, 29.7],
		]);
		expect(Math.round((e.calibration[2]?.stillOpen ?? 0) * 1000) / 10).toBe(
			9.7,
		);
		expect(Math.round(e.quarter.first * 100)).toBe(49);
		expect(Math.round(e.quarter.last * 100)).toBe(81);
	});
});
