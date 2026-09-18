# Estratégia recomendada (G5)

## A tese em 3 frases
1. O arquivo de 52 mil posts **não serve para decidir**: as métricas se comportam como um sorteio com a mesma média para todos os posts (DQ-05), e as 332 comparações da taxa de engajamento ficaram dentro da faixa irrelevante de ±1 p.p. (G3), mesmo com correção para múltiplos testes (`inf-robustness.csv`).
2. Por isso a estratégia **não é trocar de canal, formato ou creator**, e sim **parar de decidir por ranking de médias** e montar a operação que gera dados capazes de decidir (G4).
3. Nos próximos 30 dias, a empresa **só assina contrato novo de patrocínio que já nasça medível** (custo, cupom/UTM e grupo de comparação), liga o custo do CRM ao post e à venda, e roda os primeiros testes com régua definida antes.

## Decisões priorizadas
Owners conforme `docs/process/05-raci.md`: HM Head de Marketing · SM Social Media Lead · GP Gestor de Parcerias · FIN Financeiro · AM AI Master.

| ID | Prioridade | Decisão | Evidência | KPI | Guardrail | Condição de parada | Owner |
|---|---|---|---|---|---|---|---|
| **STR-01** | P0 · semana 1 | **Regra de entrada para patrocínio:** nenhum contrato novo é assinado sem custo, cupom/UTM, `campaign_id` e grupo de comparação. Não é um veredito sobre patrocínio: é a condição para conseguir medi-lo | O arquivo não tem custo nem venda, então não há retorno a medir (DQ-12); patrocínio −0,003 p.p. (IC −0,014 a +0,008) | 100% dos contratos novos completos no Gate 1 | Contratos ativos e os já negociados seguem, sem renovação automática. **Exceção** (creator estratégico, campanha sazonal) só com aprovação do HM, registrada com o motivo | Regra revista no fechamento do dia 30 | HM |
| **STR-02** | P0 · semana 1 | **Auditar a origem dos dados** (quem extraiu, de qual sistema, com quais filtros) antes de qualquer nova análise | DQ-04, 05, 06, 15 | Origem documentada em 100% das extrações | Health check automático reprova o que falhar | — | HM (R: AM) |
| **STR-03** | P0 · semanas 1–2 | **Ligar o custo do CRM ao post e à venda**: inventário dos contratos sem custo, `campaign_id`, cupom e UTM por contrato | FP-01, FP-02; premissa da minha vivência (contrato em e-mail e CRM), **a validar na semana 1** | Contratos ativos com custo e cupom/UTM ≥ 95% | Nenhum dado de venda sem janela de atribuição | — | GP (C: FIN) |
| **STR-04** | P0 · dias 8–15 | **Ativar o contrato de dados** (post, contrato, creator) e o cadastro mestre de creators | FP-03 a FP-07; DQ-07, 10, 13, 14 | Completude ≥ 95% por campo | Quarentena automática abaixo do mínimo | — | AM (R: SM, GP) |
| **STR-05** | P1 · dias 16–30 | **Rodar EXP-01 (patrocínio) e EXP-02 (formato por canal)** com pré-registro e régua de ±1 p.p. | G3: o histórico não responde; só teste controlado responde | Decisão registrada no dia 30 | Leitura de 15 dias sem declarar vencedor | Dano de marca, estouro de custo ou queda além da régua | HM |
| **STR-06** | P1 · imediato | **Mudar o dashboard**: toda métrica com n e margem de erro, sem ranking de médias, com o selo DIFERENTE / EQUIVALENTE | G3: "moda é pior" e "#religious é melhor" somem com correção | 0 rankings sem n e margem de erro | — | — | AM |
| **STR-07** | P2 · dias 31–90 | **Política de verba só com efeito replicado** em 2 ciclos e retorno acima do break-even | Regra do ciclo (`03-to-be.md`) | Verba realocada apenas com decisão "Escalar" | Nenhuma realocação com base no arquivo atual | — | HM (C: FIN) |

## Respostas diretas às perguntas do Head

