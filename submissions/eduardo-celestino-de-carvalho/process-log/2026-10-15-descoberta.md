# 15/10/2026 — escolha do case e definição da hipótese

## Objetivo da interação

Escolher um desafio em que a entrega pudesse gerar uma decisão de negócio útil e definir o problema antes de programar. Em seguida, verificar se os negócios históricos permitiriam um modelo de potencial de sucesso.

## Uso de IA e verificações

1. **Comparação dos quatro briefs.** Codex / ChatGPT leu requisitos, critérios e guia de submissão. A recomendação foi o Challenge 003 pela exigência de software funcional e decisão comercial explicável. O candidato confirmou a escolha.
2. **Conferência inicial do dataset público.** Codex / ChatGPT verificou os CSVs originais do Kaggle e contou 4.238 oportunidades `Won`, 2.473 `Lost`, 1.589 `Engaging` e 500 `Prospecting`; 1.425 das abertas não têm conta informada. Esses números ainda serão incorporados ao tratamento reproduzível da solução.
3. **Definição do problema de negócio.** Antes de escolher modelo ou interface, formulamos a decisão: quais negócios merecem o tempo do vendedor agora, por quê e com qual próximo passo. Separamos potencial de sucesso, valor e urgência.
4. **Intervenção do candidato.** Eduardo perguntou se os dados continham oportunidades efetivamente concluídas e propôs usar as ganhas e perdidas para criar um modelo preditivo de “potencial de sucesso”. A ideia orienta o plano em [docs/02-modelagem-e-validacao.md](../docs/02-modelagem-e-validacao.md).
5. **Revisão crítica da ideia.** Codex / ChatGPT identificou risco de vazamento por `close_date`, `close_value` e etapa final, além de ausência de conta na carteira aberta e falta de histórico das etapas. A decisão foi testar o modelo contra uma referência simples e apresentar limites com clareza.
6. **Escolha da metodologia.** Após nova solicitação do candidato, adotamos CRISP-DM com contrato de previsão, separação temporal, comparação com referência simples e métricas de ordenação da carteira. Consultamos documentação primária da IBM e do scikit-learn. A skill oficial `jupyter-notebook` foi instalada para apoiar experimentos reproduzíveis; não foi encontrada uma skill de modelagem preditiva no catálogo oficial consultado.
7. **Primeira auditoria executável.** Um notebook criado com a skill oficial baixou o ZIP público e conferiu chaves, etapas, nulos e datas. A junção direta com o catálogo falhou em 1.480 linhas: `GTXPro` no pipeline versus `GTX Pro` no catálogo. A correção proposta foi um mapeamento exato e documentado, com verificação de que todos os produtos passam a encontrar correspondência. O arquivo original permanece intacto.
8. **Correção no preparo do repositório.** O comando inicial de stage forçado na pasta inteira incluiu também o ZIP baixado, pois `git add -f` ignora as regras de exclusão. A verificação do stage detectou isso antes de qualquer commit ou envio; o ZIP foi retirado do stage e a instrução passou a exigir uma lista explícita de arquivos. O ZIP continua apenas local.

## Ajuste de rumo e contribuição humana

A recomendação inicial priorizava regras transparentes. O candidato percebeu que os desfechos históricos também poderiam apoiar aprendizado supervisionado. O plano foi ampliado: testar se o modelo acrescenta utilidade à decisão comercial, mantendo regras simples como referência. Nenhum desempenho preditivo foi afirmado antes de validação.

A primeira versão da hipótese pressupunha que a relação entre pipeline e catálogo poderia ser usada diretamente. A auditoria mostrou que isso excluiria preço de catálogo em 16,8% dos negócios; ajustamos o plano para normalizar apenas a grafia `GTXPro` e testar a cobertura da junção. Esse é um erro de premissa encontrado antes do treinamento, não um resultado do modelo.

## Próximas evidências necessárias

- Auditoria reproduzível de chaves, datas e nulos.
- Definição das variáveis realmente disponíveis na data da decisão.
- Comparação temporal entre modelo e referência simples.
- Demonstração funcional para um vendedor e registro de ajustes após teste.
- Registro das métricas e da cobertura do modelo, inclusive nos negócios sem conta informada.
