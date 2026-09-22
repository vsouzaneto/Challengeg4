import type { ChallengeCode } from "@/lib/research/stories";

export type ModelVariant = {
  id: string;
  name: string;
  metric: string;
  summary: string;
  sees: string[];
  ignores: string[];
  output: string;
  stats: { label: string; value: string; hint: string }[];
  explain: string;
  limits: string[];
};

export type ModelWorkshopStory = {
  code: ChallengeCode;
  path: string;
  researchHref: string;
  notebook: string;
  metaTitle: string;
  metaDescription: string;
  kicker: string;
  headline: string;
  headlineMuted: string;
  lede: string;
  variants: ModelVariant[];
};

export const MODEL_WORKSHOPS: ModelWorkshopStory[] = [
  {
    code: "001",
    path: "/model-challenge-001",
    researchHref: "/research-challenge-001#analysis",
    notebook: "notebook-data-001-churn/04_ANALISE_retention/saas-retention-revenue-risk-analytics.ipynb",
    metaTitle: "Oficina do modelo — Challenge 001 churn",
    metaDescription:
      "O Lab 04 de retenção não treina um classificador. A oficina sonda ciclo de vida, movimento de plano, coorte e país.",
    kicker: "Oficina do modelo · retenção",
    headline: "Sondar o risco.",
    headlineMuted: "Ver quem pesa na receita.",
    lede: "Este notebook não troca de kernel. Ele não ajusta um classificador. A oficina percorre os recortes que o Lab 04 usa para decidir onde a retenção age primeiro: taxa, volume e ARR no mesmo lugar. O label canônico do challenge continua sendo churn_events; os percentuais abaixo são o snapshot com churn_flag.",
    variants: [
      {
        id: "lifecycle",
        name: "Ciclo de vida",
        metric: "taxa × tamanho",
        summary:
          "Compara caminhos de entrada, plano e movimento. A taxa mais alta nem sempre é a prioridade: segmento pequeno com churn alto perde para caminho grande com taxa relevante.",
        sees: ["entrada trial ou pago", "plano", "upgrade ou downgrade", "tamanho do segmento"],
        ignores: ["um único motivo declarado como causa", "média da base inteira"],
        output: "Um mapa de prioridade. Direct Paid → Enterprise → Upgraded junta taxa alta e segmento grande.",
        stats: [
          { label: "Contas", value: "500", hint: "base RavenStack" },
          { label: "Ativas", value: "390", hint: "snapshot Lab 04" },
          { label: "Taxa geral", value: "22,0%", hint: "churn_flag" },
          { label: "Classificador", value: "não", hint: "diagnóstico, não score" },
        ],
        explain:
          "O recorte explica a prioridade pela combinação de taxa e tamanho. Não atribui a saída a uma feature isolada.",
        limits: [
          "Não produz probabilidade por account_id.",
          "Não substitui o join com churn_events.",
        ],
      },
      {
        id: "movement",
        name: "Movimento de plano",
        metric: "30,0% downgrade",
        summary:
          "Quem só reduziu o plano tem a maior taxa do grupo. Quem fez upgrade ainda sai a 23,7%. Subir de plano não é retenção garantida.",
        sees: ["só downgrade", "upgrade", "sem movimento"],
        ignores: ["satisfação declarada sem o plano", "uso médio da base"],
        output: "Downgrade isolado marca 30,0%. Upgrade marca 23,7%, acima da taxa geral de 22,0%.",
        stats: [
          { label: "Só downgrade", value: "30,0%", hint: "maior taxa do grupo" },
          { label: "Upgrade", value: "23,7%", hint: "não é vitória automática" },
          { label: "Trial", value: "25,8%", hint: "contra 21,1% pago direto" },
          { label: "Geral", value: "22,0%", hint: "linha de comparação" },
        ],
        explain:
          "O movimento de assinatura acompanha a saída. O notebook não trata isso como causa fechada.",
        limits: [
          "Downgrade pode ser sintoma de valor percebido, orçamento ou confiança.",
          "Sem o evento canônico, a taxa é leitura de snapshot.",
        ],
      },
      {
        id: "cohort",
        name: "Coorte",
        metric: "1ª data de churn",
        summary:
          "A retenção mensal usa a primeira data de churn por conta, para não contar de novo quem tem mais de um evento. O fim da observação corta o que ainda não deu tempo de medir.",
        sees: ["mês de signup", "primeira data de churn", "fim da observação"],
        ignores: ["eventos repetidos da mesma conta", "coorte ainda imatura como se fosse antiga"],
        output: "Taxa de retenção por coorte de signup, mês a mês.",
        stats: [
          { label: "Unidade", value: "conta", hint: "não o evento repetido" },
          { label: "Chave", value: "1ª saída", hint: "primeira data" },
          { label: "Eixo", value: "mês", hint: "coorte de signup" },
          { label: "Score", value: "não", hint: "curva, não probabilidade" },
        ],
        explain:
          "A coorte mostra quando a base se esvazia. Não diz qual feature empurrou a conta para fora.",
        limits: [
          "Conta com vários eventos entra uma vez.",
          "Não há AUC neste recorte.",
        ],
      },
      {
        id: "geo",
        name: "País",
        metric: "68 contas US",
        summary:
          "A Alemanha tem a taxa mais alta, 32,0%. Os Estados Unidos têm o maior volume de saída: 68 contas, taxa 23,4%. A prioridade geográfica segue o impacto, não o pico.",
        sees: ["país", "contas que saíram", "taxa no país"],
        ignores: ["país pequeno com taxa alta como se fosse o maior risco de receita"],
        output: "Fila de mercados por volume de saída, com a taxa ao lado.",
        stats: [
          { label: "Alemanha", value: "32,0%", hint: "maior taxa" },
          { label: "Estados Unidos", value: "68", hint: "maior volume de saída" },
          { label: "Taxa US", value: "23,4%", hint: "abaixo da Alemanha" },
          { label: "Regra", value: "impacto", hint: "volume antes do pico" },
        ],
        explain:
          "O país entra como onde agir, não como explicação cultural da saída.",
        limits: [
          "Taxa alta em base pequena não sobe na fila.",
          "ARR por país não está neste cartão; o notebook separa indústria para receita.",
        ],
      },
    ],
  },
  {
    code: "002",
    path: "/model-challenge-002",
    researchHref: "/research-challenge-002#analysis",
    notebook:
      "notebook-process-002-support/04_ANALISE_supportiq/supportiq-customer-support-intelligence-platform.ipynb",
    metaTitle: "Oficina do modelo — Challenge 002 support",
    metaDescription:
      "Dois classificadores de satisfação em tickets Closed: floresta com campos do ticket e regressão logística no texto.",
    kicker: "Oficina do modelo · satisfação",
    headline: "Sondar a nota.",
    headlineMuted: "Ver o que o ticket carrega.",
    lede: "Os dois modelos preveem Customer Satisfaction Rating só em tickets Closed. O notebook imprime acurácia e não grava o número no arquivo: esta oficina não inventa o resultado. O que está escrito é o contrato de treino.",
    variants: [
      {
        id: "forest",
        name: "Floresta aleatória",
        metric: "150 árvores",
        summary:
          "Pipeline com imputação, one-hot e RandomForestClassifier. Split estratificado 80/20, random_state 42. O alvo é a nota inteira.",
        sees: [
          "idade e gênero",
          "produto",
          "tipo, prioridade e canal",
          "assunto e descrição como categoria",
          "tamanho do texto, ano e mês da compra, hora da primeira resposta",
        ],
        ignores: [
          "resolution_hours, calculada e deixada de fora da lista",
          "tickets que não estão Closed",
          "Topic_group, ausente neste disco",
        ],
        output: "Uma classe de nota para o ticket de teste. A acurácia é impressa no Run All e não está salva no notebook.",
        stats: [
          { label: "Árvores", value: "150", hint: "n_estimators" },
          { label: "Teste", value: "20%", hint: "stratify na nota" },
          { label: "Semente", value: "42", hint: "random_state" },
          { label: "Acurácia", value: "—", hint: "impressa, não arquivada" },
        ],
        explain:
          "A floresta vê campos do ticket e o texto inteiro como categoria, não como frase. Assunto e descrição em one-hot não explicam uma palavra.",
        limits: [
          "Horas de resolução não entram, embora tenham sido calculadas.",
          "One-hot de descrição não generaliza para texto novo.",
          "Sem o Dataset 2 não há rótulo de oito classes.",
        ],
      },
      {
        id: "tfidf",
        name: "Logística no texto",
        metric: "TF-IDF 5.000",
        summary:
          "Assunto e descrição viram um campo. TfidfVectorizer com 5.000 termos, unigramas e bigramas, stop words em inglês. LogisticRegression com max_iter 1.000.",
        sees: ["ticket_text", "nota inteira como alvo"],
        ignores: [
          "canal, prioridade e tipo",
          "idade e produto",
          "horas de resolução",
        ],
        output: "A mesma nota, agora só a partir do texto. Outro print de acurácia, também sem valor arquivado.",
        stats: [
          { label: "Termos", value: "5.000", hint: "max_features" },
          { label: "N-gramas", value: "1–2", hint: "inglês" },
          { label: "Iterações", value: "1.000", hint: "max_iter" },
          { label: "Split", value: "80/20", hint: "mesma semente 42" },
        ],
        explain:
          "O coeficiente do termo diz o que o texto empurra na nota. Não diz se a fila demorou.",
        limits: [
          "Texto sozinho não vê prioridade nem canal.",
          "Os dois modelos não estão comparados com um número salvo.",
        ],
      },
    ],
  },
  {
    code: "003",
    path: "/model-challenge-003",
    researchHref: "/research-challenge-003#analysis",
    notebook:
      "notebook-build-003-lead-scorer/04_ANALISE_crm/0-2-do-crm-fields-actually-predict-deal-outcomes.ipynb",
    metaTitle: "Oficina do modelo — Challenge 003 lead",
    metaDescription:
      "Regressão logística que ranqueia Won contra Lost. O holdout temporal fica perto de AUC 0,5.",
    kicker: "Oficina do modelo · ranking",
    headline: "Sondar o ranking.",
    headlineMuted: "Ver o que ele não separa.",
    lede: "A pergunta do notebook é estreita: campos observáveis antes do desfecho separam Won de Lost em dados futuros? O score é P(Won | x). A métrica é ROC AUC. O pipe aberto não entra no treino. close_value, close_date e deal_stage ficam de fora.",
    variants: [
      {
        id: "baseline",
        name: "Baseline",
        metric: "AUC ≈ 0,526",
        summary:
          "Regressão logística com o que se sabe enquanto o deal está ativo: vendedor, produto, conta, setor, escritório, série, gestor, região, tempo de engage e subsidiária.",
        sees: [
          "sales_agent, product, account, sector",
          "office_location, series, manager, regional_office",
          "year_established, revenue, employees, sales_price",
          "is_subsidiary, engage_year, engage_month, engage_quarter",
        ],
        ignores: ["opportunity_id", "deal_stage", "close_date", "close_value"],
        output: "Probabilidade de Won no holdout temporal. AUC ≈ 0,526, pouco acima de 0,5.",
        stats: [
          { label: "AUC", value: "≈ 0,526", hint: "holdout temporal" },
          { label: "Acaso", value: "0,500", hint: "ranking aleatório" },
          { label: "Modelo", value: "logística", hint: "baseline interpretável" },
          { label: "Alvo", value: "Won = 1", hint: "Lost = 0" },
        ],
        explain:
          "O notebook lê o resultado como pouco poder de ordenação fora da amostra. Atributo estático, deriva no tempo e identidade de conta ou vendedor são as hipóteses de limite — não uma causa fechada.",
        limits: [
          "Não ranqueia o pipe aberto. Isso é o Lab 03.",
          "AUC perto de 0,5 não vira score de produção sozinho.",
        ],
      },
      {
        id: "core-rep",
        name: "Core + vendedor",
        metric: "AUC ≈ 0,540",
        summary:
          "Empilhar o vendedor em cima do núcleo sobe um pouco o AUC. É o melhor degrau da pilha core, não um salto.",
        sees: ["núcleo do deal", "identidade do vendedor"],
        ignores: ["close_value", "desfecho já conhecido"],
        output: "AUC ≈ 0,540 no mesmo tipo de comparação.",
        stats: [
          { label: "Core", value: "≈ 0,530", hint: "sem vendedor" },
          { label: "Core + rep", value: "≈ 0,540", hint: "melhor degrau" },
          { label: "Com conta", value: "≈ 0,525", hint: "a conta não soma" },
          { label: "Acaso", value: "0,500", hint: "referência" },
        ],
        explain:
          "O vendedor acrescenta um pouco de ordem. A conta, por cima, não melhora o holdout.",
        limits: ["Identidade de vendedor generaliza mal para gente nova.", "Ainda é logística, não um modelo mais flexível."],
      },
      {
        id: "context",
        name: "Contexto",
        metric: "AUC ≈ 0,543",
        summary:
          "Entre os blocos estruturais, contexto é o que mais separa. Produto e firmografia ficam abaixo do acaso.",
        sees: ["bloco de contexto do experimento"],
        ignores: ["produto como bloco único", "firmografia como bloco único", "valor realizado"],
        output: "Contexto ≈ 0,543. Produto ≈ 0,496. Firmografia ≈ 0,487. Tudo estrutural ≈ 0,530.",
        stats: [
          { label: "Contexto", value: "≈ 0,543", hint: "maior bloco" },
          { label: "Estrutural", value: "≈ 0,530", hint: "todos os blocos" },
          { label: "Produto", value: "≈ 0,496", hint: "abaixo do acaso" },
          { label: "Firmografia", value: "≈ 0,487", hint: "abaixo do acaso" },
        ],
        explain:
          "Juntar blocos fracos não cria sinal. Produto e tamanho da conta, sozinhos, não ordenam Won acima de Lost.",
        limits: [
          "O maior AUC do notebook continua perto de meio.",
          "Falta histórico de interação, mudança de stage e recência — o próprio texto aponta isso.",
        ],
      },
    ],
  },
  {
    code: "004",
    path: "/model-challenge-004",
    researchHref: "/research-challenge-004#analysis",
    notebook: "notebook-marketing-004-social/04_ANALISE_social/social-media-engagement-analyser.ipynb",
    metaTitle: "Oficina do modelo — Challenge 004 social",
    metaDescription:
      "XGBoost de cinco classes sobre engajamento por seguidor, com texto TF-IDF e metadados, separado por creator_id.",
    kicker: "Oficina do modelo · engajamento",
    headline: "Sondar o quintil.",
    headlineMuted: "Ver o post sem repetir o creator.",
    lede: "Não há engagement_rate no CSV. O notebook cria a taxa como (likes + 2×shares + 0,5×comments) / follower_count e corta em cinco quintis. Um XGBoost funde TF-IDF e metadados. O split é por creator_id, para o mesmo creator não vazar do treino para o teste. A acurácia é impressa e não está arquivada.",
    variants: [
      {
        id: "fusion",
        name: "Fusão",
        metric: "300 árvores",
        summary:
          "XGBClassifier multi:softprob, cinco classes, profundidade 6, learning rate 0,05, subsample e colsample 0,9. A matriz é TF-IDF empilhado nos metadados.",
        sees: [
          "TF-IDF do texto, até 15.000 termos",
          "hora, dia, fim de semana, tamanho do texto, hashtags",
          "log de seguidores, creator grande, patrocínio, disclosure",
          "polaridade e subjetividade",
          "plataforma, tipo, categoria, língua e faixas de audiência",
        ],
        ignores: [
          "engagement_rate nativo",
          "custo de patrocínio",
          "creator_name como chave",
          "likes crus como alvo — entram na taxa, não como feature solta do rótulo",
        ],
        output: "Classe 0 a 4 no teste. Acurácia de validação e de teste são impressas no Run All.",
        stats: [
          { label: "Árvores", value: "300", hint: "max_depth 6" },
          { label: "Taxa", value: "0,05", hint: "learning_rate" },
          { label: "Classes", value: "5", hint: "quintis da taxa" },
          { label: "Acurácia", value: "—", hint: "impressa, não arquivada" },
        ],
        explain:
          "A classe é um quintil da taxa derivada, não um engajamento absoluto. Dois posts no mesmo quintil podem ter volumes muito diferentes.",
        limits: [
          "Quintil força faixas quase do mesmo tamanho. Não é um limiar de negócio.",
          "Sem custo, o modelo não diz se patrocinar vale em dinheiro.",
        ],
      },
      {
        id: "text",
        name: "Texto",
        metric: "TF-IDF 15.000",
        summary:
          "O texto junta descrição, hashtags e comentários. O vetorizador aprende só no treino: max_features 15.000, n-gramas 1–2, min_df 5, stop words em inglês.",
        sees: ["content_description", "hashtags", "comments_text"],
        ignores: ["plataforma e formato, que ficam no bloco de metadados", "seguidores, que já estão no denominador da taxa"],
        output: "Um bloco esparso que a fusão concatena. Não é um segundo classificador treinado à parte.",
        stats: [
          { label: "Termos", value: "15.000", hint: "max_features" },
          { label: "min_df", value: "5", hint: "termo raro sai" },
          { label: "N-gramas", value: "1–2", hint: "inglês" },
          { label: "Fit", value: "treino", hint: "val e teste só transform" },
        ],
        explain:
          "Hashtag e comentário entram na frase. A importância de um termo só existe dentro da fusão, não num modelo de texto isolado.",
        limits: ["Não há AUC só de texto neste notebook.", "Stop words em inglês cortam outras línguas do brief."],
      },
      {
        id: "split",
        name: "Split por creator",
        metric: "GroupShuffle",
        summary:
          "GroupShuffleSplit em creator_id: 30% saem do treino e essa fatia se parte ao meio em validação e teste. O mesmo creator não aparece dos dois lados.",
        sees: ["creator_id como grupo", "post como linha"],
        ignores: ["split aleatório de posts do mesmo creator", "creator_name"],
        output: "Três massas sem creator compartilhado. Tamanhos são impressos no Run All.",
        stats: [
          { label: "Fora do treino", value: "30%", hint: "primeiro split" },
          { label: "Val / teste", value: "50/50", hint: "da fatia de 30%" },
          { label: "Grupo", value: "creator_id", hint: "não o nome" },
          { label: "Semente", value: "42", hint: "os dois splits" },
        ],
        explain:
          "Separar por creator mede se o padrão atravessa gente nova. Um split por post deixaria o modelo memorizar quem posta.",
        limits: [
          "creator_name não é identificador único.",
          "Audiência continua faixa, não pessoa.",
        ],
      },
    ],
  },
];

export function getModelWorkshop(code: ChallengeCode): ModelWorkshopStory {
  const story = MODEL_WORKSHOPS.find((item) => item.code === code);
  if (!story) {
    throw new Error(`Unknown model workshop ${code}`);
  }
  return story;
}
