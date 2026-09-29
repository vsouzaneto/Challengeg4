"use client"

import { useEffect } from "react"

import { ErrorState } from "@/components/error-state"

// Erro de rota dentro do shell: sidebar continua navegável.
export default function Error({
  error,
  retry,
}: {
  error: Error & { digest?: string }
  retry: () => void
}) {
  useEffect(() => {
    // Envie para o serviço de monitoramento do projeto (Sentry etc.).
    console.error(error)
  }, [error])

  return (
    <ErrorState
      title="Esta página falhou ao carregar"
      description={error.digest ? `Código: ${error.digest}` : undefined}
      onRetry={retry}
    />
  )
}
