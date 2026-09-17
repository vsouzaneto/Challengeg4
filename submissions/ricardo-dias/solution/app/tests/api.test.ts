import { describe, expect, it, vi } from "vitest";
import { POST as classify } from "@/app/api/classify/route";
import { createDraftHandler, draftsEnabled } from "@/lib/draft";
import { loadModel, loadRules } from "@/lib/eval-data";
import type { ClassifyResponse } from "@/lib/types";
import { MAX_BATCH, MAX_TEXT_CHARS } from "@/lib/validation";

const post = (body: unknown, raw = false) =>
  new Request("http://test/api", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: raw ? (body as string) : JSON.stringify(body),
  });

const OK_TEXT = "laptop screen broken keyboard not working please help";
const words = (chars: number) => `${"a ".repeat(Math.floor(chars / 2))}`.slice(0, chars).padEnd(chars, "a");

describe("POST /api/classify — validação", () => {
  it.each([
    ["JSON inválido", "{", true, 400],
    ["corpo não-objeto", [1, 2], false, 400],
    ["sem text nem texts", {}, false, 400],
    ["text e texts juntos", { text: OK_TEXT, texts: [OK_TEXT] }, false, 400],
    ["text numérico", { text: 42 }, false, 400],
    ["text objeto", { text: { a: 1 } }, false, 400],
    ["text null", { text: null }, false, 400],
    ["text vazio", { text: "   " }, false, 400],
    ["uma palavra", { text: "laptop" }, false, 400],
    ["texts não-lista", { texts: "laptop broken" }, false, 400],
    ["texts vazio", { texts: [] }, false, 400],
  ])("%s → %i", async (_name, body, raw, status) => {
    const res = await classify(post(body, raw as boolean));
    expect(res.status).toBe(status);
    expect((await res.json()).error).toEqual(expect.any(String));
  });

  it("aceita exatamente o limite de caracteres e recusa (413) um acima, sem cortar", async () => {
    expect((await classify(post({ text: words(MAX_TEXT_CHARS) }))).status).toBe(200);
    const res = await classify(post({ text: words(MAX_TEXT_CHARS + 1) }));
    expect(res.status).toBe(413);
    expect((await res.json()).error).toMatch(/5001 caracteres excede o limite de 5000/);
  });

  it("aceita lote no limite e recusa (413) um acima", async () => {
    expect((await classify(post({ texts: Array(MAX_BATCH).fill(OK_TEXT) }))).status).toBe(200);
    expect((await classify(post({ texts: Array(MAX_BATCH + 1).fill(OK_TEXT) }))).status).toBe(413);
  });

  it("lote com itens inválidos é recusado inteiro, indicando cada índice", async () => {
    const res = await classify(post({ texts: [OK_TEXT, 7, { t: OK_TEXT }, "x", words(MAX_TEXT_CHARS + 1)] }));
    expect(res.status).toBe(400);
    const body = await res.json();
    expect(body.errors.map((e: { index: number }) => e.index)).toEqual([1, 2, 3, 4]);
    expect(body.errors[3].status).toBe(413);
    expect(body.results).toBeUndefined();
  });
});

describe("POST /api/classify — equivalência lote × unitário", () => {
  it("mesma categoria, confiança, rota e motivo para cada ticket", async () => {
    const texts = [
      OK_TEXT,
      "urgent phishing email received account hacked",
      "new starter belgrade thursday dear joiner attached thank kind regards administrator",
      "My payment failed and I want my money back for the damaged TV",
      "  please grant admin rights on my workstation to install software  ",
    ];
    const batch = (await (await classify(post({ texts }))).json()).results as ClassifyResponse[];
    expect(batch).toHaveLength(texts.length);
    for (const [i, text] of texts.entries()) {
      const single = (await (await classify(post({ text }))).json()) as ClassifyResponse;
      const { similar: _s, ...a } = single;
      const { similar: sb, ...b } = batch[i];
      void _s;
      expect(b).toEqual(a);
      expect(sb).toEqual([]);
    }
  });
});

describe("POST /api/draft — política aplicada no servidor", () => {
  const makeHandler = (hasProvider = true) => {
    const generate = vi.fn(async () => new Response("rascunho"));
    const handler = createDraftHandler({ getModel: loadModel, getRules: loadRules, hasProvider: () => hasProvider, generate });
    return { handler, generate };
  };

  it("ticket escalado recebe 403 e o provedor NÃO é chamado, mesmo com categoria forjada", async () => {
    const { handler, generate } = makeHandler();
    const res = await handler(post({ text: "urgent account hacked phishing please help", category: "Hardware" }));
    expect(res.status).toBe(403);
    expect(await res.json()).toMatchObject({ route: "escalar" });
    expect(generate).not.toHaveBeenCalled();
  });

  it("bloqueio vale mesmo sem provedor configurado (política antes da chave)", async () => {
    const { handler, generate } = makeHandler(false);
    expect((await handler(post({ text: "refund my order immediately please" }))).status).toBe(403);
    expect(generate).not.toHaveBeenCalled();
  });

  it("ticket permitido chama o provedor uma vez com a categoria do SERVIDOR, ignorando a do cliente", async () => {
    const { handler, generate } = makeHandler();
    const res = await handler(post({ text: OK_TEXT, category: "HR Support" }));
    expect(res.status).toBe(200);
    expect(generate).toHaveBeenCalledTimes(1);
    const [[arg]] = generate.mock.calls as unknown as [[{ text: string; category: string }]];
    expect(arg.category).not.toBe("HR Support");
    expect(res.headers.get("X-Draft-Category")).toBe(arg.category);
  });

  it("sem provedor e ticket permitido → 503 sem chamada", async () => {
    const { handler, generate } = makeHandler(false);
    expect((await handler(post({ text: OK_TEXT }))).status).toBe(503);
    expect(generate).not.toHaveBeenCalled();
  });

  it("rascunho exige opt-in explícito: token OIDC ou chave sozinhos não ligam o LLM", () => {
    expect(draftsEnabled({})).toBe(false);
    expect(draftsEnabled({ VERCEL_OIDC_TOKEN: "t" })).toBe(false);
    expect(draftsEnabled({ AI_GATEWAY_API_KEY: "k" })).toBe(false);
    expect(draftsEnabled({ DRAFTS_ENABLED: "true" })).toBe(false);
    expect(draftsEnabled({ DRAFTS_ENABLED: "1", AI_GATEWAY_API_KEY: "k" })).toBe(false);
    expect(draftsEnabled({ DRAFTS_ENABLED: "true", AI_GATEWAY_API_KEY: "k" })).toBe(true);
    expect(draftsEnabled({ DRAFTS_ENABLED: "true", VERCEL_OIDC_TOKEN: "t" })).toBe(true);
  });

  it("valida a entrada com as mesmas regras do classify", async () => {
    const { handler, generate } = makeHandler();
    expect((await handler(post({ text: 12 }))).status).toBe(400);
    expect((await handler(post({ text: words(MAX_TEXT_CHARS + 1) }))).status).toBe(413);
    expect((await handler(post("{", true))).status).toBe(400);
    expect(generate).not.toHaveBeenCalled();
  });
});
