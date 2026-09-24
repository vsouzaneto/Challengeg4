// Deterministic fixtures derived from the OpenAPI examples (docs-site/docs/api/openapi.json).
// Dev/test only — never imported by production code (see main.tsx).
import type {
  AgentSummary,
  ManagerSummary,
  MetaResponse,
  ModelMetricsResponse,
  PipelineGroup,
  PipelineSummary,
  Reason,
  RegionSummary,
  ScoredDeal,
} from '../api/client';

export const AS_OF = '2017-12-31';
export const MODEL_VERSION = '2017-12-31-lr-v1';
export const ZOMBIE_THRESHOLD = 138;

const ORG: { region: string; manager: string; agents: string[] }[] = [
  {
    region: 'Central',
    manager: 'Melvin Marxen',
    agents: ['Darcel Schlecht', 'Cassey Cress', 'Kary Hendrixson'],
  },
  { region: 'Central', manager: 'Dustin Brinkmann', agents: ['Zane Levy', 'Anna Snelling'] },
  { region: 'East', manager: 'Cara Losch', agents: ['Vicki Laflamme', 'Moses Frase'] },
  { region: 'East', manager: 'Rocco Neubert', agents: ['Donn Cantrell', 'Boris Faz'] },
  { region: 'West', manager: 'Celia Rouche', agents: ['Reed Clapper', 'Niesha Huffines'] },
  { region: 'West', manager: 'Summer Sewald', agents: ['Gladys Colclough', 'Wilburn Farren'] },
];

const PRODUCTS: [string, number][] = [
  ['GTX Pro', 4821],
  ['MG Advanced', 3393],
  ['GTK 500', 26768],
  ['GTX Basic', 550],
  ['MG Special', 55],
  ['GTX Plus Basic', 1096],
];
const ACCOUNTS = [
  'Konex',
  'Zumgoity',
  'Hottechi',
  'Cheers',
  'Kan-code',
  'Isdom',
  'Streethex',
  'Faxquote',
];

// Small LCG so fixtures are stable across runs.
function rng(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
}

function tierOf(score: number): ScoredDeal['tier'] {
  return score >= 75 ? 'A' : score >= 55 ? 'B' : score >= 35 ? 'C' : 'D';
}

function reasonsFor(d: {
  product: string;
  account: string | null;
  days: number | null;
  price: number;
  agentRate: number;
  agentN: number;
  productRate: number;
  productN: number;
}): Reason[] {
  // Texts follow docs/revops-review.md §1: context codes are informative (direction i, weight 0).
  const rs: Reason[] = [];
  const rate = Math.round(d.productRate * 100);
  rs.push({
    code: 'PRODUCT_BASE_RATE',
    direction: 'i',
    weight: 0.56,
    text_pt: `${d.product} fecha em ${rate}% dos casos (${d.productN} deals no histórico; média geral 63%).`,
  });
  rs.push({
    code: 'AGENT_PRODUCT_FIT',
    direction: 'i',
    weight: 0,
    text_pt: `Você fecha ${Math.round(d.agentRate * 100)}% dos ${d.product} (${d.agentN} deals${d.agentN < 30 ? ', amostra pequena' : ''}).`,
  });
  if (d.days === null) {
    rs.push({
      code: 'PROSPECTING_NO_TIMELINE',
      direction: 'i',
      weight: 0,
      text_pt:
        'Em Prospecting, sem data de primeiro contato: não dá para medir urgência; a posição na fila vem só do valor.',
    });
  } else if (d.days > ZOMBIE_THRESHOLD) {
    rs.push({
      code: 'ZOMBIE_RISK',
      direction: '-',
      weight: -18,
      text_pt: `${d.days} dias em Engaging: nenhum deal na história fechou depois de 138. Este deal saiu da sua fila de trabalho e está na fila "Confirmar ou encerrar".`,
    });
  } else if (d.days > 60) {
    rs.push({
      code: 'SURVIVAL_POSITIVE',
      direction: 'i',
      weight: 0,
      text_pt:
        d.days > 120
          ? `${d.days} dias em Engaging. Deals que chegaram aqui fecharam em 68% dos casos — mas nenhum deal fechou depois de 138 dias: faltam ${138 - d.days}.`
          : `${d.days} dias em Engaging. Deals que chegaram aqui fecharam em 68% dos casos.`,
    });
  }
  if (d.price > 10000) {
    rs.push({
      code: 'HIGH_TICKET',
      direction: '+',
      weight: 7,
      text_pt: `Ticket alto: R$ ${Math.round(d.price * d.productRate).toLocaleString('pt-BR')} esperados se fechar (preço de tabela R$ ${d.price.toLocaleString('pt-BR')}; ${d.product} fecha em ${rate}% dos casos).`,
    });
  } else if (d.price < 1000) {
    rs.push({
      code: 'LOW_TICKET',
      direction: '-',
      weight: -2,
      text_pt: `Ticket baixo: ${d.product} vale R$ ${d.price}. Feche rápido ou deixe para depois dos deals maiores.`,
    });
  }
  if (d.account === null) {
    rs.push({
      code: 'ACCOUNT_UNKNOWN',
      direction: 'i',
      weight: 0,
      text_pt:
        'Sem conta no CRM: não sabemos setor, porte nem histórico. Registre a conta antes do próximo contato — leva 1 minuto e libera confiança alta.',
    });
  }
  rs.push({
    code: 'MODEL_CONTRIBUTION',
    direction: 'i',
    weight: 0,
    text_pt: 'Modelo estatístico em modo sombra: ajuste de 0 pontos.',
  });
  return rs.sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight));
}

