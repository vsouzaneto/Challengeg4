# Camada de dados e scoring

Python 3.10 ou superior. O motor usa somente a biblioteca padrão.
A interface opcional em `app.py` requer Streamlit, listado em `requirements.txt`.
Não há exportação automática de arquivos.

## Interface

Streamlit não estava instalado no ambiente de implementação e não foi instalado.
A execução visual permanece pendente. Quando a dependência estiver disponível,
execute na raiz do repositório:

```powershell
python -B -m streamlit run submissions/luciano-henrique/solution/app.py --browser.gatherUsageStats=false
```

O aplicativo calcula o ranking global antes de aplicar filtros. Manager e região
são apenas contexto de filtro. Seleções vazias significam todos; filtros combinam-se
por interseção. A Watchlist também respeita esses filtros e não exclui linhas do ranking.
Price Only altera somente a ordenação, sem recalcular scores. A seleção de uma
oportunidade mostra evidência e explicação determinística, sem LLM.

`app.py` pode ser importado sem Streamlit porque a dependência visual é carregada
somente em `main()`. Isso permite testar integração e filtros sem fingir uma
validação de renderização. `test_app.py` cobre preservação da carteira, scores
globais em cada filtro, filtros combinados, Watchlist, baseline e explicações.

Na raiz do repositório:

```powershell
python -B submissions/luciano-henrique/solution/run.py
python -B -m unittest discover -s submissions/luciano-henrique/solution -p "test_*.py" -v
```

O caminho dos CSVs é resolvido a partir de `data.py`, independentemente do diretório
de execução. `-B` evita arquivos de cache Python. A execução imprime resumo e top 10.
`score_open_opportunities(load_data())` retorna todas as oportunidades abertas em
memória, com evidências, baseline de preço, Watchlist e scores.

## Regras fixas

- `GTXPro` vira `GTX Pro` somente em memória. CSVs originais não são modificados.
- Abertas: Prospecting/Engaging; histórico: Won/Lost.
- Referência padrão: 31/12/2017, inclusive. É uma simulação de fim do período,
  não a data comprovada de extração. `close_date` só restringe disponibilidade do
  histórico e verifica consistência temporal; nunca entra como feature.
- Taxa geral: Won / encerradas disponíveis na referência.
- Taxa ajustada: `(Won_grupo + 50 * taxa_geral) / (n_grupo + 50)`.
- Historical Fit: média simples das taxas ajustadas de produto e vendedor.
- Balanced Priority: `sales_price * historical_fit`.
- Priority Score: `100 * (rank_médio - 1) / (N - 1)` em TODAS as abertas.
  Empates recebem o mesmo percentil; caso único ou todos iguais recebem 50.
  Preservar o score global ao filtrar; arredondar apenas para apresentação.
- Confiança da evidência: Alta se ambos os suportes >= 200; Média se ambos >= 50;
  Baixa nos demais casos. Não é garantia de acerto ou intervalo estatístico.
- Watchlist: preço >= percentil 80 (interpolação linear) e confiança Baixa.
  Empates no limite são incluídos. Watchlist nunca remove uma linha do ranking.
- Produto/vendedor sem histórico: taxa geral como fallback, suporte zero.
  Suportes não são somados: os grupos se sobrepõem. Shrinkage não cria exemplos reais.
- ID desempata apenas a exibição, sem alterar o Priority Score.

## Contrato e limites

Priority Score NÃO é probabilidade de fechamento. Historical Fit NÃO é uma
probabilidade calibrada. Balanced Priority é uma heurística econômica, não uma
promessa de receita ou lucro. O teste temporal anterior não demonstrou ganho
confiável sobre preço sozinho.

O resultado mantém `sales_price` como baseline e expõe `n_product`,
`n_sales_agent`, as duas taxas ajustadas, `confidence` e `watchlist`.
Conta é apenas contexto; setor, manager e região não entram no score.
`close_value` não é lido pelo scoring. Won/Lost é usado exclusivamente como
resultado do histórico, nunca como feature das abertas.

O carregador interrompe para chaves duplicadas, referências preenchidas inválidas,
estágios desconhecidos ou CSVs malformados. Conta vazia é aceita. Scoring interrompe
para preço inválido, histórico indisponível ou datas inconsistentes.

Não reconstruímos carteiras passadas: filtrar resultados por data não recupera
o estado histórico das oportunidades. A função recebe o snapshot aberto fornecido;
cadastros e preços não têm versões temporais. Para simular outro snapshot, fornecer
os dados correspondentes. Ausência de todas as abertas retorna ranking vazio.

Testes cobrem regressão do dataset, preservação dos CSVs, exclusão de resultados
futuros, independência de campos proibidos, fallback, shrinkage, empates e confiança.
