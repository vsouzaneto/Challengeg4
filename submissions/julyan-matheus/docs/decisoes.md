Decisões do produto
Decisão 1: Triagem em 4 baldes em vez de ranking único.
Limpar (deal com mais de 138 dias)/ requalificar ( Deals sem conta que tem que ter a conta vinculada) / Iniciar (prospecting) / focar (os que estao vivos dentro das métricas que levantamos , esses e somente esses recebem score)
MOTIVO: 81% do pipeline passsou do teto de dias e 68% nao tem conta, branquear todos deixaria isso de fora.



Decisão 2: Deals sem conta nao somem e nem ganham score, eles vao para aba "requalificar" com a ação explicita para vincular conta , ordenando por recencia.
Motivo : nenhum deal sem conta fechou.

Decisão 3: Pesos do score
Afinidade vendedor×produto 40% / Momentum 25% / Valor do produto 20% / Carga do vendedor 15%.
Motivo:proporcional ao efeito medido nas hipóteses. Valor entra porque a meta do vendedor é em dinheiro. Fora do score: tamanho da empresa, produto isolado, gerente e região, não separaram Won de Lost.



Decisão 4: dois indicadores na tela 
Valor esperado (chance × preço do produto).
Motivo: no backtest, misturar valor no score bagunçou a ordenação do meio (Q1–Q3 fora de ordem). Separados, o vendedor vê "o que vai fechar" e "onde está o dinheiro" sem um contaminar o outro.

Backtest (01/09/2017 → 31/12/2017, 893 deals): grupo quente fechou 78,9% vs 71,4% do frio, com receita 3x maior. Afinidade caiu de 19 para 8 pontos fora da amostra — ainda o maior fator.



Decisão 5: Ajustes propostos pelo Claude Code na spec (aceitos)
- Normalização por escala natural em vez de min-max (score estável, não muda quando outro deal entra)
- Bloco "Hoje" ordenado só por valor esperado (score × valor contava chance duas vezes erro meu na spec)
- Momentum em degraus fixos (0/14/30/60/90/120) em vez de por dia
Origem: IA apontou, eu avaliei e aceitei os 4. Nenhum muda a lógica das hipóteses.


Decisão 6: Score honesto + etiqueta relativa
Score fica na escala real (62–78). Cada deal ganha etiqueta "Top / Meio / Fundo do seu Focar" pela posição entre os deals do vendedor.
Motivo: esticar pra 0–100 faria um deal de 62% parecer zero. O vendedor lê o número como chance real.
Origem: IA apontou a compressão, ofereceu esticar visualmente, eu recusei.


Decisão 7: Requalificar ordenada por urgência; "Hoje" vazio vira instrução
Engaging primeiro (mais recentes no topo), Prospecting depois. Quando Focar está vazio, o bloco "Hoje" diz quantos deals estão sem conta e que vincular conta é a ação do dia.
Motivo: 9 de 27 vendedores têm Focar vazio. Tela vazia sem instrução seria inútil pra eles e são justamente os que mais precisam.
Origem: eu vi no print do Darcel e pedi o ajuste.



Achado da Tela 2: time do Melvin Marxen (5 vendedores) inteiro com 0 em Focar; 4 de 5 do Dustin Brinkmann. Os alertas de 60% sem conta / 80% vencido quase não disparam  "0 em Focar" é o sinal mais útil. Mantive os três alertas (IA sugeriu simplificar; preferi deixar pra quando o CRM estiver mais limpo).


Decisão 8: Auditoria independente (ChatGPT, sem contexto) — 8 pontos
Aceitos e corrigidos: 1 e 2 (filtrar histórico e carga pela data de referência), 4 (limitar capacidade a 0–1), 8 (sem etiqueta Top/Meio/Fundo quando Focar < 3).
Documentados como limitação: 3 (score ranqueia, não é probabilidade calibrada), 7 (cold start).
Rejeitado: 6 (deal_stage)  só Engaging recebe score, Prospecting não tem engage_date.
Mantido: 5 (preço de tabela no valor esperado)  dataset não tem valor do deal aberto; close_value seria leakage.
