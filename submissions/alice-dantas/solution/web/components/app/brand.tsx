import { ChartNoAxesColumnIncreasing } from "lucide-react";
import Link from "next/link";

import { BRAND } from "@/copy/pt-BR";

export function Brand() {
  return (
    <Link
      href="/carteira"
      aria-label={BRAND.name}
      className="flex w-fit items-center gap-2 rounded-md text-xl font-bold tracking-tight outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
    >
      <ChartNoAxesColumnIncreasing className="size-5 text-primary" strokeWidth={2.75} aria-hidden />
      <span>{BRAND.wordmark}</span>
    </Link>
  );
}
