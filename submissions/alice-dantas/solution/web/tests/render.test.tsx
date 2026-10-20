// Telas: navegação, Carteira e Equipe com respostas sintéticas da API, textos do catálogo e erros de contrato.
import { act, fireEvent, render as renderDom, screen, waitFor, within } from "@testing-library/react";
import type { ReactElement } from "react";
import { describe, expect, test, vi } from "vitest";

import { DataBadge } from "@/components/app/data-badge";
import { MainNav } from "@/components/app/main-nav";
import { MobileNav } from "@/components/app/mobile-nav";
import { EvidencePage } from "@/components/evidence/evidence-page";
import { IntelligencePage } from "@/components/intelligence/intelligence-page";
import { GroupTabs } from "@/components/portfolio/group-tabs";
import { PortfolioPage } from "@/components/portfolio/portfolio-page";
import { RulesPage } from "@/components/rules/rules-page";
import { TeamPage } from "@/components/team/team-page";
import { TooltipProvider } from "@/components/ui/tooltip";
import Home from "@/app/page";
import {
  CONTRACT_ERROR, DIMENSION_LABELS, EVIDENCE, EVIDENCE_TEXT, GROUP_LABELS, INTELLIGENCE, NAV, RANKER_LABELS,
  ROLE_LABELS, RULES, TECH_COLUMNS, TEAM, UI, actionText, bandRange, bandTitle, diagnosticText, groupZeroNote, errorText,
  ageContextText, findingText, groupDescription, groupEmptyText, groupOrderShort, groupRange, groupShort, historyEmptyText, pipelineEmptyText, reasonText,
  sectorLabel, startAction, startReason, startReasonShort, smallSampleNote, suggestionText, suggestionsFor, tieNote, tieText,
} from "@/copy/pt-BR";
import type { Evidence, Intelligence, Rules, SellerPipeline, TeamPipeline } from "@/lib/contract";
import { formatCompact, formatInt, formatPct, formatPp } from "@/lib/format";
import { resetProductSamples } from "@/lib/product-sample";

import { navigation } from "./navigation";
import { errors, intelligence, intelligenceDeals, load, sellerPipeline, teamPipeline } from "./fixtures";

// Os mesmos provedores do layout que os componentes usam.
const render = (ui: ReactElement) => renderDom(ui, { wrapper: TooltipProvider });

type Reply = { status: number; body: unknown };
const ok = (body: unknown): Reply => ({ status: 200, body });

