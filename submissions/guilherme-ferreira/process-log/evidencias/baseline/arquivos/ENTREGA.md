# Estratégia de Social Media: o que os 52 mil posts realmente dizem

**Para:** Head de Marketing · **De:** AI Master, Marketing · **Base:** `social_media_dataset.csv` (52.214 posts, 5.000 creators, 29/05/2023 a 28/05/2025)

---

## Em 1 minuto

1. **Nenhuma variável deste dataset afeta o engajamento.** Plataforma, formato, categoria, tamanho do creator, patrocínio, idioma, audiência, horário, dia da semana, hashtags e duração: todo post tem ~10.100 views, ~1.510 likes, ~300 shares e ~200 comentários. A diferença máxima entre dois grupos quaisquer fica abaixo de **0,3%**. Fiz 85 testes estatísticos e o número de "achados" foi o que o acaso produziria sozinho.
2. **O dataset tem a assinatura de dados sintéticos, não de posts reais.** Cada métrica segue uma distribuição aleatória (Poisson) em torno de um valor fixo. Views não têm relação com seguidores: um creator com 1K seguidores tem o mesmo alcance de um com 1M. Nenhum post teve engajamento baixo. O mesmo creator aparece com um número diferente de seguidores em cada post. Nomes, URLs e textos são gerados automaticamente.
3. **Por isso não vou entregar "vídeos de 30–60s em Tech geram 3,2x mais shares".** Esse tipo de frase pode ser tirado deste arquivo, mas seria ruído vendido como insight. Eu mostro abaixo que o "melhor segmento" de um ano não se repete no ano seguinte.
4. **O que dá para decidir mesmo assim:** (a) auditar a fonte dos dados esta semana; (b) pagar influenciador por resultado entregue (CPM/CPE), nunca por número de seguidores; (c) medir o efeito de patrocínio com testes controlados, não com comparação histórica; (d) adotar a ferramenta `signal_check.py`, que separa sinal de ruído antes de qualquer decisão de verba.

---

## 1. Análise de performance

### 1.1 O retrato geral

| Métrica | Média | Desvio-padrão | Mín–máx | Leitura |
|---|---|---|---|---|
| Views | 10.100 | 100 (1%) | 9.676 – 10.551 | Na vida real, o alcance varia 100x a 1.000x entre posts |
| Likes | 1.510 | 39 | 1.354 – 1.668 | |
| Shares | 300 | 17 | 227 – 380 | |
| Comentários | 200 | 14 | 140 – 258 | |
| Engajamento/views | 19,9% | 0,5 p.p. | 17,9% – 22,2% | Taxa alta e sem variação |

Um teste técnico, para quem quiser conferir: em todas as quatro métricas a variância é igual à média (razão de 0,99 a 1,00) e os percentis 1, 25, 50, 75 e 99 coincidem com os de uma Poisson teórica até a unidade. É exatamente o que sai de um gerador como `numpy.random.poisson(10100)`. Posts reais não se comportam assim.

### 1.2 O que gera engajamento? Nada do que está nos dados

Engajamento por views em cada corte, com o lift em relação à média:

| Corte | Melhor grupo | Pior grupo | Diferença máxima | Estatisticamente significativo? |
|---|---|---|---|---|
| Plataforma | Bilibili +0,02% | Instagram −0,03% | 0,05% | Não (p=0,36) |
| Formato | Text +0,05% | Image −0,01% | 0,06% | Não (p=0,22) |
| Categoria | Lifestyle +0,01% | Tech −0,03% | 0,04% | Não (p=0,29) |
| Tamanho do creator | 50–100K +0,03% | <10K −0,04% | 0,07% | Não (p=0,74) |
| Patrocinado vs. orgânico | — | — | 0,01% | Não (p=0,88) |
| Faixa etária da audiência | — | — | 0,06% | Não (p=0,52) |
| Gênero da audiência | — | — | 0,00% | Não (p=0,93) |
| País da audiência | — | — | 0,11% | Não (p=0,45) |
| Hora / dia / mês do post | — | — | 0,07% – 0,22% | Não |
| Nº de hashtags / duração | — | — | 0,05% – 0,08% | Não |

