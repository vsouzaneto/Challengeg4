import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { GUIDE_TONE, IconTile } from "@/components/app/icon-tile";
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { UI } from "@/copy/pt-BR";

/** Um número do topo da página: ícone, rótulo, valor grande e uma linha de apoio. `loading` troca o valor por um esqueleto. */
export function KpiCard({ label, value, help, icon, loading }: {
  label: string; value: string; help?: ReactNode; icon: LucideIcon; loading?: boolean;
}) {
  return (
    <Card size="sm">
      <CardHeader className="flex flex-row items-center gap-2">
        <IconTile icon={icon} tone={GUIDE_TONE} size="sm" />
        <CardDescription>{label}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-1">
        {loading ? (
          <Skeleton className="h-9 w-28" aria-label={UI.loading} />
        ) : (
          <>
            <span className="text-3xl font-semibold tabular-nums">{value}</span>
            {help && <span className="flex items-center gap-1 text-xs text-muted-foreground">{help}</span>}
          </>
        )}
      </CardContent>
    </Card>
  );
}
