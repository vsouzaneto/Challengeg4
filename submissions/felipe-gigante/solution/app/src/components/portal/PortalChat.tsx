"use client";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState, useTransition } from "react";
import { Send } from "lucide-react";
import { sendCustomerMessage, sendCsat } from "@/app/portal/actions";
import type { Step } from "@/lib/ai/pipeline";

type Data = {
  ticket: { id: string; status: string; csat: number | null; subject: string; assignee: string };
  messages: { id: number; role: "customer" | "ai" | "agent"; author: string; body: string; at: number }[];
  insight: { decision: string; confidence: number; category: string; priority: string; sentiment: string; sentimentScore: number; risk: string; tier: string; trace: { steps: Step[]; reasons: string[] } | null };
};
const DOT: Record<string, string> = { ok: "bg-emerald-500", warn: "bg-amber-500", block: "bg-rose-600", skip: "bg-slate-300" };
const STATUS: Record<string, string> = { new: "Novo", open: "Em análise", pending: "Aguardando você", escalated: "Com especialista", resolved: "Resolvido", closed: "Encerrado" };

export function PortalChat({ token }: { token: string }) {
  const [data, setData] = useState<Data | null>(null);
  const [text, setText] = useState("");
  const [pending, start] = useTransition();
  const [score, setScore] = useState(0);
  const [comment, setComment] = useState("");
  const bottom = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    const r = await fetch(`/api/portal/${token}`, { cache: "no-store" });
    if (r.ok) setData(await r.json());
  }, [token]);
  useEffect(() => {
    // Polling: o setState acontece no callback do fetch (assinatura de sistema externo).
    const poll = () => { fetch(`/api/portal/${token}`, { cache: "no-store" }).then((r) => (r.ok ? r.json() : null)).then((d) => d && setData(d)); };
    poll();
    const id = setInterval(poll, 3000);
    return () => clearInterval(id);
  }, [token]);
  useEffect(() => { bottom.current?.scrollIntoView({ behavior: "smooth" }); }, [data?.messages.length]);

  if (!data) return <div className="p-10 text-center text-muted">Carregando…</div>;
  const { ticket, messages, insight } = data;
  const send = () => { const b = text; setText(""); start(async () => { await sendCustomerMessage(token, b); await load(); }); };

  return (
    <main className="mx-auto grid max-w-5xl gap-6 px-6 py-8 lg:grid-cols-[1fr_340px]">
      <div className="card flex h-[calc(100vh-140px)] flex-col overflow-hidden shadow-sm">
        <div className="flex items-center justify-between border-b border-line px-5 py-3">
          <div><div className="text-sm font-semibold text-navy">{ticket.subject}</div><div className="text-xs text-muted">{ticket.id} · atendido por {ticket.assignee === "AI Agent" ? "Assistente G4 (IA)" : ticket.assignee}</div></div>
          <span className="rounded-full bg-offwhite px-2.5 py-1 text-xs font-semibold text-navy">{STATUS[ticket.status] ?? ticket.status}</span>
        </div>
        <div className="flex-1 space-y-3 overflow-y-auto bg-offwhite/60 px-5 py-4">
          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === "customer" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm shadow-sm ${m.role === "customer" ? "rounded-br-sm bg-navy text-offwhite" : m.role === "ai" ? "rounded-bl-sm bg-white" : "rounded-bl-sm border border-gold/40 bg-gold-100"}`}>
                <div className={`mb-0.5 text-[11px] font-semibold ${m.role === "customer" ? "text-offwhite/60" : "text-gold"}`}>{m.role === "customer" ? "Você" : m.role === "ai" ? "🤖 Assistente G4" : `👤 ${m.author} · especialista`}</div>
                <div className="whitespace-pre-wrap">{m.body}</div>
              </div>
            </div>
          ))}
          {pending && <div className="text-xs text-muted">Assistente digitando…</div>}
          {ticket.status === "resolved" && !ticket.csat && (
            <div className="mx-auto max-w-sm rounded-xl border border-gold/40 bg-white p-4 text-center shadow-sm">
              <div className="text-sm font-semibold text-navy">Como você avalia sua experiência?</div>
              <div className="my-2 flex justify-center gap-1 text-3xl">
                {[1, 2, 3, 4, 5].map((s) => <button key={s} onClick={() => setScore(s)} className={s <= score ? "text-gold" : "text-line hover:text-gold/60"} aria-label={`${s} estrelas`}>★</button>)}
              </div>
              <input value={comment} onChange={(e) => setComment(e.target.value)} className="input text-xs" placeholder="Quer contar o motivo? (opcional)" />
              <button disabled={!score} onClick={() => start(async () => { await sendCsat(token, score, comment); await load(); })} className="btn btn-gold mt-2 w-full">Enviar avaliação</button>
            </div>
          )}
          {ticket.csat && <div className="text-center text-sm text-muted">Obrigado pela avaliação: <span className="text-gold">{"★".repeat(ticket.csat)}</span></div>}
          <div ref={bottom} />
        </div>
        {ticket.status !== "closed" && (
          <div className="flex gap-2 border-t border-line p-3">
            <input value={text} onChange={(e) => setText(e.target.value)} onKeyDown={(e) => e.key === "Enter" && text.trim() && send()} className="input" placeholder="Escreva sua mensagem…" />
            <button disabled={!text.trim() || pending} onClick={send} className="btn btn-gold"><Send size={15} /></button>
          </div>
        )}
      </div>

      <aside className="space-y-4">
        <div className="card p-4">
          <div className="kicker mb-1">Modo demo · por dentro da IA</div>
          <p className="mb-3 text-xs text-muted">O cliente real não vê este painel. Ele mostra o que o pipeline decidiu na última mensagem.</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {[["Decisão", insight.decision.toUpperCase()], ["Confiança", `${(insight.confidence * 100).toFixed(0)}%`], ["Categoria", insight.category], ["Prioridade", insight.priority], ["Sentimento", `${insight.sentiment} (${insight.sentimentScore})`], ["Risco", insight.risk]].map(([k, v]) => (
              <div key={k} className="rounded-md bg-offwhite px-2 py-1.5"><div className="text-[10px] uppercase tracking-wide text-muted">{k}</div><div className="font-semibold text-navy">{v}</div></div>
            ))}
          </div>
          {insight.trace && (
            <ol className="mt-3 space-y-1.5">
              {insight.trace.steps.map((s) => (
                <li key={s.name} className="flex gap-2 text-[11px]"><span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${DOT[s.status]}`} /><div><b>{s.name}</b><div className="text-muted">{s.detail}</div></div></li>
              ))}
            </ol>
          )}
        </div>
        <Link href="/portal" className="btn btn-ghost w-full">+ Novo atendimento</Link>
      </aside>
    </main>
  );
}
