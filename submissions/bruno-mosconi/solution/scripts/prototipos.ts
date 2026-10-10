// Dados reais para os protótipos de layout (process-log/prototipos/). Usa só funções do núcleo.
// Rodar: node scripts/prototipos.ts

import { writeFileSync } from "node:fs";
import { availableDates, funnelAt, teamStatus } from "../src/core/analysis.ts";
import { isoDate, priceOf } from "../src/core/data.ts";
import { deadline, priceRanks } from "../src/core/reason.ts";
import {
	agentLists,
	bandForAge,
	chanceCurve,
	REFERENCE_DATE,
	scoreOpen,
} from "../src/core/rules.ts";
import { potentialScores } from "../src/core/score.ts";
import { loadDataset } from "../src/node/load.ts";

const ds = loadDataset();
const MANAGER = "Summer Sewald";
const team = ds.agents.filter((a) => a.manager === MANAGER).map((a) => a.name);
const withDeals = new Set(ds.deals.map((d) => d.agent));

const dates = availableDates(ds).map(({ t, available }) => {
	const iso = isoDate(t);
	if (!available) return { iso, available };
	const curve = chanceCurve(ds.deals, t);
	const scores = potentialScores(scoreOpen(ds, t, curve));
	const showAccount = t === REFERENCE_DATE;
	const sellers = Object.fromEntries(
		team.map((name) => {
			const l = agentLists(ds, t, name, curve);
			const ranks = priceRanks(l.focus);
			const funnel = funnelAt(ds, t, curve, new Set([name]));
			return [
				name,
				{
					hasDeals: withDeals.has(name),
					funnel: funnel.slices,
					focus: l.focus.map((s, i) => {
						const band = bandForAge(curve, s.age);
						const pct = Math.round(s.chance * 100);
						return {
							id: s.deal.id,
							product: s.deal.product,
							account: showAccount ? s.deal.account : undefined,
							age: s.age,
							price: s.price,
							chance: pct,
							potential: Math.round(s.price * (pct / 100)),
							score: scores.get(s.deal.id),
							bandFrom: band?.from,
							deadline: deadline(s.age),
							position: i + 1,
							priceRank: ranks.get(s.deal.id),
						};
					}),
					review: l.review.map((s) => ({
						id: s.deal.id,
						product: s.deal.product,
						account: showAccount ? s.deal.account : undefined,
						age: s.age,
						price: s.price,
					})),
					prospect: l.prospect.map((d) => ({
						id: d.id,
						product: d.product,
						account: d.account,
						price: priceOf(ds, d),
					})),
				},
			];
		}),
	);
	return {
		iso,
		available,
		scoreBase: scores.size,
		team: teamStatus(ds, t, team, curve),
		teamFunnel: funnelAt(ds, t, curve, new Set(team)).slices,
		sellers,
	};
});

const out = new URL("../../process-log/prototipos/dados.js", import.meta.url);
writeFileSync(
	out,
	`// Gerado por solution/scripts/prototipos.ts a partir dos CSVs reais. Não editar.\nwindow.DADOS = ${JSON.stringify({ manager: MANAGER, dates })};\n`,
);
console.log(`ok: ${out.pathname}`);