/** API simulada: vendedores e meta sempre respondem; `pipeline` responde às carteiras. */
function stubApi(pipeline: (url: string) => Reply) {
  const fetch = vi.fn(async (url: string) => {
    const reply = url.endsWith("/api/sellers") ? ok(load("sellers")) : url.endsWith("/api/meta") ? ok(load("meta")) : pipeline(url);
    return new Response(JSON.stringify(reply.body), { status: reply.status });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const bySeller = (url: string): Reply => {
  const name = decodeURIComponent(url.split("/api/sellers/")[1].split("/")[0]);
  return ok(load({ "Ana Alfa": "pipeline-ana-alfa", "Bruno Beta": "pipeline-bruno-beta", "Carla Gama": "pipeline-carla-gama" }[name]!));
};

const tab = (label: string) => screen.findByRole("tab", { name: new RegExp(`^${label}`) });

describe("navegação central", () => {
  test("cinco páginas, com a ativa marcada; a Inteligência entre Equipe e Evidência", () => {
    navigation.go("/equipe");
    render(<MainNav />);
    const links = within(screen.getByRole("navigation")).getAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual(Object.values(NAV));
    expect(links.map((link) => link.textContent).slice(1, 4)).toEqual([NAV.equipe, NAV.inteligencia, NAV.evidencia]);
    expect(screen.getByRole("link", { name: NAV.equipe }).getAttribute("aria-current")).toBe("page");
    expect(screen.getByRole("link", { name: NAV.carteira }).getAttribute("aria-current")).toBeNull();
  });

  test("no celular o menu é um botão que abre as cinco páginas, com a ativa marcada", async () => {
    navigation.go("/equipe");
    render(<MobileNav />);
    expect(screen.queryAllByRole("link")).toHaveLength(0);
    fireEvent.keyDown(screen.getByRole("button", { name: UI.menu }), { key: "Enter" });
    const links = await screen.findAllByRole("menuitem");
    expect(links.map((link) => link.textContent)).toEqual(Object.values(NAV));
    expect(links.find((link) => link.textContent === NAV.equipe)?.getAttribute("aria-current")).toBe("page");
  });

  test("a data dos dados que não carrega diz que falta a conexão e deixa tentar de novo", async () => {
    let attempts = 0;
    vi.stubGlobal("fetch", vi.fn(async () => {
      attempts += 1;
      return attempts === 1 ? new Response("{}", { status: 503 }) : new Response(JSON.stringify(load("meta")), { status: 200 });
    }));
    render(<DataBadge />);
    const retry = await screen.findByRole("button", { name: new RegExp(UI.dataUnavailable) });
    expect(retry.textContent).toBe(UI.dataUnavailable);
    fireEvent.click(retry);
    expect(await screen.findByText(/^Dados até /)).toBeTruthy();
  });

  test("a página inicial leva à carteira", () => {
    expect(() => Home()).toThrow("redirect:/carteira");
  });
});

describe("carteira", () => {
  test("escolher o vendedor mostra o próximo passo, as abas e guarda o vendedor na URL", async () => {
    stubApi(bySeller);
    render(<PortfolioPage />);
    const picker = await screen.findByRole("combobox", { name: UI.seller });
    await waitFor(() => expect((picker as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(picker);
    fireEvent.click(await screen.findByRole("option", { name: "Ana Alfa" }));

    expect(navigation.params.get("vendedor")).toBe("Ana Alfa");
    const payload = sellerPipeline("pipeline-ana-alfa");
    expect(await screen.findByText(UI.nextStepTitle)).toBeTruthy();
    expect(screen.getAllByText(actionText(payload.groups[0].next_action!)).length).toBeGreaterThan(0);
    expect((await tab(GROUP_LABELS.focar)).getAttribute("aria-selected")).toBe("true");
    for (const group of payload.groups) expect(await tab(GROUP_LABELS[group.state])).toBeTruthy();
    // Acima da tabela, a faixa curta do grupo (a definição inteira fica em Como funciona).
    expect(screen.getByText(groupShort("focar", payload.meta))).toBeTruthy();
    expect(screen.queryByText(groupDescription("focar", payload.meta))).toBeNull();
    expect(window.localStorage.getItem("rankio.vendedor")).toBe("Ana Alfa");
  });

  test("título com a contagem de abertas ao lado da busca e dos filtros, sem o bloco de textos antes da tabela", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const title = await screen.findByRole("heading", { name: UI.portfolioTitle });
    const row = title.parentElement!.parentElement as HTMLElement;
    expect(within(row).getByLabelText(`${UI.portfolioCount}: 8`).textContent).toBe("8");
    expect(within(row).getByRole("searchbox", { name: UI.listFilters.searchLabel })).toBeTruthy();
    expect(within(row).getByRole("button", { name: new RegExp(`^${UI.listFilters.button}`) })).toBeTruthy();
    for (const gone of [/^Ordem:/, /^Nota:/, /Sem oportunidades em/, /^8 abertas/]) expect(screen.queryByText(gone)).toBeNull();
  });

  test("cada título de faixa de valor leva às faixas em Como funciona; a faixa sem valor não tem o link", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    await screen.findByRole("heading", { name: UI.portfolioTitle });
    const items = sellerPipeline("pipeline-ana-alfa").groups[0].items;
    const links = await screen.findAllByRole("link", { name: UI.bandRangesLink });
    const bands = new Set(items.map((item) => item.value_band).filter(Boolean));
    expect(links).toHaveLength(bands.size);
    for (const link of links) expect(link.getAttribute("href")).toBe("/como-funciona");
  });

  test("o último vendedor volta na próxima visita; Focar vazio abre no grupo indicado", async () => {
    window.localStorage.setItem("rankio.vendedor", "Bruno Beta");
    stubApi(bySeller);
    render(<PortfolioPage />);
    await waitFor(() => expect(navigation.params.get("vendedor")).toBe("Bruno Beta"));
    const focar = sellerPipeline("pipeline-bruno-beta").groups[0];
    expect(focar.empty?.code).toBe("start_with_group");
    expect((await tab(GROUP_LABELS.qualificar)).getAttribute("aria-selected")).toBe("true");
    // O cartão diz por onde começar no título; a ação e o motivo (o mesmo texto de groupEmptyText) vêm embaixo.
    const start = focar.empty as Extract<typeof focar.empty, { code: "start_with_group" }>;
    expect(screen.getByText(UI.startHeadline(GROUP_LABELS.qualificar))).toBeTruthy();
    expect(screen.getByText(startAction(start))).toBeTruthy();
    expect(screen.getByText(startReasonShort(start, focar.state))).toBeTruthy();
    expect(groupEmptyText(start)).toBe(`${startReason(start)} Comece por ${GROUP_LABELS.qualificar}: ` +
      `${startAction(start).charAt(0).toLowerCase()}${startAction(start).slice(1)}`);
  });

  test("a aba fica na URL", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa&grupo=revisar");
    stubApi(bySeller);
    render(<PortfolioPage />);
    expect((await tab(GROUP_LABELS.revisar)).getAttribute("aria-selected")).toBe("true");
  });

  test("vendedor sem oportunidades abertas", async () => {
    navigation.go("/carteira?vendedor=Carla%20Gama");
    stubApi(bySeller);
    render(<PortfolioPage />);
    expect(await screen.findByText(pipelineEmptyText(sellerPipeline("pipeline-carla-gama").empty!))).toBeTruthy();
    expect(screen.queryByRole("tablist")).toBeNull();
  });

  test("o cartão mostra o empate inteiro, sem eleger um ID", async () => {
    const payload = structuredClone(load("pipeline-ana-alfa")) as SellerPipeline;
    const focar = payload.groups[0];
    focar.items = [...focar.items.filter((i) => i.tie_size > 1), ...focar.items.filter((i) => i.tie_size === 1)];
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(() => ok(payload));
    render(<PortfolioPage />);
    // O empate vira um chip (produto e valor uma vez só), e os itens ficam iguais entre si, sem numeração.
    const card = (await screen.findByText(UI.tieChip(2, "GTX Basic", 550))).closest("[data-slot=card]") as HTMLElement;
    expect(within(card).getByRole("button", { name: /^E050/ })).toBeTruthy();
    expect(within(card).getByRole("button", { name: /^E100/ })).toBeTruthy();
    expect(within(card).queryByRole("button", { name: /^EPP/ })).toBeNull();
    expect(within(card).getByRole("button", { name: /^E050/ }).textContent).not.toMatch(/GTX Basic|550/);
    fireEvent.click(within(card).getByRole("button", { name: UI.tieHelpLabel }));
    expect(await screen.findByText(UI.tieHelp)).toBeTruthy();
  });

  test("produto com poucas vendas fechadas: a análise avisa; produto com histórico grande, não", async () => {
    resetProductSamples();
    const [first, second] = sellerPipeline("pipeline-ana-alfa").groups[0].items;
    expect(first.product).not.toBe(second.product);
    const history = structuredClone(load("intelligence-rich")) as Intelligence;
    const segments = history.breakdowns.find((breakdown) => breakdown.dimension === "product")!.segments;
    segments[0] = { ...segments[0], key: first.product!, history: { ...segments[0].history, closed: 25, won: 15 } };
    segments[1] = { ...segments[1], key: second.product!, history: { ...segments[1].history, closed: 500, won: 300 } };
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi((url) => (url.includes("/api/intelligence") ? ok(history) : bySeller(url)));
    render(<PortfolioPage />);

    fireEvent.click(await screen.findByRole("button", { name: UI.whyHereFor(first.opportunity_id) }));
    const panel = await screen.findByRole("region", { name: UI.whyHereFor(first.opportunity_id) });
    expect(await within(panel).findByText(smallSampleNote(first.product!, 25, 15))).toBeTruthy();
    // Só informa: o texto do motivo da posição continua o mesmo.
    for (const reason of first.reasons) expect(within(panel).getByText(reasonText(reason))).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: UI.whyHereFor(second.opportunity_id) }));
    const other = await screen.findByRole("region", { name: UI.whyHereFor(second.opportunity_id) });
    await waitFor(() => expect(within(other).getByText(UI.limitsShort)).toBeTruthy());
    expect(within(other).queryByText(/vendas fechadas do/)).toBeNull();
  });

  test("por que está aqui: a análise abre na própria linha, várias ao mesmo tempo, sem painel lateral", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const [first, second] = sellerPipeline("pipeline-ana-alfa").groups[0].items;
    const open = await screen.findByRole("button", { name: UI.whyHereFor(first.opportunity_id) });
    expect(open.getAttribute("aria-expanded")).toBe("false");
    fireEvent.click(open);

    const panel = await screen.findByRole("region", { name: UI.whyHereFor(first.opportunity_id) });
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(open.getAttribute("aria-expanded")).toBe("true");
    // A análise fica dentro da tabela, logo abaixo da linha da oportunidade.
    const row = open.closest("tr") as HTMLElement;
    expect(row.nextElementSibling?.contains(panel)).toBe(true);
    for (const role of new Set(first.reasons.map((r) => r.role))) expect(within(panel).getByText(ROLE_LABELS[role])).toBeTruthy();
    for (const reason of first.reasons) expect(within(panel).getByText(reasonText(reason))).toBeTruthy();
    expect(within(panel).getByText(actionText(first.next_action))).toBeTruthy();
    expect(first.reasons).toHaveLength(2);  // só o que decidiu: grupo e ordem
    // C4: a linha curta fica visível; o aviso inteiro, fechado em "O que ele não vê" (no DOM).
    expect(within(panel).getByText(UI.limitsShort)).toBeTruthy();
    expect(within(panel).getByRole("button", { name: UI.blindSpotButton })).toBeTruthy();
    expect(within(panel).getByText(UI.limitsNote)).toBeTruthy();

    // A de baixo abre sem fechar a primeira: dá para comparar as duas.
    fireEvent.click(screen.getByRole("button", { name: UI.whyHereFor(second.opportunity_id) }));
    expect(await screen.findByRole("region", { name: UI.whyHereFor(second.opportunity_id) })).toBeTruthy();
    expect(screen.getByRole("region", { name: UI.whyHereFor(first.opportunity_id) })).toBeTruthy();

    // Recolher fecha só a que foi pedida; clicar na linha também alterna.
    fireEvent.click(within(panel).getByRole("button", { name: UI.closeAnalysis }));
    await waitFor(() => expect(screen.queryByRole("region", { name: UI.whyHereFor(first.opportunity_id) })).toBeNull());
    expect(screen.getByRole("region", { name: UI.whyHereFor(second.opportunity_id) })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: UI.whyHereFor(second.opportunity_id) }));
    await waitFor(() => expect(screen.queryByRole("region", { name: UI.whyHereFor(second.opportunity_id) })).toBeNull());
  });

  test("o cartão do topo abre a análise na lista", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const first = sellerPipeline("pipeline-ana-alfa").groups[0].items[0];
    const card = (await screen.findByText(UI.nextStepTitle)).closest("[data-slot=card]") as HTMLElement;
    fireEvent.click(within(card).getByRole("button", { name: new RegExp(`^${first.opportunity_id}`) }));
    expect(await screen.findByRole("region", { name: UI.whyHereFor(first.opportunity_id) })).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  test("o painel traz o contexto histórico da idade, sem contagem nem urgência", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const { groups, meta } = sellerPipeline("pipeline-ana-alfa");
    const item = groups[0].items[0];
    fireEvent.click(await screen.findByRole("button", { name: UI.whyHereFor(item.opportunity_id) }));
    const sheet = await screen.findByRole("region", { name: UI.whyHereFor(item.opportunity_id) });
    expect(within(sheet).getByText(UI.ageContextTitle)).toBeTruthy();
    expect(within(sheet).getByRole("button", { name: UI.ageContextShort })).toBeTruthy();  // C4: fechado em "Ver detalhe"
    expect(within(sheet).getByText(ageContextText(item.age_days!, meta))).toBeTruthy();
    expect(within(sheet).getByText(UI.ageContextNote)).toBeTruthy();
    expect(within(sheet).getByText(UI.nextStep)).toBeTruthy();
    expect(sheet.textContent).not.toMatch(/faltam|restam|dias para/i);
  });

  test("a tabela não traz linha de empate e todos os IDs ficam alinhados; o painel ainda diz que o empate é só pelo código", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const tied = sellerPipeline("pipeline-ana-alfa").groups[0].items.find((i) => i.tie_size > 1)!;
    const buttons = await screen.findAllByRole("button", { name: /^Por que .* está aqui$/ });
    expect(screen.queryByText(/oportunidades empatadas/)).toBeNull();
    const cells = new Set(buttons.map((b) => (b.closest("td") as HTMLElement).className));
    expect(cells.size).toBe(1);
    fireEvent.click(await screen.findByRole("button", { name: UI.whyHereFor(tied.opportunity_id) }));
    const sheet = await screen.findByRole("region", { name: UI.whyHereFor(tied.opportunity_id) });
    expect(within(sheet).getByText(tieNote(tied)!)).toBeTruthy();
    expect(tieNote(sellerPipeline("pipeline-ana-alfa").groups[0].items[0])).toBeNull();
  });

  test("o botão ao lado das abas explica cada grupo, na ordem das abas", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const { groups, meta } = sellerPipeline("pipeline-ana-alfa");
    const limits = { won_cycle_limit_days: meta.won_cycle_limit_days, cycle_limit_days: meta.cycle_limit_days,
      cycle_percentile: meta.cycle_percentile };
    fireEvent.click(await screen.findByRole("button", { name: UI.groupGuide.button }));
    const guide = await screen.findByText(UI.groupGuide.title);
    const box = guide.parentElement as HTMLElement;
    expect(within(box).getAllByRole("term").map((t) => t.textContent)).toEqual(groups.map((g) => GROUP_LABELS[g.state]));
    // A frase curta e o chip do limite (números do meta); a definição inteira fica em Como funciona.
    for (const group of groups) {
      expect(within(box).getByText(groupShort(group.state, limits))).toBeTruthy();
      expect(within(box).getByText(groupRange(group.state, limits))).toBeTruthy();
    }
    // A ordem dentro do grupo fica visível no rodapé, e as regras completas estão a um link.
    expect(within(box).getByText(groupOrderShort(sellerPipeline("pipeline-ana-alfa").ordering))).toBeTruthy();
    expect(within(box).queryByRole("link")).toBeNull();  // sem atalho repetido: as regras têm a própria página
  });

  test("as abas seguem a ordem Focar, Qualificar, Acompanhar, Confirmar, Completar", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const tabs = within(await screen.findByRole("tablist", { name: UI.groupsLabel })).getAllByRole("tab");
    expect(tabs.map((t) => t.textContent!.replace(/\d+$/, ""))).toEqual(
      ["Focar", "Qualificar", "Acompanhar", "Confirmar", "Completar"]);
  });

  test("o painel traz sugestões de negociação por cenário e o aviso novo", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const item = sellerPipeline("pipeline-ana-alfa").groups[0].items[0];  // sem conta registrada
    fireEvent.click(await screen.findByRole("button", { name: UI.whyHereFor(item.opportunity_id) }));
    const sheet = await screen.findByRole("region", { name: UI.whyHereFor(item.opportunity_id) });
    const box = within(sheet).getByRole("region", { name: UI.suggestionsTitle });
    expect(within(box).getByText(UI.suggestionsIntro)).toBeTruthy();
    for (const suggestion of suggestionsFor(item)) expect(within(box).getByText(suggestionText(suggestion))).toBeTruthy();
    expect(within(box).getByText(/^Se a conta não está registrada:/)).toBeTruthy();
    expect(within(sheet).getByText(UI.limitsNote)).toBeTruthy();
    // Com conta registrada, a sugestão da conta ausente não aparece.
    const withAccount = sellerPipeline("pipeline-ana-alfa").groups[0].items[1];
    expect(withAccount.account).not.toBeNull();
    fireEvent.click(screen.getByRole("button", { name: UI.whyHereFor(withAccount.opportunity_id) }));
    const other = await screen.findByRole("region", { name: UI.whyHereFor(withAccount.opportunity_id) });
    expect(within(other).queryByText(/^Se a conta não está registrada:/)).toBeNull();
  });

  test("busca e filtros: a lista, a contagem e a URL; limpar volta tudo", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const ids = async () => (await screen.findAllByRole("button", { name: /^Por que .* está aqui$/ })).map((b) => b.textContent);
    const all = await ids();
    expect(all).toEqual(["EPP", "EGP", "E050", "E100", "EMG"]);

    fireEvent.change(screen.getByRole("searchbox", { name: UI.listFilters.searchLabel }), { target: { value: "beta" } });
    await waitFor(() => expect(navigation.params.get("q")).toBe("beta"));
    expect(await ids()).toEqual(["EGP"]);
    expect(screen.getByRole("status").textContent).toBe(UI.listFilters.result(2, 8));

    fireEvent.click(screen.getByRole("button", { name: UI.listFilters.clear }));
    await waitFor(() => expect(navigation.params.get("q")).toBeNull());
    expect(await ids()).toEqual(all);
  });

  test("filtro de cliente na URL: só as com (ou sem) cliente registrado, sem mudar a ordem nem a classificação", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa&cliente=com");
    stubApi(bySeller);
    render(<PortfolioPage />);
    const ids = async () => (await screen.findAllByRole("button", { name: /^Por que .* está aqui$/ })).map((b) => b.textContent);
    expect(await ids()).toEqual(["EGP"]);
    fireEvent.mouseDown(await tab(GROUP_LABELS.acompanhar));
    await waitFor(async () => expect(await ids()).toEqual(["E101"]));
    navigation.go("/carteira?vendedor=Ana%20Alfa&cliente=sem&grupo=revisar");
    expect(await screen.findByText(UI.listFilters.noneHere)).toBeTruthy();
  });

  test("resposta fora do contrato vira mensagem de erro, não tela quebrada", async () => {
    const body = structuredClone(load("pipeline-ana-alfa")) as any;
    body.groups[0].items[0].reasons[0].code = "alta_chance";
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(() => ok(body));
    render(<PortfolioPage />);
    expect((await screen.findByRole("alert")).textContent).toBe(CONTRACT_ERROR);
  });

  test("erro da API usa o texto do catálogo para o código", async () => {
    navigation.go("/carteira?vendedor=Ana%20Alfa");
    stubApi(() => ({ status: 404, body: (load("errors") as Record<string, unknown>)["404"] }));
    render(<PortfolioPage />);
    expect((await screen.findByRole("alert")).textContent).toBe(errorText(errors()["404"]));
  });
});

