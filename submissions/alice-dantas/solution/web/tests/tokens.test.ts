// AC-5.1: todo par de texto do design system tem contraste AA (≥ 4,5 : 1) nos dois temas.
import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, test } from "vitest";

import { WEB_DIR } from "./fixtures";

const css = readFileSync(join(WEB_DIR, "app", "globals.css"), "utf8");

function tokens(selector: string): Record<string, string> {
  const block = css.match(new RegExp(`(?:^|\\n)${selector.replace(".", "\\.")} \\{([^}]*)\\}`))?.[1] ?? "";
  return Object.fromEntries([...block.matchAll(/--([\w-]+):\s*(#[0-9a-f]{6});/gi)].map(([, name, hex]) => [name, hex]));
}

function luminance(hex: string): number {
  const channels = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const [r, g, b] = channels.map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

const contrast = (a: string, b: string) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

// [texto, fundo]: os pares que a interface usa.
const PAIRS = [
  ["foreground", "background"], ["foreground", "card"], ["card-foreground", "card"],
  ["popover-foreground", "popover"], ["muted-foreground", "background"], ["muted-foreground", "card"],
  ["muted-foreground", "muted"], ["primary-foreground", "primary"], ["primary-strong", "background"],
  ["primary-strong", "card"], ["primary-strong", "accent"], ["secondary-foreground", "secondary"],
  ["accent-foreground", "accent"], ["destructive", "card"], ["destructive", "background"],
  ["status-focar", "status-focar-bg"], ["status-acompanhar", "status-acompanhar-bg"],
  ["status-revisar", "status-revisar-bg"],
  ["status-revisar", "background"], ["status-qualificar", "status-qualificar-bg"],
  ["status-nao-pontuavel", "status-nao-pontuavel-bg"],
  ["foreground", "heat-1"], ["foreground", "heat-2"], ["foreground", "heat-3"], ["foreground", "heat-4"],
] as const;

// Objetos não textuais (barras, segmentos, ícones grandes): ≥ 3 : 1 sobre o card e o fundo (WCAG 1.4.11).
const NON_TEXT = [
  "status-focar-fill", "status-qualificar-fill", "status-acompanhar-fill", "status-revisar-fill",
  "status-nao-pontuavel-fill", "chart-3",
].flatMap((fill) => [[fill, "card"], [fill, "background"]] as const);

describe.each([[":root", "claro"], [".dark", "escuro"]])("tema %s (%s)", (selector) => {
  const theme = tokens(selector);
  test.each(NON_TEXT)("preenchimento %s sobre %s", (fill, background) => {
    expect(theme[fill], `--${fill}`).toBeDefined();
    expect(contrast(theme[fill], theme[background])).toBeGreaterThanOrEqual(3);
  });
  test.each(PAIRS)("%s sobre %s", (text, background) => {
    expect(theme[text], `--${text}`).toBeDefined();
    expect(theme[background], `--${background}`).toBeDefined();
    expect(contrast(theme[text], theme[background])).toBeGreaterThanOrEqual(4.5);
  });
  test("lilás da marca preservado", () => {
    expect(theme.primary).toBe("#8091fa");
  });
});
