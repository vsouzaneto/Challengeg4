# Baseline — ChatGPT

| Campo | Valor |
|---|---|
| Data | 2026-09-16 |
| Operado por | Douglas França (conversa nova, sem contexto da submissão) |
| Entrada | Somente o brief do Challenge 004, colado como primeira mensagem (print `g1-chatgpt-00a-brief-colado.png`) |
| Como respondeu | Abriu com uma frase curta, **pesquisou em 5 sites** e só então escreveu a resposta longa ("Pensou por 1m 48s"). O texto abaixo foi copiado a partir da resposta longa, que começa em "Sim."; a abertura está no print `g1-chatgpt-00b-inicio-resposta.png`: "Esse desafio tem espaço para uma entrega muito forte, porque ele não está pedindo só 'análise de social': está testando se você consegue transformar dado bruto em decisão executiva + ferramenta recorrente. Vou estruturar a solução como se fosse uma submissão de AI Master e, se eu conseguir acessar o dataset diretamente, já avanço para os testes e findings reais." |
| Recebeu os dados? | Não. A IA pediu o CSV no final |
| Checagem numérica | `outputs/tables/g1-baseline-claims-check.csv` |

## Resposta literal

~~~~text
Sim. E antes de fechar qualquer conclusão numérica, eu faria duas correções metodológicas que podem elevar bastante a sua entrega.

O dataset original do Kaggle é explicitamente simulado, com mais de 52 mil posts e distribuição construída para representar comportamento realista. Além disso, ele possui views, likes, shares, comments_count e follower_count, mas a documentação pública não mostra custo pago por patrocínio nem receita gerada. Portanto, não dá para chamar uma diferença de performance de ROI financeiro real. O correto é medir uplift de performance/eficiência do patrocínio e deixar ROI financeiro como limitação.

Como eu montaria sua submissão

Eu não faria uma análise do tipo:

TikTok = 4,2%
Instagram = 3,7%
YouTube = 3,4%

Isso é análise descritiva. O desafio está praticamente avisando que isso não basta.

Eu criaria uma estrutura de 3 camadas de decisão:

1. Performance absoluta
Quem gera mais views, engagements, shares etc.

2. Performance normalizada
Quem performa melhor considerando o tamanho do creator.

Duas métricas importantes:

$$ ER_{view} = \frac{likes + comments + shares}{views} $$ $$ ER_{followers} = \frac{likes + comments + shares}{follower\_count} $$

3. Performance ajustada
Comparar conteúdos semelhantes controlando:

Platform + Content type + Category + Creator size + Audience + Language

Esse terceiro nível é onde sua entrega deixa de parecer trabalho de BI e passa a parecer trabalho de AI Master.

A pergunta central da análise

Em vez de:

“Qual plataforma tem maior engagement rate?”

Eu estruturaria como:

“Depois de controlar tamanho do creator, tipo de conteúdo, categoria e audiência, quais características realmente aumentam a probabilidade de um post superar o benchmark?”

Isso abre espaço para uma análise muito melhor.

1. Criar faixas de creator

Não compare um creator de 8 mil seguidores com alguém de 2 milhões.

Eu criaria:

Segmento	Followers
Nano	< 10K
Micro	10K–50K
Mid	50K–250K
Macro	250K–1M
Mega	> 1M

Mas faria uma segunda análise usando quintis do próprio dataset, porque os cortes acima são decisões de negócio e os quintis evitam buckets muito desbalanceados.

Depois calcularia algo muito interessante:

Engagement Efficiency
$$ Efficiency = \frac{Engagements}{Followers/1000} $$

Isso responde:

quantas interações cada 1.000 seguidores do creator geram?

Um creator de 30K pode gerar menos interações absolutas que um de 2M, mas ser muito mais eficiente.

2. Não medir só engagement

Eu criaria quatro KPIs diferentes.

Consumption

Views

Responde:

o conteúdo consegue distribuição?

Interaction

Likes + Comments + Shares

