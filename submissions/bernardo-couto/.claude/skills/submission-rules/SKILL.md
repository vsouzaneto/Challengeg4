---
name: submission-rules
description: Regras de submissão do G4 AI Master Challenge destiladas dos READMEs oficiais — PR-only, escopo de arquivos, armadilha do .gitignore, template obrigatório, process log obrigatório, critérios do que torna uma submissão forte ou fraca. Use ao preparar commits, PR, README da submissão ou process log.
user-invocable: false
---

# Regras de submissão (fonte: `../../CONTRIBUTING.md`, `../../submission-guide.md`, `../../README.md`)

## Mecânica

- Fork → branch `submission/bernardo-couto` → pasta `submissions/bernardo-couto/` → PR para `main`.
- Título do PR: `[Submission] Bernardo Couto — Challenge 003`.
- **Só arquivos dentro de `submissions/bernardo-couto/`**. PR que toca outro arquivo é rejeitado. Isso inclui `.gitignore`, README raiz, `.claude/` na raiz.
- **Armadilha dupla:** o `.gitignore` da raiz ignora `submissions/`, então `git add` puro não adiciona nada; e `git add -f` ignora **todos** os `.gitignore`, inclusive o nosso, arrastando `node_modules`/`.venv`. Use sempre `bash tools/git-stage.sh`.
- Um PR por pessoa; atualizações via push na mesma branch.
- Sem deadline fixo; time budget de referência 4–6 h (não há bônus por 40 h).

## Estrutura esperada

```
submissions/bernardo-couto/
├── README.md        ← segue templates/submission-template.md, seção por seção
├── solution/        ← código, dados raw (CC0), instruções de setup
├── process-log/     ← screenshots/, chat-exports/, narrativa, decisões
└── docs/            ← documentação adicional
```

## Process log — obrigatório, sem ele = desclassificado

Deve mostrar: ferramentas de IA usadas e para quê; como o problema foi decomposto antes de promptar; **onde a IA errou e como foi corrigido**; o que o humano adicionou que a IA sozinha não faria; quantas iterações. Formatos aceitos: screenshots, gravação, chat export, narrativa, git history, notebook comentado. Este projeto usa: git history com commits pequenos + `process-log/decisions.md` + configuração `.claude/` versionada + screenshots.

## O que o G4 declara avaliar

- Entendeu o problema antes de executar?
- Usou IA de forma inteligente ou copy-paste?
- O resultado resolve o problema de verdade?
- Alguém consegue entender e agir com base na entrega?

Forte: entendeu o problema; IA usada estrategicamente; output acionável amanhã; process log com iteração e julgamento; comunicação clara para técnico e não-técnico.
Fraca: genérico; zero verificação ("a IA disse, o candidato acreditou"); 1 prompt → 1 resposta; parecer inteligente em vez de resolver; 40 páginas onde 5 bastariam.

## Baseline

O G4 já rodou o brief em Claude, GPT e Gemini. Parecido com isso = "não agregou nada. Próximo." A entrega precisa superar em profundidade de análise, julgamento, qualidade de execução ou criatividade.
