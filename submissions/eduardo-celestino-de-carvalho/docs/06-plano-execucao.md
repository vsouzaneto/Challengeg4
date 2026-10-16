# Plano de execução — Lead Scorer web

> **Registro de planejamento.** Este documento descreve o plano inicial, com interface em Streamlit. A entrega final é o Lead Kanban: servidor em Python e interface web em [`solution/`](../solution/README.md), com a regra descrita no [doc 09](09-g3-revisao-fila-foco.md). Ver o [índice](README.md).

**Objetivo do projeto:** entregar uma aplicação local que transforme as oportunidades abertas em uma fila de ações explicável por vendedor. A execução segue o [contrato de entrega](05-contrato-entrega.md) e a [metodologia de modelagem](03-metodologia.md). **Estado:** G3 concluído, G4 a iniciar; nada foi publicado ou enviado ao repositório do G4.

## Jornada principal a construir

1. O vendedor abre a aplicação e seleciona sua carteira.
2. Vê uma lista curta de oportunidades abertas, ordenada por prioridade de ação.
3. Entende, em cada linha, os pontos de atenção, o preço de catálogo, os sinais de revisão e o motivo da posição.
4. Abre um negócio para ver fatores favoráveis, fatores de atenção, campos ausentes e um próximo passo sugerido, sem prometer que a ação causará a venda.
5. Um manager pode filtrar por vendedor/região para revisar a distribuição de atenção.

**Condição de uso:** não atribuir `close_value` a negócios abertos, não tratar ausência de conta como zero e não apresentar um índice não calibrado como chance real de fechar.

## Arquitetura inicial e decisão de escopo

**Proposta inicial:** Python para ingestão/modelagem e **Streamlit** para a aplicação web local. O brief aceita Streamlit; uma linguagem única reduz tempo de integração e deixa mais espaço para validar o score e a experiência comercial dentro do orçamento orientativo de 4–6 horas. A lógica ficará em módulos independentes da interface. Se uma limitação concreta impedir a jornada acima, registraremos a razão antes de trocar de stack.

| Camada | Responsabilidade | Prática de engenharia |
|---|---|---|
| Dados | Baixar/ler as quatro tabelas públicas, validar chaves e corrigir aliases documentados. | Dados brutos imutáveis, hash da fonte, falha explícita em schema inesperado. |
| Features | Produzir apenas sinais disponíveis antes do resultado e aplicáveis aos abertos. | Contrato de colunas e teste contra vazamento. |
| Experimento de potencial | Treinar e comparar referência simples e modelo interpretável. | Divisão temporal, pipeline de treino, versão dos parâmetros e métricas; modelo reprovado em G2. |
| Prioridade | Combinar etapa, porte indicativo, tempo desde `Engaging` e tarefa de cadastro. | Regra separada do experimento de ML, explicada e verificável; sem alegação probabilística. |
| Experiência web | Carteira, filtros, motivos, detalhes e próximos passos. | Estados vazios, linguagem clara, hierarquia visual, contraste e layout utilizável em telas menores. |
| Qualidade | Verificações automatizadas e teste manual do fluxo. | Testes de casos críticos, execução local do setup e inspeção da UI. |

Estrutura candidata, a ajustar conforme a implementação:

```text
solution/
  app.py                 # interface web
  leadscore/             # dados, features, modelo, prioridade, explicações
  notebooks/             # auditoria e experimentos reproduzíveis
  tests/                 # comportamentos críticos
  requirements.txt       # dependências fixadas
  README.md              # setup e demonstração
```

## Fases, entregas e gates

