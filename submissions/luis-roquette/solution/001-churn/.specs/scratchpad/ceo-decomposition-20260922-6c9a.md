# Fase 4 — decomposição da arquitetura A

Task: `.specs/tasks/draft/implement-ceo-answer-architecture.feature.md`. Data: 2026-09-22. Planejamento apenas; não executar código, gates ou publicação.

Fontes lidas: task completa, análise de impacto, skill `answer-first-churn`, `Makefile` e símbolos/callers de panel, quality, diagnosis, cli e publish. A arquitetura atual prevalece sobre contratos preliminares da análise de impacto, especialmente seleção terminal válida, confiança operacional e campos dos artefatos.

Decisão: sete steps, duas fases. Unificar migração da seleção terminal e callers no 01; separar histórico em diagnosis (02) e painel relativo em panel (03), paralelos após 01; unir métricas relativas, gates, scorecard e integração analítica no 04, que fecha a primeira fase executável. O 05 concentra contrato de publicação, CLI, fixtures, validação e relatório; 06 apresenta no app e 07 documenta/fecha o gate, em paralelo após 05.

Não paralelizar 02 e 04: ambos alteram diagnosis e seus testes. Não dividir dataclass, serialização e validação: contratos incompletos gerariam handoffs e estados inválidos. Não criar módulos/dependências nem um step só para configuração ou Makefile. A publicação da fase 1 conserva o conjunto de artefatos vigente, regenerado com a política corrigida; a fase 2 migra de uma vez para 14 payloads mais manifesto.

Modelos: 01 opus (contrato compartilhado, integridade); 02 opus (denominadores/receita, bootstrap); 03 opus (seleção temporal, labels e ausência de vazamento); 04 opus (confiança operacional, integridade e integração); 05 opus (contrato compartilhado, manifesto); 06 sonnet (renderização local de contrato pronto); 07 sonnet (README/Makefile e teste direcionado, sem semântica analítica). Ambos os reviewers são opus, teto disponível.

Dependências diretas: 01→02,03; 02,03→04; 04→05; 05→06,07. Caminhos críticos estruturais de cinco steps: 01→02→04→05→06 e alternativas trocando 02 por 03 e/ou 06 por 07. Sem estimativas de duração inventadas. Largura máxima 2. Sete steps, 35 subtasks; dois blocos paralelos. Três handoffs evitados ao unir seleção/callers, contrato/publicação e documentação/gate.

Cobertura: fase 1 verifica CK-2–CK-8 nos cálculos e CK-11/HR-1–HR-3 na execução analítica, sem alegar entrega executiva concluída. Fase 2 fecha todos CK/HR e as cinco rubricas nas superfícies persistidas/renderizadas. Riscos altos predominantes: migração de labels, denominadores repetidos, MRR ausente, vazamento/ponderação, gates posteriores à fila, referências inconsistentes. Cada step contém mitigação própria.

Limite de autorização: revisão humana da SPEC precede implementação. Os modelos são metadados do plano, não configuração de provider nem autorização de API paga. Gates futuros respeitam o ambiente autorizado, commit/diff exato e `codespace-manager`. Nenhuma edição de CSV bruto, deploy ou contato.
