import type { IncomingMessage, ServerResponse } from "node:http";

export class HttpError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

export function sendJson(response: ServerResponse, status: number, payload: unknown, headers: Record<string, string> = {}): void {
  response.statusCode = status;
  response.setHeader("Content-Type", "application/json; charset=utf-8");
  for (const [name, value] of Object.entries(headers)) {
    response.setHeader(name, value);
  }
  response.end(JSON.stringify(payload));
}

export async function readJson<T>(request: IncomingMessage): Promise<T> {
  const chunks: Buffer[] = [];
  let size = 0;

  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buffer.length;
    if (size > 1_000_000) {
      throw new HttpError(413, "Corpo da requisição muito grande.");
    }
    chunks.push(buffer);
  }

  if (chunks.length === 0) {
    throw new HttpError(400, "Corpo da requisição obrigatório.");
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(Buffer.concat(chunks).toString("utf8")) as unknown;
  } catch {
    throw new HttpError(400, "JSON inválido.");
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new HttpError(400, "O corpo deve ser um objeto JSON.");
  }
  return parsed as T;
}

export function requireString(value: unknown, field: string, options: { min?: number; max?: number } = {}): string {
  if (typeof value !== "string") {
    throw new HttpError(400, `${field} é obrigatório.`);
  }
  const normalized = value.trim();
  if (normalized.length < (options.min ?? 1) || normalized.length > (options.max ?? 255)) {
    throw new HttpError(400, `${field} deve conter entre ${options.min ?? 1} e ${options.max ?? 255} caracteres.`);
  }
  return normalized;
}

export function requirePassword(value: unknown): string {
  if (typeof value !== "string" || value.length < 8 || value.length > 200) {
    throw new HttpError(400, "Senha deve conter entre 8 e 200 caracteres.");
  }
  return value;
}

export function optionalString(value: unknown, field: string, max = 255): string | null {
  if (value === undefined || value === null || value === "") {
    return null;
  }
  return requireString(value, field, { max });
}

export function requireBoolean(value: unknown, field: string): boolean {
  if (typeof value !== "boolean") {
    throw new HttpError(400, `${field} deve ser verdadeiro ou falso.`);
  }
  return value;
}
