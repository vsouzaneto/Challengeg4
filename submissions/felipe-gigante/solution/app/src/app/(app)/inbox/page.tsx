import Link from "next/link";
import { all, one } from "@/lib/db";
import { getMessages, type Ticket } from "@/lib/tickets";
import { Pill, fmt, LABEL } from "@/components/ui";
import { ReplyBox } from "@/components/inbox/TicketActions";
import { AutoRefresh } from "@/components/AutoRefresh";
import type { Step } from "@/lib/ai/pipeline";
import { getGateConfig } from "@/lib/ai/gate-store";
import { computeScore, kbConfidenceOf } from "@/lib/ai/gate";

export const dynamic = "force-dynamic";
type SP = Promise<Record<string, string | undefined>>;

const VIEWS = [
  { key: "live", label: "Ao vivo (portal)", where: "source != 'dataset'" },
  { key: "escalated", label: "Escalados p/ humano", where: "status = 'escalated'" },
  { key: "suggest", label: "Aguardando aprovação", where: "decision = 'suggest' AND status IN ('open','new')" },
  { key: "open", label: "Todos em aberto", where: "status IN ('new','open','escalated','pending')" },
  { key: "all", label: "Todos", where: "1=1" },
] as const;

const STEP_COLOR: Record<Step["status"], string> = { ok: "bg-emerald-500", warn: "bg-amber-500", block: "bg-rose-600", skip: "bg-slate-300" };

function qs(sp: Record<string, string | undefined>, patch: Record<string, string | undefined>) {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries({ ...sp, ...patch })) if (v) p.set(k, v);
  return `/inbox?${p.toString()}`;
}

