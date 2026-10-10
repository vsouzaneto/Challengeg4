// A medição do `npm run bench` (CA15). Roda igual no Node e no navegador: recebe os CSVs em texto,
// multiplica os negócios por k (cópias com ID novo, mesmos vendedores e produtos) e mede o que o app
// e um job diário fariam na data padrão. Mediana de 5 rodadas, depois de 1 de aquecimento.

import { teamStatus } from "../src/core/analysis.ts";
import {
	type Dataset,
	parseDataset,
	type RawTables,
} from "../src/core/data.ts";
import {
	agentLists,
	chanceCurve,
	REFERENCE_DATE,
	scoreOpen,
} from "../src/core/rules.ts";
import { potentialScores } from "../src/core/score.ts";

export const SCALES = [1, 10, 100];

export function multiply(ds: Dataset, k: number): Dataset {
	if (k === 1) return ds;
	const deals = [];
	for (let i = 0; i < k; i++)
		for (const d of ds.deals) deals.push({ ...d, id: `${d.id}-${i}` });
	return { ...ds, deals };
}

const median = (xs: number[]) =>
	[...xs].sort((a, b) => a - b)[Math.floor(xs.length / 2)] as number;

function time(f: () => unknown): number {
	f();
	const runs: number[] = [];
	for (let i = 0; i < 5; i++) {
		const t0 = performance.now();
		f();
		runs.push(performance.now() - t0);
	}
	return median(runs);
}

export interface BenchRow {
	scale: number;
	deals: number;
	open: number;
	/** O que uma tela do app calcula: curva, score de todos, a lista de um vendedor e a equipe dele. */
	screenMs: number;
	/** O que um job diário calcularia: curva, score e as listas dos 35 vendedores. */
	jobMs: number;
	curveMs: number;
	jsonBytes: number;
}

export function bench(raw: RawTables, scales = SCALES): BenchRow[] {
	const base = parseDataset(raw);
	const t = REFERENCE_DATE;
	const seller = "Zane Levy";
	const team = base.agents
		.filter((a) => a.manager === "Summer Sewald")
		.map((a) => a.name);
	return scales.map((k) => {
		const ds = multiply(base, k);
		const curve = chanceCurve(ds.deals, t);
		return {
			scale: k,
			deals: ds.deals.length,
			open: scoreOpen(ds, t, curve).length,
			curveMs: time(() => chanceCurve(ds.deals, t)),
			screenMs: time(() => {
				const c = chanceCurve(ds.deals, t);
				potentialScores(scoreOpen(ds, t, c));
				agentLists(ds, t, seller, c);
				teamStatus(ds, t, team, c);
			}),
			jobMs: time(() => {
				const c = chanceCurve(ds.deals, t);
				potentialScores(scoreOpen(ds, t, c));
				for (const a of ds.agents) agentLists(ds, t, a.name, c);
			}),
			jsonBytes: new TextEncoder().encode(JSON.stringify(ds.deals)).length,
		};
	});
}
