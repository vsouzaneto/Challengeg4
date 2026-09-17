// @vitest-environment node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  readAudit,
  readDiagnostic,
  readModelMetrics,
  readRouting,
  readAutomationDocument,
} from "@/lib/data";

describe("contratos dos relatórios usados pela interface", () => {
  it("valida os quatro relatórios reais sem recorrer a dados de demonstração", async () => {
    const reports = await Promise.all([
      readAudit(),
      readDiagnostic(),
      readModelMetrics(),
      readRouting(),
    ]);
    for (const report of reports) expect(report).not.toBeNull();
  });
  it("inclui uma cópia fiel da proposta gerada dentro dos assets do app", async () => {
    expect(await readAutomationDocument()).toBe(
      readFileSync("../../docs/automacao.md", "utf8"),
    );
  });
});
