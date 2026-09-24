import { runMigrations } from "./migrate.js";
import { pool } from "./pool.js";

try {
  const migrations = await runMigrations();
  console.log(`Migrations applied: ${migrations}`);
} catch (error) {
  console.error("Database setup failed", error);
  process.exitCode = 1;
} finally {
  await pool.end();
}
