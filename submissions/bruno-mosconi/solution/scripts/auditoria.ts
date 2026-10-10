// npm run auditoria — recalcula cada afirmação numérica do material de partida (inventário N01–N41
// em process-log/01-revisao-inicial.md) e as hipóteses H1–H11. Grava:
//   analysis/saidas/auditoria-ts.md          (a tabela, versionada)
//   analysis/saidas/estatistica-entradas.json (entradas para conferir a estatística contra o scipy)

import { readFileSync, writeFileSync } from "node:fs";
import {
	accountGaps,
	agentRangeTests,
	agentRevenue,
	agentsWithoutDeals,
	agentsWithoutRecent,
	calibrationAt,
	closeValueFacts,
	cohortByAgent,
	cohortOutcomes,
	DIMENSIONS,
	type Dimension,
	dateFacts,
	dimensionTest,
	focusVsPriceOverlap,
	funnelAt,
	monthlyFlow,
	quarterMonthEffect,
	stageCounts,
	teamStatus,
	winRateConcluded,
	wonValueVsPrice,
} from "../src/core/analysis.ts";
import {
	METHOD_NAMES,
	type MethodName,
	perAgent,
	runBacktest,
	SNAPSHOTS,
} from "../src/core/backtest.ts";
import { day, isoDate, rows } from "../src/core/data.ts";
import { evidence } from "../src/core/evidence.ts";
import {
	agentLists,
	BANDS,
	chanceCurve,
	closedBy,
	concludedOnlyCurve,
	curveHalfWidth,
	MAX_HALF_WIDTH,
	maxCycleBy,
	observedDuration,
	openAt,
	REFERENCE_DATE,
	type Truncation,
} from "../src/core/rules.ts";
import { normalCi, pairedTest } from "../src/core/stats.ts";
import { loadDataset, readRaw } from "../src/node/load.ts";

const OUT = new URL("../analysis/saidas/", import.meta.url);
const ds = loadDataset();
const raw = readRaw();
const T = REFERENCE_DATE;

const int = (v: number) =>
	v.toLocaleString("pt-BR", { maximumFractionDigits: 0 });
const pct = (v: number, d = 1) =>
	`${(v * 100).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d })}%`;
const num = (v: number, d: number) =>
	v.toLocaleString("pt-BR", {
		minimumFractionDigits: d,
		maximumFractionDigits: d,
	});
const usd = (v: number) => `US$ ${int(v)}`;
const date = (d: number) => isoDate(d).split("-").reverse().join("/");

type Row = [
	id: string,
	claim: string,
	declared: string,
	recalculated: string,
	ok: boolean | null,
];
const table: Row[] = [];
const row = (
	id: string,
	claim: string,
	declared: string,
	recalculated: string,
	ok: boolean | null,
) => table.push([id, claim, declared, recalculated, ok]);
/** Monte Carlo com 10.000 sorteios: ±3 erros-padrão de uma fração perto de 0,5 (≈ 0,015). */
const MC_TOLERANCE = 3 * Math.sqrt((0.5 * 0.5) / 10_000);
/** Confere na precisão em que o número foi declarado. */
const same = (declared: number, actual: number, decimals = 0) =>
	Math.abs(Number(actual.toFixed(decimals)) - declared) < 1e-9;

// ---------- Dados (N01–N10)
const stages = stageCounts(ds);
const cv = closeValueFacts(ds);
const gaps = accountGaps(ds);
const facts = dateFacts(ds);
const noDeals = agentsWithoutDeals(ds);
const noRecent = agentsWithoutRecent(ds);
const gtxProRaw = rows(raw.salesPipeline).filter(
	(r) => r.product === "GTXPro",
).length;
const lastDate = Math.max(facts.lastEngage, facts.lastClose);

