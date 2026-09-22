---
status: passing
canonical: true
area: plataforma
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-000 Plataforma AI Master (pipeline compartilhado)

## Comportamento visível

O git público explica o papel, lista quatro desafios, manda o candidato escolher **um**, baixar dados no Kaggle, resolver com IA e entregar **somente** por Pull Request.

Não há app, login nem correção automática no clone.

## Contrato

### Entrada

1. Candidato lê `README.md` e `challenges/README.md`.
2. Escolhe exatamente um serviço (001–004). Mais de um é permitido pelo FAQ, mas a plataforma **prefere** um bem feito.
3. Time budget de desenho: 4–6 horas. Sem cronômetro público.

### Regras de uso de IA

1. Usar IA é esperado. Qualquer ferramenta.
2. Sem evidência de processo → desclassificado (`submission-guide.md`).
3. Colar o brief e enviar a primeira resposta ≈ baseline interno → insuficiente.
4. Não se avalia linguagem, framework, ferramenta X/Y nem experiência no setor de educação.
5. Avalia-se: entendimento do problema, uso inteligente de IA, resultado que resolve, comunicação acionável.

### Saída (pasta)

```
submissions/<nome>/
  README.md          ← templates/submission-template.md
  solution/
  process-log/
  docs/              ← opcional
```

### Canal

1. Fork → `submission/<nome>` → push → PR para `main`.
2. Título: `[Submission] <Nome> — Challenge XXX`.
3. Diff só em `submissions/<nome>/`. Qualquer outro path → rejeição.
4. Um PR por pessoa; atualização = push na mesma branch.
5. Issue = dúvida, não entrega.

## Verificação

Checklist humana (não há CI de app neste git):

- [ ] README raiz ainda aponta os quatro challenges e o FAQ de baseline.
- [ ] `CONTRIBUTING.md` ainda proíbe editar fora da pasta do candidato.
- [ ] `submission-guide.md` ainda trata process log como obrigatório.
- [ ] Template ainda tem bloco **Process Log — Como usei IA**.
- [ ] `.gitignore` ainda ignora `datasets/`, `submissions/`, `_internal/`.

## Evidência

2026-09-21: `README.md`, `CONTRIBUTING.md`, `submission-guide.md`, `templates/submission-template.md`, `.gitignore` batem com este contrato.

## Notas

Scoring privado (`_internal/`) não é contrato público. Não documentar rubrica numérica aqui.

## Sucesso / falha

- Sucesso: candidato entrega um challenge com solução + process log no path certo; banca consegue julgar processo e resultado.
- Falha: PR sem process log, PR que edita brief, ou entrega só de texto genérico igual ao baseline.

## Migração e compatibilidade

Títulos de PR e nomes de pasta (`submissions/`, `process-log/`) são estáveis. Novo challenge = SPEC nova + pasta nova — não reutilizar 001–004.
