import type { DayKey, DealStage } from './types';
export type CsvRow = Record<string, string>;
export interface Opportunity {
  opportunityId: string; salesAgent: string; product: string; originalProduct: string;
  account: string | null; sector: string | null; stage: DealStage;
  engageDate: DayKey | null; closeDate: DayKey | null; closeValue: number | null; catalogPriceUsd: number | null;
}
export interface SalesAgent { name: string; manager: string; region: string }
export interface QualityReport {
  rows: Record<string, number>; stages: Record<DealStage, number>; aliases: number;
  missingAccounts: number; missingEngageDates: number;
  unknownProducts: string[]; unknownAccounts: string[]; unknownSalesAgents: string[];
}
export function parseCsv(input: string): CsvRow[] {
  const text = input.replace(/^\uFEFF/, '');
  const rows: string[][] = [];
  let row: string[] = [], field = '', quoted = false, afterQuote = false;
  const pushField = () => { row.push(field); field = ''; afterQuote = false; };
  const pushRow = () => { pushField(); if (row.some((cell) => cell !== '')) rows.push(row); row = []; };
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') { quoted = false; afterQuote = true; }
      else field += c;
    } else if (c === ',') pushField();
    else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; pushRow(); }
    else if (c === '"') { if (field !== '' || afterQuote) throw new Error('CSV: aspas fora do início do campo.'); quoted = true; }
    else { if (afterQuote) throw new Error('CSV: conteúdo após fechamento das aspas.'); field += c; }
  }
  if (quoted) throw new Error('CSV: campo com aspas não encerradas.');
  if (field !== '' || row.length || afterQuote) pushRow();
  const headers = rows.shift()?.map((h) => h.trim());
  if (!headers?.length || headers.some((h) => !h) || new Set(headers).size !== headers.length) throw new Error('CSV: cabeçalho ausente, vazio ou duplicado.');
  return rows.map((values, i) => {
    if (values.length !== headers.length) throw new Error(`CSV: linha ${i + 2} possui ${values.length} campos; esperados ${headers.length}.`);
    return Object.fromEntries(headers.map((h, j) => [h, values[j].trim()]));
  });
}
export function validDate(value: string, field: string): DayKey | null {
  if (!value) return null;
  const parsed = new Date(`${value}T00:00:00Z`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) throw new Error(`Data inválida em ${field}: ${value}`);
  return value as DayKey;
}
function numberOrNull(value: string, field: string): number | null {
  if (!value) return null;
  const number = Number(value);
  if (!Number.isFinite(number) || number < 0) throw new Error(`Número inválido em ${field}: ${value}`);
  return number;
}
function requireColumns(rows: CsvRow[], columns: string[], file: string) {
  if (!rows.length) throw new Error(`Sem registros: ${file}`);
  for (const column of columns) if (!(column in rows[0])) throw new Error(`Coluna ausente em ${file}: ${column}`);
}
function uniqueMap(rows: CsvRow[], key: string, file: string) {
  const map = new Map<string, CsvRow>();
  for (const row of rows) { if (!row[key] || map.has(row[key])) throw new Error(`Chave vazia/duplicada em ${file}: ${row[key]}`); map.set(row[key], row); }
  return map;
}
export function ingest(files: { pipeline: string; accounts: string; products: string; teams: string; metadata?: string }) {
  const pipeline = parseCsv(files.pipeline), accounts = parseCsv(files.accounts), products = parseCsv(files.products), teams = parseCsv(files.teams);
  requireColumns(pipeline, ['opportunity_id', 'sales_agent', 'product', 'account', 'deal_stage', 'engage_date', 'close_date', 'close_value'], 'sales_pipeline.csv');
  requireColumns(accounts, ['account', 'sector', 'revenue'], 'accounts.csv');
  requireColumns(products, ['product', 'sales_price'], 'products.csv');
  requireColumns(teams, ['sales_agent', 'manager', 'regional_office'], 'sales_teams.csv');
  uniqueMap(pipeline, 'opportunity_id', 'sales_pipeline.csv');
  const accountMap = uniqueMap(accounts, 'account', 'accounts.csv'), productMap = uniqueMap(products, 'product', 'products.csv'), teamMap = uniqueMap(teams, 'sales_agent', 'sales_teams.csv');
  const quality: QualityReport = {
    rows: { pipeline: pipeline.length, accounts: accounts.length, products: products.length, teams: teams.length, metadata: files.metadata ? parseCsv(files.metadata).length : 0 },
    stages: { Prospecting: 0, Engaging: 0, Won: 0, Lost: 0 }, aliases: 0, missingAccounts: 0, missingEngageDates: 0,
    unknownAccounts: [], unknownProducts: [], unknownSalesAgents: [],
  };
  const opportunities: Opportunity[] = pipeline.map((row) => {
    const originalProduct = row.product, product = originalProduct === 'GTXPro' ? 'GTX Pro' : originalProduct;
    if (product !== originalProduct) quality.aliases++;
    const stage = row.deal_stage as DealStage;
    if (!Object.hasOwn(quality.stages, stage)) throw new Error(`Estágio inválido: ${stage}`);
    quality.stages[stage]++;
    const account = row.account || null;
    if (!account) quality.missingAccounts++; else if (!accountMap.has(account)) quality.unknownAccounts.push(account);
    if (!productMap.has(product)) quality.unknownProducts.push(product);
    if (!teamMap.has(row.sales_agent)) quality.unknownSalesAgents.push(row.sales_agent);
    const engageDate = validDate(row.engage_date, 'engage_date'), closeDate = validDate(row.close_date, 'close_date');
    if (!engageDate) quality.missingEngageDates++;
    if (engageDate && closeDate && closeDate < engageDate) throw new Error(`Fechamento anterior ao engajamento: ${row.opportunity_id}`);
    if ((stage === 'Won' || stage === 'Lost') && !closeDate) throw new Error(`Encerrado sem data: ${row.opportunity_id}`);
    return { opportunityId: row.opportunity_id, salesAgent: row.sales_agent, product, originalProduct, account, sector: account ? accountMap.get(account)?.sector || null : null, stage, engageDate, closeDate, closeValue: numberOrNull(row.close_value, 'close_value'), catalogPriceUsd: numberOrNull(productMap.get(product)?.sales_price ?? '', 'sales_price') };
  });
  for (const key of ['unknownAccounts', 'unknownProducts', 'unknownSalesAgents'] as const) quality[key] = [...new Set(quality[key])].sort();
  const agents: SalesAgent[] = teams.map((row) => ({ name: row.sales_agent, manager: row.manager, region: row.regional_office })).sort((a, b) => a.name.localeCompare(b.name));
  const prices = products.map((row) => numberOrNull(row.sales_price, 'sales_price')).filter((n): n is number => n !== null && n > 0);
  return { opportunities, quality, agents, prices };
}
