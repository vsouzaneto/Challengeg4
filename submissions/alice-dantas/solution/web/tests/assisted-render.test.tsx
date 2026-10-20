// Priorização assistida na Carteira: do botão no cartão ao resultado, com as respostas só no navegador.
import { fireEvent, render as renderDom, screen, waitFor, within } from "@testing-library/react";
import { useState, type ReactElement } from "react";
import { describe, expect, test, vi } from "vitest";

import { SelectStep } from "@/components/assessment/select-step";
import { PortfolioPage } from "@/components/portfolio/portfolio-page";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ANSWER_LABELS, ASSISTED, CATEGORY_LABELS, QUESTIONS } from "@/copy/assisted";
import { UI } from "@/copy/pt-BR";
import type { Answers, Dimension } from "@/lib/assisted/model";
import type { Item, SellerPipeline } from "@/lib/contract";

import { navigation } from "./navigation";
import { load } from "./fixtures";

const render = (ui: ReactElement) => renderDom(ui, { wrapper: TooltipProvider });
const ok = (body: unknown) => ({ status: 200, body });

/** A carteira da Ana com o empate E050 + E100 (GTX Basic, 550) no topo do cartão. */
function tiedPipeline(): SellerPipeline {
  const payload = structuredClone(load("pipeline-ana-alfa")) as SellerPipeline;
  const focar = payload.groups[0];
  focar.items = [...focar.items.filter((i) => i.tie_size > 1), ...focar.items.filter((i) => i.tie_size === 1)];
  return payload;
}

