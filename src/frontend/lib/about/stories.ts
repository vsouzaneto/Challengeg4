import type { ChallengeCode } from "@/lib/research/stories";

export type AboutBeat = {
  number: string;
  title: string;
  description: string;
  visual: "deploy" | "ai" | "collab" | "security";
};

export type AboutStory = {
  code: ChallengeCode;
  path: string;
  metaTitle: string;
  metaDescription: string;
  headline: string;
  headlineMuted: string;
  lede: string;
  beats: AboutBeat[];
};

export const ABOUT_STORIES: AboutStory[] = [
  {
    code: "001",
    path: "/about-challenge-001",
    metaTitle: "Sobre — Challenge 001 churn",
    metaDescription:
      "Pacote Databricks da RavenStack: cinco CSVs, Assistant, dashboard do CEO e o kernel de retenção.",
    headline: "Cinco tabelas para o CEO.",
    headlineMuted: "Sem a massa da Receita.",
    lede: "O pacote entra no Databricks com os cinco CSVs da RavenStack. A fonte é o SaaS Subscription & Churn Analytics (MIT). O template da Receita Federal não entra. O label canônico é a linha em ravenstack_churn_events.",
    beats: [
      {
        number: "01",
        title: "Ingestão dos cinco CSVs",
        description:
          "Lab 01, 30 min. CSV vira Delta em workspace.ravenstack. Sem esse Run All, o Assistant e a análise não acham as tabelas.",
        visual: "deploy",
      },
      {
        number: "02",
        title: "Assistant nas colunas reais",
        description:
          "Lab 02, 30 min. As perguntas cruzam as tabelas e esbarram na armadilha: accounts.churn_flag diverge do evento.",
        visual: "ai",
      },
      {
        number: "03",
        title: "Dashboard que o CEO abre",
        description:
          "Lab 03, 40 min. É o entregável. Causa, segmentos e ações saem daí, não do kernel.",
        visual: "collab",
      },
      {
        number: "04",
        title: "Retenção e risco de receita",
        description:
          "Lab 04, 40 min. O kernel Kaggle de Retention & Revenue Risk, adaptado. Widgets: catalog_name=workspace, schema_name=ravenstack. Se o caminho falhar, data_path aponta para a pasta dados.",
        visual: "security",
      },
    ],
  },
  {
    code: "002",
    path: "/about-challenge-002",
    metaTitle: "Sobre — Challenge 002 support",
    metaDescription:
      "Pacote Databricks do suporte: 8.469 tickets, Assistant, dashboard de operações e o kernel SupportIQ.",
    headline: "8.469 tickets no disco.",
    headlineMuted: "O CSV ganha o brief.",
    lede: "A fonte é o Customer Support Ticket Dataset (CC0), 8.469 linhas e 17 colunas. O brief fala em cerca de 30 mil. O arquivo ganha. O Dataset 2, com Topic_group, não está neste disco. Nome e e-mail de cliente são PII.",
    beats: [
      {
        number: "01",
        title: "Um CSV, uma tabela Delta",
        description:
          "Lab 01, 30 min. customer_support_tickets vai para workspace.supportiq. A pasta dados precisa ir junto no import.",
        visual: "deploy",
      },
      {
        number: "02",
        title: "Assistant no gargalo",
        description:
          "Lab 02, 30 min. Perguntas de gargalo, CSAT e horas. Horas são TTR menos o primeiro response, e só em Closed. Colunas com espaço pedem backtick.",
        visual: "ai",
      },
      {
        number: "03",
        title: "Dashboard de operações",
        description:
          "Lab 03, 40 min. É o entregável do Diretor de Operações: onde o fluxo trava, em horas.",
        visual: "collab",
      },
      {
        number: "04",
        title: "SupportIQ adaptado",
        description:
          "Lab 04, 40 min. Kernel de partida SupportIQ. Widgets: catalog_name=workspace, schema_name=supportiq. Time to Resolution é datetime, não uma coluna de horas. Ticket Type tem cinco valores.",
        visual: "security",
      },
    ],
  },
  {
    code: "003",
    path: "/about-challenge-003",
    metaTitle: "Sobre — Challenge 003 lead",
    metaDescription:
      "Pacote Databricks do CRM: quatro CSVs, Assistant, a ferramenta do vendedor e o ranking Won/Lost como lógica.",
    headline: "O vendedor abre o Lab 03.",
    headlineMuted: "O Lab 04 é a lógica.",
    lede: "A fonte é o CRM Sales Predictive Analytics (CC0): 85 contas, 7 produtos, 35 times e 8.800 oportunidades, mais o dicionário. O brief pede a ferramenta que o vendedor abre. O experimento Won/Lost informa o score. Ele não é a entrega.",
    beats: [
      {
        number: "01",
        title: "Quatro CSVs no schema crm",
        description:
          "Lab 01, 30 min. accounts, products, sales_teams e sales_pipeline viram workspace.crm. GTXPro fica cru na carga.",
        visual: "deploy",
      },
      {
        number: "02",
        title: "Assistant nas armadilhas",
        description:
          "Lab 02, 30 min. GTXPro não junta em GTX Pro. 1.425 deals abertos estão sem account. close_value nulo no aberto; 0 no histórico é Lost.",
        visual: "ai",
      },
      {
        number: "03",
        title: "A fila que o vendedor filtra",
        description:
          "Lab 03, 40 min. Entregável: pipe aberto com score e o porquê, filtrado por sales_agent. Não ordena por close_value.",
        visual: "collab",
      },
      {
        number: "04",
        title: "Campos do CRM contra o desfecho",
        description:
          "Lab 04, 40 min. Kernel de partida: os campos do CRM separam Won de Lost? Widgets: catalog_name=workspace, schema_name=crm.",
        visual: "security",
      },
    ],
  },
  {
    code: "004",
    path: "/about-challenge-004",
    metaTitle: "Sobre — Challenge 004 social",
    metaDescription:
      "Pacote Databricks de social: 52.214 posts, Assistant, dashboard de marketing e o analisador de engajamento.",
    headline: "52.214 posts, 27 colunas.",
    headlineMuted: "A taxa não vem no arquivo.",
    lede: "A fonte é o Social Media Sponsorship & Engagement Dataset (MIT). Não existe engagement_rate. A taxa por view no dump fica perto de 0,199. creator_name não é a chave. Audiência é faixa. Não há custo de patrocínio.",
    beats: [
      {
        number: "01",
        title: "Um CSV de posts",
        description:
          "Lab 01, 30 min. social_media_dataset vai para workspace.social. Sem o Run All, o Assistant e o kernel não acham a tabela.",
        visual: "deploy",
      },
      {
        number: "02",
        title: "Assistant com a taxa derivada",
        description:
          "Lab 02, 30 min. A taxa se deriva, e orgânico contra patrocinado pede controle. Não se usa uma coluna que o CSV não tem.",
        visual: "ai",
      },
      {
        number: "03",
        title: "Dashboard de marketing",
        description:
          "Lab 03, 40 min. É o entregável do Head: o que gera engajamento e onde concentrar o esforço.",
        visual: "collab",
      },
      {
        number: "04",
        title: "Analisador de engajamento",
        description:
          "Lab 04, 40 min. Kernel adaptado da aba Code do dataset. Widgets: catalog_name=workspace, schema_name=social. data_path cai na pasta dados se o auto-path falhar.",
        visual: "security",
      },
    ],
  },
];

export function getAboutStory(code: ChallengeCode): AboutStory {
  const story = ABOUT_STORIES.find((item) => item.code === code);
  if (!story) {
    throw new Error(`Unknown about story ${code}`);
  }
  return story;
}
