import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

const SIZES = {
  sm: "size-7 rounded-md [&_svg]:size-4",
  default: "size-9 rounded-lg [&_svg]:size-5",
  lg: "size-10 rounded-lg [&_svg]:size-5",
} as const;

type Props = {
  icon: LucideIcon;
  /** Classes de fundo e cor: `GROUP_VISUAL[g].tile`, ou um tom neutro (padrão) ou de orientação. */
  tone?: string;
  size?: keyof typeof SIZES;
  className?: string;
};

/** Quadrado suave com um ícone (decorativo: o texto ao lado diz o que ele é). */
export function IconTile({ icon: Icon, tone = "bg-muted text-muted-foreground", size = "default", className }: Props) {
  return (
    <span aria-hidden className={cn("flex shrink-0 items-center justify-center", SIZES[size], tone, className)}>
      <Icon />
    </span>
  );
}

/** Tom de orientação (ação de verificar no CRM), fora das cores de grupo. */
export const GUIDE_TONE = "bg-accent text-primary-strong";
