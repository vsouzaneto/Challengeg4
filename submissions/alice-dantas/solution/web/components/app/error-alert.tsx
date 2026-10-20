import { CircleAlert, TriangleAlert } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { DATA_WARNING } from "@/copy/pt-BR";

export function ErrorAlert({ message }: { message: string }) {
  return (
    <Alert variant="destructive">
      <CircleAlert aria-hidden />
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}

/** Dados diferentes da versão auditada (`meta.audited` falso). */
export function DataWarning() {
  return (
    <Alert variant="warning">
      <TriangleAlert aria-hidden />
      <AlertDescription>{DATA_WARNING}</AlertDescription>
    </Alert>
  );
}
