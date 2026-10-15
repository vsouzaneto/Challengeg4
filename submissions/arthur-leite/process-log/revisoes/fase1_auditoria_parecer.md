# Parecer do Agente Juiz — Fase 1 (auditoria dos datasets)

**Revisor:** subagente independente, contexto limpo, postura adversarial (conforme `PROTOCOLO_JUIZ.md`).
**Insumos usados:** somente os dois CSVs brutos e o README do case (`challenges/process-002-support/README.md`). O script e o PROCESS_LOG do candidato **não** foram lidos.
**Método:** recálculo do zero em Python (pandas, scipy, scikit-learn). Trechos do código no fim do documento.

---

## 1. Vereditos por afirmação

| # | Afirmação (resumo) | Veredito | Número obtido pelo juiz | Comentário |
|---|---|---|---|---|
| A1 | DS1 tem 8.469 registros; enunciado fala em ~30.000 | **CONFIRMADA** | 8.469 linhas, 8.469 Ticket IDs únicos, 17 colunas. README, linha 45: "~30.000 registros com texto real" | O README também diz que `Ticket Type` tem 3 valores, mas o dataset tem 5 (Refund, Technical, Cancellation, Product inquiry, Billing). Vale citar como mais uma divergência entre enunciado e dados. |
| A2 | 100% das descrições têm placeholder; 16 frases de abertura; a mais comum cobre ~69% | **CONFIRMADA COM RESSALVA** | 100% contêm `{product_purchased}` literal; 156 tipos distintos de placeholder (`{error_message}`, `{product_id}`...). 16 primeiras frases distintas; "I'm having an issue with the X." = 69,3%. Nenhuma descrição contém o nome real do produto comprado (0,0%). | Números batem. Ressalva de redação: as descrições não são 16 textos. O restante após a 1ª frase tem 8.077 variações (com 392 descrições duplicadas). O ponto forte é outro: **a descrição não prevê nada**. Um TF-IDF + regressão logística sobre a descrição acerta Subject 6,4% (base majoritária 6,8%), Type 19,5% (base 20,7%) e Priority 24,9% (base 25,9%), ou seja, abaixo do chute. Esse é o argumento mais forte e deveria entrar na entrega. |
| A3 | FRT/TTR são timestamps, janela de ~27 h (31/05 a 02/06/2023); compra de 2020 a 2021 | **CONFIRMADA** | FRT: 31/05/2023 21:55 a 02/06/2023 00:54. TTR: 31/05 21:53 a 02/06 00:55. Amplitude total: 27h02min. Date of Purchase: 01/01/2020 a 30/12/2021. | Testei leituras alternativas: (a) TTR−FRT como duração; (b) \|TTR−FRT\|; (c) (TTR−FRT) mod 24h; (d) hora do dia de FRT/TTR como "hora de entrada"; (e) FRT − data de compra. Nenhuma produz diferença por prioridade, canal, tipo ou assunto (Kruskal-Wallis p entre 0,06 e 0,79). Nenhuma leitura transforma essas colunas em métrica operacional. |
| A4 | Entre Closed, ~49% (1.365/2.769) têm TTR < FRT | **CONFIRMADA** | 1.365/2.769 = 49,3%; 2 empates. TTR−FRT: mediana +0,17 h, faixa −23,2 h a +23,5 h. | A distribuição de TTR−FRT é estatisticamente igual à de dois timestamps sorteados de forma independente (KS contra pares embaralhados: p = 0,23). As duas colunas não têm ligação causal entre si. |
| A5 | CSAT só em Closed (2.769; 33%); distribuição uniforme (qui² p≈0,80) | **CONFIRMADA** | 2.769 notas, todas e só em Closed. Contagens 1–5: 553/549/580/543/544. Qui² = 1,67, p = 0,797. Média ≈ 3,0. | Ressalva leve: "só existe para Closed" é coerente com um processo real (pesquisa pós-fechamento). O que indica síntese é a uniformidade, não a ausência. |
| A6 | Nenhum par categórico com associação relevante; V máx ≈ 0,072; Type ⟂ Subject | **CONFIRMADA COM RESSALVA** | V máx = 0,0722 (Priority × Product, p = 0,26). Type × Subject: V = 0,034, p = 0,98. **0 de 21 pares** com p < 0,05. | O V máximo vem de pares com `Product` (42 níveis), e o V de Cramér sem correção de viés fica inflado com muitas categorias. Corrigido, fica ≈ 0. Recomendo citar "0 de 21 pares significativos" no lugar de "V máx 0,072", que soa como efeito pequeno quando na verdade é ruído. |
| A7 | Nada explica CSAT (KW para categóricas, Spearman para duração e idade; todos p > 0,25) | **CONFIRMADA COM RESSALVA** | KW: Type 0,70; Subject 0,81; Priority 0,63; Channel 0,28; Product 0,67; Gender 0,63. Spearman: Idade 0,83; TTR−FRT 0,254; \|TTR−FRT\| 0,78. Interações (Prioridade×Canal 0,72; Tipo×Assunto 0,17; Gênero×Produto 0,31). Decis de idade e de duração (não linear): 0,97 e 0,70. | Como afirmada, a frase está correta (a duração está no limite, p = 0,254). **Mas há variáveis com p < 0,05 que o candidato não lista:** hora do FRT (ρ = −0,040, p = 0,035), data de compra (ρ = −0,039, p = 0,041) e posição do FRT na janela (p = 0,046). Com cerca de 25 testes, 1 a 2 "significâncias" a 5% são o esperado por acaso, e nenhuma sobrevive a Bonferroni (limiar ≈ 0,002). Os efeitos são de ρ ≈ 0,04 (R² < 0,2%). Recomendo declarar explicitamente quantos testes foram feitos e que a correção para múltiplas comparações foi aplicada. Caso contrário, um avaliador pode "achar sinal" que o candidato não mencionou. |
| A8 | 67% não fechados (5.700), 2.881 Pending | **CONFIRMADA COM RESSALVA** | Open 2.819, Pending 2.881, Closed 2.769. Não fechados = 5.700 (67,3%). | Número correto. **Risco de interpretação:** as três categorias são estatisticamente equiprováveis (qui² uniforme p = 0,33). "67% de backlog" não é um achado operacional, é o resultado de um sorteio de 1/3 para cada status. Se a entrega usar esse número como "gargalo", cai na mesma armadilha que o candidato denuncia. Também não há data de abertura do ticket, então não dá para medir aging do backlog. |
| A9 | "O DS1 é aleatório; diferenças entre grupos estão dentro do ruído" | **CONFIRMADA COM RESSALVA (redação forte demais)** | Ver itens anteriores e os achados novos. | A conclusão prática está certa: o DS1 não sustenta diagnóstico de tempo nem de satisfação. Mas "aleatório" é impreciso por dois motivos: (1) há **estrutura determinística coerente** (máquina de estados de status, ver Achado N3); (2) há **um artefato não aleatório de geração** (timestamps derivam com o Ticket ID, ver Achado N1). A redação mais defensável é "sintético, com variáveis geradas de forma independente", junto com o tamanho de efeito que os testes conseguiriam detectar (ver seção 3). |
| A10 | DS2: 47.837 registros, sem nulos e sem duplicatas; texto real pré-processado; 8 classes desbalanceadas (Hardware ~28%, Admin rights ~4%); ruído de rótulo | **CONFIRMADA COM RESSALVA** | 47.837 × 2; 0 nulos; 0 linhas e 0 documentos duplicados; 0 documentos com rótulos conflitantes. Hardware 28,5%, HR 22,8%, Access 14,9%, Misc 14,8%, Storage 5,8%, Purchase 5,2%, Internal Project 4,4%, Admin rights 3,7%. 0% maiúsculas, 0% dígitos. Mediana de 26 tokens (máx. 981). TF-IDF + LR, 5-fold: **acurácia 86,1%**, macro-F1 0,859; pior classe Admin rights (recall 0,67). | "Real" não é verificável com certeza a partir dos dados, mas é muito plausível: há assinaturas, disclaimers jurídicos, cadeias "re:"/"sent", dias da semana e cargos ("engineer ext"). O "pré-processado" é parcial: o assunto do e-mail mantém stopwords ("issue with server process"; "the" aparece 1.924 vezes), números foram removidos e nomes, aparentemente, também. Isso degrada o texto ("please create confluence", sem "account"). Ruído de rótulo: na amostra de 32, julguei **5 rótulos claramente duvidosos e 3 ambíguos** (≈15–25%), coerente com o teto de ~86% do classificador linear. O DS2 não tem metadados (tempo, prioridade, canal, CSAT), então serve para automação/classificação, **não** para diagnóstico operacional. |

