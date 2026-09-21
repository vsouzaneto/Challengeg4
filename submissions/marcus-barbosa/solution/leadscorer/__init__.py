"""Lead Scorer — priorização explicável de oportunidades do pipeline de vendas.

Módulos:
    data     carga dos CSVs, validação de schema, normalização e junção das 4 tabelas
    audit    relatório de saúde dos dados (contagens, nulos, inconsistências)
    scoring  fatores, agregação, categorias de ação e explicações (funções puras)
    backtest validação do score contra o histórico Won/Lost, inclusive por snapshot
"""
