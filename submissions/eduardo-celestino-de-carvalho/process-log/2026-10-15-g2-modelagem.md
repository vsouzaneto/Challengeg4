# 15/10/2026 — G2: modelo, avaliação temporal e decisão

## Pedido e hipótese

O candidato pediu para avançar ao G2 após registrar sua ideia: usar negócios `Won`/`Lost` para estimar o potencial dos negócios abertos. A IA foi usada para estruturar o experimento, implementar código, executar verificações e registrar o resultado. A decisão de negócio continua sujeita à revisão do candidato antes da submissão.

## Passos e evidências

1. A IA contou negócios com rótulo disponível em cortes temporais. Confirmou que `engage_date` é entrada em `Engaging`, não criação da oportunidade, e que `Prospecting` não tem essa data. Rejeitou dividir linhas aleatoriamente.
2. Criou ambiente Python local e instalou `scikit-learn==1.9.1`, conforme o guia oficial, sem incluir `.venv` no projeto publicável.
3. O primeiro ensaio usava janelas de observação desiguais entre validação e teste. Ao ver que isso favorecia negócios de duração diferente, a IA corrigiu o protocolo para **30 dias iguais** nas duas coortes. Depois alinhou também o treino a esse mesmo alvo condicional. Os números do ensaio preliminar foram descartados da decisão final.
4. O primeiro ranking desempate usava `opportunity_id`; isso poderia criar resultado artificial entre scores iguais. A IA trocou por divisão fracionária da última posição entre negócios empatados e adicionou um teste que verifica independência da ordem das linhas.
5. Comparou taxa global, preço, taxa por produto suavizada e duas regressões logísticas com entradas permitidas. O critério de escolha foi aplicado à validação antes de interpretar o teste. O método escolhido teve AUC 0,513 e Brier 0,2512 no teste, contra Brier 0,2484 da taxa global; nas 150 primeiras posições trouxe 83,40 ganhos esperados contra 82,43 da referência global e só 4,60% da receita observada.
6. Foram executados 11 testes de contrato e temporalidade, todos aprovados. O relatório é reproduzível por `solution/experiment_model.py` e os agregados estão em `solution/experiments/g2-results.json`.

## Julgamento e correção de rumo

O experimento **não validou** uma probabilidade de ganho para oportunidades abertas. O treino e teste consideram somente negócios resolvidos em 30 dias, deixando muitos casos sem desfecho nesse prazo; a carteira real inclui `Prospecting` e negócios longos. O ganho pequeno em número de fechamentos não compensa o baixo valor da fila criada pelo modelo. A decisão para G3 é usar uma regra de prioridade comercial explicável e apresentar taxas históricas, se úteis, apenas com o devido contexto. Nenhuma afirmação de aumento de conversão ou receita será feita.

## Arquivos e origem

Somente o dataset público do challenge foi usado. Nenhum código, dado ou segredo de outros projetos do Desktop foi importado. O ZIP de dados e o ambiente virtual são locais e ignorados pelo Git. Não houve commit, fork, push ou PR ao repositório do G4.
