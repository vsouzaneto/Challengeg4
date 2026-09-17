// @vitest-environment jsdom
import { readFileSync } from "node:fs";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { DiagnosticoReport } from "@/lib/types";
import { WasteCalculator } from "../waste-calculator";

const report: DiagnosticoReport = JSON.parse(
  readFileSync("data/diagnostico.json", "utf8"),
);
afterEach(cleanup);

describe("calculadora: premissas e estados inválidos", () => {
  it("recalcula o cenário e restaura os valores de referência", () => {
    const { container } = render(
      <WasteCalculator scenario={report.scenario} />,
    );
    const initial = container.querySelector(".scenario-value")?.textContent;
    fireEvent.change(screen.getByLabelText("Volume anual de tickets"), {
      target: { value: "60000" },
    });
    expect(container.querySelector(".scenario-value")?.textContent).not.toBe(
      initial,
    );
    fireEvent.click(screen.getByRole("button", { name: "Restaurar" }));
    expect(container.querySelector(".scenario-value")?.textContent).toBe(
      initial,
    );
  });
  it("suspende a estimativa quando uma fração excede 100%", () => {
    const { container } = render(
      <WasteCalculator scenario={report.scenario} />,
    );
    fireEvent.change(
      screen.getByLabelText("Tickets roteados automaticamente"),
      { target: { value: "130" } },
    );
    expect(container.querySelector(".scenario-value")).toBeNull();
    expect(screen.getByRole("status").textContent).toContain(
      "Percentuais devem ficar entre 0 e 100",
    );
  });
  it("preserva as perdas por retrabalho quando o acerto automático cai", () => {
    const { container } = render(
      <WasteCalculator scenario={report.scenario} />,
    );
    fireEvent.change(
      screen.getByLabelText("Acerto nos roteados automaticamente"),
      { target: { value: "0" } },
    );
    expect(container.querySelector(".badge-danger")?.textContent).toContain(
      "-",
    );
  });
});
