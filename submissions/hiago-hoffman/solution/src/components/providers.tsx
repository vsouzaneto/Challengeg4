import { Toaster } from "@/components/ui/toast"
import { TooltipProvider } from "@/components/ui/tooltip"

// Providers globais. Adicione aqui (auth, query client, tema) quando o produto precisar.
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Toaster>
      <TooltipProvider>{children}</TooltipProvider>
    </Toaster>
  )
}