row(
	"N01",
	"vendedores; oportunidades",
	"35; ~8.800",
	`${ds.agents.length}; ${int(ds.deals.length)}`,
	ds.agents.length === 35 && ds.deals.length === 8800,
);
row(
	"N02",
	"close_value = 0 nos perdidos; vazio nos abertos",
	"2.473 de 2.473; vazio",
	`${int(cv.lostWithZero)} de ${int(cv.lost)}; vazio em ${int(cv.openWithEmpty)} de ${int(cv.open)}`,
	cv.lostWithZero === 2473 && cv.lost === 2473 && cv.openWithEmpty === cv.open,
);
row(
	"N03",
	"negócios; empresas; produtos; vendedores",
	"8.800; 85; 7; 35",
	`${int(ds.deals.length)}; ${ds.accounts.size}; ${ds.prices.size}; ${ds.agents.length}`,
	ds.deals.length === 8800 &&
		ds.accounts.size === 85 &&
		ds.prices.size === 7 &&
		ds.agents.length === 35,
);
row(
	"N04",
	"Won · Lost · Engaging · Prospecting",
	"4.238 · 2.473 · 1.589 · 500",
	`${int(stages.Won)} · ${int(stages.Lost)} · ${int(stages.Engaging)} · ${int(stages.Prospecting)}`,
	stages.Won === 4238 &&
		stages.Lost === 2473 &&
		stages.Engaging === 1589 &&
		stages.Prospecting === 500,
);
row("N05", 'linhas com "GTXPro"', "1.480", int(gtxProRaw), gtxProRaw === 1480);
row(
	"N06",
	"Prospecting com alguma data",
	"0",
	String(facts.prospectingWithAnyDate),
	facts.prospectingWithAnyDate === 0,
);
row(
	"N07",
	"em andamento sem empresa; concluídos sem empresa",
	"1.425 de 2.089; 0",
	`${int(gaps.openWithoutAccount)} de ${int(gaps.open)}; ${gaps.concludedWithoutAccount}`,
	gaps.openWithoutAccount === 1425 &&
		gaps.open === 2089 &&
		gaps.concludedWithoutAccount === 0,
);
row(
	"N08",
	"primeira data; última; 1º concluído; maior ciclo",
	"20/10/2016; 31/12/2017; 01/03/2017; 138",
	`${date(facts.firstEngage)}; ${date(lastDate)}; ${date(facts.firstClose)}; ${Math.max(facts.maxCycleWon, facts.maxCycleLost)} (ganhos ${facts.maxCycleWon}, perdidos ${facts.maxCycleLost})`,
	facts.firstEngage === day("2016-10-20") &&
		lastDate === day("2017-12-31") &&
		facts.firstClose === day("2017-03-01") &&
		Math.max(facts.maxCycleWon, facts.maxCycleLost) === 138,
);
row(
	"N09",
	"vendedores sem nenhum negócio",
	"5: Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova",
	`${noDeals.length}: ${[...noDeals].sort().join(", ")}`,
	[...noDeals].sort().join("|") ===
		"Carl Lin|Carol Thompson|Elizabeth Anderson|Mei-Mei Johns|Natalya Ivanova",
);
const onlyStaleOrProspect = noRecent.agents.filter(
	(a) => a.stale + a.prospecting > 0,
).length;
const nothingOpen = noRecent.agents.length - onlyStaleOrProspect;
row(
	"N10",
	"sem negócio recente em 31/12 (dos com histórico): só parados/prospecção; nada aberto",
	"9 de 30: 6; 3",
	`${noRecent.agents.length} de ${noRecent.withHistory}: ${onlyStaleOrProspect}; ${nothingOpen}`,
	noRecent.agents.length === 9 &&
		noRecent.withHistory === 30 &&
		onlyStaleOrProspect === 6 &&
		nothingOpen === 3,
);

// ---------- Curva (N12, N13)
// As linhas N conferem afirmações da preparação: usam a regra dela, sem correção do corte da base.
// A regra final (G1) tem seção própria no fim.
const PREP = { truncation: "none" } as const;
const PREP_BT = { truncation: "none", onlyEligible: false } as const;
const curve = chanceCurve(ds.deals, T, PREP);
const co = cohortOutcomes(ds, T);
const declaredCurve = [49.8, 46.4, 44.0, 32.9, 21.2, 9.1];
row(
	"N12",
	"chance por faixa 0·30·60·90·104·120",
	declaredCurve.map((v) => num(v, 1)).join(" · "),
	curve.map((c) => num(c.chance * 100, 1)).join(" · "),
	curve.every((c, i) => same(declaredCurve[i] as number, c.chance * 100, 1)),
);
row(
	"N12",
	"coorte: negócios; último início",
	"5.991; 15/08/2017",
	`${int(co.n)}; ${date(co.lastEngage)}`,
	co.n === 5991 && co.lastEngage === day("2017-08-15"),
);
const wrong = concludedOnlyCurve(ds.deals, T, [14, 90]);
row(
	"N13",
	"só concluídos: aos 14 e aos 90 dias",
	"68,7% · 71,1%",
	wrong.map((c) => pct(c.chance)).join(" · "),
	same(68.7, (wrong[0]?.chance ?? 0) * 100, 1) &&
		same(71.1, (wrong[1]?.chance ?? 0) * 100, 1),
);

// ---------- Funil em 31/12 (N14–N16, N20)
const f = funnelAt(ds, T, curve);
const s = f.slices;
const openPrice =
	s["no-prazo"].listPrice + s.esfriando.listPrice + s.parado.listPrice;
