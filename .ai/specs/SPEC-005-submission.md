---
status: passing
canonical: true
area: entrega
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-005 Submissão (solução + process log + PR)

## Comportamento visível

Toda entrega tem **duas partes**. Falta a segunda = desclassificado, independente da qualidade da primeira.

A banca precisa ver **como** a pessoa usou IA, não só o artefato final.

## Contrato

### Parte 1 — Solução

Formato livre, limitado pelo challenge:

| Serviço | Núcleo da solução |
|---------|-------------------|
| 001 | Relatório de diagnóstico |
| 002 | Diagnóstico + proposta de automação (+ protótipo opcional) |
| 003 | Software que roda + docs de setup/lógica/limites |
| 004 | Análise + estratégia (+ ferramenta opcional) |

Estrutura que o guia diz que “funciona bem” (não é schema rígido):

1. Executive summary (1 parágrafo)
2. Abordagem
3. Resultado
4. Recomendações
5. Limitações

O template (`templates/submission-template.md`) materializa isso no README da pasta.

### Parte 2 — Process log

Formatos aceitos (um ou combinação): screenshots, screen recording, chat export, narrativa, git history, notebook comentado.

O log precisa mostrar:

- Ferramentas e por quê
- Decomposição **antes** de promptar
- Onde a IA errou e a correção
- O que o humano adicionou que a IA sozinha não faria
- Quantas iterações

Um prompt → uma resposta → PR = submissão fraca / baseline.

### Parte 3 — Canal git

Ver [SPEC-000-platform.md](SPEC-000-platform.md). Path, título de PR e restrição de diff são gate.

## Forte vs fraco (régua pública)

**Forte:** entendeu o problema; IA estratégica; output acionável amanhã; iteração e julgamento; comunicação clara para técnico e não-técnico.

**Fraco:** genérico para qualquer empresa; zero verificação (IA disse, candidato acreditou); um shot; parecer inteligente em vez de resolver; 40 páginas onde 5 bastavam.

## Verificação

- [ ] Template ainda tem seção `Process Log — Como usei IA` marcada como desclassificatória.
- [ ] Guia ainda lista os seis formatos de evidência.
- [ ] `CONTRIBUTING.md` ainda tem o checklist (challenge lido, pasta certa, process log, template, setup se houver código, sem editar o resto).

## Evidência

2026-09-21: `submission-guide.md` + `CONTRIBUTING.md` + `templates/submission-template.md`.

## Notas

Evidências podem ser link (Loom) ou arquivos em `process-log/`. Não exigir um único formato.

## Sucesso / falha

- Sucesso: README do template preenchido + `solution/` + `process-log/` com iteração visível; PR no formato.
- Falha: só `solution/` sem log; ou log = “usei o ChatGPT”.

## Migração e compatibilidade

Nomes `solution/`, `process-log/`, `docs/` e o título `[Submission] …` são estáveis. Mudar o gate de desclassificação exige confirmação do G4.
