export interface DatabaseConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
}

function parsePort(value: string | undefined): number {
  const port = Number(value ?? 3000);
  return Number.isInteger(port) && port > 0 ? port : 3000;
}

export const config = {
  port: parsePort(process.env.PORT),
  nodeEnv: process.env.NODE_ENV ?? "development",
  database: {
    host: process.env.DB_HOST ?? "127.0.0.1",
    port: Number(process.env.DB_PORT ?? 5432),
    user: process.env.DB_USER ?? "lead_scorer",
    password: process.env.DB_PASSWORD ?? "lead_scorer",
    database: process.env.DB_NAME ?? "lead_scorer",
  } satisfies DatabaseConfig,
  dataDir: process.env.DATA_DIR ?? new URL("../../data/", import.meta.url).pathname,
  migrationsDir: process.env.MIGRATIONS_DIR ?? new URL("../migrations/", import.meta.url).pathname,
  defaultAdminEmail: process.env.DEFAULT_ADMIN_EMAIL ?? "admin@leadscore.local",
  defaultAdminPassword: process.env.DEFAULT_ADMIN_PASSWORD ?? "lead@teste55",
  secureCookies: process.env.COOKIE_SECURE === "true",
  sessionMaxAgeSeconds: 60 * 60 * 24 * 8,
};
