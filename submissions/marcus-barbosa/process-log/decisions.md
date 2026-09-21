# Ledger de decisões

Origem: **MB** = decisão do Marcus · **CONS** = consenso após discussão · **IA** = sugestão da IA aceita sem alteração.

| # | Data | Decisão | Origem | Evidência / racional |
|---|---|---|---|---|
| 1 | 2026-09-21 | Auditar o repositório e o processo público (176 reviews) antes de escolher o challenge, para eliminar pegadinhas | MB | Pedido explícito: "desenvolvimento blindado de qualquer tipo de viés" |
| 2 | 2026-09-21 | Escolher o Challenge 003 (Lead Scorer) | MB | Painel de agentes deu empate 002=33 × 003=32; Marcus escolheu 003 pelo alinhamento com o negócio do G4 e pelo build |
| 3 | 2026-09-21 | Definição de pronto: 100% dos marcos em `docs/marcos.md`, banca de revisores com 100/100 e revisor final impressionado | MB | Instrução direta |
| 4 | 2026-09-21 | Commits com autoria real (Marcus Barbosa), incrementais; `git add -f` por causa do `.gitignore` da raiz; nunca editar arquivos fora da pasta | CONS | Reviews #2, #55, #57 penalizaram autoria "Claude", edição fora da pasta e commit único |
| 5 | 2026-09-21 | Gerar 3 baselines "brief colado" antes de qualquer análise, para provar superação do baseline do G4 | IA | Metodologia baseline-then-exceed observada na review de maior nota do 003 (#69) |
| 6 | 2026-09-21 | Não usar o token de API do Kaggle colado no chat; download feito pela sessão do próprio Marcus no Chrome. Token deve ser revogado e removido de qualquer export de conversa | MB/CONS | Regra de segurança: a IA não manuseia credenciais; o transcript vai para o repo e não pode conter segredos |
| 7 | 2026-09-21 | Rubrica de diferenciação com 16 itens mensuráveis escrita antes de abrir os CSVs, a partir das lacunas dos 3 baselines | CONS | `differentiation-rubric.md`; lacunas em `baselines/00-sintese.md` |
| 8 | 2026-09-21 | Toda taxa histórica do scoring vem da janela limpa (engajados entre 2017-03-01 e 2017-08-15), por causa do truncamento à esquerda e da censura à direita da base | IA | H21, H12b/c, H10b em `hypotheses.md` |
| 9 | 2026-09-21 | Deals em Engaging com idade acima de 138 dias (1.291, 81% do Engaging) saem do ranking probabilístico e formam o bloco "Confirmar se está vivo", ordenado por valor de lista; o fato vira o achado central para RevOps | CONS | Marcus delegou a escolha à análise com exigência de justificativa e endossou. Razão: nenhum deal fechou após 138 dias (Won e Lost), logo qualquer P(ganho) ali é extrapolação; misturá-los empurraria os deals mais improváveis para o topo por serem caros |
| 10 | 2026-09-21 | Histórico do vendedor não entra no score do deal; carga de deals abertos por vendedor aparece só na visão do gerente | CONS | Marcus delegou e endossou. Razão: H1 (p=0,26) e H2b (gap igual ao nulo binomial) mostram variação compatível com o acaso; incluir criaria viés circular. Teste de invariância: trocar o vendedor não muda o score |
| 11 | 2026-09-21 | Hipóteses ficam registradas com origem IA; o papel do Marcus é documentado como direção (objetivo, barra, método, endosso das decisões), sem atribuir a ele formulações que não fez | MB | Instrução de que tudo seja explicável e verdadeiro; ledger não pode conter atribuição falsa |
