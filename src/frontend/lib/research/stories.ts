export type ChallengeCode = "001" | "002" | "003" | "004";

export type StoryStat = {
  value: string;
  label: string;
  hint: string;
};

export type StoryCard = {
  id: string;
  short: string;
  title: string;
  body: string;
  metric: string;
};

export type StoryRow = {
  id: string;
  label: string;
  detail: string;
  keep: boolean;
};

export type StoryLens = {
  id: string;
  label: string;
  subtitle: string;
  lead: string;
  points: string[];
};

export type ResearchStory = {
  code: ChallengeCode;
  slug: string;
  menuLabel: string;
  path: string;
  modelPath: string;
  aboutPath: string;
  imagePath: string;
  metaTitle: string;
  metaDescription: string;
  headline: string;
  headlineMuted: string;
  paragraphs: string[];
  stats: StoryStat[];
  signalTitle: string;
  signalBody: string;
  cards: StoryCard[];
  cutTitle: string;
  cutBody: string;
  rows: StoryRow[];
  analysisMuted: string;
  lenses: StoryLens[];
};

export const CHALLENGES: ResearchStory[] = [
  {
    code: "001",
    slug: "churn",
    menuLabel: "001 churn",
    path: "/research-challenge-001",
    modelPath: "/model-challenge-001",
    aboutPath: "/about-challenge-001",
    imagePath: "/model-2-challenge-001",
    metaTitle: "Pesquisa — Challenge 001 churn",
    metaDescription:
      "Contexto e análise do diagnóstico de churn da RavenStack: cinco tabelas, label canônico e prioridade por impacto.",
    headline: "O churn não é a taxa.",
    headlineMuted: "É o cruzamento.",
    paragraphs: [
      "A RavenStack é um SaaS B2B com cerca de 500 contas. O CEO vê o churn subir. O CS diz que a satisfação está bem. O Produto diz que o uso cresceu. A pergunta do challenge é o que sobra quando essas três frases encontram as cinco tabelas.",
      "O contrato cruza contas, assinaturas, uso, tickets e eventos de churn por account_id e subscription_id. O label canônico é a linha em churn_events. A coluna accounts.churn_flag diverge e não substitui o evento.",
      "O Lab 04 lê um snapshot com churn_flag: 390 contas ativas e taxa de 22,0%. Essa leitura serve para comparar segmentos. Ela não é a causa raiz. A causa só aparece no join, e a prioridade junta taxa, volume e receita.",
    ],
    stats: [
      { value: "500", label: "Contas RavenStack", hint: "SaaS B2B no brief" },
      { value: "5", label: "Tabelas no cruzamento", hint: "uma tabela só fica fora" },
      { value: "22,0%", label: "Taxa no snapshot", hint: "Lab 04 · churn_flag" },
      { value: "390", label: "Contas ativas", hint: "mesmo snapshot" },
    ],
    signalTitle: "A taxa alta nem sempre é o problema.",
    signalBody:
      "Recortes do Lab 04, calculados com churn_flag. Servem para ver onde o volume muda a prioridade. O label canônico do challenge continua sendo churn_events.",
    cards: [
      {
        id: "downgrade",
        short: "movimento",
        title: "Só downgrade",
        body: "Contas que apenas reduziram o plano têm a maior taxa do grupo de movimento. Upgrade não é retenção automática: quem subiu ainda churnou 23,7%.",
        metric: "30,0% de churn",
      },
      {
        id: "trial",
        short: "entrada",
        title: "Trial contra pago direto",
        body: "Quem entra por trial churnou acima de quem entrou já pagando, e os dois ficam perto da taxa geral. Onboarding de trial é risco extra, não o único.",
        metric: "25,8% trial · 21,1% direto",
      },
      {
        id: "geo",
        short: "país",
        title: "Alemanha contra Estados Unidos",
        body: "A Alemanha tem a taxa mais alta. Os Estados Unidos têm o maior número de contas que saíram. Campanha de retenção que segue só a taxa escolhe o mercado errado.",
        metric: "32,0% DE · 68 contas US",
      },
      {
        id: "industry",
        short: "indústria",
        title: "FinTech e DevTools",
        body: "FinTech concentra o maior ARR ativo. DevTools junta ARR relevante com a maior taxa entre as indústrias grandes. Impacto é taxa vezes receita, não o pico isolado.",
        metric: "ARR × taxa",
      },
    ],
    cutTitle: "O que entra no diagnóstico.",
    cutBody:
      "O corte segue o contrato do challenge: cruzar as cinco tabelas, nomear segmentos com conta, e propor ação com impacto. O atalho de uma coluna só sai.",
    rows: [
      {
        id: "join",
        label: "Join das cinco tabelas",
        detail: "contas, assinatura, uso, tickets, eventos",
        keep: true,
      },
      {
        id: "event",
        label: "Label = churn_events",
        detail: "linha de evento, não a flag da conta",
        keep: true,
      },
      {
        id: "impact",
        label: "Prioridade por impacto",
        detail: "taxa, volume e ARR no mesmo recorte",
        keep: true,
      },
      {
        id: "flag",
        label: "churn_flag como verdade",
        detail: "diverge do evento; snapshot, não causa",
        keep: false,
      },
      {
        id: "one-table",
        label: "Ler uma tabela só",
        detail: "fora do contrato do brief",
        keep: false,
      },
      {
        id: "csat",
        label: "“A satisfação caiu”",
        detail: "sem uso × tickets × receita",
        keep: false,
      },
    ],
    analysisMuted: "Mesmas contas, outra pergunta.",
    lenses: [
      {
        id: "cause",
        label: "Causa",
        subtitle: "além do óbvio",
        lead: "Satisfação estável e uso em alta não fecham o caso. A causa que o CEO consegue usar é a que sobrevive ao cruzamento — canal, movimento de plano e ticket — e não a média da base.",
        points: [
          "Testar “o uso cresceu” por segmento, não na média.",
          "Separar correlação de causa: downgrade acompanha saída, não prova sozinho o motivo.",
          "O snapshot de 22,0% orienta a busca. O evento confirma quem saiu.",
        ],
      },
      {
        id: "segments",
        label: "Segmentos",
        subtitle: "taxa e tamanho",
        lead: "O mapa de ciclo de vida do Lab 04 aponta Direct Paid → Enterprise → Upgraded: taxa alta e segmento grande. Trial pequeno com taxa alta perde prioridade para quem concentra conta e receita.",
        points: [
          "Downgrade isolado: 30,0% no snapshot.",
          "Estados Unidos: maior volume de saída, taxa 23,4%.",
          "DevTools: ARR ativo com a taxa mais alta entre indústrias grandes.",
        ],
      },
      {
        id: "actions",
        label: "Ações",
        subtitle: "dono e impacto",
        lead: "A ação útil nomeia o recorte, a lista de contas e o que muda nesta semana. “Melhorar a experiência” não entra. Conta de receita alta não pesa igual a conta pequena.",
        points: [
          "Reter primeiro onde taxa, volume e ARR se encontram.",
          "Tratar upgrade que não segurou o cliente como falha de expectativa, não como vitória.",
          "Playbook de CS em cima de account_id, com ARR ao lado.",
        ],
      },
    ],
  },
  {
    code: "002",
    slug: "support",
    menuLabel: "002 support",
    path: "/research-challenge-002",
    modelPath: "/model-challenge-002",
    aboutPath: "/about-challenge-002",
    imagePath: "/model-2-challenge-002",
    metaTitle: "Pesquisa — Challenge 002 support",
    metaDescription:
      "Contexto e análise operacional do suporte: 8.469 tickets, horas derivadas só em Closed, e o que não automatizar.",
    headline: "Onde o fluxo trava.",
    headlineMuted: "Em horas, não em feeling.",
    paragraphs: [
      "O Diretor de Operações pede três coisas: onde se perde tempo, o que a satisfação acompanha, e quanto disso volta em horas. A saída é diagnóstico com número, mais uma proposta de automação que deixa uma zona humana explícita.",
      "No disco há 8.469 tickets e 17 colunas. O brief fala em cerca de 30 mil por ano. O CSV ganha. Ticket Type tem cinco valores. Time to Resolution é data e hora, não uma coluna de horas.",
      "Horas de resolução são TTR menos o primeiro response, e só em tickets Closed. O segundo dataset, com Topic_group, não está neste disco. Sem ele não há ground truth local para um classificador de oito classes.",
    ],
    stats: [
      { value: "8.469", label: "Tickets no CSV", hint: "o brief dizia ~30 mil" },
      { value: "17", label: "Colunas", hint: "Dataset 1" },
      { value: "5", label: "Tipos de ticket", hint: "Ticket Type" },
      { value: "Closed", label: "Onde CSAT existe", hint: "horas só nesse status" },
    ],
    signalTitle: "O relógio não está na coluna.",
    signalBody:
      "O sinal operacional depende de derivar horas e de restringir satisfação aos tickets encerrados. Ler o datetime cru, ou a base inteira, mistura fila aberta com trabalho já feito.",
    cards: [
      {
        id: "hours",
        short: "tempo",
        title: "Horas são diferença",
        body: "Time to Resolution chega como datetime. A duração comparável é o intervalo até o primeiro response, e tickets com diferença negativa precisam de regra explícita — o kernel trata virada de dia.",
        metric: "TTR − FRT · Closed",
      },
      {
        id: "status",
        short: "status",
        title: "CSAT não é da fila aberta",
        body: "Customer Satisfaction Rating e o tempo de resolução só fazem sentido em Closed. Incluir o restante puxa a média com ticket que ainda não acabou.",
        metric: "métrica só em Closed",
      },
      {
        id: "type",
        short: "tipo",
        title: "Cinco tipos, não um tema",
        body: "O gargalo que o brief pede é a combinação canal × prioridade × tipo. Um tipo médio esconde a célula que concentra o pior tempo.",
        metric: "5 valores de Ticket Type",
      },
      {
        id: "dataset-2",
        short: "texto",
        title: "Sem Topic_group local",
        body: "O zip do challenge repetiu o mesmo CSV. Dá para diagnosticar a operação no Dataset 1. Não dá para treinar as oito classes sem o arquivo que traz o rótulo.",
        metric: "Dataset 2 ausente",
      },
    ],
    cutTitle: "O que a automação pode tocar.",
    cutBody:
      "Automatizar o que o texto e o tempo sustentam. Deixar com gente o que o dado não separa, e não publicar nome ou e-mail de cliente.",
    rows: [
      {
        id: "derived-hours",
        label: "Horas derivadas em Closed",
        detail: "TTR − primeiro response",
        keep: true,
      },
      {
        id: "cell",
        label: "Gargalo na combinação",
        detail: "canal × prioridade × tipo",
        keep: true,
      },
      {
        id: "human",
        label: "Fila que continua humana",
        detail: "julgamento que o dado não cobre",
        keep: true,
      },
      {
        id: "thirty-k",
        label: "Base de ~30 mil",
        detail: "o arquivo tem 8.469 linhas",
        keep: false,
      },
      {
        id: "topic",
        label: "Topic_group neste disco",
        detail: "não há ground truth local",
        keep: false,
      },
      {
        id: "pii",
        label: "Nome e e-mail no entregável",
        detail: "PII — agregar antes de mostrar",
        keep: false,
      },
    ],
    analysisMuted: "Mesmos tickets, outra decisão.",
    lenses: [
      {
        id: "bottleneck",
        label: "Gargalo",
        subtitle: "piores tempos",
        lead: "O fluxo trava numa célula, não num canal inteiro. A leitura útil é o pior tempo de resolução na combinação de canal, prioridade e tipo, em horas já derivadas.",
        points: [
          "Comparar só tickets Closed.",
          "Tratar datetime negativo como regra, não como lixo silencioso.",
          "Quantificar a fatia de horas recuperável, não a média global.",
        ],
      },
      {
        id: "csat",
        label: "Satisfação",
        subtitle: "o que move a nota",
        lead: "A nota acompanha tempo, canal ou tipo — a resposta tem que sair dos Closed, com o recorte na mesa. “Demora incomoda” sem a célula não orienta a fila.",
        points: [
          "CSAT ausente fora de Closed não entra na média.",
          "Separar primeiro response do tempo até resolver.",
          "O tipo do ticket muda o que é espera aceitável.",
        ],
      },
      {
        id: "automation",
        label: "Automação",
        subtitle: "e o que fica humano",
        lead: "Classificar, rotear e sugerir resposta cabem onde o padrão se repete. Critical e o caso ambíguo continuam com pessoa. Sem o Dataset 2, o protótipo de oito classes não tem como ser medido aqui.",
        points: [
          "Descrever o fluxo: entra o ticket, atua o modelo, entra o humano.",
          "Nomear um tipo que não deve ser delegado, com exemplo agregado.",
          "Não commitar dump com Customer Name ou Customer Email.",
        ],
      },
    ],
  },
  {
    code: "003",
    slug: "lead",
    menuLabel: "003 lead",
    path: "/research-challenge-003",
    modelPath: "/model-challenge-003",
    aboutPath: "/about-challenge-003",
    imagePath: "/model-2-challenge-003",
    metaTitle: "Pesquisa — Challenge 003 lead",
    metaDescription:
      "Contexto e análise do lead scorer: pipe aberto com score explicável, sem ordenar por close_value.",
    headline: "Um score que o vendedor abre.",
    headlineMuted: "Não a fila por valor.",
    paragraphs: [
      "A Head de RevOps quer uma ferramenta que o vendedor usa no pipe aberto. O Lab 04 mede se campos do CRM separam Won de Lost. Essa lógica informa o score. Ela não é a entrega: o vendedor não prioriza negócio já fechado.",
      "O disco traz 85 contas, 7 produtos, 35 times e 8.800 oportunidades. Stages do contrato: Prospecting, Engaging, Won, Lost. close_value nulo no pipe aberto não é zero, e zero no histórico marca Lost.",
      "GTXPro no arquivo não encontra GTX Pro na tabela de produtos. 1.425 deals abertos estão sem account. Normalizar a chave e tratar nulo são parte do score, não um rodapé.",
    ],
    stats: [
      { value: "8.800", label: "Oportunidades", hint: "sales_pipeline" },
      { value: "85", label: "Contas", hint: "accounts" },
      { value: "1.425", label: "Abertas sem conta", hint: "account nulo" },
      { value: "7", label: "Produtos", hint: "GTXPro ≠ GTX Pro" },
    ],
    signalTitle: "O valor de fechamento mente no aberto.",
    signalBody:
      "Ordenar o pipe por close_value coloca no topo o que ainda não tem valor, ou trata zero como perdido. O score precisa de outra base e de uma frase que o vendedor leia.",
    cards: [
      {
        id: "open-pipe",
        short: "aberto",
        title: "Pipe aberto é o produto",
        body: "Won e Lost ensinam o ranking. A tela que o vendedor abre lista o que ainda está em Prospecting ou Engaging, filtrado pelo sales_agent.",
        metric: "score no aberto",
      },
      {
        id: "close-value",
        short: "valor",
        title: "Nulo não é zero",
        body: "No pipe aberto, close_value vem vazio. No histórico, 0 corresponde a Lost. Usar um no lugar do outro inverte a fila.",
        metric: "0 = Lost no histórico",
      },
      {
        id: "gtx",
        short: "produto",
        title: "GTXPro não junta",
        body: "O CSV grava GTXPro. A dimensão de produto espera GTX Pro. Sem normalizar depois da carga, esse produto some do join.",
        metric: "1.480 linhas GTXPro",
      },
      {
        id: "account",
        short: "conta",
        title: "Deal sem conta",
        body: "1.425 oportunidades abertas não têm account. Features de setor e tamanho da conta não existem ali. O score tem que dizer isso, não imputar em silêncio.",
        metric: "account nulo",
      },
    ],
    cutTitle: "O que o ranking pode usar.",
    cutBody:
      "Entra o que muda a ordem com um motivo legível. Sai o atalho de ordenar pelo valor de fechamento e a chave de produto quebrada.",
    rows: [
      {
        id: "score",
        label: "Score no pipe aberto",
        detail: "Prospecting e Engaging, não o já resolvido",
        keep: true,
      },
      {
        id: "why",
        label: "Porquê ao lado do número",
        detail: "o vendedor lê os fatores",
        keep: true,
      },
      {
        id: "agent",
        label: "Filtro por sales_agent",
        detail: "“o meu pipe”, não a base inteira",
        keep: true,
      },
      {
        id: "sort-value",
        label: "Ordenar por close_value",
        detail: "não é lógica de scoring",
        keep: false,
      },
      {
        id: "zero",
        label: "Tratar nulo como 0",
        detail: "0 no histórico é Lost",
        keep: false,
      },
      {
        id: "gtx-raw",
        label: "GTXPro sem normalizar",
        detail: "não encontra GTX Pro",
        keep: false,
      },
    ],
    analysisMuted: "Mesmo CRM, outro uso.",
    lenses: [
      {
        id: "score",
        label: "Score",
        subtitle: "além do valor",
        lead: "O ranking aprende em Won contra Lost e devolve uma ordem para o que ainda está aberto. Stage, tempo no pipe, conta, produto e vendedor são o ponto de partida. O que passa é o fator que os dados sustentam além disso.",
        points: [
          "AUC no Lab 04 mede se Won fica acima de Lost no holdout.",
          "A ferramenta não mostra só o já ganho.",
          "Sem score, ordenar por valor falha o brief.",
        ],
      },
      {
        id: "why",
        label: "Explicação",
        subtitle: "três fatores",
        lead: "O vendedor precisa entender por que um deal está no topo. A frase cita o recorte — stage, dias, conta — e não um coeficiente solto.",
        points: [
          "Cada linha do pipe aberto carrega score e why.",
          "Conta ausente aparece como limite, não como setor inventado.",
          "Produto só entra depois da chave GTX Pro.",
        ],
      },
      {
        id: "limits",
        label: "Limites",
        subtitle: "o que não faz",
        lead: "A solução não prevê o valor que ainda não existe e não substitui o vendedor no deal sem conta. Escalar pede a chave estável e o pipe aberto sempre separado do histórico.",
        points: [
          "Won/Lost é treino. Aberto é a fila.",
          "1.425 deals abertos não têm conta para enriquecer.",
          "Setup da ferramenta fica no Lab 03, não no notebook de experimento.",
        ],
      },
    ],
  },
  {
    code: "004",
    slug: "social",
    menuLabel: "004 social",
    path: "/research-challenge-004",
    modelPath: "/model-challenge-004",
    aboutPath: "/about-challenge-004",
    imagePath: "/model-2-challenge-004",
    metaTitle: "Pesquisa — Challenge 004 social",
    metaDescription:
      "Contexto e análise de engajamento: 52.214 posts, taxa derivada, e patrocínio sem custo no arquivo.",
    headline: "Engajamento com controle.",
    headlineMuted: "A taxa isolada mente.",
    paragraphs: [
      "O Head de Marketing quer o que gera engajamento de verdade, se patrocinar vale, e uma estratégia: onde concentrar, o que parar, o que fazer nesta semana. “Vídeo performa melhor que imagem” não conta como achado.",
      "O arquivo tem 52.214 posts e 27 colunas. Não existe engagement_rate. Qualquer taxa é derivada. As métricas de engajamento do dump são quase constantes, perto de 0,199 por view. Audiência chega como faixa, não como lista de pessoas.",
      "creator_name não é a chave do creator. O CSV não traz custo de patrocínio. Comparar orgânico e patrocinado sem controle, ou inventar ROI em dinheiro, sai do que o arquivo sustenta.",
    ],
    stats: [
      { value: "52.214", label: "Posts", hint: "uma tabela" },
      { value: "27", label: "Colunas", hint: "sem engagement_rate" },
      { value: "≈ 0,199", label: "Engajamento / view", hint: "quase constante no dump" },
      { value: "0", label: "Custo de sponsor", hint: "coluna ausente" },
    ],
    signalTitle: "O óbvio não separa os posts.",
    signalBody:
      "Com a taxa quase plana, a diferença útil aparece no recorte — plataforma, formato, categoria, faixa de creator — e na comparação orgânico contra patrocinado com o mesmo controle.",
    cards: [
      {
        id: "rate",
        short: "taxa",
        title: "A taxa não vem pronta",
        body: "O Lab 04 deriva engajamento por follower_count. A leitura do disco também anota engajamento por view perto de 0,199, quase sem variação. As duas contas precisam ser nomeadas. Nenhuma é coluna nativa.",
        metric: "derivar e dizer como",
      },
      {
        id: "audience",
        short: "audiência",
        title: "Audiência é faixa",
        body: "O perfil que mais engaja é um bucket, não um JSON de pessoas. Dá para cruzar faixa com plataforma e formato. Não dá para descrever um indivíduo.",
        metric: "bucket, não pessoa",
      },
      {
        id: "creator",
        short: "creator",
        title: "Nome não é identificador",
        body: "creator_name não corresponde um para um a creator_id. Agregar pelo nome mistura criadores e infla o “top performer”.",
        metric: "creator_id é a chave",
      },
      {
        id: "sponsor",
        short: "sponsor",
        title: "Patrocínio sem preço",
        body: "Dá para comparar alcance e engajamento de orgânico e patrocinado. Não dá para falar custo implícito em moeda: essa coluna não está no arquivo.",
        metric: "sem custo no CSV",
      },
    ],
    cutTitle: "O que a estratégia pode afirmar.",
    cutBody:
      "Entra o recorte com controle. Sai a frase genérica de formato e qualquer número de dinheiro que o arquivo não tem.",
    rows: [
      {
        id: "derived",
        label: "Taxa derivada, nomeada",
        detail: "dizer o denominador: view ou follower",
        keep: true,
      },
      {
        id: "control",
        label: "Orgânico vs. patrocinado com controle",
        detail: "mesmo formato, faixa e plataforma",
        keep: true,
      },
      {
        id: "bucket",
        label: "Audiência em faixa",
        detail: "bucket por plataforma e formato",
        keep: true,
      },
      {
        id: "native-rate",
        label: "engagement_rate nativo",
        detail: "a coluna não existe",
        keep: false,
      },
      {
        id: "name-pk",
        label: "creator_name como chave",
        detail: "não é 1:1 com creator_id",
        keep: false,
      },
      {
        id: "cost",
        label: "ROI em dinheiro do sponsor",
        detail: "não há custo no CSV",
        keep: false,
      },
    ],
    analysisMuted: "Mesmos posts, outra decisão.",
    lenses: [
      {
        id: "engagement",
        label: "Engajamento",
        subtitle: "além do formato",
        lead: "O que gera engajamento é a combinação de plataforma, tipo, categoria e faixa de creator. O formato sozinho — vídeo contra imagem — é a linha de base que o brief já descartou.",
        points: [
          "Comparar dentro da plataforma, não na média global.",
          "Usar a faixa de audiência, não um perfil inventado.",
          "Registrar posts sem engajamento: survivorship distorce o topo.",
        ],
      },
      {
        id: "sponsor",
        label: "Patrocínio",
        subtitle: "quando vale",
        lead: "Patrocinar vale no recorte em que o patrocinado supera o orgânico depois do controle de formato e faixa. Sem custo no arquivo, a política fala de condição e de perfil, não de reais por view.",
        points: [
          "Mostrar o cru e o controlado lado a lado.",
          "Threshold de seguidores só se a faixa do CSV sustentar.",
          "Não preencher custo que não veio no dump.",
        ],
      },
      {
        id: "strategy",
        label: "Estratégia",
        subtitle: "onde concentrar e o que parar",
        lead: "A recomendação nomeia plataforma, formato, frequência e faixa, mais o que parar porque o retorno no recorte é fraco, mais um quick win desta semana.",
        points: [
          "Um lugar para concentrar esforço, com o recorte.",
          "Uma política de patrocínio com condição, não um sim genérico.",
          "Um formato ou plataforma para interromper, com o número do recorte.",
        ],
      },
    ],
  },
];

export function getStory(code: ChallengeCode): ResearchStory {
  const story = CHALLENGES.find((item) => item.code === code);
  if (!story) {
    throw new Error(`Unknown challenge ${code}`);
  }
  return story;
}
