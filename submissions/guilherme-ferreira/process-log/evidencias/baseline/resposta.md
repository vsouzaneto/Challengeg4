# Estratégia de Social Media: o que os 52 mil posts realmente dizem

**Para:** Head de Marketing · **Base:** `social_media_dataset.csv` (52.214 posts, 5.000 creators, 29/05/2023 a 28/05/2025)

---

## Em 1 minuto

1. **Nada neste dataset muda o engajamento.** Plataforma, formato, categoria, tamanho do creator, patrocínio, idioma, audiência, horário, hashtags e duração: todo post tem cerca de **10.100 views, 1.510 likes, 300 shares e 200 comentários**. A maior diferença entre dois grupos quaisquer fica abaixo de **0,3%**. Fiz 85 testes estatísticos. O acaso sozinho geraria uns 4 resultados "significativos"; saiu 1. Depois de corrigir para o número de testes, saíram 0.
2. **Os dados parecem gerados por computador, não coletados de posts reais.** Cada métrica varia só por sorteio em torno de um valor fixo (estatisticamente, uma distribuição Poisson). Um creator com 1 mil seguidores tem o mesmo alcance de um com 1 milhão. Nenhum post fracassou. O mesmo creator aparece com um número de seguidores diferente a cada post. Nomes, URLs e textos seguem padrões de geração automática.
3. **Por isso não vou entregar frases como "vídeos de 30–60s em Tech geram 3,2x mais shares".** Dá para tirar esse tipo de frase deste arquivo, mas seria ruído vendido como insight. Mostro abaixo que o "melhor segmento" de um ano não se repete no ano seguinte.
4. **Mesmo assim, dá para decidir o seguinte:**
   - auditar a origem dos dados esta semana;
   - pagar influenciador pelo resultado entregue, nunca pelo número de seguidores;
   - medir o efeito do patrocínio com testes controlados;
   - adotar a ferramenta `signal_check.py`, que separa sinal de ruído antes de qualquer decisão de verba.

---

## 1. Análise de performance

### 1.1 Visão geral
| Métrica | Média | Desvio-padrão | Mín–máx |
|---|---|---|---|
| Views | 10.100 | 100 (1%) | 9.676 – 10.551 |
| Likes | 1.510 | 39 | 1.354 – 1.668 |
| Shares | 300 | 17 | 227 – 380 |
| Comentários | 200 | 14 | 140 – 258 |
| Engajamento ÷ views | 19,9% | 0,5 p.p. | 17,9% – 22,2% |

Em dados reais, o alcance varia de 100 a 1.000 vezes entre posts. Aqui varia 1%.

Nas quatro métricas, a variância é igual à média (razão entre 0,99 e 1,00), e os percentis 1, 25, 50, 75 e 99 batem com os de uma Poisson teórica até a unidade. Esse é o padrão de números gerados por computador, não de posts reais.

### 1.2 O que gera engajamento? Nenhuma das variáveis disponíveis
| Corte | Diferença máxima entre grupos | Significativo? |
|---|---|---|
| Plataforma | 0,05% | Não (p=0,36) |
| Formato (vídeo, imagem, texto, misto) | 0,06% | Não (p=0,22) |
| Categoria | 0,04% | Não (p=0,29) |
| Tamanho do creator | 0,07% | Não (p=0,74) |
| Patrocinado × orgânico | 0,01% | Não (p=0,88) |
| Idade, gênero e país da audiência | 0,00% a 0,11% | Não |
| Hora, dia e mês do post | 0,07% a 0,22% | Não |
| Número de hashtags, duração | 0,05% a 0,08% | Não |

- **Correlações** entre views, likes, shares, comentários, seguidores e duração ficam todas entre −0,007 e +0,007, ou seja, praticamente zero.
- **Creators:** nenhum creator performa melhor de forma consistente (p=0,93).
- **Modelo preditivo:** montei um modelo com 104 parâmetros, treinei com os posts de 2023–24 e testei nos de 2024–25. A nota de acerto dele (R²) no teste foi −0,005. Na prática, ele prevê pior do que simplesmente usar a média.

### 1.3 Patrocínio funciona?
Comparei de forma justa, controlando por plataforma, formato, categoria, tamanho do creator, idioma e audiência.

