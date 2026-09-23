# Rubrica da resposta executiva

## Regra de avaliação

A nota mede a capacidade da entrega de responder à pergunta do CEO com precisão, cobertura e utilidade. Ela não mede certeza causal. Cada rodada é pontuada sem arredondamento; a meta é `>= 9,5/10` e nenhum hard cap acionado.

| Dimensão | Peso | Nota máxima exige |
|---|---:|---|
| Resposta direta | 2,0 | Diagnóstico, limite causal e decisão no primeiro bloco. |
| Precisão quantitativa | 2,0 | Churn, denominadores, períodos, MRR, cobertura e incerteza corretos. |
| Reconciliação CS × Produto | 2,0 | Agregado e coorte comparados; respondentes não generalizados para a base. |
| Calibração causal | 1,5 | Hipótese inconclusiva nunca chamada de causa, driver ou mecanismo mais forte. |
| Utilidade decisória | 1,5 | Ações com responsável, prazo, população, métrica e regras de avançar/parar. |
| Consistência e auditoria | 1,0 | JSON, relatório e dashboard usam os mesmos claims, valores e `analysis_id`. |

## Hard caps

- Causalidade indevida: nota máxima `8,0`.
- População, período ou denominador incorreto: nota máxima `8,0`.
- Números divergentes entre superfícies: nota máxima `8,0`.

## Âncoras

### 7,0 — linha de base

Confirma a alta do churn e explica a contradição por coortes, mas chama uma hipótese inconclusiva de “mecanismo mais forte”, destaca um segmento com RR 1,08× como se fosse concentração, não leva o impacto econômico ao resumo e oferece uma única ação genérica.

### 9,5 — mínimo de aprovação

Responde em até 45 segundos: quantifica mudança e impacto; explica Produto × CS por população; declara que a causa ainda não foi demonstrada; evita falsa concentração; apresenta três validações executáveis; e mantém rastreabilidade idêntica nas três superfícies.

## Medições por incremento

| Rodada | Direta /2 | Precisão /2 | CS×Produto /2 | Causal /1,5 | Decisão /1,5 | Auditoria /1 | Total | Hard cap | Evidência |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| Linha de base | 1,4 | 1,2 | 1,8 | 1,0 | 0,8 | 0,8 | **7,0** | Não | Avaliação anterior ao novo plano. |
| Task 1 — contrato | 1,4 | 1,2 | 1,8 | 1,0 | 0,8 | 0,8 | **7,0** | Não | Rubrica e regressão fixam o critério; output ainda não mudou. |
| Task 2 — veredito completo | 1,8 | 1,9 | 1,8 | 1,5 | 0,7 | 0,9 | **8,6** | Não | MRR observado e ausência de concentração material entram no contrato. |
| Task 3 — abstenção e ações | 1,9 | 1,9 | 1,9 | 1,5 | 1,4 | 0,9 | **9,5** | Não | Três validações substituem a falsa causa e a ação genérica. |
| Task 4 — leitura executiva | 2,0 | 1,9 | 2,0 | 1,5 | 1,5 | 0,9 | **9,8** | Não | Confiança traduzida e leitura de 45 segundos; artefatos reais ainda pendentes. |
| Task 5 — entrega validada | 2,0 | 1,9 | 2,0 | 1,5 | 1,5 | 1,0 | **9,9** | Não | Artefatos reais consistentes, gate integral verde e dashboard conferido em desktop e 390×844. |

## Evidência da nota final

- **Resposta direta — 2,0:** a abertura começa por “Resposta curta”, quantifica a alta, declara que nenhum mecanismo passou os gates e termina com a decisão.
- **Precisão — 1,9:** publica 12,4%, +7,0 pp e US$ 1.622.337 com períodos, população, denominador e limitações rastreáveis. O desconto de 0,1 preserva a distinção entre qualidade da resposta e certeza causal.
- **CS × Produto — 2,0:** confronta uso agregado com futuros churners e limita satisfação aos respondentes, com coberturas de 63,3% e 65,9%.
- **Causalidade e decisão — 3,0:** afirma “Causa ainda não demonstrada” e entrega três validações com owner, prazo, população, métrica e regras de avançar/parar.
- **Auditoria — 1,0:** `analysis_id=886cfb2b…`; JSON, relatório e dashboard compartilham o mesmo conteúdo; nenhum hard cap foi acionado.

**Nota final interna: 9,9/10.** Ela avalia a qualidade da resposta entregue, não garante avaliação externa nem causalidade de 95%.
