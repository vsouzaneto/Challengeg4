// Respostas da API com dados sintéticos, gravadas por scripts/export_fixtures.py (no back).
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

import type {
  ErrorBody, Intelligence, IntelligenceDeals, Meta, SellerList, SellerPipeline, TeamPipeline,
} from "@/lib/contract";
import {
  zErrorBody, zIntelligence, zIntelligenceDeals, zMeta, zSellerList, zSellerPipeline, zTeamPipeline,
} from "@/lib/contract/zod.gen";

export const WEB_DIR = join(import.meta.dirname, "..");
const FIXTURES_DIR = join(import.meta.dirname, "fixtures");

export const load = (name: string): unknown => JSON.parse(readFileSync(join(FIXTURES_DIR, `${name}.json`), "utf8"));

export const readContract = (): { components: { schemas: Record<string, any> } } =>
  JSON.parse(readFileSync(join(WEB_DIR, "contract", "openapi.json"), "utf8"));

const names = (prefix: string) =>
  readdirSync(FIXTURES_DIR).filter((f) => f.startsWith(prefix)).map((f) => f.replace(/\.json$/, "")).sort();

export const sellerPipeline = (name: string) => zSellerPipeline.parse(load(name)) as SellerPipeline;
export const teamPipeline = (name: string) => zTeamPipeline.parse(load(name)) as TeamPipeline;
export const meta = () => zMeta.parse(load("meta")) as Meta;
export const sellers = () => zSellerList.parse(load("sellers")) as SellerList;
export const errors = () =>
  Object.fromEntries(Object.entries(load("errors") as Record<string, unknown>)
    .map(([status, body]) => [status, zErrorBody.parse(body) as ErrorBody]));

export const intelligence = (name: string) => zIntelligence.parse(load(name)) as Intelligence;
export const intelligenceDeals = (name: string) => zIntelligenceDeals.parse(load(name)) as IntelligenceDeals;

export const SELLER_PIPELINES = names("pipeline-");
export const INTELLIGENCE_DEALS = names("intelligence-deals-");
export const INTELLIGENCE_PAGES = names("intelligence-").filter((name) => !INTELLIGENCE_DEALS.includes(name));
export const TEAM_PIPELINES = names("team-");

/** Todas as carteiras das fixtures, do vendedor e do time. */
export const allPipelines = (): (SellerPipeline | TeamPipeline)[] => [
  ...SELLER_PIPELINES.map(sellerPipeline),
  ...TEAM_PIPELINES.map(teamPipeline),
];
