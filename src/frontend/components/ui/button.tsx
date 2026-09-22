import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-medium transition-[background-color,color,border-color] duration-[var(--g4s-duration)] disabled:pointer-events-none disabled:bg-[var(--g4s-bg-subtle)] disabled:text-[var(--g4s-fg-muted)] disabled:opacity-100 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-secondary',
        destructive:
          'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline:
          'border border-[var(--g4s-border-strong)] bg-transparent text-primary hover:bg-[var(--g4s-bg-subtle)]',
        secondary:
          'bg-secondary text-secondary-foreground hover:bg-primary',
        ghost:
          'text-[var(--g4s-fg-medium)] hover:text-primary hover:bg-[var(--g4s-bg-subtle)]',
        link: 'text-[var(--g4s-fg-medium)] underline-offset-4 hover:text-primary hover:underline',
      },
      size: {
        default: 'h-10 px-6 py-2 has-[>svg]:px-4',
        sm: 'h-9 gap-1.5 px-4 has-[>svg]:px-3',
        lg: 'h-11 px-6 has-[>svg]:px-5',
        icon: 'size-10',
        'icon-sm': 'size-8',
        'icon-lg': 'size-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : 'button'

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
