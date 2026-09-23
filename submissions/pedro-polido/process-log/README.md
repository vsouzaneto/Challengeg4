# Process log — como a IA foi usada

> Registro cronológico, escrito durante o trabalho (não reconstruído no final).
> Atores: **Pedro** (decisões, contexto, revisão) e **Claude Code** (Opus, agente no terminal: exploração, código, testes).
> O histórico de commits da branch `submission/pedro-polido` é a outra metade deste log.

## Linha do tempo

### 1. Entender o desafio antes de escolher (22/09)
- Claude Code clonou o repositório, leu o README principal, o guia de submissão e os 4 challenges e resumiu.
- **Pergunta do Pedro:** "qual desafio dá para fazer algo mais diferente que chame a atenção de forma eficiente?"
- **Recomendação da IA:** 002, com uma *hipótese a verificar*: o Dataset 1 (Kaggle `suraj520`) seria sintético, e a
  resposta de referência de qualquer LLM iria "achar" gargalos em ruído.
- **Decisão do Pedro:** 002. Baixou os dois datasets.

### 2. Verificar a hipótese antes de construir qualquer coisa
Primeira coisa feita com os dados: tentar *derrubar* a hipótese. Ela sobreviveu a tudo:

| Teste | Resultado |
|---|---|
| Volume | 8.469 linhas, não ~30.000 como diz o brief |
| Placeholders de template (`{product_purchased}`) | 100% das descrições |
| Resolução antes da primeira resposta | 49,3% dos tickets fechados |
| Janela de todas as datas de resposta e resolução | 27 horas |
| Tipo × assunto | independentes (p = 0,98) |
| Prever CSAT com todas as variáveis | 20,9% de acerto = chutar a nota mais comum |

- Em paralelo, um classificador de referência no Dataset 2 (texto real) acertou 86,6%, e **61% dos tickets com 97,7% de
  acerto** quando a IA só age com confiança ≥ 0,9. Isso virou a espinha da proposta de automação.

### 3. Decisões do Pedro que definiram a entrega
| Pergunta | Decisão | Por quê |
|---|---|---|
| Como posicionar o dataset sintético? | **Abrir a entrega com ele** | É o que separa a entrega do baseline: a IA sozinha reporta padrões no ruído |
| Qual LLM? | **Gemini** (chave própria) | Disponível; a chave fica num `.env` fora do git e nunca passa pelo chat |
| Formato do protótipo? | **Web app na Vercel** | O avaliador clica numa URL e usa em 30 segundos; Streamlit ficaria parecido com o de todo mundo |

### 4. Auditoria reproduzível (`solution/pipeline/01_auditoria_dataset1.py`)
A exploração virou um script em que cada afirmação sai com um número. Erros da IA pegos nesta etapa:

- **Contagem errada escrita à mão.** Na exploração, a IA rotulou a análise de combinações como "60 combos". São 80
  (4 canais × 4 prioridades × 5 tipos). Corrigido: o script calcula o número em vez de escrevê-lo.
- **Afirmação mais forte do que os dados.** O primeiro rascunho dizia que "todos os campos são uniformes". Gênero não é
  (p = 0,007). A afirmação foi restrita aos campos operacionais (p ≥ 0,11), e o motivo ficou documentado no código.
- **Tentação de ajustar a métrica ao discurso.** O teste "resoluções com vocabulário de suporte" deu 1%, não 0%. Em vez de
  apertar a regex até dar zero, olhamos os 23 casos: eram "order"/"account" como palavras soltas ("Account eat tax
  accept."). O card reporta as duas coisas: 0 de 2.769 descrevem ação técnica; 23 têm palavras genéricas soltas.
- **Permutation test para cada "achado" que uma análise ingênua faria.** A "pior combinação" (Email × Medium × Product
  inquiry, 3,4 h) aparece com dados embaralhados em 78% das simulações. É exatamente o tipo de frase que o baseline produz.
