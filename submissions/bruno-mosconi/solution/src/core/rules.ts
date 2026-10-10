// Regra de priorização numa data de referência T. Tudo aqui olha só o que se sabia em T
// (definições pré-registradas em process-log/01-revisao-inicial.md, seção 3).

import { type Dataset, type Deal, day, priceOf } from "./data.ts";
import { wilson } from "./stats.ts";

export const COOLING_FROM = 90; // "Esfriando" a partir de 90 dias
export const STALE_AFTER = 138; // "Parado" depois de 138 dias
export const BANDS = [0, 30, 60, 90, 104, 120] as const;
export const REFERENCE_DATE = day("2017-12-31");

export type AtRisk = ">=" | ">";

/**
 * A base só traz negócios concluídos a partir da primeira conclusão observada (01/03/2017) ou ainda
 * abertos: os antigos que aparecem são os que sobreviveram até lá (revisão inicial, H11).
 * - "lateEntry" (padrão, D27): usa todos, mas um negócio só conta na faixa b se, aos b dias, já estava
 *   na janela observada (início + b ≥ primeira conclusão).
 * - "clean": só negócios iniciados a partir da primeira conclusão observada (análise de sensibilidade).
 * - "none": a curva da preparação, sem correção.
 */
export type Truncation = "none" | "clean" | "lateEntry";
export const DEFAULT_TRUNCATION: Truncation = "lateEntry";

/** Meia-largura máxima do IC 95% (Wilson) aceita em qualquer faixa para a data ficar disponível. */
export const MAX_HALF_WIDTH = 0.05;

export interface CurveOptions {
	bands?: readonly number[];
	/**
	 * ">" (padrão): em risco na faixa b quem durou mais de b dias. Um negócio aberto em T com idade a
	 * tem conclusão depois de início + a, então se compara com quem durou mais de a.
	 * ">=" era a definição pré-registrada; a revisão mostrou que ela inclui quem concluiu no próprio dia.
	 */
	atRisk?: AtRisk;
	cutoff?: number; // dias; coorte = iniciados até T − cutoff; acima disso, parado
	minEngage?: number; // só iniciados a partir deste dia (H11)
	truncation?: Truncation;
}

export interface BandChance {
	from: number;
	atRisk: number;
	won: number;
	chance: number;
}

export const existsAt = (d: Deal, t: number): boolean =>
	d.engage !== null && d.engage <= t;
export const closedBy = (d: Deal, t: number): boolean =>
	d.close !== null && d.close <= t;
export const openAt = (d: Deal, t: number): boolean =>
	existsAt(d, t) && !closedBy(d, t);
export const wonBy = (d: Deal, t: number): boolean =>
	d.stage === "Won" && closedBy(d, t);

/** Dias entre o início e min(conclusão, T). Para quem conclui depois de T, vale T. */
export function observedDuration(d: Deal, t: number): number {
	if (d.engage === null) throw new Error(`negócio sem data: ${d.id}`);
	return (closedBy(d, t) ? (d.close as number) : t) - d.engage;
}

export const ageAt = (d: Deal, t: number): number => observedDuration(d, t);

/** Maior ciclo entre os concluídos até T (alternativa ao corte fixo de 138). */
export function maxCycleBy(deals: readonly Deal[], t: number): number {
	let max = -1;
	for (const d of deals)
		if (existsAt(d, t) && closedBy(d, t))
			max = Math.max(max, observedDuration(d, t));
	return max;
}

/** Primeira conclusão observada até T: o início da janela em que a base enxerga desfechos. */
export function firstCloseBy(deals: readonly Deal[], t: number): number | null {
	let first: number | null = null;
	for (const d of deals)
		if (closedBy(d, t) && (first === null || (d.close as number) < first))
			first = d.close;
	return first;
}

