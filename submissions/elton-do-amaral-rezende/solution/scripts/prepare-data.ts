import { createHash } from 'node:crypto';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { rawDirectory, generatedDirectory } from './paths';
import { ingest } from '../src/domain/ingestion';
import { historicalStats, rank, scoreOpportunity, scoringCandidate } from '../src/domain/scoring/engine';
import { SCORING_AS_OF_DATE, SCORING_RULE } from '../src/domain/config';

const requiredFiles = ['sales_pipeline.csv', 'accounts.csv', 'products.csv', 'sales_teams.csv'];
const json = (data: unknown) => JSON.stringify(data, null, 2) + '\n';
async function main() {
  const provenance = JSON.parse(await readFile(join(rawDirectory, 'provenance.json'), 'utf8')) as Record<string, unknown>;
  if (![provenance.sourceUrl, provenance.license, provenance.retrievedAt, provenance.datasetVersion].every((v) => typeof v === 'string' && v.trim())) throw new Error('Proveniência incompleta. Consulte data/raw/README.md.');
  const names = [...requiredFiles];
  try { await readFile(join(rawDirectory, 'metadata.csv')); names.push('metadata.csv'); } catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error; }
  const files = await Promise.all(names.map(async (name) => {
    const bytes = await readFile(join(rawDirectory, name));
    if (!bytes.length) throw new Error(`Arquivo vazio: ${name}`);
    return { name, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex'), contents: bytes.toString('utf8') };
  }));
  const contents = (name: string) => files.find((f) => f.name === name)!.contents;
  const data = ingest({ pipeline: contents('sales_pipeline.csv'), accounts: contents('accounts.csv'), products: contents('products.csv'), teams: contents('sales_teams.csv'), metadata: files.some((f) => f.name === 'metadata.csv') ? contents('metadata.csv') : undefined });
  const manifestFiles = files.map(({ contents: _contents, ...f }) => f);
  const datasetVersion = `${provenance.datasetVersion}-${createHash('sha256').update(JSON.stringify(manifestFiles)).digest('hex').slice(0, 16)}`;
  const stats = historicalStats(data.opportunities, SCORING_AS_OF_DATE);
  const opportunities = rank(data.opportunities.filter((o) => o.stage === 'Prospecting' || o.stage === 'Engaging').map((o) => scoreOpportunity(scoringCandidate(o, o.stage as 'Prospecting' | 'Engaging'), stats, data.prices)));
  await mkdir(generatedDirectory, { recursive: true });
  const preparedDirectory = fileURLToPath(new URL('../src/data/', import.meta.url));
  await mkdir(preparedDirectory, { recursive: true });
  await writeFile(join(generatedDirectory, 'raw-manifest.json'), json({ datasetVersion, provenance, files: manifestFiles }));
  await writeFile(join(generatedDirectory, 'quality-report.json'), json(data.quality));
  await writeFile(join(generatedDirectory, 'historical-statistics.json'), json(stats));
  await writeFile(join(preparedDirectory, 'opportunities.generated.json'), json({ datasetVersion, asOfDate: SCORING_AS_OF_DATE, rule: SCORING_RULE, agents: data.agents, opportunities, quality: data.quality }));
  console.log(`Dados preparados: ${data.opportunities.length} oportunidades, ${opportunities.length} abertas, ${data.quality.aliases} aliases. Versão: ${datasetVersion}`);
  console.log(`Vínculos desconhecidos: produto ${data.quality.unknownProducts.length}, conta ${data.quality.unknownAccounts.length}, vendedor ${data.quality.unknownSalesAgents.length}.`);
}
main().catch((error: unknown) => { console.error(error instanceof Error ? error.message : error); process.exitCode = 1; });
