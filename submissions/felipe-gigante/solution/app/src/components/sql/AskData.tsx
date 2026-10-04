"use client";
import { useState, useTransition } from "react";
import { Play, Sparkles } from "lucide-react";
import { askAction, runSqlAction, type SqlAnswer } from "@/app/(app)/perguntas/actions";
import { HBars } from "@/components/charts";

const SOURCE: Record<string, string> = { llm: "gerado por LLM", biblioteca: "biblioteca de consultas", manual: "SQL manual" };

function Chart({ a }: { a: SqlAnswer }) {
  // Gráfico automático quando o resultado é "rótulo + número".
  if (a.rows.length < 2 || a.rows.length > 30 || a.columns.length < 2) return null;
  const numIdx = a.columns.findIndex((_, i) => i > 0 && a.rows.every((r) => typeof r[i] === "number"));
  if (numIdx < 0 || typeof a.rows[0][0] === "number") return null;
  return (
    <div className="mt-4">
      <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted">{a.columns[numIdx]} por {a.columns[0]}</div>
      <HBars color="#002037" data={a.rows.map((r) => ({ label: String(r[0] ?? "—").slice(0, 40), value: Number(r[numIdx]) }))} />
    </div>
  );
}

export function AskData({ suggestions, llm }: { suggestions: string[]; llm: boolean }) {
  const [q, setQ] = useState("");
  const [sql, setSql] = useState("");
  const [answer, setAnswer] = useState<SqlAnswer | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [pending, start] = useTransition();

  const ask = (question: string) => {
    if (!question.trim()) return;
    setQ(question);
    start(async () => {
      const a = await askAction(question);
      setAnswer(a);
      setSql(a.sql ?? "");
      setHistory((h) => [question, ...h.filter((x) => x !== question)].slice(0, 8));
    });
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_300px]">
      <div className="space-y-5">
        <div className="card p-5">
          <form onSubmit={(e) => { e.preventDefault(); ask(q); }} className="flex gap-2">
            <input value={q} onChange={(e) => setQ(e.target.value)} className="input py-2.5 text-base" placeholder="Ex.: Por que a IA escalou para humano nos últimos 7 dias?" />
            <button disabled={pending || !q.trim()} className="btn btn-gold shrink-0"><Sparkles size={15} />{pending ? "Consultando…" : "Perguntar"}</button>
          </form>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {suggestions.map((s) => (
              <button key={s} onClick={() => ask(s)} className="rounded-full border border-line bg-offwhite px-3 py-1 text-xs text-navy hover:border-gold">{s}</button>
            ))}
          </div>
          <p className="mt-3 text-[11px] text-muted">
            {llm ? "Perguntas livres são convertidas em SQL por LLM." : "Sem LLM configurado: entende as perguntas da biblioteca (variações e períodos como “últimos 7 dias”). Configure GROQ_API_KEY para perguntas livres."}
            {" "}Somente leitura: comandos que alteram dados e tabelas de autenticação são bloqueados; máximo de 200 linhas.
          </p>
        </div>

        {answer && (
          <div className="card p-5">
            {answer.explanation && <p className="text-sm text-ink">{answer.explanation}</p>}
            <div className="mt-3">
              <div className="mb-1 flex items-center justify-between text-xs text-muted">
                <span>SQL {answer.source && <>· <b>{SOURCE[answer.source]}</b></>}{answer.ms !== undefined && ` · ${answer.ms} ms · ${answer.rows.length} linhas`}</span>
                <button disabled={pending || !sql.trim()} onClick={() => start(async () => setAnswer(await runSqlAction(sql)))} className="btn btn-navy py-1 text-xs"><Play size={12} />Rodar SQL</button>
              </div>
              <textarea value={sql} onChange={(e) => setSql(e.target.value)} rows={Math.min(8, Math.max(3, sql.split("\n").length + 1))} spellCheck={false}
                className="input bg-navy font-mono text-xs text-offwhite" placeholder="Escreva um SELECT…" />
            </div>
            {answer.error && <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-800">{answer.error}</p>}
            {!answer.error && answer.columns.length > 0 && (
              <>
                <Chart a={answer} />
                <div className="mt-4 max-h-[420px] overflow-auto rounded-lg border border-line">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-offwhite"><tr>{answer.columns.map((c) => <th key={c} className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-muted">{c}</th>)}</tr></thead>
                    <tbody>{answer.rows.map((r, i) => (
                      <tr key={i} className="border-t border-line">{r.map((v, j) => <td key={j} className={`px-3 py-1.5 ${typeof v === "number" ? "text-right tabular-nums" : ""}`}>{v === null ? "—" : typeof v === "number" ? v.toLocaleString("pt-BR") : String(v)}</td>)}</tr>
                    ))}</tbody>
                  </table>
                  {!answer.rows.length && <p className="p-4 text-sm text-muted">Nenhum resultado.</p>}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      <aside className="space-y-5">
        <div className="card p-4">
          <div className="kicker mb-2">Perguntas recentes</div>
          {history.length ? history.map((h) => <button key={h} onClick={() => ask(h)} className="block w-full truncate py-1 text-left text-sm text-navy hover:text-gold">{h}</button>) : <p className="text-xs text-muted">Nenhuma ainda.</p>}
        </div>
        <div className="card p-4 text-xs text-muted">
          <div className="kicker mb-2">Tabelas disponíveis</div>
          <ul className="space-y-1 font-mono">
            <li><b className="text-navy">tickets</b> — canal, assunto, categoria, prioridade, sentimento, decisão, risco, CSAT, datas</li>
            <li><b className="text-navy">messages</b> — conversa de cada ticket</li>
            <li><b className="text-navy">events</b> — escalonamentos, feedback, CSAT, gaps</li>
            <li><b className="text-navy">kb_articles</b> · <b className="text-navy">kb_gaps</b></li>
          </ul>
        </div>
      </aside>
    </div>
  );
}
