# 15/10/2026 — Origem dos +19% e demo pública

## Pedido

Depois de abrir o PR, o candidato pediu uma avaliação como se fosse o avaliador. A IA apontou duas melhorias, e o candidato pediu para fazer as duas:
- corrigir a explicação dos +19%, que era o ponto mais arriscado;
- publicar uma demo que o avaliador abra sem instalar nada, a melhoria que as reviews mais citam.

## A explicação dos +19%

**O que estava escrito.** README, Dashboard e procedimento atribuíam o ganho a "não perder tempo com parados" (0 de 750 escolhas, contra 91).

**A crítica da IA, e o erro dentro dela.** Na avaliação, a IA afirmou que tirar os parados sozinho não ganhava nada. A base era a variante com desempate "mais antigo primeiro", que rendeu 1,74 mi, quase igual a "só valor". Essa variante não é neutra: ela escolhe os negócios perto do limite, que fecham menos.

**O que os dados mostram.** Foram acrescentadas duas variantes neutras e um bootstrap pareado (150 pares vendedor × data, 5.000 reamostras, semente fixa).

| Variante | Receita | Vagas com parados |
|---|---:|---:|
| Só valor | 1,76 mi | 91 |
| Colunas, sem desempate por idade | 1,90 mi | 0 |
| Valor e mais novo primeiro, sem colunas | 2,06 mi | 31 |
| Lead Kanban | 2,09 mi | 0 |

- O ganho vem da idade do negócio. Tirar os parados explica cerca de 40% dele; preferir os mais novos, o restante. A explicação antiga não estava errada, mas cobria menos da metade.
- Ganho sobre "só valor": +18,5%, com IC 95% de +12,4% a +25,4%.
- Sobre "valor e idade, sem colunas", a vantagem é pequena (+0,4% a +2,5%). As colunas valem por tirar os parados da agenda e dar a eles uma ação própria. O texto agora diz isso, em vez de vender as colunas como a fonte do ganho.

**Correções.**
- No Dashboard, o fato 4 ganhou três barras (só valor, sem os parados, Lead Kanban), a margem provável e a frase "vem da idade do negócio".
- No procedimento, a tabela tem as quatro variantes e a decomposição.
- README, doc 09 e o README da solução foram alinhados.
- Os resultados anteriores do JSON ficaram idênticos; só foram acrescentadas as chaves novas.

## Demo pública

- **Ajuste do app:** ele passou a buscar os dados por caminho relativo. Sem o servidor Python, lê `data/board.json`.
- **Geração da demo:** `build_static.py` copia a interface e grava esse JSON com o mesmo payload de `/api/board`. A página gerada é marcada como estática, para não tentar o servidor e registrar um erro 404 no console a cada visita.
- **Teste antes de publicar:** os arquivos foram servidos numa subpasta, como no GitHub Pages, sem servidor Python. Funcionaram os 75 cartões, o fato 4 corrigido, o procedimento e o vídeo, sem erros no console.
- **Publicação:** no GitHub Pages do fork do candidato, num branch separado (`gh-pages`), fora do PR.

## Onde a IA errou nesta etapa

1. **A crítica que exagerava.** A afirmação de que "tirar os parados sozinho não ganha nada" se apoiava numa variante enviesada. Ela foi refeita com variantes neutras antes de mudar qualquer texto.
2. **Arredondamento que escondia o resultado.** O intervalo da comparação com "valor e idade" aparecia como "+0% a +2%", o que esconde que ele é positivo. Valores pequenos passaram a ter uma casa decimal.
