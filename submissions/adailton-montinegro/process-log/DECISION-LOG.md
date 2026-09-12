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

## 2026-09-12 — Superfícies da entrega

### Decisão avaliada

Escolher entre uma aplicação interativa, um relatório estático ou uma entrega combinada.

### Recomendação da IA

Entregar Streamlit e PDF, evitando que a avaliação dependa da execução do app e preservando a exploração detalhada.

### Decisão do autor

Formato duplo aprovado. O Streamlit será a superfície explorável; o PDF será o artefato canônico. O Markdown versionado será a fonte editável, e os dois formatos deverão consumir as mesmas métricas gold.

## 2026-09-12 — Gate profissional de parada

### Problema

A parcela recuperável permite uma análise demonstrativa, mas continuar a análise após encontrar falhas sistêmicas poderia sugerir que essa é a conduta recomendada para uma empresa real.

### Complemento do autor

Entre a auditoria e a continuação analítica, a entrega deve avisar que a decisão correta seria parar, corrigir o sistema e somente depois retomar o diagnóstico. Se houver urgência, a investigação precisa buscar evidência independente em clientes e nos times de CS e Suporte.

### Decisão

Foi aprovado o gate descrito em `docs/adr/0004-gate-de-parada-e-analise-demonstrativa.md`. O Streamlit e o PDF deverão apresentar o callout antes de qualquer conclusão sobre churn. Pesquisa de satisfação, coleta de sugestões, entrevistas e revisão operacional serão recomendadas como rota de curto prazo.
