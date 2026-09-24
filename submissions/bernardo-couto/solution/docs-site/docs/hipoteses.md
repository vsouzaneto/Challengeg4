# Hipóteses registradas antes da análise

Onze hipóteses foram escritas em `solution/pipeline/analysis/00_hypotheses.md` **antes** de rodar qualquer script de análise, cada uma com o que aconteceria se fosse refutada. Os vereditos foram acrescentados depois, sem alterar o texto original. O arquivo completo, com números e intervalos de confiança, fica junto ao código do pipeline; esta página resume os vereditos.

| # | Hipótese | Veredito | Consequência no produto |
|---|---|---|---|
| H1 | Sobrevivência em Engaging é sinal positivo até ~90 dias e depois vira zumbi | Confirmada parcialmente: a curva sobe e não cai, mas em corte temporal fixo a idade não discrimina (AUC-ROC 0,50) | `SURVIVAL_POSITIVE` informativo; `ZOMBIE_RISK` (> 138 d) regra dura |
| H2 | Poder discriminativo: agente > produto > setor, todos modestos | Confirmada na ordem, refutada na utilidade (AUC-ROC fora do tempo 0,475–0,504) | `AGENT_*` e `SECTOR_FIT` informativos, peso zero |
| H3 | Conta ausente é preenchimento tardio, não sinal de qualidade | Refutada: fração com conta plana em toda faixa de idade; 100% dos fechados têm conta vs 32% dos abertos | `account_*` proibido como feature; entra só em `confidence` e `reasons` |
| H4 | Sazonalidade por mês de engajamento; fim de trimestre no fechamento | Refutada como formulada; o efeito é de calendário de registro (Lost), não de engajamento | Nenhuma feature de sazonalidade; `QUARTER_END_WINDOW` vetado |
| H5 | Mais deals abertos ao mesmo tempo → menor win rate | Refutada (sinais opostos nos dois cortes, ICs contêm zero) | `AGENT_OVERLOAD` informativo, para o manager |
| H6 | Produtos mais caros fecham menos | Confirmada na direção, irrelevante na magnitude (60–65%) | Invariante Spearman(score, preço) < 0,9 |
| H7 | Histórico da conta prevê o futuro da conta | Refutada (AUC-ROC 0,475 / 0,489) | `ACCOUNT_HISTORY` informativo |
| H8 | `close_value / sales_price` dos Won é estável | Confirmada (mediana 0,967–1,004) | Valor esperado = preço × razão × taxa do produto |
| H9 | "Mais novo primeiro" é baseline forte a bater | Refutada — e a premissa também: nenhum critério bate o aleatório entre deals vivos | Posicionamento "valor × timing + higiene"; `p_win` = taxa-base por produto |
| H10 | Tamanho da conta tem efeito positivo pequeno | Refutada (Spearman ≈ 0) | `ACCOUNT_SIZE` informativo |
| H11 | A maioria do pipeline Engaging já passou do ciclo máximo | Confirmada com folga: 1.291 de 1.589 (81,2%) > 138 dias | Fila "Confirmar ou encerrar"; sprint de limpeza |

Sete refutadas (H3, H4, H5, H7, H9, H10 e a utilidade de H2); detalhes e evidência por hipótese em `docs/figures/01_eda.md`, `10_backtest.md`, `11_diagnostics.md` e `20_model_candidates.md`.
