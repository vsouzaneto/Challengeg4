# Parecer do Agente Juiz — Fase 3 (benchmark de triagem + modelo de desperdício/ROI)

Revisor independente e adversarial. Recalculei todos os números do zero, com código próprio, a partir de `data/ds2_it_tickets/all_tickets_processed_improved_v3.csv` e dos caches (`ds2_minilm.npy`, `llm_gemini-3.5-flash-lite_*.jsonl`). Só li o código do candidato depois de terminar o recálculo. Nenhuma API de LLM foi chamada.

## 1. Vereditos por afirmação

| # | Afirmação | Veredito | Número do juiz | Comentário |
|---|---|---|---|---|
| B1 | A (TF-IDF + LogReg C=5): acc 86,0%, F1m 0,86 | **CONFIRMADA** | acc 0,8603; F1m 0,8597 | Os splits batem (33.485 / 4.784 / 9.568). Não há duplicatas exatas no dataset nem entre treino e teste. Há quase-duplicatas (seção 2.1), mas elas mexem pouco na acurácia: cerca de 0,6 p.p. |
| B2 | B (MiniLM + LogReg C=10): acc 80,8%, F1m 0,81, pior que A | **CONFIRMADA** | acc 0,8077; F1m 0,8130 | Ressalva menor: o MiniLM é pequeno e foi usado congelado. A conclusão vale para "embeddings genéricos + classificador linear", não para embeddings em geral. |
| B3 | LLM: zero-shot 44,0% (F1m 0,41); few-shot 48,0% (F1m 0,49); A na mesma amostra 85,0% | **CONFIRMADA COM RESSALVA** | zero 0,440 / 0,412; few 0,480 / 0,490; A 0,850 | Os números são exatos e os 400 ids são os da amostra declarada. IC95% por bootstrap: zero-shot 39–49%, few-shot 43,5–53%. A ressalva é que o desenho do teste favorece o modelo local (seção 2.3). |
| B4 | Faixas: limiar auto 0,71, cobertura 74,2%, precisão 95,1%; sugere 24,1% com top-2 de 90,3%; humano 1,8% | **CONFIRMADA COM RESSALVA** | Limiar exato 0,7085: auto 74,15% / 95,11%; sugere 24,08%, top-2 90,28% (top-1 61,8%); humano 1,77%. Com grade de 0,01: 73,9% / 95,2% | O método está correto: o limiar é escolhido na validação e medido no teste. Mas os 95% estão no limite. No teste, o IC95% da precisão vai de 94,7% a 95,7%, e a chance de ficar abaixo de 95% é de cerca de 20%. Se a escolha do limiar também for reamostrada, a precisão varia de 94,6% a 95,9% e a cobertura de 71,4% a 76,2%. Na faixa auto, Hardware tem precisão de 92,6%, abaixo da meta. E 42 de 352 tickets de "Administrative rights" (12%) são roteados automaticamente para a fila errada, quase todos para Hardware. É a categoria mais sensível do ponto de vista de segurança. |
| B5 | "LLMs genéricos perdem porque as categorias são convenções internas ('Miscellaneous', 'Internal Project'); um modelo simples vence por ~40 pontos, custa zero e não envia dados para fora" | **CONFIRMADA COM RESSALVA (a redação deve mudar)** | Diferença de 37 a 41 p.p. Tirando Misc/IP, o LLM acerta só 49–50% | O mecanismo apontado explica só parte do resultado. Fora de Misc/IP o LLM continua em torno de 50%: acerta 38–41% de Hardware, 37–42% de HR Support e 20–47% de Admin rights. Ou seja, todas as categorias seguem a convenção de rotulagem da organização, não só as duas citadas. Além disso, o LLM foi testado em condições desfavoráveis (seção 2.3). "Custa zero" não é verdade no sentido estrito: o custo por ticket é praticamente nulo, mas há custo de treino, integração, monitoramento e retreino. E "vence por ~40 pontos" vale só para este LLM, com este prompt e este texto. |

## 2. Bugs e riscos encontrados

### 2.1 Vazamento por quase-duplicatas: baixo
- Duplicatas exatas: 0, no dataset e também entre teste e treino.
- Similaridade de cosseno (MiniLM) entre cada ticket de teste e o vizinho mais próximo no treino: 2,0% do teste tem similaridade ≥ 0,99, 8,2% tem ≥ 0,95 e 16,5% tem ≥ 0,90. Nesses casos o vizinho tem o mesmo rótulo em 95–97% das vezes.
- Com TF-IDF, 5,7% do teste tem similaridade ≥ 0,90 com algum ticket de treino. O modelo A acerta 95,6% desses e 85,4% dos demais. Sem esses ~6% de quase-duplicatas, a acurácia cai de 86,0% para 85,4%. A inflação é de cerca de 0,6 p.p. e não muda nenhuma conclusão, mas vale reportar "85–86%".
- Recomendação para a operação real: separar treino e teste por tempo (treinar no passado, testar no futuro). Tickets gerados por templates recorrentes podem inflar o resultado mais em produção do que um split aleatório mostra.

