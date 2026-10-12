# Process log — narrativa passo a passo

Sessão única de IA (Claude, via Cowork com o painel do Claude in Chrome aberto na aba do repositório), 11/10/2026, cerca de 4 horas. Abaixo, cada etapa, o que eu pedi, o que a IA fez, e onde eu intervi. Os prints em `screenshots/` seguem a mesma numeração.

## Etapa 1 — Ler tudo procurando pegadinha (≈20 min)
**Meu prompt (resumido):** "Eu preciso cumprir esse challenge. Tome cuidado para não cair em pegadinhas que podem estar embutidas no challenge."
**O que a IA fez:** leu o README pela aba do navegador, clonou o repositório, listou os 10 arquivos, leu os 4 challenges, CONTRIBUTING, guia, template e `.gitignore`, e procurou texto oculto (comentários HTML, caracteres invisíveis).
**Achados:** `submissions/` ignorado pelo `.gitignore`; regra de não alterar arquivos fora da pasta; baseline de IA já existente; título de PR rígido; suspeita prévia de que os datasets do Kaggle citados são sintéticos.
**Minha decisão:** nenhuma ainda — pedi comparação de custo entre os challenges.

## Etapa 2 — Escolher o challenge pelo custo-benefício (≈5 min)
**Meu prompt:** "Qual desses vai consumir menos token?"
**IA:** ordenou 003 < 001 < 004 < 002 com justificativa. Recomendou 003 pela economia.
**Minha decisão:** 004, por ser minha área (marketing) — aceitei o custo maior.

## Etapa 3 — Dados (≈10 min)
A IA tentou baixar do Kaggle direto e a rede bloqueou. Baixei manualmente e anexei o `archive.zip`. Informei nome, LinkedIn e que o GitHub estava logado no Chrome.

## Etapa 4 — Auditoria de qualidade antes de qualquer análise (≈30 min)
**IA (sem eu pedir especificamente, mas por causa da instrução da etapa 1):** ao ver a primeira linha do CSV, apontou texto gerado por Faker e propôs auditar antes de analisar. Rodou perfil completo: distribuições, correlações, consistência de creator, engajamento por corte.
**Resultado:** views Normal(10.100 ± 100), correlações ≈ 0, engajamento 19,9% em todo corte.
**Minha intervenção:** nenhuma correção necessária; aceitei a proposta de confirmar com testes formais antes de decidir a entrega.

## Etapa 5 — Testes formais (≈20 min)
Kruskal-Wallis em 90 combinações fator × métrica, Shapiro/KS para forma das distribuições, t-test patrocinado × orgânico, split-half de 120 segmentos, gradient boosting com validação cruzada. Tudo confirmou: ruído puro. Resultado que poderia enganar: 2 testes "significativos" — a IA comparou com a taxa esperada por acaso (4,5) e descartou.

## Etapa 6 — Decisão de entrega (≈5 min)
**IA:** apresentou três caminhos: (a) auditoria + ferramenta + plano, (b) auditoria + estratégia em documento, (c) fingir sinal (desaconselhado). Perguntou também se podia usar minha experiência profissional como contexto.
**Minha decisão:** (a), e contexto genérico (sem nomes nem números internos).

## Etapa 7 — Script reproduzível e gráficos (≈30 min)
A IA escreveu `solution/analysis/run_audit.py` (recebe o CSV, gera `summary.json`, `segments.csv` e 5 figuras, imprime o veredito), rodou e inspecionou um gráfico antes de seguir.

## Etapa 8 — Ferramenta: Social Signal Gate (≈60 min)
A IA escreveu o `template.html` (HTML único, sem dependências, parser de CSV próprio, teste de permutação, split-half, CV, consistência de creator, painel bloqueável) e o `build_dashboard.py` que embute os números do dataset do challenge para o arquivo abrir sozinho. Gerou um CSV sintético com sinal plantado para testar o caminho "verde" e rodou Playwright nos dois cenários: vermelho/bloqueado com o Kaggle, verde/liberado (r = 0,99) com o CSV de teste, zero erros de console. Tirou screenshots.

## Etapa 9 — Textos (≈40 min)
Auditoria (01), estratégia (02), README no template, este log. Revisei README, auditoria e estratégia e aprovei sem alterações — o texto já refletia as decisões que eu tinha tomado nas etapas 2, 4 e 6.

## Etapa 10 — Git (≈15 min)
Troquei o conector GitHub da sessão para a minha conta definitiva. Fork no GitHub, branch `submission/diego-falabella`, subida dos arquivos pelo conector GitHub da sessão (o `.gitignore` do repo ignora `submissions/`, então quem usa git local precisa de `git add -f`), PR com o título no formato exigido. Verificado que nenhum arquivo fora da pasta foi alterado.

## Iterações
Contei 1 iteração de auditoria → 1 de confirmação → 1 de decisão → 1 build do script → 1 build + 1 teste da ferramenta → 1 rodada de textos + 1 revisão. Nenhum prompt único gerou a entrega; a maior parte do valor veio das perguntas de bifurcação (pegadinha? custo? dá pra confiar? qual caminho?) e não do volume de output.
