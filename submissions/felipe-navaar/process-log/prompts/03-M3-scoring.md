# M3 — motor de regras

Leia AGENTS.md, docs/PRD.md e os documentos relacionados antes de agir.

Verifique se existe política explicitamente aprovada em docs/DECISOES.md. Se não houver, apresente a proposta com fórmulas, pesos, exemplos e limitações e PARE para aprovação. Não deduza aprovação a partir deste prompt.
Com aprovação, implemente src/scoring.py e config/scoring_policy.json. Separe UI de lógica. Garanta score 0–100, explicações reconciliáveis, warnings, versão, corte temporal e desempate determinístico. Pontue somente abertos; preserve dados ausentes. Teste cenários controlados, fronteiras, estabilidade e ausência de leakage. Registre comandos/resultados e pare antes do M4.

Ao encerrar: resuma alterações, verificações realizadas, saídas observadas, limitações e próximo módulo. Não avance automaticamente.
