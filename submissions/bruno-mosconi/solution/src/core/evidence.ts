// O que o "Como funciona" mostra (CA16): as três provas e as limitações, calculadas dos dados
// com as mesmas funções da auditoria. Só a captura do modelo de ML vem de fora: é a saída do
// analysis/significancia_ml.py (semente 0), lida por vendedor e data.

import {
	calibrationAt,
	cohortByAgent,
	type Dimension,
	dimensionTest,
	quarterMonthEffect,
	winRateConcluded,
} from "./analysis.ts";
import { runBacktest, type Unit } from "./backtest.ts";
import { type Dataset, isoDate, rows } from "./data.ts";
import {
	firstCloseBy,
	observedDuration,
	openAt,
	REFERENCE_DATE,
	STALE_AFTER,
} from "./rules.ts";
import { pairedTest } from "./stats.ts";

/** Os fatores testados contra a chance de fechar, na ordem da tela. */
export const FACTORS: readonly { key: Dimension; label: string }[] = [
	{ key: "agent", label: "Vendedor" },
	{ key: "product", label: "Produto" },
	{ key: "regional", label: "Regional" },
	{ key: "sector", label: "Setor da empresa" },
	{ key: "accountEmployees", label: "Porte (funcionários)" },
	{ key: "accountRevenue", label: "Porte (receita)" },
];

const shareOf = (us: readonly Unit[], f: (u: Unit) => number) =>
	us.reduce((s, u) => s + f(u), 0) / us.reduce((s, u) => s + u.denominator, 0);

export function evidence(ds: Dataset, mlCsv: string) {
	// Prova 2: a lista no passado (regra final, só as datas com histórico suficiente).
	const bt = runBacktest(ds);
	const byDate = bt.snapshots.map((t) => {
		const us = bt.units.filter((u) => u.t === t);
		return {
			t,
			weighted: shareOf(us, (u) => u.captured.weighted),
			price: shareOf(us, (u) => u.captured.price),
			random: shareOf(us, (u) => u.randomExpected),
		};
	});
	const ml = new Map(rows(mlCsv).map((r) => [`${r.agent}|${r.t}`, r]));
	const mlUnits = bt.units.map((u) => {
		const r = ml.get(`${u.agent}|${isoDate(u.t)}`);
		if (!r || Math.abs(Number(r.den) - u.denominator) > 0.5)
			throw new Error(`ML sem a mesma unidade: ${u.agent}, ${isoDate(u.t)}`);
		return { agent: u.agent, ml: Number(r.ml_0), u };
	});
	// Unidade do teste pareado = vendedor, somando as datas (como na auditoria).
	const byAgent = [...Map.groupBy(mlUnits, (x) => x.agent).values()];
	const paired = (
		a: (x: (typeof mlUnits)[number]) => number,
		b: (x: (typeof mlUnits)[number]) => number,
	) =>
		pairedTest(
			byAgent.map((xs) => ({
				a: xs.reduce((s, x) => s + a(x), 0),
				b: xs.reduce((s, x) => s + b(x), 0),
				den: xs.reduce((s, x) => s + x.u.denominator, 0),
			})),
		);
	const weighted = (x: (typeof mlUnits)[number]) => x.u.captured.weighted;
	const backtest = {
		dates: byDate,
		weighted: bt.share.weighted,
		price: bt.share.price,
		random: bt.share.random,
		situationThenPrice: bt.share.situationThenPrice,
		all: bt.share,
		ml:
			mlUnits.reduce((s, x) => s + x.ml, 0) /
			bt.units.reduce((s, u) => s + u.denominator, 0),
		weightedVsPrice: paired(weighted, (x) => x.u.captured.price),
		weightedVsSituation: paired(
			weighted,
			(x) => x.u.captured.situationThenPrice,
		),
		mlVsWeighted: paired((x) => x.ml, weighted),
	};

	// Prova 3: os fatores, entre os concluídos (ganho ou perdido).
	const factors = FACTORS.map(({ key, label }) => {
		const r = dimensionTest(ds, key);
		return {
			key,
			label,
			rates: r.groups.map((g) => g.rate),
			p: r.chi.p,
			missing: r.missing,
		};
	});
	// Para o gestor: dos negócios iniciados há mais de 138 dias, quanto ainda está aberto (frio).
	const open = cohortByAgent(ds).map((a) => a.open / a.n);
	const agentCold = {
		min: Math.min(...open),
		max: Math.max(...open),
		p: dimensionTest(ds, "agent", "cohort").chi.p,
	};

	// Setor e porte só entre concluídos: "sem empresa" só acontece nos em andamento (vaza o desfecho).
	const inProgress = ds.deals.filter(
		(d) => d.stage === "Engaging" || d.stage === "Prospecting",
	);
	const noAccount = {
		inProgress:
			inProgress.filter((d) => d.account === null).length / inProgress.length,
		concluded: ds.deals.filter(
			(d) => (d.stage === "Won" || d.stage === "Lost") && d.account === null,
		).length,
	};

	// Limitações.
	const firstClose = firstCloseBy(ds.deals, REFERENCE_DATE) as number;
	const startedBefore = ds.deals.filter(
		(d) => d.engage !== null && d.engage < firstClose,
	).length;
	const calibration = bt.snapshots.map((t) => {
		const c = calibrationAt(ds, t);
		// Os que em 31/12 ainda podiam virar venda (abertos com até 138 dias): o teto da realizada.
		const stillOpen = ds.deals.filter(
			(d) =>
				openAt(d, t) &&
				observedDuration(d, t) <= STALE_AFTER &&
				openAt(d, REFERENCE_DATE) &&
				observedDuration(d, REFERENCE_DATE) <= STALE_AFTER,
		).length;
		return {
			t,
			n: c.n,
			predicted: c.predicted,
			realized: c.realized,
			stillOpen: stillOpen / c.n,
		};
	});
	const q = quarterMonthEffect(ds);

	return {
		backtest,
		factors,
		overallWinRate: winRateConcluded(ds).rate,
		agentCold,
		noAccount,
		truncation: { firstClose, startedBefore },
		calibration,
		quarter: {
			first: q.months[0]?.rate ?? 0,
			last: q.months[2]?.rate ?? 0,
			p: q.chi.p,
		},
	};
}

export type Evidence = ReturnType<typeof evidence>;
