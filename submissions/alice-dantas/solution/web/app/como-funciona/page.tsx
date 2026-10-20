import type { Metadata } from "next";

import { RulesPage } from "@/components/rules/rules-page";
import { NAV } from "@/copy/pt-BR";

export const metadata: Metadata = { title: NAV.comoFunciona };

export default function Page() {
  return <RulesPage />;
}
