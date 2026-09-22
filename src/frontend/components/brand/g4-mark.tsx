import Link from "next/link";

import { cn } from "@/lib/utils";

type G4MarkProps = {
  href?: string;
  scrolled?: boolean;
  className?: string;
};

export function G4Mark({ href = "/", scrolled = false, className }: G4MarkProps) {
  return (
    <Link href={href} className={cn("flex items-center gap-2 group", className)}>
      <img
        src="/brand/logo-g4-completa-branca.svg"
        alt="G4"
        className={cn(
          "w-auto transition-all duration-500",
          scrolled ? "h-6" : "h-8",
        )}
      />
    </Link>
  );
}
