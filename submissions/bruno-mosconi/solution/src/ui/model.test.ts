import { describe, expect, it } from "vitest";
import { availableDates } from "../core/analysis.ts";
import type { Deadline } from "../core/reason.ts";
import {
	chanceCurve,
	concludedOnlyCurve,
	REFERENCE_DATE,
} from "../core/rules.ts";
import { dataset } from "./dataset.ts";
import {
	dayModel,
	greeting,
	heroAction,
	LOW_SCORE,
	PEOPLE,
	sellerModel,
} from "./model.ts";

const today = dayModel(REFERENCE_DATE);

describe("herói com score baixo (D46)", () => {
	// Em 31/12, os três casos da base: nº 1 com score 0, 0 e 20, e prospecção à espera.
	it.each([
		["Anna Snelling", 0],
		["Versie Hillebrand", 0],
		["Lajuana Vencill", 20],
	])(
		"%s (score %i): o herói vira a prospecção e a ordem não muda",
		(name, score) => {
			const m = sellerModel(today, name);
			expect(m.focus[0]?.score).toBe(score);
			const a = heroAction(m, today.t);
			expect(a).toBe("prospeccao");
			expect(m.focus.map((d) => d.position)).toEqual(
				m.focus.map((_, i) => i + 1),
			);
			expect(greeting(m, a).lead).toBe("Comece pela prospecção.");
			// Sem prospecção (ex.: data passada), a ação é a dos frios.
			const semProspeccao = { ...m, prospect: [] };
			expect(heroAction(semProspeccao, today.t)).toBe("perda");
			expect(greeting(semProspeccao, "perda").lead).toBe(
				"Comece atualizando os frios.",
			);
		},
	);

	it.each(["Zane Levy", "Niesha Huffines"])(
		"%s: o nº 1 continua herói",
		(name) => {
			const m = sellerModel(today, name);
			expect(m.focus[0]?.score).toBeGreaterThanOrEqual(LOW_SCORE);
			expect(heroAction(m, today.t)).toBeNull();
		},
	);

	it("vale para todos: herói de ação só abaixo de 25, e só com prospecção ou frios", () => {
		for (const { t, available } of availableDates(dataset)) {
			if (!available) continue;
			const d = dayModel(t);
			for (const p of PEOPLE) {
				const m = sellerModel(d, p.name);
				const a = heroAction(m, t);
				const low = (m.focus[0]?.score ?? 100) < LOW_SCORE;
				if (!low) expect(a).toBeNull();
				if (a === "prospeccao") expect(t).toBe(REFERENCE_DATE);
				if (a === "perda") expect(m.review.length).toBeGreaterThan(0);
				if (low && !a) expect(m.prospect.length + m.review.length).toBe(0);
			}
		}
	});
});

describe("saudação (D47): conta só os 5 primeiros", () => {
	it("frase por tamanho da lista", () => {
		for (const p of PEOPLE) {
			const m = sellerModel(today, p.name);
			const a = heroAction(m, today.t);
			const g = greeting(m, a);
			const n = Math.min(5, m.focus.length);
			if (!n) expect(g.lead).toBe("");
			else if (a) continue;
			else if (n === 1)
				expect(g).toEqual({ lead: "Comece por este.", urg: "" });
			else {
				expect(g.lead).toBe(`Comece por estes ${n}.`);
				expect(g.urg).toMatch(
					/^(Destes, .+ nesta semana\.|Nenhum deles esfria nesta semana\.)$/,
				);
			}
		}
	});

	it("só os 5 primeiros contam: o 6º esfriando não muda a frase", () => {
		const base = sellerModel(today, "Zane Levy");
		const calm: Deadline = { kind: "esfria", days: 40 };
		const focus = base.focus.slice(0, 6).map((d, i) => ({
			...d,
			deadline: (i === 5 ? { kind: "esfria", days: 3 } : calm) as Deadline,
		}));
		expect(focus).toHaveLength(6);
		expect(greeting({ ...base, focus }, null).urg).toBe(
			"Nenhum deles esfria nesta semana.",
		);
		focus[1] = {
			...(focus[1] as (typeof focus)[number]),
			deadline: { kind: "parado", days: 2 },
		};
		expect(greeting({ ...base, focus }, null).urg).toBe(
			"Destes, 1 fica frio nesta semana.",
		);
	});

	it("os que esfriam fora dos 5 primeiros não entram na conta", () => {
		const m = sellerModel(today, "Zane Levy");
		const soon = (ds: typeof m.focus) =>
			ds.filter((d) => d.deadline?.kind === "esfria" && d.deadline.days <= 7)
				.length;
		const k = soon(m.focus.slice(0, 5));
		const g = greeting(m, null);
		if (k) expect(g.urg).toContain(`${k} esfria`);
		else expect(g.urg).not.toContain("esfriam");
	});
});

describe("prova 1: as frases fixas valem em todas as datas disponíveis", () => {
	it("a chance real nunca sobe com a idade; só com concluídos, ela termina acima de onde começa", () => {
		for (const { t, available } of availableDates(dataset)) {
			if (!available) continue;
			const real = chanceCurve(dataset.deals, t).map((b) => b.chance);
			for (let i = 1; i < real.length; i++)
				expect(real[i]).toBeLessThanOrEqual(real[i - 1] as number);
			const wrong = concludedOnlyCurve(dataset.deals, t).map((b) => b.chance);
			expect(wrong.at(-1)).toBeGreaterThan(wrong[0] as number);
		}
	});
});