export function cohort(
	deals: readonly Deal[],
	t: number,
	opts: CurveOptions = {},
): Deal[] {
	const cutoff = opts.cutoff ?? STALE_AFTER;
	const from =
		(opts.truncation ?? DEFAULT_TRUNCATION) === "clean"
			? (firstCloseBy(deals, t) ?? Number.POSITIVE_INFINITY)
			: Number.NEGATIVE_INFINITY;
	return deals.filter(
		(d) =>
			d.engage !== null &&
			d.engage <= t - cutoff &&
			d.engage >= from &&
			(opts.minEngage === undefined || d.engage >= opts.minEngage),
	);
}

/** Chance de virar venda para quem ainda está aberto ao começar cada faixa (sem viés de sobrevivência). */
export function chanceCurve(
	deals: readonly Deal[],
	t: number,
	opts: CurveOptions = {},
): BandChance[] {
	const bands = opts.bands ?? BANDS;
	const strict = (opts.atRisk ?? ">") === ">";
	const window = firstCloseBy(deals, t) ?? Number.POSITIVE_INFINITY;
	const late = (opts.truncation ?? DEFAULT_TRUNCATION) === "lateEntry";
	const base = cohort(deals, t, opts).map((d) => ({
		engage: d.engage as number,
		dur: observedDuration(d, t),
		won: wonBy(d, t),
	}));
	return bands.map((from) => {
		const risk = base.filter(
			(x) =>
				(strict ? x.dur > from : x.dur >= from) &&
				(!late || x.engage + from >= window),
		);
		const won = risk.filter((x) => x.won).length;
		return {
			from,
			atRisk: risk.length,
			won,
			chance: risk.length ? won / risk.length : 0,
		};
	});
}

/** Maior meia-largura do IC 95% entre as faixas (1 quando alguma faixa está vazia). */
export function curveHalfWidth(curve: readonly BandChance[]): number {
	return Math.max(
		...curve.map((c) => {
			if (c.atRisk === 0) return 1;
			const [lo, hi] = wilson(c.won, c.atRisk);
			return (hi - lo) / 2;
		}),
	);
}

/** A data tem histórico suficiente se toda faixa tem IC 95% de no máximo ±5 p.p. (G1). */
export const hasEnoughHistory = (curve: readonly BandChance[]): boolean =>
	curveHalfWidth(curve) <= MAX_HALF_WIDTH;

/** O cálculo errado: só concluídos até T, com ciclo > b. Fica aqui para mostrar o viés. */
export function concludedOnlyCurve(
	deals: readonly Deal[],
	t: number,
	bands: readonly number[] = BANDS,
	atRisk: AtRisk = ">",
): BandChance[] {
	const done = deals
		.filter((d) => existsAt(d, t) && closedBy(d, t))
		.map((d) => ({ dur: observedDuration(d, t), won: d.stage === "Won" }));
	return bands.map((from) => {
		const risk = done.filter((x) =>
			atRisk === ">" ? x.dur > from : x.dur >= from,
		);
		const won = risk.filter((x) => x.won).length;
		return {
			from,
			atRisk: risk.length,
			won,
			chance: risk.length ? won / risk.length : 0,
		};
	});
}

/**
 * O cálculo errado como alguém o faria: chance por dia exato entre os concluídos até T
 * (ciclo > idade), sem saber que acima de 138 dias nada é concluído. Para idades além do último
 * dia com pelo menos minSample casos, usa esse último dia. É o método "chance só com concluídos"
 * do backtest da preparação (analysis/backtest_referencia.py, closed_only).
 */
