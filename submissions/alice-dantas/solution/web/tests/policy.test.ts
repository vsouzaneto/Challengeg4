// Mesma política em todas as telas: o front segue a ordem de grupos e os números que vêm da API e nunca
// decide grupo por conta própria (regra A, ADR-006). Um grupo novo no back aparece sem mudar componentes.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

import { describe, expect, test } from "vitest";

import { GROUP_LABELS } from "@/copy/pt-BR";

import { WEB_DIR, allPipelines, intelligence, load, readContract, teamPipeline } from "./fixtures";

const GROUP_KEYS = readContract().components.schemas.Group.properties.state.enum as string[];

function sources(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) return name === "ui" || name === "contract" ? [] : sources(path);
    return /\.tsx?$/.test(name) ? [path] : [];
  });
}

test("nenhum componente, página ou utilitário escreve uma chave de grupo à mão", () => {
  const key = new RegExp(`["'\`](${GROUP_KEYS.join("|")})["'\`]|\\.(${GROUP_KEYS.join("|")})\\b`);
  const files = [...sources(join(WEB_DIR, "app")), ...sources(join(WEB_DIR, "components")), ...sources(join(WEB_DIR, "lib"))];
  expect(files.length).toBeGreaterThan(10);
  const offenders = files.filter((path) => key.test(readFileSync(path, "utf8"))).map((path) => relative(WEB_DIR, path));
  expect(offenders).toEqual([]);
});

describe("as fixtures seguem uma política só", () => {
  test.each(allPipelines().map((p, i) => [i, p] as const))("carteira %i: grupos na ordem da API e contagens do summary", (_, p) => {
    expect(p.groups.map((g) => g.state)).toEqual(p.ordering.group_order);
    expect(p.ordering.group_order).toEqual(GROUP_KEYS);
    for (const g of p.groups) {
      expect(g.count).toBe(p.summary[g.state]);
      expect(g.items.every((item) => item.group === g.state)).toBe(true);
      expect(g.items.every((item) => item.reasons.map((r) => r.role).join() === "group,order")).toBe(true);
    }
    expect(p.groups.reduce((total, g) => total + g.count, 0)).toBe(p.summary.total);
  });

  test("regras, meta e carteiras trazem os mesmos limites", () => {
    const rules = load("rules") as { meta: Record<string, unknown> };
    for (const p of allPipelines()) expect(p.meta).toEqual(rules.meta);
    expect(rules.meta).toMatchObject({ won_cycle_limit_days: 100, cycle_limit_days: 138, cycle_percentile: 90 });
  });

  test("todo grupo do contrato tem nome no catálogo", () => {
    expect(Object.keys(GROUP_LABELS).sort()).toEqual([...GROUP_KEYS].sort());
  });
});

test("a Inteligência mostra as abertas com a política da Equipe (mesmo recorte, mesmos grupos)", () => {
  for (const [page, team] of [["intelligence-all", "team-all"], ["intelligence-east", "team-east"]]) {
    const intel = intelligence(page);
    const equipe = teamPipeline(team);
    expect(intel.open.summary).toEqual(equipe.summary);
    expect(intel.ordering).toEqual(equipe.ordering);
    expect(intel.meta).toEqual(equipe.meta);
  }
});
