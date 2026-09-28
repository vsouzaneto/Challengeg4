import { Skeleton } from "@/components/ui/skeleton"

// Loading de rota: espelha o layout da página (header + conteúdo), sem spinner de tela cheia.
export default function Loading() {
  return (
    <div className="flex flex-col gap-6" aria-busy="true" aria-label="Carregando">
      <div className="flex flex-col gap-2">
        <Skeleton className="h-7 w-48" />
        <Skeleton className="h-4 w-80 max-w-full" />
      </div>
      <Skeleton className="h-64 w-full" />
    </div>
  )
}
