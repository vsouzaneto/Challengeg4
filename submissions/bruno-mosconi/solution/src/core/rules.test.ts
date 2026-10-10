// Casos pequenos calculados à mão: cada teste fixa uma definição pré-registrada.

import { describe, expect, it } from "vitest";
import type { Dataset, Deal, Stage } from "./data.ts";
import { day } from "./data.ts";
import {
	agentLists,
	bandIndex,
	chanceCurve,
	cohort,
	concludedOnlyByDay,
	concludedOnlyCurve,
	maxCycleBy,
	observedDuration,
	openAt,
	REFERENCE_DATE,
	situation,
} from "./rules.ts";

const T = day("2017-12-31");

let seq = 0;
function deal(
	stage: Stage,
	engage: number | null,
	close: number | null,
	extra: Partial<Deal> = {},
): Deal {
	seq++;
	return {
		id: `D${String(seq).padStart(3, "0")}`,
		agent: "Ana",
		product: "P",
		account: null,
		stage,
		engage,
		close,
		closeValue: stage === "Won" ? 100 : stage === "Lost" ? 0 : null,
		...extra,
	};
}

const ds = (
	deals: Deal[],
	prices: Record<string, number> = { P: 100 },
): Dataset => ({
	deals,
	accounts: new Map(),
	prices: new Map(Object.entries(prices)),
	agents: [{ name: "Ana", manager: "M", regional: "R" }],
});

describe("estado em T", () => {
	it("quem conclui depois de T está aberto em T, e a duração para em T", () => {
		const d = deal("Won", T - 10, T + 5);
		expect(openAt(d, T)).toBe(true);
		expect(observedDuration(d, T)).toBe(10);
	});

	it("idade 138 ainda é Esfriando; 139 é Parado; 89 é No prazo; 90 é Esfriando", () => {
		expect(situation(138)).toBe("esfriando");
		expect(situation(139)).toBe("parado");
		expect(situation(89)).toBe("no-prazo");
		expect(situation(90)).toBe("esfriando");
		expect(bandIndex(138)).toBe(5);
		expect(bandIndex(139)).toBe(-1);
		expect(bandIndex(103)).toBe(3);
		expect(bandIndex(104)).toBe(4);
	});

	it("maior ciclo só olha concluídos até T", () => {
		const deals = [
			deal("Won", T - 300, T - 200),
			deal("Lost", T - 100, T + 50),
		];
		expect(maxCycleBy(deals, T)).toBe(100);
	});
});

