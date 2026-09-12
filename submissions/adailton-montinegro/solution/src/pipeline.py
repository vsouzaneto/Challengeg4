#!/usr/bin/env python3
"""
pipeline.py - Orquestrador Determinístico de Engenharia de Dados RavenStack
Executa ingestão e transformações completas no DuckDB (Bronze -> Silver -> Gold).
"""

import os
import sys
import duckdb

DB_PATH = "submissions/adailton-montinegro/solution/data/ravenstack.duckdb"
SQL_DIR = "submissions/adailton-montinegro/solution/sql"

def run_script(con: duckdb.DuckDBPyConnection, rel_path: str, stage_name: str):
    full_path = os.path.join(SQL_DIR, rel_path)
    if not os.path.exists(full_path):
        print(f"[ERRO] Arquivo SQL não encontrado: {full_path}")
        sys.exit(1)
    
    print(f"[*] Executando etapa: {stage_name} ({rel_path})...")
    with open(full_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
    con.execute(sql_content)
    print(f"[✓] {stage_name} concluído com sucesso.")

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = duckdb.connect(DB_PATH)
    
    print("==========================================================")
    print("   RAVENSTACK ANALYTICS PIPELINE (DUCKDB ENGINE)")
    print("==========================================================")
    
    # 1. Camada Bronze
    run_script(con, "01_bronze/ingest.sql", "Camada Bronze (Ingestão)")
    
    # 2. Camada Silver
    run_script(con, "02_silver/clean_and_quarantine.sql", "Camada Silver (Higienização & Quarentena)")
    
    # 3. Camada Gold
    run_script(con, "03_gold/dimensions.sql", "Camada Gold (Dimensões)")
    run_script(con, "03_gold/facts.sql", "Camada Gold (Fatos)")
    run_script(con, "03_gold/mrr_bridge.sql", "Camada Gold (MRR Bridge)")
    run_script(con, "03_gold/retention_cohorts.sql", "Camada Gold (Coortes de Retenção)")
    run_script(con, "03_gold/health_score.sql", "Camada Gold (Health Score & Risco)")
    
    # Validações Rápidas de Qualidade e Métricas
    print("\n--- RESUMO DA QUARENTENA DE INCONSISTÊNCIAS ---")
    quarantine_summary = con.execute("""
        SELECT anomaly_type, count(*), sum(impact_mrr)
        FROM silver.quarentena_inconsistencias
        GROUP BY anomaly_type
        ORDER BY count(*) DESC
    """).fetchall()
    for row in quarantine_summary:
        print(f"  Tipo: {row[0]:<35} | Registros: {row[1]:<5} | Impacto MRR: ${float(row[2] or 0):,.2f}")
        
    print("\n--- RESUMO DO FECHAMENTO DE MRR (JANEIRO 2026) ---")
    latest_bridge = con.execute("""
        SELECT year_month, beginning_mrr, new_mrr, reactivation_mrr, expansion_mrr, contraction_mrr, churned_mrr, ending_mrr, active_accounts
        FROM gold.agg_mrr_bridge
        ORDER BY month_date DESC
        LIMIT 1
    """).fetchone()
    if latest_bridge:
        print(f"  Mês de Referência:  {latest_bridge[0]}")
        print(f"  Beginning MRR:      ${latest_bridge[1]:,.2f}")
        print(f"  New MRR:            ${latest_bridge[2]:,.2f}")
        print(f"  Reactivation MRR:   ${latest_bridge[3]:,.2f}")
        print(f"  Expansion MRR:      ${latest_bridge[4]:,.2f}")
        print(f"  Contraction MRR:    ${latest_bridge[5]:,.2f}")
        print(f"  Churned MRR:        ${latest_bridge[6]:,.2f}")
        print(f"  Ending MRR:         ${latest_bridge[7]:,.2f}")
        print(f"  Contas Ativas:      {latest_bridge[8]}")
        
    con.close()
    print(f"\n[✓] Pipeline integral executado com sucesso. Banco salvo em: {DB_PATH}")

if __name__ == "__main__":
    main()