const openDeals = s["no-prazo"].deals + s.esfriando.deals + s.parado.deals;
const focusWeighted = s["no-prazo"].weighted + s.esfriando.weighted;
row(
	"N14",
	"no prazo · esfriando · parados (dos Engaging)",
	"110 · 188 · 1.291",
	`${s["no-prazo"].deals} · ${s.esfriando.deals} · ${int(s.parado.deals)}`,
	s["no-prazo"].deals === 110 &&
		s.esfriando.deals === 188 &&
		s.parado.deals === 1291,
);
row(
	"N15",
	"preço de lista dos Engaging; % parado (do valor); prospecção",
	"US$ 3,89 mi; 82%; US$ 1,07 mi",
	`US$ ${num(openPrice / 1e6, 2)} mi; ${pct(s.parado.listPrice / openPrice, 0)}; US$ ${num(f.prospecting.listPrice / 1e6, 2)} mi`,
	same(3.89, openPrice / 1e6, 2) &&
		same(82, (s.parado.listPrice / openPrice) * 100) &&
		same(1.07, f.prospecting.listPrice / 1e6, 2),
);
row(
	"N16",
	"valor ponderado (no prazo + esfriando)",
	"≈ US$ 195 mil",
	usd(focusWeighted),
	same(195, focusWeighted / 1000), // "≈ US$ 195 mil": confere na precisão declarada (milhares)
);
row(
	"N20",
	"US$ no prazo · esfriando · parado · prospecção",
	"227.651 · 465.914 · 3.198.664 · 1.073.986",
	`${int(s["no-prazo"].listPrice)} · ${int(s.esfriando.listPrice)} · ${int(s.parado.listPrice)} · ${int(f.prospecting.listPrice)}`,
	s["no-prazo"].listPrice === 227_651 &&
		s.esfriando.listPrice === 465_914 &&
		s.parado.listPrice === 3_198_664 &&
		f.prospecting.listPrice === 1_073_986,
);
row(
	"N20",
	'"82% dos negócios com data" (P5): % dos negócios × % do valor',
	"82% dos negócios",
	`${pct(s.parado.deals / openDeals)} dos negócios; ${pct(s.parado.listPrice / openPrice)} do valor`,
	same(82, (s.parado.deals / openDeals) * 100),
);
row(
	"N21",
	"nenhum concluído depois de 138 dias",
	"0",
	String(
		[...ds.deals].filter(
			(d) => d.close !== null && d.close - (d.engage as number) > 138,
		).length,
	),
	facts.maxCycleWon <= 138 && facts.maxCycleLost <= 138,
);

// ---------- Taxa de ganho e coorte (N24, N25)
const wr = winRateConcluded(ds);
const nci = normalCi(wr.won, wr.n);
row(
	"N24",
	"taxa de ganho entre concluídos; IC 95%",
	"63,15%; 62,0–64,3%",
	`${pct(wr.rate, 2)}; Wilson ${num(wr.wilson[0] * 100, 1)}–${num(wr.wilson[1] * 100, 1)}% (normal ${num(nci[0] * 100, 1)}–${num(nci[1] * 100, 1)}%)`,
	same(63.15, wr.rate * 100, 2) &&
		same(62.0, wr.wilson[0] * 100, 1) &&
		same(64.3, wr.wilson[1] * 100, 1),
);
row(
	"N25",
	"de cada 100 iniciados: ganhos · perdidos · nunca concluídos",
	"50 · 29 · 22",
	`${num((co.won / co.n) * 100, 1)} · ${num((co.lost / co.n) * 100, 1)} · ${num((co.open / co.n) * 100, 1)} (coorte de ${int(co.n)})`,
	same(50, (co.won / co.n) * 100) &&
		same(29, (co.lost / co.n) * 100) &&
		same(22, (co.open / co.n) * 100),
);

// ---------- O que não muda a taxa (N11, N26–N29)
const dimNames: Record<Dimension, string> = {
	agent: "vendedor",
	manager: "gestor",
	regional: "regional",
	product: "produto",
	sector: "setor",
	account: "empresa",
	accountRevenue: "receita da empresa (quartis)",
	accountEmployees: "funcionários da empresa (quartis)",
};
const declaredP: Partial<Record<Dimension, number>> = {
	agent: 0.264,
	manager: 0.786,
	regional: 0.604,
	product: 0.372,
	sector: 0.971,
	account: 0.943,
};
const dimResults = Object.fromEntries(
	DIMENSIONS.map((d) => [d, dimensionTest(ds, d)]),
) as Record<Dimension, ReturnType<typeof dimensionTest>>;
for (const d of DIMENSIONS) {
	const decl = declaredP[d];
	if (decl === undefined) continue;
	const r = dimResults[d];
	row(
		"N26",
		`p do qui-quadrado: ${dimNames[d]}`,
		num(decl, 3),
		`${num(r.chi.p, 3)} (χ² = ${num(r.chi.statistic, 2)}, ${r.chi.df} g.l.)`,
		same(decl, r.chi.p, 3),
	);
}
const rangeTests = agentRangeTests(ds);
row(
	"N27",
	"melhor − pior vendedor; % dos sorteios ≥",
	"15,4 p.p.; 36–38%",
	`${num(rangeTests.count.observed * 100, 1)} p.p.; ${pct(rangeTests.count.shareAtLeast)} (10.000 sorteios, semente 20171231)`,
	same(15.4, rangeTests.count.observed * 100, 1) &&
		rangeTests.count.shareAtLeast >= 0.355 &&
		rangeTests.count.shareAtLeast <= 0.385,
);
row(
	"N28",
	"em valor: diferença; % dos sorteios ≥",
	"23,5 p.p.; ~41%",
	`${num(rangeTests.value.observed * 100, 1)} p.p.; ${pct(rangeTests.value.shareAtLeast)}`,
	same(23.5, rangeTests.value.observed * 100, 1) &&
		Math.abs(rangeTests.value.shareAtLeast - 0.41) <= MC_TOLERANCE,
);
const rev = agentRevenue(ds);
row(
	"N29",
	"receita: maior ÷ menor; Spearman com volume; com taxa",
	"9,3×; 0,62; −0,21",
	`${num(rev.maxOverMin, 1)}×; ${num(rev.spearmanVolume, 2)}; ${num(rev.spearmanWinRate, 2)}`,
	same(9.3, rev.maxOverMin, 1) &&
		same(0.62, rev.spearmanVolume, 2) &&
		same(-0.21, rev.spearmanWinRate, 2),
);
const q = quarterMonthEffect(ds);
row(
	"N30",
	"taxa por mês do trimestre: 1º · 2º · 3º",
	"49,0 · 54,7 · 80,7",
	q.months.map((m) => num(m.rate * 100, 1)).join(" · "),
	q.months.every((m, i) =>
		same([49.0, 54.7, 80.7][i] as number, m.rate * 100, 1),
	),
);