Responde:

ele consegue reação?

Engagement Rate

Engagements / Views

Responde:

entre quem consumiu, quantos reagiram?

Share Rate

Shares / Views

Essa, para mim, seria uma das métricas mais importantes do desafio.

Likes são relativamente baratos.

Compartilhamento representa capacidade de propagação.

Pode surgir, por exemplo:

vídeo gera mais likes, mas determinado conteúdo Mixed gera 2,4× mais shares entre creators Micro.

Esse é o tipo de finding que vale colocar na capa.

3. Criar o benchmark relativo

Aqui está uma ideia que eu colocaria como diferencial.

Um ER de 4% pode ser fantástico no YouTube e mediano em outro contexto.

Então calcularia para cada post:

$$ RelativePerformance = \frac{ER_{post}} {MedianER_{peer-group}} $$

Onde peer group é:

Platform × Creator Size × Content Category

Assim:

1.0x = benchmark
1.4x = 40% melhor que posts comparáveis
0.7x = 30% abaixo

Isso elimina boa parte do problema de comparar coisas incompatíveis.

E permite escrever findings como:

“Vídeos não vencem universalmente. O ganho está concentrado em determinadas combinações de plataforma, categoria e tamanho de creator.”

Muito mais sofisticado.

4. A análise de patrocínio precisa ser feita em pares comparáveis

Essa provavelmente é a parte mais importante do challenge.

Não podemos simplesmente fazer:

sponsored.mean() vs organic.mean()

Mesmo que dê uma diferença enorme.

Porque patrocinados podem estar concentrados em creators maiores, determinadas plataformas ou determinados formatos.

Eu faria primeiro uma análise bruta e depois uma ajustada.

Comparação bruta

Organic ER vs Sponsored ER.

Depois:

Matched comparison

Para cada sponsored post, comparar com posts orgânicos semelhantes em:

plataforma;
creator size;
categoria;
content type;
audiência predominante;
idioma;
período.

E calcular:

$$ SponsorshipUplift = \frac{Metric_{Sponsored} - Metric_{OrganicBenchmark}} {Metric_{OrganicBenchmark}} $$

Então teremos algo parecido com:

Micro creator + TikTok + Tech → +X% reach, +Y% share rate

versus

Macro creator + Instagram + Lifestyle → +X% views, mas −Y% ER

Isso responde de fato:

onde patrocínio agrega valor?

5. Uma distinção que eu colocaria no relatório

Pode acontecer algo assim:

Sponsored

+18% views
−14% engagement rate

Isso não significa automaticamente:

“patrocínio não funciona”.

Pode significar:

o patrocínio compra distribuição, mas dilui interação.

E aí a decisão depende do objetivo.

Para awareness, pode valer.

Para community/engagement, talvez não.

Eu dividiria a política em:

Awareness campaigns

Otimizar para:

Views / Reach proxy

Engagement campaigns

Otimizar para:

ER + Share Rate

Advocacy/Virality

Otimizar para:

Shares / Views

Isso é muito mais executivo.

6. E eu evitaria falar em ROI sem custo

O Kaggle documenta patrocinador, categoria e disclosure, mas não apresenta custo pago ao influencer nem receita atribuída ao conteúdo.

Logo:

não existe ROI financeiro calculável nessa base.

Podemos calcular:

Sponsored Performance Uplift

ou

Sponsorship Efficiency

Mas não:

$$ ROI=\frac{Receita-Custo}{Custo} $$

sem inventar custo.

Isso é um ponto que eu explicitamente colocaria no relatório.

Mostra maturidade analítica.

7. Pergunta ainda mais interessante: creator grande compra alcance ou performance?

Rodaria:

log(follower_count) × engagement_rate

e:

log(follower_count) × views

É possível aparecer algo como:

followers ↑ → views ↑
followers ↑ → ER ↓

Nesse caso a conclusão não seria:

pequenos creators são melhores.

Seria:

escala e eficiência são produtos diferentes.

