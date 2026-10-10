// Números da investigação: a auditoria (scripts/auditoria.ts) e a página "Como funciona" usam
// estas mesmas funções, para não haver uma segunda versão da regra.

import { SNAPSHOTS } from "./backtest.ts";
import { type Dataset, type Deal, priceOf } from "./data.ts";
import {
	agentLists,
	type BandChance,
	type CurveOptions,
	chanceCurve,
	chanceForAge,
	closedBy,
	hasEnoughHistory,
	observedDuration,
	openAt,
	REFERENCE_DATE,
	type Situation,
	STALE_AFTER,
	scoreOpen,
	situation,
	wonBy,
} from "./rules.ts";
import {
	type ChiSquareResult,
	chiSquare,
	permutationRange,
	spearman,
	wilson,
} from "./stats.ts";

const isConcluded = (d: Deal) => d.stage === "Won" || d.stage === "Lost";
const isOpen = (d: Deal) => d.stage === "Engaging" || d.stage === "Prospecting";

export function stageCounts(ds: Dataset): Record<Deal["stage"], number> {
	const c = { Won: 0, Lost: 0, Engaging: 0, Prospecting: 0 };
	for (const d of ds.deals) c[d.stage]++;
	return c;
}

export function dateFacts(ds: Dataset) {
	const engages = ds.deals.flatMap((d) =>
		d.engage === null ? [] : [d.engage],
	);
	const closes = ds.deals.flatMap((d) => (d.close === null ? [] : [d.close]));
	const cycles = (stage: Deal["stage"]) =>
		ds.deals
			.filter((d) => d.stage === stage)
			.map((d) => (d.close as number) - (d.engage as number));
	return {
		firstEngage: Math.min(...engages),
		lastEngage: Math.max(...engages),
		firstClose: Math.min(...closes),
		lastClose: Math.max(...closes),
		maxCycleWon: Math.max(...cycles("Won")),
		maxCycleLost: Math.max(...cycles("Lost")),
		prospectingWithAnyDate: ds.deals.filter(
			(d) => d.stage === "Prospecting" && (d.engage ?? d.close) !== null,
		).length,
		engagingWithClose: ds.deals.filter(
			(d) => d.stage === "Engaging" && d.close !== null,
		).length,
	};
}

export function accountGaps(ds: Dataset) {
	const open = ds.deals.filter(isOpen);
	const byStage = Object.fromEntries(
		(["Won", "Lost", "Engaging", "Prospecting"] as const).map((s) => {
			const all = ds.deals.filter((d) => d.stage === s);
			return [
				s,
				{
					total: all.length,
					withoutAccount: all.filter((d) => d.account === null).length,
				},
			];
		}),
	) as Record<Deal["stage"], { total: number; withoutAccount: number }>;
	return {
		open: open.length,
		openWithoutAccount: open.filter((d) => d.account === null).length,
		concludedWithoutAccount: ds.deals.filter(
			(d) => isConcluded(d) && d.account === null,
		).length,
		byStage,
	};
}

export function closeValueFacts(ds: Dataset) {
	const lost = ds.deals.filter((d) => d.stage === "Lost");
	const open = ds.deals.filter(isOpen);
	return {
		lost: lost.length,
		lostWithZero: lost.filter((d) => d.closeValue === 0).length,
		open: open.length,
		openWithEmpty: open.filter((d) => d.closeValue === null).length,
	};
}

/** H6: o valor dos ganhos comparado com o preço de lista. */
export function wonValueVsPrice(ds: Dataset) {
	const ratios = ds.deals
		.filter((d) => d.stage === "Won")
		.map((d) => (d.closeValue as number) / priceOf(ds, d));
	ratios.sort((a, b) => a - b);
	return {
		n: ratios.length,
		min: ratios[0] as number,
		max: ratios[ratios.length - 1] as number,
		mean: ratios.reduce((s, v) => s + v, 0) / ratios.length,
		within10pct:
			ratios.filter((r) => Math.abs(r - 1) <= 0.1).length / ratios.length,
	};
}

export const agentsWithoutDeals = (ds: Dataset): string[] =>
	ds.agents
		.map((a) => a.name)
		.filter((n) => !ds.deals.some((d) => d.agent === n));

/** Vendedores com histórico e sem nenhum negócio em andamento recente (≤ 138 dias) em T. */
export function agentsWithoutRecent(ds: Dataset, t = REFERENCE_DATE) {
	const withHistory = ds.agents
		.map((a) => a.name)
		.filter((n) => ds.deals.some((d) => d.agent === n));
	const curve = chanceCurve(ds.deals, t);
	const result = withHistory.flatMap((agent) => {
		const l = agentLists(ds, t, agent, curve);
		if (l.focus.length > 0) return [];
		return [{ agent, stale: l.review.length, prospecting: l.prospect.length }];
	});
	return { withHistory: withHistory.length, agents: result };
}

