# Process Log — Humano + IA

## Filosofia
A solução não foi construída como “a IA resolveu o desafio”.

O processo foi **decisão humana + aceleração e crítica por IA**.

## Caminho

### 1. Problema antes da tecnologia
A pergunta evoluiu de “qual deal vai ganhar?” para “em que oportunidade deve o vendedor investir o próximo minuto?”. Daí nasceu o FocusScore.

### 2. Arquitetura
Foi escolhida uma solução próxima de produção: Odoo Community + n8n + ChatGPT + ambiente dedicado em g4.mftechsolutions.pt.

### 3. Explainability
O score evoluiu para prioridade, tags, atividades, deadlines e contexto para ação.

### 4. Credenciais
Uma abordagem inicial de autenticação revelou limitações. Durante testes, uma credencial errada apontou para outro CRM. O resultado foi melhor separação de ambientes e uso da credencial dedicada G4_odoo.

### 5. Duplicação
Os primeiros imports mostraram que uma sincronização não pode assumir execução única. A arquitetura evoluiu para idempotência usando opportunity_id como referência.

### 6. Parsing HTML
A description do Odoo continha HTML. A primeira lógica tratou-a como texto simples. O workflow executava sem erro, mas interpretava campos incorretamente. O HTML passou a ser normalizado antes do parsing.

**Aprendizagem:** workflow verde não significa resultado correto.

### 7. Run Once for All Items
Um Code node recebia milhares de oportunidades e devolvia uma. Após corrigir o retorno: input 8.800 → output 8.800.

### 8. Escala
O processamento foi validado progressivamente antes de executar o dataset completo.

### 9. Lost = 0
O primeiro WIN INTELLIGENCE mostrou Won 4.238, Lost 0 e win rate 100%. Os Lost estavam arquivados. Depois da correção: Won 4.238, Lost 2.473, Open 2.089, win rate 63,2%.

**Aprendizagem:** resultados perfeitos merecem investigação antes de celebração.

### 10. Estatística
A primeira versão usava mínimo de 50 negócios por segmento. Isso foi considerado insuficiente como proxy de confiança. Foram adicionados intervalos de confiança, efeito absoluto, comparação vs restante população, p-value, múltiplos testes, shrinkage e classificação de evidência.

## Onde a IA não foi seguida automaticamente
A discussão sobre “Prioritária 🔥” levou a separar stage de priority. Também foi rejeitada a ideia de criar 35 utilizadores artificiais apenas para reproduzir o dataset.

## Contribuições
| Origem | Contribuições |
|---|---|
| Humano | problema, arquitetura, UX comercial, decisões de produto, validação e seleção das sugestões |
| IA | análise, crítica técnica, código, debugging, leakage e estatística |
| Construção conjunta | FocusScore, explainability, enrichment, automações, testes e WIN INTELLIGENCE |

## Principal aprendizagem
Lead Scoring não é apenas calcular um número.

**dados → contexto → FocusScore → explicação → prioridade → próxima ação**

O valor surgiu no ciclo **ideia → crítica → implementação → teste → erro → correção**.
