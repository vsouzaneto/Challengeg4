# Process Log — Challenge 003

## Ferramentas de IA

Codex foi usado para inspecionar o repositório e os CSVs, analisar regras de priorização, implementar a aplicação local e iterar a interface. O README do challenge e o guia oficial de submissão foram consultados para manter a solução aderente aos requisitos. Ideias de operação dos CRMs The Flooring Empire, RefurbHub e Imvest serviram como referência, sem copiar seus dados.

## Decomposição e decisões

1. Entender estrutura e qualidade dos dados antes de pontuar oportunidades.
2. Separar intenção observável, fit comercial e confiança dos dados.
3. Transformar o score em fila de trabalho com ações e histórico por oportunidade.
4. Construir uma tela de vendedor com busca, filtros, contexto e registro de contato.

A métrica foi posicionada como **sales prioritization**, não probabilidade de compra: o dataset não contém interações, decisores, respostas ou prazo de compra. O score combina momento do pipeline, preço de tabela, fit setor × produto/porte e histórico da conta.

## Iterações e correções

Foram necessárias mais de dez iterações conversacionais entre exploração, regras da fila e interface. Uma hipótese inicial tratava `Engaging` como sinal forte de interesse; a análise temporal mostrou que 81% dos negócios nesse estágio já excediam o ciclo máximo histórico de 138 dias. A recência passou a reduzir o componente de momento e a fila ganhou cadência e revisão para casos stale.

A primeira ideia de ordenar tudo diretamente pelo score não cobria retornos e tentativas do vendedor. A lógica foi ajustada para priorizar ações vencidas, manter a propriedade do negócio com o vendedor responsável e registrar `Pular`, `No Answer` e `Contactado` com regras diferentes. A tela também evoluiu de uma explicação numérica para fatores em linguagem comercial, inicialmente recolhidos para evitar poluição visual.

## Contribuição humana

O candidato trouxe achados exploratórios de outra análise do dataset, questionou as hipóteses sobre estágio e recência, definiu o objetivo como fila operacional, escolheu os pesos do Priority Score e determinou a experiência dos botões, notas, sentimento e cadência. Também decidiu manter a interface desktop como foco inicial e adiar refinamento mobile.

## Estado e limites

A aplicação usa os dados reais e roda localmente. Ainda não há autenticação, ingestão de novas oportunidades, serviço multiusuário em produção nem integração com CRM. A base é histórica (2017), e o score não é probabilidade de fechamento. Antes da submissão, deve-se incluir a solução no repositório do challenge e abrir um Pull Request conforme o guia oficial.

## Queue Mode

Após aprovar um mockup gerado por IA, o candidato solicitou o modo de foco: modal com um cliente por vez, três botões com cores semânticas e editor de notas substituindo as ações. A implementação reutiliza o registro existente de interações. A validação usa uma base SQLite isolada para conferir avanço, notas e cadência sem inserir interações de teste na carteira principal.

Como detalhe editorial aprovado, após a quinta ação da sessão o Queue Mode mostra uma Builder Card inspirada na seção de apresentação do portfolio de Paulo Lanzilotti. O card quebra a repetição visual, apresenta nome, função, proposta e histórico profissional, oferece o link do portfolio e retorna ao próximo contato. Ele é explicitamente separado da fila: não tem score, não é salvo como oportunidade e não altera métricas comerciais.
