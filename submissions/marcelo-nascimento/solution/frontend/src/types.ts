export interface User {
  id: number;
  name: string;
  email: string;
}

export interface ApplicationUser extends User {
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export type EvidenceValue = string | number | boolean | null;

export interface ScoreFactor {
  id: string;
  label: string;
  points: number;
  maxPoints: number;
  strength: "forte" | "moderada" | "fraca" | "sem evidência";
  reason: string;
  evidence: Record<string, EvidenceValue>;
}

export interface ScoreResult {
  opportunityId: string;
  score: number;
  rawScore: number;
  factors: ScoreFactor[];
  justification: string;
  calculatedAt: string;
}

export interface Opportunity {
  id: string;
  account: string | null;
  product: string;
  dealStage: "Prospecting" | "Engaging" | "Won" | "Lost";
  salesAgent: string;
  score: number;
  isHotLead: boolean;
}

export type OpportunityDetail = Omit<Opportunity, "score"> & {
  sector: string | null;
  employees: number | null;
  revenue: number | null;
  series: string | null;
  salesPrice: number | null;
  manager: string | null;
  regionalOffice: string | null;
  engageDate: string | null;
  closeDate: string | null;
  closeValue: number | null;
  score: ScoreResult;
}

export interface FilterOptions {
  stages: string[];
  products: string[];
  sectors: Array<{ id: string; label: string }>;
  sellers: string[];
  scoreBands: Array<{ id: string; label: string }>;
}

export interface PaginatedOpportunities {
  data: Opportunity[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
  calculatedAt: string;
}

export interface DashboardData {
  metrics: {
    openOpportunities: number;
    hotLeads: number;
    averageOpenScore: number | null;
    pipelineValue: number | null;
  };
  priorityOpportunities: Opportunity[];
  scoreDistribution: Array<{ id: string; label: string; count: number }>;
  calculatedAt: string;
}

export interface GroupAverage {
  name: string;
  count: number;
  averageScore: number | null;
}

export interface ReportData {
  distribution: Array<{ id: string; label: string; count: number }>;
  averageByProduct: GroupAverage[];
  averageBySector: GroupAverage[];
  pipelineByStage: Array<{ stage: string; count: number }>;
  historicalConversionByProduct: Array<GroupAverage & { won: number; lost: number; conversionRate: number }>;
  total: number;
  calculatedAt: string;
}