describe("coorte e chance por faixa", () => {
	// Iniciados há 200 dias (todos na coorte de T):
	// A ganho em 10 dias; B perdido em 40; C ganho em 95; D ainda aberto; E perdido em 0.
	const start = T - 200;
	const deals = [
		deal("Won", start, start + 10),
		deal("Lost", start, start + 40),
		deal("Won", start, start + 95),
		deal("Engaging", start, null),
		deal("Lost", start, start),
		deal("Won", T - 50, T - 10), // fora da coorte: iniciado depois de T − 138
	];

	it("coorte = iniciados até T − 138", () => {
		expect(cohort(deals, T)).toHaveLength(5);
	});

	it("em risco na faixa b = duração > b; aberto conta como não ganho", () => {
		const c = chanceCurve(deals, T);
		expect(c[0]).toMatchObject({ from: 0, atRisk: 4, won: 2 }); // E (0 dias) sai; A, C ganham
		expect(c[1]).toMatchObject({ from: 30, atRisk: 3, won: 1 }); // B(40), C(95), D(aberto)
		expect(c[3]).toMatchObject({ from: 90, atRisk: 2, won: 1 }); // C, D
		expect(c[5]).toMatchObject({ from: 120, atRisk: 1, won: 0 }); // só D
	});

	it("a definição pré-registrada '>=' inclui quem concluiu no próprio dia", () => {
		expect(chanceCurve(deals, T, { atRisk: ">=" })[0]).toMatchObject({
			atRisk: 5,
			won: 2,
		}); // E entra
	});

	it("anti-vazamento: mudar o que acontece depois de T não muda nada em T", () => {
		const t = start + 150;
		const before = deals.map((d) => ({ ...d }));
		const after = deals.map((d) =>
			d.close === null || d.close > t
				? { ...d, stage: "Won" as Stage, close: t + 1, closeValue: 999 }
				: d,
		);
		expect(chanceCurve(after, t)).toEqual(chanceCurve(before, t));
		expect(concludedOnlyCurve(after, t)).toEqual(concludedOnlyCurve(before, t));
	});

	it("só concluídos: o aberto some e a chance sobe (o viés)", () => {
		const c = concludedOnlyCurve(deals, T);
		expect(c[0]).toMatchObject({ atRisk: 4, won: 3 }); // A, B, C e o ganho de fora da coorte; E sai
		expect(c[3]).toMatchObject({ atRisk: 1, won: 1 }); // só C: 100%
	});

	it("só concluídos por dia: idade além do último dia com amostra usa esse dia", () => {
		const f = concludedOnlyByDay(deals, T, 2);
		// concluídos: A 10 W, B 40 L, C 95 W, E 0 L, F 40 W. Com ≥ 2 casos, o último dia é 39.
		expect(f(0)).toBeCloseTo(3 / 4, 12); // ciclo > 0: A, B, C, F
		expect(f(39)).toBeCloseTo(2 / 3, 12); // B, C, F
		expect(f(500)).toBeCloseTo(2 / 3, 12); // parado não vira 0 neste método
		expect(concludedOnlyByDay([], T)(10)).toBe(0);
	});
});

describe("listas do vendedor", () => {
	it("Foque agora por valor ponderado, empate pelo ID; parados na ordem da D21", () => {
		const start = T - 300;
		const history = [
			deal("Won", start, start + 10),
			deal("Lost", start, start + 20),
			deal("Won", start, start + 100),
			deal("Lost", start, start + 130),
		];
		// Coorte = 4 do histórico + s1, s2 e s3 (abertos, iniciados até T − 138).
		// Faixa 0: 2 ganhos em 7. Faixa 90: em risco h3(100), h4(130), s1, s2, s3 → 1 em 5.
		const x = deal("Engaging", T - 5, null, { id: "Z1", product: "Caro" });
		const y = deal("Engaging", T - 95, null, { id: "A1", product: "Caro" });
		const z = deal("Engaging", T - 6, null, { id: "B1", product: "Caro" });
		const s1 = deal("Engaging", T - 200, null, { id: "S1", product: "P" });
		const s2 = deal("Engaging", T - 300, null, { id: "S2", product: "P" });
		const s3 = deal("Engaging", T - 150, null, { id: "S3", product: "Caro" });
		const p1 = deal("Prospecting", null, null, { id: "P1", product: "P" });
		const p2 = deal("Prospecting", null, null, { id: "P2", product: "Caro" });
		const data = ds([...history, x, y, z, s1, s2, s3, p1, p2], {
			P: 100,
			Caro: 1000,
		});
		// Os dados de teste não têm o corte de 01/03/2017; o caso fixa a regra da lista, não a coorte.
		const curve = chanceCurve(data.deals, REFERENCE_DATE, {
			truncation: "none",
		});
		const l = agentLists(data, REFERENCE_DATE, "Ana", curve);
		// B1 e Z1 empatam (2/7 × 1000) e o ID desempata; A1 (95 dias) vale 1/5 × 1000.
		expect(l.focus.map((s) => s.deal.id)).toEqual(["B1", "Z1", "A1"]);
		expect(l.focus.map((s) => s.weighted)).toEqual([2000 / 7, 2000 / 7, 200]);
		expect(l.review.map((s) => s.deal.id)).toEqual(["S3", "S2", "S1"]); // preço; depois o mais antigo
		expect(l.prospect.map((d) => d.id)).toEqual(["P2", "P1"]);
		expect(agentLists(data, REFERENCE_DATE - 1, "Ana").prospect).toEqual([]); // D13
	});
});
