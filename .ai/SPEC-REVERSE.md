# SPEC-REVERSE — ai-master-challenge

| Campo | Valor |
|-------|-------|
| **Repo** | `ai-master-challenge` |
| **Owner** | G4 Educação S.A. |
| **Licença** | MIT (`LICENSE`) |
| **Runtime** | nenhum neste git |
| **Data da leitura** | 2026-09-21 |

## Papel

Repositório público do processo seletivo **AI Master**. Contém o enunciado da seleção, quatro briefs de desafio, o contrato de submissão via Pull Request e o template da pasta do candidato.

Não é API, frontend, worker, admin nem banco. Não há `package.json`, `src/`, Docker, CI de app, Secret Manager ou localhost.

## Árvore observada (2026-09-21)

```
ai-master-challenge/
  README.md                         proposta + FAQ + índice dos 4 desafios
  CONTRIBUTING.md                   fluxo fork → branch → PR
  submission-guide.md               solução + process log (obrigatório)
  LICENSE
  .gitignore
  templates/
    submission-template.md          README da pasta do candidato
  challenges/
    README.md                       matriz de escolha
    data-001-churn/README.md
    process-002-support/README.md
    build-003-lead-scorer/README.md
    marketing-004-social/README.md
```

Ausente no clone (por desenho, via `.gitignore`):

| Path | Motivo |
|------|--------|
| `datasets/` | candidato baixa no Kaggle |
| `submissions/` | só existe no fork do candidato |
| `_internal/` | scoring privado — nunca commitar |

## Pipeline real (único fluxo)

```
candidato lê README raiz
        │
        ▼
escolhe 1 challenge em /challenges
        │
        ▼
baixa datasets no Kaggle (fora do git)
        │
        ▼
resolve (qualquer ferramenta de IA) + process log
        │
        ▼
fork → branch submission/<nome> → pasta submissions/<nome>/
        │
        ▼
PR para main  título: [Submission] Nome — Challenge XXX
```

Único canal de entrega: **Pull Request**. Issue = dúvida, não submissão.

## Contratos vivos (código = markdown)

| Assunto | Onde |
|---------|------|
| O que é AI Master / regras / FAQ | `README.md` |
| Qual challenge escolher | `challenges/README.md` |
| Brief 001 | `challenges/data-001-churn/README.md` |
| Brief 002 | `challenges/process-002-support/README.md` |
| Brief 003 | `challenges/build-003-lead-scorer/README.md` |
| Brief 004 | `challenges/marketing-004-social/README.md` |
| Como abrir PR | `CONTRIBUTING.md` |
| O que enviar | `submission-guide.md` |
| README da pasta do candidato | `templates/submission-template.md` |
| Identidade visual G4 Scale | `.ai/design-system/` (PDF + tokens; reverse em `design-system/SPEC-REVERSE.md`) |

## Invariantes já escritas no repo

1. Preferência: **um** challenge bem feito; mais de um é permitido, superficialidade é penalizada.
2. Time budget projetado: **4–6 horas**. Mais horas não pontuam extra.
3. **Use IA.** Qualquer ferramenta. Sem evidência de processo = desclassificado.
4. Baseline interno: o G4 já rodou cada brief em múltiplos modelos. Copy-paste do brief ≈ baseline = insuficiente.
5. PR só pode tocar `submissions/<nome>/`. Qualquer outro path = rejeição.
6. Um PR por pessoa; updates na mesma branch.
7. Título do PR: `[Submission] Nome — Challenge XXX`.
8. Candidato **não** precisa saber uma linguagem específica, frameworks ou o setor de educação.

## O que este git não é

- Produto B4A / glam / Bfluence.
- Serviço HTTP, Cloud Run, Firebase Hosting ou Cloud SQL.
- Dataset versionado.
- Motor de correção automática (scoring está em `_internal/`, fora do git público).
