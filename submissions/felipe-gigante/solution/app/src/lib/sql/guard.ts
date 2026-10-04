// Guardrail do text-to-SQL: somente leitura, uma instrução, sem tabelas sensíveis, com limite de linhas.
const FORBIDDEN = /\b(insert|update|delete|drop|alter|create|attach|detach|pragma|replace|vacuum|reindex|begin|commit|rollback|savepoint|load_extension)\b/i;
const SENSITIVE = /\b(users|sessions|password_hash|sqlite_master|sqlite_schema|meta)\b/i;

export type GuardResult = { ok: true; sql: string } | { ok: false; error: string };

export function guardSql(raw: string): GuardResult {
  let sql = raw.trim().replace(/^```(sql)?/i, "").replace(/```$/, "").trim().replace(/;+\s*$/, "");
  if (!/^(select|with)\b/i.test(sql)) return { ok: false, error: "Apenas consultas de leitura (SELECT/WITH) são permitidas." };
  if (sql.includes(";")) return { ok: false, error: "Apenas uma instrução por consulta." };
  if (FORBIDDEN.test(sql)) return { ok: false, error: "A consulta contém um comando que altera dados — bloqueada." };
  if (SENSITIVE.test(sql)) return { ok: false, error: "Tabelas de autenticação e configuração não podem ser consultadas." };
  sql = `SELECT * FROM (${sql}) LIMIT 200`;
  return { ok: true, sql };
}
