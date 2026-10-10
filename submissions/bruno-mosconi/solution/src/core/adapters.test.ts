// CA10: trocar a fonte não muda a regra. O JSON é montado das linhas cruas dos CSVs (com "GTXPro",
// datas em texto e outros nomes de campo), passa por JSON.stringify/parse e volta pelo adaptador.

import { describe, expect, it } from "vitest";
import { readRaw } from "../node/load.ts";
import { runBacktest } from "./backtest.ts";
import { type CrmJson, fromCrmJson, parseDataset, rows } from "./data.ts";
import { agentLists, chanceCurve, REFERENCE_DATE } from "./rules.ts";

const raw = readRaw();
const orNull = (s: string | undefined) => (s ? s : null);
const json: CrmJson = {
	opportunities: rows(raw.salesPipeline).map((r) => ({
		id: r.opportunity_id ?? "",
		owner: r.sales_agent ?? "",
		product: r.product ?? "",
		account: orNull(r.account),
		stage: r.deal_stage as CrmJson["opportunities"][number]["stage"],
		engagedAt: orNull(r.engage_date),
		closedAt: orNull(r.close_date),
		amount: r.close_value ? Number(r.close_value) : null,
	})),
	accounts: rows(raw.accounts).map((r) => ({
		name: r.account ?? "",
		sector: r.sector ?? "",
		revenueMillions: Number(r.revenue),
		employees: Number(r.employees),
	})),
	products: rows(raw.products).map((r) => ({
		name: r.product ?? "",
		listPrice: Number(r.sales_price),
	})),
	team: rows(raw.salesTeams).map((r) => ({
		name: r.sales_agent ?? "",
		manager: r.manager ?? "",
		office: r.regional_office ?? "",
	})),
};

describe("dois adaptadores, o mesmo resultado", () => {
	const fromCsv = parseDataset(raw);
	const fromJson = fromCrmJson(JSON.parse(JSON.stringify(json)));

	it("o Dataset é o mesmo", () => {
		expect(fromJson).toEqual(fromCsv);
	});

	it("as listas de todos os vendedores e o backtest são os mesmos", () => {
		const t = REFERENCE_DATE;
		const [ca, cb] = [
			chanceCurve(fromCsv.deals, t),
			chanceCurve(fromJson.deals, t),
		];
		expect(cb).toEqual(ca);
		for (const a of fromCsv.agents) {
			const ids = (l: ReturnType<typeof agentLists>) => [
				l.focus.map((s) => s.deal.id),
				l.review.map((s) => s.deal.id),
				l.prospect.map((d) => d.id),
			];
			expect(ids(agentLists(fromJson, t, a.name, cb)), a.name).toEqual(
				ids(agentLists(fromCsv, t, a.name, ca)),
			);
		}
		expect(runBacktest(fromJson).share).toEqual(runBacktest(fromCsv).share);
	});
});
