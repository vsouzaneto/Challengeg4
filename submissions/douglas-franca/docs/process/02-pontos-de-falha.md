# 02 · Pontos de falha

> **Em 3 linhas:** são 8 falhas: 3 exclusivas do conteúdo orgânico, 3 exclusivas de parcerias e 2 comuns. Cada uma aponta a prova no arquivo (DQ/INF) ou a fonte na operação. O custo de não corrigir é sempre o mesmo: **decidir verba com base em ruído**.

Rótulos de origem: **[dado]** comprovado no arquivo · **[operação]** relatado pelo Douglas · **[hipótese]** a validar com o time.

| FP | Fluxo | Etapa | Falha | Origem e prova | Impacto na decisão | Correção (TO-BE) |
|---|---|---|---|---|---|---|
| **FP-01** | B · Parcerias | Contrato | Custo registrado em e-mail e CRM **sem chave** que o ligue aos posts | [operação] contrato no CRM · [dado] DQ-12: nenhuma coluna de custo | Retorno de patrocínio incalculável | `campaign_id` do CRM obrigatório em todo post patrocinado |
| **FP-02** | B · Parcerias | Resultado | Venda não atribuída ao contrato | [dado] DQ-12: sem cliques, conversão, receita · [operação] resultado chega por relatório e dashboard | Patrocínio avaliado por engajamento, que é igual ao orgânico (INF: −0,003 p.p.) | Cupom e UTM únicos por contrato; venda e margem por `campaign_id` |
| **FP-03** | B · Parcerias | Prospecção | Sem cadastro mestre de creator | [dado] DQ-07: 100% dos creators com mais de 1 nome; seguidores mudam a cada post | Recontratação sem histórico; tamanho de creator não confiável | Cadastro mestre com ID, handles, seguidores datados e auditoria de audiência |
| **FP-04** | Comum | Coleta | Extração incompleta, origem não documentada, sem validação | [dado] DQ-04, 05, 06, 15: zero fracassos, colunas sem coerência · [operação] "de onde vocês retiraram estes dados?" | Estratégia construída sobre um arquivo que não representa a operação | Health check automático na entrada; origem e data de extração em cada linha |
| **FP-05** | A · Conteúdo | Briefing e produção | Formato, duração e mensagem sem padrão | [dado] DQ-10: `content_length` sem unidade · DQ-11: texto sem semântica | Impossível aprender qual formato ou duração funciona | Briefing padronizado: formato, `duration_seconds`, tema, gancho, CTA |
| **FP-06** | A · Conteúdo | Pauta e publicação | Cadência e horário não planejados nem registrados com fuso | [dado] DQ-09: todo creator com 10–11 posts · DQ-14: publicação uniforme 24h | "Com que frequência postar?" fica sem resposta | Calendário com cadência planejada × realizada; `published_at` com fuso |
| **FP-07** | A · Conteúdo | Audiência | Audiência guardada como rótulo único por post | [dado] DQ-13, DQ-15: idioma sem relação com país | Persona inferida sem base | Distribuição de audiência (%) por post e por creator, com data |
| **FP-08** | Comum | Decisão | Decisão por ranking de médias, sem hipótese prévia, régua ou comparação | [dado] G3: "vencedores" como moda e #religious somem com correção · [hipótese] dashboard sem n e sem margem de erro | Sempre aparece um "vencedor", mesmo quando é ruído | Pré-registro, régua ±1 p.p., grupo de comparação, leitura a cada 15 dias e decisão a cada 30 |