export function concludedOnlyByDay(
	deals: readonly Deal[],
	t: number,
	minSample = 30,
): (age: number) => number {
	const done = deals.filter((d) => existsAt(d, t) && closedBy(d, t));
	if (done.length === 0) return () => 0;
	const maxCycle = Math.max(...done.map((d) => observedDuration(d, t)));
	const atRisk = new Array<number>(maxCycle + 1).fill(0);
	const won = new Array<number>(maxCycle + 1).fill(0);
	for (const d of done) {
		const dur = observedDuration(d, t);
		for (let x = 0; x < dur; x++) {
			atRisk[x] = (atRisk[x] as number) + 1;
			if (d.stage === "Won") won[x] = (won[x] as number) + 1;
		}
	}
	let xmax = 0;
	atRisk.forEach((n, x) => {
		if (n >= minSample) xmax = x;
	});
	return (age) => {
		const x = Math.min(Math.max(age, 0), xmax);
		return (won[x] as number) / (atRisk[x] as number);
	};
}

/** Índice da faixa da idade; −1 quando passou do corte (parado). */
export function bandIndex(
	age: number,
	bands: readonly number[] = BANDS,
	cutoff = STALE_AFTER,
): number {
	if (age > cutoff) return -1;
	let idx = -1;
	bands.forEach((b, i) => {
		if (b <= age) idx = i;
	});
	return idx;
}

/** A faixa da idade, ou null quando parado. A frase (D28) e o score usam a mesma faixa. */
export function bandForAge(
	curve: readonly BandChance[],
	age: number,
	cutoff = STALE_AFTER,
): BandChance | null {
	const i = bandIndex(
		age,
		curve.map((c) => c.from),
		cutoff,
	);
	return curve[i] ?? null;
}

export const chanceForAge = (
	curve: readonly BandChance[],
	age: number,
	cutoff = STALE_AFTER,
): number => bandForAge(curve, age, cutoff)?.chance ?? 0;

export type Situation = "no-prazo" | "esfriando" | "parado";

export const situation = (
	age: number,
	coolingFrom = COOLING_FROM,
): Situation =>
	age > STALE_AFTER ? "parado" : age >= coolingFrom ? "esfriando" : "no-prazo";

export const byId = (a: Deal, b: Deal): number =>
	a.id < b.id ? -1 : a.id > b.id ? 1 : 0;

export interface ScoredDeal {
	deal: Deal;
	age: number;
	price: number;
	chance: number;
	weighted: number;
}

export interface AgentLists {
	focus: ScoredDeal[]; // "Foque agora": abertos até 138 dias, por valor ponderado
	review: ScoredDeal[]; // "Revisar ou encerrar": parados
	prospect: Deal[]; // "Inicie contato": Prospecting, só na data padrão (D13)
}

/** Ordem da lista "Revisar ou encerrar" (D21): preço, depois idade (mais antigo primeiro), depois ID. */
export const reviewOrder = (a: ScoredDeal, b: ScoredDeal): number =>
	b.price - a.price || b.age - a.age || byId(a.deal, b.deal);

export function scoreOpen(
	ds: Dataset,
	t: number,
	curve: readonly BandChance[],
	agent?: string,
): ScoredDeal[] {
	return ds.deals
		.filter((d) => openAt(d, t) && (agent === undefined || d.agent === agent))
		.map((deal) => {
			const age = ageAt(deal, t);
			const price = priceOf(ds, deal);
			const chance = chanceForAge(curve, age);
			return { deal, age, price, chance, weighted: chance * price };
		});
}

export function agentLists(
	ds: Dataset,
	t: number,
	agent: string,
	curve = chanceCurve(ds.deals, t),
): AgentLists {
	const scored = scoreOpen(ds, t, curve, agent);
	const focus = scored
		.filter((s) => s.age <= STALE_AFTER)
		.sort((a, b) => b.weighted - a.weighted || byId(a.deal, b.deal));
	const review = scored.filter((s) => s.age > STALE_AFTER).sort(reviewOrder);
	const prospect =
		t === REFERENCE_DATE
			? ds.deals
					.filter((d) => d.stage === "Prospecting" && d.agent === agent)
					.sort((a, b) => priceOf(ds, b) - priceOf(ds, a) || byId(a, b))
			: [];
	return { focus, review, prospect };
}
