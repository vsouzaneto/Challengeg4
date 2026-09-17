// Validação única das entradas das APIs. Nunca corta texto nem lote em silêncio:
// fora dos limites a requisição é recusada com status e mensagem explícitos.

export const MAX_TEXT_CHARS = 5_000;
export const MAX_BATCH = 500;
export const MIN_WORDS = 2;

export type Invalid = { ok: false; status: 400 | 413; error: string };
type TextResult = { ok: true; text: string } | Invalid;

export function validateText(value: unknown): TextResult {
  if (typeof value !== "string") {
    return { ok: false, status: 400, error: "O texto do ticket deve ser uma string." };
  }
  const text = value.trim();
  if (text.length > MAX_TEXT_CHARS) {
    return {
      ok: false,
      status: 413,
      error: `Texto com ${text.length} caracteres excede o limite de ${MAX_TEXT_CHARS}.`,
    };
  }
  if (text === "" || text.split(/\s+/).length < MIN_WORDS) {
    return { ok: false, status: 400, error: `Envie o texto do ticket com pelo menos ${MIN_WORDS} palavras.` };
  }
  return { ok: true, text };
}

export async function readJsonObject(request: Request): Promise<{ ok: true; body: Record<string, unknown> } | Invalid> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return { ok: false, status: 400, error: "Corpo da requisição não é um JSON válido." };
  }
  if (body === null || typeof body !== "object" || Array.isArray(body)) {
    return { ok: false, status: 400, error: "Corpo da requisição deve ser um objeto JSON." };
  }
  return { ok: true, body: body as Record<string, unknown> };
}

export type ClassifyInput =
  | { ok: true; mode: "single"; text: string }
  | { ok: true; mode: "batch"; texts: string[] }
  | (Invalid & { errors?: { index: number; status: 400 | 413; error: string }[] });

export function validateClassifyBody(body: Record<string, unknown>): ClassifyInput {
  const hasText = "text" in body;
  const hasTexts = "texts" in body;
  if (hasText === hasTexts) {
    return { ok: false, status: 400, error: "Envie exatamente um dos campos: text (um ticket) ou texts (lote)." };
  }
  if (hasText) {
    const r = validateText(body.text);
    return r.ok ? { ok: true, mode: "single", text: r.text } : r;
  }
  if (!Array.isArray(body.texts)) {
    return { ok: false, status: 400, error: "texts deve ser uma lista de strings." };
  }
  if (body.texts.length === 0) {
    return { ok: false, status: 400, error: "texts está vazio." };
  }
  if (body.texts.length > MAX_BATCH) {
    return { ok: false, status: 413, error: `Lote com ${body.texts.length} tickets excede o limite de ${MAX_BATCH}.` };
  }
  const texts: string[] = [];
  const errors: { index: number; status: 400 | 413; error: string }[] = [];
  body.texts.forEach((value, index) => {
    const r = validateText(value);
    if (r.ok) texts.push(r.text);
    else errors.push({ index, status: r.status, error: r.error });
  });
  if (errors.length > 0) {
    return {
      ok: false,
      status: 400,
      error: `${errors.length} ticket(s) inválido(s) no lote; nenhum foi classificado.`,
      errors,
    };
  }
  return { ok: true, mode: "batch", texts };
}
