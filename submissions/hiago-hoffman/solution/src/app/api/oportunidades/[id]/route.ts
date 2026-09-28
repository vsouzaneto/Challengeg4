import { getState } from "@/lib/server/store"
import { buildDetail } from "@/lib/server/view"

// Detalhamento do score de uma oportunidade aberta (carregado ao clicar no card).
export async function GET(_req: Request, ctx: RouteContext<"/api/oportunidades/[id]">) {
  const { id } = await ctx.params
  const detail = buildDetail(await getState(), id)
  if (!detail) return Response.json({ error: "Oportunidade não encontrada ou já encerrada." }, { status: 404 })
  return Response.json(detail)
}
