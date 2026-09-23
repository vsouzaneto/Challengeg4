# Diagnóstico de churn da RavenStack

## Resposta para o CEO

O churn mensal ponderado chegou a **12,4%** no período recente, alta de **7,0 pontos percentuais** sobre a referência. O MRR perdido observado foi de **US$ 1.622.337**. Esse valor mede a receita associada aos churns registrados; não representa receita automaticamente recuperável.

O aparente conflito entre Produto e Customer Success vem de populações diferentes. O uso diário por conta cresceu no agregado, de **0,336 para 0,493**, mas caiu entre as contas que churnariam nos 30 dias seguintes, de **0,349 para 0,304**. A satisfação geral dos respondentes subiu de **3,96 para 4,02**, enquanto caiu de **4,50 para 3,67** entre respondentes que churnariam em 30 dias. As coberturas de satisfação foram de 63,3% e 65,9%; portanto, esses números descrevem quem respondeu a tickets, não toda a base.

**Causa ainda não demonstrada.** Nenhuma das seis hipóteses avaliadas passou simultaneamente pelos testes de estabilidade, associação, cronologia, amostra e confirmação entre fontes. Também não há concentração material comprovada: o maior segmento elegível, Estados Unidos, apresentou risco relativo descritivo de 1,08x, abaixo do limiar de 1,25x.

**Decisão recomendada:** corrigir a medição e validar uso e satisfação antes de automatizar qualquer intervenção em clientes. A abstenção causal evita direcionar esforço e receita para um mecanismo que os dados atuais não sustentam.

## Ações priorizadas

| Prioridade | Responsável | Ação e critério de sucesso | Impacto estimado | Confiança |
|---|---|---|---|---|
| 7 dias | Head de Dados | Sanear eventos fora do ciclo de vida e reproduzir as métricas. Avançar se churn e coortes permanecerem estáveis. | Impedir dados temporalmente inválidos de sustentar decisões. Impacto financeiro não estimável antes do saneamento. | Alta para qualidade; não causal. |
| 30 dias | Head de Produto | Acompanhar uso antes do churn com cobertura mínima de 70%. Avançar se a queda anteceder o churn; parar se desaparecer ou ocorrer depois. | Produzir a primeira estimativa prospectiva comparável. Impacto financeiro ainda não estimável. | Condicionada à cobertura. |
| 30 dias | Head de CS | Medir satisfação fora dos tickets, com resposta mínima de 70% por estrato. Avançar se a diferença persistir; parar se desaparecer. | Remover o viés de respondentes e comparar coortes representativas. Impacto financeiro ainda não estimável. | Condicionada à representatividade. |

O limite financeiro conhecido é o MRR perdido observado de US$ 1.622.337. Sem histórico de intervenções, qualquer previsão de recuperação seria inventada.

## Como cheguei à resposta

Eu tratei a documentação como parte do produto. O trabalho começou com leitura repetida do briefing até duas passadas consecutivas sem novos achados. Em seguida, conduzi cinco ondas socráticas adaptativas, com 25 decisões registradas, antes de escrever a SPEC.

A implementação seguiu SDD e ciclos de **Planejamento, Revisão, Execução e Teste**. O primeiro plano passou por 20 revisões. A construção ocorreu em nove fases, seguida por três rodadas de redundância e cinco rodadas de lapidação visual. Quando a evidência não sustentou causalidade ou o modelo preditivo não superou os gates fora do tempo, a solução recusou a conclusão em vez de fabricar confiança.

## Evolução da resposta

| Momento | Problema encontrado | Decisão humana | Nota interna |
|---|---|---|---:|
| Linha de base | A resposta confirmava o churn, mas destacava sinais frágeis. | Exigir impacto econômico, população e limite causal no primeiro bloco. | 7,0 |
| Veredito completo | Faltavam ausência de concentração e ação proporcional à evidência. | Separar fatos, associações e hipóteses; recusar um mecanismo vencedor. | 8,6 |
| Abstenção e ações | A conclusão era correta, mas pouco acionável. | Converter incerteza em três validações com responsáveis, prazos e regras de parada. | 9,5 |
| Entrega validada | Era preciso provar consistência entre superfícies. | Usar um JSON canônico, checksums, reprodução e 86 testes. | 9,9 |

As notas são uma rubrica interna de qualidade da resposta. Não representam avaliação do G4 nem 99% de certeza causal.

## Evidência e limites

A análise cruza as cinco tabelas por conta, assinatura e tempo. O painel usa janelas de 7, 30 e 90 dias e duas cronologias: `observed`, para sensibilidade, e `strict`, para decisão. A auditoria registrou 34.240 ocorrências de regras de qualidade; uma linha pode aparecer em mais de uma regra. Entre elas estão 19.142 usos anteriores à assinatura, 13.198 usos anteriores ao cadastro e 1.077 tickets anteriores ao cadastro.

O modelo preditivo foi tratado como opcional e não foi publicado porque falhou no gate fora do tempo. A watchlist contém contas específicas para validação, não autorização para contato. O `analysis_id` desta execução é `886cfb2b…`.

## Onde aprofundar

- [Relatório executivo completo](../artifacts/report.md)
- [Dashboard e instruções de reprodução](../README.md)
- [Resposta canônica](../artifacts/ceo_answer.json)
- [Diário de descoberta socrática](../../../process-log/001-descoberta-socratica.md)
- [Diário de implementação](../../../process-log/003-implementacao-feedback-looping.md)
