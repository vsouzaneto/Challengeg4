"use client"

import "./globals.css"

// Falha no root layout: renderiza documento próprio, sem providers.
export default function GlobalError({ retry }: { retry: () => void }) {
  return (
    <html lang="pt-BR">
      <body className="flex min-h-svh flex-col items-center justify-center gap-4 p-6 text-center font-sans">
        <title>Erro</title>
        <h1 className="text-xl font-semibold">Algo deu errado</h1>
        <p className="text-muted-foreground">Recarregue a página ou tente novamente.</p>
        <button
          onClick={() => retry()}
          className="rounded-lg border px-3 py-1.5 text-sm hover:bg-muted"
        >
          Tentar novamente
        </button>
      </body>
    </html>
  )
}