- **85 testes** (11 dimensões + tempo e duração × views, likes, shares, comentários e taxa): **1** deu p<0,05. O acaso sozinho produziria cerca de 4. Com correção para múltiplos testes, **0**.
- **Correlações** entre views, likes, shares, comentários, seguidores e duração ficam todas entre −0,007 e +0,007.
- **Efeito do creator:** o mesmo creator não performa consistentemente melhor que outros (p=0,93). Não existem "bons creators" nos dados.
- **Modelo preditivo:** um modelo com 104 parâmetros (plataforma × formato × categoria, tamanho do creator, patrocínio, audiência e idioma), treinado em 2023–24 e testado em 2024–25, teve **R² de −0,005 no teste**. Ele prevê pior do que simplesmente chutar a média.

### 1.3 Patrocínio funciona?

Fiz a comparação justa que o brief pede, controlando por plataforma, formato, categoria, tamanho do creator, idioma e audiência:

- **Regressão com todos os controles:** efeito do patrocínio = **−0,001 p.p.** na taxa de engajamento (IC 95%: −0,010 a +0,007 p.p.).
- **Comparação dentro de 136 estratos** (plataforma × formato × categoria × faixa de creator): lift médio ponderado de **−0,015%**. 8 estratos deram "significativo", quase o que o acaso daria (~7).
- **Alcance:** 10.100 views no patrocinado e 10.100 no orgânico.
- **Tipo de disclosure** (explícito, implícito, nenhum) e **categoria do patrocinador**: sem diferença.
- **Custo implícito:** o dataset **não tem coluna de custo**. Não é possível calcular ROI de patrocínio com ele. Quem disser o contrário está inventando o denominador.

**Conclusão:** com 22 mil posts patrocinados, o intervalo de confiança descarta qualquer efeito maior que **±0,05%** no engajamento. Se estes dados fossem reais, patrocínio não mudaria nada no engajamento, e o único critério de decisão seria o custo. Como os dados não parecem reais, a pergunta continua em aberto e precisa ser respondida com o desenho da Seção 2.

### 1.4 Qual audiência engaja mais?

Nenhuma. Faixa etária, gênero e país da audiência não mudam o engajamento em nenhuma plataforma, formato ou categoria. Há dois problemas estruturais adicionais:

- Os campos de "distribuição" de audiência trazem um único valor por post (ex.: "19-25"), não uma distribuição. Não dá para segmentar por persona.
- A mistura de idiomas é idêntica em todas as plataformas (50% inglês, 20% chinês e 10% de cada um dos outros), inclusive em Bilibili e RedNote, que são chinesas. Isso é outro sinal de geração artificial.

### 1.5 O que NÃO funciona: as armadilhas analíticas deste dataset

É aqui que uma análise feita às pressas (ou por uma IA sem supervisão) erra. Três "insights" que parecem ótimos e são falsos:

**Armadilha 1: "Micro-influencers engajam 100x mais."** Se a taxa for calculada como engajamento ÷ seguidores, creators com menos de 10K seguidores aparecem com 37% e os com mais de 500K com 0,3%. Isso é artefato matemático: o engajamento é o mesmo (~2.010) em todas as faixas, e dividir por um número menor dá um resultado maior. Na métrica certa, engajamento ÷ views, a taxa é 19,9% em todas as faixas.

**Armadilha 2: "O segmento campeão."** Ranqueei os 3–4 cortes combinados (plataforma × formato × categoria × creator) em 2023–24. O top 1 foi "Bilibili + imagem + beauty + 500K+", com +0,56%. Em 2024–25 esse mesmo segmento ficou em **−0,06%**. A correlação entre o ranking de um ano e o do ano seguinte é **0,10**, praticamente zero. Qualquer lista de "top segmentos" tirada deste arquivo é sorteio.

**Armadilha 3: "Hashtags vencedoras."** Das 970 hashtags com 100 posts ou mais, 59 aparecem como "significativas" (esperado pelo acaso: ~48). Depois da correção para múltiplos testes, sobram **0**. As hashtags são palavras soltas do dicionário ("safe", "religious", "tend"), sem relação com o conteúdo.

**Sobre o viés de sobrevivência:** o menor post do dataset tem 9.676 views e 1.354 likes. Não há fracasso nenhum. Numa base real, uma parcela relevante dos posts tem engajamento próximo de zero, e a ausência desses casos já indica que o arquivo não representa a operação.