function nextActionFor(days: number | null, account: string | null): string {
  if (days === null) return 'Registre o primeiro contato no CRM ao fazê-lo.';
  if (days > ZOMBIE_THRESHOLD)
    return 'Confirme com o cliente se a oportunidade existe; se não, encerre no CRM.';
  if (days > 100)
    return `Faltam ${ZOMBIE_THRESHOLD - days} dias para o ciclo máximo já visto: fechar ou desistir esta semana.`;
  if (account === null) return 'Confirmar a conta no CRM e agendar próximo passo.';
  if (days > 60) return 'Ligar esta semana e propor data de fechamento.';
  return 'Mantenha o ritmo: agendar próximo contato.';
}

export function buildDeals(): ScoredDeal[] {
  const rand = rng(42);
  const deals: ScoredDeal[] = [];
  let seq = 0;
  for (const unit of ORG) {
    for (const agent of unit.agents) {
      const agentRate = 0.55 + rand() * 0.15;
      const n = 6 + Math.floor(rand() * 5);
      for (let i = 0; i < n; i++) {
        const [product, price] = PRODUCTS[Math.floor(rand() * PRODUCTS.length)]!;
        const account = rand() < 0.68 ? null : ACCOUNTS[Math.floor(rand() * ACCOUNTS.length)]!;
        const prospecting = rand() < 0.24;
        const days = prospecting ? null : Math.floor(rand() * 160);
        const pWin = Math.max(
          0.2,
          Math.min(
            0.9,
            agentRate + (account ? 0.05 : -0.03) + (days !== null && days > 138 ? -0.2 : 0),
          ),
        );
        const urgency =
          days === null ? 0.3 : days > 138 ? 0.2 : days > 100 ? 0.5 : 0.6 + (days / 100) * 0.3;
        const expected = Math.round(price * pWin * 100) / 100;
        const score = Math.max(
          5,
          Math.min(
            98,
            Math.round((pWin * 60 + urgency * 30 + Math.log10(price + 1) * 3) * 10) / 10,
          ),
        );
        seq += 1;
        deals.push({
          opportunity_id: `Z${String(seq).padStart(3, '0')}OYW${String.fromCharCode(65 + (seq % 26))}`,
          sales_agent: agent,
          manager: unit.manager,
          regional_office: unit.region,
          product,
          account,
          deal_stage: prospecting ? 'Prospecting' : 'Engaging',
          days_in_engaging: days,
          priority_score: score,
          tier: tierOf(score),
          p_win: Math.round(pWin * 100) / 100,
          expected_value: expected,
          sales_price: price,
          urgency: Math.round(urgency * 100) / 100,
          confidence: account ? 'alta' : prospecting ? 'baixa' : 'media',
          reasons: reasonsFor({
            product,
            account,
            days,
            price,
            agentRate,
            agentN: 10 + Math.floor(rand() * 40),
            productRate: 0.6 + (PRODUCTS.findIndex((p) => p[0] === product) % 3) * 0.02,
            productN: 400 + Math.floor(rand() * 900),
          }),
          next_action: nextActionFor(days, account),
          as_of: AS_OF,
          model_version: MODEL_VERSION,
        });
      }
    }
  }
  // Pin the OpenAPI example as the top deal so tests can assert on it.
  deals.unshift({
    account: 'Konex',
    as_of: AS_OF,
    confidence: 'alta',
    days_in_engaging: 78,
    deal_stage: 'Engaging',
    expected_value: 3412.5,
    sales_price: 4821,
    manager: 'Melvin Marxen',
    model_version: MODEL_VERSION,
    next_action: 'Ligar esta semana e propor data de fechamento.',
    opportunity_id: 'Z063OYW0',
    p_win: 0.71,
    priority_score: 82.4,
    product: 'GTX Pro',
    reasons: [
      {
        code: 'HIGH_TICKET',
        direction: '+',
        text_pt:
          'Ticket alto: R$ 3.412 esperados se fechar (preço de tabela R$ 4.821; GTX Pro fecha em 71% dos casos).',
        weight: 9,
      },
      {
        code: 'PRODUCT_BASE_RATE',
        direction: 'i',
        text_pt: 'GTX Pro fecha em 71% dos casos (1.480 deals no histórico; média geral 63%).',
        weight: 0.56,
      },
      {
        code: 'AGENT_PRODUCT_FIT',
        direction: 'i',
        text_pt: 'Você fecha 74% dos GTX Pro (52 deals).',
        weight: 0,
      },
      {
        code: 'SURVIVAL_POSITIVE',
        direction: 'i',
        text_pt: '78 dias em Engaging. Deals que chegaram aqui fecharam em 68% dos casos.',
        weight: 0,
      },
      {
        code: 'MODEL_CONTRIBUTION',
        direction: 'i',
        text_pt: 'Modelo estatístico em modo sombra: ajuste de 0 pontos.',
        weight: 0,
      },
    ],
    regional_office: 'Central',
    sales_agent: 'Darcel Schlecht',
    tier: 'A',
    urgency: 0.8,
  });
  return deals;
}

