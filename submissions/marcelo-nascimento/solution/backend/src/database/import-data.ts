import type { PoolClient } from "pg";
import { resolve } from "node:path";
import { config } from "../config.js";
import { normalizeProduct, normalizeSector } from "../scoring/normalization.js";
import { hashPassword } from "../security.js";
import { numberValue, optional, readCsv, required } from "./csv.js";
import { pool } from "./pool.js";

const validStages = new Set(["Prospecting", "Engaging", "Won", "Lost"]);

function rowsInBatches<T>(rows: T[], size: number): T[][] {
  const batches: T[][] = [];
  for (let index = 0; index < rows.length; index += size) {
    batches.push(rows.slice(index, index + size));
  }
  return batches;
}

async function importAccounts(client: PoolClient): Promise<Map<string, number>> {
  const rows = await readCsv(resolve(config.dataDir, "accounts.csv"));

  for (const row of rows) {
    await client.query(
      `INSERT INTO accounts (name, sector, year_established, revenue, employees, office_location)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [
        required(row, "account", "accounts.csv"),
        normalizeSector(optional(row, "sector")),
        numberValue(optional(row, "year_established")),
        numberValue(optional(row, "revenue")),
        numberValue(optional(row, "employees")),
        optional(row, "office_location"),
      ],
    );
  }

  const { rows: ids } = await client.query<{ id: number; name: string }>("SELECT id, name FROM accounts");
  const idsByName = new Map(ids.map((row) => [row.name, row.id]));

  for (const row of rows) {
    const subsidiary = optional(row, "subsidiary_of");
    if (!subsidiary) {
      continue;
    }
    const accountName = required(row, "account", "accounts.csv");
    const accountId = idsByName.get(accountName);
    const subsidiaryId = idsByName.get(subsidiary);
    if (!accountId || !subsidiaryId) {
      throw new Error(`Invalid account relationship for ${accountName}`);
    }
    await client.query("UPDATE accounts SET subsidiary_id = $1 WHERE id = $2", [subsidiaryId, accountId]);
  }

  return idsByName;
}

async function importProducts(client: PoolClient): Promise<Map<string, number>> {
  const rows = await readCsv(resolve(config.dataDir, "products.csv"));
  const ids = new Map<string, number>();

  for (const batch of rowsInBatches(rows, 200)) {
    const values: unknown[] = [];
    const placeholders = batch.map((row, index) => {
      const offset = index * 3;
      values.push(
        required(row, "product", "products.csv"),
        required(row, "series", "products.csv"),
        numberValue(optional(row, "sales_price")),
      );
      return `($${offset + 1}, $${offset + 2}, $${offset + 3})`;
    });
    const result = await client.query<{ id: number; name: string }>(
      `INSERT INTO products (name, series, sales_price) VALUES ${placeholders.join(", ")} RETURNING id, name`,
      values,
    );
    result.rows.forEach((row) => ids.set(row.name, row.id));
  }

  return ids;
}

async function importSalesAgents(client: PoolClient): Promise<Map<string, number>> {
  const rows = await readCsv(resolve(config.dataDir, "sales_teams.csv"));
  const ids = new Map<string, number>();

  for (const batch of rowsInBatches(rows, 200)) {
    const values: unknown[] = [];
    const placeholders = batch.map((row, index) => {
      const offset = index * 3;
      values.push(
        required(row, "sales_agent", "sales_teams.csv"),
        optional(row, "manager"),
        optional(row, "regional_office"),
      );
      return `($${offset + 1}, $${offset + 2}, $${offset + 3})`;
    });
    const result = await client.query<{ id: number; name: string }>(
      `INSERT INTO sales_agents (name, manager, regional_office) VALUES ${placeholders.join(", ")} RETURNING id, name`,
      values,
    );
    result.rows.forEach((row) => ids.set(row.name, row.id));
  }

  return ids;
}

async function importOpportunities(
  client: PoolClient,
  accounts: Map<string, number>,
  products: Map<string, number>,
  agents: Map<string, number>,
): Promise<number> {
  const rows = await readCsv(resolve(config.dataDir, "sales_pipeline.csv"));

  for (const batch of rowsInBatches(rows, 500)) {
    const values: unknown[] = [];
    const placeholders = batch.map((row, index) => {
      const productName = normalizeProduct(required(row, "product", "sales_pipeline.csv"));
      const agentName = required(row, "sales_agent", "sales_pipeline.csv");
      const accountName = optional(row, "account");
      const stage = required(row, "deal_stage", "sales_pipeline.csv");
      const productId = productName ? products.get(productName) : undefined;
      const agentId = agents.get(agentName);
      const accountId = accountName ? accounts.get(accountName) : null;

      if (!productId || !agentId || !validStages.has(stage) || (accountName !== null && accountId === undefined)) {
        throw new Error(`Invalid relationship or stage in opportunity ${row.opportunity_id}`);
      }

      const offset = index * 8;
      values.push(
        required(row, "opportunity_id", "sales_pipeline.csv"),
        agentId,
        productId,
        accountId ?? null,
        stage,
        optional(row, "engage_date"),
        optional(row, "close_date"),
        numberValue(optional(row, "close_value")),
      );
      return `($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5}, $${offset + 6}, $${offset + 7}, $${offset + 8})`;
    });

    await client.query(
      `INSERT INTO opportunities (
         id, sales_agent_id, product_id, account_id, deal_stage, engage_date, close_date, close_value
       ) VALUES ${placeholders.join(", ")}`,
      values,
    );
  }

  return rows.length;
}

async function ensureDefaultUser(client: PoolClient): Promise<void> {
  const bootstrapKey = "default-admin";
  const existing = await client.query<{ id: number }>(
    "SELECT id FROM users WHERE bootstrap_key = $1 OR email = $2 ORDER BY bootstrap_key NULLS LAST LIMIT 1",
    [bootstrapKey, config.defaultAdminEmail],
  );
  if (existing.rows[0]) {
    await client.query("UPDATE users SET bootstrap_key = $1 WHERE id = $2", [bootstrapKey, existing.rows[0].id]);
    return;
  }

  const passwordHash = await hashPassword(config.defaultAdminPassword);
  await client.query(
    "INSERT INTO users (name, email, password_hash, bootstrap_key) VALUES ($1, $2, $3, $4)",
    ["Administrador", config.defaultAdminEmail, passwordHash, bootstrapKey],
  );
}

export async function importData(): Promise<{ accounts: number; opportunities: number }> {
  const client = await pool.connect();

  try {
    await client.query("BEGIN");
    await client.query("TRUNCATE opportunities, accounts, products, sales_agents RESTART IDENTITY CASCADE");
    const accounts = await importAccounts(client);
    const products = await importProducts(client);
    const agents = await importSalesAgents(client);
    const opportunities = await importOpportunities(client, accounts, products, agents);
    await ensureDefaultUser(client);
    await client.query("COMMIT");
    return { accounts: accounts.size, opportunities };
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}