---

## 2. Achados novos

**N1. Artefato de geração nos timestamps (reforça a tese de síntese; não é sinal operacional).**
FRT e TTR se correlacionam com o Ticket ID (Spearman ρ = 0,14, p ≈ 10⁻²⁷ para FRT; ρ = 0,10, p ≈ 10⁻⁷ para TTR). Em decis de ID, a janela de cada registro tem sempre ~24 h de largura e desliza cerca de 3 h do primeiro ao último decil (mínimo de FRT vai de −2,07 h para +0,83 h em relação a 01/06 00:00; inclinação ≈ 0,42 h por 1.000 IDs). O padrão é típico de um gerador do tipo "agora + aleatório(0, 24 h)" rodando linha a linha durante umas 3 horas. Os e-mails são todos `@example.com/.org/.net` e a coluna `Resolution` é texto sem sentido no estilo Faker ("Offer investment fish.", "West decision evidence bit."), com 2.769 frases únicas. A pequena correlação FRT×TTR entre Closed (ρ = 0,055, p = 0,004) vem desse deslizamento comum, não de processo.
→ **Não é crítico contra o candidato.** É evidência adicional e mais "forense" de que o DS1 é sintético. Recomendo incluir.

**N2. Sinais "significantes" não reportados que um avaliador pode encontrar.** CSAT × hora do FRT (p = 0,035), CSAT × data de compra (p = 0,041) e CSAT × decil da hora do FRT (p = 0,042). Tudo isso desaparece com correção para múltiplas comparações e tem efeito irrelevante (ρ ≈ 0,04). Recomendo que a entrega diga isso de forma preventiva.

