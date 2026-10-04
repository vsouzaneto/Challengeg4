import Link from "next/link";
import { requireUser } from "@/lib/auth";
import { Logo } from "@/components/Logo";
import { NavLinks } from "@/components/NavLinks";
import { logout } from "@/app/(auth)/actions";
import { llmEnabled } from "@/lib/ai/llm";
import { one } from "@/lib/db";

const ROLE: Record<string, string> = { manager: "Gestor", agent: "Agente", knowledge: "Knowledge Manager" };

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const user = await requireUser();
  const counts = await one<{ esc: number; gaps: number }>(
    "SELECT (SELECT COUNT(*) FROM tickets WHERE status='escalated' AND source!='dataset') esc, (SELECT COUNT(*) FROM kb_gaps WHERE status='pending') gaps");
  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 flex h-screen w-60 shrink-0 flex-col bg-navy px-4 py-5 text-offwhite">
        <div className="px-1"><Logo light /></div>
        <NavLinks badges={{ inbox: counts?.esc ?? 0, knowledge: counts?.gaps ?? 0 }} />
        <div className="mt-auto space-y-3">
          <Link href="/simulador" className="block rounded-lg border border-gold/40 bg-gold/10 px-3 py-2.5 text-sm font-semibold text-gold hover:bg-gold/20">
            Simulador do cliente
            <span className="block text-[11px] font-normal text-offwhite/60">abra um ticket como cliente</span>
          </Link>
          <div className="rounded-lg bg-white/5 px-3 py-2 text-[11px] text-offwhite/60">
            Modelo: <b className="text-offwhite">{llmEnabled() ? "cascata local → LLM" : "tier local (sem LLM)"}</b>
          </div>
          <div className="flex items-center justify-between border-t border-white/10 pt-3">
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold">{user.name}</div>
              <div className="text-[11px] text-offwhite/50">{ROLE[user.role] ?? user.role}</div>
            </div>
            <form action={logout}><button className="text-xs text-offwhite/60 hover:text-gold">Sair</button></form>
          </div>
        </div>
      </aside>
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
