# Relatório de qualidade dos dados (G2)

> **Em 3 linhas:** o arquivo está íntegro no formato, mas **não descreve uma operação real**. Views, likes, shares e comentários se comportam exatamente como um sorteio de Poisson com **a mesma média para todos os 52.214 posts**, e as demais colunas não têm associação entre si. Sem acesso ao gerador, isto é inferência pela assinatura estatística, não prova de origem; mas nenhuma operação real produz essa assinatura. Por isso nenhuma característica de post, creator, audiência ou patrocínio pode explicar resultado; qualquer "insight" de performance extraído deste arquivo é ruído.

Reprodução: `uv run python src/audit/run_audit.py`. Tabelas em `outputs/tables/dq-*.csv`.

## 1. O mecanismo: por que não há sinal (D1 da rubrica)

Numa distribuição de Poisson, **a variância é igual à média**. Contagens de engajamento em redes sociais reais são sobredispersas (variância muito maior que a média), porque poucos posts viralizam e muitos fracassam; é por isso que se usam modelos como a binomial negativa.

| Métrica | Média | Variância / média | p (H₀: Poisson) |
|---|---:|---:|---:|
| views | 10.100 | **0,991** | 0,13 |
| likes | 1.510 | **1,003** | 0,63 |
| shares | 300 | **0,999** | 0,82 |
| comments | 200 | **0,993** | 0,27 |

- Nenhuma métrica rejeita Poisson (p > 0,05 em todas).
- Nos **76 segmentos** testados (plataforma, formato, categoria, patrocínio e idade da audiência), a razão fica entre **0,94 e 1,04**, e a média (λ) varia no máximo **0,29%** entre segmentos (`dq-poisson.csv`).
- As métricas são **independentes entre si**: r(likes, views) = 0,001; r(shares, views) = −0,007; r(views, seguidores) = 0,005. No mundo real, mais views trazem mais likes.
- **Consequência:** o engajamento é praticamente constante (19,9%) *por construção*. As diferenças observadas entre segmentos vão no máximo a **0,0126 p.p.** (idade da audiência; `dq-segment-amplitude.csv`) e são o ruído esperado de um sorteio. Os testes de significância do baseline estavam certos, mas não diziam **por quê**.

## 2. Achados

| ID | Severidade | Achado | Número | Tratamento |
|---|---|---|---|---|
| DQ-01 | OK | Estrutura íntegra | 52.214 × 27; zero duplicatas; zero inconsistência de patrocínio | nenhum |
| DQ-02 | Menor | Nulos em texto | hashtags 16,7%; comments_text 16,6% | preservar ausência |
| DQ-03 | Maior | Orgânico codificado como texto | `sponsor_name = "Not sponsors"`, `disclosure = "none"` | regra explícita nas agregações |
| DQ-04 | **Crítica** | Sem cauda e sem fracasso | 0 posts com métrica zerada; o maior post tem 1,09x as views do menor | não há "top performers" a copiar (viés de sobrevivência invertido) |
| DQ-05 | **Crítica** | Gerador Poisson com λ fixo | var/média 0,99–1,00 | nenhum achado de performance é acionável |
| DQ-06 | **Crítica** | Métricas independentes entre si | todos os \|r\| < 0,01 | alcance não gera interação neste arquivo |
| DQ-07 | Maior | Sem cadastro mestre de creator | 100% dos 5.000 creators com mais de 1 nome; desvio de seguidores dentro do creator (284 mil) ≈ população (288 mil) | tamanho de creator = atributo do post |
| DQ-08 | Maior | Seguidores uniformes | KS contra uniforme D = 0,003; faixa 1.013–999.998; nano 0,87%; mega (>1M) = 0 | faixas "mega" não existem |
| DQ-09 | Maior | Cadência fixa | todo creator tem 10–11 posts em 2 anos | frequência ótima não é mensurável |
| DQ-10 | Maior | `content_length` sem unidade | mesma distribuição para vídeo, imagem e texto (Kruskal p = 0,94) | faixas "30–60s" não significam nada |
| DQ-11 | Maior | Texto de gerador de dados falsos | 0% das URLs são de plataformas; 100% dos sponsors com nome no padrão de empresa gerada; 971 hashtags distintas, 7,7% palavras como "or" e "their" | hashtag/NLP inválido |
| DQ-12 | Maior | Sem custo nem resultado | não há custo, fee, campaign_id, cliques, conversão, receita | ROI e custo implícito só como função paramétrica |
| DQ-13 | Maior | Audiência agregada | 1 faixa etária, 1 gênero e 1 país por post | vale para o post, não para a pessoa |
| DQ-14 | Maior | Tempo sem padrão humano | ~2.200 posts/mês constantes; 3h da manhã = 2.193 vs 19h = 2.267 (χ² p = 0,59) | horário e sazonalidade não inferíveis |
| DQ-15 | Maior | Colunas sorteadas independentemente | Cramér's V ≤ 0,013 em 7 pares; 1.360 posts em chinês com audiência no Brasil | persona/segmentação sem base |
| DQ-16 | Info | Audiência Brasil | 6.505 posts (12,5%), distribuídos igualmente pelas 5 plataformas | reforça DQ-15 |

## 3. Veredito: o que o arquivo permite afirmar

| ✅ Pode | ❌ Não pode |
|---|---|
| Descrever a composição do arquivo | Dizer o que "gera engajamento" |
| Mostrar que patrocínio e orgânico são **equivalentes** neste arquivo (G3) | Calcular ROI ou custo real de patrocínio |
| Usar o arquivo como **teste de calibração** das ferramentas (um bom detector precisa dizer "sem sinal" aqui) | Definir threshold de seguidores, frequência, horário ou duração |
| Diagnosticar **o que a operação não registra** (seção 4) | Segmentar pessoas por idade, gênero ou país |
| | Treinar modelo preditivo útil |

## 4. Ponte para o processo
Cada lacuna acima foi mapeada para a etapa da operação que deveria gerar o dado: `docs/gap-to-process-map.md`.

## Gate G2
**PASS**: auditoria reproduzível; achados com número; limites de inferência declarados.

**Decisões pendentes do Douglas:**
1. Tratar o arquivo como "dados sintéticos de uma operação hipotética" e seguir com a análise obrigatória como **exercício de método**, ou tratar a descoberta como o achado principal do relatório?
2. Limiar de relevância prática para o G3 (sugestão: **±1 p.p.** de engagement rate e **±5%** de views. Abaixo disso, nenhuma decisão de verba muda).