describe("equipe", () => {
  test("números, duas análises em abas, filtros na URL e na chamada", async () => {
    const fetch = stubApi(() => ok(load("team-all")));
    navigation.go("/equipe?gerente=Mara%20Um");
    render(<TeamPage />);
    const payload = teamPipeline("team-all");
    const summary = await screen.findByRole("region", { name: UI.teamSummaryLabel });
    // Um cartão com o total e uma legenda por grupo (na ordem da API), cada uma com a contagem da API e sem %.
    expect(within(summary).getByText(formatInt(payload.summary.total))).toBeTruthy();
    const legend = within(summary).getAllByRole("button").filter((b) => Object.values(GROUP_LABELS).some((l) => b.textContent?.startsWith(l)));
    expect(legend.map((b) => b.textContent?.match(/^\D+/)?.[0])).toEqual(payload.ordering.group_order.map((s) => GROUP_LABELS[s]));
    payload.ordering.group_order.forEach((state, i) => expect(legend[i].textContent).toContain(formatInt(payload.summary[state])));
    expect(summary.textContent).not.toMatch(/%/);
    expect(fetch.mock.calls.some(([url]) => String(url).endsWith("/api/pipeline?manager=Mara+Um"))).toBe(true);

    // Abaixo dos números, uma aba por análise, com a contagem; abre em "Por vendedor".
    const views = screen.getByRole("tablist", { name: TEAM.views.label });
    const sellersTab = within(views).getByRole("tab", { name: new RegExp(`^${TEAM.views.sellers}`) });
    const itemsTab = within(views).getByRole("tab", { name: new RegExp(`^${TEAM.views.opportunities}`) });
    expect(sellersTab.getAttribute("aria-selected")).toBe("true");
    expect(sellersTab.textContent).toContain(String(payload.by_seller.length));
    expect(itemsTab.textContent).toContain(String(payload.summary.total));
    // O cartão "Vendedores · com carteira aberta" conta só quem tem oportunidade aberta; a aba lista todos.
    const withOpen = payload.by_seller.filter((seller) => seller.total > 0).length;
    expect(withOpen).toBeLessThan(payload.by_seller.length);
    const stats = screen.getByRole("region", { name: TEAM.stats.label });
    const sellersCard = within(stats).getByText(TEAM.stats.sellers).closest("[data-slot=card]") as HTMLElement;
    expect(sellersCard.textContent).toContain(formatInt(withOpen));
    expect(sellersCard.textContent).toContain(TEAM.stats.sellersHelp);
    expect(screen.queryByRole("tablist", { name: UI.groupsLabel })).toBeNull();
    // As colunas por vendedor seguem a ordem de grupos da API.
    const bySeller = screen.getByText(TEAM.bySellerHelp).closest("[data-slot=card]") as HTMLElement;
    const headers = within(bySeller).getAllByRole("columnheader").map((cell) => cell.textContent ?? "");
    const labels = Object.values(GROUP_LABELS);
    expect(headers.filter((h) => labels.some((l) => h.startsWith(l))).map((h) => labels.find((l) => h.startsWith(l)))).toEqual(
      payload.ordering.group_order.map((state) => GROUP_LABELS[state]));

    // A escolha vai para a URL e só a análise aberta fica na tela (sem rolagem longa).
    fireEvent.mouseDown(itemsTab);
    expect(navigation.params.get("visao")).toBe("oportunidades");
    expect(await screen.findByRole("tablist", { name: UI.groupsLabel })).toBeTruthy();
    expect(screen.getAllByRole("columnheader", { name: UI.columns.seller })).toHaveLength(1);
    // Como na Carteira: sem legenda nem nota de cliente entre as abas e a tabela; só a faixa curta do grupo.
    for (const gone of [/^Ordem:/, /^Nota:/]) expect(screen.queryByText(gone)).toBeNull();

    // Cada grupo da legenda leva à lista já no grupo.
    fireEvent.click(legend[legend.length - 1]);
    expect(navigation.params.get("grupo")).toBe(payload.ordering.group_order[legend.length - 1]);

    fireEvent.click(screen.getByRole("button", { name: UI.filters.clear }));
    expect(navigation.params.get("gerente")).toBeNull();
    await waitFor(() => expect(fetch.mock.calls.some(([url]) => String(url).endsWith("/api/pipeline"))).toBe(true));
  });

  test("Focar em zero diz que o zero é de tempo, não de qualidade; com Focar, a frase não aparece", async () => {
    const payload = load("team-all") as TeamPipeline;
    stubApi(() => ok({ ...payload, summary: { ...payload.summary, focar: 0 } }));
    navigation.go("/equipe");
    const { unmount } = render(<TeamPage />);
    const summary = await screen.findByRole("region", { name: UI.teamSummaryLabel });
    expect(within(summary).getByText(groupZeroNote("focar", 0, payload.meta)!)).toBeTruthy();
    unmount();

    stubApi(() => ok(payload));
    render(<TeamPage />);
    const again = await screen.findByRole("region", { name: UI.teamSummaryLabel });
    expect(within(again).queryByText(groupZeroNote("focar", 0, payload.meta)!)).toBeNull();
  });

  test("Copiar tabela leva todos os vendedores do filtro, separados por tabulação", async () => {
    const writeText = vi.fn(() => Promise.resolve());
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    stubApi(() => ok(load("team-all")));
    navigation.go("/equipe");
    render(<TeamPage />);
    const payload = teamPipeline("team-all");
    fireEvent.click(await screen.findByRole("button", { name: TEAM.copyTable }));
    const text = (writeText.mock.calls[0] as unknown as [string])[0];
    const lines = text.split("\n");
    expect(lines).toHaveLength(payload.by_seller.length + 1);
    expect(lines[0].split("\t")).toEqual([UI.columns.seller, TEAM.total,
      ...payload.ordering.group_order.map((state) => GROUP_LABELS[state]), TEAM.withoutAccount]);
    expect(lines[1].split("\t")[0]).toBe(payload.by_seller[0].seller);
    expect(await screen.findByText(TEAM.tableCopied)).toBeTruthy();
  });

  test("filtro sem oportunidades", async () => {
    stubApi(() => ok(load("team-empty")));
    navigation.go("/equipe?gerente=Ninguem&visao=oportunidades");
    render(<TeamPage />);
    expect(await screen.findByText(pipelineEmptyText(teamPipeline("team-empty").empty!))).toBeTruthy();
  });

  test("tabela paginada, na ordem da API, sem rolagem infinita", () => {
    const { groups, meta } = sellerPipeline("pipeline-ana-alfa");
    const ids = () => screen.getAllByRole("button", { name: /^Por que .* está aqui$/ })
      .map((button) => button.textContent);
    const view = (reveal: { id: string } | null) => (
      <GroupTabs groups={groups} tab="focar" onTab={() => {}} expanded={[]} onToggle={() => {}}
                 renderPanel={() => null} reveal={reveal} limits={meta} pageSize={2} />);
    const { rerender } = render(view(null));
    const all = groups[0].items.map((item) => item.opportunity_id);
    expect(ids()).toEqual(all.slice(0, 2));
    expect(screen.getByText(UI.pagination.range(1, 2, 5))).toBeTruthy();
    act(() => fireEvent.click(screen.getByRole("link", { name: UI.pagination.page(3) })));
    expect(ids()).toEqual(all.slice(4));
    expect(screen.getByText(UI.pagination.range(5, 5, 5))).toBeTruthy();
    expect(screen.getByRole("link", { name: UI.pagination.next }).getAttribute("aria-disabled")).toBe("true");
    act(() => fireEvent.click(screen.getByRole("link", { name: UI.pagination.previous })));
    expect(ids()).toEqual(all.slice(2, 4));
    // Abrir uma oportunidade de fora da lista (o cartão do topo) pode passar da página: a tabela vai até ela.
    rerender(<TooltipProvider>{view({ id: all[0] })}</TooltipProvider>);
    expect(ids()).toEqual(all.slice(0, 2));
  });
});

