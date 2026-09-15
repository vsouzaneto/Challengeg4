import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lead Scorer",
  description: "Triagem e score do pipeline de vendas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen">
        <header className="border-b border-neutral-200 bg-white">
          <nav className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 text-sm">
            <span className="font-semibold tracking-tight">Lead Scorer</span>
            <Link href="/" className="text-neutral-600 hover:text-neutral-900">
              Meu pipeline
            </Link>
            <Link href="/gerente" className="text-neutral-600 hover:text-neutral-900">
              Visão do gerente
            </Link>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
