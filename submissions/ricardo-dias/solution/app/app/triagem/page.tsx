import type { Metadata } from "next";
import Link from "next/link";
import { TriageWorkspace } from "@/components/triage-workspace";
import { PageHeading } from "@/components/ui";
import { Icon } from "@/components/icons";

export const metadata: Metadata = { title: "Triagem" };
export default function TriagePage() {
  return (
    <>
      <PageHeading
        eyebrow="Da solicitação ao encaminhamento"
        title="Um próximo passo para cada ticket."
        description="Experimente a classificação, entenda a decisão e veja onde a supervisão humana entra no fluxo."
        action={
          <Link className="button secondary" href="/modelo">
            Ver avaliação do modelo
            <Icon name="arrow" width={16} />
          </Link>
        }
      />
      <TriageWorkspace />
    </>
  );
}
