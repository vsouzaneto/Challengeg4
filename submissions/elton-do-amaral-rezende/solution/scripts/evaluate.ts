import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadRaw } from './load-raw';
import { generatedDirectory } from './paths';
import { evaluate } from '../src/domain/evaluation';

async function main() {
  const data = await loadRaw(), report = evaluate(data.opportunities, data.prices);
  await mkdir(generatedDirectory, { recursive: true });
  await writeFile(join(generatedDirectory, 'evaluation-report.json'), JSON.stringify(report, null, 2) + '\n');
  await writeFile(fileURLToPath(new URL('../src/data/evaluation.generated.json', import.meta.url)), JSON.stringify({ cutoff: report.cutoff, horizon: report.horizon, outcomes: report.outcomes, eligible: report.eligible, summary: report.summary.filter((r) => r.k === 10), limitations: report.limitations }, null, 2) + '\n');
  console.log(`Avaliação: ${report.historicalClosed} históricos, ${report.eligible} candidatos; ${report.outcomes.wins} Won, ${report.outcomes.losses} Lost e ${report.outcomes.censored} censurados.`);
  console.table(report.summary.filter((r) => r.k === 10).map((r) => ({ method: r.method, selected: r.selected, wins: r.wins, losses: r.losses, censored: r.censored, rate: r.resolvedWinRate?.toFixed(4), lift: r.lift?.toFixed(4) })));
}
main().catch((error: unknown) => { console.error(error instanceof Error ? error.message : error); process.exitCode = 1; });