**N3. A estrutura de status é determinística e coerente, a única "lógica de processo" do DS1.** Open ⇒ sem FRT, sem TTR e sem CSAT (2.819). Pending ⇒ FRT presente, sem TTR (2.881). Closed ⇒ FRT, TTR, Resolution e CSAT presentes (2.769). Não há nenhuma exceção. Isso é útil para o modelo de dados do protótipo, mas também mostra que "Open" aqui significa "ainda sem primeira resposta".

**N4. Poder estatístico (o candidato deveria declarar).** Com cerca de 690 notas por grupo e desvio-padrão de 1,41, o efeito mínimo detectável (80% de poder, α = 5%) numa comparação de dois grupos de CSAT é ≈ **0,2 ponto na escala de 1 a 5**. Para associação entre categóricas com n = 8.469, detectam-se valores de V da ordem de 0,03 a 0,05. Ou seja, os testes **tinham poder** para achar efeitos operacionalmente modestos e não acharam. Isso fortalece a conclusão e deve ser dito.

**N5. Desvios mínimos de uniformidade.** Customer Gender (p = 0,007; "Other" 31,7%) e Ticket Subject (p = 0,02) não são perfeitamente uniformes. O desvio é pequeno e irrelevante, mas impede dizer que "todas as distribuições são uniformes".

