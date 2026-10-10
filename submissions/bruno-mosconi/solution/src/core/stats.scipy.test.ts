// D23: cada função estatística escrita à mão contra o scipy, nos mesmos dados.
// Referência gerada por analysis/referencia_scipy.py (scipy-reference.json, versionado).
// Tolerâncias definidas antes de rodar (process-log/01-revisao-inicial.md):
//   contas determinísticas: 1e-12 absoluto + 1e-9 relativo;
//   Monte Carlo (10.000 sorteios de cada lado): fração ±0,02 (≈ 3σ); limites do IC ±0,5 p.p.

import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
	chi2Sf,
	chiSquare,
	type PairedUnit,
	pairedTest,
	permutationRange,
	spearman,
	wilson,
} from "./stats.ts";

const ref = JSON.parse(
	readFileSync(new URL("./scipy-reference.json", import.meta.url), "utf8"),
);

const close = (ours: number, theirs: number) =>
	expect(Math.abs(ours - theirs)).toBeLessThanOrEqual(
		1e-12 + 1e-9 * Math.abs(theirs),
	);

describe(`contra o scipy ${ref.scipy}`, () => {
	it("cauda do qui-quadrado em 35 pontos", () => {
		for (const c of ref.chi2Sf) close(chi2Sf(c.x, c.df), c.sf);
	});

	it("qui-quadrado de independência nas tabelas reais (dimensões e mês do trimestre)", () => {
		for (const [name, c] of Object.entries<{
			table: number[][];
			statistic: number;
			df: number;
			p: number;
		}>(ref.chiSquare)) {
			const r = chiSquare(c.table);
			expect(r.df, name).toBe(c.df);
			close(r.statistic, c.statistic);
			close(r.p, c.p);
		}
	});

	it("IC de Wilson", () => {
		for (const c of ref.wilson) {
			const [lo, hi] = wilson(c.k, c.n);
			close(lo, c.low);
			close(hi, c.high);
		}
	});

	it("Spearman", () => {
		for (const c of Object.values<{ x: number[]; y: number[]; rho: number }>(
			ref.spearman,
		)) {
			close(spearman(c.x, c.y), c.rho);
		}
	});

	it("embaralhamento: mesma estatística; fração de sorteios dentro de ±0,02", () => {
		const { observed, shareAtLeast } = ref.permutation;
		const { group, y } = readGroups();
		const ours = permutationRange(group, y);
		close(ours.observed, observed);
		expect(Math.abs(ours.shareAtLeast - shareAtLeast)).toBeLessThanOrEqual(
			0.02,
		);
	});

	it("teste pareado: diferença exata; IC ±0,5 p.p.; p ±0,02", () => {
		for (const c of Object.values<{
			units: PairedUnit[];
			difference: number;
			ci95: [number, number];
			pSignFlip: number;
		}>(ref.paired)) {
			const r = pairedTest(c.units);
			close(r.difference, c.difference);
			expect(Math.abs(r.ci95[0] - c.ci95[0])).toBeLessThanOrEqual(0.005);
			expect(Math.abs(r.ci95[1] - c.ci95[1])).toBeLessThanOrEqual(0.005);
			expect(Math.abs(r.pSignFlip - c.pSignFlip)).toBeLessThanOrEqual(0.02);
		}
	});
});

function readGroups(): { group: number[]; y: number[] } {
	const e = JSON.parse(
		readFileSync(
			new URL(
				"../../analysis/saidas/estatistica-entradas.json",
				import.meta.url,
			),
			"utf8",
		),
	);
	return e.permutation;
}
