import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { normalizeProduct, normalizeSector } from "./normalization.js";
import { calculateScore, createScoringContext } from "./scoring.js";
import { scoreOpportunities } from "./scoring-service.js";
import type { DealStage, ScoringOpportunity } from "./types.js";

interface OpportunityInput {
  id: string;
  stage?: DealStage;
  product?: string;
  series?: string | null;
  accountId?: number | null;
  accountName?: string | null;
  sector?: string | null;
  employees?: number | null;
  revenue?: number | null;
  closeDate?: string | null;
}

function opportunity(input: OpportunityInput): ScoringOpportunity {
  const stage = input.stage ?? "Won";
  return {
    id: input.id,
    dealStage: stage,
    productId: 1,
    product: input.product ?? "GTX Pro",
    series: input.series === undefined ? "GTX" : input.series,
    salesPrice: null,
    accountId: input.accountId === undefined ? 1 : input.accountId,
    accountName: input.accountName === undefined ? "Cliente A" : input.accountName,
    sector: input.sector === undefined ? "technology" : input.sector,
    employees: input.employees === undefined ? 100 : input.employees,
    revenue: input.revenue === undefined ? 100 : input.revenue,
    salesAgentId: 1,
    salesAgent: "Vendedor",
    manager: null,
    regionalOffice: null,
    engageDate: null,
    closeDate: input.closeDate === undefined ? "2017-01-01" : input.closeDate,
    closeValue: 100,
  };
}

function score(target: ScoringOpportunity, history: ScoringOpportunity[], referenceDate = "2018-01-01") {
  return calculateScore(target, history, referenceDate, "2018-01-02T00:00:00.000Z", createScoringContext(history));
}

function factorPoints(result: ReturnType<typeof score>, id: string): number {
  const factor = result.factors.find((candidate) => candidate.id === id);
  assert.ok(factor);
  return factor.points;
}