**N6. Divergências do enunciado.** O README promete ~30.000 registros, "texto real de descrição e resolução", 3 tipos de ticket e colunas de "tempo até" (durações). Os dados entregam 8.469 registros, texto-modelo e lorem ipsum, 5 tipos e timestamps. Vale tabelar isso na entrega, porque é o argumento que justifica mudar de abordagem.

**Nenhum sinal real escondido foi encontrado no DS1.** Busquei em: texto da descrição × Subject/Type/Priority (classificador e qui²), palavras-chave × Subject (ex.: "password" → Account access 9,1% contra base de 6,0%, n = 230, compatível com ruído), Resolution (tamanho) × CSAT, idade e data de compra × todas as categóricas, relações não lineares por decis, interações de segunda ordem e quatro leituras alternativas das colunas de tempo.

---

## 3. Redação recomendada para o Diretor de Operações

> "Antes de qualquer diagnóstico, validei a base. O Dataset 1 (8.469 tickets, não os ~30 mil citados) é **sintético**. As descrições são 16 frases-modelo com campos não preenchidos (`{product_purchased}`), as resoluções são texto sem sentido e os 'tempos' são carimbos de data e hora espalhados numa única janela de 27 horas. Em metade dos tickets fechados, a resolução aparece antes da primeira resposta.
>
> Testei, com poder estatístico para detectar diferenças de cerca de 0,2 ponto de satisfação, se canal, prioridade, tipo, assunto, produto, perfil do cliente ou tempo influenciam a nota ou a resolução. **Nenhum efeito apareceu acima do que o acaso produziria.** Por isso não vou apresentar 'gargalos por canal' nem 'drivers de CSAT' com base nesses dados. Seriam números que parecem reais e levariam a decisões erradas.
>
> O que a base oferece é a **estrutura** da operação: o fluxo de status Aberto → Aguardando cliente → Fechado, a taxonomia de canais, prioridades, tipos e assuntos, e onde cada métrica deveria ser medida. Uso essa estrutura para desenhar o fluxo com IA. Para provar que a automação funciona, uso o Dataset 2 (≈48 mil chamados reais de TI), em que um classificador simples já acerta ≈86% das categorias. O primeiro passo do projeto real é instrumentar a operação para coletar tempos e satisfação confiáveis."

Evitar: "o dataset é aleatório" sem qualificar, "67% de backlog" como achado, e "não há nada a aproveitar".

**O que ainda se extrai legitimamente do DS1:**
- O esquema de dados e a máquina de estados de status (N3), como molde para o protótipo e para o plano de instrumentação.
- A taxonomia de rótulos (5 tipos, 16 assuntos, 4 canais, 4 prioridades, 42 produtos), útil como espaço de categorias de um roteador.
- O volume relativo por categoria só como ilustração de mix, deixando claro que é sintético e ≈ uniforme.
- As 16 frases-modelo como casos de teste de fumaça para o protótipo (nunca como dado de treino ou avaliação).
- Um "anti-exemplo" didático: demonstrar que um classificador treinado na descrição do DS1 fica no nível do chute, enquanto no DS2 chega a 86%. Isso mostra rigor e justifica a escolha do DS2.

---

## 4. Código executado (trechos principais)

