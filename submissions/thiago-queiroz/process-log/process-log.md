# Process Log — Challenge 004

## Resumo

O trabalho foi conduzido como um processo de decisão assistido por IA, com auditoria dos dados antes da narrativa, gates explícitos, desenvolvimento orientado a testes, revisão visual e revisão Cética em contexto separado. O objetivo não foi maximizar o número de gráficos, mas impedir que uma fixture sintética produzisse recomendações convincentes, mas não sustentadas.

## Ferramentas e papéis

- **Thiago Queiroz:** escolha do desafio, decisões de escopo, validação visual, correções de linguagem executiva e gate final de submissão.
- **Hermes Agent:** coordenação, decomposição, implementação, testes e consolidação das evidências.
- **Agentes em contextos separados:** auditorias metodológicas, revisões Céticas e tentativas de refutação.
- **Python:** auditoria dos dados, construção determinística, testes e empacotamento.
- **Playwright / Chromium:** QA visual e verificação de comportamento offline.
- **Git:** histórico, gerações imutáveis e checkpoints.

## Decomposição inicial

O brief foi separado em seis perguntas operacionais:

1. Onde concentrar esforço?
2. Qual frequência de postagem usar?
3. Qual política de patrocínio adotar?
4. Qual perfil ou limiar de influenciador priorizar?
5. O que parar de fazer?
6. O que implementar nesta semana?

Antes de responder, cada pergunta recebeu um contrato mínimo: campos necessários, estimando, evidência disponível, limitação e ação permitida. Essa etapa revelou que várias solicitações do brief, como retorno sobre investimento e ranking de creators, não eram identificáveis com os campos fornecidos.

## Evolução e iterações

O processo estruturado registra vinte eventos principais, de `EVT-001` a `EVT-020`, além da revisão autoritativa final e da auditoria posterior do notebook público.

### 1. Seleção e auditoria

- Challenge 004 escolhido como sistema de decisão.
- Fonte, licença, hashes, esquema e proveniência congelados.
- Dataset identificado como simulado.
- Identidade dos creators e reutilização de URLs auditadas.
- Decisão humana: não tratar a fixture como verdade operacional.

### 2. Primeiras gerações rejeitadas

As gerações iniciais foram bloqueadas por problemas como:

- claims sem vínculo executável com evidências;
- matriz decisória ambígua;
- contratos incompletos de falha;
- instruções canônicas e próximos passos obsoletos;
- capturas não autenticadas;
- bytes navegados não vinculados ao HTML revisado;
- ausência de respostas estratégicas explícitas;
- linguagem estatística mais forte do que a evidência.

Essas gerações não foram relabeladas como aprovadas. Cada bloqueio material virou teste de regressão e exigiu novos bytes e nova revisão.

### 3. V2 e remediações

A V2 foi redesenhada em três camadas:

- **Desconstrução:** separar o que parece acionável do que a base realmente mede.
- **Choque de Realidade:** tornar visíveis simulação, identidade instável, uniformidade e ausência de economia atribuível.
- **Guardião da Qualidade dos Dados:** bloquear recomendações incompatíveis com o nível de evidência.

Uma revisão autoritativa intermediária encontrou quatro falhas altas, duas médias e uma baixa. Foram corrigidas com testes prévios:

- matriz estratégica de seis respostas;
- análise de 970 hashtags com Welch aproximado e correção de Holm;
- tese descritiva restrita;
- patrocínio ajustado apenas nos componentes efetivamente calculados;
- estimando comparável;
- mapas de claims e decisões vinculantes;
- linguagem executiva em português.

Outra geração foi bloqueada porque o CSV e o ZIP não estavam dentro do checkout congelado. A correção tornou o pacote autossuficiente e verificável em cópia limpa.

### 4. Feedback humano

Thiago aprovou a direção e pediu refinamentos de comunicação:

- histórico completo do processo;
- separação visual de rótulos e valores;
- cards comparáveis para patrocínio, audiência e múltiplas comparações;
- linguagem de risco financeiro sem extrapolação;
- matriz com alertas executivos;
- gráfico trimestral com escala declarada;
- conexão entre identidade instável e recomendação de creators;
- meta de mensuração condicionada a desfecho, amostra, potência e atribuição.

A geração seguinte foi novamente bloqueada. A revisão identificou linguagem indevida sobre falsos positivos, manifesto de testes inconsistente, promessa excessiva sobre mensuração, capturas legadas e falta de evidência da matriz em zoom ampliado. Tudo foi convertido em regressões e corrigido em uma nova geração.

### 5. Aprovação técnica

A geração final recebeu:

- Schema Gate: `PASS`;
- nota: `10,0/10`;
- severidades: `C0/H0/M0/L0`;
- `safe_to_checkpoint=true`;
- 47 testes aprovados;
- dois builds idênticos;
- 30 capturas autenticadas;
- zero erro de console, página ou rede;
- zero overflow horizontal ou sobreposição.

### 6. Tentativa adicional de refutação

Antes da submissão, foi auditado um notebook público baseado no mesmo dataset. O notebook propunha um classificador XGBoost e um gráfico de engajamento por horário.

A reprodução encontrou:

- target definido por `(likes + 2×shares + 0,5×comentários) / seguidores`;
- `follower_count` sozinho reproduz aproximadamente 96% das classes;
- correlação classe × seguidores de aproximadamente `−0,979`;
- informação pós-publicação em `comments_text`;
- split por `creator_id` semanticamente inválido;
- thresholds calculados antes do split;
- gráfico por horário baseado na média da classe artificial, não em interações reais.

Recalculando interações reais por hora, a maior e a menor média diferiram cerca de 0,22%. Isso não sustenta um horário vencedor e não alterou a conclusão da V2.

## Principais erros da IA e resposta humana

1. **Excesso de confiança estatística:** linguagem causal ou definitiva foi substituída por evidência insuficiente e limites explícitos.
2. **Ação antes da identificação:** rankings e políticas foram bloqueados quando faltavam identidade estável, custo, receita e atribuição.
3. **Mistura de métricas:** estimandos foram separados e rotulados.
4. **QA declarativa:** hashes, screenshots e bytes navegados passaram a ser autenticados e reproduzidos.
5. **Estado documental obsoleto:** gerações inconsistentes foram rejeitadas em vez de reparadas retroativamente.
6. **Alta acurácia enganosa:** um baseline de uma variável foi usado para demonstrar o acoplamento matemático do alvo.

## Julgamento humano que orientou a entrega

A contribuição central foi decidir não entregar a recomendação que o brief parecia esperar quando os bytes não a sustentavam. A solução transforma essa recusa em produto: mostra por que a decisão está bloqueada, protege orçamento, informa o que falta e apresenta um caminho de medição prospectiva.

## Evidências vinculadas

- `process-timeline.json`: eventos e decisões.
- `refutation-log.md`: falhas encontradas e remediações.
- `human-review-v2.md`: feedback humano convertido em requisitos.
- `authoritative-skeptic-review.md`: revisão técnica final.
- `kaggle-notebook-comparison.md`: tentativa adicional de refutação.
- `../docs/dataset-audit.md`: auditoria reproduzível.
- `../docs/visual-qa.md`: QA visual.
- `../solution/source-checkpoint.zip`: fonte, dados, testes e evidências congeladas.

## Privacidade

O process log público não inclui credenciais, segredos, conversas privadas não relacionadas ou dados pessoais brutos. As evidências foram curadas para mostrar decisões, iterações e correções sem expor conteúdo sensível.
