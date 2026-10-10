// Backtest: em cada foto T, ordena os negócios abertos de cada vendedor e mede quanto da receita
// ganha em (T, T+90] ficou entre os 10 primeiros. Curva, coorte e corte vêm só do que se sabia em T.

import { type Dataset, type Deal, day, priceOf } from "./data.ts";
import {
	type AtRisk,
	BANDS,
	type BandChance,
	byId,
	chanceCurve,
	chanceForAge,
	concludedOnlyByDay,
	DEFAULT_TRUNCATION,
	hasEnoughHistory,
	maxCycleBy,
	observedDuration,
	openAt,
	type Situation,
	STALE_AFTER,
	situation,
	type Truncation,
} from "./rules.ts";

export const SNAPSHOTS = [
	"2017-06-30",
	"2017-07-31",
	"2017-08-31",
	"2017-09-30",
].map(day);
export const WINDOW_DAYS = 90;
export const TOP_N = 10;

export interface Candidate {
	deal: Deal;
	age: number;
	price: number;
	stale: boolean;
	revenue: number; // close_value se ganho em (T, T+90]; senão 0
}

interface Context {
	curve: readonly BandChance[];
	wrongChance: (age: number) => number;
	cutoff: number;
	coolingFrom: number;
}

const SITUATION_RANK: Record<Situation, number> = {
	"no-prazo": 2,
	esfriando: 1,
	parado: 0,
};

type Ranker = (cands: Candidate[], ctx: Context) => Candidate[];

const tie = (a: Candidate, b: Candidate) => byId(a.deal, b.deal);
const chanceOf = (ctx: Context, c: Candidate) =>
	chanceForAge(ctx.curve, c.age, ctx.cutoff);
const sortBy = (cands: Candidate[], key: (c: Candidate) => number) =>
	[...cands].sort((a, b) => key(b) - key(a) || tie(a, b));

export const METHODS = {
	weighted: (cands, ctx) => sortBy(cands, (c) => chanceOf(ctx, c) * c.price),
	// No prazo antes de esfriando antes de parado; dentro de cada grupo, por preço.
	situationThenPrice: (cands, ctx) =>
		sortBy(
			cands,
			(c) => SITUATION_RANK[situation(c.age, ctx.coolingFrom)] * 1e7 + c.price,
		),
	priceNoStale: (cands) => {
		const fresh = sortBy(
			cands.filter((c) => !c.stale),
			(c) => c.price,
		);
		const stale = cands
			.filter((c) => c.stale)
			.sort((a, b) => b.price - a.price || b.age - a.age || tie(a, b));
		return [...fresh, ...stale];
	},
	price: (cands) => sortBy(cands, (c) => c.price),
	concludedOnly: (cands, ctx) =>
		sortBy(cands, (c) => ctx.wrongChance(c.age) * c.price),
} satisfies Record<string, Ranker>;

export type MethodName = keyof typeof METHODS;
export const METHOD_NAMES = Object.keys(METHODS) as MethodName[];

export interface BacktestOptions {
	snapshots?: readonly number[];
	bands?: readonly number[];
	atRisk?: AtRisk;
	cutoff?: "fixed" | "observed"; // 138 fixo ou o maior ciclo observado em T (H2)
	minEngage?: number; // curva só com iniciados a partir deste dia (H11)
	coolingFrom?: number; // início de "esfriando" (D2: 90; a preparação usou 91)
	truncation?: Truncation; // padrão DEFAULT_TRUNCATION (D27)
	/** Só as fotos com histórico suficiente (CA6). Padrão: sim, quando truncation ≠ "none". */
	onlyEligible?: boolean;
}

export interface Unit {
	agent: string;
	t: number;
	candidates: number;
	denominator: number;
	captured: Record<MethodName, number>;
	randomExpected: number;
}

export interface BacktestResult {
	units: Unit[];
	share: Record<MethodName | "random", number>;
	cutoffs: number[];
	snapshots: number[]; // fotos usadas: só as com histórico suficiente, salvo onlyEligible: false
}

