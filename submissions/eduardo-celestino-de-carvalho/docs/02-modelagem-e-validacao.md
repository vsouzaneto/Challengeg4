# Hipótese de modelo e plano de validação

> **Hipótese registrada em 15/10/2026:** usar negócios concluídos (`Won`/`Lost`) para estimar o potencial de sucesso de oportunidades abertas. A hipótese surgiu de uma pergunta do candidato após a definição do problema de negócio.

## Universo e alvo

- **Treino e avaliação:** oportunidades concluídas, com alvo `Won = 1` e `Lost = 0`.
- **Aplicação:** oportunidades `Prospecting` e `Engaging`.
- **Levantamento inicial:** 4.238 ganhas, 2.473 perdidas e 2.089 abertas. Conferir esses números novamente no pipeline reproduzível.

A proporção de ganhos entre negócios concluídos não é, por si, a probabilidade de ganho de toda a carteira: negócios ainda abertos não têm desfecho observado.

## Variáveis candidatas, sujeitas à auditoria

- Produto e preço de catálogo, obtidos de `products.csv`.
- Vendedor, manager e regional, obtidos de `sales_teams.csv`.
- Informações de conta, quando presentes, sem depender delas para atender toda a carteira.
- Datas anteriores ao resultado, somente se sua disponibilidade na decisão for demonstrada.

**Excluir como entradas:** `close_date`, `close_value`, `deal_stage` final (`Won`/`Lost`) e qualquer variável calculada a partir do resultado. Identificadores não devem ser tratados automaticamente como sinal preditivo.

## Riscos conhecidos

1. **Vazamento temporal:** campos do desfecho produziriam uma avaliação artificialmente boa.
2. **Ausência de conta:** 1.425 das 2.089 oportunidades abertas não têm `account`; as concluídas têm esse campo. Medir a cobertura do modelo e oferecer um caminho que não dependa da conta.
3. **Sem histórico de etapas:** não sabemos em qual etapa cada negócio concluído estava na data em que uma previsão teria sido feita. Assim, não há base direta para treinar probabilidades separadas para `Prospecting` e `Engaging`.
4. **Desfecho censurado:** os negócios ainda abertos podem terminar em ganho ou perda. Avaliar apenas os concluídos introduz seleção; a previsão deve ser apresentada como aproximação, não como probabilidade operacional comprovada.
5. **Mudança no tempo:** os registros são históricos (2016–2017). Um modelo treinado neles precisaria ser recalibrado antes de uso real atual.
6. **Grupos pequenos:** segmentos com poucos negócios podem exibir taxas extremas por acaso. Comparações por vendedor, produto e conta exigem tamanho amostral e regularização.
7. **Junção de produto:** 1.480 negócios registram `GTXPro`, mas o catálogo traz `GTX Pro`. Uma correspondência direta perde o preço desses negócios; usar mapeamento explícito e verificável, sem excluir as linhas silenciosamente.

## Experimentos planejados

1. Auditar cardinalidade, duplicatas, junções, nulos, cronologia e distribuição do alvo.
2. Criar uma referência simples de priorização, documentando regras e limitações.
3. Treinar um modelo interpretável com variáveis disponíveis antes do fechamento; só adicionar complexidade se houver ganho demonstrado.
4. Separar avaliação no tempo, respeitando a data em que rótulos se tornariam conhecidos. Registrar qualquer viés provocado por negócios ainda abertos.
5. Comparar com a referência em **ordenação da carteira** (por exemplo, ganho observado nos primeiros `k` negócios), além de discriminação e calibração, quando aplicável.
6. Medir cobertura e comportamento para contas ausentes; revisar exemplos individuais de scores altos e baixos.

**Atualização em 15/10/2026:** o experimento foi executado e documentado em [07-g2-modelagem.md](07-g2-modelagem.md). A regressão logística não mostrou ganho operacional suficiente no teste temporal. Não será usada como probabilidade de ganho da carteira aberta; o G3 criará uma prioridade comercial explicável.

## Da previsão à prioridade de ação

O potencial de sucesso é apenas um sinal. A fila do vendedor deverá considerar também valor potencial, momento e qualidade dos dados, sempre com uma explicação legível. O preço de catálogo pode ser um substituto imperfeito para valor de uma oportunidade; `close_value` não pode ser usado para negócios abertos. A interface deve permitir reconhecer casos em que o julgamento humano prevalece.