- **Comparação com todos os controles ao mesmo tempo (regressão):** o efeito do patrocínio é de **−0,001 ponto percentual**, com intervalo de confiança de 95% entre −0,010 e +0,007.
- **Comparação dentro de 136 grupos parecidos** (mesma plataforma, formato, categoria e faixa de creator): o ganho médio é de −0,015%. 8 grupos deram "significativo", quase exatamente os ~7 que o acaso produziria.
- **Alcance:** 10.100 views no patrocinado e 10.100 no orgânico. Também não há diferença por tipo de aviso de publicidade nem por categoria do patrocinador.
- **Custo:** **o dataset não tem coluna de custo.** Não dá para calcular o retorno do patrocínio com ele.

**Conclusão:** com 22 mil posts patrocinados, o intervalo de confiança descarta qualquer efeito maior que ±0,05% no engajamento. Se os dados fossem reais, patrocinar não mudaria o engajamento, e a decisão dependeria só do custo. Como eles não parecem reais, a pergunta continua em aberto e precisa ser respondida com testes (Seção 2).

### 1.4 Qual audiência engaja mais?
Nenhuma. Idade, gênero e país da audiência não mudam o resultado em nenhuma combinação de plataforma, formato ou categoria. Há dois problemas adicionais:
- O campo chamado "distribuição" de audiência traz um único valor por post (por exemplo, "19-25"), e não uma distribuição. Isso impede segmentar por persona.
- A mistura de idiomas é idêntica em todas as plataformas (50% inglês, 20% chinês), inclusive no Bilibili e no RedNote, que são redes chinesas.

### 1.5 O que NÃO funciona: três "insights" falsos que este dataset produz
1. **"Micro-influencers engajam 100 vezes mais."** Se a taxa for calculada como engajamento ÷ seguidores, creators com menos de 10 mil seguidores aparecem com 37% e os com mais de 500 mil, com 0,3%. Isso é efeito da conta: o engajamento é cerca de 2.010 em todas as faixas, então dividir por menos seguidores dá um número maior. Medido como engajamento ÷ views, todas as faixas ficam em 19,9%.
2. **"O segmento campeão."** O melhor segmento de 2023–24 foi Bilibili + imagem + beauty + creators acima de 500 mil, com +0,56%. Em 2024–25 esse mesmo segmento ficou em −0,06%. A correlação entre o ranking de um ano e o do ano seguinte é de 0,10, praticamente nenhuma.
3. **"Hashtags vencedoras."** Entre 970 hashtags, 59 parecem "significativas", e o acaso sozinho produziria cerca de 48. Depois de corrigir para o número de testes, sobram 0. As hashtags são palavras soltas do dicionário.

**Viés de sobrevivência:** o pior post do dataset tem 9.676 views. Em uma base real, uma fatia relevante dos posts tem engajamento perto de zero. A ausência desses casos já mostra que o arquivo não representa a operação.

---

## 2. Estratégia recomendada (em ordem de prioridade)

Os dados não sustentam a escolha de plataforma, formato ou faixa de creator. Por isso, a estratégia abaixo funciona tanto se os dados forem reais quanto se não forem.

**P1. Esta semana: verificar a origem dos dados.** O CSV foi exportado das nossas contas ou baixado do Kaggle como exemplo? Vale comparar 20 posts do arquivo com o painel nativo de cada plataforma. Custa um dia de trabalho e evita mudar orçamento com base em ruído.

**P2. Próximas 2 semanas: montar a base certa.** Faltam campos sem os quais as perguntas do brief não têm resposta:
- **custo** por post ou contrato;
- **resultado de negócio**: UTM, cupom, vendas;
- **seguidores do creator na data do post**;
- **alcance único e retenção de vídeo**;
- **perfil real da audiência**, em percentuais por faixa.

