// O que a tela mostra de cada negócio, lido do núcleo. Nenhuma regra nova aqui.

import mlCsv from "../../analysis/saidas/ml-por-vendedor.csv?raw";
import { teamStatus } from "../core/analysis.ts";
import { type Deal, priceOf } from "../core/data.ts";
import { type Evidence, evidence } from "../core/evidence.ts";
import {
	chancePhrase,
	type Deadline,
	deadline,
	type EmptyFocus,
	emptyFocus,
	priceRanks,
	showAccount,
	shownPercent,
	shownWeighted,
} from "../core/reason.ts";
import {
	agentLists,
	type BandChance,
	bandForAge,
	chanceCurve,
	concludedOnlyCurve,
	REFERENCE_DATE,
	type ScoredDeal,
	STALE_AFTER,
	scoreOpen,
	situation,
} from "../core/rules.ts";
import { potentialScores } from "../core/score.ts";
import { dataset as ds } from "./dataset.ts";
import { plural } from "./format.ts";

export type Temp = "quente" | "esfriando" | "frio";

const TEMP = {
	"no-prazo": "quente",
	esfriando: "esfriando",
	parado: "frio",
} as const;
export const tempOf = (age: number): Temp => TEMP[situation(age)];

export interface DealView {
	id: string;
	product: string;
	/** Nas datas passadas fica oculta, e a falta dela também (D34): undefined = não mostrar nada. */
	account: string | null | undefined;
	age: number | null; // null = prospecção (sem data)
	price: number;
	percent: number; // chance de fechar, pelo histórico, em % inteira
	potential: number; // preço × percent, o mesmo número da conta
	score?: number; // só quentes e esfriando (D39)
	phrase: string;
	deadline: Deadline | null;
	position: number;
	priceRank?: number;
	temp: Temp | null;
}

export interface DayModel {
	t: number;
	curve: BandChance[];
	scores: Map<string, number>;
	scoreBase: number; // negócios quentes e esfriando da empresa nesta data
}

export function dayModel(t: number): DayModel {
	const curve = chanceCurve(ds.deals, t);
	const scores = potentialScores(scoreOpen(ds, t, curve));
	return { t, curve, scores, scoreBase: scores.size };
}

const WITH_DEALS = new Set(ds.deals.map((d) => d.agent));

export interface SellerModel {
	name: string;
	hasDeals: boolean;
	focus: DealView[];
	review: DealView[];
	prospect: DealView[];
	empty: EmptyFocus | null;
}

export function sellerModel(day: DayModel, name: string): SellerModel {
	const lists = agentLists(ds, day.t, name, day.curve);
	const ranks = priceRanks(lists.focus);
	const account = (d: Deal) => (showAccount(day.t) ? d.account : undefined);
	const scored = (s: ScoredDeal, i: number): DealView => ({
		id: s.deal.id,
		product: s.deal.product,
		account: account(s.deal),
		age: s.age,
		price: s.price,
		percent: shownPercent(s.chance),
		potential: shownWeighted(s),
		score: day.scores.get(s.deal.id),
		phrase: chancePhrase(bandForAge(day.curve, s.age)),
		deadline: deadline(s.age),
		position: i + 1,
		priceRank: ranks.get(s.deal.id),
		temp: tempOf(s.age),
	});
	const hasDeals = WITH_DEALS.has(name);
	return {
		name,
		hasDeals,
		focus: lists.focus.map(scored),
		review: lists.review.map(scored),
		prospect: lists.prospect.map((d, i) => ({
			id: d.id,
			product: d.product,
			account: account(d),
			age: null,
			price: priceOf(ds, d),
			percent: 0,
			potential: 0,
			phrase: "",
			deadline: null,
			position: i + 1,
			temp: null,
		})),
		empty: emptyFocus(lists, hasDeals),
	};
}

/**
 * D46 (regra de apresentação, não de score): se o nº 1 tem score abaixo de 25, o herói passa a
 * ser a ação que mais pesa na semana: a prospecção, se houver (só na data padrão, D13), ou os
 * frios. A ordem da lista não muda; o nº 1 vira um cartão normal.
 */
export const LOW_SCORE = 25;
export type HeroAction = "prospeccao" | "perda";