export default async function InboxPage({ searchParams }: { searchParams: SP }) {
  const sp = await searchParams;
  const view = VIEWS.find((v) => v.key === sp.view) ?? VIEWS[0];
  const page = Math.max(1, Number(sp.page) || 1);
  const args: string[] = [];
  let where = view.where;
  if (sp.q) { where += " AND (subject LIKE ? OR customer_name LIKE ? OR id LIKE ? OR summary LIKE ?)"; args.push(...Array(4).fill(`%${sp.q}%`)); }
  if (sp.priority) { where += " AND priority = ?"; args.push(sp.priority); }

  const [list, count, counts] = await Promise.all([
    all<Ticket>(`SELECT * FROM tickets WHERE ${where} ORDER BY CASE priority WHEN 'Critical' THEN 0 WHEN 'High' THEN 1 ELSE 2 END, updated_at DESC LIMIT 40 OFFSET ?`, [...args, (page - 1) * 40]),
    one<{ n: number }>(`SELECT COUNT(*) n FROM tickets WHERE ${where}`, args),
    Promise.all(VIEWS.map((v) => one<{ n: number }>(`SELECT COUNT(*) n FROM tickets WHERE ${v.where}`))),
  ]);
  const selectedId = sp.t ?? list[0]?.id;
  const t = selectedId ? await one<Ticket>("SELECT * FROM tickets WHERE id=?", [selectedId]) : null;
  const msgs = t ? await getMessages(t.id) : [];
  const trace = t?.trace ? (JSON.parse(t.trace) as { steps: Step[]; reasons: string[]; kb: { id: number; title: string; score: number }[]; topTerms: string[]; grounded: number | null }) : null;
  const article = t?.kb_article_id ? await one<{ title: string }>("SELECT title FROM kb_articles WHERE id=?", [t.kb_article_id]) : null;
  const humanOwned = !!t && (t.status === "escalated" || (t.assignee !== "AI Agent" && !t.assignee.startsWith("Fila")));
  const pages = Math.ceil((count?.n ?? 0) / 40);
  const gate = await getGateConfig();
  const parts = t ? computeScore(gate, t.category_conf, kbConfidenceOf(gate, t.kb_score, t.kb_weight ?? 1), t.sentiment) : null;

  return (
    <div className="flex h-screen flex-col">
      {t && t.source !== "dataset" && <AutoRefresh />}
      <div className="flex items-center gap-2 border-b border-line bg-white px-5 py-3">
        <h1 className="h-display mr-3 text-lg font-extrabold text-navy">Smart Inbox</h1>
        {VIEWS.map((v, i) => (
          <Link key={v.key} href={qs({}, { view: v.key })} className={`rounded-full px-3 py-1 text-xs font-semibold ${v.key === view.key ? "bg-navy text-white" : "bg-offwhite text-muted hover:text-navy"}`}>
            {v.label} <span className="opacity-60">{fmt.n(counts[i]?.n)}</span>
          </Link>
        ))}
        <form className="ml-auto flex gap-2" action="/inbox">
          <input type="hidden" name="view" value={view.key} />
          <input name="q" defaultValue={sp.q} placeholder="Buscar ticket, cliente, assunto…" className="input w-64 py-1.5" />
          <select name="priority" defaultValue={sp.priority ?? ""} className="input w-32 py-1.5">
            <option value="">Prioridade</option>{["Critical", "High", "Medium", "Low"].map((p) => <option key={p}>{p}</option>)}
          </select>
          <button className="btn btn-navy py-1.5">Filtrar</button>
        </form>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-[340px_1fr_360px]">
        {/* Lista */}
        <div className="flex min-h-0 flex-col border-r border-line bg-white">
          <div className="min-h-0 flex-1 overflow-y-auto">
            {list.map((x) => (
              <Link key={x.id} href={qs(sp, { t: x.id })} className={`block border-b border-line px-4 py-3 hover:bg-offwhite ${x.id === selectedId ? "border-l-4 border-l-gold bg-gold-100/40" : ""}`}>
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-sm font-semibold text-ink">{x.customer_name}</span>
                  <span className="shrink-0 text-[11px] text-muted">{fmt.ago(x.updated_at)}</span>
                </div>
                <div className="truncate text-xs text-muted">{x.id} · {x.channel} · {x.subject}</div>
                <div className="mt-1.5 flex flex-wrap gap-1">
                  <Pill v={x.priority} /><Pill v={x.decision} /><Pill v={x.sentiment} /><Pill v={x.status} />
                </div>
                <div className="mt-1 truncate text-[11px] text-muted">{x.category} → {x.assignee}</div>
              </Link>
            ))}
            {!list.length && <div className="p-6 text-sm text-muted">Nenhum ticket nesta visão.</div>}
          </div>
          <div className="flex items-center justify-between border-t border-line px-4 py-2 text-xs text-muted">
            <span>{fmt.n(count?.n)} tickets</span>
            <span className="flex gap-2">
              {page > 1 && <Link href={qs(sp, { page: String(page - 1), t: undefined })} className="font-semibold text-navy">← anterior</Link>}
              <span>{page}/{pages || 1}</span>
              {page < pages && <Link href={qs(sp, { page: String(page + 1), t: undefined })} className="font-semibold text-navy">próxima →</Link>}
            </span>
          </div>
        </div>

        {/* Conversa */}
        <div className="flex min-h-0 flex-col bg-offwhite">
          {t ? (
            <>
              <div className="border-b border-line bg-white px-6 py-3">
                <div className="flex items-center gap-2">
                  <h2 className="h-display truncate text-base font-bold text-navy">{t.subject}</h2>
                  <Pill v={t.status} />
                </div>
                <div className="text-xs text-muted">{t.id} · {t.customer_name} &lt;{t.customer_email}&gt; · {t.channel}{t.product ? ` · ${t.product}` : ""} · responsável: <b className="text-ink">{t.assignee}</b>
                  {t.source === "dataset" && <> · <span className="text-gold">Dataset 1 ({t.dataset_type}, {t.dataset_priority})</span></>}
                </div>
              </div>
              <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-6 py-4">
                {msgs.map((m) => m.role === "system" ? (
                  <div key={m.id} className="mx-auto max-w-lg rounded-lg border border-dashed border-gold/60 bg-gold-100/50 px-3 py-1.5 text-center text-xs text-navy">{m.body}</div>
                ) : (
                  <div key={m.id} className={`flex ${m.role === "customer" ? "justify-start" : "justify-end"}`}>
                    <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm shadow-sm ${m.role === "customer" ? "rounded-bl-sm bg-white" : m.role === "ai" ? "rounded-br-sm bg-navy text-offwhite" : "rounded-br-sm bg-gold text-white"}`}>
                      <div className={`mb-1 text-[11px] font-semibold ${m.role === "customer" ? "text-muted" : "opacity-70"}`}>
                        {m.role === "ai" ? "🤖 AI Agent" : m.role === "agent" ? `👤 ${m.author}` : m.author} · {new Date(m.created_at).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}
                      </div>
                      <div className="whitespace-pre-wrap">{m.body}</div>
                    </div>
                  </div>
                ))}
                {t.csat && (
                  <div className="mx-auto max-w-sm rounded-xl border border-line bg-white p-3 text-center text-sm">
                    <div className="text-lg text-gold">{"★".repeat(t.csat)}{"☆".repeat(5 - t.csat)}</div>
                    <div className="text-xs text-muted">CSAT {t.csat}/5{t.csat_comment ? ` — “${t.csat_comment}”` : ""}</div>
                  </div>
                )}
                {t.source === "dataset" && t.dataset_resolution && (
                  <div className="rounded-lg border border-line bg-white p-3 text-xs text-muted">
                    <b>Resolução registrada no dataset:</b> “{t.dataset_resolution}” <span className="text-rose-700">(texto sintético/lorem ipsum — por isso não foi usado para treinar respostas)</span>
                  </div>
                )}
              </div>
              {!["closed"].includes(t.status) && (
                <ReplyBox key={`${t.id}-${t.suggested_reply?.length ?? 0}-${t.updated_at}`} ticketId={t.id} suggested={t.suggested_reply} canReply humanOwned={humanOwned} />
              )}
            </>
          ) : <div className="m-auto text-sm text-muted">Selecione um ticket.</div>}
        </div>

        {/* AI Insights */}
        <aside className="min-h-0 overflow-y-auto border-l border-line bg-white p-5">
          {t && (
            <div className="space-y-5">
              <div>
                <div className="kicker mb-2">AI Insights</div>
                <div className="rounded-xl bg-navy p-4 text-offwhite">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-offwhite/60">Decisão do gate</span><Pill v={t.decision} />
                  </div>
                  <div className="mt-2 flex items-end gap-2">
                    <div className="h-display text-3xl font-extrabold text-gold">{(t.ai_confidence * 100).toFixed(0)}%</div>
                    <div className="pb-1 text-xs text-offwhite/60">confiança · tier {t.model_tier}</div>
                  </div>
                  <div className="relative mt-2 h-1.5 rounded-full bg-white/10">
                    <div className="h-full rounded-full bg-gold" style={{ width: `${t.ai_confidence * 100}%` }} />
                    {[gate.suggestThreshold, gate.autoThreshold].map((x) => <div key={x} className="absolute -top-1 h-3.5 border-l border-white/60" style={{ left: `${x * 100}%` }} />)}
                  </div>
                  <div className="mt-1 flex justify-between text-[10px] text-offwhite/50"><span>HUMANO</span><span>mín {Math.round(gate.suggestThreshold * 100)}% · máx {Math.round(gate.autoThreshold * 100)}%</span><span>AUTO</span></div>
                  {parts && (
                    <div className="mt-2 rounded-md bg-white/5 px-2 py-1.5 font-mono text-[11px] text-offwhite/80">
                      {gate.wClassifier.toFixed(2)}×{t.category_conf.toFixed(2)} cls + {(1 - gate.wClassifier).toFixed(2)}×{parts.kbConfidence.toFixed(2)} KB{parts.penalty ? ` − ${parts.penalty.toFixed(2)}` : ""} = {parts.score.toFixed(2)}
                      <Link href="/confianca" className="ml-1 font-sans text-gold hover:underline">ajustar</Link>
                    </div>
                  )}
                  {trace?.reasons.length ? <ul className="mt-3 space-y-1 text-xs text-offwhite/80">{trace.reasons.map((r) => <li key={r}>• {r}</li>)}</ul> : null}
                </div>
              </div>

              <dl className="grid grid-cols-2 gap-3 text-sm">
                {[
                  ["Categoria", <>{t.category} <span className="text-xs text-muted">{(t.category_conf * 100).toFixed(0)}%</span></>],
                  ["Time (roteamento)", t.team],
                  ["Prioridade sugerida", <Pill key="p" v={t.priority}>{t.priority} · {t.priority_score}</Pill>],
                  ["Sentimento", <Pill key="s" v={t.sentiment}>{LABEL[t.sentiment]} · {t.sentiment_score}</Pill>],
                  ["Risco", <Pill key="r" v={t.risk_level} />],
                  ["Assunto/intenção", t.topic],
                ].map(([k, v]) => (
                  <div key={k as string}><dt className="text-[11px] font-semibold uppercase tracking-wide text-muted">{k}</dt><dd className="mt-0.5">{v}</dd></div>
                ))}
              </dl>

              {t.summary && <div><div className="label">Resumo</div><p className="text-sm">{t.summary}</p></div>}

              <div>
                <div className="label">Artigos da KB consultados</div>
                {trace?.kb.length ? trace.kb.map((k) => (
                  <Link key={k.id} href="/knowledge" className="mb-1 flex justify-between rounded-md bg-offwhite px-2 py-1 text-xs hover:text-navy">
                    <span className={k.title === article?.title ? "font-semibold" : ""}>{k.title}</span><span className="text-muted">{k.score.toFixed(2)}</span>
                  </Link>
                )) : <p className="text-xs text-muted">—</p>}
                {trace?.grounded !== null && trace?.grounded !== undefined && <p className="mt-1 text-[11px] text-muted">Groundedness da resposta: {(trace.grounded * 100).toFixed(0)}%</p>}
              </div>

              {JSON.parse(t.risk_reasons || "[]").length > 0 && (
                <div><div className="label">Risco identificado</div>
                  <ul className="space-y-1 text-xs">{(JSON.parse(t.risk_reasons) as string[]).map((r) => <li key={r} className="rounded bg-rose-50 px-2 py-1 text-rose-800">{r}</li>)}</ul>
                </div>
              )}

              {trace && (
                <div>
                  <div className="label">Pipeline (trace)</div>
                  <ol className="space-y-2">
                    {trace.steps.map((s) => (
                      <li key={s.name} className="flex gap-2 text-xs">
                        <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${STEP_COLOR[s.status]}`} />
                        <div><b className="text-ink">{s.name}</b> <span className="text-muted">· {s.ms.toFixed(1)}ms</span><div className="text-muted">{s.detail}</div></div>
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