export const DEALS = buildDeals();

export const META: MetaResponse = {
  schema_version: '1.0.0',
  as_of_available: ['2017-09-30', AS_OF],
  default_as_of: AS_OF,
  model_version: MODEL_VERSION,
  artifacts_present: true,
  open_deals: DEALS.length,
  snapshot_date: AS_OF,
};

const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0);
const tiers = (ds: ScoredDeal[]) => ({
  A: ds.filter((d) => d.tier === 'A').length,
  B: ds.filter((d) => d.tier === 'B').length,
  C: ds.filter((d) => d.tier === 'C').length,
  D: ds.filter((d) => d.tier === 'D').length,
});

export function agents(): AgentSummary[] {
  return ORG.flatMap((u) =>
    u.agents.map((a) => {
      const ds = DEALS.filter((d) => d.sales_agent === a);
      return {
        sales_agent: a,
        manager: u.manager,
        regional_office: u.region,
        open_deals: ds.length,
        expected_value: sum(ds.map((d) => d.expected_value)),
        tier_distribution: tiers(ds),
      };
    }),
  );
}

export function managers(): ManagerSummary[] {
  return ORG.map((u) => {
    const ds = DEALS.filter((d) => d.manager === u.manager);
    return {
      manager: u.manager,
      regional_office: u.region,
      sales_agents: u.agents,
      open_deals: ds.length,
      expected_value: sum(ds.map((d) => d.expected_value)),
    };
  });
}

export function regions(): RegionSummary[] {
  const names = [...new Set(ORG.map((u) => u.region))];
  return names.map((r) => {
    const units = ORG.filter((u) => u.region === r);
    const ds = DEALS.filter((d) => d.regional_office === r);
    return {
      regional_office: r,
      managers: units.map((u) => u.manager),
      agents: sum(units.map((u) => u.agents.length)),
      open_deals: ds.length,
      expected_value: sum(ds.map((d) => d.expected_value)),
    };
  });
}

function group(key: string, ds: ScoredDeal[]): PipelineGroup {
  const zombies = ds.filter((d) => (d.days_in_engaging ?? 0) > ZOMBIE_THRESHOLD);
  const cooling = ds.filter((d) => {
    const days = d.days_in_engaging ?? 0;
    return days > 100 && days <= ZOMBIE_THRESHOLD;
  });
  return {
    nominal_zombie_value: sum(zombies.map((d) => d.sales_price ?? 0)),
    cooling_count: cooling.length,
    cooling_value: sum(cooling.map((d) => d.expected_value)),
    key,
    open_deals: ds.length,
    engaging: ds.filter((d) => d.deal_stage === 'Engaging').length,
    prospecting: ds.filter((d) => d.deal_stage === 'Prospecting').length,
    expected_value: sum(ds.map((d) => d.expected_value)),
    zombie_count: zombies.length,
    zombie_value: sum(zombies.map((d) => d.expected_value)),
    account_coverage: ds.length ? ds.filter((d) => d.account).length / ds.length : 0,
    tier_distribution: tiers(ds),
    avg_priority_score: ds.length ? sum(ds.map((d) => d.priority_score)) / ds.length : 0,
  };
}

export function pipelineSummary(
  groupBy: PipelineSummary['group_by'],
  ds: ScoredDeal[],
): PipelineSummary {
  const keys = [...new Set(ds.map((d) => d[groupBy]))];
  return {
    group_by: groupBy,
    as_of: AS_OF,
    model_version: MODEL_VERSION,
    zombie_threshold_days: ZOMBIE_THRESHOLD,
    cooling_min_days: 101,
    total: group('total', ds),
    groups: keys.map((k) =>
      group(
        k,
        ds.filter((d) => d[groupBy] === k),
      ),
    ),
  };
}