| Gate | Trabalho | Entrega concreta | Aceite para avançar |
|---|---|---|---|
| G0 — Brief | Converter todas as exigências em critérios verificáveis. | [Contrato de entrega](05-contrato-entrega.md). | F1–P1 têm evidências planejadas. **Concluído.** |
| G1 — Dados | Fechar auditoria de tipos, datas, nulos, chaves e aliases; criar carga reproduzível. | [Relatório](04-auditoria-inicial.md), rotina de preparação e 7 testes de contrato. | Quatro tabelas carregam; junções conferidas; 0 registros descartados. **Concluído.** |
| G2 — Método | Definir corte temporal e baseline; treinar modelo simples; comparar lista curta e cobertura dos abertos. | [Experimento e decisão](07-g2-modelagem.md). | Modelo não mostrou utilidade operacional; seguir com regra explicável. **Concluído.** |
| G3 — Produto | Implementar jornada do vendedor, explicações, filtros e avisos de dados ausentes. | Aplicação web (Streamlit, depois substituída pelo Lead Kanban) e [regra documentada](08-g3-fila-comercial.md). | Vendedor encontra prioridades e entende a razão sem ler documentação técnica. **Concluído.** |
| G4 — Qualidade | Verificar cenários críticos, setup limpo, interface e resultados apresentados. | Testes, revisão de UI, limitações e instruções. | Outro usuário consegue rodar e reproduzir a demonstração; nenhum campo pós-fechamento alimenta o score. |
| G5 — Handover | Completar README e process log, revisar conteúdo publicável. | Pasta de submissão pronta para revisão local. | Todos os itens F1–P1 atendidos. Fork, push e PR permanecem fora deste gate até a solução final e a orientação do candidato. |

## Backlog priorizado

**P0 — obrigatório para esta proposta:** ingestão das quatro tabelas; normalização auditável; referência simples; avaliação do potencial; prioridade explicável; carteira por vendedor com filtros de manager/região; setup; limitações; process log. Os filtros ampliam um requisito mínimo com o bônus de maior utilidade comercial citado pelo brief.

**P1 — diferencial se P0 estiver sólido:** exportação da lista, comparação visual entre modelos e inspeção guiada de exemplos. Acessibilidade e responsividade básicas já fazem parte do aceite de G3/G4; refinamentos adicionais ficam em P1.

**Fora do protótipo:** integração com CRM real, autenticação, contato automático ao cliente, hospedagem e promessa de aumento de receita. Demandam dados ou validação operacional não fornecidos.

## Referências de práticas do portfólio local

Usaremos como referência a separação entre regras de negócio e interface, a visão comercial orientada a pipeline e tarefas, a organização em módulos, documentação de decisões e verificação dos fluxos de uso observadas nos projetos anteriores do candidato. Esses são **padrões de trabalho**, não fontes de dados para o challenge. Nesta fase não há necessidade de copiar código de outro projeto; qualquer reaproveitamento futuro dependerá de revisão de origem, dependências e conteúdo.

## Riscos e decisões previstas

| Risco observado | Resposta planejada |
|---|---|
| 68,2% dos negócios abertos sem conta | Modelo principal deve funcionar sem dados de conta; mostrar cobertura e não inventar preenchimento. |
| Produto `GTXPro` não casa com catálogo | Alias exato documentado e testado; preservar valor original para auditoria. |
| Dados de fechamento vazam para o treino | Lista permitida de features e teste que falha se colunas pós-resultado entrarem. |
| Negócios abertos sem desfecho e sem histórico de etapas | Diferenciar índice retrospectivo de probabilidade operacional; declarar seleção/censura. |
| Modelo não supera referência simples | Manter priorização transparente e reportar o experimento, sem forçar ML como vitrine. |
| Experiência vira dashboard passivo | Testar a jornada de segunda-feira: prioridade, motivo e próxima ação visíveis. |
| ZIP local ou conteúdo de outros projetos entra no PR | Stage com lista explícita de arquivos; revisar diff e origem antes de qualquer publicação. |

## Critério de conclusão local

- [x] Carga e auditoria de dados reproduzíveis com origem pública identificada.
- [x] Experimento de baseline/modelo reproduzível e avaliado no tempo; modelo reprovado para uso operacional.
- [x] Sistema web executa de acordo com o setup documentado.
- [x] Prioridade vai além de ordenar por valor e explica cada negócio.
- [x] Interface orienta o vendedor e oferece filtros úteis ao manager.
- [ ] Testes e inspeção manual cobrem vazamento, alias, dados ausentes e fluxo principal.
- [ ] README final informa abordagem, resultados, recomendações e limitações.
- [ ] Process log mostra iterações reais, papel da IA e julgamento do candidato.
- [ ] Revisão final confirma que só arquivos da submissão entrariam em eventual PR.
