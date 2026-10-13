# Sumário executivo: triagem de suporte com IA

**Para:** conselho técnico · **De:** Diogo da Silva Carrico · **Data:** 13/10/2026

## Decisão pedida

Aprovar três passos, nesta ordem:

1. **Instrumentar a operação de suporte** para medir o que hoje não se mede: abertura do ticket, transferências, tempo de espera e reabertura.
2. **Um piloto de triagem automática em modo sombra**, com tickets da própria operação: a IA classifica em silêncio e nada muda para o cliente até ela provar 95% de precisão por fila.
3. **Manter com pessoas, por política,** tudo o que envolve dinheiro, contrato, segurança, dados pessoais ou risco físico.

## O que encontramos

- **Os dados entregues não sustentam um diagnóstico.** O conjunto de tickets é sintético, e o brief erra o volume (8.469 tickets, não 30 mil) e os tipos de ticket (5, não 3). Nenhum gargalo e nenhum fator de satisfação resistem a testes estatísticos.
- **O tempo de resposta não pode ser medido**, porque não há data de abertura dos tickets. Por isso a primeira recomendação é instrumentar.
- **A triagem é a menor parte do desperdício.** A estimativa, com premissas rotuladas, é de 68 horas por mês (R$ 3.075). O maior custo está em transferências e espera, que os dados não registram.

## O que propomos

```mermaid
flowchart LR
    A["Ticket"] --> B{"Caso sensível<br/>pela política?"}
    B -- sim --> P["Pessoa responsável"]
    B -- não --> C{"Modelo conhece<br/>o tipo de ticket?"}
    C -- não --> H["Triagem humana"]
    C -- sim --> D{"Fila já comprovada e<br/>confiança acima do limiar?"}
    D -- não --> H
    D -- sim --> F["Fila certa,<br/>sem triagem manual"]
```

A IA só encaminha o ticket. Ela não responde ao cliente, não concede acessos e não decide reembolsos. No piloto, cada correção feita por um agente vira dado de monitoramento.

## O que o protótipo mostra

| Indicador | Resultado | Leitura |
| --- | --- | --- |
| Acurácia do classificador | 86,7% | Medida em tickets de TI reais, num conjunto de teste usado uma só vez |
| Tickets roteados sozinhos | 43,5% | Com 97,7% de precisão, medidos no fluxo completo da demo; 4 filas já provaram 95% e outras 3 esperam o piloto, que pode levar a cobertura a 64,1% |
| Tickets de outra operação barrados | 98,1% | O modelo reconhece o que não conhece; por isso precisa ser retreinado com os tickets da nossa operação |
| Tamanho do piloto | 230 tickets roteados | Menos de uma semana no volume do brief, para provar 95% de precisão no geral |

O protótipo hoje é uma demo de linha de comando com a política, o guarda e o classificador. A correção pelo agente, o registro das decisões e o monitoramento são construídos no piloto.

## Custos

| Opção | Custo mensal |
| --- | --- |
| Construir a triagem (roda localmente, sem API paga) | Cerca de R$ 40 de infraestrutura, mais horas de manutenção |
| Comprar IA para o helpdesk atual | De R$ 0 (quando já incluída no plano) a cerca de R$ 9.800 |

Antes de construir, vale verificar se o helpdesk atual já inclui IA de triagem.

## Riscos e como tratamos

| Risco | Como tratamos |
| --- | --- |
| O modelo aprendeu com tickets de TI de outra organização, em inglês | Retreinar com tickets da operação, em português, antes do piloto; até lá, o guarda manda para pessoas o que o modelo não conhece |
| Roteamento errado | Uma fila só roteia sozinha depois de provar 95% de precisão; no piloto, o agente corrige a fila e ela volta ao modo assistido se a precisão cair |
| Caso sensível automatizado | Regras de política rodam antes do modelo e não podem ser ignoradas por ele |
| Pedido de acesso roteado para outra fila | Medido no teste: 5 de 176 foram para Hardware, e nenhum pedia privilégio; no piloto, cada caso assim conta como violação da política |
| Dados de clientes enviados a terceiros | A triagem roda localmente; qualquer uso futuro de LLM só com plano pago e acordo de tratamento de dados |
| Benefício superestimado | Premissas rotuladas; o modo sombra mede os minutos reais de triagem |

## Próximos passos

| Quando | O quê |
| --- | --- |
| Semanas 1 e 2 | Instrumentar o helpdesk e separar tickets já classificados para o retreino |
| Semanas 3 e 4 | Retreinar com tickets da operação e rodar em modo sombra |
| Semanas 5 e 6 | Modo assistido nas filas que provarem 95% de precisão |
| Fim da semana 6 | Decisão, fila por fila, sobre o roteamento automático |

Detalhes: `docs/diagnostico.md`, `docs/proposta-automacao.md` e `docs/classificador.md`.
