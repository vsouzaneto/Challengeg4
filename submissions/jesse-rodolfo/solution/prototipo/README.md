# Protótipo: classificador e roteador de tickets (dataset 2)

Prova de viabilidade técnica da fase 2 (triagem e roteamento). Não é o piloto da fase 1.

## Como rodar (da raiz da submissão, com os CSVs em `solution/data/raw/`)

1. `bash solution/data/download.sh` baixa os datasets (precisa do `kaggle.json`).
2. `.venv/bin/python -I solution/prototipo/treinar.py` treina, imprime as métricas e salva `modelo.joblib` (ignorado pelo git).
3. `.venv/bin/python -I solution/prototipo/rotear.py "texto do ticket"` devolve categoria, confiança e rota.
4. `.venv/bin/python -m pytest solution/prototipo -q` roda os 5 testes (treina sozinho se faltar o modelo).
5. Limiar e portões são constantes no topo de `rotear.py` (`LIMIAR = 0.7`, `PORTOES`).

## Método

TF-IDF (1 a 2 gramas, `min_df=3`) + regressão logística. Remove "thanks", "thank", "regards", "best" e "annual leave" antes de treinar. Split 80/20 estratificado, seed 42: 38.269 para treino e 9.568 no held-out, nunca visto no treino.

## Resultado no held-out (9.568 tickets)

| Métrica | Valor |
|---|---|
| Acurácia | 85,69% |
| Classe majoritária (Hardware) | 28,47% |

Limiar de confiança (rota "humano" abaixo dele):

| Limiar | Cobertura (% acima do limiar) | Acurácia só nos aceitos | Aceitos |
|---|---|---|---|
| 0,5 | 82,7% | 92,1% | 7.914 |
| 0,6 | 73,1% | 94,6% | 6.990 |
| **0,7** | **62,9%** | **96,7%** | **6.021** |
| 0,8 | 52,0% | 98,0% | 4.977 |
| 0,9 | 38,7% | 99,3% | 3.706 |

Com o limiar de 0,7 e os portões `Purchase` e `Administrative rights`, 57,3% do held-out segue como "automático", com 96,5% de acerto. Outros 5,6% passam do limiar e vão para humano por serem portão.

## Limites

- A acurácia é contra o rótulo do dataset, e a auditoria mostrou ruído de rótulo (exemplos: "oracle issue" como Hardware; na cronometragem, a triagem humana sem ajuda acertou 1 de 5). O teto real é desconhecido.
- Hardware absorve erro das demais classes (coluna Hardware da matriz de confusão). Administrative rights tem recall baixo (216 de 352).
- As categorias do dataset 2 são de service desk interno de TI e RH, não as do dataset 1. Os dois portões de `PORTOES` são proposta para este dataset, decisão do Jessé a confirmar.
- Limiar de 0,7 foi escolhido pela tabela, não calibrado com tickets reais da operação. A regra de parada da fase 2 (pausar se menos de 60% passarem do limiar) está perto: 62,9%.
- O texto do dataset 2 já vem pré-processado. Em produção o classificador recebe o texto original, sem assinatura.