describe("equipe por vendedor", () => {
  test("todo vendedor do filtro, na ordem da API, com link para a carteira; as colunas ordenam e voltam", async () => {
    stubApi(() => ok(load("team-all")));
    navigation.go("/equipe");
    render(<TeamPage />);
    const table = (await screen.findByText(TEAM.bySellerHelp)).closest("[data-slot=card]") as HTMLElement;
    const rows = (load("team-all") as TeamPipeline).by_seller;
    const names = () => within(table).getAllByRole("link").map((link) => link.textContent);
    expect(names()).toEqual(rows.map((row) => row.seller));
    expect(within(table).getAllByRole("link")[0].getAttribute("href")).toBe(`/carteira?vendedor=${encodeURIComponent(rows[0].seller)}`);
    expect(screen.getByRole("link", { name: TEAM.seeEvidence }).getAttribute("href")).toBe("/evidencia");

    // Cada coluna é um botão que ordena: crescente, decrescente e, no terceiro clique, a ordem da API.
    const head = within(table).getByRole("columnheader", { name: new RegExp(`^${TEAM.total}`) });
    expect(head.getAttribute("aria-sort")).toBe("none");
    const byTotal = (dir: 1 | -1) => [...rows].sort((a, b) => (a.total - b.total) * dir).map((row) => row.total);
    const totals = () => within(table).getAllByRole("row").slice(1).map((row) => Number(row.querySelectorAll("td")[1].textContent!.replace(/\D/g, "")));
    fireEvent.click(within(head).getByRole("button"));
    expect(head.getAttribute("aria-sort")).toBe("ascending");
    expect(totals()).toEqual(byTotal(1).slice(0, totals().length));
    fireEvent.click(within(head).getByRole("button"));
    expect(head.getAttribute("aria-sort")).toBe("descending");
    expect(totals()).toEqual(byTotal(-1).slice(0, totals().length));
    fireEvent.click(within(head).getByRole("button"));
    expect(head.getAttribute("aria-sort")).toBe("none");
    expect(names()).toEqual(rows.map((row) => row.seller).slice(0, names().length));
  });

  test("filtro sem vendedores: a aba mostra a mensagem, sem tabela vazia", async () => {
    stubApi(() => ok(load("team-empty")));
    navigation.go("/equipe?gerente=Ninguem");
    render(<TeamPage />);
    expect(await screen.findByText(TEAM.noSellers)).toBeTruthy();
    expect(screen.queryByText(TEAM.bySellerHelp)).toBeNull();
  });

  test("escritório com vendedor sem abertas: ele aparece com zeros; a lista de oportunidades fica vazia", async () => {
    stubApi(() => ok(load("team-east")));
    navigation.go("/equipe?escritorio=East");
    render(<TeamPage />);
    const table = (await screen.findByText(TEAM.bySellerHelp)).closest("[data-slot=card]") as HTMLElement;
    expect(within(table).getAllByRole("link").map((link) => link.textContent)).toEqual(["Carla Gama"]);
  });
});

