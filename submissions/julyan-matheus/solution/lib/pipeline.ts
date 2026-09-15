/**
 * Build-time view of the pipeline shared by every page.
 * Computed once per process (React `cache`) from the CSVs in /data.
 */
import { cache } from "react";
import { loadAll } from "./data";
import { buildStats, isOpen, isScored, scorePipeline, todayPicks, countBuckets, byScoreDesc } from "./scoring";
import type { Bucket, PipelineRow, SalesAgent, ScoredDeal } from "./types";

export const agentSlug = (name: string) => name.toLowerCase().replace(/\s+/g, "-");

export interface AgentView {
  name: string;
  slug: string;
  manager: string;
  regional_office: string;
  rows: PipelineRow[];
  counts: Record<Bucket, number>;
  total: number;
  focar: ScoredDeal[];
  today: ScoredDeal[];
}

export const getPipeline = cache(() => {
  const { deals, products, salesTeams } = loadAll();
  const stats = buildStats(deals, products);
  const rows = scorePipeline(deals, products, stats.ref);

  const teamByAgent = new Map(salesTeams.map((t) => [t.sales_agent, t]));
  const names = [...new Set(deals.filter(isOpen).map((d) => d.sales_agent))].sort((a, b) => a.localeCompare(b));

  const agents: AgentView[] = names.map((name) => {
    const team: SalesAgent | undefined = teamByAgent.get(name);
    const mine = rows.filter((r) => r.deal.sales_agent === name);
    const counts = countBuckets(mine);
    return {
      name,
      slug: agentSlug(name),
      manager: team?.manager ?? "—",
      regional_office: team?.regional_office ?? "—",
      rows: mine,
      counts,
      total: mine.length,
      focar: mine.filter(isScored).sort(byScoreDesc),
      today: todayPicks(mine, 3),
    };
  });

  const managers = [...new Set(agents.map((a) => a.manager))].sort((a, b) => a.localeCompare(b));

  return { ref: stats.ref, stats, rows, agents, managers };
});

export function getAgent(slug: string): AgentView | undefined {
  return getPipeline().agents.find((a) => a.slug === slug);
}