Mega creators = distribuição.

Micro creators = eficiência.

E isso naturalmente gera uma política diferente para cada objetivo.

8. Audience-market fit

O dataset possui predominância de idade, gênero e localização.

Eu criaria:

Platform × Age × Content Category

Depois:

Content Type × Age

Depois:

Sponsored × Age

Exemplo do tipo de conclusão que queremos obter:

19–25 não é simplesmente “a audiência que mais engaja”. Ela performa acima do benchmark especificamente em Tech + TikTok + Video, enquanto 26–35 supera o benchmark em Lifestyle + Instagram.

Essa granularidade é exatamente o que o brief pede.

9. O que NÃO funciona

Eu criaria um quadrante.

Scale × Efficiency
	ER alto	ER baixo
Views altas	SCALE	AWARENESS ONLY
Views baixas	NICHE WINNER	STOP

A parte inferior direita é simples:

baixo alcance + baixo ER → parar.

Mas ainda acrescentaria:

Waste Index
$$ WasteScore = Percentile(Views^{-1}) + Percentile(ER^{-1}) $$

Ou uma versão ponderada.

Assim conseguimos listar:

Top 10 combinações de plataforma × formato × creator tier com maior desperdício.

Isso vira uma decisão executiva.

10. Survivorship bias

O README faz um alerta excelente sobre posts com zero ou baixíssimo engagement.

Então eu faria uma análise que muita gente esqueceria:

Failure rate
$$ FailureRate = \frac{Posts < P25_{benchmark}} {TotalPosts} $$

E não apenas média.

Imagine:

Estratégia A

ER médio = 7%

mas 45% dos posts fracassam.

Estratégia B

ER médio = 6,3%

mas apenas 8% fracassam.

Para planejamento recorrente, B pode ser muito mais previsível.

Isso é uma conclusão de negócio excelente.

11. Eu criaria um modelo preditivo como diferencial

Não faria um modelo complexo só para dizer que usei IA.

Usaria CatBoost ou LightGBM.

Input:

platform
content_type
content_category
content_length
hashtags_count
follower_count
creator_tier
is_sponsored
disclosure_type
audience_age
audience_gender
audience_location
language
weekday
hour
month

Target:

log(engagement_rate)

ou ainda melhor:

Target binário

Top Performer = ER > P75 do peer-group

Então a ferramenta responde:

Qual a probabilidade deste conteúdo ficar entre os 25% melhores conteúdos comparáveis?

Exemplo:

ANTES DE POSTAR

TikTok
Tech
Video
45 segundos
Creator: 38K
19–25
Brazil
Sponsored: No

Predicted performance

78% chance of Top Quartile

Muito mais utilizável pelo social media.

12. E usaria SHAP

Em vez de só previsão:

“ER estimado: 6,7%”

mostraria:

Por quê

Creator tier: +14%

45s duration: +9%

Tech category: +7%

Sponsored: −5%

Hashtag count: −2%

Assim o modelo se transforma em recomendação.

13. O produto final que eu construiria

Eu chamaria de:

Social Intelligence Engine

Não simplesmente “dashboard”.

Teríamos três módulos.

Monitor

O que aconteceu?

Performance histórica.

Diagnose

Por que aconteceu?

Benchmark relativo + drivers + sponsorship uplift.

Recommend

O que devemos publicar agora?

Modelo preditivo + recomendação.

O Head poderia selecionar:

Platform: TikTok
Objective: Shares
Category: Tech
Audience: 19–25

E receber algo como:

Creator: 10–50K
Content: Video
Length: 30–60s
Sponsored: Organic
Benchmark share rate: X
Expected relative performance: 1.4×
Confidence: High

Isso é um diferencial bem maior que apenas entregar um Power BI.

A estrutura da apresentação

Eu faria 8 telas, no máximo.

01 — Executive summary

Três descobertas.

Três decisões.

Sem gráfico complexo.

02 — Where engagement actually comes from

Platform × Format × Creator size.

