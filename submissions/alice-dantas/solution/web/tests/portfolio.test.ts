// Leitura da ordem da API: por onde começar e o primeiro bloco, sem regra nova no front.
import { describe, expect, test } from "vitest";

import {
  NO_FILTERS, activeFilterCount, defaultTab, filterGroups, filtersToQuery, firstBlock, hasFilters, parseFilters,
  productsIn, startGroup, type ListFilters,
} from "@/lib/portfolio";

import { sellerPipeline, teamPipeline } from "./fixtures";

describe("por onde começar", () => {
  test("Focar com itens: começa por Focar", () => {
    expect(startGroup(sellerPipeline("pipeline-ana-alfa"))?.state).toBe("focar");
  });
  test("Focar vazio: o grupo indicado pelo back em start_with_group", () => {
    const payload = sellerPipeline("pipeline-bruno-beta");
    expect(payload.groups[0].empty?.code).toBe("start_with_group");
    expect(startGroup(payload)?.state).toBe("qualificar");
    expect(defaultTab(payload)).toBe("qualificar");
  });
  test.each([["pipeline-edges-davi-delta", "acompanhar"], ["pipeline-edges-eva-epsilon", "revisar"]])(
    "Focar vazio em %s: começa pelo grupo seguinte com itens (%s)", (name, state) => {
      const payload = sellerPipeline(name);
      expect(startGroup(payload)?.state).toBe(state);
      expect(defaultTab(payload)).toBe(state);
    });
  test("sem abertas: nenhum grupo; a aba inicial é a primeira da ordem", () => {
    const payload = sellerPipeline("pipeline-carla-gama");
    expect(startGroup(payload)).toBeNull();
    expect(defaultTab(payload)).toBe("focar");
    expect(startGroup(teamPipeline("team-empty"))).toBeNull();
  });
});

describe("primeiro bloco", () => {
  test("item sem empate: só ele", () => {
    expect(firstBlock(sellerPipeline("pipeline-ana-alfa").groups[0]).map((i) => i.opportunity_id)).toEqual(["EPP"]);
  });
  test("empate no topo: o bloco inteiro", () => {
    const focar = sellerPipeline("pipeline-ana-alfa").groups[0];
    const tied = { ...focar, items: focar.items.filter((i) => i.tie_size > 1) };
    expect(firstBlock(tied).map((i) => i.opportunity_id)).toEqual(["E050", "E100"]);
  });
  test("sem preço de tabela não há empate", () => {
    const naoPontuavel = sellerPipeline("pipeline-edges-bruno-beta").groups.find((g) => g.state === "nao_pontuavel")!;
    const noPrice = { ...naoPontuavel, items: naoPontuavel.items.filter((i) => i.sales_price === null) };
    expect(firstBlock(noPrice)).toHaveLength(1);
  });
});

describe("busca e filtros da lista", () => {
  const groups = sellerPipeline("pipeline-ana-alfa").groups;
  const ids = (filters: Partial<ListFilters>) =>
    filterGroups(groups, { ...NO_FILTERS, ...filters }).flatMap((g) => g.items.map((i) => i.opportunity_id));
  const all = groups.flatMap((g) => g.items.map((i) => i.opportunity_id));

  test("sem busca nem filtro, os grupos seguem como vieram", () => {
    expect(filterGroups(groups, NO_FILTERS)).toBe(groups);
    expect(hasFilters(NO_FILTERS)).toBe(false);
  });
  test("com cliente e sem cliente repartem a lista, na ordem da API, e atualizam a contagem", () => {
    expect([...ids({ account: "com" }), ...ids({ account: "sem" })].sort()).toEqual([...all].sort());
    expect(ids({ account: "com" })).toEqual(["EGP", "E101", "E139"]);
    expect(filterGroups(groups, { ...NO_FILTERS, account: "com" }).map((g) => g.count)).toEqual([1, 0, 1, 1, 0]);
  });
  test("a busca acha por ID, produto e cliente, sem acento nem maiúscula", () => {
    expect(ids({ q: "e050" })).toEqual(["E050"]);
    expect(ids({ q: "  gtx basic " })).toEqual(["E050", "E100", "E101", "E138", "E139"]);
    expect(ids({ q: "BETA corp" })).toEqual(["EGP", "E101"]);
    expect(ids({ q: "nada disso" })).toEqual([]);
  });
  test("produto, faixa de valor, idade e início da negociação", () => {
    expect(ids({ product: "GTX Pro" })).toEqual(["EGP"]);
    expect(ids({ band: "baixo" })).toEqual(["EMG"]);
    expect(ids({ ageMin: 100, ageMax: 120 })).toEqual(["E100", "E101"]);
    const e050 = groups.flatMap((g) => g.items).find((i) => i.opportunity_id === "E050")!;
    expect(ids({ from: e050.engage_date, to: e050.engage_date })).toEqual(["E050"]);
  });
  test("sem idade ou data, a oportunidade fica de fora quando o filtro de idade ou de data está ativo", () => {
    const withUndated = sellerPipeline("pipeline-edges-bruno-beta").groups;
    const total = withUndated.flatMap((g) => g.items).length;
    const undated = withUndated.flatMap((g) => g.items).filter((i) => i.age_days === null).length;
    expect(undated).toBeGreaterThan(0);
    const aged = filterGroups(withUndated, { ...NO_FILTERS, ageMin: 0 }).flatMap((g) => g.items).length;
    expect(aged).toBe(total - undated);
  });
  test("a URL guarda e recupera a busca e os filtros", () => {
    const filters: ListFilters = {
      q: "beta", account: "com", product: "GTX Pro", band: "alto", ageMin: 10, ageMax: 90, from: "2017-01-02",
      to: "2017-03-04",
    };
    const query = new URLSearchParams(Object.entries(filtersToQuery(filters)).flatMap(([k, v]) => (v ? [[k, v]] : [])));
    expect(parseFilters(query)).toEqual(filters);
    expect(activeFilterCount(filters)).toBe(7);
    expect(filtersToQuery(NO_FILTERS)).toEqual({
      q: null, cliente: null, produto: null, faixa: null, idade_min: null, idade_max: null, de: null, ate: null });
  });
  test("valor inválido na URL é ignorado", () => {
    const bad = new URLSearchParams("cliente=x&faixa=enorme&idade_min=-3&idade_max=abc&de=ontem&ate=2017-13");
    expect(parseFilters(bad)).toEqual(NO_FILTERS);
  });
  test("os produtos do filtro são os que aparecem na lista, em ordem alfabética", () => {
    expect(productsIn(groups)).toEqual(["GTX Basic", "GTX Plus Pro", "GTX Pro", "MG Special"]);
  });
});