---

## 2. Estratégia recomendada

Não vou recomendar em qual plataforma, formato ou faixa de creator concentrar esforço, porque os dados não sustentam nenhuma escolha. A estratégia abaixo foi pensada para funcionar em qualquer cenário: tanto se estes dados forem reais quanto se não forem. Está em ordem de prioridade.

### Prioridade 1 (esta semana): descobrir de onde vieram os dados
- Pergunte ao time: esse CSV foi exportado das nossas contas (Meta Business Suite, TikTok Business Center, YouTube Studio) ou baixado do Kaggle como referência? A página do Kaggle trata o arquivo como dataset público de exemplo, e todos os sinais indicam que ele é sintético.
- Se o time acredita que são nossos dados reais, compare 20 posts do CSV com os números nativos das plataformas. Se não baterem, há um problema de pipeline, e isso por si só já é um achado importante.
- **Custo:** 1 dia de uma pessoa. **Valor:** evita realocar orçamento com base em ruído.

### Prioridade 2 (próximas 2 semanas): montar a base certa
O dataset não tem colunas sem as quais não dá para responder às três perguntas do brief. A base mínima:

| Campo que falta | Para que serve |
|---|---|
| **Custo por post/contrato** (fee, produto, impulsionamento) | ROI e custo por engajamento. Sem isso, "patrocínio vale a pena?" não tem resposta |
| **Resultado de negócio** (cliques, cupom, UTM, vendas) | Engajamento não é receita |
| **Seguidores do creator na data do post** (fixo por creator) | Alcance relativo, controle por tamanho |
| **Impressões/alcance únicos e retenção de vídeo** | Diferenciar "viu" de "consumiu" |
| **Mix de audiência de verdade** (% por faixa, não um único valor) | Segmentação por persona |

### Prioridade 3: política de patrocínio (vale desde já, com qualquer dado)
1. **Pague por entrega, não por seguidores.** Contratos com preço por CPM (custo por mil views) ou CPE (custo por engajamento) garantidos, com bônus por conversão rastreada (cupom/UTM). Seguidor é uma promessa de alcance, e neste dataset a promessa é literalmente zero: correlação de 0,005 entre seguidores e views.
2. **Limite de renovação:** só renove um influenciador cujo CPE ficou **≤ ao CPE médio do nosso orgânico impulsionado** na mesma plataforma nos últimos 90 dias. O valor exato sai da base da Prioridade 2. Não há como calcular esse número a partir deste arquivo.
3. **Faixa de creator:** comece com creators de 10K a 100K. Não é que os dados provem que eles engajam mais (não provam). É que o custo por post é menor, o que permite **mais testes pelo mesmo orçamento**, e o aprendizado é o gargalo agora.
4. **Meça o efeito real com um teste controlado**, não com comparação histórica: sorteie metade dos creators elegíveis para receber patrocínio neste trimestre e compare com a outra metade. Com o desvio-padrão típico de dados reais, algo em torno de 200 a 400 posts por braço detecta uma diferença de 15–20%. Isso é viável num trimestre.

### Prioridade 4: o que parar de fazer
- **Parar** de decidir verba com base em rankings de "top segmentos" e "top hashtags" sem validar em outro período. Neste dataset, o ranking de um ano prevê 0% do ano seguinte.
- **Parar** de usar engajamento ÷ seguidores como métrica de comparação entre creators de tamanhos diferentes, porque ela favorece os pequenos automaticamente. Use engajamento ÷ views (ou ÷ alcance).
- **Parar** de negociar fee por número de seguidores (ver Prioridade 3).
- *Não posso afirmar, com base nestes dados, que alguma plataforma, formato ou categoria deve ser cortada.* Qualquer corte feito agora seria arbitrário.

### Quick wins (implementáveis esta semana)
1. **Auditoria da fonte:** 20 posts do CSV comparados com o painel nativo (Prioridade 1).
2. **UTM + cupom exclusivo** em todo post patrocinado a partir de segunda-feira. Custo zero e cria o dado de ROI que hoje não existe.
3. **Trocar a métrica do relatório semanal** para engajamento ÷ views por plataforma, sempre com a faixa de creator ao lado.
4. **Rodar o `signal_check.py`** (Seção 3) antes de cada reunião de alocação de verba. Nada vira decisão se aparecer como "RUÍDO".

