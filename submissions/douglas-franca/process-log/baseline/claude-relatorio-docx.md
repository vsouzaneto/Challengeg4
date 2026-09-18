# Baseline — Claude: relatório .docx gerado

Conversão para texto de `CLAUDE-Estrategia_Social_Media_Relatorio.docx` (5 figuras omitidas). O arquivo binário original não é versionado.

---

ESTRATÉGIA DE SOCIAL MEDIA

Análise de 52.214 posts orgânicos e patrocinados

Instagram · TikTok · YouTube · Bilibili · RedNote

Preparado para: Head de Marketing

Preparado por: AI Master — Marketing

Setembro de 2026

⚠ Achado crítico logo na página seguinte: os dados fornecidos não contêm sinal estatístico de performance. Leia o sumário executivo antes de qualquer coisa.

## 1. Sumário executivo

Você pediu três respostas — o que gera engajamento de verdade, se vale a pena patrocinar, e qual deveria ser a estratégia de conteúdo. Analisei os 52.214 posts com testes estatísticos formais (ANOVA, correlação, teste t) e um modelo preditivo de machine learning. O resultado é direto:

Os dados, como estão hoje, não contêm nenhum sinal estatisticamente detectável de que plataforma, tipo de conteúdo, categoria, patrocínio, tamanho de creator ou perfil de audiência influenciem o engajamento. Todas as diferenças observadas entre segmentos são estatisticamente equivalentes a ruído aleatório (p > 0,20 em todos os testes; um modelo de machine learning treinado para prever engajamento a partir de 7 variáveis teve poder preditivo de R² ≈ 0 — o mesmo que simplesmente chutar a média).

Isso não é uma falha da análise — é o achado mais importante do dataset, e é exatamente o tipo de coisa que uma análise rasa ("vídeo performa melhor que imagem") esconderia. Recomendar uma plataforma ou formato específico com base nestes dados seria apresentar opinião disfarçada de dado — o oposto do que foi pedido.

Nas seções 3 e 4 mostro as evidências completas. Na seção 5 respondo, com honestidade, cada uma das perguntas do briefing. Na seção 6 traduzo isso em uma estratégia de curtíssimo prazo (o que fazer nesta semana, dado que ainda não temos sinal confiável). Na seção 7 entrego o diferencial pedido: um painel interativo que a equipe pode usar recorrentemente — e que já vem com teste de significância embutido, para que ninguém confunda ruído com sinal de novo.

### Os 4 números que resumem tudo

| Métrica | Valor | Leitura |

|---|---|---|

| Diferença de engajamento entre a melhor e a pior plataforma | 0,10 p.p. (19,90% a 19,91% vs. 19,90% a 19,90%) | Estatisticamente igual a zero (ANOVA p = 0,55) |

| Diferença orgânico vs. patrocinado | 0,01 p.p. | Estatisticamente igual a zero (teste t p = 0,80) |

| Correlação seguidores do creator × engajamento | r = −0,002 | Praticamente nula |

| R² de modelo preditivo (Random Forest, 7 variáveis) | ≈ 0,00 | O modelo não prevê melhor que "chutar a média" |



## 2. Metodologia

Dataset: Social Media Sponsorship & Engagement Dataset (licença MIT), 52.214 posts, 5.000 creators únicos, 5 plataformas (Bilibili, Instagram, RedNote, TikTok, YouTube), período de 01/01/2024 a 09/09/2024. Sem valores nulos nas colunas de métricas.

Métrica principal — taxa de engajamento: (curtidas + compartilhamentos + comentários) ÷ visualizações, calculada por post. É a métrica padrão da indústria e a mais comparável entre plataformas com escalas de audiência diferentes.

Testes aplicados a cada segmentação (plataforma, tipo de conteúdo, categoria, patrocínio, tipo de divulgação, faixa etária e gênero de audiência, localização, idioma, categoria de patrocinador):

ANOVA (ou teste t para variáveis binárias) para comparar médias entre grupos, com intervalo de confiança de 95%;

Correlação de Pearson para variáveis contínuas (seguidores, tamanho do conteúdo, número de hashtags);

Um modelo de Random Forest (200 árvores) treinado para prever a taxa de engajamento a partir de plataforma, tipo de conteúdo, categoria, patrocínio, seguidores, tamanho do conteúdo e nº de hashtags, validado em conjunto de teste separado (80/20) — usado como checagem final: se nem um modelo não-linear com múltiplas variáveis combinadas encontra sinal, a ausência de sinal não é um artefato de olhar variável por variável.

Threshold de significância: p < 0,05. Nenhum dos testes acima cruzou esse limite (o mais próximo foi tipo de conteúdo, p = 0,21).

## 3. Achado central: os dados não contêm sinal de performance

Antes de qualquer segmentação, um fato salta aos olhos ao examinar as métricas brutas:

| Métrica | Média | Desvio padrão | Coeficiente de variação |

|---|---|---|---|

| Visualizações | 10.100 | 100 | 1,0% |

| Curtidas | 1.510 | 39 | 2,6% |

| Compartilhamentos | 300 | 17 | 5,8% |