function stubApi(payload: SellerPipeline) {
  const fetch = vi.fn(async (url: string) => {
    const body = url.endsWith("/api/sellers") ? load("sellers") : url.endsWith("/api/meta") ? load("meta") : payload;
    return new Response(JSON.stringify(body), { status: 200 });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const escape = (text: string) => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const group = (dimension: Dimension) => screen.getByRole("radiogroup", { name: new RegExp(escape(QUESTIONS[dimension])) });
const pick = (dimension: Dimension, label: string) =>
  fireEvent.click(within(group(dimension)).getByRole("radio", { name: label }));

const FULL_NO_ACTION: Answers = {
  interest: "replied", timing: "within_30", need: "confirmed", urgency: "concrete", budget: "confirmed",
  authority: "access", progress: "none",
};
function answer(answers: Answers) {
  for (const [dimension, option] of Object.entries(answers)) {
    pick(dimension as Dimension, (ANSWER_LABELS as Record<string, Record<string, string>>)[dimension][option]);
  }
}
const next = () => fireEvent.click(screen.getByRole("button", { name: new RegExp(`^(${ASSISTED.ask.next}|${ASSISTED.ask.finish})$`) }));

async function openTieSheet() {
  navigation.go("/carteira?vendedor=Ana%20Alfa");
  const fetch = stubApi(tiedPipeline());
  render(<PortfolioPage />);
  const card = (await screen.findByText(UI.tieChip(2, "GTX Basic", 550))).closest("[data-slot=card]") as HTMLElement;
  fireEvent.click(within(card).getByRole("button", { name: ASSISTED.card.button }));
  const sheet = await screen.findByRole("dialog", { name: ASSISTED.title });
  return { fetch, sheet, card };
}

describe("do cartão ao resultado", () => {
  test("o botão só aparece no empate, e a seleção pede de 2 a 5 sem nada marcado", async () => {
    const { sheet } = await openTieSheet();
    const boxes = within(sheet).getAllByRole("checkbox");
    expect(boxes).toHaveLength(2);
    expect(boxes.every((box) => box.getAttribute("aria-checked") === "false")).toBe(true);
    const go = within(sheet).getByRole("button", { name: ASSISTED.select.next }) as HTMLButtonElement;
    expect(go.disabled).toBe(true);
    fireEvent.click(boxes[0]);
    expect(go.disabled).toBe(true);
    fireEvent.click(boxes[1]);
    expect(go.disabled).toBe(false);
    expect(within(sheet).getByText(new RegExp(escape(ASSISTED.select.counter(2))))).toBeTruthy();
  });

  test("sem empate no topo, o cartão não oferece avaliar", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(structuredClone(load("pipeline-ana-alfa")) as SellerPipeline);
    render(<PortfolioPage />);
    await screen.findByRole("tablist");
    expect(screen.queryByRole("button", { name: ASSISTED.card.button })).toBeNull();
  });

  test("responder, ver a ordem por pontos, o bloco à parte e o selo na Carteira; nada vai à rede", async () => {
    const { fetch, sheet } = await openTieSheet();
    for (const box of within(sheet).getAllByRole("checkbox")) fireEvent.click(box);
    fireEvent.click(within(sheet).getByRole("button", { name: ASSISTED.select.next }));

    // E050: tudo confirmado, sem ação combinada (95 pontos).
    expect(await screen.findByText(ASSISTED.ask.progress(1, 2))).toBeTruthy();
    answer(FULL_NO_ACTION);
    next();
    // E100: "Não sei" em tudo.
    expect(await screen.findByText(ASSISTED.ask.progress(2, 2))).toBeTruthy();
    for (const radio of screen.getAllByRole("radio", { name: "Não sei" })) fireEvent.click(radio);
    next();

    const ordered = await screen.findByRole("list", { name: ASSISTED.result.title });
    const cards = within(ordered).getAllByText(/^\d+º/);
    expect(cards).toHaveLength(1);
    const first = ordered.querySelector("[data-opportunity]") as HTMLElement;
    expect(first.getAttribute("data-opportunity")).toBe("E050");
    expect(within(first).getByText(ASSISTED.points(95))).toBeTruthy();
    expect(within(first).getByText(CATEGORY_LABELS.define_continuity)).toBeTruthy();
    expect(within(first).getByText(ASSISTED.result.position(1, false))).toBeTruthy();

    const aside = screen.getByRole("region", { name: ASSISTED.result.asideTitle });
    expect(aside.querySelector("[data-opportunity]")?.getAttribute("data-opportunity")).toBe("E100");
    expect(within(aside).getByText(ASSISTED.points(0))).toBeTruthy();
    expect(screen.getByText(ASSISTED.disclaimer)).toBeTruthy();
    expect(within(screen.getByRole("dialog", { name: ASSISTED.title })).queryByText(/%/)).toBeNull();

    // Nenhuma chamada além da API de leitura que a tela já usa.
    for (const [url, init] of fetch.mock.calls as unknown as [string, RequestInit | undefined][]) {
      expect(url).toMatch(/\/api\/(sellers|meta|intelligence)/);
      expect(init?.method ?? "GET").toBe("GET");
    }

    // Ficou no navegador, e o selo aparece no cartão sem mudar a ordem oficial.
    const stored = JSON.parse(window.localStorage.getItem("rankio.avaliacoes.v1")!);
    expect(Object.keys(stored.assessments["Ana Alfa"]).sort()).toEqual(["E050", "E100"]);
    fireEvent.click(screen.getByRole("button", { name: ASSISTED.close, hidden: true }));
    await waitFor(() => expect(screen.queryByRole("dialog", { name: ASSISTED.title })).toBeNull());
    expect(screen.getAllByText(ASSISTED.mark.done(CATEGORY_LABELS.define_continuity)).length).toBeGreaterThan(0);
    expect(screen.getAllByText(ASSISTED.mark.aside).length).toBeGreaterThan(0);
  });

  test("avaliação incompleta fica fora da ordem como comparação parcial, e dá para retomar", async () => {
    const { sheet } = await openTieSheet();
    for (const box of within(sheet).getAllByRole("checkbox")) fireEvent.click(box);
    fireEvent.click(within(sheet).getByRole("button", { name: ASSISTED.select.next }));
    await screen.findByText(ASSISTED.ask.progress(1, 2));
    answer(FULL_NO_ACTION);
    next();
    await screen.findByText(ASSISTED.ask.progress(2, 2));
    pick("interest", ANSWER_LABELS.interest.replied); // só uma resposta
    next();

    const partial = await screen.findByRole("region", { name: ASSISTED.result.partialTitle });
    expect(within(partial).getByText(ASSISTED.result.partialBody(["E100"]))).toBeTruthy();
    fireEvent.click(within(partial).getByRole("button", { name: `${ASSISTED.result.answer} E100` }));
    expect(await screen.findByText(ASSISTED.ask.progress(2, 2))).toBeTruthy();
    expect(within(group("interest")).getByRole("radio", { name: ANSWER_LABELS.interest.replied }).getAttribute("aria-checked")).toBe("true");
  });

  test("o vendedor reordena e a posição fica identificada como escolhida por ele", async () => {
    const { sheet } = await openTieSheet();
    for (const box of within(sheet).getAllByRole("checkbox")) fireEvent.click(box);
    fireEvent.click(within(sheet).getByRole("button", { name: ASSISTED.select.next }));
    await screen.findByText(ASSISTED.ask.progress(1, 2));
    answer(FULL_NO_ACTION);
    next();
    await screen.findByText(ASSISTED.ask.progress(2, 2));
    answer({ ...FULL_NO_ACTION, timing: "later", budget: "none", urgency: "none" });
    next();

    const list = await screen.findByRole("list", { name: ASSISTED.result.title });
    const order = () => [...list.querySelectorAll("[data-opportunity]")].map((el) => el.getAttribute("data-opportunity"));
    expect(order()).toEqual(["E050", "E100"]);
    fireEvent.click(screen.getByRole("button", { name: ASSISTED.result.down("E050") }));
    expect(order()).toEqual(["E100", "E050"]);
    expect(screen.getAllByText(ASSISTED.result.manual)).toHaveLength(2);
  });

  test("duas com os mesmos pontos continuam empatadas", async () => {
    const { sheet } = await openTieSheet();
    for (const box of within(sheet).getAllByRole("checkbox")) fireEvent.click(box);
    fireEvent.click(within(sheet).getByRole("button", { name: ASSISTED.select.next }));
    for (const index of [1, 2]) {
      await screen.findByText(ASSISTED.ask.progress(index, 2));
      answer(FULL_NO_ACTION);
      next();
    }
    // Duas no modal e duas no cartão do topo, que passa a mostrar a ordem pela avaliação.
    expect(await screen.findAllByText(ASSISTED.result.position(1, true))).toHaveLength(4);
    expect(screen.getByText(ASSISTED.card.orderedBy)).toBeTruthy();
  });

  test("se o navegador não guarda, a avaliação segue e avisa", async () => {
    const { sheet } = await openTieSheet();
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("cheio"); });
    for (const box of within(sheet).getAllByRole("checkbox")) fireEvent.click(box);
    fireEvent.click(within(sheet).getByRole("button", { name: ASSISTED.select.next }));
    await screen.findByText(ASSISTED.ask.progress(1, 2));
    answer(FULL_NO_ACTION);
    next();
    await screen.findByText(ASSISTED.ask.progress(2, 2));
    next();
    expect(await screen.findByText(ASSISTED.unsaved)).toBeTruthy();
    vi.restoreAllMocks();
  });
});