describe("evidência", () => {
  const evidence = () => load("evidence") as Evidence;

  test("linguagem de negócio (padrão): a pergunta, cada estratégia com rótulo e números do payload", async () => {
    stubApi(() => ok(load("evidence")));
    navigation.go("/evidencia");
    render(<EvidencePage />);
    const { design, rankers } = evidence();
    const text = EVIDENCE_TEXT.negocio;
    expect(await screen.findByText(text.question(design.top_k, design.horizon_days))).toBeTruthy();
    const detail = screen.getByText(text.detailTitle).closest("[data-slot=card]") as HTMLElement;
    for (const ranker of rankers) {
      const row = within(detail).getByText(RANKER_LABELS[ranker.code]).closest("tr") as HTMLElement;
      expect(within(row).getByText(formatPct(ranker.val_at_k))).toBeTruthy();
      if (ranker.delta_val) {
        // A frase inteira fica para o leitor de tela; na tela, a diferença curta e a faixa.
        expect(within(row).getByText(text.delta(ranker.delta_val)).className).toContain("sr-only");
        expect(within(row).getByText(text.deltaShort(ranker.delta_val))).toBeTruthy();
        expect(within(row).getByText(text.deltaRange(ranker.delta_val))).toBeTruthy();
      }
    }
    // Sem jargão: nenhuma coluna técnica, nenhum "pp" nem "IC95%".
    expect(within(detail).queryByText(TECH_COLUMNS.auc)).toBeNull();
    expect(detail.textContent).not.toMatch(/\bpp\b|IC95%|AUC|Val@/);
    expect(document.body.textContent).not.toMatch(/vazamento|leak/i);
    // A fixture sintética não vem dos CSVs auditados: o aviso aparece.
    expect(design.audited_data).toBe(false);
    expect(screen.getByText(EVIDENCE.notAudited)).toBeTruthy();
    // A limitação principal: o veredito do back, dito em linguagem de negócio.
    expect(screen.getByText(text.verdict(evidence().without_no_outcome_verdict))).toBeTruthy();
  });

  test("linguagem técnica: métricas completas, com a escolha na URL", async () => {
    stubApi(() => ok(load("evidence")));
    navigation.go("/evidencia?linguagem=tecnica");
    render(<EvidencePage />);
    const { design, rankers } = evidence();
    const text = EVIDENCE_TEXT.tecnica;
    expect(await screen.findByText(text.question(design.top_k, design.horizon_days))).toBeTruthy();
    const detail = screen.getByText(text.detailTitle).closest("[data-slot=card]") as HTMLElement;
    for (const header of [TECH_COLUMNS.auc, TECH_COLUMNS.hits(design.top_k), TECH_COLUMNS.lift(design.top_k)]) {
      expect(within(detail).getByRole("columnheader", { name: header })).toBeTruthy();
    }
    for (const ranker of rankers) {
      const row = within(detail).getByText(RANKER_LABELS[ranker.code]).closest("tr") as HTMLElement;
      expect(within(row).getByText(formatPct(ranker.p_at_k))).toBeTruthy();
      if (ranker.delta_val) expect(within(row).getByText(formatPp(ranker.delta_val.value))).toBeTruthy();
    }
    expect(screen.getByRole("combobox", { name: EVIDENCE.languageLabel }).textContent).toBe("Linguagem técnica");
  });

  test("sem o resultado do backtest, a mensagem do catálogo", async () => {
    const body = { detail: "x", code: "evidence_unavailable" as const, params: { file: "backtest_results.json" } };
    stubApi(() => ({ status: 503, body }));
    render(<EvidencePage />);
    expect((await screen.findByRole("alert")).textContent).toBe(errorText(body));
  });
});

