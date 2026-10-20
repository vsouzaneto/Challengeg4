import type { Metadata } from "next";
import { Suspense } from "react";

import { EvidencePage } from "@/components/evidence/evidence-page";
import { NAV } from "@/copy/pt-BR";

export const metadata: Metadata = { title: NAV.evidencia };

export default function Page() {
  return (
    <Suspense>
      <EvidencePage />
    </Suspense>
  );
}