// ---------- Backtest (N17, N32, N39)
const bt = runBacktest(ds, PREP_BT);
const declaredBt: Record<MethodName | "random", number> = {
	weighted: 44.41,
	situationThenPrice: 43.35,
	priceNoStale: 40.1,
	price: 36.17,
	concludedOnly: 32.23,
	random: 15.4,
};
const methodLabel: Record<MethodName | "random", string> = {
	weighted: "valor ponderado",
	situationThenPrice: 'situação e preço ("faixas e preço")',
	priceNoStale: "preço sem parados",
	price: "só preço",
	concludedOnly: "chance só com concluídos",
	random: "aleatório",
};
for (const m of [...METHOD_NAMES, "random"] as const) {
	row(
		"N17",
		`backtest: ${methodLabel[m]}`,
		`${num(declaredBt[m], 2)}%`,
		pct(bt.share[m], 2),
		same(declaredBt[m], bt.share[m] * 100, 2),
	);
}
row(
	"N39",
	"métodos no backtest",
	"6",
	String(METHOD_NAMES.length + 1),
	METHOD_NAMES.length + 1 === 6,
);
// N18: o ML vem do Python (analysis/significancia_ml.py); o teste pareado é o mesmo do H3.
const mlRows = rows(readFileSync(new URL("ml-por-vendedor.csv", OUT), "utf8"));
const unitKey = (agent: string, t: number) => `${agent}|${isoDate(t)}`;
const btByUnit = new Map(bt.units.map((u) => [unitKey(u.agent, u.t), u]));
const sameUniverse = mlRows.every(
	(r) => btByUnit.get(`${r.agent}|${r.t}`)?.denominator === Number(r.den),
);
const mlTotal = mlRows.reduce((s, r) => s + Number(r.den), 0);
const mlShare = (col: string) =>
	mlRows.reduce((s, r) => s + Number(r[col]), 0) / mlTotal;
const mlSeeds = Object.keys(mlRows[0] ?? {}).filter((k) => k.startsWith("ml_"));
const mlPaired = (other: (r: Record<string, string>) => number) =>
	pairedTest(
		[...Map.groupBy(mlRows, (r) => r.agent ?? "").values()].map((rs) => ({
			a: rs.reduce((s, r) => s + Number(r.ml_0), 0),
			b: rs.reduce((s, r) => s + other(r), 0),
			den: rs.reduce((s, r) => s + Number(r.den), 0),
		})),
	);
const mlVsDay = mlPaired((r) => Number(r.ev_dia));
const mlVsD5 = mlPaired(
	(r) => btByUnit.get(`${r.agent}|${r.t}`)?.captured.weighted ?? Number.NaN,
);
const mlByDay = mlShare("ev_dia");
row(
	"N18",
	"ML 45,0% × valor ponderado 44,6% (exploratório)",
	"45,0 · 44,6",
	`ML ${mlSeeds.map((k) => pct(mlShare(k), 2)).join(" = ")} (${mlSeeds.length} sementes) · valor ponderado por dia exato ${pct(mlByDay, 2)}; mesmo universo do backtest: ${sameUniverse ? "sim" : "NÃO"}`,
	// O exploratório imprime com 1 casa e não desempata pelo ID; aqui há desempate. Tolerância de 0,1 p.p.
	Math.abs(mlShare("ml_0") * 100 - 45.0) <= 0.1 &&
		Math.abs(mlByDay * 100 - 44.6) <= 0.1 &&
		sameUniverse,
);
const sqlIds = new Set(
	readFileSync(new URL("../auditoria_sql.py", OUT), "utf8").match(/Q\d\d/g) ??
		[],
);
row(
	"N40",
	'"21 consultas" em auditoria_sql.py',
	"21",
	`${sqlIds.size} (Q01–Q21, mais a Q12b)`,
	sqlIds.size === 21,
);

// ---------- Hipóteses
const lines: string[] = [];
const h = (s: string) => lines.push(s);
const btLine = (label: string, r: ReturnType<typeof runBacktest>) =>
	`| ${label} | ${[...METHOD_NAMES, "random"].map((m) => pct(r.share[m as MethodName], 2)).join(" | ")} |`;
const btHeader = `| Variante | ${[...METHOD_NAMES, "random"].map((m) => methodLabel[m as MethodName]).join(" | ")} |\n|---|${"---|".repeat(METHOD_NAMES.length + 1)}`;

