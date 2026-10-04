import { PortalHeader } from "@/components/portal/PortalHeader";

// Dinâmico: as server actions desta rota (login/cadastro/abrir ticket) precisam do SQLite empacotado,
// e o Next não aplica outputFileTracingIncludes a rotas estáticas.
export const dynamic = "force-dynamic";

export default function PortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-offwhite">
      <PortalHeader />
      {children}
    </div>
  );
}
