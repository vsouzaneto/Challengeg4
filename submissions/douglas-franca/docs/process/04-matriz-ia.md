# 04 · Onde a IA entra

> **Em 3 linhas:** a IA assume o que é repetitivo e verificável: checar origem e completude, calcular régua e retorno, montar a leitura. Ela ajuda (sem decidir) no que exige criatividade ou julgamento: hipóteses, briefings, triagem de creators. **Aprovar gasto, definir break-even, escalar e cuidar da marca são sempre humanos.** Uma tarefa só sobe de nível com prova de que a IA acerta.

Níveis: 🤖 **AUTO**: a IA executa e registra; um humano audita por amostra · 🤝 **ASSIST**: a IA propõe e um humano aprova cada item · 👤 **HUMANO**: a IA não participa da decisão.

| Etapa (03-to-be) | Tarefa | Nível | Por que este nível | Risco se automatizar além disso | Guardrail | KPI de controle | Owner |
|---|---|---|---|---|---|---|---|
| Gate 0 | Health check do arquivo: variância/média, correlações, duplicatas, coerência entre colunas (as regras do G2) | 🤖 AUTO | Regras determinísticas e testadas; este arquivo seria reprovado | Aceitar dado ruim sem ver | Reprovação bloqueia a análise; o AI Master revisa cada reprovação | % de extrações reprovadas; tempo até a correção | AI Master |
| Gate 0 | Pergunta de origem ao time (quem extraiu, de onde) | 👤 HUMANO | Exige conversa e responsabilização | — | Origem registrada no arquivo | 100% das extrações com origem | Head de Marketing |
| 1 | Sugerir hipóteses a partir de ciclos anteriores e tendências | 🤝 ASSIST | Criatividade útil, mas sujeita a alucinação (G1: Gemini inventou achados) | Testar hipóteses inventadas | Toda hipótese cita evidência ou é marcada como exploratória | % de hipóteses com evidência citada | Social Media Lead / Gestor de Parcerias |
| 1 | Calcular régua, tamanho de amostra e duração do teste | 🤖 AUTO | Cálculo estatístico padrão | Teste subdimensionado | Fórmula versionada e testada | Testes com poder ≥80% | AI Master |
| 1 | Definir métrica primária e régua de relevância | 👤 HUMANO | Decisão de negócio (G3: definida pelo Douglas) | Otimizar a métrica errada | Registro antes do teste | 100% dos testes pré-registrados | Head de Marketing |
| Gate 1 | Checar se o contrato está completo (custo, `campaign_id`, cupom, UTM, comparação) | 🤖 AUTO | Checklist objetivo | Contrato incompleto entrar no ciclo | Incompleto não recebe `campaign_id` ativo | % de contratos completos | AI Master |
| Gate 1 | Calcular break-even (fee máximo dado margem e venda esperada) | 🤖 AUTO | Função paramétrica (G5) | Premissa errada virar número "oficial" | Cada insumo com procedência; Financeiro valida | Diferença entre break-even previsto e realizado | AI Master |
| Gate 1 | **Aprovar o gasto e o teste** | 👤 HUMANO | Responsabilidade financeira e de marca | Gasto sem dono | Assinatura no CRM | 100% dos contratos com aprovação registrada | Head + Financeiro |
| 2A | Rascunho de briefing (formato, duração, gancho, CTA) | 🤝 ASSIST | Acelera a produção; a voz da marca é humana | Conteúdo genérico ou fora da marca | Aprovação do Social Media Lead | % de briefings aprovados sem retrabalho | Social Media Lead |
| 2B | Triagem de creators: histórico no cadastro, sinais de audiência falsa, fit de categoria | 🤝 ASSIST | Volume alto; a decisão exige contexto de relacionamento | Descartar creator bom ou aprovar fraude | Gestor revisa a lista curta | % de recomendações aceitas; fraudes detectadas depois | Gestor de Parcerias |
| 2B | Negociar e fechar o contrato | 👤 HUMANO | Relacionamento e reputação | — | — | — | Gestor de Parcerias |
| 2A/2B | Brand safety do conteúdo antes de publicar | 👤 HUMANO | Risco reputacional | Crise de marca | Checklist assinado | Incidentes de marca | Social Media Lead |
| 4 | Coleta e validação do data contract | 🤖 AUTO | Integração repetitiva | Dado incompleto contaminar a leitura | Quarentena abaixo de 95% de completude | Completude por campo | AI Master |
| 5 | Leitura de 15 dias: volume, custo, guardrails | 🤖 AUTO | Monitoramento com regras fixas | Declarar vencedor cedo | A leitura **não mostra** "vencedor" antes do dia 30 | Alertas disparados × confirmados | AI Master |
| 5 | Parada antecipada por dano | 👤 HUMANO | Decisão com impacto | Parar por ruído | Só com guardrail violado e registro | Paradas justificadas | Head de Marketing |
| 6 | Relatório de fechamento (efeito, margem de erro, custo, venda, retorno) | 🤖 AUTO | Cálculo e redação padronizados | Narrativa enviesada | Números vindos só das tabelas; limitações sempre visíveis | Divergência relatório × tabela = 0 | AI Master |
| 6 | **Decidir Escalar / Replicar / Iterar / Parar** | 👤 HUMANO | A regra propõe; a pessoa decide com o contexto | Escalar por regra sem ver o todo | Decisão registrada com justificativa | Decisões revertidas no ciclo seguinte | Head de Marketing |
| 7 | Resumir aprendizados e sugerir a próxima pauta | 🤝 ASSIST | Síntese útil | Reforçar viés | Aprendizado cita o ciclo de origem | % da pauta ligada a aprendizados | Social Media Lead |

## Regra de promoção de nível
Uma tarefa 🤝 ASSIST só vira 🤖 AUTO quando:
1. a taxa de correção humana fica **abaixo de 5% por 8 semanas seguidas**;
2. nenhum erro com impacto financeiro ou de marca acontece no período;
3. o Head aprova a promoção por escrito.

Se a correção passar de 10% em qualquer ciclo, a tarefa volta um nível. **Nenhuma tarefa 👤 HUMANO é promovida.**

## O que nunca automatizar
Aprovar gasto · definir métrica e régua · definir break-even · negociar contrato · brand safety · decidir escalar ou parar.