export function heroAction(m: SellerModel, t: number): HeroAction | null {
	const top = m.focus[0];
	if (!top || (top.score ?? 0) >= LOW_SCORE) return null;
	if (t === REFERENCE_DATE && m.prospect.length) return "prospeccao";
	return m.review.length ? "perda" : null;
}

/** A ação da semana (D46): quantos negócios, quanto somam a preço de lista e o título. */
export function actionInfo(m: SellerModel, a: HeroAction) {
	const list = a === "prospeccao" ? m.prospect : m.review;
	return {
		n: list.length,
		total: list.reduce((s, d) => s + d.price, 0),
		title:
			a === "prospeccao"
				? `${plural(list.length, "negócio", "negócios")} em prospecção para iniciar contato`
				: `${plural(list.length, "negócio frio", "negócios frios")} para atualizar ou dar perda`,
	};
}

/** Sem nada em andamento: nem prioridade, nem frio, nem prospecção. */
export const nothingOpen = (m: SellerModel) =>
	!m.focus.length && !m.review.length && !m.prospect.length;

/** O que a pessoa vai encontrar na semana dela, para a tela "Quem é você?". */
export function weekSummary(day: DayModel, name: string): string {
	const m = sellerModel(day, name);
	const a = heroAction(m, day.t);
	if (a === "prospeccao" || (!m.focus.length && m.prospect.length))
		return `Semana de prospecção: ${plural(m.prospect.length, "negócio", "negócios")}`;
	if (a === "perda")
		return `Semana de frios: ${plural(m.review.length, "negócio", "negócios")}`;
	if (m.focus.length)
		return plural(m.focus.length, "prioridade", "prioridades");
	if (m.review.length)
		return `Só negócios frios: ${plural(m.review.length, "negócio", "negócios")}`;
	return "Sem negócios em andamento";
}

/** A saudação (D47): conta só os 5 de "Comece por estes". */
export function greeting(
	m: SellerModel,
	action: HeroAction | null,
): { lead: string; urg: string } {
	const top = m.focus.slice(0, 5);
	if (!top.length) return { lead: "", urg: "" };
	if (action)
		return {
			lead:
				action === "prospeccao"
					? "Comece pela prospecção."
					: "Comece atualizando os frios.",
			urg: "",
		};
	if (top.length === 1) return { lead: "Comece por este.", urg: "" };
	const soon = (kind: Deadline["kind"]) =>
		top.filter((d) => d.deadline?.kind === kind && d.deadline.days <= 7).length;
	const cool = soon("esfria");
	const cold = soon("parado");
	const parts = [
		cool && `${cool} ${cool === 1 ? "esfria" : "esfriam"}`,
		cold && `${cold} ${cold === 1 ? "fica frio" : "ficam frios"}`,
	].filter(Boolean);
	return {
		lead: `Comece por estes ${top.length}.`,
		urg: parts.length
			? `Destes, ${parts.join(" e ")} nesta semana.`
			: "Nenhum deles esfria nesta semana.",
	};
}

export const teamOf = (manager: string) =>
	ds.agents.filter((a) => a.manager === manager).map((a) => a.name);

export const teamModel = (day: DayModel, manager: string) =>
	teamStatus(ds, day.t, teamOf(manager), day.curve);

export const PEOPLE = ds.agents;
export const MANAGERS = [...new Set(ds.agents.map((a) => a.manager))].map(
	(name) => ({
		name,
		regional: ds.agents.find((a) => a.manager === name)?.regional ?? "",
		team: teamOf(name).length,
	}),
);

/** O maior potencial exibido em qualquer uma das datas: a escala de tamanho dos pontos não muda com a data. */
export const maxPotential = (ts: readonly number[]) =>
	Math.max(
		...ts.flatMap((t) =>
			scoreOpen(ds, t, chanceCurve(ds.deals, t))
				.filter((s) => s.age <= STALE_AFTER)
				.map(shownWeighted),
		),
	);

let proofs: Evidence | undefined;
/** As provas do "Como funciona", calculadas uma vez, quando a página abre pela primeira vez. */
export const evidenceOnce = (): Evidence => {
	proofs ??= evidence(ds, mlCsv);
	return proofs;
};

/** O cálculo errado (só concluídos), para mostrar o engano na mesma data da regra. */
export const illusionCurve = (t: number) => concludedOnlyCurve(ds.deals, t);