### 2.2 Bugs de código: nenhum que altere resultado
- `benchmark.py`: a função `limiar_para_precisao` escolhe o ponto mais profundo da curva em que a precisão acumulada ainda é ≥ 95%. Na validação isso dá exatamente 95,03%, ou seja, maximiza a cobertura encostando na meta. Não é bug, mas explica por que o teste fica no limite. Para ter folga, use alvo de 96% ou o limite inferior de um intervalo de confiança.
- `REVISAO_AUTO_MIN = 0.17` arredonda 10 s (0,1667) e gera diferenças de ±2 h. É irrelevante.
- `llm_classify.py`: os exemplos few-shot saem de `tr` (os 80% de treino + validação), então não há vazamento do teste. Mas a associação id→predição depende de o LLM devolver os ids certos dentro do JSON do lote, e o código não confere se cada id voltou uma única vez. Os 400 ids batem, então o risco é baixo, mas essa checagem deveria existir.
- A acurácia do LLM varia com a posição do ticket no lote. Por quartil de posição, o zero-shot acerta 45%, 57%, 34% e 40%. Pode ser ruído (n=100 por quartil), mas também é compatível com degradação causada pelo lote de 20.

### 2.3 A comparação com o LLM é parcialmente um espantalho
Os fatores abaixo desfavorecem o LLM. Nenhum deles é um erro quando visto sozinho.
1. **O texto chega pré-processado:** minúsculas, sem stopwords, sem pontuação e sem nomes. Exemplo real do dataset: "user user hello assign opportunities head architecture cannot him interface please his user configured thank". Um modelo de bag-of-words não perde nada com isso. Um LLM perde a sintaxe, que é justamente onde ele é forte.
2. **Foi usado o modelo mais barato da família (flash-lite)**, com temperatura 0 e sem raciocínio.
3. **O prompt traz só os nomes das categorias**, sem definição operacional. Sem definição, é impossível adivinhar o que cabe em "HR Support" ou "Miscellaneous" num helpdesk de TI.
4. **São 3 exemplos por classe, cortados em 300 caracteres**, e os mesmos 24 exemplos em todos os lotes. O modelo A aprendeu com 33.485 exemplos.
5. **Cada chamada classifica um lote de 20 tickets**, o que permite interferência entre tickets e efeito de posição.
6. O corte em 1.200 caracteres **não** é problema: a mediana dos textos tem 175 caracteres e só 3% passam de 1.200.

Um LLM mais forte, com definições das categorias, dezenas de exemplos escolhidos por similaridade (kNN few-shot) e um ticket por chamada provavelmente chegaria bem mais perto. A conclusão justa é **"um LLM genérico sem o contexto da organização não substitui o histórico rotulado"**, e não "LLM perde para modelo simples".

### 2.4 Calibração e faixas
- A calibração é boa e levemente subconfiante: ECE ≈ 0,032. Com confiança entre 0,4 e 0,7, a acurácia real fica 5 a 9 p.p. acima da confiança declarada. Como o limiar é escolhido empiricamente, isso não invalida as faixas.
- Na faixa "sugere", a primeira sugestão acerta só **61,8%**, e a categoria certa fica fora das 2 sugestões em **9,7%** dos casos. Se o atendente ancorar e aceitar sempre a primeira sugestão, o erro nessa faixa sobe para 38%, e não fica nos 15% de hoje.
- Precisão por categoria prevista, na faixa auto: Access 97,1%, Admin rights 95,7%, HR 95,8%, **Hardware 92,6%**, Internal Project 96,5%, **Misc 94,6%**, Purchase 99,0%, Storage 97,8%. Hardware funciona como "ralo" dos erros: recebe na faixa auto 41 tickets de Admin rights, 40 de HR e 25 de Access. Recomendo um limiar por categoria (mais alto para Hardware) ou uma regra que impeça o roteamento automático de Admin rights para outra fila.

### 2.5 Riscos do modelo de desperdício/ROI (Parte 2)
**Aritmética: CONFIRMADA.** Recálculo:

| Cenário | Horas hoje | Horas com IA | Horas recuperadas | FTE | R$/ano |
|---|---|---|---|---|---|
| Conservador | 890 | 222 | 668 | 0,38 | 25,5 mil |
| Base | 1.792 | 295 | 1.498 | 0,86 | 57,3 mil |
| Otimista | 3.112 | 413 | 2.699 | 1,54 | 103,2 mil |

