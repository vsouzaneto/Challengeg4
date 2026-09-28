import type { Metadata } from "next"

import { ReferenceView } from "./_reference/reference-view"

export const metadata: Metadata = { title: "Referência" }

// Página de referência da fundação. Substitua pela primeira jornada real
// e apague a pasta _reference.
export default function Page() {
  return <ReferenceView />
}
