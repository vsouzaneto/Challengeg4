import { classifyTicket } from "@/lib/classifier";
import { getModel, getNeighbors, getPolicyRules } from "@/lib/server-data";
import { readJsonObject, validateClassifyBody } from "@/lib/validation";

// POST { text } → ClassifyResponse
// POST { texts: string[] } (1..500) → { results: ClassifyResponse[] } — mesmo caminho do unitário, sem "similar".
// Entradas inválidas ou acima dos limites são recusadas (400/413), nunca cortadas.
export async function POST(request: Request) {
  const parsed = await readJsonObject(request);
  if (!parsed.ok) return Response.json({ error: parsed.error }, { status: parsed.status });
  const input = validateClassifyBody(parsed.body);
  if (!input.ok) {
    const { error, errors, status } = input;
    return Response.json(errors ? { error, errors } : { error }, { status });
  }

  const model = getModel();
  const rules = getPolicyRules();
  if (input.mode === "batch") {
    return Response.json({ results: input.texts.map((t) => classifyTicket(model, rules, t, null)) });
  }
  return Response.json(classifyTicket(model, rules, input.text, getNeighbors()));
}
