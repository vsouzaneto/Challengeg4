# SPEC-DRIVEN — ai-master-challenge

Como evoluir a plataforma de desafios sem inventar serviço, dataset, critério ou canal de entrega.

---

## Fonte de verdade

| Assunto | Onde |
|---------|------|
| O que o git faz hoje | [SPEC-REVERSE.md](SPEC-REVERSE.md) |
| Produto / audiência | [architecture/PRODUCT.md](architecture/PRODUCT.md) |
| Topologia dos 4 serviços | [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) |
| Datasets e chaves | [architecture/DATA-SOURCES.md](architecture/DATA-SOURCES.md) |
| Specs | [specs/README.md](specs/README.md) |
| Modelos lógicos | [erd/00-index-erd.md](erd/00-index-erd.md) · [erd/SPEC-DRIVEN.md](erd/SPEC-DRIVEN.md) |
| Identidade G4 Scale | [design-system/SPEC-DRIVEN.md](design-system/SPEC-DRIVEN.md) · [design-system/GUIDANCE.md](design-system/GUIDANCE.md) |
| Brief público do serviço | `challenges/<id>/README.md` |
| Contrato de PR | `CONTRIBUTING.md` + `submission-guide.md` + `templates/submission-template.md` |

Specs de fatia: `.ai/specs/SPEC-*.md`. Uma spec `in_progress` por vez.

Não criar segundo mapa de desafios neste diretório. Índice público permanece em `challenges/README.md` + `README.md` da raiz.

---

## Regras que o repo já impõe

1. **Quatro serviços, um pipeline.** 001–004 são independentes. Não há orquestração entre eles. Candidato escolhe **um**.
2. **Brief = README do challenge.** Mudança de contexto, dataset, deliverable ou critério **atualiza o README público na mesma mudança** que a spec.
3. **Dados fora do git.** Links Kaggle + chaves declaradas no README. Sem CSV no clone. Sem inventar coluna.
4. **Submissão só via PR** para `main`, pasta `submissions/<nome>/`, título `[Submission] Nome — Challenge XXX`.
5. **Process log é gate.** Sem evidência de uso de IA = desclassificado. Formatos em `submission-guide.md`.
6. **Baseline não é nota de corte pública.** O repo declara que respostas iguais ao “colar o brief na IA” são insuficientes. Não publicar o baseline em `.ai/` nem no README.
7. **PRs de candidato não editam plataforma.** `CONTRIBUTING.md`: só `submissions/<nome>/`.
8. **Time budget 4–6 h** é desenho, não cronômetro. Não adicionar deadline fixo sem decisão explícita do G4.
9. **Sem secrets.** Tokens Kaggle, rubricas privadas e `_internal/` ficam fora do git público e deste `.ai/`.
10. **Não é B4A.** Não criar Linear Project, slug, Cloud Run, Firebase ou Secret Manager para este repo.

---

## Onde colocar mudança nova

| Tipo | Destino |
|------|---------|
| Brief / critério de um serviço | `challenges/<id>/README.md` + spec `SPEC-00N-*.md` + ERD se o modelo de dados mudar |
| Novo challenge | **parar e confirmar** com o G4. Se aprovado: pasta `challenges/<area>-00N-<slug>/`, linha nos dois READMEs, spec + ERD novos |
| Contrato de PR / checklist | `CONTRIBUTING.md` |
| O que enviar / process log | `submission-guide.md` + `SPEC-005-submission.md` |
| README da pasta do candidato | `templates/submission-template.md` |
| Proposta / FAQ / o que avalia | `README.md` da raiz + `SPEC-000-platform.md` |
| Fonte de dados | `architecture/DATA-SOURCES.md` + ERD do serviço |
| Cor / componente UI | `.ai/design-system/` — hex canônico só com reamostra do PDF |

Cópia/layout do brief pode mudar sem nova spec se invariantes (datasets, deliverables obrigatórios, gates de qualidade) permanecerem.

---

## Invariantes por serviço (não diluir)

| Serviço | Gate que a spec não pode afrouxar |
|---------|-----------------------------------|
| 001 Churn | Cruzar as **5** tabelas; causa raiz + segmentos em risco + ações priorizadas |
| 002 Support | Diagnóstico numérico **e** proposta do que automatizar / não automatizar; ambos os datasets |
| 003 Lead Scorer | Software **roda** com dados reais + scoring explicável (não mockup / não “só ordenar por valor”) |
| 004 Social | Análise de engagement **e** estratégia (onde concentrar, patrocínio, o que parar, quick wins) |

Diferenciais (modelo, dashboard, protótipo) são opcionais **exceto** no 003, onde o build é o deliverable principal.

---

## Qualidade

Mudança de brief ou de critério = atualizar spec + README do challenge +, se couber, `challenges/README.md` e o índice da raiz.

Não inventar registro, coluna, licença ou cardinalidade. Se o Kaggle mudou e o README ficou velho → corrigir com evidência (URL + colunas observadas), não “completar de memória”.

Áreas críticas (review humano): critérios de qualidade, datasets/licenças, regras de PR, texto do process log (desclassificação).

---

## Git

Candidato: fluxo em `CONTRIBUTING.md` (fork, `submission/<nome>`, PR para `main`).

Maintainer da plataforma: este `.ai/` e os briefs **não** entram no PR de candidato. Branch/PR de evolução da plataforma é mudança de produto — confirmar com o G4 antes de publicar novo challenge ou alterar gate de desclassificação.