describe("marcar na lista", () => {
  async function openList() {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(tiedPipeline());
    render(<PortfolioPage />);
    await screen.findByText(UI.tieChip(2, "GTX Basic", 550));
    return screen.getAllByRole("checkbox", { name: /para priorizar$/ }) as HTMLElement[];
  }

  test("a barra pede 2, marcar não abre a análise e Priorizar vai direto às perguntas", async () => {
    const boxes = await openList();
    expect(screen.queryByRole("region", { name: ASSISTED.selection.barLabel })).toBeNull();
    fireEvent.click(boxes[0]);
    const bar = screen.getByRole("region", { name: ASSISTED.selection.barLabel });
    expect(within(bar).getByText(ASSISTED.selection.counter(1))).toBeTruthy();
    expect((within(bar).getByRole("button", { name: ASSISTED.selection.action }) as HTMLButtonElement).disabled).toBe(true);
    expect(document.querySelector("[data-state=selected]")).toBeNull();
    fireEvent.click(boxes[1]);
    fireEvent.click(within(bar).getByRole("button", { name: ASSISTED.selection.action }));
    const dialog = await screen.findByRole("dialog", { name: ASSISTED.title });
    expect(within(dialog).getByText(ASSISTED.dialog.step(1, 2))).toBeTruthy();
    expect(within(dialog).queryByText(ASSISTED.select.title)).toBeNull();
  });

  test("Limpar desfaz a escolha", async () => {
    const boxes = await openList();
    fireEvent.click(boxes[0]);
    fireEvent.click(screen.getByRole("button", { name: ASSISTED.selection.clear }));
    expect(screen.queryByRole("region", { name: ASSISTED.selection.barLabel })).toBeNull();
  });
});

