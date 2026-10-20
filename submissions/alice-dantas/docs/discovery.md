# Discovery — Challenge 003 | Lead Scorer

**Última atualização:** 19/10/2026 · Versão condensada. Evidência numérica completa em [data-audit.md](./data-audit.md) (reproduzível pelo [script](../solution/scripts/audit_data.py)); decisões de solução em [architecture.md](./architecture.md). Etiquetas: **[Briefing]** está no briefing; **[Dados]** foi medido na auditoria; **[Hipótese]** não foi confirmada.

<a id="indice"></a>
**Conteúdo:** [1. Problema](#problema) · [2. Hipóteses e decisões](#hipoteses) · [3. O que os dados permitem](#dados) · [4. Prioridade e KPIs](#prioridade) · [5. Handoff](#handoff) · [Glossário](#glossario)

<a id="problema"></a>
## 1. Problema

**Declarado [Briefing].** A Head de RevOps diz que os vendedores gastam tempo demais em deals que não fecham e deixam boas oportunidades esfriar. Hoje 35 vendedores priorizam cerca de 8.800 oportunidades "no feeling". O pedido é uma ferramenta que mostre o pipeline e diga onde focar.

**Interpretado.** É um problema de alocação de atenção, mas hoje é **percepção da liderança**, sem custo, baseline nem medição. A solução veio definida antes de provar que priorizar é o gargalo (a causa pode ser critério, capacidade ou incentivos). E o valor de uma oportunidade aberta não existe até ela fechar: `close_value` só existe no fechamento e vale 0 se Lost.

**Quem decide.** O vendedor (usuário primário) decide qual deal trabalhar e quando revisar ou reativar. O manager decide onde apoiar e qual forecast comprometer. A RevOps decide se vale padronizar o critério e investir em dados.

<a id="hipoteses"></a>
## 2. Hipóteses e decisões, com o veredito dos dados

| ID | Afirmação | O que os dados mostram | Conclusão |
| --- | --- | --- | --- |
| P-001 | Tempo demais em deals que não fecham | Esforço não é medido. Lost (36,9% dos fechados) fecha mais rápido que Won (mediana 14 d contra 57 d) | Não verificável |
| P-002 | Boas oportunidades esfriam | Sem atividade nem histórico de estágio. AUC da idade de 0,475 a 0,571, sem direção estável | Não verificável |
| P-003 | Priorização individual, sem critério compartilhado | Nenhuma coluna registra a decisão do vendedor | Não verificável |
| H-001 | Falta critério compartilhado | Taxa de ganho por vendedor de 55,0% a 70,4%, indistinguível do acaso (p = 0,26) | Não verificável |
| H-002 | A capacidade é o gargalo | Média de 64,5 abertas por vendedor; o efeito da carga some ao controlar vendedor × mês (ρ = −0,007) | Não sustentada |
| H-003 | Incentivos e apego mantêm deals sem chance | 1.291 de 1.589 Engaging (81,2%) estão acima do maior ciclo fechado (138 d); pode ser teto de extração | Não verificável |
| H-004 | O vendedor não vê padrões do portfólio | Sem sinal em produto (p = 0,37), escritório, manager, setor (p = 0,97) e conta (p = 0,94) | Contradita |
| H-005 | A qualidade do CRM limita a decisão | `GTXPro` perde 1.480 linhas (16,8%) num join; conta nula em 68,2% das abertas e 0% das fechadas; 461 linhas idênticas | Sustentada |
| H-006 | O histórico reflete a priorização passada | Sem atribuição nem esforço; nenhum fechamento antes de 2017-03-01 (outra seleção, comprovada) | Não verificável |
| H-007 | O feeling já é razoável | Nenhuma regra estática passa de AUC 0,571; o feeling não é observável | Não verificável |
| H-008 | O valor de um deal aberto não está definido | `close_value` nulo nas 2.089 abertas; o preço de tabela chega a ±20% do valor fechado em 95,9% dos Won | Sustentada (proxy validado só nos Won) |

**Decisões do mapa:** HD-01 qual deal trabalhar (parcial: o valor é mensurável, a chance não discrimina) · HD-02 quando desqualificar (parcial: há referência de ciclo, mas a idade não previu perda) · HD-03 quando reativar (não verificável) · HD-04 onde o manager intervém (parcial: visão descritiva) · HD-05 qual forecast comprometer (não verificável) · HD-06 metas e capacidade (não verificável) · HD-07 baseline e retorno (parcial: custo e margem não existem) · HD-08 campos e regras de estágio (sustentada).

<a id="dados"></a>
## 3. O que os dados permitem

- **Base [Dados].** 8.800 oportunidades, 85 contas, 7 produtos, 35 vendedores. Resultado conhecido em 6.711 (4.238 Won e 2.473 Lost); 2.089 abertas (1.589 Engaging, 500 Prospecting). Taxa de ganho de 63,15% entre os fechados (IC95% de 61,99% a 64,30%), de 48,2% a 71,9% contando as abertas e de 48,6% a 82,8% por mês.
- **Quase nada prevê o resultado.** Com campos legítimos, AUC de 0,47 a 0,57 e Brier a ±0,003 da taxa global. O único padrão forte, o mês de fechamento (AUC 0,644), é **vazamento**.
- **O valor é função do produto:** 7 níveis de preço. Com a chance praticamente constante, o valor esperado vira um ranking por produto, com empates massivos.
- **O pipeline está fora do histórico.** Nenhum fechado passou de 138 dias e 81,2% dos Engaging estão acima disso; só 298 estão dentro. Não sabemos se são abandonados, legítimos ou efeito da extração.
- **Limites.** Retrato único, sem data de extração (corte assumido: 2017-12-31), com truncamento à esquerda; manager e escritório são a foto atual. Não há esforço, atividade, baseline humano, capacidade, custo-hora, margem, metas nem forecasts. Os padrões são compatíveis com dado sintético (28,4% de fechamentos em fim de semana), o que é hipótese.

**Conclusões atraentes e injustificadas:** (1) "81% do pipeline está parado, limpar libera 3,2 mi": falta sinal de abandono, e o valor é preço de tabela. (2) "Fecha melhor no fim do trimestre, priorizem esse timing": é vazamento. (3) "Priorizar por valor melhora a receita" ou "o vendedor X é melhor que o Y": ordenar por preço eleva o valor do topo de forma mecânica, e as diferenças entre vendedores são acaso.

| Sinais | Campos |
| --- | --- |
| Válidos | `deal_stage` (filtro); produto e preço (valor); idade desde `engage_date`, só em Engaging (flag); completude |
| Só contexto, sem sinal | Vendedor, manager, escritório, conta, setor |
| Proibidos | `close_date`, `close_value`, ciclo, mês de fechamento, posição da linha, `opportunity_id` |

<a id="prioridade"></a>
## 4. Prioridade e KPIs

Prioridade para o vendedor tem quatro componentes, e só o primeiro é quantificável com respaldo: **valor em jogo** (sustentado), **chance de fechar** (não discrimina por deal; só existe a taxa-base de 63,15%), **risco de esfriar** (só a idade, em Engaging, instável) e **pontuabilidade** (conta nula em 68% das abertas, Prospecting sem data). Por isso o motor não pode ser um modelo de probabilidade: uma regra transparente por valor e higiene é viável, e um modelo pareceria rigoroso e entregaria a taxa-base. O efeito de qualquer regra só se mede em piloto com grupo de controle.

**KPIs.** O principal candidato é o Δ de win rate ponderado por valor nos deals priorizados, com adoção semanal, qualidade do score (calibração e lift) e valor aberto acima do P90 do ciclo como apoio. Hoje só os descritivos são calculáveis: ticket Won de 2.360,9 (mediana 1.117), ciclo Won de 51,8 dias e soma Won de 10.005.534. O KPI principal tem duas leituras com defeitos opostos: como razão, fica quase plano (a taxa por produto vai de 60,0% a 64,8%); como "valor capturado no top-K", sobe por construção ao priorizar produtos caros. A validação deve reportar habilidade (AUC) e valor em colunas separadas.

<a id="handoff"></a>
## 5. Handoff para a arquitetura

**Restrições.** (1) Nenhuma probabilidade por deal; a taxa-base só como faixa. (2) Lista de campos proibidos com teste automático. (3) Normalização com contagem de linhas por junção. (4) "Hoje" como parâmetro e limiar de idade relativo ao histórico. (5) Estados explícitos; conta nula é lacuna de cadastro, não critério. (6) Precisão exibida não excede a dos dados: faixas, empates declarados. (7) Vendedor, manager e escritório só como escopo, nunca ranking de pessoas. (8) Explicação só com campos verificáveis, sem texto livre de LLM. (9) Registro de eventos para medir adoção. (10) Backtest temporal em 5 ou mais cortes contra baselines; nenhum resultado histórico é apresentado como efeito da ferramenta.

**Premissas.** Corte em 2017-12-31 (com outro corte, 81,2% passa a 77,9%); `GTXPro` = `GTX Pro`; abertas nunca são negativas; preço de tabela como proxy de valor; as 461 linhas idênticas são mantidas. Dois testes baratos não foram executados (taxa de ganho em coorte madura; evolução das abertas acima do maior ciclo); a arquitetura os absorve tratando a taxa-base como faixa e a flag de idade como configurável.

**A pedir à empresa, por impacto:** log de atividades e histórico de estágio; quando a conta é preenchida; por que Engaging passa de 138 dias; definição de Lost e data de extração; atribuição de deals e capacidade; metas, comissão, custo-hora e margem.

<a id="glossario"></a>
## Glossário

**Taxa-base:** média geral de ganho, sem informação por deal; não é probabilidade calibrada. **Vazamento:** usar na previsão algo que só existe depois do resultado. **Backtest:** simular o passado com o que se sabia até uma data. **AUC:** de 0,5 (sorteio) a 1 (perfeito), mede quão bem se separa quem ganha de quem perde. **Brier:** erro médio das probabilidades. **Lift no top-K:** quanto a lista dos K primeiros supera uma lista ingênua. **Envelhecido:** aberto há mais tempo que qualquer oportunidade já fechada; não prova abandono. **Proxy:** número usado no lugar do que não se mede. **Viés de seleção:** o histórico reflete onde o esforço foi aplicado.
