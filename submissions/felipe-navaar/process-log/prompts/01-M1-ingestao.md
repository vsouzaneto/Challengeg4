# M1 — ingestão e qualidade

Leia AGENTS.md, docs/PRD.md e os documentos relacionados antes de agir.

Implemente src/ingest.py e testes de integridade. Leia data/raw sem modificar os arquivos. Valide schema, tipos e chaves; preserve product_raw, normalize alias, faça left joins many-to-one. Reporte faltas, falhas de correspondência e contagens. Não descartar account ausente. Use caminhos portáveis.
Reconcilie com docs/EDA_BASELINE.json. Rode os testes, registre saídas reais no process log e pare antes do M2.

Ao encerrar: resuma alterações, verificações realizadas, saídas observadas, limitações e próximo módulo. Não avance automaticamente.
