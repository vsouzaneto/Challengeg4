"use server";
import { requireUser } from "@/lib/auth";
import { db, logEvent } from "@/lib/db";
import { guardSql } from "@/lib/sql/guard";
import { matchLibrary } from "@/lib/sql/library";
import { SQL_SCHEMA } from "@/lib/sql/schema";
import { llmEnabled, llmSql } from "@/lib/ai/llm";

export type SqlAnswer = {
  question: string; sql: string | null; explanation: string; source: "llm" | "biblioteca" | "manual" | null;
  columns: string[]; rows: (string | number | null)[][]; error?: string; ms?: number;
};

async function execute(sql: string): Promise<Pick<SqlAnswer, "columns" | "rows" | "error" | "ms">> {
  const g = guardSql(sql);
  if (!g.ok) return { columns: [], rows: [], error: g.error };
  const t0 = Date.now();
  try {
    const r = await (await db()).execute(g.sql);
    return { columns: r.columns, rows: r.rows.map((row) => r.columns.map((_, i) => { const v = row[i]; return typeof v === "bigint" ? Number(v) : (v as string | number | null); })), ms: Date.now() - t0 };
  } catch (e) {
    return { columns: [], rows: [], error: `Erro ao executar: ${(e as Error).message}` };
  }
}

export async function askAction(question: string): Promise<SqlAnswer> {
  const u = await requireUser();
  const q = question.trim().slice(0, 500);
  let gen: { sql: string; explanation: string } | null = null;
  let source: SqlAnswer["source"] = null;
  if (llmEnabled()) { gen = await llmSql(q, SQL_SCHEMA); source = gen ? "llm" : null; }
  if (!gen) { gen = matchLibrary(q); source = gen ? "biblioteca" : null; }
  if (!gen) {
    return { question: q, sql: null, source: null, columns: [], rows: [], explanation: "",
      error: llmEnabled() ? "Não consegui transformar essa pergunta em consulta." : "Sem LLM configurado, entendo as perguntas da biblioteca (veja sugestões) — ou escreva o SQL direto no editor. Configure GROQ_API_KEY para perguntas livres." };
  }
  await logEvent(null, "text_to_sql", { by: u.name, question: q, source });
  return { question: q, sql: gen.sql, explanation: gen.explanation, source, ...(await execute(gen.sql)) };
}

export async function runSqlAction(sql: string): Promise<SqlAnswer> {
  await requireUser();
  return { question: "", sql, explanation: "Consulta editada manualmente.", source: "manual", ...(await execute(sql)) };
}