h("### H1, H2, H11 e sensibilidade: o backtest muda com as escolhas?\n");
h(btHeader);
h(btLine("reconciliado (faixas do AGENTS, corte 138, em risco com >)", bt));
h(
	btLine(
		"H1: faixas de 30 em 30 dias",
		runBacktest(ds, {
			...PREP_BT,
			bands: [0, 30, 60, 90, 120],
		}),
	),
);
h(
	btLine(
		"H1: chance por dia exato",
		runBacktest(ds, {
			...PREP_BT,
			bands: Array.from({ length: 139 }, (_, i) => i),
		}),
	),
);
const btObserved = runBacktest(ds, {
	...PREP_BT,
	cutoff: "observed",
});
h(btLine("H2: corte = maior ciclo observado em T", btObserved));
h(
	btLine(
		"pré-registrado no C1: em risco com ≥",
		runBacktest(ds, {
			...PREP_BT,
			atRisk: ">=",
		}),
	),
);
h(
	btLine(
		"situação com a fronteira da preparação (esfriando a partir de 91)",
		runBacktest(ds, {
			...PREP_BT,
			coolingFrom: 91,
		}),
	),
);
h(
	btLine(
		"H11: só as fotos de 31/08 e 30/09",
		runBacktest(ds, {
			...PREP_BT,
			snapshots: SNAPSHOTS.slice(2),
		}),
	),
);
h(
	btLine(
		"H11: curva só com iniciados a partir de 01/03/2017",
		runBacktest(ds, {
			...PREP_BT,
			minEngage: day("2017-03-01"),
		}),
	),
);
h("");
h(
	`H2: maior ciclo observado em cada foto: ${SNAPSHOTS.map((t, i) => `${date(t)} = ${btObserved.cutoffs[i]}`).join("; ")}; em 31/12/2017 = ${maxCycleBy(ds.deals, T)}.`,
);
const late = ds.deals.filter(
	(d) => d.engage !== null && d.engage >= day("2017-03-01") && d.close !== null,
);
h(
	`H11: maior ciclo entre os iniciados a partir de 01/03/2017 = ${Math.max(...late.map((d) => (d.close as number) - (d.engage as number)))} (${int(late.length)} concluídos).`,
);
h(
	`H11: iniciados em 2016 = ${int(ds.deals.filter((d) => d.engage !== null && d.engage < day("2017-01-01")).length)}; em jan–fev/2017 = ${int(ds.deals.filter((d) => d.engage !== null && d.engage >= day("2017-01-01") && d.engage < day("2017-03-01")).length)}.`,
);
const lateCurve = chanceCurve(ds.deals, T, {
	...PREP,
	minEngage: day("2017-03-01"),
});
h(
	`H11: curva em 31/12 só com iniciados a partir de 01/03/2017: ${lateCurve.map((c) => `${c.from}: ${pct(c.chance)} (${int(c.atRisk)})`).join(" · ")}.`,
);
h(
	`Curva reconciliada (>) em 31/12, com n em risco: ${curve.map((c) => `${c.from}: ${pct(c.chance)} (${int(c.atRisk)})`).join(" · ")}.`,
);
h(
	`Pré-registrado no C1 (≥): ${chanceCurve(ds.deals, T, {
		...PREP,
		atRisk: ">=",
	})
		.map((c) => `${c.from}: ${pct(c.chance)}`)
		.join(" · ")}.`,
);
const curveGe = chanceCurve(ds.deals, T, { ...PREP, atRisk: ">=" });
const fGe = funnelAt(ds, T, curveGe);
const wrongGe = concludedOnlyCurve(ds.deals, T, [14, 90], ">=");
h(
	`Pré-registrado no C1 (≥) nos números que divergiam: N13 só concluídos aos 14 e 90 dias = ${wrongGe.map((c) => pct(c.chance, 2)).join(" · ")}; N16 valor ponderado = ${usd(fGe.slices["no-prazo"].weighted + fGe.slices.esfriando.weighted)}.`,
);
h(
	`H11: coorte de cada foto com a curva só de iniciados a partir de 01/03/2017: ${SNAPSHOTS.map((t) => `${date(t)} = ${int(chanceCurve(ds.deals, t, { ...PREP, minEngage: day("2017-03-01") })[0]?.atRisk ?? 0)}`).join("; ")} (coorte vazia = chance 0 para todos = ordem pelo ID).`,
);
h(
	btLine(
		"H11: curva limpa (iniciados a partir de 01/03/2017), só 31/08 e 30/09",
		runBacktest(ds, {
			...PREP_BT,
			snapshots: SNAPSHOTS.slice(2),
			minEngage: day("2017-03-01"),
		}),
	),
);
h(
	"\nCalibração: chance prevista pela curva em T para os abertos com até 138 dias × fração ganha até 31/12/2017\n\n| Foto | Curva | Coorte | Abertos | Prevista | Realizada | Por faixa (prevista → realizada, n) |\n|---|---|---|---|---|---|---|",
);
for (const t of SNAPSHOTS.slice(1, 3)) {
	for (const [label, o] of [
		["cheia", PREP],
		["limpa (desde 01/03/2017)", { truncation: "clean" }],
	] as const) {
		const c = calibrationAt(ds, t, T, o);
		h(
			`| ${date(t)} | ${label} | ${int(c.cohort)} | ${int(c.n)} | ${pct(c.predicted)} | ${pct(c.realized)} | ${c.bands.map((b) => `${b.from}: ${pct(b.predicted, 0)} → ${pct(b.realized, 0)} (${b.n})`).join(" · ")} |`,
		);
	}
}
h(
	"\nH11: inícios e conclusões por mês\n\n| Mês | Inícios | Ganhos concluídos | Perdidos concluídos |\n|---|---|---|---|",
);
for (const m of monthlyFlow(ds))
	h(`| ${m.month} | ${int(m.started)} | ${int(m.won)} | ${int(m.lost)} |`);
