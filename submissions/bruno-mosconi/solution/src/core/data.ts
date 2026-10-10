// Leitura das 4 tabelas do CRM. O núcleo só conhece o contrato `Dataset`; quem o monta é um
// adaptador: `parseDataset` lê os CSVs do desafio (o app), `fromCrmJson` lê um JSON no formato de
// uma API de CRM (prova de que trocar a fonte não muda a regra, CA10). Os CSVs vêm sem aspas (um
// teste garante), então um split basta.

export type Stage = "Won" | "Lost" | "Engaging" | "Prospecting";

export interface Deal {
	id: string;
	agent: string;
	product: string; // já normalizado ("GTXPro" → "GTX Pro")
	account: string | null;
	stage: Stage;
	engage: number | null; // dia (dias desde 01/01/1970, UTC)
	close: number | null;
	closeValue: number | null;
}

export interface Account {
	name: string;
	sector: string;
	revenue: number; // milhões de US$ (metadata.csv)
	employees: number;
}

export interface Agent {
	name: string;
	manager: string;
	regional: string;
}

export interface Dataset {
	deals: Deal[];
	accounts: Map<string, Account>;
	prices: Map<string, number>;
	agents: Agent[];
}

export interface RawTables {
	accounts: string;
	products: string;
	salesPipeline: string;
	salesTeams: string;
}

const MS_PER_DAY = 86_400_000;

export const day = (iso: string): number =>
	Date.UTC(
		Number(iso.slice(0, 4)),
		Number(iso.slice(5, 7)) - 1,
		Number(iso.slice(8, 10)),
	) / MS_PER_DAY;

export const isoDate = (d: number): string =>
	new Date(d * MS_PER_DAY).toISOString().slice(0, 10);

export function rows(text: string): Record<string, string>[] {
	const lines = text.split(/\r?\n/).filter((l) => l !== "");
	const header = (lines[0] ?? "").split(",");
	return lines.slice(1).map((line, i) => {
		if (line.includes('"'))
			throw new Error(`linha ${i + 2} tem aspas; o parser não trata aspas`);
		const cells = line.split(",");
		if (cells.length !== header.length) {
			throw new Error(
				`linha ${i + 2} tem ${cells.length} colunas, esperado ${header.length}`,
			);
		}
		return Object.fromEntries(header.map((h, j) => [h, cells[j] ?? ""]));
	});
}

const PRODUCT_ALIASES: Record<string, string> = { GTXPro: "GTX Pro" };

const STAGES: readonly string[] = ["Won", "Lost", "Engaging", "Prospecting"];

const orNull = (s: string | undefined): string | null => (s ? s : null);

export function parseDataset(raw: RawTables): Dataset {
	const deals = rows(raw.salesPipeline).map((r): Deal => {
		const stage = r.deal_stage ?? "";
		if (!STAGES.includes(stage))
			throw new Error(`etapa desconhecida: ${stage}`);
		const product = r.product ?? "";
		const engage = orNull(r.engage_date);
		const close = orNull(r.close_date);
		const value = orNull(r.close_value);
		return {
			id: r.opportunity_id ?? "",
			agent: r.sales_agent ?? "",
			product: PRODUCT_ALIASES[product] ?? product,
			account: orNull(r.account),
			stage: stage as Stage,
			engage: engage === null ? null : day(engage),
			close: close === null ? null : day(close),
			closeValue: value === null ? null : Number(value),
		};
	});
	const accounts = new Map(
		rows(raw.accounts).map((r) => [
			r.account ?? "",
			{
				name: r.account ?? "",
				sector: r.sector ?? "",
				revenue: Number(r.revenue),
				employees: Number(r.employees),
			},
		]),
	);
	const prices = new Map(
		rows(raw.products).map((r) => [r.product ?? "", Number(r.sales_price)]),
	);
	const agents = rows(raw.salesTeams).map((r) => ({
		name: r.sales_agent ?? "",
		manager: r.manager ?? "",
		regional: r.regional_office ?? "",
	}));
	return { deals, accounts, prices, agents };
}

export function priceOf(ds: Dataset, d: Deal): number {
	const p = ds.prices.get(d.product);
	if (p === undefined) throw new Error(`produto sem preço: ${d.product}`);
	return p;
}

/** Um JSON como o de uma API de CRM: outros nomes de campo, datas ISO, preço junto do produto. */
export interface CrmJson {
	opportunities: {
		id: string;
		owner: string;
		product: string;
		account: string | null;
		stage: Stage;
		engagedAt: string | null; // "2017-10-20"
		closedAt: string | null;
		amount: number | null;
	}[];
	accounts: {
		name: string;
		sector: string;
		revenueMillions: number;
		employees: number;
	}[];
	products: { name: string; listPrice: number }[];
	team: { name: string; manager: string; office: string }[];
}

export function fromCrmJson(json: CrmJson): Dataset {
	return {
		deals: json.opportunities.map((o) => {
			if (!STAGES.includes(o.stage))
				throw new Error(`etapa desconhecida: ${o.stage}`);
			return {
				id: o.id,
				agent: o.owner,
				product: PRODUCT_ALIASES[o.product] ?? o.product,
				account: o.account,
				stage: o.stage,
				engage: o.engagedAt === null ? null : day(o.engagedAt),
				close: o.closedAt === null ? null : day(o.closedAt),
				closeValue: o.amount,
			};
		}),
		accounts: new Map(
			json.accounts.map((a) => [
				a.name,
				{
					name: a.name,
					sector: a.sector,
					revenue: a.revenueMillions,
					employees: a.employees,
				},
			]),
		),
		prices: new Map(json.products.map((p) => [p.name, p.listPrice])),
		agents: json.team.map((m) => ({
			name: m.name,
			manager: m.manager,
			regional: m.office,
		})),
	};
}