// Layout per docs/specs/scoring-spec.md §8 (numbers from the pandas prototype).
export const METRICS: ModelMetricsResponse = {
  model_version: MODEL_VERSION,
  model_card_path: `models/${MODEL_VERSION}/model_card.md`,
  model_card_markdown:
    '# Model card\n\nRegras transparentes + regressão logística; validação temporal em 2017-06-30 e 2017-09-30.',
  feature_list: ['product_base_rate', 'days_in_engaging', 'agent_product_fit'],
  metrics: {
    model_version: MODEL_VERSION,
    as_of: AS_OF,
    cuts: ['2017-06-30', '2017-09-30'],
    summary: {
      coverage: 2089,
      prospecting_count: 500,
      zombie_count: 1291,
      account_known_rate: 0.32,
      mean_calibration_error: 0.04,
      spearman_score_price: 0.46,
    },
    backtest: {
      '2017-06-30': {
        n_open: 1810,
        n_labeled: 700,
        n_censored: 1110,
        base_rate: 0.61,
        brier: 0.239,
        auc_pr: 0.61,
        auc_pr_ci: [0.56, 0.66],
        auc_roc: 0.51,
        lift_top_decile: 1.1,
        precision_at_10: 0.58,
        precision_at_10_ci: [0.53, 0.63],
        precision_at_25: 0.57,
        revenue_capture_top20: 0.34,
        revenue_capture_top20_ci: [0.29, 0.39],
        calibration_bins: [
          { bin: 0, p_low: 0.4, p_high: 0.5, predicted: 0.46, actual: 0.44, count: 120 },
          { bin: 1, p_low: 0.5, p_high: 0.6, predicted: 0.55, actual: 0.57, count: 300 },
          { bin: 2, p_low: 0.6, p_high: 0.7, predicted: 0.64, actual: 0.62, count: 200 },
          { bin: 3, p_low: 0.7, p_high: 0.8, predicted: 0.74, actual: 0.7, count: 60 },
          { bin: 4, p_low: 0.8, p_high: 0.9, predicted: 0.83, actual: 0.8, count: 20 },
        ],
      },
      '2017-09-30': {
        n_open: 2409,
        n_labeled: 935,
        n_censored: 1474,
        base_rate: 0.598,
        brier: 0.243,
        auc_pr: 0.605,
        auc_pr_ci: [0.558, 0.649],
        auc_roc: 0.495,
        lift_top_decile: 1.14,
        precision_at_10: 0.56,
        precision_at_10_ci: [0.51, 0.61],
        precision_at_25: 0.552,
        revenue_capture_top20: 0.359,
        revenue_capture_top20_ci: [0.305, 0.398],
        calibration_bins: [
          { bin: 0, p_low: 0.4, p_high: 0.5, predicted: 0.46, actual: 0.46, count: 118 },
          { bin: 1, p_low: 0.5, p_high: 0.6, predicted: 0.55, actual: 0.57, count: 412 },
          { bin: 2, p_low: 0.6, p_high: 0.7, predicted: 0.64, actual: 0.64, count: 903 },
          { bin: 3, p_low: 0.7, p_high: 0.8, predicted: 0.74, actual: 0.73, count: 356 },
          { bin: 4, p_low: 0.8, p_high: 0.9, predicted: 0.83, actual: 0.81, count: 64 },
        ],
      },
    },
    baselines: {
      random: {
        '2017-09-30': {
          precision_at_10: 0.603,
          precision_at_10_ci: [0.55, 0.65],
          auc_pr: 0.619,
          revenue_capture_top20: 0.206,
          lift_top_decile: 1.16,
        },
        '2017-06-30': {
          precision_at_10: 0.6,
          precision_at_10_ci: [0.55, 0.65],
          revenue_capture_top20: 0.2,
        },
      },
      newest: {
        '2017-09-30': {
          precision_at_10: 0.547,
          precision_at_10_ci: [0.5, 0.6],
          auc_pr: 0.581,
          revenue_capture_top20: 0.194,
        },
        '2017-06-30': { precision_at_10: 0.55, precision_at_10_ci: [0.5, 0.6] },
      },
      price: {
        '2017-09-30': {
          precision_at_10: 0.577,
          precision_at_10_ci: [0.53, 0.63],
          auc_pr: 0.593,
          revenue_capture_top20: 0.459,
        },
        '2017-06-30': { precision_at_10: 0.57, precision_at_10_ci: [0.52, 0.62] },
      },
      base_rate: {
        '2017-09-30': {
          precision_at_10: 0.557,
          precision_at_10_ci: [0.51, 0.61],
          auc_pr: 0.605,
          revenue_capture_top20: 0.006,
        },
        '2017-06-30': { precision_at_10: 0.56, precision_at_10_ci: [0.51, 0.61] },
      },
    },
  },
};