O custo/hora de R$ 38,24 e o FTE de 1.747 h também conferem.

**Premissas e enquadramento: CONFIRMADA COM RESSALVA.** Um CFO vai apontar estas fragilidades:
1. **"Taxa de transferência" não é "erro de categorização".** A fonte (MetricNet/ICMI, via GB Advisors) existe e traz os 15–25% e os +2,8/+4,9 min. Mas ela fala de transferências em contact center, principalmente por telefone. Isso inclui **escalonamentos previstos no processo** (N1→N2, especialista), que continuariam existindo mesmo com triagem perfeita. Tratar os 15% inteiros como "roteado errado" superestima o retrabalho evitável. Sugestão de redação: "taxa de transferência de 15–25% (MetricNet/ICMI); assumimos que só *uma parte* disso é erro de triagem: 5% no conservador, 8% no base, 12% no otimista". No cenário base, usar 5% em vez de 15% reduz a recuperação de 1.498 h para 1.353 h. O efeito é modesto porque o retrabalho responde por só 16% das horas de hoje.
2. **O resultado depende quase todo de uma premissa de fonte fraca.** No cenário base, 1.500 das 1.792 h gastas hoje vêm da premissa de 3 min de triagem por ticket, tirada de blogs de fornecedores (o próprio candidato reconhece o viés). Com 1,5 min, a recuperação cai para 761 h (0,44 FTE). Na prática, o ROI se resume a quanto tempo a equipe gasta hoje classificando tickets. O texto deveria dizer isso de forma explícita, e essa deveria ser a primeira medição do piloto (cronometrar 50 triagens).
3. **Inconsistência de referência (crítica).** O erro da IA (4,9% na faixa auto) é medido **contra o rótulo humano**. Já o erro humano de hoje (15%) é uma premissa **contra a verdade**. Se os humanos erram 15%, os rótulos de treino carregam esse ruído, e uma IA que concorda 95% com eles reproduz parte desses erros. Portanto, a queda de 15% para 7,5% no roteamento errado **não está demonstrada**: ela compara duas réguas diferentes. Só passaria a valer se os rótulos do DS2 fossem auditados ou corrigidos (por exemplo, usando o rótulo final após a resolução).
4. **Mudança de domínio.** O desempenho de 74% de cobertura com 95% de precisão foi medido num helpdesk interno de TI, em inglês, com 47 mil rótulos. A operação do case é suporte ao cliente, com cerca de 30 mil tickets/ano por e-mail, chat, **telefone** e redes sociais. O modelo terá de ser retreinado no histórico do cliente, cuja qualidade de rótulo é desconhecida. Num cenário de domínio pior (auto 55% com 92% de precisão, sugere 35%, humano 10%), a recuperação no cenário base cai para 1.292 h. E ligações telefônicas nem passam por triagem de texto.
5. **Premissas otimistas sem fonte.** "10 s para conferir" um ticket automático e "30 s para escolher entre 2" não têm fonte. Com 20 s e 45 s, a recuperação no base fica em 1.406 h. Supor que o humano erra na faixa "sugere" o mesmo que erra hoje **não é conservador**: se ele ancorar na primeira sugestão, o erro chega a 38% e a recuperação no base cai para 1.389 h.
6. **Cenário combinado plausível:** triagem de 2 min, erro de triagem de 8%, 20 s/45 s e domínio pior dão **cerca de 710 h/ano, 0,41 FTE e R$ 27 mil**. Esse é o conservador de verdade, e não o base.
7. **O número é benefício bruto, não ROI.** Falta o lado do investimento: integração com o helpdesk, rotulagem e limpeza do histórico, retreino periódico, monitoramento e horas do time de dados. Além disso, os R$ 57 mil são **valor de tempo liberado**, não economia de caixa. O próprio texto diz que "não é demissão", então a folha não diminui. Um CFO vai perguntar qual é o payback e qual linha do P&L muda.
8. **Escala.** 0,9 FTE é pouco num time que atende 30 mil tickets/ano. Isso não é defeito, mas a triagem automática deve ser apresentada como **habilitadora** (menos espera em fila errada, base para roteamento e respostas sugeridas), e não como o grande ganho financeiro.

## 3. Redações recomendadas

**B5 (substituir por):**
> "No nosso teste, um LLM genérico (Gemini flash-lite, que recebeu só os nomes das categorias e 3 exemplos por classe, e leu o texto já pré-processado) acertou 44–48% das categorias. Um classificador simples, treinado em 33 mil tickets históricos da própria organização, acertou 85–86%. O motivo principal é que as categorias seguem convenções internas de rotulagem: mesmo em 'Hardware' e 'HR Support' o LLM errou mais da metade. Não testamos um LLM mais forte, com definições das categorias e exemplos escolhidos por similaridade, o que provavelmente reduziria a diferença. A lição prática é que **o ativo é o histórico rotulado da empresa**. O modelo local tem custo por ticket praticamente nulo, responde em milissegundos e não envia dados a terceiros. Os custos que existem são de manutenção e retreino."