export function candidatesAt(
	ds: Dataset,
	t: number,
	cutoff: number,
): Candidate[] {
	return ds.deals
		.filter((d) => openAt(d, t))
		.map((deal) => {
			const age = observedDuration(deal, t);
			const won =
				deal.stage === "Won" &&
				(deal.close as number) > t &&
				(deal.close as number) <= t + WINDOW_DAYS;
			return {
				deal,
				age,
				price: priceOf(ds, deal),
				stale: age > cutoff,
				revenue: won ? (deal.closeValue ?? 0) : 0,
			};
		});
}

/** A ordem de cada método para cada vendedor numa foto T (o que o backtest mede). */
export function rankAt(ds: Dataset, t: number, opts: BacktestOptions = {}) {
	const cutoff =
		opts.cutoff === "observed" ? maxCycleBy(ds.deals, t) : STALE_AFTER;
	const bands = (opts.bands ?? BANDS).filter((b) => b <= cutoff);
	const ctx: Context = {
		curve: chanceCurve(ds.deals, t, {
			bands,
			atRisk: opts.atRisk,
			cutoff,
			minEngage: opts.minEngage,
			truncation: opts.truncation,
		}),
		wrongChance: concludedOnlyByDay(ds.deals, t),
		cutoff,
		coolingFrom: opts.coolingFrom ?? 90,
	};
	const byAgent = Map.groupBy(candidatesAt(ds, t, cutoff), (c) => c.deal.agent);
	const agents = [...byAgent].sort(([a], [b]) => (a < b ? -1 : 1));
	return {
		cutoff,
		eligible: hasEnoughHistory(ctx.curve),
		agents: agents.map(([agent, cands]) => ({
			agent,
			cands,
			ranked: Object.fromEntries(
				METHOD_NAMES.map((m) => [m, METHODS[m](cands, ctx)]),
			) as Record<MethodName, Candidate[]>,
		})),
	};
}

export function runBacktest(
	ds: Dataset,
	opts: BacktestOptions = {},
): BacktestResult {
	const units: Unit[] = [];
	const cutoffs: number[] = [];
	const used: number[] = [];
	const onlyEligible =
		opts.onlyEligible ?? (opts.truncation ?? DEFAULT_TRUNCATION) !== "none";
	for (const t of opts.snapshots ?? SNAPSHOTS) {
		const r = rankAt(ds, t, opts);
		if (onlyEligible && !r.eligible) continue;
		used.push(t);
		cutoffs.push(r.cutoff);
		for (const { agent, cands, ranked } of r.agents) {
			const denominator = cands.reduce((s, c) => s + c.revenue, 0);
			const captured = Object.fromEntries(
				METHOD_NAMES.map((m) => [
					m,
					ranked[m].slice(0, TOP_N).reduce((s, c) => s + c.revenue, 0),
				]),
			) as Record<MethodName, number>;
			const randomExpected = Math.min(1, TOP_N / cands.length) * denominator;
			units.push({
				agent,
				t,
				candidates: cands.length,
				denominator,
				captured,
				randomExpected,
			});
		}
	}
	const total = units.reduce((s, u) => s + u.denominator, 0);
	const share = Object.fromEntries([
		...METHOD_NAMES.map((m) => [
			m,
			units.reduce((s, u) => s + u.captured[m], 0) / total,
		]),
		["random", units.reduce((s, u) => s + u.randomExpected, 0) / total],
	]) as BacktestResult["share"];
	return { units, share, cutoffs, snapshots: used };
}

/** Por vendedor, somando as datas: a unidade do teste pareado (as fotos se sobrepõem). */
export function perAgent(units: readonly Unit[], a: MethodName, b: MethodName) {
	const m = new Map<string, { a: number; b: number; den: number }>();
	for (const u of units) {
		const x = m.get(u.agent) ?? { a: 0, b: 0, den: 0 };
		x.a += u.captured[a];
		x.b += u.captured[b];
		x.den += u.denominator;
		m.set(u.agent, x);
	}
	return [...m.values()];
}
