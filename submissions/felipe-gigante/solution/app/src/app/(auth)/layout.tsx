import { Logo } from "@/components/Logo";

// Dinâmico: as server actions desta rota (login/cadastro/abrir ticket) precisam do SQLite empacotado,
// e o Next não aplica outputFileTracingIncludes a rotas estáticas.
export const dynamic = "force-dynamic";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <aside className="relative hidden overflow-hidden bg-navy p-12 text-offwhite lg:flex lg:flex-col lg:justify-between">
        <div className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full border border-gold/20" />
        <div className="pointer-events-none absolute -right-10 top-24 h-64 w-64 rounded-full border border-gold/10" />
        <Logo light />
        <div className="max-w-lg">
          <h1 className="h-display text-4xl font-extrabold leading-tight">
            IA que resolve o previsível. <span className="text-gold">Humanos</span> onde existe risco.
          </h1>
          <p className="mt-5 text-offwhite/70">
            Triagem, prioridade, sentimento, Knowledge Base e guardrails em um único fluxo — com escalonamento
            upstream para humanos e devolução downstream para a IA concluir e medir CSAT.
          </p>
        </div>
        <div />
      </aside>
      <main className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden"><Logo /></div>
          {children}
        </div>
      </main>
    </div>
  );
}