export interface FunnelSlice {
	deals: number;
	listPrice: number;
	weighted: number;
}

const emptySlices = (): Record<Situation, FunnelSlice> => ({
	"no-prazo": { deals: 0, listPrice: 0, weighted: 0 },
	esfriando: { deals: 0, listPrice: 0, weighted: 0 },
	parado: { deals: 0, listPrice: 0, weighted: 0 },
});

/**
 * Funil em andamento em T, por situação, a preço de lista; e a prospecção à parte (D13).
 * `agents` limita aos vendedores dos filtros da tela.
 */
export function funnelAt(
	ds: Dataset,
	t = REFERENCE_DATE,
	curve: readonly BandChance[] = chanceCurve(ds.deals, t),
	agents?: ReadonlySet<string>,
) {
	const slices = emptySlices();
	for (const s of scoreOpen(ds, t, curve)) {
		if (agents && !agents.has(s.deal.agent)) continue;
		const slice = slices[situation(s.age)];
		slice.deals++;
		slice.listPrice += s.price;
		slice.weighted += s.weighted;
	}
	const prospects =
		t === REFERENCE_DATE
			? ds.deals.filter(
					(d) => d.stage === "Prospecting" && (!agents || agents.has(d.agent)),
				)
			: [];
	return {
		slices,
		prospecting: {
			deals: prospects.length,
			listPrice: prospects.reduce((s, d) => s + priceOf(ds, d), 0),
		},
	};
}

export function winRateConcluded(ds: Dataset) {
	const done = ds.deals.filter(isConcluded);
	const won = done.filter((d) => d.stage === "Won").length;
	return {
		won,
		n: done.length,
		rate: won / done.length,
		wilson: wilson(won, done.length),
	};
}

/** "De cada 100 iniciados": a coorte em T dividida em ganho, perdido e ainda aberto. */
export function cohortOutcomes(ds: Dataset, t = REFERENCE_DATE) {
	const c = ds.deals.filter(
		(d) => d.engage !== null && d.engage <= t - STALE_AFTER,
	);
	const won = c.filter((d) => wonBy(d, t)).length;
	const lost = c.filter((d) => d.stage === "Lost" && closedBy(d, t)).length;
	return {
		n: c.length,
		won,
		lost,
		open: c.length - won - lost,
		lastEngage: Math.max(...c.map((d) => d.engage as number)),
	};
}

export type Dimension =
	| "agent"
	| "manager"
	| "regional"
	| "product"
	| "sector"
	| "account"
	| "accountRevenue"
	| "accountEmployees";

export const DIMENSIONS: readonly Dimension[] = [
	"agent",
	"manager",
	"regional",
	"product",
	"sector",
	"account",
	"accountRevenue",
	"accountEmployees",
];

/** Quartis calculados sobre as 85 empresas (não sobre os negócios). */
function quartileLabel(values: readonly number[]) {
	const sorted = [...values].sort((a, b) => a - b);
	const cut = (q: number) =>
		sorted[Math.floor(q * (sorted.length - 1))] as number;
	const [q1, q2, q3] = [cut(0.25), cut(0.5), cut(0.75)];
	return (v: number) =>
		v <= q1 ? "Q1" : v <= q2 ? "Q2" : v <= q3 ? "Q3" : "Q4";
}

export function dimensionKey(
	ds: Dataset,
	dim: Dimension,
): (d: Deal) => string | null {
	const agentOf = new Map(ds.agents.map((a) => [a.name, a]));
	const accounts = [...ds.accounts.values()];
	const revQ = quartileLabel(accounts.map((a) => a.revenue));
	const empQ = quartileLabel(accounts.map((a) => a.employees));
	const acc = (d: Deal) =>
		d.account === null ? undefined : ds.accounts.get(d.account);
	switch (dim) {
		case "agent":
			return (d) => d.agent;
		case "manager":
			return (d) => agentOf.get(d.agent)?.manager ?? null;
		case "regional":
			return (d) => agentOf.get(d.agent)?.regional ?? null;
		case "product":
			return (d) => d.product;
		case "sector":
			return (d) => acc(d)?.sector ?? null;
		case "account":
			return (d) => d.account;
		case "accountRevenue":
			return (d) => {
				const a = acc(d);
				return a ? revQ(a.revenue) : null;
			};
		case "accountEmployees":
			return (d) => {
				const a = acc(d);
				return a ? empQ(a.employees) : null;
			};
	}
}

export interface GroupRate {
	group: string;
	n: number;
	won: number;
	rate: number;
}

export interface DimensionResult {
	groups: GroupRate[];
	chi: ChiSquareResult;
	missing: number; // negócios sem o atributo (ex.: sem empresa)
}

