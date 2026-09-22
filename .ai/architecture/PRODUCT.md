# Produto — AI Master Challenge

Audiência deste git: candidatos ao papel **AI Master** no G4 e maintainers que editam briefs. Não é superfície consumidora glam / B4A.

## O que é

Processo seletivo que testa se a pessoa consegue entrar numa área (dados, suporte, vendas, marketing), entender o problema de negócio e usar IA generativa como alavanca para entregar algo **acionável** — não um copy-paste do brief.

Um AI Master, no texto do repo:

- Entende o problema **antes** de abrir ferramenta
- Usa IA como alavanca, não muleta
- Entrega solução funcional, não só apresentação
- Sabe o que automatizar e o que não

## Superfície

Não há URL de app. Superfície = GitHub (README + challenges + PR).

| Artefato | Quem | Função |
|----------|------|--------|
| `README.md` | Candidato | Proposta, regras, FAQ, time budget |
| `challenges/*` | Candidato | Brief + dados + critérios |
| `CONTRIBUTING.md` + `submission-guide.md` | Candidato | Como entregar |
| PR em `submissions/<nome>/` | Banca | Única entrada de correção |
| `_internal/` (fora do git) | Banca | Scoring privado |

## Comportamento visível (sucesso)

Candidato lê um challenge, baixa os CSVs no Kaggle, decompõe o problema, itera com IA, verifica números, entrega pasta no formato do template com process log. A banca consegue: (1) reproduzir ou ler o resultado, (2) ver o julgamento humano além do baseline, (3) agir com o output (CEO / Diretor / Head).

## Comportamento visível (falha)

- Sem process log → desclassificado.
- PR altera arquivos fora de `submissions/<nome>/` → rejeitado.
- Output indistinguível do baseline (colar o brief num modelo) → insuficiente.
- 001 sem cruzar 5 tabelas; 002 com um dataset só ou “automatizar 100%”; 003 mockup / notebook sem uso; 004 média por plataforma como conclusão.

## Constraints

- Time budget desenhado: 4–6 horas.
- Qualquer ferramenta de IA é permitida; a ferramenta em si não pontua.
- Comunicação para executivo não-técnico (CEO, Diretor de Ops, Head de RevOps, Head de Marketing).
- Datasets públicos (Kaggle), licenças declaradas no brief (MIT ou CC0).
- Brand do desafio: **G4** / **AI Master**. UI: identidade **G4 Scale** (`.ai/design-system/`). Empresa fictícia do 001: **RavenStack**. Não misturar com brand glam nem com o rebrand institucional G4 2026 (dourado / esfera armilar).

## O que não é

- Curso, bootcamp ou certificado.
- Hackathon com ranking público neste git.
- Plataforma de correção automática no clone público.
- Produto SaaS do G4 (os quatro “clientes” dos briefs são cenários).
