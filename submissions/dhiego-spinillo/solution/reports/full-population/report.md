# Classificação da base completa do D2

**47.837 registros processados com o modelo local congelado. Nenhum novo treino ou chamada paga.**

## O que esta rodada acrescenta

Perfil integral de categorias, scores e **1.114 divergências** entre modelo e rótulo da base. Destas, **305** têm score ≥ 0,61. São casos para revisão: a divergência pode vir do modelo, do rótulo ou de ambiguidade. Score alto não confirma intenção nem autoriza procedimento.

**A evidência de desempenho continua sendo o teste original: 688/800 (86%).** As 1.192 previsões de validação/teste foram reproduzidas, incluindo scores dentro da tolerância de 1e-10. Não são novos exemplos. Alguns tickets de teste foram posteriormente examinados no desenvolvimento.

## Universos separados

| Universo | Registros | Concordâncias | Divergências | Concordância com rótulo |
|---|---:|---:|---:|---:|
| Treino | 45.790 | 44.885 | 905 | 98,02% |
| Validação | 392 | 342 | 50 | 87,24% |
| Teste original | 800 | 688 | 112 | 86,00% |
| Excluídos do treino por proximidade | 847 | 801 | 46 | 94,57% |
| Excluídos da validação por proximidade | 8 | 7 | 1 | 87,50% |

A concordância global é 97,67%; **não usar como acurácia independente**, pois 45.790 registros participaram do treino. A validação escolheu o limiar; os excluídos têm proximidade lexical com outros grupos e não são um novo teste. O teste contém dependência residual documentada na comparação.

## Distribuição de categorias

| Categoria | Rótulo da base | Sugestão local |
|---|---:|---:|---:|
| Access | 7.125 | 7.080 |
| Administrative rights | 1.760 | 1.705 |
| HR Support | 10.915 | 10.940 |
| Hardware | 13.617 | 13.846 |
| Internal Project | 2.119 | 2.076 |
| Miscellaneous | 7.060 | 7.054 |
| Purchase | 2.464 | 2.405 |
| Storage | 2.777 | 2.731 |

Hardware e RH concentram 24.532/47.837 rótulos (51,28%). Isso orienta uma amostra de revisão do domínio. Não mede demanda na empresa do desafio, urgência, carga de trabalho ou elegibilidade ao autosserviço.

## Uso na decisão

1. Manter classificação assistida: no teste, 44 dos 658 tickets acima do limiar divergiram (6,69%), acima da meta de 5%.
2. Revisar a taxonomia e as divergências antes de automatizar encaminhamentos. Hardware ↔ RH concentra 239 divergências na base inteira, majoritariamente usada no treino.
3. Avaliar intenção, tentativas, risco e completude separadamente. O D2 não possui referência para essas tarefas, nem estado da conta, notas internas ou resultado da resolução.
4. Medir elegibilidade e ganho no piloto. Não multiplicar os 30 mil tickets anuais pelo percentual acima do limiar para estimar saving.

## Rastreabilidade

- [Resumo JSON e metadados](summary.json).
- [Predição por registro — CSV comprimido](predictions.csv.gz): linha, partição, rótulo, sugestão e score; sem texto original.
- [Script](../../classificar_base_completa.py) verifica hashes do CSV/modelo, cobertura exclusiva do split e igualdade com a avaliação histórica.
- [Comparação Local × Jev](../../comparacao.md) preservada. Jev e LLM não foram executados sobre toda a base.

Reprodução, da pasta da submissão:

```bash
.venv/bin/python solution/classificar_base_completa.py data/dataset2.zip --output /tmp/g4-d2-integral
```

Comparar o JSON e o CSV com os arquivos versionados. Timestamp e duração dependem da execução. O resumo Markdown é gerado junto aos resultados; seus links pressupõem a estrutura versionada `solution/reports/full-population/`.
