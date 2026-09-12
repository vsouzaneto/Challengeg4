# Decision log

## 2026-09-12 — Preparação e contrato analítico

### Objetivo

Estruturar uma submissão reproduzível para o Challenge 001, com Streamlit e DuckDB, sem enviar alterações ao GitHub antes de autorização explícita.

### Ferramentas de IA e automação

- **Codex:** inspeção do repositório, auditoria inicial dos CSVs, desenho do processo analítico e implementação assistida.
- **Subagentes Codex:** revisões independentes e somente leitura das regras da submissão, da arquitetura enxuta e dos limites estatísticos.
- **RTK:** redução do volume das saídas de terminal durante a investigação.

### Trabalho realizado

1. O repositório foi clonado localmente com o remoto denominado `upstream` para reduzir risco de push acidental.
2. As regras do challenge, do processo de submissão e do template foram lidas antes de criar código.
3. Foi identificado que `submissions/` está ignorado pelo próprio `.gitignore`, embora seja o local obrigatório da entrega.
4. Foi realizada uma auditoria exploratória dos cinco CSVs públicos.
5. Foram encontradas divergências entre as fontes de churn, assinaturas simultâneas e eventos fora das janelas temporais possíveis.
6. A política de verdade analítica foi discutida e aprovada antes da implementação.

### Onde a IA poderia ter errado

A resposta inicial poderia ter aceitado os flags de churn, somado todas as assinaturas e produzido indicadores visualmente convincentes. A inspeção dos arquivos mostrou que essa abordagem confundiria três fenômenos diferentes e criaria receita não reconciliada.

### Julgamento humano incorporado

O autor aprovou separar snapshot, eventos e assinaturas; preservar sujeira em quarentena; não inventar substituições; rotular proxies; e não chamar um score heurístico de probabilidade.

### Decisão

Adotar o contrato descrito em `docs/adr/0001-politica-de-verdade-analitica.md` antes de construir o pipeline e o dashboard.

## 2026-09-12 — Distribuição dos dados e artefato final

### Problema

Os dados precisam alimentar a aplicação e permanecer reproduzíveis, mas os CSVs públicos e o banco derivado não devem ser versionados como se fossem código da submissão.

### Recomendação da IA

Versionar apenas o downloader, o manifesto e os hashes, reconstruindo o DuckDB a partir da fonte pública.

### Complemento do autor

A política só é aceitável se os dados necessários ao Streamlit estiverem disponíveis e se houver um artefato final com a análise concluída.

### Decisão

Foi aprovada a política descrita em `docs/adr/0002-distribuicao-e-reprodutibilidade-dos-dados.md`: bootstrap automatizado, validação de integridade, rebuild determinístico e artefato estático final avaliável sem executar o app.
