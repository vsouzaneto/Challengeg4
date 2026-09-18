# 05 · Quem faz o quê (RACI)

> **Em 3 linhas:** seis papéis, **todos já existentes na operação**; o redesenho não exige contratação. O AI Master opera a camada de dados e automação. Cada etapa tem **um único responsável pela decisão (A)**. A tabela responde a duas perguntas que todo teste precisa ter respondidas antes de começar: **quem valida o break-even e quem opera o grupo de comparação**.

**R** executa · **A** responde pela decisão (um por linha) · **C** é consultado · **I** é informado

Papéis: **HM** Head de Marketing · **SM** Social Media Lead · **GP** Gestor de Parcerias · **FIN** Financeiro · **AM** AI Master · **CR** Creator

## Ciclo de 30 dias
| Etapa | HM | SM | GP | FIN | AM | CR |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Gate 0 · origem e health check dos dados | A | I | I | — | R | — |
| 1 · Hipótese e pré-registro (conteúdo) | A | R | — | — | C | — |
| 1 · Hipótese e pré-registro (parceria) | A | C | R | C | C | — |
| Definir métrica primária e régua | **A/R** | C | C | — | C | — |
| Calcular amostra, duração e break-even | I | I | I | C | **A/R** | — |
| **Validar custo e break-even** | C | — | C | **A/R** | R | — |
| Gate 1 · aprovar teste e gasto | **A** | C | R | R | C | — |
| 2A · Briefing e produção | I | **A/R** | — | — | C | — |
| 2B · Contrato com `campaign_id`, cupom e UTM | I | — | **A/R** | C | R | C |
| **Montar e operar o grupo de comparação** | I | C | R | — | **A/R** | I |
| Brand safety antes de publicar | C | **A/R** | R | — | — | C |
| 3 · Publicação instrumentada | I | **A/R** | R | — | C | R |
| 4 · Coleta e validação do data contract | I | I | I | — | **A/R** | — |
| 5 · Leitura de 15 dias | I | C | C | I | **A/R** | — |
| Parada antecipada por dano | **A** | C | C | C | R | I |
| 6 · Relatório de fechamento de 30 dias | I | C | C | C | **A/R** | — |
| **Decidir Escalar / Replicar / Iterar / Parar** | **A** | C | C | C | R | — |
| 7 · Aprendizado para pauta e pipeline | A | R | R | I | R | — |

## Os três testes iniciais (G5)
| Teste | Pergunta | Dono da decisão (A) | Quem opera (R) | Quem valida break-even | Quem opera a comparação |
|---|---|---|---|---|---|
| EXP-01 · Patrocínio | Patrocínio paga a conta em venda? | HM | GP | FIN | AM |
| EXP-02 · Formato por canal | Qual formato move a taxa de engajamento em cada canal? | HM | SM | — (sem gasto adicional) | AM |
| EXP-03 · Cadência | Postar mais gera alcance e engajamento adicionais? | HM | SM | FIN (custo de produção) | AM |
