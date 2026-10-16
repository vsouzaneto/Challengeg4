# Problema de negócio e critérios de decisão

## Situação apresentada no brief

Uma equipe de 35 vendedores trabalha um histórico de aproximadamente 8.800 oportunidades. A Head de Revenue Operations relata que a priorização depende do julgamento individual; alguns negócios consomem esforço sem retorno, enquanto outros podem deixar de receber atenção no momento certo. Isso é uma **hipótese de problema operacional**, não uma causa já demonstrada pelos dados.

## Decisão a apoiar

> Dada a carteira de um vendedor e seu tempo limitado, quais oportunidades merecem atenção agora, por quê e com que próximo passo?

Essa decisão combina três dimensões que devem aparecer separadas na análise:

1. **Potencial de sucesso:** chance estimada de um negócio terminar em `Won`, sujeita aos limites do histórico.
2. **Valor potencial:** importância econômica aproximada, usando somente informação disponível antes do fechamento.
3. **Momento de agir:** sinal operacional de que uma ação é útil agora. O dataset não contém última interação ou próxima tarefa; tempo desde `engage_date` é, no máximo, um substituto imperfeito.

O score final é uma **prioridade de trabalho**, não uma promessa de fechamento nem uma prova de que o contato do vendedor causará a venda.

## Usuários e trabalho real

| Usuário | Decisão | Saída útil |
|---|---|---|
| Vendedor | Em quais negócios agir hoje | Lista curta da própria carteira, motivo da prioridade e próximo passo sugerido |
| Manager | Onde orientar ou redistribuir atenção | Visão por vendedor e região, com razões e alertas de dados ausentes |
| RevOps | Se a regra de priorização ajuda | Comparação com critério simples, adoção e resultados em piloto futuro |

## O que seria sucesso

**Nesta entrega:** a ferramenta roda com o dataset público, apresenta as oportunidades abertas por responsável, aplica uma priorização verificável e explica suas razões. A documentação permite reproduzir a análise e entender os limites.

**Em uma operação real:** vendedores usam a fila; a equipe reage em menos tempo a oportunidades relevantes; conversão, receita e produtividade melhoram em comparação justa com o processo anterior. Esses efeitos não podem ser demonstrados apenas pelo CSV histórico e exigiriam um piloto prospectivo.

## Perguntas que a exploração dos dados deve responder

- Qual é a distribuição de ganhos e perdas por produto, vendedor e região, considerando o tamanho de cada grupo?
- As características disponíveis nas oportunidades abertas também estão presentes no histórico usado para aprendizado?
- Quais campos foram preenchidos somente depois de o negócio avançar ou fechar?
- Qual regra simples serviria como referência justa para o modelo?
- Como sinalizar informação insuficiente sem punir automaticamente o vendedor ou inventar dados?
- Quantas oportunidades cabem de fato na agenda diária de um vendedor? O dataset não informa essa capacidade; qualquer valor usado no protótipo deve ser tratado como parâmetro, não fato.
