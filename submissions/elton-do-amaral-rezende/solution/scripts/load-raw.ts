import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { rawDirectory } from './paths';
import { ingest } from '../src/domain/ingestion';
export async function loadRaw() {
  const read = (name: string) => readFile(join(rawDirectory, name), 'utf8');
  const [pipeline, accounts, products, teams] = await Promise.all(['sales_pipeline.csv', 'accounts.csv', 'products.csv', 'sales_teams.csv'].map(read));
  return ingest({ pipeline, accounts, products, teams });
}