/**
 * Taxa por grupo. "concluded": ganhos ÷ concluídos em 31/12/2017.
 * "cohort": ganhos ÷ coorte em T (aberto conta como não ganho), o desfecho que o score usa (H5).
 */
export function dimensionTest(
	ds: Dataset,
	dim: Dimension,
	outcome: "concluded" | "cohort" = "concluded",
	t = REFERENCE_DATE,
): DimensionResult {
	const key = dimensionKey(ds, dim);
	const base =
		outcome === "concluded"
			? ds.deals.filter(isConcluded)
			: ds.deals.filter(
					(d) => d.engage !== null && d.engage <= t - STALE_AFTER,
				);
	const map = new Map<string, { n: number; won: number }>();
	let missing = 0;
	for (const d of base) {
		const k = key(d);
		if (k === null) {
			missing++;
			continue;
		}
		const g = map.get(k) ?? { n: 0, won: 0 };
		g.n++;
		if (outcome === "concluded" ? d.stage === "Won" : wonBy(d, t)) g.won++;
		map.set(k, g);
	}
	const groups = [...map]
		.map(([group, g]) => ({ group, n: g.n, won: g.won, rate: g.won / g.n }))
		.sort((a, b) => b.rate - a.rate || (a.group < b.group ? -1 : 1));
	return {
		groups,
		chi: chiSquare(groups.map((g) => [g.won, g.n - g.won])),
		missing,
	};
}

/** Embaralhamento: a diferença entre o melhor e o pior vendedor, em quantidade e em valor de lista. */
export function agentRangeTests(
	ds: Dataset,
	iterations = 10_000,
	seed = 20171231,
) {
	const done = ds.deals.filter(isConcluded);
	const names = [...new Set(done.map((d) => d.agent))].sort();
	const group = done.map((d) => names.indexOf(d.agent));
	const y = done.map((d) => (d.stage === "Won" ? 1 : 0));
	const weights = done.map((d) => priceOf(ds, d));
	return {
		count: permutationRange(group, y, { iterations, seed }),
		value: permutationRange(group, y, { weights, iterations, seed }),
	};
}

/** Receita por vendedor: acompanha volume ou taxa de ganho? */
export function agentRevenue(ds: Dataset) {
	const names = [...new Set(ds.deals.map((d) => d.agent))].sort();
	const rows = names.map((agent) => {
		const mine = ds.deals.filter((d) => d.agent === agent && isConcluded(d));
		const won = mine.filter((d) => d.stage === "Won");
		return {
			agent,
			revenue: won.reduce((s, d) => s + (d.closeValue ?? 0), 0),
			concluded: mine.length,
			winRate: won.length / mine.length,
		};
	});
	const rev = rows.map((r) => r.revenue);
	return {
		rows,
		maxOverMin: Math.max(...rev) / Math.min(...rev),
		spearmanVolume: spearman(
			rev,
			rows.map((r) => r.concluded),
		),
		spearmanWinRate: spearman(
			rev,
			rows.map((r) => r.winRate),
		),
	};
}

/** Taxa de ganho pelo mês do trimestre em que o negócio foi concluído. */
export function quarterMonthEffect(ds: Dataset) {
	const out = [1, 2, 3].map((m) => ({ month: m, n: 0, won: 0, rate: 0 }));
	for (const d of ds.deals.filter(isConcluded)) {
		const month = new Date((d.close as number) * 86_400_000).getUTCMonth();
		const slot = out[month % 3] as (typeof out)[number];
		slot.n++;
		if (d.stage === "Won") slot.won++;
	}
	for (const s of out) s.rate = s.won / s.n;
	return { months: out, chi: chiSquare(out.map((s) => [s.won, s.n - s.won])) };
}

/** Inícios e conclusões por mês (S1 e H11: a base começa cortada). */
export function monthlyFlow(ds: Dataset) {
	const m = new Map<string, { started: number; won: number; lost: number }>();
	const slot = (d: number) => {
		const k = new Date(d * 86_400_000).toISOString().slice(0, 7);
		const x = m.get(k) ?? { started: 0, won: 0, lost: 0 };
		m.set(k, x);
		return x;
	};
	for (const d of ds.deals) {
		if (d.engage !== null) slot(d.engage).started++;
		if (d.close !== null) slot(d.close)[d.stage === "Won" ? "won" : "lost"]++;
	}
	return [...m]
		.sort(([a], [b]) => (a < b ? -1 : 1))
		.map(([month, x]) => ({ month, ...x }));
}

