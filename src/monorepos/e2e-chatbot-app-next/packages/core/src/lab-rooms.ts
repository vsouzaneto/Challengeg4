export const LAB_ROOM_ALIASES = ['churn', 'support', 'crm', 'social'] as const;

export type LabRoomAlias = (typeof LAB_ROOM_ALIASES)[number];

export type LabRoom = {
  alias: LabRoomAlias;
  title: string;
  pack: string;
  schema: string;
  tables: readonly string[];
  suggestions: readonly string[];
  envKey: string;
};

export const LAB_ROOMS: readonly LabRoom[] = [
  {
    alias: 'churn',
    title: '001 Churn',
    pack: 'notebook-data-001-churn',
    schema: 'ravenstack',
    tables: [
      'workspace.ravenstack.ravenstack_accounts',
      'workspace.ravenstack.ravenstack_subscriptions',
      'workspace.ravenstack.ravenstack_feature_usage',
      'workspace.ravenstack.ravenstack_support_tickets',
      'workspace.ravenstack.ravenstack_churn_events',
    ],
    suggestions: [
      'Quantas contas distintas existem e quantas têm pelo menos um churn_event_id?',
      'O churn_flag de ravenstack_accounts coincide com a existência de churn_event_id?',
      'Taxa de contas com evento de churn por industry e plan_tier',
    ],
    envKey: 'GENIE_SPACE_ID_CHURN',
  },
  {
    alias: 'support',
    title: '002 Suporte',
    pack: 'notebook-process-002-support',
    schema: 'supportiq',
    tables: ['workspace.supportiq.customer_support_tickets'],
    suggestions: [
      'Quantos tickets por Ticket Status, Ticket Type, Ticket Priority e Ticket Channel?',
      'Em Closed, p95 de horas TTR menos FRT por canal, prioridade e tipo',
      'CSAT médio por canal, tipo e prioridade só em Closed',
    ],
    envKey: 'GENIE_SPACE_ID_SUPPORT',
  },
  {
    alias: 'crm',
    title: '003 CRM',
    pack: 'notebook-build-003-lead-scorer',
    schema: 'crm',
    tables: [
      'workspace.crm.accounts',
      'workspace.crm.products',
      'workspace.crm.sales_teams',
      'workspace.crm.sales_pipeline',
    ],
    suggestions: [
      'Quantas oportunidades por deal_stage e quantas abertas (Prospecting + Engaging)?',
      'Quais product do pipeline não existem em products, incluindo GTXPro vs GTX Pro?',
      'Ordenar só por close_value serve para o pipe aberto?',
    ],
    envKey: 'GENIE_SPACE_ID_CRM',
  },
  {
    alias: 'social',
    title: '004 Social',
    pack: 'notebook-marketing-004-social',
    schema: 'social',
    tables: ['workspace.social.social_media_dataset'],
    suggestions: [
      'Quantos posts por platform, content_type e content_category? Inclua Bilibili e RedNote.',
      'Taxa derivada (likes+shares+comments_count)/views por platform e is_sponsored',
      'creator_id vs creator_name: quantos nomes distintos por creator?',
    ],
    envKey: 'GENIE_SPACE_ID_SOCIAL',
  },
] as const;

export function isLabRoomAlias(value: string): value is LabRoomAlias {
  return (LAB_ROOM_ALIASES as readonly string[]).includes(value);
}

export function getLabRoom(alias: string): LabRoom | undefined {
  return LAB_ROOMS.find((room) => room.alias === alias);
}

export function listConfiguredLabRooms(
  env: NodeJS.ProcessEnv = process.env,
): Array<LabRoom & { spaceId: string | null }> {
  return LAB_ROOMS.map((room) => ({
    ...room,
    spaceId: env[room.envKey]?.trim() || null,
  }));
}