Mostrar que o efeito é de combinação, e não uma variável isolada.

03 — Scale ≠ Efficiency

Followers × Views × Engagement efficiency.

Macro vs Micro.

04 — Does sponsorship work?

Antes:

Organic vs Sponsored bruto.

Depois:

Adjusted Sponsored Uplift.

Essa tela provavelmente será uma das mais fortes.

05 — Audience fit

Audience × Platform × Category.

06 — What we're wasting

Quadrante:

Reach × Efficiency

Destacar a área STOP.

07 — Monday morning strategy

Algo extremamente objetivo:

DOUBLE DOWN

3 estratégias.

TEST

2 estratégias.

STOP

3 estratégias.

08 — Social Intelligence Engine

Print/demo da ferramenta.

E a estratégia final deve ter só quatro decisões

Não faria uma lista de 20 recomendações.

Eu entregaria:

1. SCALE

As combinações com:

>1.25× benchmark

e volume suficiente.

2. TEST

Combinações com potencial, mas amostra pequena.

3. OPTIMIZE

Bom reach e ER abaixo do esperado.

4. STOP

<0.75× benchmark

com amostra relevante.

Isso cria uma política que o time consegue continuar usando depois do challenge.

Quick wins

A parte “o que fazemos segunda-feira” eu estruturaria assim:

1. Pare de avaliar posts somente por likes.
Dashboard passa a mostrar Views, ER, Share Rate e Relative Performance.

2. Todo creator recebe um benchmark próprio.
Nunca mais Mega vs Micro diretamente.

3. Todo sponsored post passa a ter um organic control group.

4. Conteúdo abaixo de 0,75× do benchmark entra em revisão.

5. Conteúdo acima de 1,25× entra automaticamente na fila de replicação/teste.

6. O planejamento semanal passa a usar o predictor antes da publicação.

Isso é acionável.

Process Log

Também faria questão de mostrar que IA não fez simplesmente “analise o CSV”.

Algo assim:

1. DATA AUDIT
IA utilizada para mapear schema, detectar inconsistências e sugerir testes.
Validação humana das métricas e regras de negócio.

2. EXPLORATORY ANALYSIS
Python/Pandas para análises descritivas e segmentadas.
IA usada para identificar hipóteses adicionais.

3. SPONSORSHIP ANALYSIS
Comparação bruta identificada como potencialmente enviesada.
Criado modelo ajustado por plataforma, categoria, creator size e formato.

4. FEATURE ENGINEERING
Creator tiers
Share rate
Engagement efficiency
Relative performance
Failure rate
Hashtag count
Temporal features

5. PREDICTIVE MODEL
CatBoost/LightGBM.
Cross validation.
SHAP para interpretabilidade.

6. STRATEGY
IA utilizada para transformar findings estatísticos em hipóteses.
Recomendações só foram aceitas quando suportadas pelos dados.

7. VALIDATION
Checagem de sample size, outliers, leakage e estabilidade dos resultados.

Isso responde muito melhor ao requisito de evidenciar como IA foi utilizada.

Há um bloqueio para eu fechar os números agora

A página pública confirma o schema e a natureza da base, mas não expõe as 52 mil linhas para eu processar diretamente daqui. E a cópia de GitHub encontrada na busca é outro schema, portanto decidi não contaminar a análise usando números dela. O Kaggle original é uma base simulada com as características descritas no challenge. A outra análise pública inclusive concluiu coisas superficiais como “vídeo tem maior engagement” e “sponsored tem menor engagement”, justamente o nível que eu evitaria na sua entrega.

Baixe o CSV/ZIP do Kaggle e anexe aqui. Aí eu consigo fazer a próxima etapa de verdade: rodar as 52 mil linhas, descobrir os segmentos vencedores/perdedores, estimar o uplift ajustado de patrocínio, encontrar thresholds de creator, analisar hashtags/audiência e transformar isso nos findings numéricos que vão para a apresentação
~~~~
