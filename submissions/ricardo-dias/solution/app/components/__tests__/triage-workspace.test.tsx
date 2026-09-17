// @vitest-environment jsdom
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  act,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { TriageWorkspace } from "../triage-workspace";
import type { ClassifyResponse } from "@/lib/types";

const prediction: ClassifyResponse = {
  category: "Hardware",
  confidence: 0.9,
  knownShare: 1,
  probabilities: [
    { label: "Hardware", p: 0.9 },
    { label: "Access", p: 0.1 },
  ],
  topTerms: [{ term: "screen", weight: 0.2 }],
  route: "auto",
  reasonCode: "auto",
  routeReason: "Roteado automaticamente para a fila Hardware.",
  draftAllowed: true,
  similar: [],
};
function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
async function classify() {
  fireEvent.change(screen.getByLabelText("Descrição do atendimento"), {
    target: { value: "laptop screen broken" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Classificar ticket" }));
  await screen.findByRole("heading", { name: "Hardware" });
}
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("Triagem: interações e falhas de integração", () => {
  it("carrega amostra da API e só revela a referência depois da classificação", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        json({
          items: [{ id: 42, text: "laptop screen broken", label: "Hardware" }],
        }),
      )
      .mockResolvedValueOnce(json(prediction));
    vi.stubGlobal("fetch", fetchMock);
    render(<TriageWorkspace />);
    fireEvent.click(screen.getByRole("button", { name: "Amostra aleatória" }));
    await waitFor(() =>
      expect(
        (
          screen.getByLabelText(
            "Descrição do atendimento",
          ) as HTMLTextAreaElement
        ).value,
      ).toBe("laptop screen broken"),
    );
    expect(screen.queryByText(/Rótulo de referência:/)).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Classificar ticket" }));
    await screen.findByText(/Rótulo de referência: Hardware/);
    expect(fetchMock.mock.calls[0][0]).toBe("/api/sample?n=1");
  });

  it("descarta uma resposta atrasada quando o usuário altera o ticket", async () => {
    let complete!: (value: Response) => void;
    const fetchMock = vi.fn(
      () =>
        new Promise<Response>((resolve) => {
          complete = resolve;
        }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<TriageWorkspace />);
    const input = screen.getByLabelText("Descrição do atendimento");
    fireEvent.change(input, { target: { value: "laptop screen broken" } });
    fireEvent.click(screen.getByRole("button", { name: "Classificar ticket" }));
    fireEvent.change(input, { target: { value: "another different ticket" } });
    await act(async () => {
      complete(json(prediction));
    });
    expect(screen.queryByRole("heading", { name: "Hardware" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Gerar rascunho" })).toBeNull();
  });

  it("mantém a classificação se o serviço de rascunho retornar 503", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(json(prediction))
      .mockResolvedValueOnce(
        json({ error: "Rascunho indisponível neste ambiente." }, 503),
      );
    vi.stubGlobal("fetch", fetchMock);
    render(<TriageWorkspace />);
    await classify();
    fireEvent.click(screen.getByRole("button", { name: "Gerar rascunho" }));
    await screen.findByRole("alert");
    expect(screen.getByRole("heading", { name: "Hardware" })).toBeTruthy();
    expect(screen.getByRole("alert").textContent).toContain(
      "Rascunho indisponível",
    );
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({
      text: "laptop screen broken",
    });
  });

  it("não oferece rascunho quando a política exige escalação", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          json({
            ...prediction,
            route: "escalar",
            reasonCode: "escalation_terms",
            draftAllowed: false,
            routeReason: "Sinal de risco: atendente sênior.",
          }),
        ),
    );
    render(<TriageWorkspace />);
    await classify();
    expect(screen.queryByRole("button", { name: "Gerar rascunho" })).toBeNull();
    expect(
      screen.getByText("Este atendimento exige uma resposta humana."),
    ).toBeTruthy();
  });

  it("lê o stream de rascunho e oferece cópia apenas ao concluir", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode("Olá, vamos verificar "));
        controller.enqueue(encoder.encode("o equipamento."));
        controller.close();
      },
    });
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(json(prediction))
        .mockResolvedValueOnce(new Response(stream)),
    );
    render(<TriageWorkspace />);
    await classify();
    fireEvent.click(screen.getByRole("button", { name: "Gerar rascunho" }));
    await screen.findByRole("button", { name: "Copiar rascunho" });
    expect(
      screen.getByText("Olá, vamos verificar o equipamento."),
    ).toBeTruthy();
  });

  it("envia o lote em uma requisição e contabiliza o destino retornado pela API", async () => {
    const items = Array.from({ length: 200 }, (_, id) => ({
      id,
      text: `ticket sample ${id}`,
      label: "Hardware",
    }));
    const results = items.map((_, id) => ({
      ...prediction,
      route: id < 100 ? "auto" : "revisao_humana",
    }));
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(json({ items }))
      .mockResolvedValueOnce(json({ results }));
    vi.stubGlobal("fetch", fetchMock);
    render(<TriageWorkspace />);
    fireEvent.click(
      screen.getByRole("button", { name: "Avaliar uma amostra" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Testar em 200 tickets" }),
    );
    await screen.findByText("Avaliação concluída: 200 tickets classificados.");
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(JSON.parse(fetchMock.mock.calls[1][1].body).texts).toHaveLength(200);
    expect(
      screen.getByText("100 tickets passaram por todas as regras"),
    ).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Mostrar erros" }));
    expect(screen.getByText("Nenhuma divergência nesta amostra.")).toBeTruthy();
  });

  it("não publica métricas se a API retornar um lote incompleto", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(
          json({
            items: [{ id: 1, text: "laptop screen broken", label: "Hardware" }],
          }),
        )
        .mockResolvedValueOnce(json({ results: [] })),
    );
    render(<TriageWorkspace />);
    fireEvent.click(
      screen.getByRole("button", { name: "Avaliar uma amostra" }),
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Testar em 200 tickets" }),
    );
    await screen.findByRole("alert");
    expect(screen.queryByText("Acerto na amostra")).toBeNull();
  });

  it("mostra o erro de validação da API sem fabricar um resultado", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          json({ error: "Ticket inválido para classificação." }, 400),
        ),
    );
    render(<TriageWorkspace />);
    fireEvent.change(screen.getByLabelText("Descrição do atendimento"), {
      target: { value: "laptop broken" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Classificar ticket" }));
    expect((await screen.findByRole("alert")).textContent).toContain(
      "Ticket inválido",
    );
    expect(screen.queryByText("Resultado da triagem")).toBeNull();
  });
});
