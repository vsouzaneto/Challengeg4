# Jev ou classificador local?

**Execução em 21/09/2026.** Escolha: TF-IDF + regressão logística para sugerir categoria; confirmação humana em todos os casos. [Resultados completos](reports/comparison/summary.json).

| Mesmo teste reservado | Classificador local | Jev 1.13.0 |
|---|---:|---:|
| Tickets | 800 | 800 |
| Acertos | 688 (86,00%) | 362 (45,25%) |
| F1 macro — peso igual por categoria | 0,8511 | 0,4200 |
| Latência mediana por ticket | 0,68 ms | 273,15 ms |
| Falhas de API/contrato no lote | 0 | 0 |
| Limiar que atendeu ao critério na validação | 0,61 | Nenhum |

Prever sempre Hardware acertaria 28,50% no teste. A diferença pareada de acurácia local − Jev foi de 40,75 pontos percentuais; intervalo bootstrap de 95%: 37,00 a 44,63 pontos. Há dependência residual entre textos: o intervalo por linha pode ser estreito.

## O que comparamos

O local aprendeu categorias com 45.790 exemplos rotulados. Jev recebeu apenas o texto e definições das oito categorias, sem exemplos de treino nessa execução. Comparamos dois sistemas nessas condições, não superioridade universal de arquiteturas. O rótulo `Topic_group` é a referência disponível, não uma taxonomia integralmente auditada por humanos. O desempenho no D2 não demonstra resultado no domínio do D1.

O CSV mantém o hash da auditoria inicial. Antes do filtro: 46.637 treino + 400 validação + 800 teste = 47.837. Retirados 847 exemplos do treino próximos dos conjuntos reservados e 8 da validação próximos do teste: **45.790 + 392 + 800 + 855 retirados = 47.837**. Hash de palavras/pares e similaridade cosseno ≥0,92 são uma heurística lexical; não eliminam toda paráfrase.

O teste contém 9 pares próximos entre si, sem que isso prove vazamento do treino. Como sensibilidade, removemos os 15 registros envolvidos, sem retreinar nem mudar o limiar. Nos 785 restantes: local **85,86%**, Jev **45,10%**. A escolha permanece. [Sensibilidade](reports/comparison/sensitivity.json).

## Por que não encaminhar sem humano

O critério pré-definido era maximizar cobertura com erro empírico ≤5% na validação, ao menos 30 exemplos aceitos e grade de limiares de 0,50 a 0,99. No modelo local, 0,61 selecionou 319/392 exemplos com 95,61% de acerto na validação. No teste, selecionou 658/800, mas houve **44 erros: acerto de 93,31%, erro de 6,69%**. A meta não se manteve.

Por isso, **82,25% de cobertura não significa 82,25% de tickets automatizados sem atendente**. O protótipo automatiza a sugestão; todo registro de decisão continua humano. Jev não apresentou um limiar viável sob o mesmo critério. `confidence` do fornecedor é preservado, mas a seleção usa a probabilidade da categoria escolhida. Não são probabilidades de acerto calibradas no nosso domínio.

## Custo, tempo e limites

Foram 1.192 chamadas Jev bem-sucedidas, sem retentativa automática: 392 validação e 800 teste. Versão retornada em todas: `jev-1.13.0`. Tokens reportados: 715.176 de entrada e 98.801 de saída. Estimativa **US$0,03004** com entrada a US$0,042/milhão e saída gratuita na [tabela publicada](https://typesafe.ai/blog/introducing-system-one-models-and-jev), consultada em 21/09; não é fatura nem inclui outros experimentos.

Jev usou conexão persistente e quatro chamadas concorrentes; o tempo inclui rede. O local mede uma inferência por vez com modelo já carregado; treinamento levou 11,18s nesta máquina, registrado separadamente. Não generalizar os tempos para outra infraestrutura.

O Brier preserva probabilidades recebidas, incluindo arredondamento: 33 distribuições Jev somaram 0,99. A comparação principal não foi recalibrada após o teste. Não investigamos contaminação do pré-treino do Jev por bases públicas. Nenhuma economia de trabalho ativo, redução de churn ou melhora de satisfação foi medida.

**Reprodução:** `comparar_classificadores.py` (prepare → jev → report) e `sensibilidade_teste.py`. Entradas, identificadores das linhas, parâmetros, fingerprints, resultados por ticket e versão do artefato estão em `reports/comparison/`. A etapa `jev` consome API; gerar o relatório novamente não faz chamadas.
