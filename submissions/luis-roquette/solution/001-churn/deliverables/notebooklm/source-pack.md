# Challenge 001 — fonte fechada para o NotebookLM

Use somente este documento. Ele sintetiza o processo e o diagnóstico sem dados pessoais, caminhos locais ou afirmações causais não sustentadas.

## Pergunta do CEO

O churn subiu, enquanto CS relata satisfação estável e Produto relata uso crescente. O objetivo é explicar o aparente conflito, identificar o que os dados realmente sustentam e recomendar a próxima decisão.

## Oito etapas do método

1. **Absorção do briefing:** releitura em loop até duas passadas consecutivas sem novos achados.
2. **Pesquisa antes de construir:** busca por soluções validadas e aplicação de Ponytail para reutilizar antes de criar.
3. **Descoberta socrática:** cinco ondas adaptativas e 25 decisões antes de escrever a solução.
4. **SPEC:** requisitos, critérios de aceite, limites causais e definição de pronto transformados em contrato verificável.
5. **Plano lapidado:** vinte revisões; encerramento somente após duas passadas consecutivas sem melhoria substancial.
6. **Implementação em feedback looping:** Planejamento, Revisão, Execução e Teste; gate vermelho reinicia a própria fase.
7. **Redundância e lapidação:** três rodadas de correção e cinco rodadas visuais, limitadas para evitar refinamento infinito.
8. **Resposta executiva e entrega:** fatos, limites e ações reunidos em brief, dashboard, vídeo, tour e evidências auditáveis.

## Quatro marcos de qualidade interna

| Nota interna | Evolução observada |
|---:|---|
| 7,0 | Confirmava o churn, mas ainda destacava sinais frágeis. |
| 8,6 | Separou fatos, associações e hipóteses; incluiu ausência de concentração. |
| 9,5 | Transformou incerteza em validações com responsáveis, prazos e regras de parada. |
| 9,9 | Reconciliou resposta, dashboard, relatório e artefatos pela mesma fonte canônica. |

Essas notas são uma rubrica interna de qualidade. Não são avaliação do G4 nem confiança estatística.

## Três viradas humanas

1. **Separar agregados de coortes:** a alta geral de uso não descreve as contas que churnariam.
2. **Recusar causalidade frágil:** nenhuma hipótese recebeu o rótulo de causa sem passar por todos os gates.
3. **Converter incerteza em ação:** a ausência de causa demonstrada virou um plano de validação com donos, prazos e critérios de parada.

## Seis fatos do diagnóstico

1. O churn mensal ponderado recente chegou a **12,4%**, alta de **7,0 pontos percentuais** sobre a referência.
2. O MRR perdido observado foi de **US$ 1.622.337**; não é receita automaticamente recuperável.
3. O uso diário por conta subiu de **0,336 para 0,493** no agregado, mas caiu de **0,349 para 0,304** entre futuros churners de 30 dias.
4. A satisfação dos respondentes subiu de **3,96 para 4,02** no geral, mas caiu de **4,50 para 3,67** entre futuros churners; a cobertura ficou perto de 65%.
5. Não houve concentração material demonstrada: o maior segmento elegível teve risco relativo de **1,08×**, abaixo do limiar de **1,25×**.
6. Nenhuma das seis hipóteses passou todos os gates; o modelo opcional também não foi publicado. A causa permanece não demonstrada.

## Resposta final

O conflito desaparece quando comparamos populações equivalentes: os agregados de Produto e CS podem melhorar ao mesmo tempo em que a coorte que churnará piora. Isso demonstra divergência entre populações, não uma causa.

A decisão correta é validar antes de intervir: Dados saneia eventos em sete dias; Produto acompanha uso prospectivamente por 30 dias; CS mede satisfação fora dos tickets por 30 dias. Sem histórico de intervenção, o impacto financeiro futuro não é causalmente estimável.

## Limites obrigatórios

- Não afirmar que uso ou satisfação causaram churn.
- Não tratar US$ 1.622.337 como receita recuperável.
- Não apresentar as notas internas como nota do G4.
- Não omitir a cobertura parcial de satisfação nem a qualidade temporal dos dados.
- Não chamar a watchlist de autorização para contato automático.
