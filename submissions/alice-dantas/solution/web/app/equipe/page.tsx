import type { Metadata } from "next";
import { Suspense } from "react";

import { TeamPage } from "@/components/team/team-page";
import { NAV } from "@/copy/pt-BR";

export const metadata: Metadata = { title: NAV.equipe };

export default function Page() {
  return (
    <Suspense>
      <TeamPage />
    </Suspense>
  );
}
