import type { Metadata } from "next"

import { PipelineView } from "@/components/pipeline/pipeline-view"
import { getState } from "@/lib/server/store"
import { buildBoard, type Filters } from "@/lib/server/view"

export const metadata: Metadata = { title: "Pipeline" }

const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v) || undefined

export default async function Page({ searchParams }: PageProps<"/">) {
  const sp = await searchParams
  const filters: Filters = { regiao: one(sp.regiao), manager: one(sp.manager), vendedor: one(sp.vendedor) }
  const board = buildBoard(await getState(), filters)
  return <PipelineView board={board} />
}
