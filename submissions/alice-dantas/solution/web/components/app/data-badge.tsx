"use client";

import { CalendarDays, RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { UI, dataLabel } from "@/copy/pt-BR";
import { useMeta } from "@/lib/use-meta";

/** De quando são os dados: sempre visível, para o vendedor saber a data da lista. Se a data não carrega, o selo
 * diz que falta a conexão (e não que os dados "não existem") e deixa tentar de novo. */
export function DataBadge() {
  const { meta, error, retry } = useMeta();
  if (!meta && !error) return <Skeleton className="h-5 w-32 rounded-4xl" />;
  if (!meta) {
    return (
      <Button variant="outline" size="xs" className="rounded-4xl text-muted-foreground" onClick={retry}
              title={UI.dataRetry} aria-label={`${UI.dataUnavailable}. ${UI.dataRetry}`}>
        <RefreshCw aria-hidden />
        {UI.dataUnavailable}
      </Button>
    );
  }
  return (
    <Badge variant="outline" className="text-muted-foreground">
      <CalendarDays aria-hidden className="max-sm:hidden" />
      {dataLabel(meta)}
    </Badge>
  );
}
