// Contrato: os tipos e a validação gerados batem com o openapi.json e aceitam as respostas da API.
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { describe, expect, test } from "vitest";

import { zIntelligence, zSellerPipeline } from "@/lib/contract/zod.gen";

import {
  INTELLIGENCE_DEALS, INTELLIGENCE_PAGES, SELLER_PIPELINES, TEAM_PIPELINES, WEB_DIR, errors, intelligence,
  intelligenceDeals, load, meta, sellerPipeline, sellers, teamPipeline,
} from "./fixtures";

describe("respostas da API passam na validação do contrato", () => {
  test.each(SELLER_PIPELINES)("%s", (name) => {
    expect(() => sellerPipeline(name)).not.toThrow();
  });
  test.each(TEAM_PIPELINES)("%s", (name) => {
    expect(() => teamPipeline(name)).not.toThrow();
  });
  test.each(INTELLIGENCE_PAGES)("%s", (name) => {
    expect(() => intelligence(name)).not.toThrow();
  });
  test.each(INTELLIGENCE_DEALS)("%s", (name) => {
    expect(() => intelligenceDeals(name)).not.toThrow();
  });
  test("meta, vendedores e erros", () => {
    expect(meta().contract_version).toBe(7);
    expect(sellers().sellers.length).toBeGreaterThan(0);
    expect(Object.keys(errors())).toEqual(["404", "422", "503"]);
  });
});

describe("resposta fora do contrato é recusada", () => {
  const base = () => structuredClone(load("pipeline-ana-alfa")) as any;

  test("código de motivo desconhecido", () => {
    const payload = base();
    payload.groups[0].items[0].reasons[0].code = "alta_chance";
    expect(zSellerPipeline.safeParse(payload).success).toBe(false);
  });
  test("tipo errado", () => {
    const payload = base();
    payload.groups[0].items[0].age_days = "104";
    expect(zSellerPipeline.safeParse(payload).success).toBe(false);
  });
  test("campo obrigatório ausente", () => {
    const payload = base();
    delete payload.groups[0].items[0].next_action;
    expect(zSellerPipeline.safeParse(payload).success).toBe(false);
  });
  test("diagnóstico ou descoberta desconhecidos", () => {
    const payload = structuredClone(load("intelligence-rich")) as any;
    payload.diagnostics[0].code = "venda_mais";
    expect(zIntelligence.safeParse(payload).success).toBe(false);
    const other = structuredClone(load("intelligence-rich")) as any;
    other.findings[0].code = "melhor_vendedor";
    expect(zIntelligence.safeParse(other).success).toBe(false);
  });
  test("campo novo do back é tolerado (mudança aditiva não quebra a tela)", () => {
    const payload = base();
    payload.groups[0].items[0].campo_novo = 1;
    expect(zSellerPipeline.safeParse(payload).success).toBe(true);
  });
});

test("lib/contract está atualizado com contract/openapi.json", { timeout: 60_000 }, () => {
  const out = mkdtempSync(join(tmpdir(), "contract-"));
  execFileSync(join(WEB_DIR, "node_modules", ".bin", "openapi-ts"),
    ["-i", "./contract/openapi.json", "-o", out, "-p", "zod", "-p", "@hey-api/typescript"],
    { cwd: WEB_DIR, stdio: "pipe" });
  const committed = join(WEB_DIR, "lib", "contract");
  expect(readdirSync(out).sort()).toEqual(readdirSync(committed).sort());
  for (const file of readdirSync(out)) {
    expect(readFileSync(join(committed, file), "utf8"), `${file}: rode npm run contract`)
      .toBe(readFileSync(join(out, file), "utf8"));
  }
});