| Comentários | 200 | 14 | 7,0% |



Para contexto: dados reais de redes sociais seguem distribuições de cauda longa (power law) — a maioria dos posts tem pouquíssimo alcance e uma minoria "viraliza" com 10x, 100x ou 1000x a média. Aqui, o desvio padrão das visualizações é de apenas 1% da média: o post de menor alcance no dataset inteiro (9.676 views) está a menos de 5% do post de maior alcance (10.551 views). Não existe um único post "viral" nem um único post com engajamento zero em 52.214 registros — o que por si só é estatisticamente improvável em dados reais de redes sociais.

Figura 1 — Distribuição da taxa de engajamento: um sino estreito e simétrico, característico de ruído gerado aleatoriamente, não de comportamento real de audiência.

A taxa de engajamento média do dataset é de 19,9%. Para comparação, benchmarks de mercado (Socialinsider, Hootsuite, RivalIQ) situam engajamento "bom" entre 1% e 6% dependendo da plataforma — um patamar 3 a 20 vezes menor. Isso, somado à ausência de variância real, é consistente com um dataset gerado sinteticamente (para fins de treino/desafio) e não com uma extração direta das APIs das plataformas.

Isso muda o que este relatório pode honestamente entregar — e é comunicado com transparência nas próximas seções, em vez de maquiado.

## 4. Evidência segmento a segmento

### 4.1 Plataforma

Figura 2 — Barras de erro (IC 95%) se sobrepõem entre todas as plataformas. ANOVA: p = 0,55.

### 4.2 Tipo de conteúdo

Figura 3 — Vídeo, imagem, texto e conteúdo misto performam de forma estatisticamente idêntica. ANOVA: p = 0,21.

### 4.3 Patrocínio

Figura 4 — Diferença de 0,01 ponto percentual entre orgânico e patrocinado. Teste t: p = 0,80. O tamanho médio de creator contratado (499.924 seguidores) é praticamente idêntico ao de quem não é patrocinado (499.855) — ou seja, a equipe não está nem direcionando patrocínio para creators de perfil diferente.

### 4.4 Tamanho do creator (seguidores)

Figura 5 — Nenhuma relação entre seguidores e engajamento (r = −0,002). Micro-influenciadores não engajam mais nem menos que mega-influenciadores neste dataset.

### 4.5 Demais dimensões testadas

O mesmo padrão se repete em todas as outras variáveis disponíveis — nenhuma cruza o limiar de significância de 5%:

| Dimensão | p-valor (ANOVA) | Maior diferença entre grupos |

|---|---|---|

| Categoria de conteúdo (beauty/lifestyle/tech) | 0,44 | 0,07 p.p. |

| Tipo de divulgação (explícita/implícita/nenhuma) | 0,39 | 0,09 p.p. |

| Categoria do patrocinador | 0,40 | 0,25 p.p. |

| Faixa etária da audiência | 0,40 | 0,13 p.p. |

| Gênero da audiência | ≈1,00 | 0,01 p.p. |

| Localização da audiência | 0,29 | 0,21 p.p. |

| Idioma | 0,40 | 0,11 p.p. |

| Nº de hashtags (correlação) | 0,18 (r=0,006) | — |

| Tamanho do conteúdo / duração (correlação) | 0,10 (r=0,007) | — |



Conclusão da seção: com 52 mil observações — amostra grande o suficiente para detectar até diferenças pequenas — nenhuma variável disponível explica variação no engajamento. Isso não significa que essas variáveis nunca importam no mundo real; significa que este dataset específico não permite afirmar que importam.

## 5. Respondendo às perguntas do briefing — com honestidade

### O que gera engajamento de verdade?

Resposta honesta: com os dados atuais, não é possível identificar isso. Nenhuma das variáveis capturadas (plataforma, formato, categoria, tamanho de creator, audiência, hashtags, duração) explica a variação — que, aliás, é mínima. Qualquer afirmação do tipo "vídeos curtos de tech engajam mais" feita a partir deste dataset seria estatisticamente falsa, ainda que "soe" plausível.

### Patrocínio funciona? Vale a pena patrocinar?

Resposta honesta: os dados não mostram diferença de engajamento entre posts patrocinados e orgânicos (0,01 p.p., p = 0,80), em nenhuma faixa de tamanho de creator. Se o objetivo do patrocínio for gerar engajamento acima do orgânico, este dataset não sustenta esse retorno. Isso é, em si, um achado acionável: hoje a equipe não tem evidência que justifique o investimento em patrocínio — o que é diferente de "patrocínio não funciona" no mundo real. É um sinal para auditar como o retorno de patrocínio está sendo medido e registrado internamente.

### Qual o perfil de audiência que mais engaja?

Resposta honesta: nenhum. Idade, gênero e localização da audiência não se relacionam com engajamento neste dataset (p entre 0,29 e 1,00).

### O que NÃO funciona?

Aqui há uma resposta real e importante, só que em outro nível: o que não funciona é decidir estratégia de conteúdo com base neste dataset. Qualquer plano construído sobre "plataforma X performa melhor" ou "formato Y gera mais compartilhamento" estaria se apoiando em ruído, e caso a equipe já tenha tomado decisões de orçamento com base em relatórios anteriores que cruzaram essas mesmas variáveis, vale revisar a fonte de dados usada.

