# G3 — Fila comercial e regras de atenção

> **Substituído em 15/10/2026 por [G3 revisado: fila de foco](09-g3-revisao-fila-foco.md).** A regra de pontos abaixo priorizava negócios além de qualquer ciclo histórico de fechamento e teve desempenho inferior a ordenar só por preço no backtest. Mantida como registro do processo.

**Status:** aplicação web local implementada em 15/10/2026. Entrada: quatro tabelas públicas verificadas em G1. A aplicação lê as 2.089 oportunidades abertas da fotografia do CRM em **31/12/2017**, sem alterar `deal_stage` nem gravar no CRM.

## Decisão atendida

O vendedor precisa separar duas tarefas: **revisar negócios em `Engaging`** e **qualificar oportunidades em `Prospecting`**. A interface mostra até três sugestões em cada grupo, uma tabela da carteira completa, filtros e detalhe com pontos, razões e próxima ação. Contas ausentes geram uma tarefa de cadastro; a oportunidade permanece em sua etapa original e não recebe uma “probabilidade menor”. Manager e regional ajudam a inspecionar carteiras, não entram no score.

## Índice de atenção, sem interpretação probabilística

| Componente | Regra | Pontos | Por quê |
|---|---|---:|---|
| Etapa | `Engaging` / `Prospecting` | 35 / 15 | Negociações em curso pedem acompanhamento; prospecting pede qualificação. |
| Porte indicativo | Preço do produto na faixa baixa / intermediária / alta entre preços distintos do catálogo | 10 / 20 / 30 | Distribui atenção por porte sem deixar o item mais caro dominar sozinho. Para os sete produtos atuais, as faixas correspondem aos 2 menores, 2 intermediários e 3 maiores preços. |
| Tempo desde entrada em `Engaging` | Até 29 / de 30 a 89 / 90 dias ou mais | 5 / 15 / 20 | Sinaliza a necessidade de **revisar a etapa**. Não é tempo desde o último contato. Em `Prospecting`, vale 0 porque a data não existe. |
| Cadastro | Conta não identificada / identificada | 5 / 0 | Cria trabalho de identificação da conta. É atenção operacional, não evidência sobre conversão. |

**Máximo observado pela regra: 90 pontos.** `Alta` = 85–90; `Média` = 50–84; `Rotina` = abaixo de 50. Em empate de pontos, maior preço de catálogo vem antes; persistindo o empate, o ID apenas estabiliza a exibição. Negócios empatados em ambos têm a **mesma prioridade**, apesar da ordem visível. A regra foi definida como política de triagem para o protótipo e precisa ser validada com o time comercial antes de uso real.

**Exemplo:** uma oportunidade em `Engaging`, com produto da faixa alta, entrada há mais de 90 dias e conta não identificada recebe `35 + 30 + 20 + 5 = 90`. A ação é revalidar interesse, etapa e próximo compromisso e registrar a conta. Uma oportunidade em `Prospecting`, também de faixa alta e sem conta, recebe `15 + 30 + 0 + 5 = 50`; a ação é qualificar necessidade, decisor e prazo e identificar a conta. Nenhuma dessas pontuações é a chance de fechar.

## Evidência funcional

- A fila preserva **2.089** abertos: 1.589 `Engaging` e 500 `Prospecting`; 1.425 não têm conta identificada. Nenhum `Won` ou `Lost` é exibido ou pontuado.
- A interface permite filtrar por regional, manager, vendedor, etapa, faixa de prioridade, ausência de conta e busca; os filtros mantêm a pontuação original.
- O detalhe mostra produto, preço de catálogo, conta, etapa, vendedor, regional, manager, data da etapa quando existe, componentes da regra e ação sugerida. Um CSV da visão filtrada contém somente campos visíveis e nenhum campo de fechamento.
- A ordenação vai além do preço: um `Engaging` de menor preço e com necessidade de revisão pode preceder um `Prospecting` de maior preço. Isso é coberto por teste automatizado.
- A versão local foi exercitada com `streamlit.testing.v1.AppTest` e em navegador real: abertura inicial, seleção de vendedor, detalhe, filtro de conta ausente e visualização estreita. Na carteira de exemplo de Anna Snelling, a aplicação mostrou 112 abertos, sendo 57 `Engaging`, 55 `Prospecting` e 69 contas a identificar.

## Limites de uso

Esta é uma **fotografia histórica** e não uma agenda de clientes atuais. `engage_date` registra entrada em `Engaging`; o dataset não informa criação da oportunidade, última interação, compromisso agendado ou valor estimado do negócio. Preço de catálogo é uma aproximação de porte, sem equivalência automática com `close_value`. Pesos e faixas são heurísticos, não otimizados por um teste de impacto; os resultados do G2 rejeitaram o modelo preditivo como probabilidade operacional. O sistema não envia mensagens, altera etapas, autentica usuários nem sincroniza com CRM.

Para escalar, seria necessário integrar CRM com snapshots e atividades datadas, confirmar com o time comercial o sentido de cada ação, definir capacidade de trabalho por vendedor e medir adoção e resultado prospectivamente. A regra poderá então ser revista com dados atuais.
