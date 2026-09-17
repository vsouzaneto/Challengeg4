import { getHoldout } from "@/lib/server-data";

// GET /api/sample?n=200 → tickets aleatórios do conjunto de teste (nunca vistos no treino)
export async function GET(request: Request) {
  const n = Math.min(Math.max(Number(new URL(request.url).searchParams.get("n")) || 1, 1), 500);
  const pool = getHoldout();
  const picked = [...pool];
  for (let i = picked.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [picked[i], picked[j]] = [picked[j], picked[i]];
  }
  return Response.json({ items: picked.slice(0, n) }, { headers: { "Cache-Control": "no-store" } });
}