h("");
h(
	`Curva "só concluídos" nas mesmas faixas: ${concludedOnlyCurve(ds.deals, T)
		.map((c) => `${c.from}: ${pct(c.chance)}`)
		.join(" · ")}.`,
);
h("");

h("### H3 e H4: o ganho do valor ponderado é real? A métrica discrimina?\n");
h(
	"| Comparação (unidade = vendedor, 4 fotos somadas) | Diferença | IC 95% (bootstrap) | p (troca de sinais) |\n|---|---|---|---|",
);
const paired: Record<string, ReturnType<typeof pairedTest>> = {};
const pairedInputs: Record<string, ReturnType<typeof perAgent>> = {};
for (const other of [
	"priceNoStale",
	"situationThenPrice",
	"price",
	"concludedOnly",
] as const) {
	const units = perAgent(bt.units, "weighted", other);
	const r = pairedTest(units);
	paired[other] = r;
	pairedInputs[other] = units;
	h(
		`| valor ponderado − ${methodLabel[other]} | ${num(r.difference * 100, 2)} p.p. | ${num(r.ci95[0] * 100, 2)} a ${num(r.ci95[1] * 100, 2)} p.p. | ${num(r.pSignFlip, 4)} |`,
	);
}
h(
	`| ML (semente 0) − valor ponderado por dia exato (mesmo script) | ${num(mlVsDay.difference * 100, 2)} p.p. | ${num(mlVsDay.ci95[0] * 100, 2)} a ${num(mlVsDay.ci95[1] * 100, 2)} p.p. | ${num(mlVsDay.pSignFlip, 4)} |`,
);
h(
	`| ML (semente 0) − valor ponderado por faixas (D5) | ${num(mlVsD5.difference * 100, 2)} p.p. | ${num(mlVsD5.ci95[0] * 100, 2)} a ${num(mlVsD5.ci95[1] * 100, 2)} p.p. | ${num(mlVsD5.pSignFlip, 4)} |`,
);
h("");
for (const [i, t] of SNAPSHOTS.entries()) {
	const us = bt.units.filter((u) => u.t === t);
	const counts = us.map((u) => u.candidates).sort((a, b) => a - b);
	h(
		`H4 ${date(t)}: ${us.length} vendedores; abertos por vendedor de ${counts[0]} a ${counts[counts.length - 1]} (mediana ${counts[Math.floor(counts.length / 2)]}); com 10 ou menos: ${counts.filter((c) => c <= 10).length}. Corte: ${bt.cutoffs[i]}.`,
	);
}
h("");

h("### H5 e H9: as dimensões no desfecho da coorte, e o tamanho da empresa\n");
h(
	"| Dimensão | p (concluídos) | p (coorte) | grupos | sem o atributo (concluídos) | maior − menor taxa |\n|---|---|---|---|---|---|",
);
for (const d of DIMENSIONS) {
	const a = dimResults[d];
	const b = dimensionTest(ds, d, "cohort");
	const rates = a.groups.map((g) => g.rate);
	h(
		`| ${dimNames[d]} | ${num(a.chi.p, 3)} | ${num(b.chi.p, 3)} | ${a.groups.length} | ${int(a.missing)} | ${num((Math.max(...rates) - Math.min(...rates)) * 100, 1)} p.p. |`,
	);
}
h(
	"\nH5: coorte de 31/12 por vendedor (o efeito está no que fica aberto, não na taxa entre concluídos)\n\n| Vendedor | Coorte | Ganho | Aberto | Ganho entre concluídos |\n|---|---|---|---|---|",
);
for (const r of cohortByAgent(ds))
	h(
		`| ${r.agent} | ${int(r.n)} | ${pct(r.won / r.n)} | ${pct(r.open / r.n)} | ${pct(r.won / (r.won + r.lost))} |`,
	);
h(
	`\nH9: negócios em andamento sem empresa (logo, sem receita e funcionários): ${int(gaps.openWithoutAccount)} de ${int(gaps.open)} (${pct(gaps.openWithoutAccount / gaps.open)}). Por etapa: ${Object.entries(
		gaps.byStage,
	)
		.map(([k, v]) => `${k} ${int(v.withoutAccount)}/${int(v.total)}`)
		.join("; ")}.`,
);
h(`Mês do trimestre: χ² p = ${q.chi.p.toExponential(2)}.`);
h("");

h("### H6, H7, H8, H10\n");
const wv = wonValueVsPrice(ds);
h(
	`H6: close_value ÷ preço de lista nos ${int(wv.n)} ganhos: mínimo ${num(wv.min, 2)}, máximo ${num(wv.max, 2)}, média ${num(wv.mean, 3)}; dentro de ±10%: ${pct(wv.within10pct)}.`,
);
h(
	`H7: maior ciclo dos ganhos = ${facts.maxCycleWon}; dos perdidos = ${facts.maxCycleLost}. Engaging com data de conclusão: ${facts.engagingWithClose}.`,
);
h(
	`H8: "de cada 10" por faixa: ${curve.map((c) => `${c.from}: ${pct(c.chance)} → ${Math.round(c.chance * 10)}`).join(" · ")}.`,
);
const ov = focusVsPriceOverlap(ds);
h(
	`H10 (31/12): vendedores com "Foque agora" não vazia = ${ov.length}; tamanho da lista de ${Math.min(...ov.map((o) => o.focus))} a ${Math.max(...ov.map((o) => o.focus))}; dos 10 primeiros por valor ponderado, em média ${num((ov.reduce((s, o) => s + o.overlap / o.of, 0) / ov.length) * 100, 1)}% também são os 10 mais caros; listas idênticas em ${ov.filter((o) => o.overlap === o.of).length} vendedores.`,
);
const sectors = [
	...new Set([...ds.accounts.values()].map((a) => a.sector)),
].sort();
h(`Setores grafados no accounts.csv: ${sectors.join(", ")}.`);

