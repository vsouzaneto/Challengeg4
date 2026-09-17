<!-- Gerado por solution/analysis/05_report.py a partir de docs/templates/modelo.md.tmpl. Não edite à mão. -->

# Classificador e roteamento: como foi construído e avaliado

## Resumo

| | Resultado no teste (IC 95%) |
|---|---|
| Acurácia do classificador | **86,0%** (85,2%–86,7%), contra 28,5% da classe mais comum |
| F1 macro | **0,856** (0,846–0,864) |
| Tickets roteados automaticamente (política completa da API) | **65,3%** (64,2%–66,4%) |
| Acerto nos roteados automaticamente | **94,9%** (94,3%–95,6%) |
| Pedidos de privilégio que foram automaticamente para outra fila | **5 de 264** (1,9%) |

## Dados e partições

Dataset 2: 47.837 tickets de TI interna rotulados em 8 categorias. Partição estratificada com semente fixa:

| Partição | Tickets | Para que serve |
|---|---|---|
| Treino | 33.485 | Ajuste do TF-IDF e dos modelos |
| Validação | 7.176 | **Todas** as escolhas: modelo, regularização, poda, limiares |
| Teste | 7.176 | Avaliação final, feita **uma vez** depois de congelar as escolhas |

### Por que refizemos a avaliação

A primeira versão usou um único conjunto de 20% para comparar modelos, escolher poda e limiares **e** reportar resultado: 86,4% de acurácia, F1 0,865, 69,7% automáticos com 95,7% de acerto. Esses números ficam registrados como **exploratórios**. A revisão cruzada (Codex) apontou o problema e refizemos com treino, validação e teste.

**Ressalva honesta:** decisões de *desenho* foram tomadas olhando aquele primeiro conjunto: usar regressão logística, criar o guarda de domínio, ignorar stopwords no guarda, podar coeficientes. O teste atual não é "virgem" em sentido estrito. Os *valores* (C, poda, limiares) foram re-selecionados só na validação.

## Seleção (somente validação)

| Modelo (validação) | Acurácia | F1 macro |
|---|---|---|
| Baseline: sempre a classe mais comum | 28,5% | 0,055 |
| TF-IDF + Complement Naive Bayes | 80,6% | 0,793 |
| TF-IDF + Linear SVM (sem probabilidade) | 86,5% | 0,867 |
| TF-IDF + Regressão Logística (C=1) | 85,8% | 0,852 |
| TF-IDF + Regressão Logística (C=4) | 86,7% | 0,867 |
| TF-IDF + Regressão Logística (C=10) | 86,5% | 0,867 |

Critérios, definidos antes de olhar o teste:

- Modelo: maior F1 macro na validação entre modelos com probabilidade (necessária para limiar e fila humana).
- Poda: maior ε com queda de F1 macro de validação ≤ 0.2 ponto.
- Guarda de domínio: quantil 5% da fração de palavras conhecidas na validação.
- Limiares de confiança e privilégio: maior cobertura automática com a política completa, sujeita a acerto ≥ 95% nos automáticos e vazamento ≤ 2% dos pedidos de privilégio.

Escolhas congeladas: C = 4, poda ε = 0,30, limiar de confiança = 65%, guarda de domínio = 93%, limiar de probabilidade de privilégio = 5%.

O SVM linear tem desempenho equivalente, mas não fornece probabilidade. Sem probabilidade não há limiar de confiança nem fila humana, por isso escolhemos a regressão logística.

## Desempenho do classificador no teste

| Categoria | Precisão | Recall | F1 | Tickets no teste |
|---|---|---|---|---|
| Hardware | 81,0% | 89,6% | 0,851 | 2.042 |
| HR Support | 86,3% | 88,4% | 0,874 | 1.638 |
| Access | 90,6% | 85,4% | 0,879 | 1.069 |
| Miscellaneous | 83,3% | 83,4% | 0,833 | 1.059 |
| Storage | 95,3% | 82,9% | 0,887 | 416 |
| Purchase | 96,5% | 88,1% | 0,921 | 370 |
| Internal Project | 92,2% | 78,6% | 0,849 | 318 |
| Administrative rights | 87,1% | 66,3% | 0,753 | 264 |

A classe mais difícil é **Administrative rights** (recall 66,3%): pedidos de privilégio se confundem com Access e Hardware. Por isso a política de roteamento trata essa categoria à parte (abaixo).

## Roteamento: o que o app realmente faz

Os números abaixo vêm de `scripts/evaluate-routing.ts`, que roda **as mesmas funções da API** (`predict` e `decideRoute`) sobre os 7.176 tickets do teste. A ordem da política é:

