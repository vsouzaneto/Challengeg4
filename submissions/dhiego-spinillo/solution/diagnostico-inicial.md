# Diagnóstico inicial — para discussão

**Estado:** fatos auditados; conclusões e proposta em discussão. Fonte numérica: [JSON da auditoria](reports/auditoria-datasets.json).

| Problema identificado | Evidência | Consequência |
|---|---|---|
| Amostra não equivale ao volume anual do cenário | D1 tem 8.469 linhas | Separar amostra observada dos 30 mil tickets/ano hipotéticos. |
| Não é possível medir duração desde a abertura | Abertura ausente; resolução anterior à resposta em 1.365 de 2.769 pares (49,30%) | Não produzir ranking de canais por duração nem transformar diferenças absolutas em tempo corrigido. |
| Satisfação tem cobertura limitada | 2.769 notas, todas em tickets fechados; 32,70% da base | Declarar denominador e seleção; não generalizar automaticamente para todos os tickets. |
| Texto do D1 tem sinais de estrutura artificial | Todas as descrições contêm o literal `{product_purchased}` | Não tratar resoluções como conhecimento validado para respostas automáticas. |
| Tickets não fechados não comprovam atraso | 5.700 abertos/pendentes | Sem prazo e tempo confiáveis, não afirmar crescimento do backlog ou violação de SLA. |
| Classificação precisa de referência | D2 tem 47.837 textos e oito grupos; classe majoritária corresponde a 28,47% | Comparar modelo com baseline e avaliar fora do treino. |
| Os datasets representam domínios diferentes | D1: suporte de produtos; D2: service desk interno | Não transferir desempenho entre bases ou fabricar uma junção. |

Foram verificadas duplicatas exatas normalizadas no D2 (nenhuma); quase duplicatas ainda não foram verificadas. Associações descritivas entre satisfação e canal/tipo/prioridade não estabelecem causalidade nem provam irrelevância desses fatores em operações reais.

## Perguntas para a análise com Dhiego

1. Como responder ao diretor sobre desperdício quando não conseguimos medir esforço nem duração com segurança?
2. Que intervenção vale testar mesmo com essa limitação?
3. Qual erro operacional seria mais caro: encaminhamento errado ou revisão adicional?
4. Que evidência mínima justificaria automatizar um encaminhamento?

Nenhuma dessas perguntas é considerada resolvida apenas por constar num plano.