// ---------- Regra final (G1)
h("\n## Regra final (G1): a coorte e o corte da base\n");
const RULES: [Truncation, string][] = [
	[
		"lateEntry",
		"entrada tardia: todos, cada um a partir da idade que tinha em 01/03/2017 (regra final)",
	],
	[
		"clean",
		"limpa: só iniciados a partir da primeira conclusão observada (sensibilidade)",
	],
	["none", "sem correção (regra da preparação)"],
];
h(
	`Data disponível = toda faixa com IC 95% (Wilson) de no máximo ±${num(MAX_HALF_WIDTH * 100, 0)} p.p.\n`,
);
h(
	`| Regra | ${[...SNAPSHOTS, T].map(date).join(" | ")} |\n|---|${"---|".repeat(SNAPSHOTS.length + 1)}`,
);
for (const [tr, label] of RULES)
	h(
		`| ${label} | ${[...SNAPSHOTS, T]
			.map((t) => {
				const c = chanceCurve(ds.deals, t, { truncation: tr });
				const w = curveHalfWidth(c);
				return `faixa 0: ${int(c[0]?.atRisk ?? 0)} em risco; ${w >= 1 ? "faixa vazia" : `±${num(w * 100, 2)} p.p.`}${w <= MAX_HALF_WIDTH ? " ✓" : ""}`;
			})
			.join(" | ")} |`,
	);
h("\nCurva em 31/12/2017 (chance por faixa 0 · 30 · 60 · 90 · 104 · 120):\n");
for (const [tr, label] of RULES)
	h(
		`- ${label}: ${chanceCurve(ds.deals, T, { truncation: tr })
			.map((c) => pct(c.chance))
			.join(" · ")}; valor ponderado (no prazo + esfriando) ${usd(
			(() => {
				const ff = funnelAt(
					ds,
					T,
					chanceCurve(ds.deals, T, { truncation: tr }),
				);
				return ff.slices["no-prazo"].weighted + ff.slices.esfriando.weighted;
			})(),
		)}`,
	);
h(
	'\nBacktest só nas datas disponíveis, e teste pareado (unidade = vendedor). O CA3 pede o ganho sobre "só preço", com IC.\n',
);
h(
	"| Regra | Fotos | Valor ponderado | Situação e preço | Só preço | Ponderado − só preço | Ponderado − situação e preço | Ponderado − preço sem parados |\n|---|---|---|---|---|---|---|---|",
);
for (const [tr, label] of RULES) {
	const r = runBacktest(ds, { truncation: tr });
	const pt = (o: MethodName) => {
		const x = pairedTest(perAgent(r.units, "weighted", o));
		return `${num(x.difference * 100, 2)} p.p. (IC ${num(x.ci95[0] * 100, 2)} a ${num(x.ci95[1] * 100, 2)}; p ${num(x.pSignFlip, 4)})`;
	};
	h(
		`| ${label} | ${r.snapshots.map(date).join(", ")} | ${pct(r.share.weighted, 2)} | ${pct(r.share.situationThenPrice, 2)} | ${pct(r.share.price, 2)} | ${pt("price")} | ${pt("situationThenPrice")} | ${pt("priceNoStale")} |`,
	);
}
{
	// O mesmo número do "Como funciona" (src/core/evidence.ts): o ML de analysis/significancia_ml.py
	// (semente 0) nas mesmas unidades vendedor × data do backtest da regra final.
	const b = evidence(
		ds,
		readFileSync(
			new URL("../analysis/saidas/ml-por-vendedor.csv", import.meta.url),
			"utf8",
		),
	).backtest;
	const x = b.mlVsWeighted;
	h(
		`\nModelo de ML na regra final (${b.dates.map((d) => date(d.t)).join(", ")}): ${pct(b.ml, 2)} contra ${pct(b.weighted, 2)} do valor ponderado; ML − ponderado = ${num(x.difference * 100, 2)} p.p. (IC ${num(x.ci95[0] * 100, 2)} a ${num(x.ci95[1] * 100, 2)}; p ${num(x.pSignFlip, 4)}). Captura na regra final: ${METHOD_NAMES.map((m) => `${m} ${pct(b.all[m], 2)}`).join(" · ")} · aleatório ${pct(b.random, 2)}. Por data, ponderado · só preço · aleatório: ${b.dates.map((d) => `${date(d.t)} ${pct(d.weighted, 2)} · ${pct(d.price, 2)} · ${pct(d.random, 2)}`).join("; ")}.`,
	);
}
{
	// Retrato por regional em 31/12/2017: onde estão as prioridades e a prospecção (achado do Bruno).
	const curve = chanceCurve(ds.deals, T);
	h(
		"\nPor regional em 31/12/2017 (vendedores; negócios quentes e esfriando; vendedores sem nenhum; prospecção; % frio do valor em andamento com data):\n",
	);
	h(
		"| Regional | Vendedores | Quentes e esfriando | Sem prioridade | Prospecção | Frio |\n|---|---|---|---|---|---|",
	);
	for (const r of [...new Set(ds.agents.map((a) => a.regional))].sort()) {
		const names = ds.agents.filter((a) => a.regional === r).map((a) => a.name);
		const lists = names.map((n) => agentLists(ds, T, n, curve));
		const st = teamStatus(ds, T, names, curve);
		const cold = st.reduce((x, a) => x + a.slices.parado.listPrice, 0);
		const all = st.reduce(
			(x, a) =>
				x +
				a.slices["no-prazo"].listPrice +
				a.slices.esfriando.listPrice +
				a.slices.parado.listPrice,
			0,
		);
		h(
			`| ${r} | ${names.length} | ${int(lists.reduce((x, l) => x + l.focus.length, 0))} | ${lists.filter((l) => !l.focus.length).length} | ${int(lists.reduce((x, l) => x + l.prospect.length, 0))} | ${pct(cold / all)} |`,
		);
	}
}
h(
	'\nCalibração: prevista pela curva em T × ganha até 31/12/2017, para os abertos com até 138 dias. "Ainda podiam concluir" são os que, em 31/12, estavam abertos com até 138 dias: o teto supõe que todos virariam venda.\n',
);
h(
	"| Foto | Abertos | Realizada | Ainda podiam concluir | Teto | Prevista: limpa | Prevista: entrada tardia | Prevista: sem correção |\n|---|---|---|---|---|---|---|---|",
);
for (const t of SNAPSHOTS.slice(1)) {
	const open = ds.deals.filter(
		(d) => openAt(d, t) && observedDuration(d, t) <= 138,
	);
	const unresolved = open.filter(
		(d) => !closedBy(d, T) && observedDuration(d, T) <= 138,
	).length;
	const cal = (tr: Truncation) => calibrationAt(ds, t, T, { truncation: tr });
	const real = cal("clean").realized;
	h(
		`| ${date(t)} | ${int(open.length)} | ${pct(real)} | ${int(unresolved)} (${pct(unresolved / open.length)}) | ${pct(real + unresolved / open.length)} | ${pct(cal("clean").predicted)} | ${pct(cal("lateEntry").predicted)} | ${pct(cal("none").predicted)} |`,
	);
}
h("");

