/** Prints the sanity checks required by docs/spec.md §10. Run: npm run sanity */
import { loadDeals, loadProducts } from "../lib/data";
import { buildStats, countBuckets, isScored, scorePipeline, todayPicks } from "../lib/scoring";

const deals = loadDeals();
const products = loadProducts();
const stats = buildStats(deals, products);
const rows = scorePipeline(deals, products);
const focar = rows.filter(isScored).sort((a, b) => b.score - a.score);
const scores = focar.map((x) => x.score);

console.log("Data de referência:", stats.ref, "| win rate global:", (stats.globalWinRate * 100).toFixed(1) + "%");
console.log("Baldes:", countBuckets(rows));
console.log(
  "Momentum por degrau:",
  [...stats.momentumCurve].map(([k, v]) => `≥${k}d → ${(v.winRate * 100).toFixed(0)}% (n=${v.sample})`).join(" | "),
);
console.log("Carga por vendedor min/média/max:", stats.loadMin, stats.loadMean.toFixed(1), stats.loadMax);
console.log("Score no Focar min/mediana/max:", Math.min(...scores), scores[Math.floor(scores.length / 2)], Math.max(...scores));

for (const x of [focar[0], focar[Math.floor(focar.length / 2)], focar[focar.length - 1]]) {
  console.log(
    `\n${x.deal.opportunity_id} | ${x.deal.sales_agent} | ${x.deal.product} | ${x.deal.account} | ${x.daysOpen} dias | score ${x.score} | valor esperado $${x.expectedValue}`,
  );
  for (const w of x.why) console.log(`  [${w.tone}] ${w.text}`);
}

console.log(
  "\nHoje (top 3 por valor esperado):",
  todayPicks(rows).map((x) => `${x.deal.opportunity_id} $${x.expectedValue} (score ${x.score})`).join(", "),
);
