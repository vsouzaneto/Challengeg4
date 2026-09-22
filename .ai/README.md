# `.ai/` — hub Spec-Driven (AI Master Challenge)

Índice operacional deste git. O repositório **não** é um produto B4A nem um runtime com API/DB. É a plataforma de desafios do processo seletivo **AI Master** (G4 Educação): briefs, contrato de submissão e critérios de qualidade.

Os quatro challenges são tratados aqui como **serviços independentes** que compartilham o mesmo pipeline de entrada (fork → branch → PR) e o mesmo contrato de evidência (process log).

```
.ai/
  SPEC-REVERSE.md     o que o repo faz hoje
  SPEC-DRIVEN.md      como evoluir sem inventar contrato
  architecture/       produto, topologia, fontes de dados
  specs/              specs SDD por serviço + plataforma
  erd/                modelos lógicos dos datasets (Kaggle)
  design-system/      identidade G4 Scale (PDF → tokens → componentes)
```

| Pasta / arquivo | Comece por |
|-----------------|------------|
| Reverse | [SPEC-REVERSE.md](SPEC-REVERSE.md) |
| Evolução | [SPEC-DRIVEN.md](SPEC-DRIVEN.md) |
| Produto | [architecture/PRODUCT.md](architecture/PRODUCT.md) |
| Topologia | [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) |
| Dados | [architecture/DATA-SOURCES.md](architecture/DATA-SOURCES.md) |
| Specs | [specs/README.md](specs/README.md) |
| ERDs | [erd/00-index-erd.md](erd/00-index-erd.md) · reverse [erd/SPEC-REVERSE.md](erd/SPEC-REVERSE.md) |
| Design system | [design-system/README.md](design-system/README.md) |

## Serviços (challenges)

| ID | Pasta | Área | Tipo |
|----|-------|------|------|
| 001 | `challenges/data-001-churn` | Dados / Analytics | Análise |
| 002 | `challenges/process-002-support` | Operações / CX | Diagnóstico + automação + build |
| 003 | `challenges/build-003-lead-scorer` | Vendas / RevOps | Build (software funcionando) |
| 004 | `challenges/marketing-004-social` | Marketing | Análise + estratégia |

Fonte canônica de cada brief: o `README.md` da pasta do challenge. Este `.ai/` **não** substitui o README público — organiza contrato, invariantes e modelo de dados para agentes e maintainers.

## Proibido neste diretório

- Secrets, tokens Kaggle, connection strings.
- Inventar Linear Project, slug B4A, GCP (`b4a-prj-*`) ou runtime que o git não tem.
- Copiar datasets para o git (`datasets/` é gitignored).
- Inventar colunas, chaves ou cardinalidade que o README do challenge não declara.
