# 01 · Processo atual (AS-IS)

> **Em 3 linhas:** a operação tem dois fluxos, **conteúdo orgânico** e **parcerias**, que terminam no mesmo lugar: um relatório do time e um dashboard que levam o Head a decidir pauta e verba. Nos dois fluxos, a decisão é tomada **sem régua prévia, sem comparação e sem ligar custo a resultado**. Os pontos vermelhos (FP) são as falhas que o arquivo de 52 mil posts deixa visíveis.

Fontes: brief do challenge; vivência de operação do Douglas (`process-log/decisions.md`, G4); lacunas do dado (`docs/gap-to-process-map.md`).

> **Premissa a validar.** O brief não descreve como a operação funciona. As etapas que vêm da vivência do Douglas (contrato registrado no e-mail e no CRM, resultado reportado ao Head por relatório e dashboard) são **premissas**, confirmadas ou corrigidas na semana 1 (STR-02, reunião de origem dos dados). As que vêm do arquivo são evidência.

```mermaid
flowchart TB
    subgraph HEAD["Head de Marketing"]
        H1["Define metas e verba"]
        H9{"Decide pauta, canais<br/>e renovação de parcerias"}
    end

    subgraph SM["Time de Social Media · fluxo A: conteúdo orgânico"]
        A1["Planeja pauta<br/>FP-06 cadência e horário não planejados<br/>FP-08 sem hipótese registrada"]
        A2["Briefing e produção<br/>FP-05 formato, duração e mensagem sem padrão"]
        A3["Publica em Instagram, TikTok, YouTube<br/>FP-06 horário sem fuso"]
    end

    subgraph GP["Gestor de Parcerias · fluxo B: patrocínio"]
        B1["Prospecta creator<br/>FP-03 sem cadastro mestre"]
        B2["Negocia e fecha contrato<br/>registrado em e-mail e CRM"]
        B3["Critério de escolha não documentado<br/>FP-08 sem grupo de comparação"]
    end

    subgraph CR["Creator"]
        C1["Publica conteúdo patrocinado"]
    end

    subgraph DADOS["Coleta e relatório"]
        D1["Métricas das plataformas<br/>FP-04 extração incompleta e sem validação<br/>FP-07 audiência só como rótulo"]
        D2["Custo fica no CRM<br/>FP-01 sem chave que ligue ao post"]
        D3["Venda não é atribuída<br/>FP-02 sem cupom ou UTM por contrato"]
        D4["Relatório do time e dashboard<br/>médias sem n nem margem de erro"]
    end

    H1 --> A1 --> A2 --> A3 --> D1
    H1 --> B1 --> B2 --> B3 --> C1 --> D1
    B2 --> D2
    C1 --> D3
    D1 --> D4
    D2 -.não chega.-> D4
    D3 -.não chega.-> D4
    D4 --> H9
    H9 -->|ranking de médias| A1
    H9 -->|renova ou expande| B1

    classDef fp fill:#fdecec,stroke:#e34948,color:#0b0b0b;
    class A1,A2,A3,B1,B3,D1,D2,D3 fp;
```

## Leitura para o Head
| Fluxo | O que acontece hoje | Por que isso impede decidir |
|---|---|---|
| **A · Conteúdo orgânico** | A pauta nasce sem hipótese; formato, duração, cadência e horário não são padronizados nem registrados; o resultado vira média no dashboard | Não há como saber **o que** funcionou nem **por quê**: o arquivo não tem variação de cadência, não tem unidade de duração e não tem horário com fuso |
| **B · Parcerias** | O gestor fecha o contrato e registra no e-mail e no CRM; o creator publica; o resultado volta como engajamento | O **custo está no CRM, mas não chega ao post**, e a **venda não é atribuída**. Sem essas duas pontas não existe retorno a calcular, só engajamento, que é igual ao orgânico |
| **Decisão (comum)** | Relatório e dashboard com médias levam o Head a decidir pauta e verba | Sem régua prévia, sem margem de erro e sem grupo de comparação, **sempre aparece um "vencedor"**, mesmo quando é ruído (G3: 332 comparações, todas equivalentes) |