1. **Escalação:** termo de risco ou urgência no texto → atendente sênior, sem rascunho de IA.
2. **Guarda de domínio:** vocabulário pouco conhecido pelo modelo → revisão humana.
3. **Confiança:** abaixo do limiar → revisão humana.
4. **Privilégio administrativo:** previsto como tal → revisão humana (aprovação obrigatória).
5. **Risco de privilégio:** probabilidade de privilégio acima do limiar, mesmo prevendo outra categoria → revisão humana.
6. Caso contrário → **roteamento automático** para a fila prevista.

| Destino | Tickets | Proporção |
|---|---|---|
| Automático | 4.687 | 65,3% |
| Revisão humana | 2.020 | 28,1% |
| Escalação | 469 | 6,5% |

| Motivo | Tickets | Proporção |
|---|---|---|
| Roteado automaticamente | 4.687 | 65,3% |
| Confiança abaixo do limiar | 1.468 | 20,5% |
| Vocabulário fora do padrão (guarda de domínio) | 271 | 3,8% |
| Previsto como privilégio administrativo | 129 | 1,8% |
| Probabilidade de privilégio acima do limiar | 152 | 2,1% |
| Termo de risco/urgência | 469 | 6,5% |

**Por categoria real:**

| Categoria real | Tickets | Automático | Revisão humana | Escalação | Acerto nos automáticos |
|---|---|---|---|---|---|
| Hardware | 2.042 | 1.260 | 600 | 182 | 95,4% |
| HR Support | 1.638 | 1.211 | 365 | 62 | 95,6% |
| Access | 1.069 | 747 | 233 | 89 | 95,6% |
| Miscellaneous | 1.059 | 666 | 328 | 65 | 93,5% |
| Storage | 416 | 288 | 107 | 21 | 94,1% |
| Purchase | 370 | 308 | 58 | 4 | 95,8% |
| Internal Project | 318 | 202 | 96 | 20 | 92,1% |
| Administrative rights | 264 | 5 | 233 | 26 | 0,0% |

**Vazamento de pedidos de privilégio:** dos 264 tickets cujo rótulo real é Administrative rights, 5 (1,9%) foram previstos como outra categoria e roteados automaticamente: Hardware (5). Na validação foram 0,4%. A regra de risco de privilégio mandou 152 tickets para aprovação humana, além dos 129 previstos diretamente como privilégio.

**Leitura:** o acerto nos automáticos ficou em 94,9% no teste, contra 95,1% na validação. O critério de seleção pedia 95% na validação, e o teste fica no limite inferior dessa meta. Recomendamos operar primeiro em modo sombra e reajustar o limiar com dados da operação.

A política TypeScript concorda 100% com a réplica Python usada na seleção, verificado em todos os tickets de validação e teste.

## Guarda de domínio: confiança alta não é garantia

Aplicado aos tickets do Dataset 1 (e-commerce), o modelo passa do limiar de confiança em 56,7% dos casos, e 91% desses viram "Hardware", inclusive pedidos de pagamento. **O modelo erra com convicção fora do domínio em que foi treinado.** O guarda (fração de palavras de conteúdo conhecidas pelo modelo) barra 98,6% desses tickets, contra 3,9% do teste do próprio domínio. Com a política completa, o Dataset 1 ficaria 0,1% automático, 83,6% revisão humana e 16,3% escalação.

**Implicação:** em produção o classificador precisa ser re-treinado com o histórico rotulado da própria operação. Um modelo "pronto" de outro contexto não serve.

## Limitações do modelo

- **Correlação espúria visível na explicação:** num ticket de novo funcionário, o termo "belgrade" (nome de escritório) é um dos que mais puxam para HR Support. O modelo aprendeu localização como sinal. Mostrar os termos que explicam cada decisão foi o que revelou isso, e é um motivo para manter a explicação visível ao agente.
- **Texto pré-processado:** o Dataset 2 vem em minúsculas, sem dígitos e anonimizado. Texto cru de outra empresa tende a ter desempenho menor.
- **Termos de escalação** são heurística escrita à mão. O Dataset 2 não tem rótulo de prioridade para validá-los.
- **Probabilidades** não foram recalibradas. O limiar foi escolhido empiricamente na validação.

## Reprodução

```bash
bash solution/pipeline.sh   # 01 → 03 → evaluate-routing → 02 → 05 → testes
```

Sem Kaggle, o próprio repositório tem o necessário para os testes: `analysis/artifacts/` guarda as partições de validação e teste e as predições do Python (`npm test` roda paridade, política e APIs).
