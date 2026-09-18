# 03 · Processo redesenhado (TO-BE)

> **Em 3 linhas:** os dois fluxos (conteúdo e parcerias) passam a entrar num **ciclo único de aprendizado**: nenhum post ou contrato começa sem hipótese e régua, nenhum dado entra sem validação, e nenhuma verba muda sem o fechamento de 30 dias. O ritmo é o definido pelo Douglas: **leitura a cada 15 dias, decisão a cada 30**. A IA faz a checagem e o cálculo; aprovar gasto e decidir escala continuam humanos.

```mermaid
flowchart TB
    G0{{"Gate 0 · Origem dos dados<br/>de onde veio, quem extraiu, health check"}}
    G0 -->|reprovado| FIX["Corrigir extração<br/>antes de qualquer análise"]
    FIX --> G0
    G0 -->|aprovado| P1

    P1["1 · Hipótese e pré-registro<br/>métrica: taxa de engajamento, régua ±1 p.p.<br/>parcerias: + custo, venda e break-even"]
    P1 --> G1{"Gate 1 · Aprovação<br/>Head aprova; Financeiro valida custo"}
    G1 -->|incompleto| P1

    G1 -->|conteúdo| A["2A · Briefing padronizado<br/>formato, duração, tema, gancho, CTA<br/>cadência e horário planejados"]
    G1 -->|parceria| B["2B · Contrato instrumentado<br/>campaign_id do CRM, cupom e UTM<br/>creator no cadastro mestre, grupo de comparação"]

    A --> P3["3 · Publicação instrumentada<br/>published_at com fuso, IDs ligados"]
    B --> P3
    P3 --> P4["4 · Coleta automática<br/>validação do data contract, completude ≥95%"]
    P4 --> Q{"5 · Leitura quinzenal · dia 15<br/>só acompanhamento e guardrails"}
    Q -->|dano ou custo estourado| STOP["Parada antecipada<br/>com registro do motivo"]
    Q -->|segue| D{"6 · Fechamento do ciclo · dia 30<br/>efeito, margem de erro, custo, venda"}
    D -->|acima da régua e do break-even| E1["Escalar"]
    D -->|promissor, incerto| E2["Replicar"]
    D -->|execução falhou| E3["Iterar"]
    D -->|equivalente ou abaixo do break-even| E4["Parar"]
    E1 --> L["7 · Aprendizado registrado<br/>volta para a pauta e para o pipeline de parcerias"]
    E2 --> L
    E3 --> L
    E4 --> L
    STOP --> L
    L --> P1

    classDef gate fill:#eaf2fc,stroke:#2a78d6,color:#0b0b0b;
    classDef human fill:#fff4e0,stroke:#eda100,color:#0b0b0b;
    class G0,Q gate;
    class G1,D human;
```

Legenda: azul = gate automático com revisão · amarelo = decisão humana obrigatória.

## As regras do ciclo

| Momento | O que acontece | Regra |
|---|---|---|
| **Gate 0 · Origem** | Antes de qualquer análise, a pergunta do Douglas: "de onde vocês retiraram estes dados, e de que forma?" | Sem origem documentada e health check aprovado, **não há análise**. Este arquivo de 52 mil posts seria reprovado aqui (DQ-05) |
| **1 · Pré-registro** | Hipótese, métrica primária, régua, duração do ciclo, grupo de comparação e, em parcerias, custo total e break-even | Escrito **antes** de publicar; não pode mudar depois de ver o resultado |
| **Gate 1 · Aprovação** | Head aprova o teste; Financeiro valida custo e break-even das parcerias | **Regra de entrada:** nenhum contrato novo de patrocínio é assinado sem passar por este gate (custo, cupom/UTM, grupo de comparação). Ativos seguem; exceção só com aprovação do Head, registrada. Decisão do Douglas; no G8 deixou de ser "suspensão" |
| **2A · Conteúdo** | Briefing padronizado para Instagram, TikTok e YouTube | Toda peça registra formato, duração em segundos, tema, gancho, CTA, horário planejado |
| **2B · Parceria** | Contrato no CRM gera `campaign_id`, cupom e UTM | Post patrocinado sem `campaign_id` não entra na leitura |
| **4 · Coleta** | Extração automática com validação | Completude mínima de 95% dos campos do data contract; o que falha fica em quarentena |
| **5 · Leitura de 15 dias** | Acompanhamento: volume, custo, guardrails (queda de engajamento além da régua, brand safety, estouro de custo) | **Não se declara vencedor no dia 15.** Olhar e decidir cedo aumenta a chance de confundir sorte com resultado. Só se para por dano |
| **6 · Fechamento de 30 dias** | Efeito com margem de erro, custo, venda e retorno | **Escalar:** efeito acima de +1 p.p. **e** retorno acima do break-even · **Replicar:** promissor, com margem de erro larga · **Iterar:** falha de execução ou de dado · **Parar:** equivalente (dentro de ±1 p.p.) ou abaixo do break-even |
| **7 · Aprendizado** | O resultado vira registro consultável | A próxima pauta e o próximo contrato partem do que foi aprendido, não do ranking de médias |

## Como o novo processo responde às perguntas do brief
| Pergunta do Head | Como passa a ser respondida |
|---|---|
| O que gera engajamento? | Testes de formato, duração e tema **dentro de cada canal** (2A), com régua de ±1 p.p. |
| Vale patrocinar? | Contrato com custo, venda atribuída e grupo de comparação (2B); decisão pelo break-even no dia 30 |
| Qual audiência engaja? | Distribuição de audiência por post e por creator (data contract), testada por segmento pré-registrado |
| Onde concentrar esforço? | Ciclos de 30 dias acumulam evidência por canal, formato e faixa de creator; escala só com resultado replicado |
| Frequência de postagem? | Cadência planejada × realizada vira variável testável (rollout escalonado) |
| O que parar? | Tudo que fechar o ciclo como **Parar** sai da pauta ou do pipeline |
