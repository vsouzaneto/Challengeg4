import duckdb, pandas as pd, numpy as np, sys
from scipy.stats import chi2_contingency, chi2
import os, pathlib
D = os.environ.get("CRM_DATA_DIR", str(pathlib.Path(__file__).resolve().parent.parent / "data"))
con = duckdb.connect()
con.execute(f"""
CREATE VIEW teams AS SELECT * FROM read_csv_auto('{D}/sales_teams.csv');
CREATE VIEW products AS SELECT * FROM read_csv_auto('{D}/products.csv');
CREATE VIEW accounts AS SELECT * FROM read_csv_auto('{D}/accounts.csv');
CREATE VIEW raw AS SELECT * FROM read_csv_auto('{D}/sales_pipeline.csv', types={{'engage_date':'DATE','close_date':'DATE'}});
CREATE VIEW p AS
  SELECT r.*, CASE WHEN r.product='GTXPro' THEN 'GTX Pro' ELSE r.product END AS prod,
         t.manager, t.regional_office AS region, a.sector, pr.sales_price AS price,
         date_diff('day', engage_date, close_date) AS cycle,
         date_diff('day', engage_date, DATE '2017-12-31') AS age_end
  FROM raw r JOIN teams t USING (sales_agent)
  LEFT JOIN accounts a USING (account)
  LEFT JOIN products pr ON pr.product = CASE WHEN r.product='GTXPro' THEN 'GTX Pro' ELSE r.product END;
""")
out = []
def q(title, sql, note=""):
    df = con.execute(sql).df()
    out.append(f"### {title}\n```sql\n{sql.strip()}\n```\n{df.to_markdown(index=False)}\n{note}\n")
    return df
def chi_from(df, gcol, wcol="won", ncol="n"):
    t = np.c_[df[wcol], df[ncol]-df[wcol]]
    s, p, dof, _ = chi2_contingency(t, correction=False); return s, dof, p

q("Q01 Contagem por estágio", "SELECT deal_stage, count(*) n FROM raw GROUP BY 1 ORDER BY 2 DESC")
q("Q02 Abertos sem conta", "SELECT count(*) FILTER (WHERE account IS NULL) sem_conta, count(*) abertos, round(100.0*count(*) FILTER (WHERE account IS NULL)/count(*),1) pct FROM raw WHERE deal_stage IN ('Prospecting','Engaging')")
q("Q03 Produtos fora do catálogo", "SELECT product, count(*) n FROM raw WHERE product NOT IN (SELECT product FROM products) GROUP BY 1")
q("Q04 Vendedores sem deals", "SELECT sales_agent FROM teams WHERE sales_agent NOT IN (SELECT DISTINCT sales_agent FROM raw)")
q("Q05 Datas, IDs e consistência", """SELECT min(engage_date) eng_min, max(engage_date) eng_max, min(close_date) close_min, max(close_date) close_max,
 count(*) FILTER (WHERE close_date < engage_date) fecha_antes, count(*) - count(DISTINCT opportunity_id) ids_dup,
 count(*) FILTER (WHERE deal_stage='Prospecting' AND engage_date IS NOT NULL) prosp_com_data,
 count(*) FILTER (WHERE deal_stage IN ('Won','Lost') AND close_date IS NULL) fechado_sem_data,
 count(*) FILTER (WHERE deal_stage='Lost' AND close_value<>0) lost_valor_nao_zero FROM raw""")
w = q("Q06 Taxa de vitória entre fechados (com IC de Wilson)", """WITH c AS (SELECT count(*) n, count(*) FILTER (WHERE deal_stage='Won') w FROM raw WHERE deal_stage IN ('Won','Lost'))
SELECT n, w, round(w/n,4) taxa,
 round(((w/n + 1.96^2/(2*n)) - 1.96*sqrt((w/n)*(1-w/n)/n + 1.96^2/(4*n*n)))/(1+1.96^2/n),4) ic_inf,
 round(((w/n + 1.96^2/(2*n)) + 1.96*sqrt((w/n)*(1-w/n)/n + 1.96^2/(4*n*n)))/(1+1.96^2/n),4) ic_sup FROM c""")