## 6. Estratégia recomendada

Dado o achado da seção 3, a estratégia certa não é "concentrar esforço na plataforma X" — seria inventar uma resposta que os dados não sustentam. A estratégia certa é corrigir a capacidade de medir antes de otimizar o que medir.

### Onde concentrar esforço (curto prazo)

Sem evidência para priorizar uma plataforma, formato ou categoria específica sobre outra — manter a distribuição atual entre as 5 plataformas evita o risco de abandonar um canal que, no mundo real, pode estar performando de forma muito diferente do que este dataset sugere.

Redirecionar o esforço de "qual plataforma" para "consertar a instrumentação de dados" — é o maior gargalo identificado.

### Política de patrocínio

Pausar aumento de investimento em patrocínio até haver dados confiáveis de ROI incremental — os dados atuais não sustentam nem justificam nem descartam a prática.

Se decisões de patrocínio precisam continuar sendo tomadas, criar um piloto controlado: mesmo creator/categoria, alternando posts patrocinados e orgânicos, com métricas capturadas diretamente das plataformas (não de um dataset agregado) por 4–6 semanas.

Threshold de seguidores/engajamento para justificar investimento: não é possível definir um número responsável com os dados de hoje — qualquer valor seria arbitrário.

### O que parar de fazer

Parar de tomar decisões de mix de plataforma/formato com base em relatórios que usam esta fonte de dados sem qualificação estatística.

Parar de comparar engajamento bruto entre plataformas sem teste de significância — o hábito de comparar médias "a olho" é exatamente o que levou este dataset a parecer informativo à primeira vista.

### Quick wins — o que pode ser implementado nesta semana

1) Auditar a pipeline de coleta de dados: confirmar com o time de dados/BI se este export vem diretamente das APIs das plataformas ou passou por alguma normalização/anonimização que pode ter achatado a variância real.

2) Adotar o painel interativo entregue na seção 7 como ferramenta padrão de acompanhamento — ele já aplica teste de significância automaticamente, então qualquer diferença futura entre segmentos só será reportada como "insight" se for estatisticamente real.

3) Definir, com o time de dados, um plano de instrumentação mínima: cada post deve carregar view/like/share/comment reais e um timestamp de coleta, para permitir granularidade temporal (este dataset atual não permite, por exemplo, saber se o engajamento cai com o tempo).

4) Reapresentar este achado para qualquer decisão de budget de Q3/Q4 que tenha se apoiado nesta fonte de dados.

## 7. Diferencial: painel de decisão com significância embutida

Em vez de um modelo preditivo de engajamento (que, como mostrado na seção 2, teria R² ≈ 0 e daria uma falsa sensação de precisão), o diferencial entregue é uma ferramenta que resolve o problema real revelado por esta análise: a equipe precisa de um jeito de checar rapidamente, toda vez que quiser comparar dois segmentos, se a diferença observada é real ou ruído — sem depender de um analista rodar Python.

O painel (link enviado separadamente) permite:

Selecionar qualquer combinação de plataforma, tipo de conteúdo, categoria e patrocínio e comparar métricas lado a lado;

Ver automaticamente se a diferença é estatisticamente significativa (teste aplicado em tempo real, com o mesmo padrão de rigor desta análise) — cada comparação é marcada como "diferença real" ou "dentro da margem de ruído";

Servir como padrão da casa: a partir de agora, nenhuma decisão de mix de conteúdo precisa se apoiar em uma média comparada "a olho".

Quando dados reais (com variância genuína) começarem a alimentar este painel, ele vai automaticamente passar a apontar diferenças reais entre segmentos — e é nesse momento que a estratégia de conteúdo passa a poder ser otimizada com confiança.

## 8. Process log

Ferramenta usada: Claude (Anthropic), com execução de código Python (pandas, scipy, scikit-learn, matplotlib) em ambiente sandboxed para toda a análise estatística, e geração deste documento e do painel interativo.

Carregamento e checagem de qualidade dos dados: 52.214 linhas, 27 colunas, sem nulos em colunas de métrica.

Cálculo da métrica de engajamento e exploração de estatísticas descritivas — identificação do desvio padrão anormalmente baixo em views/likes/shares/comments.

Testes formais (ANOVA, teste t, correlação de Pearson) para cada uma das 10 dimensões categóricas/contínuas disponíveis.

Modelo de Random Forest como checagem cruzada de que a ausência de sinal não depende da escolha do teste estatístico.

Geração de gráficos com intervalo de confiança de 95% para tornar o achado visualmente verificável, não apenas uma tabela de p-valores.

Redação do relatório e do painel interativo com base nos resultados acima — nenhum número neste documento foi estimado ou assumido sem cálculo direto sobre o dataset.

Nota metodológica: a decisão de não fabricar recomendações de plataforma/formato/patrocínio a partir de diferenças não significativas foi deliberada e é o núcleo analítico deste trabalho, em linha com o critério do próprio briefing de evitar achismo disfarçado de dado.
