import type { Metadata } from "next";
import { Suspense } from "react";

import { PortfolioPage } from "@/components/portfolio/portfolio-page";
import { NAV } from "@/copy/pt-BR";

export const metadata: Metadata = { title: NAV.carteira };

export default function Page() {
  return (
    <Suspense>
      <PortfolioPage />
    </Suspense>
  );
}