describe("remover uma avaliação", () => {
  const stored = () => JSON.parse(window.localStorage.getItem("rankio.avaliacoes.v1") ?? "{}").assessments?.["Ana Alfa"] ?? {};

  async function twoAnswered() {
    const { sheet } = await openTieSheet();
    for (const box of within(sheet).getAllByRole("checkbox")) fireEvent.click(box);
    fireEvent.click(within(sheet).getByRole("button", { name: ASSISTED.select.next }));
    for (const index of [1, 2]) {
      await screen.findByText(ASSISTED.ask.progress(index, 2));
      answer(FULL_NO_ACTION);
      next();
    }
    return screen.findByRole("list", { name: ASSISTED.result.title });
  }

  test("no cartão de resultado: pede confirmação e, ao confirmar, apaga só aquela avaliação", async () => {
    const list = await twoAnswered();
    fireEvent.click(screen.getByRole("button", { name: ASSISTED.remove.label("E050") }));
    expect(await screen.findByText(ASSISTED.remove.title)).toBeTruthy();
    expect(Object.keys(stored()).sort()).toEqual(["E050", "E100"]); // ainda não apagou
    fireEvent.click(screen.getByRole("button", { name: ASSISTED.remove.confirm }));
    await waitFor(() => expect(Object.keys(stored())).toEqual(["E100"]));
    expect([...list.querySelectorAll("[data-opportunity]")].map((el) => el.getAttribute("data-opportunity"))).toEqual(["E100"]);
    expect(screen.getByRole("region", { name: ASSISTED.result.partialTitle })).toBeTruthy();
  });

  test("cancelar mantém as respostas", async () => {
    await twoAnswered();
    fireEvent.click(screen.getByRole("button", { name: ASSISTED.remove.label("E100") }));
    fireEvent.click(await screen.findByRole("button", { name: ASSISTED.remove.cancel }));
    expect(Object.keys(stored()).sort()).toEqual(["E050", "E100"]);
    expect(screen.getByRole("dialog", { name: ASSISTED.title })).toBeTruthy();
  });

  test("no painel \"Por que está aqui\": o selo some da Carteira depois de remover", async () => {
    const first = (load("pipeline-ana-alfa") as SellerPipeline).groups[0].items[0];
    window.localStorage.setItem("rankio.avaliacoes.v1", JSON.stringify({
      assessments: { "Ana Alfa": { [first.opportunity_id]: {
        opportunityId: first.opportunity_id, answers: FULL_NO_ACTION, confirmedConflicts: [],
        assessedAt: "2018-01-02T10:00:00.000Z", policyVersion: "assisted-points-v1", version: 1 } } },
      orders: {},
    }));
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(structuredClone(load("pipeline-ana-alfa")) as SellerPipeline);
    render(<PortfolioPage />);
    fireEvent.click(await screen.findByRole("button", { name: UI.whyHereFor(first.opportunity_id) }));
    const reasons = await screen.findByRole("region", { name: UI.whyHereFor(first.opportunity_id) });
    expect(within(reasons).getByText(ASSISTED.mark.done(CATEGORY_LABELS.define_continuity))).toBeTruthy();
    fireEvent.click(within(reasons).getByRole("button", { name: ASSISTED.remove.label(first.opportunity_id) }));
    fireEvent.click(await screen.findByRole("button", { name: ASSISTED.remove.confirm }));
    await waitFor(() => expect(stored()).toEqual({}));
    expect(screen.queryByText(ASSISTED.mark.done(CATEGORY_LABELS.define_continuity))).toBeNull();
    expect(within(reasons).queryByRole("button", { name: ASSISTED.remove.label(first.opportunity_id) })).toBeNull();
  });
});

