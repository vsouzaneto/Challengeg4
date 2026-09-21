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