describe("Scoring Engine", () => {
  it("returns zero when no evidence exists", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [target]);

    assert.equal(result.score, 0);
    assert.equal(result.rawScore, 0);
    assert.deepEqual(result.factors.map((factor) => factor.points), [0, 0, 0, 0]);
    assert.match(result.justification, /não sustentam pontos/iu);
  });

  it("starts from zero without a baseline", () => {
    const result = score(opportunity({ id: "TARGET" }), [opportunity({ id: "TARGET" })]);
    assert.equal(result.score, 0);
  });

  it("applies confidence to a single exact win", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [target, opportunity({ id: "W1" })]);

    assert.equal(factorPoints(result, "account_product_fit"), 35 * 0.7 * 0.25);
    assert.equal(result.score, Math.round(result.rawScore));
  });

  it("increases confidence with a larger equivalent win rate", () => {
    const target = opportunity({ id: "TARGET" });
    const oneWin = [target, opportunity({ id: "W1" })];
    const tenWins = Array.from({ length: 10 }, (_, index) => opportunity({ id: `W${index}` }));
    const small = score(target, oneWin);
    const large = score(target, [target, ...tenWins]);

    assert.ok(factorPoints(large, "account_product_fit") > factorPoints(small, "account_product_fit"));
  });

  it("combines exact and series evidence without double counting", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [
      target,
      opportunity({ id: "EXACT-WIN" }),
      opportunity({ id: "SERIES-WIN", product: "GTX Basic" }),
      opportunity({ id: "SERIES-LOSS", product: "GTX Basic", stage: "Lost" }),
    ]);

    const expected = 35 * (0.7 * (1 / 4) + 0.3 * (1 / 7));
    assert.equal(factorPoints(result, "account_product_fit"), expected);
  });

  it("calculates product and sector evidence", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [
      target,
      opportunity({ id: "S1" }),
      opportunity({ id: "S2" }),
      opportunity({ id: "S3" }),
      opportunity({ id: "S4", stage: "Lost" }),
    ]);

    assert.equal(factorPoints(result, "sector_product_fit"), 30 * (3 / 14));
  });

  it("calculates employee and revenue profile independently", () => {
    const target = opportunity({ id: "TARGET", employees: 150, revenue: 150 });
    const buyers = [
      opportunity({ id: "B1", accountId: 2, accountName: "B", employees: 100, revenue: null }),
      opportunity({ id: "B2", accountId: 3, accountName: "C", employees: 200, revenue: null }),
    ];
    const result = score(target, [target, ...buyers]);

    assert.equal(factorPoints(result, "company_profile_fit"), 10);
    assert.match(result.factors.find((factor) => factor.id === "company_profile_fit")?.reason ?? "", /sem histórico válido de receita/iu);
  });

  it("calculates financial compatibility from four distinct buyers", () => {
    const target = opportunity({ id: "TARGET", revenue: 25 });
    const buyers = [10, 20, 30, 40].map((revenue, index) => opportunity({
      id: `B${index}`,
      accountId: index + 2,
      accountName: `Buyer ${index}`,
      revenue,
    }));
    const result = score(target, [target, ...buyers]);

    assert.equal(factorPoints(result, "financial_fit"), 15);
    assert.equal(result.factors.find((factor) => factor.id === "financial_fit")?.evidence.sampleSize, 4);
  });

  it("treats missing information as zero without failure", () => {
    const target = opportunity({
      id: "TARGET",
      accountId: null,
      accountName: null,
      sector: null,
      employees: null,
      revenue: null,
    });
    const result = score(target, [target]);

    assert.equal(result.score, 0);
    assert.equal(result.factors.length, 4);
  });

  it("excludes the evaluated opportunity from its own history", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [target]);

    assert.equal(result.factors[0]?.evidence.exactTotal, 0);
  });

  it("uses only Won and Lost evidence", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [
      target,
      opportunity({ id: "OPEN", stage: "Prospecting", closeDate: null }),
      opportunity({ id: "ENGAGING", stage: "Engaging", closeDate: null }),
    ]);

    assert.equal(result.factors[1]?.evidence.sampleSize, 0);
  });

  it("excludes closed opportunities outside the reference date", () => {
    const target = opportunity({ id: "TARGET" });
    const future = opportunity({ id: "FUTURE", closeDate: "2018-06-01" });
    const result = score(target, [target, future], "2018-01-01");

    assert.equal(result.factors[1]?.evidence.sampleSize, 0);
  });

  it("normalizes known product and sector aliases", () => {
    assert.equal(normalizeProduct(" GTXPro "), "GTX Pro");
    assert.equal(normalizeSector("technolgy"), "technology");
    assert.equal(normalizeProduct(""), null);
  });

  it("never exceeds 100", () => {
    const target = opportunity({ id: "TARGET", employees: 100, revenue: 100 });
    const history = Array.from({ length: 100 }, (_, index) => opportunity({
      id: `H${index}`,
      accountId: index + 2,
      accountName: `Buyer ${index}`,
      employees: 100,
      revenue: 100,
    }));
    const result = score(target, [target, ...history]);

    assert.ok(result.rawScore <= 100);
    assert.ok(result.score <= 100);
  });

  it("is deterministic for the same input", () => {
    const target = opportunity({ id: "TARGET" });
    const history = [target, opportunity({ id: "W1" }), opportunity({ id: "L1", stage: "Lost" })];
    assert.deepEqual(score(target, history), score(target, history));
  });

  it("generates deterministic explanations and factor evidence", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [target, opportunity({ id: "W1" })]);
    const accountFactor = result.factors.find((factor) => factor.id === "account_product_fit");

    assert.ok(accountFactor?.reason);
    assert.equal(accountFactor?.evidence.exactWon, 1);
    assert.match(result.justification, /probabilidade/iu);
  });

  it("preserves the exact sum of factor contributions", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [target, opportunity({ id: "W1" }), opportunity({ id: "L1", stage: "Lost" })]);
    const total = result.factors.reduce((sum, factor) => sum + factor.points, 0);

    assert.equal(result.rawScore, total);
    assert.equal(result.score, Math.round(result.rawScore));
  });

  it("excludes the evaluated opportunity from every historical factor", () => {
    const target = opportunity({ id: "TARGET" });
    const result = score(target, [target]);

    assert.equal(result.factors.find((factor) => factor.id === "account_product_fit")?.evidence.exactTotal, 0);
    assert.equal(result.factors.find((factor) => factor.id === "sector_product_fit")?.evidence.sampleSize, 0);
    assert.equal(result.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.medianEmployees, null);
    assert.equal(result.factors.find((factor) => factor.id === "financial_fit")?.evidence.sampleSize, 0);
  });

  it("uses the close date as the default historical reference for closed opportunities", () => {
    const target = opportunity({ id: "TARGET", closeDate: "2017-06-01" });
    const future = opportunity({ id: "FUTURE", accountId: 2, accountName: "Cliente B", closeDate: "2017-12-01" });
    const result = scoreOpportunities([target, future], "2018-01-02T00:00:00.000Z")[0];

    assert.ok(result);
    assert.equal(result.scoreResult.factors.find((factor) => factor.id === "sector_product_fit")?.evidence.sampleSize, 0);
  });

  it("requires four distinct revenue buyers and handles values outside the quartile range", () => {
    const target = opportunity({ id: "TARGET", revenue: 5 });
    const buyers = [10, 20, 30].map((revenue, index) => opportunity({
      id: `B${index}`,
      accountId: index + 2,
      accountName: `Buyer ${index}`,
      revenue,
    }));
    const insufficient = score(target, [target, ...buyers]);
    assert.equal(factorPoints(insufficient, "financial_fit"), 0);

    const fourth = opportunity({ id: "B3", accountId: 5, accountName: "Buyer 3", revenue: 40 });
    const sufficient = score(target, [target, ...buyers, fourth]);
    assert.equal(factorPoints(sufficient, "financial_fit"), 15 * 5 / 17.5);
  });

  it("distinguishes missing target data from negative historical evidence", () => {
    const target = opportunity({ id: "TARGET", employees: null, revenue: null });
    const buyers = [10, 20, 30, 40].map((revenue, index) => opportunity({
      id: `B${index}`,
      accountId: index + 2,
      accountName: `Buyer ${index}`,
      revenue,
    }));
    const missing = score(target, [target, ...buyers]);
    assert.equal(missing.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.evidenceState, "missing_target_data");
    assert.equal(missing.factors.find((factor) => factor.id === "financial_fit")?.evidence.evidenceState, "missing_target_data");
    assert.match(missing.factors.find((factor) => factor.id === "company_profile_fit")?.reason ?? "", /não possui/iu);

    const lossTarget = opportunity({ id: "LOSS", stage: "Lost" });
    const loss = score(lossTarget, [lossTarget, opportunity({ id: "ALSO-LOSS", stage: "Lost" })]);
    assert.equal(loss.factors.find((factor) => factor.id === "account_product_fit")?.evidence.evidenceState, "calculated");
    assert.equal(loss.factors.find((factor) => factor.id === "sector_product_fit")?.evidence.evidenceState, "calculated");
  });

  it("handles account, sector, employees and revenue independently", () => {
    const exact = opportunity({ id: "EXACT" });
    const sector = opportunity({ id: "SECTOR", accountId: 2, accountName: "Cliente B" });
    const missingAccount = opportunity({ id: "NO-ACCOUNT", accountId: null, accountName: null });
    const noAccountResult = score(missingAccount, [missingAccount, exact, sector]);
    assert.equal(noAccountResult.factors.find((factor) => factor.id === "account_product_fit")?.evidence.evidenceState, "missing_account");
    assert.ok(factorPoints(noAccountResult, "sector_product_fit") > 0);

    const missingSector = opportunity({ id: "NO-SECTOR", sector: null });
    const sectorResult = score(missingSector, [missingSector, exact, sector]);
    assert.ok(factorPoints(sectorResult, "account_product_fit") > 0);
    assert.equal(sectorResult.factors.find((factor) => factor.id === "sector_product_fit")?.evidence.evidenceState, "missing_sector");

    const noEmployees = opportunity({ id: "NO-EMPLOYEES", employees: null, revenue: 100 });
    const employeeBuyer = opportunity({ id: "BUYER", accountId: 2, accountName: "Cliente B", employees: 100, revenue: 100 });
    const employeeResult = score(noEmployees, [noEmployees, employeeBuyer]);
    assert.equal(employeeResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.employeeEvidenceState, "missing_target_data");
    assert.equal(employeeResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.revenueEvidenceState, "calculated");
    assert.equal(employeeResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.employeeContribution, 0);
    assert.equal(employeeResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.revenueContribution, 10);

    const noRevenue = opportunity({ id: "NO-REVENUE", employees: 100, revenue: null });
    const revenueBuyer = opportunity({ id: "REVENUE-BUYER", accountId: 2, accountName: "Cliente B", employees: 100, revenue: 100 });
    const revenueResult = score(noRevenue, [noRevenue, revenueBuyer]);
    assert.equal(revenueResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.employeeEvidenceState, "calculated");
    assert.equal(revenueResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.employeeContribution, 10);
    assert.equal(revenueResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.revenueEvidenceState, "missing_target_data");
    assert.equal(revenueResult.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.revenueContribution, 0);
  });

  it("scores evidence from the product series when the exact product has no history", () => {
    const target = opportunity({ id: "TARGET" });
    const seriesWin = opportunity({ id: "SERIES", product: "GTX Basic" });
    const result = score(target, [target, seriesWin]);
    const factor = result.factors.find((candidate) => candidate.id === "account_product_fit");

    assert.equal(factor?.evidence.exactTotal, 0);
    assert.equal(factor?.evidence.seriesTotal, 1);
    assert.ok(Math.abs((factor?.points ?? 0) - 35 * 0.3 * (1 / 6)) < 1e-12);
  });

  it("excludes future wins from every factor", () => {
    const target = opportunity({ id: "TARGET", stage: "Prospecting", closeDate: null });
    const future = [
      opportunity({ id: "FUTURE-EXACT", closeDate: "2020-01-01" }),
      ...[2, 3, 4, 5].map((accountId) => opportunity({
        id: `FUTURE-${accountId}`,
        accountId,
        accountName: `Buyer ${accountId}`,
        closeDate: "2020-01-01",
      })),
    ];
    const result = score(target, [target, ...future], "2018-01-01");

    assert.equal(result.factors.find((factor) => factor.id === "account_product_fit")?.evidence.exactTotal, 0);
    assert.equal(result.factors.find((factor) => factor.id === "sector_product_fit")?.evidence.sampleSize, 0);
    assert.equal(result.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.medianEmployees, null);
    assert.equal(result.factors.find((factor) => factor.id === "financial_fit")?.evidence.sampleSize, 0);
  });

  it("excludes Prospecting and Engaging opportunities from every factor", () => {
    const target = opportunity({ id: "TARGET", stage: "Engaging", closeDate: null });
    const result = score(target, [
      target,
      opportunity({ id: "PROSPECTING", stage: "Prospecting", closeDate: null }),
      opportunity({ id: "ENGAGING", stage: "Engaging", closeDate: null }),
    ]);

    assert.equal(result.score, 0);
    assert.equal(result.factors.find((factor) => factor.id === "account_product_fit")?.evidence.evidenceState, "no_historical_evidence");
    assert.equal(result.factors.find((factor) => factor.id === "sector_product_fit")?.evidence.evidenceState, "no_historical_evidence");
    assert.equal(result.factors.find((factor) => factor.id === "company_profile_fit")?.evidence.evidenceState, "no_historical_evidence");
    assert.equal(result.factors.find((factor) => factor.id === "financial_fit")?.evidence.evidenceState, "insufficient_history");
  });

  it("associates the known alias with the canonical product before scoring", () => {
    const canonicalProduct = normalizeProduct("GTXPro");
    assert.ok(canonicalProduct);
    const target = opportunity({ id: "TARGET", product: canonicalProduct });
    const historyProduct = normalizeProduct("GTX Pro");
    assert.ok(historyProduct);
    const history = opportunity({ id: "W1", product: historyProduct });
    const result = score(target, [target, history]);

    assert.equal(result.factors.find((factor) => factor.id === "account_product_fit")?.evidence.exactWon, 1);
    assert.ok(factorPoints(result, "account_product_fit") > 0);
  });
});
