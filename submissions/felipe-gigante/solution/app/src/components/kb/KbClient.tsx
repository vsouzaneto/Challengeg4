"use client";
import { useState, useTransition } from "react";
import { resolveGapAction, dismissGapAction, createArticleAction, testQuestionAction, deleteArticleAction } from "@/app/(app)/knowledge/actions";
import { Pill } from "@/components/ui";

type Gap = { id: number; question: string; topic: string; category: string; occurrences: number; best_score: number; examples: string; updated_at: number };

export function GapCard({ g }: { g: Gap }) {
  const [open, setOpen] = useState(false);
  const [pending, start] = useTransition();
  const examples: string[] = JSON.parse(g.examples);
  const [form, setForm] = useState({ title: g.question.replace(/\?$/, ""), body: "", questions: examples.join("\n"), topic: g.topic === "Other" ? "" : g.topic });
  return (
    <div className="rounded-xl border border-line p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="font-semibold text-navy">“{g.question}”</div>
          <div className="mt-1 flex flex-wrap gap-1.5 text-xs">
            <span className="rounded-full bg-gold px-2 py-0.5 font-bold text-white">{g.occurrences} ocorrência{g.occurrences > 1 ? "s" : ""}</span>
            <Pill v="pending">Pending Knowledge</Pill>
            <span className="text-muted">intenção: {g.topic} · categoria: {g.category} · similaridade KB: {(g.best_score * 100).toFixed(0)}%</span>
          </div>
        </div>
        <div className="flex shrink-0 gap-2">
          <button onClick={() => setOpen(!open)} className="btn btn-gold py-1.5">{open ? "Fechar" : "Responder"}</button>
          <button disabled={pending} onClick={() => start(() => dismissGapAction(g.id))} className="btn btn-ghost py-1.5">Descartar</button>
        </div>
      </div>
      {examples.length > 1 && (
        <details className="mt-2 text-xs text-muted"><summary className="cursor-pointer">Variações agrupadas (clustering semântico)</summary>
          <ul className="mt-1 list-disc pl-5">{examples.map((e) => <li key={e}>{e}</li>)}</ul>
        </details>
      )}
      {open && (
        <div className="mt-3 space-y-2 border-t border-line pt-3">
          <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Título do artigo" />
          <textarea className="input" rows={5} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} placeholder="Resposta aprovada (é isso que a IA vai usar — e só isso)" />
          <label className="label">Perguntas-exemplo (uma por linha)</label>
          <textarea className="input text-xs" rows={3} value={form.questions} onChange={(e) => setForm({ ...form, questions: e.target.value })} />
          <button disabled={pending || !form.body.trim()} onClick={() => start(() => resolveGapAction(g.id, form))} className="btn btn-navy">Aprovar conhecimento e publicar</button>
        </div>
      )}
    </div>
  );
}

export function NewArticle() {
  const [open, setOpen] = useState(false);
  const [pending, start] = useTransition();
  const [form, setForm] = useState({ title: "", body: "", questions: "", topic: "" });
  if (!open) return <button onClick={() => setOpen(true)} className="btn btn-ghost">+ Novo artigo</button>;
  return (
    <div className="mt-3 space-y-2 rounded-xl border border-line p-4">
      <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Título" />
      <textarea className="input" rows={4} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} placeholder="Conteúdo" />
      <textarea className="input text-xs" rows={2} value={form.questions} onChange={(e) => setForm({ ...form, questions: e.target.value })} placeholder="Perguntas-exemplo, uma por linha" />
      <div className="flex gap-2">
        <button disabled={pending || !form.title || !form.body} onClick={() => start(async () => { await createArticleAction(form); setOpen(false); setForm({ title: "", body: "", questions: "", topic: "" }); })} className="btn btn-navy">Publicar</button>
        <button onClick={() => setOpen(false)} className="btn btn-ghost">Cancelar</button>
      </div>
    </div>
  );
}

export function DeleteArticle({ id }: { id: number }) {
  const [pending, start] = useTransition();
  return <button disabled={pending} onClick={() => start(() => deleteArticleAction(id))} className="text-xs text-muted hover:text-rose-700">remover</button>;
}

type TestResult = Awaited<ReturnType<typeof testQuestionAction>>;
export function TestQuestion() {
  const [q, setQ] = useState("Posso alterar o endereço de cobrança depois que a nota já foi emitida?");
  const [r, setR] = useState<TestResult | null>(null);
  const [pending, start] = useTransition();
  return (
    <div>
      <div className="flex gap-2">
        <input className="input" value={q} onChange={(e) => setQ(e.target.value)} />
        <button disabled={pending} onClick={() => start(async () => setR(await testQuestionAction(q)))} className="btn btn-navy shrink-0">{pending ? "…" : "Testar"}</button>
      </div>
      {r && (
        <div className="mt-3 rounded-lg bg-offwhite p-3 text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <Pill v={r.decision} /> <span>confiança <b>{(r.confidence * 100).toFixed(0)}%</b></span>
            <span className="text-muted">· KB: {r.article ?? "nenhum artigo"} ({(r.kbScore).toFixed(2)})</span>
            {r.createGap && <Pill v="pending">viraria Knowledge Gap</Pill>}
          </div>
          <ul className="mt-2 text-xs text-muted">{r.reasons.map((x) => <li key={x}>• {x}</li>)}</ul>
          {r.reply && <div className="mt-2 whitespace-pre-wrap rounded-lg bg-white p-3 text-xs">{r.reply}</div>}
        </div>
      )}
    </div>
  );
}