rows = []
for col in ["sales_agent", "manager", "region", "prod", "sector", "account"]:
    df = con.execute(f"SELECT {col} g, count(*) n, count(*) FILTER (WHERE deal_stage='Won') won FROM p WHERE deal_stage IN ('Won','Lost') AND {col} IS NOT NULL GROUP BY 1").df()
    s, dof, pv = chi_from(df, "g"); r = df.won/df.n
    rows.append(dict(dimensao=col, grupos=len(df), taxa_min=round(r.min(),3), taxa_max=round(r.max(),3), chi2=round(s,2), gl=dof, p=round(pv,4)))
out.append("### Q07 Taxa de vitória por dimensão (qui-quadrado, só fechados)\n" + pd.DataFrame(rows).to_markdown(index=False) + "\n")
q("Q08 Percentis do ciclo (só fechados)", """SELECT deal_stage, count(*) n, quantile_cont(cycle,0.25) p25, quantile_cont(cycle,0.5) p50, quantile_cont(cycle,0.75) p75, quantile_cont(cycle,0.9) p90, max(cycle) mx
FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY ROLLUP(deal_stage) ORDER BY 1""")
q("Q09 Três formas de medir 'chance pela idade' (X dias)", """WITH x AS (SELECT unnest([0,14,30,60,90,104,120,130,138]) X),
e AS (SELECT *, coalesce(cycle, age_end) t, engage_date <= DATE '2017-08-15' coorte FROM p WHERE deal_stage <> 'Prospecting')
SELECT X,
 round(avg(CASE WHEN deal_stage='Won' THEN 1.0 ELSE 0 END) FILTER (WHERE deal_stage IN ('Won','Lost') AND t > X),3) so_fechados_ERRADO,
 count(*) FILTER (WHERE t > X) em_risco_todos,
 round(avg(CASE WHEN deal_stage='Won' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X),3) ganho_entre_todos,
 count(*) FILTER (WHERE t > X AND coorte) em_risco_coorte,
 round(avg(CASE WHEN deal_stage='Won' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X AND coorte),3) ganho_coorte,
 round(avg(CASE WHEN deal_stage='Lost' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X AND coorte),3) perda_coorte,
 round(avg(CASE WHEN deal_stage='Engaging' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X AND coorte),3) nunca_fechou_coorte
FROM x, e GROUP BY X ORDER BY X""", "coorte = início até 15/08/2017 (todos tiveram ≥138 dias para fechar até 31/12/2017).")
q("Q10 Idade dos Engaging abertos em 31/12/2017", """SELECT count(*) engaging, count(*) FILTER (WHERE age_end <= 104) ate_104, count(*) FILTER (WHERE age_end BETWEEN 105 AND 138) d105_138,
 count(*) FILTER (WHERE age_end > 138) acima_138, round(100.0*count(*) FILTER (WHERE age_end > 138)/count(*),1) pct_acima_138, min(age_end) idade_min, max(age_end) idade_max FROM p WHERE deal_stage='Engaging'""")
q("Q11 Desfecho da coorte com janela completa", """SELECT count(*) n, round(avg((deal_stage='Won')::INT),3) ganhou, round(avg((deal_stage='Lost')::INT),3) perdeu, round(avg((deal_stage='Engaging')::INT),3) nunca_fechou
FROM p WHERE deal_stage <> 'Prospecting' AND engage_date <= DATE '2017-08-15'""")
for col in ["sales_agent", "manager", "region", "prod"]:
    df = con.execute(f"SELECT {col} g, count(*) n, count(*) FILTER (WHERE deal_stage='Engaging') won FROM p WHERE deal_stage<>'Prospecting' AND engage_date <= DATE '2017-08-15' GROUP BY 1").df()
    s, dof, pv = chi_from(df, "g"); r = df.won/df.n
    out.append(f"### Q12 '% nunca fechou' por {col} (coorte)\ngrupos={len(df)}, min={r.min():.3f}, max={r.max():.3f}, chi2={s:.1f}, gl={dof}, p={pv:.2e}\n")
