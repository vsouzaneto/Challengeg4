import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { config } from "../config.js";
import { pool } from "./pool.js";

export async function runMigrations(): Promise<number> {
  const client = await pool.connect();

  try {
    await client.query(
      "CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
    );

    const files = (await readdir(config.migrationsDir))
      .filter((file) => file.endsWith(".sql"))
      .sort();
    const { rows } = await client.query<{ name: string }>("SELECT name FROM schema_migrations");
    const applied = new Set(rows.map((row) => row.name));
    let count = 0;

    for (const file of files) {
      if (applied.has(file)) {
        continue;
      }

      const sql = await readFile(join(config.migrationsDir, file), "utf8");
      await client.query("BEGIN");
      try {
        await client.query(sql);
        await client.query("INSERT INTO schema_migrations (name) VALUES ($1)", [file]);
        await client.query("COMMIT");
        count += 1;
      } catch (error) {
        await client.query("ROLLBACK");
        throw error;
      }
    }

    return count;
  } finally {
    client.release();
  }
}
