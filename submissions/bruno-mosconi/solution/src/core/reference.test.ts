// Números de referência com os dados reais. Uma regressão no núcleo quebra o `npm run check`.
// - "none": a regra da preparação, reconciliada com o Python (01-revisao-inicial.md, R1–R4).
// - "lateEntry": a regra final (D27): cada negócio conta a partir da idade que tinha em 01/03/2017.
// - "clean": a análise de sensibilidade: coorte só com iniciados a partir de 01/03/2017.

import { describe, expect, it } from "vitest";
import { loadDataset } from "../node/load.ts";
import {
	availableDates,
	calibrationAt,
	funnelAt,
	stageCounts,
	teamStatus,
} from "./analysis.ts";
import {
	METHOD_NAMES,
	perAgent,
	rankAt,
	runBacktest,
	SNAPSHOTS,
} from "./backtest.ts";
import { type Deal, day, type Stage } from "./data.ts";
import {
	chancePhrase,
	emptyFocus,
	showAccount,
	shownPercent,
	shownWeighted,
} from "./reason.ts";
import {
	agentLists,
	bandForAge,
	chanceCurve,
	cohort,
	hasEnoughHistory,
	openAt,
	REFERENCE_DATE,
	type Truncation,
} from "./rules.ts";
import { pairedTest } from "./stats.ts";

const ds = loadDataset();
const T = REFERENCE_DATE;
const round = (v: number, d: number) => Number(v.toFixed(d));

describe("dados reais (31/12/2017)", () => {
	it("contagens", () => {
		expect(ds.deals).toHaveLength(8800);
		expect(stageCounts(ds)).toEqual({
			Won: 4238,
			Lost: 2473,
			Engaging: 1589,
			Prospecting: 500,
		});
		expect([ds.accounts.size, ds.prices.size, ds.agents.length]).toEqual([
			85, 7, 35,
		]);
	});

	it("coorte e chance por faixa (em risco: duração > b), nas três regras", () => {
		const pct = (truncation: Truncation) =>
			chanceCurve(ds.deals, T, { truncation }).map((c) =>
				round(c.chance * 100, 1),
			);
		expect(cohort(ds.deals, T, { truncation: "none" })).toHaveLength(5991);
		expect(pct("none")).toEqual([49.8, 46.4, 44.0, 32.9, 21.2, 9.1]);
		expect(cohort(ds.deals, T, { truncation: "clean" })).toHaveLength(4806);
		expect(pct("clean")).toEqual([47.3, 41.7, 38.6, 25.6, 13.5, 4.3]);
		expect(pct("lateEntry")).toEqual([47.3, 42.9, 41.2, 30.8, 19.9, 8.6]);
	});

	it("datas disponíveis: toda faixa com IC 95% de no máximo ±5 p.p.", () => {
		const ok = (truncation: Truncation) =>
			[...SNAPSHOTS, T].map((t) =>
				hasEnoughHistory(chanceCurve(ds.deals, t, { truncation })),
			);
		expect(ok("clean")).toEqual([false, false, false, true, true]); // 31/08 fica fora por ±5,013 p.p.
		expect(ok("lateEntry")).toEqual([false, true, true, true, true]);
	});

	it("funil por situação a preço de lista e valor ponderado", () => {
		const f = funnelAt(ds, T, chanceCurve(ds.deals, T, { truncation: "none" }));
		expect([
			f.slices["no-prazo"].deals,
			f.slices.esfriando.deals,
			f.slices.parado.deals,
		]).toEqual([110, 188, 1291]);
		expect([
			f.slices["no-prazo"].listPrice,
			f.slices.esfriando.listPrice,
			f.slices.parado.listPrice,
			f.prospecting.listPrice,
		]).toEqual([227_651, 465_914, 3_198_664, 1_073_986]);
		expect(
			Math.round(f.slices["no-prazo"].weighted + f.slices.esfriando.weighted),
		).toBe(195_380);
		const weighted = (curve = chanceCurve(ds.deals, T)) => {
			const x = funnelAt(ds, T, curve);
			return Math.round(
				x.slices["no-prazo"].weighted + x.slices.esfriando.weighted,
			);
		};
		expect(weighted()).toBe(182_928);
		expect(weighted(chanceCurve(ds.deals, T, { truncation: "clean" }))).toBe(
			154_880,
		);
	});
});

