import type { ChallengeCode } from "@/lib/research/stories";

export type RankRow = {
  name: string;
  metric: string;
  note: string;
};

export type StatCell = {
  label: string;
  value: string;
  hint: string;
};

export type ImageWorkshop = {
  code: ChallengeCode;
  path: string;
  metaTitle: string;
  metaDescription: string;
  kicker: string;
  headline: string;
  headlineMuted: string;
  lede: string;
  rankingTitle: string;
  rankingHint: string;
  ranking: RankRow[];
  entranceTitle: string;
  entrance: { name: string; detail: string }[];
  classification: { label: string; subtitle: string; body: string }[] | null;
  stats: StatCell[];
  bias: { title: string; body: string } | null;
  omitted: { section: string; reason: string }[];
};

export const IMAGE_WORKSHOPS: ImageWorkshop[] = [
  {
    code: "001",
    path: "/model-2-challenge-001",
    metaTitle: "Oficina — Challenge 001 churn",
    metaDescription:
      "A oficina de imagens não se aplica à RavenStack. O que cabe é o ranking de impacto, a entrada das cinco tabelas e o que o Lab 03 não mede.",
    kicker: "Oficina · retenção",
    headline: "Não há patch para ver.",
    headlineMuted: "Há conta, taxa e ARR.",
    lede: "O README do pacote descreve ingestão, Assistant, dashboard do CEO e o kernel de retenção. Não há imagem, rede nem holdout de classe. A oficina de /model-2 empresta o ranking e a entrada. O resto fica de fora.",
    rankingTitle: "Ranking de impacto",
    rankingHint: "Lab 04 · snapshot com churn_flag · volume antes da taxa",
    ranking: [
      { name: "Estados Unidos", metric: "68 contas", note: "maior volume de saída · taxa 23,4%" },
      { name: "Só downgrade", metric: "30,0%", note: "maior taxa de movimento · não é o maior mercado" },
      { name: "Alemanha", metric: "32,0%", note: "maior taxa de país · base menor que os EUA" },
      { name: "DevTools", metric: "ARR × taxa", note: "indústria grande com a taxa mais alta" },
    ],
    entranceTitle: "Entrada",
    entrance: [
      { name: "ravenstack_accounts", detail: "conta, plano, país, indústria" },
      { name: "ravenstack_subscriptions", detail: "ARR, downgrade, vigência" },
      { name: "ravenstack_feature_usage", detail: "uso e erro por assinatura" },
      { name: "ravenstack_support_tickets", detail: "horas e satisfação" },
      { name: "ravenstack_churn_events", detail: "label canônico · não é churn_flag" },
    ],
    classification: null,
    stats: [
      { label: "Contas", value: "500", hint: "base do brief" },
      { label: "Com evento", value: "—", hint: "tile 1 do Lab 03 conta no Run All" },
      { label: "Taxa no snapshot", value: "22,0%", hint: "churn_flag · não é o label" },
      { label: "Ativas", value: "390", hint: "mesmo snapshot" },
      { label: "Tabelas", value: "5", hint: "join obrigatório" },
      { label: "Lista acionável", value: "25", hint: "account_id no Lab 03" },
      { label: "Classificador", value: "não", hint: "diagnóstico, não score" },
      { label: "Imagem", value: "não", hint: "não há patch" },
    ],
    bias: null,
    omitted: [
      { section: "Galeria de imagens", reason: "A entrada são cinco CSVs, não 36 patches." },
      { section: "Classificação", reason: "O Lab 04 não treina rótulo. O Lab 03 lista contas." },
      { section: "Segmentação e segmentação de imagem", reason: "Não há máscara, U-Net nem pixel." },
      { section: "Acurácia, F1, ROC-AUC, precisão, recall", reason: "Não há holdout de classe." },
      { section: "Latência, parâmetros, épocas", reason: "Não há rede treinada." },
      { section: "Matriz de confusão", reason: "Não há verdadeiro positivo." },
      { section: "Curva de aprendizado", reason: "Não há época de treino." },
      { section: "Viés / variância", reason: "O recorte compara taxa e volume, não complexidade de modelo." },
    ],
  },
  {
    code: "002",
    path: "/model-2-challenge-002",
    metaTitle: "Oficina — Challenge 002 support",
    metaDescription:
      "Dois classificadores de nota em tickets Closed. Sem acurácia arquivada, sem imagem e sem matriz salva.",
    kicker: "Oficina · suporte",
    headline: "A nota é classe.",
    headlineMuted: "O ticket não é imagem.",
    lede: "O Lab 04 treina floresta e logística para Customer Satisfaction Rating em Closed. O notebook imprime acurácia e não grava o número. O Lab 03 entrega gargalo, horas e a rota humano/IA. Segmentar pixel não cabe.",
    rankingTitle: "Ranking da fila aberta",
    rankingHint: "Regra do Lab 03 · não é acurácia de rede",
    ranking: [
      { name: "HUMAN_NOW", metric: "Critical", note: "não automatizar" },
      { name: "HUMAN_REVIEW", metric: "cancelamento / reembolso", note: "descrição longa · dinheiro" },
      { name: "AI_SUGGEST", metric: "billing / product · Low–Medium", note: "único trecho com rascunho" },
      { name: "HUMAN_QUEUE", metric: "o resto", note: "pessoa na fila" },
    ],
    entranceTitle: "Entrada da floresta",
    entrance: [
      { name: "Tipo, prioridade, canal", detail: "one-hot · cinco tipos" },
      { name: "Assunto e descrição", detail: "categoria na floresta · frase no TF-IDF" },
      { name: "Idade, produto, hora da 1ª resposta", detail: "numéricos da floresta" },
      { name: "Horas de resolução", detail: "calculadas e deixadas de fora do modelo" },
    ],
    classification: [
      {
        label: "Floresta",
        subtitle: "150 árvores · 80/20 · semente 42",
        body: "Prevê a nota inteira com campos do ticket. Assunto e descrição entram como categoria. A acurácia sai no print e não fica no arquivo.",
      },
      {
        label: "Texto",
        subtitle: "TF-IDF 5.000 · logística",
        body: "A mesma nota, só com assunto e descrição. Não vê canal nem prioridade. Também sem acurácia arquivada.",
      },
    ],
    stats: [
      { label: "Acurácia", value: "—", hint: "impressa, não arquivada" },
      { label: "Score F1", value: "—", hint: "o report não foi salvo" },
      { label: "ROC-AUC", value: "—", hint: "não é a métrica deste notebook" },
      { label: "Latência", value: "—", hint: "não medida" },
      { label: "Precisão", value: "—", hint: "não arquivada" },
      { label: "Recall", value: "—", hint: "não arquivado" },
      { label: "Parâmetros", value: "150", hint: "árvores · não milhões de pesos" },
      { label: "Épocas", value: "—", hint: "floresta não tem época" },
    ],
    bias: null,
    omitted: [
      { section: "Galeria de imagens", reason: "A entrada é ticket, não patch histológico." },
      { section: "Segmentação e segmentação de imagem", reason: "Não há máscara. O recorte operacional é canal × prioridade × tipo." },
      { section: "Matriz de confusão", reason: "O classification_report é impresso e não fica no notebook." },
      { section: "Curva de aprendizado", reason: "Não há série treino/validação por época." },
      { section: "Viés / variância", reason: "Sem curva salva, não há como separar os dois." },
    ],
  },
  {
    code: "003",
    path: "/model-2-challenge-003",
    metaTitle: "Oficina — Challenge 003 lead",
    metaDescription:
      "O ranking do Lab 04 é AUC perto de 0,5. A fila do vendedor é regra com porquê, não uma rede.",
    kicker: "Oficina · CRM",
    headline: "O ranking quase empata o acaso.",
    headlineMuted: "A fila do vendedor é outra.",
    lede: "O Lab 04 pergunta se campos anteriores ao desfecho ordenam Won acima de Lost. A resposta arquivada fica perto de AUC 0,5. O Lab 03 não usa esse score: ordena o pipe aberto com regras e uma frase. Não há imagem.",
    rankingTitle: "Ranking de blocos",
    rankingHint: "Holdout temporal · regressão logística · acaso = 0,500",
    ranking: [
      { name: "Contexto", metric: "AUC ≈ 0,543", note: "maior bloco estrutural" },
      { name: "Core + vendedor", metric: "AUC ≈ 0,540", note: "melhor degrau da pilha" },
      { name: "Core", metric: "AUC ≈ 0,530", note: "sem vendedor" },
      { name: "Baseline", metric: "AUC ≈ 0,526", note: "tudo o que se sabe antes do fim" },
      { name: "Produto", metric: "AUC ≈ 0,496", note: "abaixo do acaso" },
      { name: "Firmografia", metric: "AUC ≈ 0,487", note: "abaixo do acaso" },
    ],
    entranceTitle: "Entrada do baseline",
    entrance: [
      { name: "Vendedor, produto, conta, setor", detail: "categorias anteriores ao desfecho" },
      { name: "Receita, funcionários, preço, subsidiária", detail: "numéricos" },
      { name: "Ano, mês e trimestre de engage", detail: "tempo" },
      { name: "close_value, close_date, deal_stage", detail: "fora · vazam o resultado" },
    ],
    classification: [
      {
        label: "Ranking",
        subtitle: "P(Won | x) · não é classe dura",
        body: "Won = 1 e Lost = 0 só para medir AUC. O vendedor não recebe essa probabilidade. Recebe o score de regras do Lab 03.",
      },
      {
        label: "Fila aberta",
        subtitle: "Engaging, conta, catálogo, agente, recência",
        body: "Pontos fixos e uma frase why. 1.425 abertos sem conta não entram num inner join. GTXPro só conta depois do replace.",
      },
    ],
    stats: [
      { label: "Acurácia", value: "—", hint: "não é a métrica" },
      { label: "Score F1", value: "—", hint: "sem limiar de classe" },
      { label: "ROC-AUC", value: "≈ 0,526", hint: "baseline · holdout temporal" },
      { label: "Latência", value: "—", hint: "não medida" },
      { label: "Precisão", value: "—", hint: "sem limiar" },
      { label: "Recall", value: "—", hint: "sem limiar" },
      { label: "Parâmetros", value: "logística", hint: "baseline interpretável" },
      { label: "Épocas", value: "—", hint: "max_iter, não época de rede" },
    ],
    bias: {
      title: "Viés alto, variância não é o caso",
      body: "0,526 contra 0,500 significa que o modelo quase não ordena o futuro. Empilhar conta piora (≈ 0,525). Produto e firmografia ficam abaixo do acaso. Isso é sinal fraco e atributo estático, não uma curva de rede que overfitou. Não há série de complexidade salva para desenhar viés contra variância.",
    },
    omitted: [
      { section: "Galeria de imagens", reason: "A entrada é oportunidade, conta e produto." },
      { section: "Segmentação e segmentação de imagem", reason: "Não há máscara. Stage não é pixel." },
      { section: "Matriz de confusão", reason: "A métrica é ordem, não um corte em 0,5." },
      { section: "Curva de aprendizado", reason: "Não há acurácia por época." },
    ],
  },
  {
    code: "004",
    path: "/model-2-challenge-004",
    metaTitle: "Oficina — Challenge 004 social",
    metaDescription:
      "Cinco quintis de taxa derivada e um XGBoost. Sem número de acurácia arquivado e sem segmentação de imagem.",
    kicker: "Oficina · social",
    headline: "O post vira quintil.",
    headlineMuted: "A imagem do tecido não entra.",
    lede: "O Lab 04 corta (likes + 2×shares + 0,5×comments) / follower_count em cinco faixas e treina um XGBoost com texto e metadados, separado por creator_id. A acurácia é impressa e não fica no arquivo. O Lab 03 decide com taxa por view controlada. Não há custo de sponsor nem máscara.",
    rankingTitle: "O que o dashboard ordena",
    rankingHint: "Lab 03 · taxa por view · célula com pelo menos 30 posts",
    ranking: [
      { name: "Concentrar", metric: "maior eng_per_view", note: "plataforma × tipo × categoria × faixa × sponsor" },
      { name: "Patrocinar", metric: "só se superar o orgânico", note: "no mesmo recorte · sem custo no CSV" },
      { name: "Parar", metric: "piores células", note: "audiência em bucket · tile 4" },
      { name: "Não usar", metric: "vídeo > imagem", note: "o brief já descartou essa frase" },
    ],
    entranceTitle: "Entrada da fusão",
    entrance: [
      { name: "Texto", detail: "descrição, hashtags, comentários · TF-IDF 15.000" },
      { name: "Metadados", detail: "hora, fim de semana, seguidores, sponsor, disclosure" },
      { name: "One-hot", detail: "plataforma, tipo, categoria, língua, faixa de audiência" },
      { name: "Grupo", detail: "creator_id no split · creator_name não é chave" },
    ],
    classification: [
      {
        label: "Fusão",
        subtitle: "XGBoost · 300 árvores · 5 classes",
        body: "multi:softprob, profundidade 6, learning rate 0,05. O alvo é o quintil da taxa por seguidor, não a view.",
      },
      {
        label: "Split",
        subtitle: "GroupShuffle por creator_id",
        body: "30% saem do treino e essa fatia se divide ao meio em validação e teste. O mesmo creator não atravessa.",
      },
    ],
    stats: [
      { label: "Acurácia", value: "—", hint: "impressa no teste, não arquivada" },
      { label: "Score F1", value: "—", hint: "report não salvo" },
      { label: "ROC-AUC", value: "—", hint: "o código calcula e não grava" },
      { label: "Latência", value: "—", hint: "não medida" },
      { label: "Precisão", value: "—", hint: "não arquivada" },
      { label: "Recall", value: "—", hint: "não arquivado" },
      { label: "Parâmetros", value: "300", hint: "árvores · depth 6 · lr 0,05" },
      { label: "Épocas", value: "—", hint: "árvore não tem época" },
    ],
    bias: null,
    omitted: [
      { section: "Galeria de imagens", reason: "O post é linha de CSV, não patch RGB." },
      { section: "Segmentação e segmentação de imagem", reason: "Faixa de audiência não é máscara de U-Net." },
      { section: "Matriz de confusão", reason: "O heatmap é desenhado no Run All e não fica no arquivo." },
      { section: "Curva de aprendizado", reason: "Não há perda por rodada salva." },
      { section: "Viés / variância", reason: "Sem curva de validação arquivada." },
    ],
  },
];

export function getImageWorkshop(code: ChallengeCode): ImageWorkshop {
  const story = IMAGE_WORKSHOPS.find((item) => item.code === code);
  if (!story) {
    throw new Error(`Unknown image workshop ${code}`);
  }
  return story;
}
