import { CircleAlertIcon, RotateCwIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"

// Estado de erro recuperável: diga o que falhou e ofereça tentar de novo.
export function ErrorState({
  title = "Não foi possível carregar",
  description = "Algo deu errado. Tente novamente em instantes.",
  onRetry,
}: {
  title?: string
  description?: string
  onRetry?: () => void
}) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <CircleAlertIcon className="text-destructive" />
        </EmptyMedia>
        <EmptyTitle>{title}</EmptyTitle>
        <EmptyDescription>{description}</EmptyDescription>
      </EmptyHeader>
      {onRetry && (
        <EmptyContent>
          <Button variant="outline" onClick={onRetry}>
            <RotateCwIcon data-icon="inline-start" />
            Tentar novamente
          </Button>
        </EmptyContent>
      )}
    </Empty>
  )
}