describe("respostas que se contradizem", () => {
  test("pede confirmação antes de classificar e deixa o vendedor dizer que está correto", async () => {
    const { sheet } = await openTieSheet();
    for (const box of within(sheet).getAllByRole("checkbox")) fireEvent.click(box);
    fireEvent.click(within(sheet).getByRole("button", { name: ASSISTED.select.next }));
    await screen.findByText(ASSISTED.ask.progress(1, 2));
    answer({ ...FULL_NO_ACTION, interest: "no_contact", need: "investigating", progress: "undated" });
    const alert = await screen.findByRole("alert");
    expect(within(alert).getByText(ASSISTED.conflict.title)).toBeTruthy();
    fireEvent.click(within(alert).getByRole("button", { name: ASSISTED.conflict.keep }));
    await waitFor(() => expect(screen.queryByRole("alert")).toBeNull());
  });
});

describe("avaliar uma oportunidade só", () => {
  test("pelo painel \"Por que está aqui\", sem escolher conjunto", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(structuredClone(load("pipeline-ana-alfa")) as SellerPipeline);
    render(<PortfolioPage />);
    const first = (load("pipeline-ana-alfa") as SellerPipeline).groups[0].items[0];
    fireEvent.click(await screen.findByRole("button", { name: UI.whyHereFor(first.opportunity_id) }));
    const reasons = await screen.findByRole("region", { name: UI.whyHereFor(first.opportunity_id) });
    fireEvent.click(within(reasons).getByRole("button", { name: ASSISTED.single.button }));
    const sheet = await screen.findByRole("dialog", { name: ASSISTED.title });
    expect(within(sheet).queryAllByRole("checkbox")).toHaveLength(0);
    expect(screen.queryByText(ASSISTED.ask.progress(1, 1))).toBeNull();
    answer(FULL_NO_ACTION);
    next();
    expect((await screen.findAllByText(ASSISTED.points(95))).length).toBeGreaterThan(0);
  });
});

describe("seleção de 2 a 5", () => {
  const pool = Array.from({ length: 6 }, (_, i) => ({
    opportunity_id: `P${i}`, product: "GTX Pro", account: null, sales_price: 4821,
  })) as Item[];

  function Harness() {
    const [chosen, setChosen] = useState<string[]>([]);
    return <SelectStep pool={pool} chosen={chosen} onChange={setChosen} onNext={() => {}} assessed={new Set(["P0"])} />;
  }

  test("no máximo 5: a sexta fica travada até desmarcar uma", () => {
    render(<Harness />);
    const boxes = screen.getAllByRole("checkbox");
    boxes.slice(0, 5).forEach((box) => fireEvent.click(box));
    expect((boxes[5] as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByText(new RegExp(escape(ASSISTED.select.full)))).toBeTruthy();
    fireEvent.click(boxes[0]);
    expect((boxes[5] as HTMLButtonElement).disabled).toBe(false);
  });
  test("quem já tem respostas vem identificado", () => {
    render(<Harness />);
    expect(screen.getAllByText(ASSISTED.select.assessed)).toHaveLength(1);
  });
});
