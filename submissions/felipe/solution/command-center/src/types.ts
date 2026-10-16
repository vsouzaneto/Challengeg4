export type Conta = {
  conta_id: string;
  nome_conta: string;
  industria: string;
  pais: string;
  canal_aquisicao: string;
  plano_atual: string;
  em_trial: string;
  mrr_usd: number;
  status_conta: string;
  churn_liquido: boolean;
  eventos_churn: number;
  data_cadastro?: string | null;
  data_ultimo_churn?: string | null;
  data_ultimo_uso?: string | null;
  score_risco?: number | null;
  faixa_risco?: string | null;
  prioridade_mrr?: number | null;
  motivo_risco?: string | null;
  taxa_escalacao_pct?: number;
};

export type InvestigacaoConta = {
  eventos_churn: { data: string; motivo: string; reativacao: boolean }[];
  uso_mensal: { mes: string; total: number }[];
  suporte: {
    tickets: number;
    csat_medio: number | null;
    taxa_escalacao_pct: number;
  };
  alertas: string[];
};

export type QualidadeDados = {
  contas_total: number;
  churn_liquido_flag: number;
  contas_flag_sem_evento_churn: number;
  mrr_contratual_flag_sem_evento_usd: number;
  pct_uso_antes_assinatura: number;
  eventos_churn_total: number;
  contas_com_evento: number;
};

export type RecomendacaoDestaque = {
  acao: string;
  impacto_mrr_usd: number;
  impacto_anual_arr_usd: number;
  confianca: string;
};

export type Bundle = {
  meta: { produto: string; versao: string; autor: string; design_ref: string };
  narrativa_executiva: { headline: string; bullets: string[] };
  kpis_globais: Record<string, number>;
  contas: Conta[];
  uso_mensal_por_industria: { month: string; industry: string; total_usage: number }[];
  filtros_disponiveis: Record<string, string[] | string> & {
    periodo_meses?: string[];
    periodo_min?: string;
    periodo_max?: string;
  };
  qualidade_dados?: QualidadeDados;
  recomendacao_destaque?: RecomendacaoDestaque;
  investigacoes?: Record<string, InvestigacaoConta>;
};

export type FilterState = {
  status_conta: string[];
  industria: string[];
  canal_aquisicao: string[];
  plano_atual: string[];
  faixa_risco: string[];
  em_trial: string;
  escalacao_acima: boolean;
  periodo_inicio: string;
  periodo_fim: string;
};

export const emptyFilters = (): FilterState => ({
  status_conta: [],
  industria: [],
  canal_aquisicao: [],
  plano_atual: [],
  faixa_risco: [],
  em_trial: "",
  escalacao_acima: false,
  periodo_inicio: "",
  periodo_fim: "",
});
