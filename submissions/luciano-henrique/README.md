# Submissão

## Luciano Henrique — Challenge 003: Lead Scorer

### Executive Summary

Uma equipe de 35 vendedores trabalha aproximadamente 8.800 oportunidades e precisa priorizá-las sem depender apenas de feeling. A solução é um aplicativo Streamlit que transforma dados do CRM em prioridades de ação para as 2.089 oportunidades abertas. A interface separa negócios com evidência suficiente para priorização daqueles de alto valor com pouco histórico, que exigem revisão humana. O Priority Score é um ranking relativo da carteira e não representa probabilidade de fechamento.

### Problema

Cada vendedor precisa decidir onde investir seu tempo. Sem uma referência comum, pode concentrar esforço em deals fracos enquanto oportunidades valiosas esfriam. O desafio é apoiar essa decisão sem esconder a incerteza presente nos dados.

### Solução

O MVP usa Python para carregar e validar os quatro CSVs e Streamlit para apresentar a carteira de forma acionável.

- Processa as 2.089 oportunidades abertas sem descartá-las.
- Calcula um Priority Score relativo de 0 a 100 entre todas as abertas.
- Usa `Balanced Priority = sales_price × Historical Fit`.
- Calcula Historical Fit pela média das taxas históricas ajustadas de produto e vendedor, com shrinkage de 50 exemplos para reduzir extremos em grupos pequenos.
- Classifica a evidência histórica como Alta, Média ou Baixa conforme o número de exemplos disponíveis.
- Mantém uma Watchlist de oportunidades de alto valor com pouca evidência para revisão humana.
- Permite filtrar por vendedor, gerente, região, estágio, confiança e revisão manual.
- Mantém a ordenação por preço como baseline visível.

Na interface, as cinco principais oportunidades com confiança Alta ou Média aparecem como prioridades de ação. A Watchlist é apresentada separadamente para evitar que pouca evidência pareça uma recomendação automática.

### Como usar

Na raiz do repositório, instale a única dependência da interface:

```powershell
python -m pip install -r submissions/luciano-henrique/solution/requirements.txt
```

Execute o aplicativo:

```powershell
python -m streamlit run submissions/luciano-henrique/solution/app.py
```

Execute os testes automatizados:

```powershell
python -B -m unittest discover -s submissions/luciano-henrique/solution -p "test_*.py" -v
```

### Resultados

- 8.800 oportunidades totais.
- 2.089 oportunidades abertas.
- 6.711 oportunidades encerradas.
- 14 testes automatizados passando.
- 1.407 abertas com confiança Alta.
- 667 abertas com confiança Média.
- 15 abertas com confiança Baixa.
- 15 oportunidades na Watchlist.

No backtest temporal, os 20% superiores por preço capturaram 48,58% do `close_value` realizado pelos Won no teste. Balanced Priority capturou 48,91%. A taxa Won foi 64,78% com Price Only e 65,53% com Balanced Priority. A diferença não foi estatisticamente convincente; portanto, a solução não afirma que Balanced Priority seja superior a ordenar somente por preço.

### Decisões importantes

- Evitamos data leakage na construção do score.
- `close_value`, `close_date` e resultados futuros não são usados como features.
- Historical Fit não é apresentado como probabilidade de fechamento.
- Priority Score indica posição relativa na carteira, não chance de compra.
- Oportunidades com pouca evidência continuam acessíveis e recebem revisão humana.
- Filtros não recalculam os scores globais.
- Priorizamos transparência e possibilidade de auditoria em vez de um modelo mais complexo e obscuro.

### Limitações

- O dataset contém registros de 2016–2017 e pode não representar uma operação atual.
- Não há atividades comerciais como última interação, próxima ação, orçamento ou decisor.
- Não há histórico de mudanças de estágio nem versões históricas dos cadastros e preços.
- 68,21% das oportunidades abertas não possuem conta associada.
- O backtest usa um único corte temporal e apenas oportunidades encerradas.
- Não há prova causal de que o ranking aumente vendas ou produtividade.
- Balanced Priority não demonstrou superioridade estatística confiável sobre preço sozinho.
- Confiança representa volume de evidência, não certeza individual ou qualidade completa dos dados.

### Estrutura do projeto

```text
submissions/luciano-henrique/
├── README.md
├── data/
│   ├── accounts.csv
│   ├── products.csv
│   ├── sales_pipeline.csv
│   └── sales_teams.csv
├── solution/
│   ├── data.py
│   ├── scoring.py
│   ├── app.py
│   ├── run.py
│   ├── README.md
│   ├── test_scoring.py
│   ├── test_app.py
│   └── requirements.txt
└── process-log/
    └── README.md
```

### Process Log

O processo completo de investigação, correção da hipótese, desenvolvimento e uso de IA está em [process-log/README.md](process-log/README.md).

### IA utilizada

- **ChatGPT:** decomposição do problema, crítica das hipóteses, desenho dos experimentos e apoio às decisões.
- **Codex:** inspeção do repositório, análise dos CSVs, implementação, execução dos testes, construção da interface e validação das alterações.
- **Julgamento humano:** correção da hipótese inicial, definição dos limites do produto, prevenção de exclusões automáticas e escolha por transparência.

O diferencial da solução não é apenas a interface: a hipótese sugerida com apoio de IA foi testada, mostrou evidência mais fraca do que parecia e levou a uma ferramenta com promessa mais limitada e defensável.
