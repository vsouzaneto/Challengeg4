export type DealStage = "Prospecting" | "Engaging" | "Won" | "Lost";

export interface Deal {
  opportunity_id: string;
  sales_agent: string;
  product: string;
  account: string | null;
  deal_stage: DealStage;
  /** ISO date (YYYY-MM-DD) or null for Prospecting. */
  engage_date: string | null;
  /** ISO date or null for open deals. Never used to score an open deal. */
  close_date: string | null;
  /** Never used to score an open deal. */
  close_value: number | null;
}

export interface Product {
  product: string;
  series: string;
  sales_price: number;
}

export interface Account {
  account: string;
  sector: string;
  year_established: number;
  revenue: number;
  employees: number;
  office_location: string;
  subsidiary_of: string | null;
}

export interface SalesAgent {
  sales_agent: string;
  manager: string;
  regional_office: string;
}

export type Bucket = "Focar" | "Requalificar" | "Iniciar" | "Limpar";

export type Tone = "positivo" | "neutro" | "alerta";

/** Relative position of the deal among the same agent's Focar deals (thirds by rank). */
export type Tier = "Top" | "Meio" | "Fundo";

export interface WhyLine {
  factor: "afinidade" | "momentum" | "capacidade";
  text: string;
  tone: Tone;
}

export interface Factors {
  /** 0–1: smoothed win rate of agent × product. */
  affinity: number;
  /** 0–1: historical win rate given the deal survived this many days. */
  momentum: number;
  /** 0–1: 1 − minmax(open deals of the agent). */
  capacity: number;
}

export interface ScoredDeal {
  deal: Deal;
  bucket: "Focar";
  daysOpen: number;
  /** 0–100 */
  score: number;
  /** Top / Meio / Fundo do Focar do vendedor, por posição no ranking (terços). Null com menos de 3 deals. */
  tier: Tier | null;
  /** 0–1, used only for expected value. */
  chance: number;
  /** chance × sales_price, in dollars. */
  expectedValue: number;
  factors: Factors;
  why: WhyLine[];
}

export interface TriagedDeal {
  deal: Deal;
  bucket: Exclude<Bucket, "Focar">;
  daysOpen: number | null;
  action: string;
}

export type PipelineRow = ScoredDeal | TriagedDeal;