// ---------- Saída
const statusText = (ok: boolean | null) =>
	ok === null ? "pendente" : ok ? "confere" : "**diverge**";
const md = [
	"# Auditoria dos números do material de partida (TypeScript)",
	"",
	`Gerado por \`npm run auditoria\` a partir de \`solution/data/\`. Data de referência: ${date(T)}. Faixas: ${BANDS.join(", ")}.`,
	"",
	"| ID | Afirmação | Declarado | Recalculado | Status |",
	"|---|---|---|---|---|",
	...table.map(
		([id, claim, decl, rec, ok]) =>
			`| ${id} | ${claim} | ${decl} | ${rec} | ${statusText(ok)} |`,
	),
	"",
	`Conferem: ${table.filter((r) => r[4] === true).length}. Divergem: ${table.filter((r) => r[4] === false).length}. Pendentes: ${table.filter((r) => r[4] === null).length}.`,
	"",
	"## Hipóteses",
	"",
	...lines,
	"",
].join("\n");
writeFileSync(new URL("auditoria-ts.md", OUT), md);

const tables = Object.fromEntries(
	DIMENSIONS.flatMap((d) => [
		[`concluded:${d}`, dimResults[d].groups.map((g) => [g.won, g.n - g.won])],
		[
			`cohort:${d}`,
			dimensionTest(ds, d, "cohort").groups.map((g) => [g.won, g.n - g.won]),
		],
	]),
);
tables.quarterMonth = q.months.map((m) => [m.won, m.n - m.won]);
const done = ds.deals.filter((d) => d.stage === "Won" || d.stage === "Lost");
const agentNames = [...new Set(done.map((d) => d.agent))].sort();
writeFileSync(
	new URL("estatistica-entradas.json", OUT),
	JSON.stringify({
		chi2Grid: [0.1, 1, 3.841458820694124, 10, 25.5, 60, 120].flatMap((x) =>
			[1, 2, 5, 29, 84].map((df) => [x, df]),
		),
		tables,
		wilson: [
			[wr.won, wr.n],
			[5, 10],
			[1, 50],
		],
		spearman: {
			volume: [
				rev.rows.map((r) => r.revenue),
				rev.rows.map((r) => r.concluded),
			],
			winRate: [rev.rows.map((r) => r.revenue), rev.rows.map((r) => r.winRate)],
		},
		permutation: {
			group: done.map((d) => agentNames.indexOf(d.agent)),
			y: done.map((d) => (d.stage === "Won" ? 1 : 0)),
			ours: rangeTests.count,
		},
		paired: Object.fromEntries(
			Object.entries(pairedInputs).map(([k, units]) => [
				k,
				{ units, ours: paired[k] },
			]),
		),
	}),
);
console.log(md);