/** H5: a coorte de cada vendedor dividida em ganho, perdido e ainda aberto. */
export function cohortByAgent(ds: Dataset, t = REFERENCE_DATE) {
	const c = ds.deals.filter(
		(d) => d.engage !== null && d.engage <= t - STALE_AFTER,
	);
	return [...Map.groupBy(c, (d) => d.agent)]
		.map(([agent, deals]) => {
			const won = deals.filter((d) => wonBy(d, t)).length;
			const open = deals.filter((d) => !closedBy(d, t)).length;
			return {
				agent,
				n: deals.length,
				won,
				lost: deals.length - won - open,
				open,
			};
		})
		.sort(
			(a, b) => a.open / a.n - b.open / b.n || (a.agent < b.agent ? -1 : 1),
		);
}

/** H10: quantos dos 10 primeiros por valor ponderado também estão entre os 10 mais caros, por vendedor. */
export function focusVsPriceOverlap(ds: Dataset, t = REFERENCE_DATE) {
	const curve = chanceCurve(ds.deals, t);
	return ds.agents.flatMap((a) => {
		const focus = agentLists(ds, t, a.name, curve).focus;
		if (focus.length === 0) return [];
		const top = new Set(focus.slice(0, 10).map((s) => s.deal.id));
		const byPrice = [...focus].sort(
			(x, y) => y.price - x.price || (x.deal.id < y.deal.id ? -1 : 1),
		);
		const overlap = byPrice
			.slice(0, 10)
			.filter((s) => top.has(s.deal.id)).length;
		return [
			{
				agent: a.name,
				focus: focus.length,
				overlap,
				of: Math.min(10, focus.length),
			},
		];
	});
}

/**
 * Calibração: em t, a chance prevista pela curva para os abertos de cada faixa, contra a fração
 * que de fato virou venda até `until`. O backtest mede a ordem; isto mede se a frase "de cada 10"
 * acerta como probabilidade.
 */
export function calibrationAt(
	ds: Dataset,
	t: number,
	until = REFERENCE_DATE,
	opts: CurveOptions = {},
) {
	const curve = chanceCurve(ds.deals, t, opts);
	const open = ds.deals
		.filter((d) => openAt(d, t))
		.map((d) => ({ age: observedDuration(d, t), won: wonBy(d, until) }))
		.filter((x) => x.age <= STALE_AFTER);
	const bands = curve.map((c, i) => {
		const upTo = curve[i + 1]?.from ?? STALE_AFTER + 1;
		const g = open.filter((x) => x.age >= c.from && x.age < upTo);
		return {
			from: c.from,
			n: g.length,
			predicted: c.chance,
			realized: g.length ? g.filter((x) => x.won).length / g.length : 0,
		};
	});
	return {
		cohort: curve[0]?.atRisk ?? 0,
		n: open.length,
		predicted:
			open.reduce((s, x) => s + chanceForAge(curve, x.age), 0) / open.length,
		realized: open.filter((x) => x.won).length / open.length,
		bands,
	};
}

export interface AgentStatus {
	agent: string;
	slices: Record<Situation, FunnelSlice>;
	open: number; // negócios em andamento com data (no prazo + esfriando + parado)
	focus: number; // tamanho da "Foque agora" (no prazo + esfriando)
	prospecting: number; // só na data padrão (D13)
}

/**
 * Situação do funil por vendedor (D29): o retrato de cada carteira, não um ranking de desempenho.
 * Ordem: valor parado, maior primeiro (D12), depois nome.
 */
export function teamStatus(
	ds: Dataset,
	t: number,
	agents: readonly string[],
	curve: readonly BandChance[] = chanceCurve(ds.deals, t),
): AgentStatus[] {
	const byAgent = new Map<string, AgentStatus>(
		agents.map((agent) => [
			agent,
			{ agent, slices: emptySlices(), open: 0, focus: 0, prospecting: 0 },
		]),
	);
	for (const s of scoreOpen(ds, t, curve)) {
		const a = byAgent.get(s.deal.agent);
		if (!a) continue;
		const sit = situation(s.age);
		a.slices[sit].deals++;
		a.slices[sit].listPrice += s.price;
		a.slices[sit].weighted += s.weighted;
		a.open++;
		if (sit !== "parado") a.focus++;
	}
	if (t === REFERENCE_DATE)
		for (const d of ds.deals) {
			const a = byAgent.get(d.agent);
			if (a && d.stage === "Prospecting") a.prospecting++;
		}
	return [...byAgent.values()].sort(
		(a, b) =>
			b.slices.parado.listPrice - a.slices.parado.listPrice ||
			(a.agent < b.agent ? -1 : 1),
	);
}

/** Datas do seletor (D1, ajuste): as 4 fotos do backtest e a data padrão, com o critério da D27. */
export const availableDates = (ds: Dataset) =>
	[...SNAPSHOTS, REFERENCE_DATE].map((t) => ({
		t,
		available: hasEnoughHistory(chanceCurve(ds.deals, t)),
	}));
