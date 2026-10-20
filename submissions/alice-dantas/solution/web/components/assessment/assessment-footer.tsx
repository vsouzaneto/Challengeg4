import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

/** O rodapé fixo da janela da avaliação: voltar à esquerda, seguir à direita, os dois em botões arredondados. */
export function AssessmentFooter({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div data-slot="dialog-footer"
         className={cn("flex flex-row items-center justify-between gap-2 border-t bg-card px-6 py-4", className)}>
      {children}
    </div>
  );
}

/** Forma comum dos botões do rodapé: pílula, com a altura de um alvo de toque. */
export const FOOTER_BUTTON = "h-10 rounded-full px-5";
