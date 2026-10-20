import type { Metadata } from "next";
import { Suspense } from "react";

import { IntelligencePage } from "@/components/intelligence/intelligence-page";
import { NAV } from "@/copy/pt-BR";

export const metadata: Metadata = { title: NAV.inteligencia };

export default function Page() {
  return (
    <Suspense>
      <IntelligencePage />
    </Suspense>
  );
}
