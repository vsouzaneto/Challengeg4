# docs: análises de apoio

Tudo o que foi gerado durante a análise, na ordem em que foi feito. Cada etapa tem:
- planilhas Excel com **fórmulas** (números verificáveis) e uma aba **LEIA-ME**;
- um diagnóstico parcial em `.md`;
- os programas Python que recriam as planilhas a partir dos CSVs originais.

Os diagnósticos parciais são etapas do raciocínio. A conclusão final está em [`../solution/relatorio.pdf`](../solution/relatorio.pdf).

## Etapas

| # | Pasta | Pergunta | Principal achado |
|---|---|---|---|
| 1 | `analise/DADOS_ORIGINAIS` | Como os dados vêm? Visão mês a mês, segmentos e features | O churn "sobe" e as três marcações de churn não batem |
| 2 | `analise/DADOS_RECONCILIA` | Qual tabela é confiável? 28 regras testadas linha a linha; 22 causas × 3 definições de churn | Só a tabela de assinaturas é coerente; o sinal é de tempo (jul/2024, primeiros 30 dias) |
| 3 | `analise/DADOS_2024_NOV_DEZ` | O que é o churn de nov/dez/2024? Troca, redução ou saída; rajadas; valores em US$; mês a mês | 0 saídas de cliente; o churn de hoje mistura trocas e reduções |
| 4 | `analise/DADOS_ENTERPRISE` | Por que o Enterprise concentra a perda? Preço, licenças, features, reclamações e perfil em 4 períodos | Sem aumento de preço nem feature nova; contas desligam pacotes e seguem Enterprise |
| 5 | `analise/DADOS_FEATURE_EVENTS_11_12_2024` | Uso de features e eventos de churn se relacionam? Tickets de quem teve churn × quem não teve | Nenhuma relação; as datas de uso são aleatórias |
| 6 | `analise/DADOS_CONSOLIDA_V1` | Contas prioritárias, perda real por trimestre, ritmo de compra, evento × cancelamento real | Perda real de US$ 538 mil contra US$ 1,18 milhão contados hoje |

`analise/MEMORIA_DO_PROJETO.md` é o arquivo de contexto usado para retomar o trabalho com a IA entre pausas: regras de trabalho, definições e achados acumulados. Ele faz parte do process log.

## Como recriar as planilhas

Requisitos: Python 3 com `pandas` e `openpyxl`.

1. Baixe os 5 CSVs do dataset ([Kaggle — SaaS Subscription & Churn Analytics](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset)) para a pasta `docs/dados/`.
2. Rode cada programa de dentro de sua pasta `scripts/`, por exemplo:

   ```
   python analise/DADOS_CONSOLIDA_V1/scripts/02_perda_real_trimestre.py
   ```

   - **Saída:** cada programa grava a planilha de volta na pasta da sua etapa.
   - **Outra pasta de dados ou de saída:** a maioria dos programas aceita os caminhos como argumentos: `python <programa>.py <pasta_dos_csv> <arquivo_saida.xlsx>`.
   - **Ordem:** os programas de `DADOS_ORIGINAIS` seguem a ordem do `LEIA-ME.txt` da pasta.

Os CSVs são só lidos, nunca alterados.

## Regras usadas em todas as etapas

- **Troca (migração):** a mesma conta abriu outra assinatura até 7 dias antes ou depois do encerramento.
- **Compra extra desfeita:** assinatura com até 30 dias de vida, havendo outra mais antiga do mesmo plano ativa na conta.
- **Redução real:** a conta desligou uma assinatura e seguiu cliente.
- **Saída do cliente:** a conta ficou sem nenhuma assinatura ativa.
- **Rajada:** 3 ou mais assinaturas da mesma conta em 7 dias corridos.
- **"Diferença confiável?":** teste exato de Fisher (proporções) ou embaralhamento dos rótulos (médias), com corte de 5%. Com menos de 10 casos, "Poucos casos para concluir".
