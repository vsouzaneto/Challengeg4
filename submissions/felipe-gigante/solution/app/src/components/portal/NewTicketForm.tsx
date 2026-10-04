"use client";
import { useActionState } from "react";
import { openTicketAction } from "@/app/portal/actions";

export function NewTicketForm({ message, setMessage }: { message: string; setMessage: (v: string) => void }) {
  const [state, action, pending] = useActionState(openTicketAction, undefined);
  return (
    <form action={action} className="card h-fit space-y-3 p-5 shadow-sm">
      <div className="h-display text-lg font-bold text-navy">Abrir atendimento</div>
      <div className="grid grid-cols-2 gap-3">
        <div><label className="label">Nome</label><input name="name" className="input" required defaultValue="Cliente Demo" /></div>
        <div><label className="label">E-mail</label><input name="email" type="email" className="input" required defaultValue="cliente@exemplo.com.br" /></div>
      </div>
      <div><label className="label">Canal</label>
        <select name="channel" className="input" defaultValue="Chat">{["Chat", "Email", "Social media", "Phone"].map((c) => <option key={c}>{c}</option>)}</select>
      </div>
      <div><label className="label">Mensagem</label><textarea name="message" rows={6} className="input" required placeholder="Descreva seu problema…" value={message} onChange={(e) => setMessage(e.target.value)} /></div>
      {state?.error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{state.error}</p>}
      <button className="btn btn-gold w-full" disabled={pending}>{pending ? "A IA está analisando…" : "Enviar"}</button>
      <p className="text-[11px] text-muted">Dados pessoais (cartão, CPF, telefone) são mascarados antes de qualquer processamento.</p>
    </form>
  );
}