describe("como funciona", () => {
  test("grupos, faixas e os dois limites vindos de /api/rules", async () => {
    stubApi(() => ok(load("rules")));
    render(<RulesPage />);
    const rules = load("rules") as Rules;
    for (const state of rules.ordering.group_order) {
      expect(await screen.findByText(groupShort(state, rules.meta))).toBeTruthy();
    }
    for (const band of rules.value_bands) {
      const row = screen.getByText(bandTitle(band.band)).closest("tr") as HTMLElement;
      expect(within(row).getByText(bandRange(band))).toBeTruthy();
    }
    expect(screen.getByText(RULES.wonLimit(rules.meta.won_cycle_limit_days, rules.meta.cycle_percentile))).toBeTruthy();
    expect(screen.getByText(RULES.longestLimit(rules.meta.cycle_limit_days))).toBeTruthy();
  });
});

describe("inteligência", () => {
  /** API simulada: a página responde com `page`; o detalhamento, com as ganhas da Ana Alfa. */
  const intelApi = (page = "intelligence-rich") => stubApi((url) =>
    url.includes("/api/intelligence/deals") ? ok(load("intelligence-deals-won")) : ok(load(page)));
  const called = (fetch: ReturnType<typeof stubApi>, suffix: string) =>
    fetch.mock.calls.some(([url]) => String(url).endsWith(suffix));
  /** Abre "Ver análises" (o rótulo traz a contagem) e devolve o painel. */
  const openAnalyses = async (count: number) => {
    const name = new RegExp(`^${INTELLIGENCE.analyses.button}\\s*${count}$`);
    fireEvent.click(await screen.findByRole("button", { name }));
    return screen.findByRole("dialog", { name: INTELLIGENCE.analyses.title });
  };

  test("números, diagnósticos e descobertas vêm do payload; a carteira aberta fica à parte", async () => {
    const fetch = intelApi();
    navigation.go("/inteligencia");
    render(<IntelligencePage />);
    const payload = intelligence("intelligence-rich");
    // O Intl põe um espaço fixo antes de "mil"/"mi"; a busca por texto normaliza os espaços.
    expect((await screen.findAllByText(formatCompact(payload.history.revenue).replace(/\s/g, " "))).length)
      .toBeGreaterThan(0);
    expect(called(fetch, "/api/intelligence")).toBe(true);
    const open = screen.getByRole("region", { name: INTELLIGENCE.open.title });
    expect(open.textContent).toContain(INTELLIGENCE.open.notRevenue);
    expect(within(open).getAllByRole("listitem").map((li) => li.textContent?.split(" ")[0])).toEqual(
      payload.ordering.group_order.map((state) => GROUP_LABELS[state]));
    // No corpo, só números: diagnósticos e descobertas ficam no painel "Ver análises".
    expect(screen.queryByText(diagnosticText(payload.diagnostics[0]).title)).toBeNull();
    const panel = await openAnalyses(payload.diagnostics.length + payload.findings.length);
    for (const d of payload.diagnostics) expect(within(panel).getByText(diagnosticText(d).title)).toBeTruthy();
    expect(within(panel).getByText(INTELLIGENCE.process.crmTitle)).toBeTruthy();
    fireEvent.mouseDown(within(panel).getByRole("tab", { name: new RegExp(`^${INTELLIGENCE.analyses.findings}`) }));
    for (const f of payload.findings) expect(within(panel).getAllByText(findingText(f).title).length).toBeGreaterThan(0);
    // Sem jargão estatístico e sem promessa de chance na página.
    expect(document.body.textContent).not.toMatch(/IC95%|qui-quadrado|Bonferroni|Wilson|probabilidade/i);
  });

  test("filtros vão para a URL e para a chamada; limpar tira todos", async () => {
    const fetch = intelApi("intelligence-sector");
    navigation.go("/inteligencia?escritorio=East&setor=retail");
    render(<IntelligencePage />);
    await screen.findByText(INTELLIGENCE.open.notRevenue, { exact: false });
    expect(called(fetch, "/api/intelligence?office=East&sector=retail")).toBe(true);
    const excluded = intelligence("intelligence-sector").open.excluded_without_account!;
    expect(screen.getByText(INTELLIGENCE.open.excluded(excluded))).toBeTruthy();
    // O recorte ativo fica à vista, um chip por filtro, e o botão mostra quantos são.
    const chips = screen.getByRole("group", { name: INTELLIGENCE.filters.activeLabel });
    expect(within(chips).getByText(INTELLIGENCE.filters.chip(DIMENSION_LABELS.office, "Leste"))).toBeTruthy();
    expect(screen.getByRole("button", { name: new RegExp(`^${INTELLIGENCE.filters.button}\\s*2$`) })).toBeTruthy();
    fireEvent.click(within(chips).getByRole("button", {
      name: INTELLIGENCE.filters.remove(DIMENSION_LABELS.sector, "Varejo") }));
    expect(navigation.params.get("setor")).toBeNull();
    expect(navigation.params.get("escritorio")).toBe("East");
    fireEvent.click(within(chips).getByRole("button", { name: UI.filters.clear }));
    expect(navigation.params.get("escritorio")).toBeNull();
    expect(navigation.params.get("setor")).toBeNull();
  });

  test("filtrar por uma linha muda a página inteira (URL), sem perder os outros filtros", async () => {
    intelApi();
    navigation.go("/inteligencia?gerente=Mara%20Um");
    render(<IntelligencePage />);
    const filterButton = await screen.findByRole("button", { name: INTELLIGENCE.explore.filterBy("Alfa Pro") });
    // O ícone sozinho não se explica: o tooltip diz o que a ação faz.
    fireEvent.focus(filterButton);
    expect((await screen.findByRole("tooltip")).textContent).toBe(INTELLIGENCE.explore.filterBy("Alfa Pro"));
    fireEvent.click(filterButton);
    expect(navigation.params.get("produto")).toBe("Alfa Pro");
    expect(navigation.params.get("gerente")).toBe("Mara Um");
  });

  test("pessoas: ordem da API (alfabética), sem gráfico e sem escolha de métrica", async () => {
    intelApi();
    navigation.go("/inteligencia?ver=seller");
    render(<IntelligencePage />);
    expect(await screen.findByText(INTELLIGENCE.explore.peopleNote, { exact: false })).toBeTruthy();
    expect(screen.queryByRole("combobox", { name: INTELLIGENCE.explore.metric })).toBeNull();
    const card = screen.getAllByText(DIMENSION_LABELS.seller).map((el) => el.closest("[data-slot=card]"))
      .find((el) => el?.querySelector("table")) as HTMLElement;
    const sellers = intelligence("intelligence-rich").breakdowns.find((b) => b.dimension === "seller")!.segments;
    const names = within(card).getAllByRole("row").slice(1).map((row) => row.querySelector("td")?.textContent);
    expect(names).toEqual(sellers.map((s) => s.key));
    expect(names).toEqual([...names].sort());
  });

  test("a tabela mostra ganhas e perdidas ao lado das fechadas, e o setor aparece em português", async () => {
    intelApi();
    navigation.go("/inteligencia?ver=sector");
    render(<IntelligencePage />);
    const sectors = intelligence("intelligence-rich").breakdowns.find((b) => b.dimension === "sector")!.segments;
    const card = (await screen.findAllByText(DIMENSION_LABELS.sector)).map((el) => el.closest("[data-slot=card]"))
      .find((el) => el?.querySelector("table")) as HTMLElement;
    const headers = within(card).getAllByRole("columnheader").map((h) => h.textContent ?? "");
    const closed = headers.findIndex((h) => h.startsWith(INTELLIGENCE.explore.columns.closed));
    expect(headers[closed + 1]).toMatch(new RegExp(`^${INTELLIGENCE.explore.columns.won}`));
    expect(headers[closed + 2]).toMatch(new RegExp(`^${INTELLIGENCE.explore.columns.lost}`));
    const first = sectors.find((s) => s.key !== null)!;
    const row = within(card).getAllByRole("row")[1];
    const cells = within(row).getAllByRole("cell").map((c) => c.textContent);
    expect(cells[0]).toBe(sectorLabel(first.key!));
    expect(cells[closed]).toBe(formatInt(first.history.closed));
    expect(cells[closed + 1]).toBe(formatInt(first.history.won));
    expect(cells[closed + 2]).toBe(formatInt(first.history.lost));
  });

  test("cruzamentos: o seletor traz os seis e cada um mantém a soma da linha", async () => {
    intelApi();
    navigation.go("/inteligencia");
    render(<IntelligencePage />);
    const picker = await screen.findByRole("combobox", { name: INTELLIGENCE.crosstab.viewBy });
    expect(picker.textContent).toBe(INTELLIGENCE.crosstab.tables.seller_product.option);
    fireEvent.keyDown(picker, { key: "ArrowDown" });
    const options = (await screen.findAllByRole("option")).map((option) => option.textContent);
    expect(options).toEqual(Object.values(INTELLIGENCE.crosstab.tables).map((table) => table.option));
    fireEvent.click(screen.getByRole("option", { name: INTELLIGENCE.crosstab.tables.sector_product.option }));
    await waitFor(() => expect(document.getElementById("cruzamento")?.textContent)
      .toBe(INTELLIGENCE.crosstab.tables.sector_product.title));
    const table = document.getElementById("cruzamento")!.closest("[data-slot=card]") as HTMLElement;
    const crosstab = intelligence("intelligence-rich").crosstabs.find((c) => c.id === "sector_product")!;
    const row = crosstab.rows[0];
    const cells = within(within(table).getAllByRole("row")[1]).getAllByRole("cell").map((c) => c.textContent);
    expect(cells[0]).toBe(sectorLabel(row.key));
    expect(cells[cells.length - 1]).toBe(formatInt(row.closed));
  });

  test("detalhamento: a linha abre as negociações com o recorte somado, e o diagnóstico abre o grupo", async () => {
    const fetch = intelApi();
    navigation.go("/inteligencia?escritorio=Central");
    render(<IntelligencePage />);
    fireEvent.click(await screen.findByRole("button", { name: INTELLIGENCE.explore.dealsOf("Alfa Pro") }));
    await waitFor(() => expect(called(fetch, "/api/intelligence/deals?product=Alfa+Pro&office=Central&outcome=won"))
      .toBe(true));
    const sheet = await screen.findByRole("dialog");
    const deals = intelligenceDeals("intelligence-deals-won");
    expect(within(sheet).getByText(INTELLIGENCE.deals.total(deals.total))).toBeTruthy();
    expect(within(sheet).getByText(INTELLIGENCE.deals.scope([
      INTELLIGENCE.deals.filterPart(DIMENSION_LABELS.product, "Alfa Pro"),
      INTELLIGENCE.deals.filterPart(DIMENSION_LABELS.office, "Central")]))).toBeTruthy();
    fireEvent.click(within(sheet).getByRole("button", { name: UI.closePanel }));

    const rich = intelligence("intelligence-rich");
    const panel = await openAnalyses(rich.diagnostics.length + rich.findings.length);
    const beyond = rich.diagnostics.find((d) => d.code === "engaging_beyond_longest_cycle")!;
    const card = within(panel).getByText(diagnosticText(beyond).title).closest("[data-slot=card]") as HTMLElement;
    // Só gerente e escritório no recorte: o atalho para a Equipe leva ao mesmo grupo.
    expect(within(card).getByRole("link", { name: INTELLIGENCE.process.seeTeam }).getAttribute("href")).toBe(
      "/equipe?visao=oportunidades&grupo=revisar&escritorio=Central");
    fireEvent.click(within(card).getByRole("button", { name: INTELLIGENCE.process.seeDeals }));
    await waitFor(() => expect(called(fetch, "/api/intelligence/deals?office=Central&outcome=open&group=revisar"))
      .toBe(true));
  });

  test("o botão Filtros abre os sete filtros num painel", async () => {
    intelApi();
    navigation.go("/inteligencia");
    render(<IntelligencePage />);
    await screen.findByText(INTELLIGENCE.open.notRevenue, { exact: false });
    // Os filtros não ficam encadeados no corpo da página.
    expect(screen.queryByRole("combobox", { name: DIMENSION_LABELS.product })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: INTELLIGENCE.filters.button }));
    const popover = await screen.findByRole("dialog", { name: INTELLIGENCE.filtersLabel });
    expect(within(popover).getAllByRole("combobox").map((box) => box.getAttribute("aria-label"))).toEqual(
      ["product", "seller", "manager", "office", "sector", "account", "size"].map(
        (key) => DIMENSION_LABELS[key as keyof typeof DIMENSION_LABELS]));
  });

  test("Como funciona abre as definições num painel", async () => {
    intelApi();
    navigation.go("/inteligencia");
    render(<IntelligencePage />);
    fireEvent.click(await screen.findByRole("button", { name: INTELLIGENCE.guide.button }));
    const guide = await screen.findByRole("dialog", { name: INTELLIGENCE.guide.title });
    for (const line of [...INTELLIGENCE.reading.definitions, ...INTELLIGENCE.reading.limits]) {
      expect(within(guide).getByText(line)).toBeTruthy();
    }
  });

  test("recorte sem fechadas", async () => {
    intelApi("intelligence-empty");
    navigation.go("/inteligencia?cliente=Ninguem");
    render(<IntelligencePage />);
    expect(await screen.findByText(historyEmptyText(intelligence("intelligence-empty").history_empty!))).toBeTruthy();
  });

  test("resposta fora do contrato", async () => {
    stubApi(() => ok({ meta: {} }));
    navigation.go("/inteligencia");
    render(<IntelligencePage />);
    expect((await screen.findByRole("alert")).textContent).toBe(CONTRACT_ERROR);
  });
});