**P3. Política de patrocínio (vale com qualquer dado):**
1. **Pagar por entrega, não por seguidores.** Contratos com custo por mil views ou custo por engajamento garantidos, mais bônus por conversão rastreada. Neste dataset, a correlação entre seguidores e views é 0,005.
2. **Regra de renovação:** só renovar com o creator cujo custo por engajamento for igual ou menor que o do nosso orgânico impulsionado na mesma plataforma nos últimos 90 dias. O valor exato sai da base montada na P2.
3. **Começar com creators de 10 mil a 100 mil seguidores.** Os dados não mostram que eles engajam mais. O motivo é que custam menos por post, então o mesmo orçamento compra mais testes, e hoje o que falta é aprendizado.
4. **Medir o efeito real com um experimento:** sortear metade dos creators elegíveis para receber patrocínio no trimestre e comparar com a outra metade. Com a variação típica de dados reais, algo entre 200 e 400 posts por grupo deve bastar para detectar uma diferença de 15% a 20%. É uma estimativa aproximada, que precisa ser recalculada com os nossos dados.

**P4. O que parar de fazer:**
- decidir verba com base em rankings de "top segmentos" ou "top hashtags" sem confirmar em outro período;
- usar engajamento ÷ seguidores para comparar creators de tamanhos diferentes (usar engajamento ÷ views ou ÷ alcance);
- negociar valor pelo número de seguidores.

**Quick wins desta semana:**
1. Auditoria de 20 posts contra o painel nativo.
2. UTM e cupom exclusivo em todo post patrocinado a partir de segunda-feira.
3. Relatório semanal passa a usar engajamento ÷ views, sempre ao lado da faixa de creator.
4. Rodar o `signal_check.py` antes de cada reunião de verba.

---

## 3. Diferencial: `signal_check.py`, detector de sinal e ruído

O maior risco hoje não é a falta de insight, e sim o excesso de insight falso. Por isso a ferramenta é um filtro para uso semanal: `python signal_check.py export.csv --min-lift 5`.

1. **Saúde dos dados:** cinco checagens em que dados reais passam e dados quebrados ou sintéticos falham.
2. **Sinal ou ruído:** um segmento (plataforma, formato, categoria, faixa de creator, patrocínio) só é marcado como **SINAL** se passar em três testes:
   - é significativo mesmo depois da correção para muitos testes;
   - se repete na 1ª e na 2ª metade do período;
   - o ganho é de pelo menos 5%.

Resultado neste dataset:
```
5 ALERTAS de saúde: views quase constantes (variação de 1%), alcance não depende
de seguidores (0,005), likes não dependem de views (0,001), 0% de posts fracassados,
seguidores mudam a cada post do mesmo creator.
Resumo: 0 de 19 segmentos com sinal acionável.
```
Com os dados reais da P2, a mesma ferramenta passa a apontar onde vale investir.

---

## 4. Como usei IA na análise

| Etapa | O que foi feito | Decisão que tomei |
|---|---|---|
| Perfil dos dados | Claude carregou o arquivo e gerou as estatísticas descritivas | A variação de apenas 1% nas views levantou suspeita e mudou o rumo da análise |
| Hipótese de dados sintéticos | Comparei as métricas com uma Poisson teórica e medi as correlações | Testei primeiro se havia algum sinal, antes de sair procurando insights |
| Varredura | 85 testes estatísticos, com correção para múltiplos testes | Contei quantos resultados o acaso geraria, em vez de destacar os "significativos" isolados |
| Patrocínio | Regressão com 9 controles e comparação em 136 grupos parecidos | Reportei o intervalo de confiança, não só o p-valor |
| Teste fora da amostra | Ranking de 2023–24 testado em 2024–25; modelo testado no período seguinte | Mostrei que a análise que uma IA entregaria não se sustenta |
| Ferramenta | `signal_check.py` | Escolhi um filtro contra ruído em vez de um dashboard |

**Onde a IA teria errado sem supervisão:** com o brief colado, o caminho natural seria montar rankings e uma estratégia confiante em cima de diferenças de 0,05%. Aqui, a resposta correta é mostrar que os dados não sustentam essas conclusões e explicar como conseguir dados que sustentem.

---

Todos os arquivos estão em `baseline_limpo/`:
- `ENTREGA.md`: este relatório;
- `analise.py`: a varredura dos 85 testes;
- `analise2.py`: controles, testes fora da amostra, hashtags e as três armadilhas;
- `signal_check.py`: a ferramenta, já rodada neste dataset;
- `signal_check_output.txt`: a saída da ferramenta.

Posso transformar o relatório em uma página web privada para compartilhar com o Head de Marketing, se quiser.