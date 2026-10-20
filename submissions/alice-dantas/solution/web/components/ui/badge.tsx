import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "cn"
import { Slot } from "radix-ui"

const badgeVariants = cva(
  "group/badge inline-flex h-6 w-fit shrink-0 items-center justify-center gap-1.5 overflow-hidden rounded-4xl border border-transparent px-2.5 py-0.5 text-xs font-medium whitespace-nowrap transition-all focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&>svg]:pointer-events-none [&>svg]:size-3.5!",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground [a]:hover:bg-primary/80",
        secondary:
          "bg-secondary text-secondary-foreground [a]:hover:bg-secondary/80",
        destructive:
          "bg-destructive/10 text-destructive focus-visible:ring-destructive/20 dark:bg-destructive/20 dark:focus-visible:ring-destructive/40 [a]:hover:bg-destructive/20",
        outline:
          "border-border bg-muted/60 text-foreground [a]:hover:bg-muted",
        ghost:
          "hover:bg-muted hover:text-muted-foreground dark:hover:bg-muted/50",
        link: "text-primary underline-offset-4 hover:underline",
        // Rankio: status dos grupos (tokens em app/globals.css; o texto do grupo sempre acompanha a cor).
        focar: "bg-status-focar-bg text-status-focar",
        acompanhar: "bg-status-acompanhar-bg text-status-acompanhar",
        revisar: "bg-status-revisar-bg text-status-revisar",
        qualificar: "bg-status-qualificar-bg text-status-qualificar",
        nao_pontuavel: "bg-status-nao-pontuavel-bg text-status-nao-pontuavel",
        // Resultado de uma negociação fechada: ganha em destaque, perdida em tom neutro (sem alarme).
        won: "bg-status-qualificar-bg text-status-qualificar",
        lost: "bg-muted text-muted-foreground",
        // Usos que não são grupo: a referência da evidência e o campo ausente.
        reference: "bg-status-focar-bg text-status-focar",
        missing: "bg-status-nao-pontuavel-bg text-status-nao-pontuavel",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot.Root : "span"

  return (
    <Comp
      data-slot="badge"
      data-variant={variant}
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