describe("telas (incremento 4)", () => {
	it("datas do seletor: 30/06 sem histórico suficiente; as outras 4 abertas", () => {
		expect(availableDates(ds).map((d) => d.available)).toEqual([
			false,
			true,
			true,
			true,
			true,
		]);
	});

	it("situação por vendedor: todos os 35 aparecem e a soma bate com o funil", () => {
		const all = ds.agents.map((a) => a.name);
		const team = teamStatus(ds, T, all);
		const f = funnelAt(ds, T);
		expect(team).toHaveLength(35);
		expect(team.filter((a) => a.open === 0)).toHaveLength(8); // 5 sem negócio + 3 sem nada aberto
		expect(team.reduce((s, a) => s + a.slices.parado.listPrice, 0)).toBe(
			f.slices.parado.listPrice,
		);
		expect(team.reduce((s, a) => s + a.focus, 0)).toBe(
			f.slices["no-prazo"].deals + f.slices.esfriando.deals,
		);
		const stale = team.map((a) => a.slices.parado.listPrice);
		expect(stale).toEqual([...stale].sort((a, b) => b - a));
	});

	it("CA4: em todo negócio da Foque agora, a frase e o score saem da mesma faixa", () => {
		const curve = chanceCurve(ds.deals, T);
		for (const { name } of ds.agents)
			for (const s of agentLists(ds, T, name, curve).focus) {
				const band = bandForAge(curve, s.age);
				expect(band?.chance).toBe(s.chance);
				const x = shownPercent(s.chance);
				expect(chancePhrase(band)).toContain(
					x === 0 ? "menos de 1 fechou" : `, ${x} fech`,
				);
			}
	});

	it("o potencial exibido (preço × chance inteira) nunca inverte a ordem, em nenhuma data", () => {
		let rows = 0;
		for (const { t, available } of availableDates(ds)) {
			if (!available) continue;
			const curve = chanceCurve(ds.deals, t);
			for (const { name } of ds.agents) {
				const shown = agentLists(ds, t, name, curve).focus.map(shownWeighted);
				rows += shown.length;
				expect(shown).toEqual([...shown].sort((a, b) => b - a));
			}
		}
		expect(rows).toBe(6016);
	});

	it("nenhuma faixa das datas disponíveis exibe 0%: a frase e a conta fecham", () => {
		for (const { t, available } of availableDates(ds)) {
			if (!available) continue;
			for (const band of chanceCurve(ds.deals, t))
				expect(shownPercent(band.chance)).toBeGreaterThan(0);
		}
	});

	it("empresa fora da data padrão: em 30/09, todo negócio sem empresa ainda estava em andamento em 31/12", () => {
		const t = day("2017-09-30");
		const noAccount = ds.deals.filter(
			(d) => openAt(d, t) && d.account === null,
		);
		expect(noAccount.length).toBeGreaterThan(1000);
		expect(noAccount.every((d) => d.close === null)).toBe(true);
		expect([showAccount(t), showAccount(T)]).toEqual([false, true]);
	});

	it('estado vazio da "Foque agora" em 31/12: 5 sem negócios, 6 com parados, 3 sem nada em andamento', () => {
		const curve = chanceCurve(ds.deals, T);
		const kinds = ds.agents.map(({ name }) =>
			emptyFocus(
				agentLists(ds, T, name, curve),
				ds.deals.some((d) => d.agent === name),
			),
		);
		const count = (k: string | null) => kinds.filter((x) => x === k).length;
		expect([
			count("sem-negocios"),
			count("revisar"),
			count("iniciar"),
			count("nada-aberto"),
			count(null),
		]).toEqual([5, 6, 0, 3, 21]);
	});

	it("o funil filtrado por vendedores soma o funil de cada um", () => {
		const [a, b] = ds.agents.map((x) => x.name);
		const one = (n: string) => funnelAt(ds, T, undefined, new Set([n]));
		const both = funnelAt(
			ds,
			T,
			undefined,
			new Set([a as string, b as string]),
		);
		expect(both.slices.parado.listPrice).toBe(
			one(a as string).slices.parado.listPrice +
				one(b as string).slices.parado.listPrice,
		);
		expect(both.prospecting.deals).toBe(
			one(a as string).prospecting.deals + one(b as string).prospecting.deals,
		);
	});
});

