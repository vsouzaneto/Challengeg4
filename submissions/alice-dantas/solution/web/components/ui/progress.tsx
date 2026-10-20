"use client"

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "cn"
import { Progress as ProgressPrimitive } from "radix-ui"

// Rankio: cor do preenchimento ligada aos tokens (app/globals.css), como as variantes de grupo do Badge.
const progressIndicatorVariants = cva("size-full flex-1 transition-all", {
  variants: {
    tone: {
      default: "bg-primary",
      neutral: "bg-chart-3",
      focar: "bg-status-focar-fill",
      acompanhar: "bg-status-acompanhar-fill",
      revisar: "bg-status-revisar-fill",
      qualificar: "bg-status-qualificar-fill",
      nao_pontuavel: "bg-status-nao-pontuavel-fill",
    },
  },
  defaultVariants: {
    tone: "default",
  },
})

function Progress({
  className,
  value,
  tone,
  ...props
}: React.ComponentProps<typeof ProgressPrimitive.Root> &
  VariantProps<typeof progressIndicatorVariants>) {
  return (
    <ProgressPrimitive.Root
      data-slot="progress"
      className={cn(
        "relative flex h-1.5 w-full items-center overflow-x-hidden rounded-full bg-muted",
        className
      )}
      value={value}
      {...props}
    >
      <ProgressPrimitive.Indicator
        data-slot="progress-indicator"
        className={progressIndicatorVariants({ tone })}
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      />
    </ProgressPrimitive.Root>
  )
}

export { Progress, progressIndicatorVariants }
