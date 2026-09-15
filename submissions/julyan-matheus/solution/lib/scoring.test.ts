import { describe, expect, it } from "vitest";
import { loadDeals, loadProducts } from "./data";
import {
  MAX_DAYS_OPEN,
  affinity,
  assignTiers,
  buildStats,
  byScoreDesc,
  countBuckets,
  isScored,
  referenceDate,
  scorePipeline,
  triage,
} from "./scoring";
import type { Deal, Product, ScoredDeal } from "./types";

const deals = loadDeals();
const products = loadProducts();
const ref = referenceDate(deals);
const rows = scorePipeline(deals, products);
const scored = rows.filter(isScored);

// Small synthetic fixtures for the rule-level tests.
const P: Product[] = [{ product: "GTX Pro", series: "GTX", sales_price: 4821 }];

function deal(over: Partial<Deal>): Deal {
  return {
    opportunity_id: "X",
    sales_agent: "Ana",
    product: "GTX Pro",
    account: "Acme",
    deal_stage: "Engaging",
    engage_date: "2017-12-01",
    close_date: null,
    close_value: null,
    ...over,
  };
}

describe("scoring — spec §9", () => {
  it("1. score sempre entre 0 e 100", () => {
    expect(scored.length).toBeGreaterThan(0);
    for (const s of scored) {
      expect(s.score).toBeGreaterThanOrEqual(0);
      expect(s.score).toBeLessThanOrEqual(100);
      expect(Number.isInteger(s.score)).toBe(true);
    }
  });

  it("2. score é determinístico", () => {
    const again = scorePipeline(loadDeals(), loadProducts());
    expect(again).toEqual(rows);
  });

  it("3. deal sem conta nunca cai em Focar", () => {
    for (const r of rows) {
      if (!r.deal.account) expect(r.bucket).not.toBe("Focar");
    }
    expect(triage(deal({ account: null }), ref)).toBe("Requalificar");
    expect(triage(deal({ account: null, deal_stage: "Prospecting", engage_date: null }), ref)).toBe("Requalificar");
  });

  it(`4. deal > ${MAX_DAYS_OPEN} dias nunca cai em Focar`, () => {
    for (const r of rows) {
      if (r.daysOpen !== null && r.daysOpen > MAX_DAYS_OPEN) expect(r.bucket).not.toBe("Focar");
    }
    expect(triage(deal({ engage_date: "2017-08-14" }), ref)).toBe("Limpar"); // 139 dias
    expect(triage(deal({ engage_date: "2017-08-15" }), ref)).toBe("Focar"); // 138 dias
  });

  it("5. mudar close_value ou close_date de um deal aberto não altera o score", () => {
    const mutated = deals.map((d) =>
      d.deal_stage === "Engaging" || d.deal_stage === "Prospecting"
        ? { ...d, close_value: 999_999, close_date: "2030-01-01" }
        : d,
    );
    const mutatedRows = scorePipeline(mutated, products);
    expect(referenceDate(mutated)).toBe(ref);
    expect(mutatedRows.filter(isScored).map((s) => [s.deal.opportunity_id, s.score, s.expectedValue])).toEqual(
      scored.map((s) => [s.deal.opportunity_id, s.score, s.expectedValue]),
    );
  });

  it("6. GTXPro e GTX Pro produzem a mesma afinidade", () => {
    const history: Deal[] = [
      deal({ opportunity_id: "a", product: "GTXPro", deal_stage: "Won", close_date: "2017-06-01", close_value: 1 }),
      deal({ opportunity_id: "b", product: "GTX Pro", deal_stage: "Won", close_date: "2017-06-02", close_value: 1 }),
      deal({ opportunity_id: "c", product: "GTXPro", deal_stage: "Lost", close_date: "2017-06-03", close_value: 0 }),
      deal({ opportunity_id: "d", product: "GTX Basic", deal_stage: "Lost", close_date: "2017-06-04", close_value: 0 }),
    ];
    const stats = buildStats(history, P);
    const a = affinity(stats, "Ana", "GTXPro");
    const b = affinity(stats, "Ana", "GTX Pro");
    expect(a).toEqual(b);
    expect(a.comboTotal).toBe(3); // both spellings counted together
    expect(a.comboWins).toBe(2);
  });

  it("7. contagem dos 4 baldes soma 2.089", () => {
    const c = countBuckets(rows);
    expect(c.Focar + c.Requalificar + c.Iniciar + c.Limpar).toBe(2089);
    expect(rows.length).toBe(2089);
  });

  it("8. sanity: balde Focar tem 89 deals na data de referência", () => {
    expect(ref).toBe("2017-12-31");
    expect(countBuckets(rows).Focar).toBe(89);
  });
});