### Onde concentrar esforço?
| Dimensão | Recomendação | Por quê |
|---|---|---|
| **Plataforma** | **Manter Instagram, TikTok e YouTube com o esforço atual** durante o 1º ciclo. Não realocar verba entre eles. Bilibili e RedNote ficam fora do escopo por não alcançarem o público brasileiro | Os 3 canais são equivalentes neste arquivo (médias de 19,899% a 19,906%: amplitude de 0,007 p.p.). Mudar agora seria decidir por ruído |
| **Tipo de conteúdo** | Testar formato **dentro de cada canal** (EXP-02: vídeo × imagem/carrossel) com briefing padronizado | Formatos equivalentes (médias de 19,898% a 19,912%: amplitude de 0,014 p.p.); o arquivo não registra duração real (DQ-10) |
| **Frequência** | **Não mudar a cadência no 1º ciclo.** Medir a cadência real de cada canal no Gate 0 (posts por semana por conta) e testar aumento por rollout escalonado no 2º ciclo (EXP-03) | O arquivo tem 10–11 posts por creator em 2 anos, a mesma cadência para todos (DQ-09): não há variação para medir o efeito da frequência |
| **Faixa de creator** | **Não usar número de seguidores como critério de contratação.** Selecionar por auditoria de audiência, fit de categoria e custo por resultado. No EXP-01, estratificar entre < 100 mil e ≥ 100 mil seguidores | Efeito de 0 a 1 milhão de seguidores: −0,001 p.p. (IC −0,020 a +0,018) |

### Política de patrocínio
1. **Patrocinar ou não?** Novos contratos, só depois do Gate 1. Hoje não há evidência de ganho: nem em engajamento, nem em alcance.
2. **Em que condições?** O contrato precisa ter custo total, `campaign_id` do CRM, cupom e UTM únicos, hipótese, métrica primária, régua, break-even aprovado pelo Financeiro e grupo de comparação.
3. **Com que perfil de influenciador?** Com cadastro mestre, audiência auditada e fit de categoria. Não existe perfil vencedor no arquivo: 23 condições testadas (plataforma, faixa, formato, categoria, tipo de divulgação, categoria do patrocinador), todas equivalentes.
4. **Threshold de seguidores ou engajamento?** **Não existe threshold nos dados.** O threshold passa a ser **financeiro**: o contrato só vale se `fee ≤ vendas incrementais × margem − custo de produção` (`src/decision/rules.py::break_even_fee`).
5. **Custo implícito:** o efeito estimado do patrocínio é **negativo** (−0,003 p.p.). No **limite superior do IC 95%**, o cenário mais favorável que o arquivo admite, um post patrocinado geraria **0,77 interação** e **3 views** a mais que um orgânico. O valor desse ganho depende de quanto vale uma interação (parâmetro do negócio, não do arquivo):

| Valor de uma interação | Teto de valor por post | Teto por contrato de 10 posts |
|---:|---:|---:|
| R$ 0,10 | R$ 0,08 | R$ 0,77 |
| R$ 0,50 | R$ 0,39 | R$ 3,87 |
| R$ 1,00 | R$ 0,77 | R$ 7,74 |
| R$ 5,00 | R$ 3,87 | R$ 38,70 |

**Comparação com o preço de mercado** (faixas por post ou Reels no Brasil, pesquisa trazida por Douglas; fontes: jmonline.com.br, vocenohype.com.br, influee.co, stan.store · `str-market-fees.csv`):

| Perfil | Fee de mercado por post | Quanto cada interação extra precisaria valer para pagar o fee | Quantas vezes o teto a R$ 5 por interação (R$ 3,87) | Vendas extras para pagar o fee, com margem de R$ 20 · R$ 50 · R$ 100 por venda |
|---|---:|---:|---:|---|
| Micro (10–100 mil) | R$ 500 – R$ 3.000 | **R$ 646 – R$ 3.876** | 129x – 775x | 25–150 · 10–60 · 5–30 |
| Grande (> 500 mil) | R$ 15.000 – R$ 100.000 | **R$ 19.381 – R$ 129.206** | 3.876x – 25.841x | 750–5.000 · 300–2.000 · 150–1.000 |

**Leitura:** a conta não depende do valor escolhido para a interação. Para o engajamento extra pagar sozinho o fee **mínimo** de um micro, cada interação a mais precisaria valer **R$ 646**. Mesmo supondo R$ 5 por interação, ele cobre menos de 1% desse fee. **Se o patrocínio se paga, é por venda atribuída**, e é por isso que o cupom e a UTM (STR-03) vêm antes de qualquer contrato novo. Fonte: `outputs/tables/str-implied-cost.csv`.