**B4 (acrescentar):**
> "Na faixa automática (74% dos tickets), a precisão medida é de 95% (IC95% ≈ 94,6–95,9%), e em Hardware fica abaixo disso (92,6%). Recomendamos começar com um limiar mais alto (por exemplo, 0,80, que dá 66% de cobertura com 96,8% de precisão) e com regras próprias para categorias sensíveis. Admin rights é o caso principal: hoje, 12% desses tickets vão automaticamente para Hardware."

**ROI (substituir o enquadramento do resultado por):**
> "Esta é uma estimativa de **tempo liberado**, não de economia de caixa: entre ~700 h/ano (0,4 FTE, ~R$ 27 mil) e ~1.500 h/ano (0,9 FTE, ~R$ 57 mil). O valor depende sobretudo do tempo que a equipe gasta hoje para classificar cada ticket. Essa premissa responde por 84% do total no cenário base e vem de fonte fraca. A redução do roteamento errado só se confirma se o histórico de rótulos for confiável, e isso ainda não foi verificado. A 'taxa de transferência' de 15–25% (MetricNet/ICMI) inclui escalonamentos legítimos, por isso usamos só uma fração dela como erro de triagem. Os custos de implantação e manutenção ainda não foram descontados. Antes de qualquer decisão financeira, o piloto mede três coisas: minutos de triagem por ticket, % de reatribuições e tempo de espera em fila errada."

## 4. Código executado pelo juiz (trechos)

```python
# Splits e classificadores (j1.py)
rest,te=train_test_split(d,test_size=0.2,stratify=d.Topic_group,random_state=42)
tr,va=train_test_split(rest,test_size=0.125,stratify=rest.Topic_group,random_state=42)
vec=TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True)
A=LogisticRegression(C=5,max_iter=3000).fit(vec.fit_transform(tr.Document),tr.Topic_group)
# -> A acc 0.8603 f1m 0.8597
Bm=LogisticRegression(C=10,max_iter=3000).fit(E[tr.index],tr.Topic_group)   # -> 0.8077 / 0.8130
s400,_=train_test_split(te,train_size=400,stratify=te.Topic_group,random_state=7)
# zero-shot 0.440/0.412 ; few-shot 0.480/0.490 ; A na amostra 0.850 ; ids batem 400/400
```
```python
# Faixas, bootstrap e por classe (j2.py / j3.py)
t1=min(t for t in grid if okv[cv>=t].mean()>=0.95)   # grade 0.01 -> 0.71
# teste: cov 0.739, prec 0.952 ; bootstrap prec IC95 [0.947,0.957], P(<.95)=0.20
# limiar reamostrado na validação: [0.68,0.71,0.74] -> prec teste [0.946,0.959], cov [0.714,0.762]
# precisão auto por classe: Hardware 0.926, Misc 0.946 ; Admin rights->Hardware auto-errados: 41
# ECE 0.032 (subconfiante em 0.4-0.7)
```
```python
# Quase-duplicatas (j3.py)
M=Et@Er.T  # MiniLM normalizado: 2.0% do teste com sim>=0.99, 16.5% com >=0.90
# TF-IDF sim>=0.90: 5.7% do teste; acc A 95.6% nesses vs 85.4% no resto
```
```python
# LLM por classe (j4.py): zero-shot Hardware 0.38, HR 0.42, Admin 0.20, Misc 0.17
# sem Misc/Internal Project: zero 48.9%, few 50.5%
```
```python
# ROI (j5.py): reproduz 668/1498/2699 h; sensibilidades:
calc(3,.05,3.9)                      # erro de triagem 5%      -> 1353 h
calc(3,.15,3.9,err_sug=.382)         # ancoragem no top-1      -> 1389 h
calc(1.5,.15,3.9)                    # triagem 1,5 min         ->  761 h
calc(2,.08,3.9,auto=.6,sug=.32,hum=.08,prec=.93,rev=20/60,esc=.75)  # combinado -> 712 h, 0,41 FTE, R$ 27,2 mil
```

Os scripts completos estão no scratchpad da sessão do juiz (j1.py a j5.py).

**Fonte verificada:** GB Advisors, "What Reassignments Really Cost" (https://www.gb-advisors.com/blog/what-reassignments-really-cost). O texto cita MetricNet/ICMI: transferência de 15–25% e +2,8 min (warm) / +4,9 min (cold). O contexto é transferência em contact center, não erro de categorização.
