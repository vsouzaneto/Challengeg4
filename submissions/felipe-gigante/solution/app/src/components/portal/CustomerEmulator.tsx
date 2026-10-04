"use client";
import Link from "next/link";
import { useState } from "react";
import { Inbox, Lock, RotateCcw } from "lucide-react";

/** Emula o navegador do cliente dentro do console (o portal roda isolado num iframe). */
export function CustomerEmulator() {
  const [session, setSession] = useState(0);
  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-white shadow-sm">
      <div className="flex items-center gap-3 border-b border-line bg-offwhite px-4 py-2.5">
        <div className="flex gap-1.5">
          <span className="h-3 w-3 rounded-full bg-rose-400" /><span className="h-3 w-3 rounded-full bg-amber-400" /><span className="h-3 w-3 rounded-full bg-emerald-400" />
        </div>
        <div className="flex flex-1 items-center gap-2 rounded-md border border-line bg-white px-3 py-1 text-xs text-muted">
          <Lock size={12} /> suporte.suaempresa.com.br
        </div>
        <button onClick={() => setSession((s) => s + 1)} className="btn btn-ghost py-1 text-xs"><RotateCcw size={13} />Novo cliente</button>
        <Link href="/inbox?view=live" className="btn btn-navy py-1 text-xs"><Inbox size={13} />Ver na Inbox</Link>
      </div>
      <iframe key={session} src="/portal" title="Portal do cliente" className="h-[calc(100vh-230px)] min-h-[560px] w-full bg-offwhite" />
    </div>
  );
}