---

## 3. O diferencial: `signal_check.py`, o detector de sinal vs. ruído

O maior risco para um time de social media com 52 mil linhas não é a falta de insight. É ter insight demais que é falso. Por isso, a ferramenta que entrego não é um "gerador de recomendações". É um **filtro que impede decisões baseadas em ruído**, e pode ser rodado toda semana sobre qualquer export com o mesmo formato.

**Uso:** `python signal_check.py export_da_semana.csv --min-lift 5`

**O que ela faz:**
1. **Saúde dos dados:** 5 checagens que dados reais passam e dados quebrados ou sintéticos não (dispersão de views, views × seguidores, views × likes, existência de posts fracassados, seguidores estáveis por creator).
2. **Sinal ou ruído:** para cada plataforma, formato, categoria, faixa de creator e patrocínio, calcula o lift de engajamento com intervalo de confiança e só marca **SINAL** se o efeito passar em três testes:
   - é estatisticamente significativo depois da correção para múltiplos testes;
   - se repete na 1ª e na 2ª metade do período;
   - é grande o bastante para importar (padrão: 5% ou mais).

**Resultado neste dataset** (arquivo `signal_check_output.txt`):

```
== SAÚDE DOS DADOS ==
Dispersão de views (CV)                      0.010   ALERTA: views quase constantes
Correlação views × seguidores                0.005   ALERTA: alcance não depende de audiência
Correlação views × likes                     0.001   ALERTA: likes não dependem de views
Posts com engajamento zero                   0.0%    ALERTA: nenhum post fracassou
Seguidores distintos por creator (mediana)   10      ALERTA: seguidores mudam a cada post

Resumo: 0 de 19 segmentos com sinal acionável; 5 alertas de saúde dos dados.
```

Quando o time carregar os dados reais da Prioridade 2, a mesma ferramenta passa a apontar os segmentos que merecem verba, agora com uma garantia de que não estão perseguindo ruído.

---

## 4. Process log: como usei IA

| Etapa | O que foi feito | Decisão humana/crítica |
|---|---|---|
| 1. Perfil dos dados | IA (Claude) carregou o CSV e gerou estatísticas descritivas | Notei que o desvio-padrão das views era 1% da média. Isso era suspeito e mudou todo o rumo da análise |
| 2. Hipótese de dados sintéticos | Teste de variância = média (Poisson), comparação de quantis com Poisson teórica, correlações entre métricas | Decidi testar a hipótese "não há sinal" antes de procurar insights, e não o contrário |
| 3. Varredura sistemática | 85 testes de Kruskal-Wallis cobrindo todas as dimensões e métricas, com correção de Bonferroni | Contei quantos "significativos" o acaso produziria, em vez de reportar os significativos isolados |
| 4. Patrocínio com controles | Regressão OLS com 9 controles + comparação em 136 estratos | O brief exigia uma comparação justa; reportei o intervalo de confiança, não só o p-valor |
| 5. Validação fora da amostra | Ranking de segmentos em 2023–24 testado em 2024–25; modelo preditivo com holdout temporal (R² = −0,005) | Deixei a "análise que uma IA entregaria" rodar só para demonstrar que ela não se sustenta |
| 6. Armadilhas | Engajamento ÷ seguidores, hashtags, top segmentos | Documentadas como "o que não funciona", porque são os erros mais prováveis do time |
| 7. Ferramenta | `signal_check.py`, que transforma a lição em uma rotina semanal | Escolhi um filtro anti-ruído em vez de dashboard ou modelo, porque é o que protege a decisão |

**Onde a IA teria errado sem supervisão:** colado o brief, o caminho natural seria produzir tabelas de "top plataforma/formato/hashtag" e uma estratégia confiante em cima de diferenças de 0,05%. O próprio brief pede frases como "3,2x mais shares". Este dataset é um teste de integridade analítica, e a resposta correta é dizer que **os dados não sustentam essas conclusões**, mostrar por quê e entregar o caminho para conseguir dados que sustentem.

**Arquivos:** `analise.py` (varredura de 85 testes), `analise2.py` (controles, holdout, hashtags, armadilhas), `signal_check.py` (ferramenta), `signal_check_output.txt` (saída).