q("Q12b '% nunca fechou' por vendedor (coorte), extremos", """SELECT sales_agent, manager, count(*) n, round(avg((deal_stage='Engaging')::INT),3) nunca_fechou, round(avg((deal_stage='Won')::INT),3) ganhou
FROM p WHERE deal_stage<>'Prospecting' AND engage_date <= DATE '2017-08-15' GROUP BY 1,2 ORDER BY nunca_fechou LIMIT 6""")
q("Q13 Prospecting por gerente", "SELECT manager, region, count(*) n FROM p WHERE deal_stage='Prospecting' GROUP BY 1,2 ORDER BY 3 DESC")
q("Q14 Valor fechado (ganhos) x preço de tabela", """SELECT prod, any_value(price) preco, count(*) ganhos, median(close_value) mediana, round(100*(median(close_value)-any_value(price))/any_value(price),2) dif_pct,
 min(close_value) minimo, max(close_value) maximo FROM p WHERE deal_stage='Won' GROUP BY 1 ORDER BY preco DESC""")
q("Q15 Maior ciclo por mês de início (fechados)", "SELECT strftime(engage_date,'%Y-%m') mes, count(*) fechados, max(cycle) maior_ciclo FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY 1 ORDER BY 1")
q("Q16 Taxa de vitória por mês de FECHAMENTO", """SELECT strftime(close_date,'%Y-%m') mes, count(*) fechados, count(*) FILTER (WHERE deal_stage='Won') ganhos, round(avg((deal_stage='Won')::INT),3) taxa
FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY 1 ORDER BY 1""")
q("Q17 Fim de trimestre x demais meses", """SELECT month(close_date) IN (3,6,9,12) fim_trimestre, count(*) fechados, round(avg((deal_stage='Won')::INT),3) taxa,
 round(avg(cycle),1) ciclo_medio FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY 1""")
q("Q18 Perdas nas 2 primeiras semanas", """SELECT count(*) FILTER (WHERE deal_stage='Lost' AND cycle<=14) perdas_ate14, count(*) FILTER (WHERE deal_stage='Lost') perdas,
 count(*) FILTER (WHERE cycle<=14) fechados_ate14, round(avg((deal_stage='Lost')::INT) FILTER (WHERE cycle<=14),3) pct_perdidos_entre_ate14 FROM p WHERE deal_stage IN ('Won','Lost')""")
q("Q19 Deals abertos por vendedor", """WITH a AS (SELECT sales_agent, count(*) n FROM raw WHERE deal_stage IN ('Prospecting','Engaging') GROUP BY 1)
SELECT count(*) vendedores_com_abertos, round(avg(n),1) media, median(n) mediana, min(n) minimo, max(n) maximo FROM a""")
q("Q20 Vendedores sem nenhum Engaging com até 138 dias", """WITH a AS (SELECT sales_agent, count(*) FILTER (WHERE deal_stage='Engaging' AND age_end<=138) vivos, count(*) abertos FROM p WHERE deal_stage IN ('Prospecting','Engaging') GROUP BY 1)
SELECT count(*) vendedores, count(*) FILTER (WHERE vivos=0) sem_deal_vivo, list(sales_agent ORDER BY sales_agent) FILTER (WHERE vivos=0) quem FROM a""")
q("Q21 Abertos por mês de início (Engaging)", "SELECT strftime(engage_date,'%Y-%m') mes, count(*) engaging_abertos FROM p WHERE deal_stage='Engaging' GROUP BY 1 ORDER BY 1")
open(pathlib.Path(__file__).resolve().parent / "saidas" / "auditoria_sql.md", "w").write("# Auditoria SQL — Desafio 003 (DuckDB sobre os CSVs originais)\n\n" + "\n".join(out))
print("\n".join(out))
