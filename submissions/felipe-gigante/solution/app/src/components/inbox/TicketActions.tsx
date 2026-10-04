"use client";
import { useState, useTransition } from "react";
import { ArrowDownToLine, ArrowUpFromLine, Check, RefreshCw, Send, X } from "lucide-react";
import { sendReplyAction, rejectAction, escalateAction, returnToAiAction, resolveAction, regenerateAction } from "@/app/(app)/inbox/actions";

export function ReplyBox({ ticketId, suggested, canReply, humanOwned }: { ticketId: string; suggested: string | null; canReply: boolean; humanOwned: boolean }) {
  const [text, setText] = useState(suggested ?? "");
  const [pending, start] = useTransition();
  const [note, setNote] = useState("");
  const [mode, setMode] = useState<"reply" | "return" | "reject">("reply");
  const act = (fn: () => Promise<void>) => start(async () => { await fn(); });
  const edited = suggested !== null && text.trim() !== suggested.trim();

  return (
    <div className="border-t border-line bg-white p-4">
      <div className="mb-2 flex items-center gap-2">
        {(["reply", "return", "reject"] as const).map((m) => (
          <button key={m} onClick={() => setMode(m)} className={`rounded-md px-2.5 py-1 text-xs font-semibold ${mode === m ? "bg-navy text-white" : "text-muted hover:bg-offwhite"}`}>
            {m === "reply" ? "Responder" : m === "return" ? "Devolver para IA (downstream)" : "Rejeitar sugestão"}
          </button>
        ))}
        {suggested && mode === "reply" && <span className="ml-auto text-[11px] text-muted">{edited ? "✎ editada → registra “edited”" : "sugestão da IA → registra “accepted”"}</span>}
      </div>

      {mode === "reply" && (
        <>
          <textarea value={text} onChange={(e) => setText(e.target.value)} rows={5} className="input font-[inherit]" placeholder="Escreva a resposta ao cliente…" />
          <div className="mt-2 flex flex-wrap gap-2">
            <button disabled={pending || !canReply || !text.trim()} onClick={() => act(() => sendReplyAction(ticketId, text, suggested))} className="btn btn-gold"><Send size={14} />Enviar</button>
            <button disabled={pending} onClick={() => act(() => regenerateAction(ticketId))} className="btn btn-ghost"><RefreshCw size={14} />Regenerar</button>
            {!humanOwned && <button disabled={pending} onClick={() => act(() => escalateAction(ticketId))} className="btn btn-ghost"><ArrowUpFromLine size={14} />Assumir (escalar p/ humano)</button>}
            <button disabled={pending} onClick={() => act(() => resolveAction(ticketId))} className="btn btn-ghost ml-auto"><Check size={14} />Resolver</button>
          </div>
        </>
      )}
      {mode === "return" && (
        <div className="space-y-2">
          <input value={note} onChange={(e) => setNote(e.target.value)} className="input" placeholder="O que foi decidido? Ex.: estorno aprovado, aparece em até 2 faturas" />
          <p className="text-xs text-muted">A IA confirma a decisão ao cliente, encerra o atendimento e solicita CSAT. O humano decide; a IA conclui.</p>
          <button disabled={pending} onClick={() => act(() => returnToAiAction(ticketId, note))} className="btn btn-navy"><ArrowDownToLine size={14} />Devolver para IA concluir</button>
        </div>
      )}
      {mode === "reject" && (
        <div className="space-y-2">
          <input value={note} onChange={(e) => setNote(e.target.value)} className="input" placeholder="Motivo (vira sinal de qualidade para evals e prompt)" />
          <button disabled={pending || !suggested} onClick={() => act(() => rejectAction(ticketId, note))} className="btn btn-ghost text-rose-700"><X size={14} />Rejeitar sugestão</button>
        </div>
      )}
    </div>
  );
}