describe("etiqueta relativa (Top / Meio / Fundo do seu Focar)", () => {
  it("terços por posição no ranking do mesmo vendedor; ranking nunca contradiz a etiqueta", () => {
    const byAgent = new Map<string, typeof scored>();
    for (const s of scored) byAgent.set(s.deal.sales_agent, [...(byAgent.get(s.deal.sales_agent) ?? []), s]);
    const order = { Top: 0, Meio: 1, Fundo: 2 };
    let checked = 0;
    for (const list of byAgent.values()) {
      if (list.length < 3) continue; // sem etiqueta, coberto em outro teste
      checked += 1;
      list.sort(byScoreDesc);
      for (let i = 1; i < list.length; i++) {
        expect(order[list[i].tier!]).toBeGreaterThanOrEqual(order[list[i - 1].tier!]);
      }
      const n = list.length;
      expect(list.filter((s) => s.tier === "Top").length).toBe(Math.ceil(n / 3));
    }
    expect(checked).toBeGreaterThan(0);
  });

  it("vendedor com menos de 3 deals no Focar não recebe etiqueta (null)", () => {
    const one: ScoredDeal[] = [{ ...scored[0], tier: "Fundo" }];
    assignTiers(one);
    expect(one[0].tier).toBeNull();

    const two: ScoredDeal[] = [
      { ...scored[0], tier: "Top", deal: { ...scored[0].deal, opportunity_id: "A" } },
      { ...scored[0], tier: "Top", deal: { ...scored[0].deal, opportunity_id: "B" } },
    ];
    assignTiers(two);
    expect(two.map((s) => s.tier)).toEqual([null, null]);
  });

  it("vendedor com exatamente 3 deals recebe Top, Meio e Fundo", () => {
    const three: ScoredDeal[] = [90, 70, 50].map((score, i) => ({
      ...scored[0],
      score,
      tier: null,
      deal: { ...scored[0].deal, opportunity_id: `D${i}` },
    }));
    assignTiers(three);
    expect(three.map((s) => s.tier)).toEqual(["Top", "Meio", "Fundo"]);
  });

  it("etiqueta na base real: só null quando o vendedor tem < 3 no Focar", () => {
    const perAgent = new Map<string, number>();
    for (const s of scored) perAgent.set(s.deal.sales_agent, (perAgent.get(s.deal.sales_agent) ?? 0) + 1);
    for (const s of scored) {
      const n = perAgent.get(s.deal.sales_agent)!;
      if (n < 3) expect(s.tier).toBeNull();
      else expect(s.tier).not.toBeNull();
    }
  });
});

describe("auditoria: janela temporal em buildStats", () => {
  it("deals fechados depois de ref não entram no histórico", () => {
    const history: Deal[] = [
      deal({ opportunity_id: "a", deal_stage: "Won", engage_date: "2017-01-01", close_date: "2017-02-01", close_value: 1 }),
      deal({ opportunity_id: "b", deal_stage: "Lost", engage_date: "2017-01-01", close_date: "2017-02-01", close_value: 0 }),
      deal({ opportunity_id: "c", deal_stage: "Won", engage_date: "2017-01-01", close_date: "2017-09-01", close_value: 1 }),
      deal({ opportunity_id: "d", deal_stage: "Won", engage_date: "2017-01-01", close_date: "2017-09-02", close_value: 1 }),
    ];
    const early = buildStats(history, P, "2017-06-30");
    expect(early.globalWinRate).toBe(0.5); // a + b only
    const late = buildStats(history, P, "2017-12-31");
    expect(late.globalWinRate).toBe(0.75); // all four
  });

  it("carga só conta deals abertos que já existiam em ref", () => {
    const list: Deal[] = [
      deal({ opportunity_id: "h", deal_stage: "Won", engage_date: "2017-01-01", close_date: "2017-02-01", close_value: 1 }),
      deal({ opportunity_id: "e1", deal_stage: "Engaging", engage_date: "2017-05-01" }),
      deal({ opportunity_id: "e2", deal_stage: "Engaging", engage_date: "2017-11-01" }),
      deal({ opportunity_id: "p1", deal_stage: "Prospecting", engage_date: null }),
    ];
    expect(buildStats(list, P, "2017-06-30").loadByAgent.get("Ana")).toBe(2); // e1 + p1
    expect(buildStats(list, P, "2017-12-31").loadByAgent.get("Ana")).toBe(3);
  });

  it("capacity fica em [0, 1]", () => {
    for (const s of scored) {
      expect(s.factors.capacity).toBeGreaterThanOrEqual(0);
      expect(s.factors.capacity).toBeLessThanOrEqual(1);
    }
  });
});
