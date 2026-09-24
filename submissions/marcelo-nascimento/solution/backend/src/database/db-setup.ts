import { importData } from "./import-data.js";
import { runMigrations } from "./migrate.js";
import { pool } from "./pool.js";

try {
  const migrations = await runMigrations();
  const imported = await importData();
  console.log(`Database ready: ${migrations} migrations, ${imported.accounts} accounts, ${imported.opportunities} opportunities`);
} catch (error) {
  console.error("Database setup failed", error);
  process.exitCode = 1;
} finally {
  await pool.end();
}
