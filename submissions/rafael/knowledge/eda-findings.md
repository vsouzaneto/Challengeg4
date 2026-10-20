# EDA — Os dados são ruído (confirmado)

Script: `process-log/probe_eda.py` · saída: `process-log/probe_eda_output.txt`.

## Evidências
- **Métricas = Poisson independentes**: views ~10.100 (desvio padrão 100; variância/média = 0,99 → Poisson), likes ~1.510, shares ~300, comments ~200. Correlação entre elas ≈ 0 (|ρ| < 0,01).
- **Sem cauda longa**: min/máx de views = 9,6K–10,6K. Nenhum post viral, nenhum post com engajamento zero (o alerta de survivorship bias não se aplica).
- **Engajamento não depende de nada**: Kruskal-Wallis p > 0,2 para plataforma, tipo, categoria, patrocínio, idioma, idade, gênero, país, disclosure, categoria do patrocinador e trimestre. Média ≈ 0,199 em todos os grupos.
- **Seguidores sem efeito**: follower_count ~ Uniforme(0, 1M) (KS p = 0,87); ρ(seguidores, views) = 0,005. Um creator com 5K seguidores tem as mesmas views de um com 1M → irreal.
- **Inconsistências**: o mesmo creator tem ~10 follower_counts diferentes (máx/mín mediano = 14x); content_length 10–599 para todos os tipos (texto/imagem com "duração"); legendas, hashtags e comentários são palavras aleatórias (Faker).
- Datas: 2023-05-29 → 2025-05-28, sem sazonalidade.

## Implicação
Qualquer "insight" de engajamento extraído deste dataset é **ruído**. As respostas de LLM (o baseline) vão reportar diferenças de 0,0001 como se fossem padrões. O valor real está em:
1. Provar isso de forma executiva e rigorosa (testes, tamanho de efeito, poder estatístico).
2. Entregar o **método + ferramenta** que funciona quando entrarem dados reais (ou mostrar que o pipeline detecta efeitos quando eles existem: injetar efeito sintético e recuperá-lo).
3. Recomendações para o que *pode* ser decidido: custo (patrocínio com o mesmo resultado = desperdício), instrumentação de dados, experimentos A/B.

## Entidades e chaves (notebook 01_eda, seção 7)
- Arquivo único (flat): post + creator + patrocinador + audiência.
- `content_id` = chave confiável. `content_url` se repete (28K distintas).
- `creator_id` **não** é estável: ~10 nomes, ~10 follower_counts, 5 plataformas e 3 categorias por id → só dá para analisar "tamanho do creator" no nível do post.
- `sponsor_name`: 18K distintos em 22K posts (nomes Faker); o mesmo nome aparece em até 6 categorias.
- Patrocínio consistente: `is_sponsored=False` ⇔ disclosure `none` ⇔ sponsor "Not sponsors".
- Categóricas independentes entre si (V de Cramér ≈ 0).
