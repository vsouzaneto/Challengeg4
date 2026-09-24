import pg from "pg";
import { config } from "../config.js";

const { Pool, types } = pg;

types.setTypeParser(20, (value: string) => {
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed)) {
    throw new Error(`Unsafe PostgreSQL bigint value: ${value}`);
  }
  return parsed;
});

export const pool = new Pool({
  host: config.database.host,
  port: config.database.port,
  user: config.database.user,
  password: config.database.password,
  database: config.database.database,
  max: 12,
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000,
});

pool.on("error", (error) => {
  console.error("PostgreSQL pool error", error);
});
