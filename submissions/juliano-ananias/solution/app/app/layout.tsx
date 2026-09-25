import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'G4 AI Master — Lead Scorer Pro | RevOps & AI Prioritization',
  description: 'Sistema Inteligente de Priorização Comercial com Copiloto Gemini e Filas de Ação RevOps.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className="h-full bg-slate-950">
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
