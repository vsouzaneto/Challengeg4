# Como o avaliador do G4 pontua: rubrica e armadilhas extraídas das reviews públicas

Resumo verificável da auditoria feita antes de escolher o challenge (21/09/2026). Fonte primária: as reviews públicas do avaliador nos PRs do repositório Gestao-Quatro-Ponto-Zero/ai-master-challenge, coletadas com `gh api repos/.../pulls/{n}/reviews`. Os números de PR citados permitem conferir cada afirmação no GitHub.

Escopo: clone local (`ai-master-challenge/`, HEAD 4aed364), branch alternativo, histórico git, metadados públicos do GitHub (100 PRs, 1 issue, 176 reviews do avaliador), páginas dos 5 datasets no Kaggle e repositórios da organização G4.

## 1. Veredito de segurança

Nenhum conteúdo malicioso, oculto ou manipulador foi encontrado dentro do repositório.

| Verificação | Resultado |
|---|---|
| Caracteres invisíveis / bidi / zero-width / tags Unicode em todos os arquivos | 0 ocorrências (só acentos PT-BR, travessão, setas e box-drawing) |
| Comentários HTML, texto colapsado, links `javascript:`/`data:` | nenhum |
| Padrões de prompt injection ("ignore previous", "system prompt", etc.) | nenhum |
| Hooks git ativos, config remoto alterada, objetos dangling | nenhum |
| Arquivos deletados no histórico | só os arquivos brief originais (versão antiga dos READMEs, sem conteúdo oculto) |
| Branch `compass-github-importer` | versão antiga + `compass.yml` (config Atlassian Compass, inofensivo) |
| GitHub Actions / rulesets / branch protection | nenhum (0 workflows) |
| Bot no repo | Codex (OpenAI) faz review automático em alguns PRs — apenas sugestões de código |
| Datasets | Kaggle oficial; licenças MIT (001, 004) e CC0 (002, 003) confirmadas |

## 2. Pegadinhas reais (não maliciosas, mas derrubam candidatos)

1. **`submissions/` está no `.gitignore` do próprio repo.** `git add submissions/x` é silenciosamente ignorado. É preciso `git add -f` ou criar um `.gitignore` próprio dentro da pasta. Editar o `.gitignore` da raiz viola a regra "não modifique arquivos fora da sua pasta" (PR #55 foi cobrado por isso).
2. **Datasets 001, 002 e 004 são sintéticos.** O avaliador premia quem detecta isso (CSAT aleatório r=-0,001, 49,3% de timestamps invertidos, placeholders `{product_purchased}` no texto, views com std=100, AUC 0,50 em churn). Quem gera "insights" sobre ruído é penalizado. Quem inventa dados sintéticos próprios foi reprovado (PR #85).
3. **Leakage de target no 001.** `upgrade_flag`/`downgrade_flag`/`reason_code`/`refund` só existem na tabela de churn. AUC ~1,0 = reprovação automática (PR #2, #78).
4. **Data de referência no 003.** O dataset é de 2017. Usar `hoje` zera recência ou dá 3.199 dias para tudo. Ancorar em `max(close_date)`.
5. **`GTXPro` vs `GTX Pro`** no `products.csv` do 003: sem normalizar, ~1.480 deals são descartados no join.
6. **Win rate com denominador errado** (inclui deals abertos) foi cobrado explicitamente (PR #60).
7. **Pasta `submission/` (singular) quebra o tooling automatizado** de auditoria (PR #102).
8. **node_modules / venv / dados brutos / modelos .pkl commitados = reprovação por higiene**, mesmo com conteúdo bom (PR #48, #82, #96).
9. **Process log em .docx/.pdf/link externo não conta.** Só Markdown + screenshots + chat exports versionados no repo.
10. **Commits com author "Claude"** foram usados como evidência contra o candidato (PR #2). Commit único também pesa contra ("histórico concentrado").
11. **"Edit automatically" ligado no Claude Code** e prompts do tipo "você é um programador sênior, faça tudo" foram citados como sinal negativo (PR #17).
12. **Avaliação é assistida por IA** ("Avaliação por G4 OS — assistente de avaliação"). O texto da submissão será lido por um LLM antes do humano. Implicação: clareza e estrutura contam; qualquer coisa que pareça instrução ao avaliador é risco.
13. **Fila atrasada.** Última review do avaliador em 2026-08-03; 28 PRs (do #106 ao #135) sem nenhuma review. Um novo avaliador (luizsoares2509) apareceu em 18/09 concedendo "segundas chances", sinal de que o processo foi retomado.

## 3. Rubrica real (extraída das reviews)

Quatro eixos: **Leitura do problema · Qualidade do output · Uso de IA (30%) · Comunicação.**

O que aprova (padrões recorrentes nos scores 8–9,3):
- Hipóteses próprias escritas ANTES de abrir a IA; hipóteses refutadas pelos dados documentadas.
- Auditoria de qualidade dos dados como primeira etapa, com números.
- Erros da IA documentados com causa raiz e correção (5 a 8 erros é a faixa dos aprovados fortes).
- Separação explícita "decisão minha / consenso / sugestão da IA".
- Ferramenta funcional, com dados reais, explicável por item, com testes automatizados.
- Honestidade: declarar AUC 0,5, dizer o que NÃO automatizar, ROI com premissas declaradas e intervalo.
- Commits incrementais (10+), screenshots das sessões (não só do app), chat exports em texto.
- Deploy público ou setup reprodutível sem chave de API.

O que reprova: process log ausente/narrativo, artefatos fora do repo, template não preenchido, leakage, higiene ruim, template genérico gerado por IA, pasta errada.

## 4. Estatística por challenge (100 PRs, 21/09/2026)

| Challenge | PRs | Taxa de aprovação entre avaliados | Score médio / máximo |
|---|---|---|---|
| 001 Churn | 27 | 50% | 7,3 / 9,3 |
| 002 Suporte | 23 | 92% | 8,6 / 9,0 |
| 003 Lead Scorer | 56 | 60% | 7,6 / 9,1 |
| 004 Social | 18 | 62% | 6,0 / 8,2 |

## 5. Contexto G4 (fora do repo)

- Org GitHub: `twenty-crm-g4` (fork do Twenty CRM, jun/2026), `g4os` (AI Chief of Staff), `g4os-skills` (skills de vendas, RFM, "onde usar IA"), Flowise.
- Vaga oficial: https://ats.g4business.com/careers/g4-ai-master-r6gpj1 (inscrição obrigatória para avançar).
- Avaliadores: João Vitor Chaves Silva (joaovitor2763) e Luiz Soares (luizsoares2509).

## 6. Painel de escolha do challenge (2026-09-21)

4 juízes (estratégia G4, sinal de contratação, risco/concorrência, viabilidade/blindagem) + 3 céticos. Resultado: 002 = 33, 003 = 32, 001 = 24, 004 = 20,5. Um cético derrubou o 002 em favor do 003; dois mantiveram. Síntese completa fora do repositório (painel de agentes); o resultado que importou está no README da submissão.

Leitura: 002 é o caminho de aprovação mais seguro (92%, falhas só de higiene); 003 é o mais alinhado ao negócio do G4 (CRM próprio) e ao build com Claude Code, com pegadinhas determinísticas fecháveis por teste, mas 56 concorrentes. A vaga (descrição pública no ATS do G4) valoriza "construir ferramentas internas e protótipos funcionais sem engenharia dedicada" e discovery end-to-end.
