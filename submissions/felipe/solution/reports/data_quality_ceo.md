# Qualidade de dados — CEO (1 página)

**Por que importa:** o board pode decidir com **cadastro** (`churn_flag`) ou com **eventos** — eles **não batem** sempre.

| Sinal | Valor | Leitura |
|-------|-------|---------|
| Contas com flag churn líquido | **110** | Definição cadastro |
| Dessas, **sem nenhum evento** de churn | **35** | Reconciliar com Financeiro/Dados |
| MRR contratual nessas contas (exposição) | **US$ 87,952** | Priorizar auditoria, não “receita recuperada” |
| Uso **antes** do início da assinatura | **19,142** / 25,000 linhas (76.6%) | Não usar série bruta para “engajamento subiu” |
| Assinaturas com múltiplas linhas de uso | **4816** | Validar grain de telemetria |

**Ação:** alinhar KPI (líquido + eventos + MRR) **e** corrigir cadastro — complementa o diagnóstico **revolving** (`executive_summary.md`).

Detalhe técnico: `outputs/data_quality_summary.csv`
