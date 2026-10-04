"use client";
import Link from "next/link";
import { useSyncExternalStore } from "react";
import { Logo } from "@/components/Logo";

const noop = () => () => {};

/** Dentro do simulador (iframe) o console já tem cabeçalho — o portal mostra só o conteúdo. */
export function PortalHeader() {
  const embedded = useSyncExternalStore(noop, () => window.self !== window.top, () => false);
  if (embedded) return null;
  return (
    <header className="bg-navy">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Logo light />
        <div className="flex items-center gap-4 text-xs text-offwhite/70">
          <span className="hidden sm:inline">Central de Ajuda · atendimento 24/7</span>
          <Link href="/login" className="rounded-md border border-white/20 px-2.5 py-1 hover:border-gold hover:text-gold">Sou agente →</Link>
        </div>
      </div>
    </header>
  );
}