### O que parar de fazer
| Parar | Evidência |
|---|---|
| Decidir pauta ou verba por **ranking de médias** | 332 comparações equivalentes; maior diferença nos fatores: 0,014 p.p. |
| **Contratar creator pelo número de seguidores** | −0,001 p.p. de 0 a 1 milhão |
| **Avaliar patrocínio por engajamento** | Equivalente ao orgânico; o teto de valor é centavos por post |
| **Ranquear creators por engajamento ÷ seguidores** | Artefato matemático (baseline Grok: "nano 51,7%") |
| **Otimizar hashtags** com base no histórico | Nenhum par com mais de 5 posts; individuais equivalentes |
| **Aceitar p < 0,05 sem correção** | "Moda é pior", "#religious é melhor" e 6 perfis de audiência somem com BH |
| **Usar modelo preditivo de engajamento** | R² = −0,001 em validação por creator |

### Quick wins desta semana
| # | Ação | Owner | Pronto quando |
|---|---|---|---|
| 1 | Reunião de origem dos dados (quem, de onde, como) | HM | Origem documentada |
| 2 | Comunicado da regra de entrada: contrato novo de patrocínio só com custo, cupom/UTM e grupo de comparação; exceções pelo HM | HM | Checklist do Gate 1 obrigatório no pipeline de parceria do CRM |
| 3 | Lista dos contratos ativos sem custo registrado | GP | Planilha com dono e prazo de regularização |
| 4 | Cupom e UTM únicos para cada contrato ativo | GP | 100% dos ativos com cupom e UTM |
| 5 | Selo "n e margem de erro" no dashboard; ranking de médias removido | AM | Dashboard revisado |

## Backlog de testes (1º e 2º ciclos)
Tamanho dos testes: o arquivo tem desvio de ~0,49 p.p. por post, irrealista. Para dados reais, a tabela abaixo mostra quantos posts por braço são necessários para detectar a régua de ±1 p.p. com 80% de poder (`str-test-sizing.csv`). O AI Master calcula o valor final com o desvio observado no Gate 0. **O teste fecha quando atinge o n por braço, não numa data:** se o volume do canal não chegar lá até o dia 30, o ciclo registra INCONCLUSIVO e o teste segue no ciclo seguinte, ou o HM aprova a régua de 2 p.p. (4x menos posts).

| Desvio real da taxa de engajamento por post | Posts por braço (régua 1 p.p.) | (régua 2 p.p.) |
|---:|---:|---:|
| 2 p.p. | 63 | 16 |
| 5 p.p. | 393 | 99 |
| 10 p.p. | 1.570 | 393 |

| Teste | Hipótese | Desenho | Métrica primária | Break-even | Decisão (A) · operação (R) · comparação | Ciclo |
|---|---|---|---|---|---|---|
| **EXP-01 · Patrocínio** | Patrocínio gera venda que paga o fee (ex.: um micro de R$ 3.000 com margem de R$ 50 precisa de 60 vendas extras) | Creators elegíveis sorteados entre patrocinado e não patrocinado, estratificados por faixa (< 100K / ≥ 100K) | Venda atribuída por cupom/UTM; taxa de engajamento como secundária | `fee ≤ vendas incrementais × margem − produção`, aprovado por FIN | HM · GP · AM | A partir do dia 16, até atingir o n |
| **EXP-02 · Formato por canal** | Um formato move a taxa de engajamento em ≥ 1 p.p. dentro do canal | Sorteio de formato por pauta, em cada canal, com briefing padronizado | Taxa de engajamento | Sem gasto adicional | HM · SM · AM | A partir do dia 16, até atingir o n |
| **EXP-03 · Cadência** | Postar mais aumenta alcance único sem derrubar a taxa de engajamento | Rollout escalonado de cadência por grupo de contas ou pautas | Alcance único; taxa de engajamento como guardrail | Custo de produção adicional, validado por FIN | HM · SM · AM | Dias 31–60 |

## Limitações
- Nada aqui diz que patrocínio, formatos ou canais **não funcionam no mundo real**; diz que **este registro não permite saber** (G2).
- O valor de uma interação e os desvios reais são **parâmetros de negócio**. As tabelas mostram cenários, não previsões.
- Os preços de mercado vêm de uma pesquisa em 4 sites, sem amostra padronizada: são faixas de referência, não cotação.
- O processo atual (contrato no e-mail e no CRM, relatório ao Head) é uma **premissa da minha experiência de operação**, a validar na semana 1 (STR-02).
- A recomendação de manter os 3 canais é de **não mudança** enquanto não há evidência; não é uma prova de que o mix atual é o ideal.

## Gate G5
**PASS** · 7 decisões priorizadas com owner, KPI e condição de parada · todas as perguntas do Head respondidas · custo implícito calculado sem inventar fee · 3 testes com dono e desenho.