describe("backtest", () => {
	const shares = (r: ReturnType<typeof runBacktest>) =>
		Object.fromEntries(
			Object.entries(r.share).map(([k, v]) => [k, round(v * 100, 2)]),
		);

	it("regra final (entrada tardia): 31/07, 31/08 e 30/09", () => {
		const r = runBacktest(ds);
		expect(r.snapshots).toEqual(SNAPSHOTS.slice(1));
		expect(shares(r)).toEqual({
			weighted: 40.86,
			situationThenPrice: 40.74,
			priceNoStale: 37.64,
			price: 33.2,
			concludedOnly: 29.09,
			random: 14.07,
		});
	});

	it('CA3: o valor ponderado ganha de "só preço" com IC 95% acima de zero, nas duas coortes', () => {
		const gain = (truncation: Truncation) => {
			const r = pairedTest(
				perAgent(runBacktest(ds, { truncation }).units, "weighted", "price"),
			);
			return [round(r.difference * 100, 2), r.ci95[0] > 0];
		};
		expect(gain("lateEntry")).toEqual([7.66, true]);
		expect(gain("clean")).toEqual([18.69, true]);
	});

	it("coorte limpa (sensibilidade): só a foto de 30/09 tem histórico suficiente", () => {
		const r = runBacktest(ds, { truncation: "clean" });
		expect(r.snapshots).toEqual([day("2017-09-30")]);
		expect(shares(r)).toEqual({
			weighted: 47.7,
			situationThenPrice: 42.11,
			priceNoStale: 35.14,
			price: 29.01,
			concludedOnly: 22.3,
			random: 13.97,
		});
	});

	it("regra da preparação: 4 fotos, 6 métodos (2 casas), igual ao Python", () => {
		expect(shares(runBacktest(ds, { truncation: "none" }))).toEqual({
			weighted: 44.41,
			situationThenPrice: 43.16,
			priceNoStale: 40.1,
			price: 36.17,
			concludedOnly: 32.23,
			random: 15.4,
		});
	});

	it("anti-vazamento: mudar o que acontece depois de T não muda a ordem de nenhum método", () => {
		const t = SNAPSHOTS[1] as number;
		const flip: Record<Stage, Stage> = {
			Won: "Lost",
			Lost: "Won",
			Engaging: "Won",
			Prospecting: "Prospecting",
		};
		const future: Deal[] = ds.deals.map((d) =>
			d.engage !== null && d.engage <= t && (d.close === null || d.close > t)
				? { ...d, stage: flip[d.stage], close: t + 1, closeValue: 1 }
				: d,
		);
		const ids = (deals: Deal[]) =>
			rankAt({ ...ds, deals }, t).agents.map((a) =>
				METHOD_NAMES.map((m) => a.ranked[m].map((c) => c.deal.id).join(",")),
			);
		expect(ids(future)).toEqual(ids(ds.deals));
	});
});

describe("calibração (H11, revisão inicial)", () => {
	it("em 31/08, a curva prevê mais ganhos do que acontecem, nas três regras", () => {
		const t = day("2017-08-31");
		const full = calibrationAt(ds, t, REFERENCE_DATE, { truncation: "none" });
		const clean = calibrationAt(ds, t, REFERENCE_DATE, { truncation: "clean" });
		const late = calibrationAt(ds, t);
		expect(
			[full, clean, late, full].map((c, i) =>
				round((i < 3 ? c.predicted : c.realized) * 100, 1),
			),
		).toEqual([51.7, 45.3, 47.7, 34.3]);
		expect(clean.cohort).toBe(1258);
	});
});
