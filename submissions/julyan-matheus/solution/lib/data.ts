import fs from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";
import type { Account, Deal, DealStage, Product, SalesAgent } from "./types";
import { normalizeProduct } from "./scoring";

const DATA_DIR = path.join(process.cwd(), "data");

function readCsv(file: string): Record<string, string>[] {
  const raw = fs.readFileSync(path.join(DATA_DIR, file), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true, trim: true });
}

const emptyToNull = (s: string): string | null => (s === "" ? null : s);
const numOrNull = (s: string): number | null => (s === "" ? null : Number(s));

export function loadDeals(): Deal[] {
  return readCsv("sales_pipeline.csv").map((r) => ({
    opportunity_id: r.opportunity_id,
    sales_agent: r.sales_agent,
    product: normalizeProduct(r.product),
    account: emptyToNull(r.account),
    deal_stage: r.deal_stage as DealStage,
    engage_date: emptyToNull(r.engage_date),
    close_date: emptyToNull(r.close_date),
    close_value: numOrNull(r.close_value),
  }));
}

export function loadProducts(): Product[] {
  return readCsv("products.csv").map((r) => ({
    product: normalizeProduct(r.product),
    series: r.series,
    sales_price: Number(r.sales_price),
  }));
}

export function loadAccounts(): Account[] {
  return readCsv("accounts.csv").map((r) => ({
    account: r.account,
    sector: r.sector,
    year_established: Number(r.year_established),
    revenue: Number(r.revenue),
    employees: Number(r.employees),
    office_location: r.office_location,
    subsidiary_of: emptyToNull(r.subsidiary_of),
  }));
}

export function loadSalesTeams(): SalesAgent[] {
  return readCsv("sales_teams.csv").map((r) => ({
    sales_agent: r.sales_agent,
    manager: r.manager,
    regional_office: r.regional_office,
  }));
}

export function loadAll() {
  return {
    deals: loadDeals(),
    products: loadProducts(),
    accounts: loadAccounts(),
    salesTeams: loadSalesTeams(),
  };
}
