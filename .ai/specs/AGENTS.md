# Specs — regras

- Nome: `SPEC-NNN-*.md`.
- Frontmatter: `status`, `canonical`, `area`, `created`, `last_updated`.
- Corpo mínimo: comportamento visível **ou** contrato; verificação; evidência; notas.
- Uma spec `in_progress` por vez.
- Não inventar Project Linear, slug B4A, GCP ou runtime.
- Brief canônico = `challenges/<id>/README.md`. Spec descreve o contrato; não contradiz o README.
- Atualizar a tabela de [`README.md`](README.md) quando criar ou mudar status.
- Dataset novo ou coluna nova = `architecture/DATA-SOURCES.md` + ERD do serviço na mesma mudança.
- Gate de desclassificação (process log, path do PR) só muda com confirmação humana do G4.