```python
import pandas as pd, numpy as np, re, itertools
from scipy import stats
d = pd.read_csv('.../ds1_customer_support/customer_support_tickets.csv')
N = len(d)                                                  # 8469

# A2 – placeholders e frases de abertura
desc = d['Ticket Description'].astype(str)
desc.str.contains('{product_purchased}', regex=False).mean() # 1.0
d2 = desc.str.replace(r'\{[a-z_]+\}', 'X', regex=True)
first = d2.str.split(r'(?<=[.!?])\s', n=1, regex=True).str[0]
first.value_counts(normalize=True)                          # 16 frases; topo 0.6929
np.mean([p in s for p, s in zip(d['Product Purchased'], desc)])  # 0.0

# A3/A4 – tempos
fr = pd.to_datetime(d['First Response Time']); tr = pd.to_datetime(d['Time to Resolution'])
cl = d['Ticket Status'] == 'Closed'
dd = (tr - fr)[cl].dt.total_seconds() / 3600
(dd < 0).sum(), (dd < 0).mean()                             # 1365, 0.493
pd.crosstab(d['Ticket Status'], [fr.notna(), tr.notna()])   # máquina de estados

# A5 – CSAT uniforme
o = d['Customer Satisfaction Rating'].value_counts().sort_index()
stats.chisquare(o.values)                                   # stat 1.67, p 0.797

# A6 – Cramér's V em todos os pares
def cv(a, b):
    ct = pd.crosstab(a, b); chi, p, *_ = stats.chi2_contingency(ct)
    return np.sqrt(chi / ct.values.sum() / (min(ct.shape) - 1)), p
cols = ['Ticket Type','Ticket Subject','Ticket Priority','Ticket Channel',
        'Product Purchased','Customer Gender','Ticket Status']
[(a, b, *cv(d[a], d[b])) for a, b in itertools.combinations(cols, 2)]  # 0/21 com p<0,05

# A7 – CSAT vs. tudo (inclui leituras alternativas de tempo)
c = d[cl].copy(); y = c['Customer Satisfaction Rating']
c['dur_h'] = dd; c['dur_mod24'] = dd % 24
c['fr_hour'] = fr[cl].dt.hour + fr[cl].dt.minute / 60
for col in ['Ticket Type','Ticket Subject','Ticket Priority','Ticket Channel','Product Purchased','Customer Gender']:
    stats.kruskal(*[v.values for _, v in y.groupby(c[col])])
for col in ['Customer Age','dur_h','dur_mod24','fr_hour', ...]:
    stats.spearmanr(c[col], y, nan_policy='omit')
# duração (3 leituras) por prioridade
stats.kruskal(*[v.values for _, v in c['dur_mod24'].groupby(c['Ticket Priority'])])

# N1 – artefato de geração
stats.spearmanr(d['Ticket ID'], fr, nan_policy='omit')     # rho 0.14, p ~1e-27
d.groupby(pd.cut(d['Ticket ID'], 10))[...].agg(['min','median','max'])  # janela de 24h deslizando ~3h

# Texto do DS1 não prevê nada
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
X1 = TfidfVectorizer(min_df=2).fit_transform(d['Ticket Description'])
for t in ['Ticket Subject','Ticket Type','Ticket Priority']:
    p1 = cross_val_predict(LogisticRegression(max_iter=2000), X1, d[t], cv=5)
    (p1 == d[t]).mean()                                     # 0.064 / 0.195 / 0.249 (< base majoritária)

# A10 – DS2
e = pd.read_csv('.../ds2_it_tickets/all_tickets_processed_improved_v3.csv')
e.shape, e.isna().sum(), e.duplicated().sum(), e['Document'].duplicated().sum()  # (47837,2), 0, 0, 0
e['Topic_group'].value_counts(normalize=True)
X = TfidfVectorizer(ngram_range=(1,2), min_df=2, sublinear_tf=True).fit_transform(e['Document'])
p = cross_val_predict(LogisticRegression(max_iter=2000, C=5), X, e['Topic_group'],
                      cv=StratifiedKFold(5, shuffle=True, random_state=0))
(p == e['Topic_group']).mean()                              # 0.861
e.sample(32, random_state=42)                               # leitura manual: 5 duvidosos + 3 ambíguos
```

Amostra manual do DS2 (random_state = 42), rótulos julgados duvidosos: #2 Hardware ("oracle... rights query... full control for codes", parece Access ou Admin rights), #6 Hardware (configuração de web app, parece software/Misc), #11 Administrative rights (troca de senha e login, parece Access), #17 Hardware (acesso a arquivos, parece Storage ou Access), #21 HR Support (papéis em módulos Oracle, parece Access). Ambíguos: #12, #19, #24.
