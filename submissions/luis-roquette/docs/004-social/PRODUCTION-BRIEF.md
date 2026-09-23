# Brief de produção da entrega

## Fonte canônica

Todo texto narrativo deriva de `CONSTRUCTION-STORY.md`. O DOCX e o TXT não recebem edições exclusivas. A análise quantitativa deriva de `solution/004-social/analysis.md` e `evidence.csv` no método `2.5.0`.

## Roteiro do Arcade

**Objetivo:** permitir que o avaliador compreenda o valor do cockpit e as três decisões em 2–3 minutos.

| Cena | Tela e ação | Callout | Conclusão |
|---:|---|---|---|
| 1 | Abrir o cockpit | “52.214 posts deixam de ser um arquivo e viram decisões rastreáveis.” | O sistema é local, manual e auditável |
| 2 | Enviar o CSV e mostrar hash, período e cobertura | “A fonte é validada antes de qualquer recomendação.” | O dataset ativo fica inequívoco |
| 3 | Percorrer os três cards executivos | “Engajamento, patrocínio e estratégia aparecem antes dos detalhes.” | As perguntas do Head são respondidas na abertura |
| 4 | Abrir o ranking multivariado | “Nenhum contexto passou todos os gates; o melhor candidato é teste, não vencedor.” | O motor evita falsa certeza |
| 5 | Abrir o cenário de patrocínio | “Sem custos e conversões, não há ROI. O cenário calcula a condição mínima para investir.” | Patrocínio vira decisão condicional |
| 6 | Mostrar as quatro semanas | “Baseline, teste, replicação ou revisão e decisão humana.” | A recomendação vira plano executável |
| 7 | Abrir evidência, registrar decisão e mostrar export | “Cada decisão conserva contexto, método e origem.” | O ciclo termina em ação auditável |

**Texto de abertura:** “Em menos de três minutos, veja como o cockpit responde às três perguntas do Head de Marketing e transforma evidência histórica em uma decisão operacional.”

**Texto final:** “Explore a análise, a evidência e o diário da construção no README da submissão.”

**Regras de captura:** usar a aplicação real; não mostrar caminho local completo; não mostrar o CSV bruto; aplicar blur a qualquer identificador externo; não afirmar ROI, causalidade, publicação automática ou performance atual de 2026.

## Prompt do vídeo no NotebookLM

> Crie um Video Overview em português do Brasil, com 4 a 6 minutos, para avaliadores do AI Master Challenge. Explique como Luis Roquette transformou o briefing de estratégia social media em um cockpit decisório local. Siga esta ordem: problema e três perguntas; absorção iterativa do briefing; pesquisa anterior ao framework; 24 ondas socráticas adaptativas; SDD e SPEC; implementação por Planejamento, Revisão, Execução e Teste; Redundância Necessária; lapidação de UI e do contrato executivo; três respostas finais; limites. Mostre como decisões humanas corrigiram e limitaram a IA. Use somente números presentes nas fontes. Não atribua causalidade, ROI ou validação humana que as fontes não comprovem. Termine indicando que o produto responde às três perguntas e que o diário permite auditar a construção.

**Correção após QA da primeira geração:** o primeiro vídeo durou 6min31s e exibiu uma frase que poderia confundir o tempo de execução da CLI com tempo de geração do código. A versão final foi regenerada com o contrato abaixo; o primeiro arquivo não integra a entrega.

> Crie um vídeo explicativo em português do Brasil, entre 4min30s e 5min30s, para avaliadores do AI Master Challenge. Use somente fatos das quatro fontes. Preserve seis passadas de absorção, pesquisa antes do framework, 24 ondas socráticas, SDD e SPEC, feedback loops, dez passadas de redundância, método 2.5, matriz 15/15, 146 testes catalogados e gate focal 45/45. Apresente os três veredictos finais. Diga claramente que 18,01 segundos foi o tempo de execução da CLI, nunca tempo para gerar código. Não alegue causalidade, ROI provado, validação humana concluída nem vencedor sustentado entre os 20 contextos.

**Resultado final:** a segunda geração durou 6min33s e corrigiu o conteúdo. A reprodução foi acelerada uniformemente para `1,1×`, sem cortes, resultando em 5min57,54s e preservando todo o roteiro.

## Prompt do mapa mental no NotebookLM

> Gere um mapa mental em português do Brasil com o nó central “Cockpit de Social Media”. Use quatro ramos principais: Desafio, Método de construção, Produto e Evidências. Em Método de construção, preserve a sequência Absorção em loop → Pesquisa → 24 ondas socráticas → SDD e SPEC → Feedback looping → Redundância Necessária → Lapidação → Gate executivo 2.5. Em Produto, inclua Entrada CSV, Motor Pandas, Cockpit Streamlit, SQLite, Export HTML e CSV. Em Evidências, inclua análise, evidence.csv, testes, Git e diário. Mantenha cada nó curto e não invente resultados.

## Prompt do infográfico no NotebookLM

> Crie um infográfico vertical em português do Brasil para um avaliador executivo. Título: “Como 52.214 posts viraram uma decisão auditável”. Organize em oito etapas numeradas: 1 Absorção do briefing, 2 Pesquisa obrigatória, 3 24 ondas socráticas, 4 SPEC orientada a testes, 5 Implementação em feedback loops, 6 Redundância Necessária, 7 Lapidação técnica e de UI, 8 Método 2.5 e três respostas. Para cada etapa, mostre uma decisão humana e uma mudança concreta no produto. Termine com três veredictos: manter o mix, não escalar patrocínio agora e executar o programa de 30 dias. Não apresente associação como causalidade nem invente ROI.

## Linha do tempo prompt para produto

| Etapa | Fragmento do prompt de Luis | Decisão | Mudança observável | Evidência |
|---:|---|---|---|---|
| 1 | “Duas passadas consecutivas sem novos achados” | Só avançar depois de provar absorção | Seis leituras; as duas últimas limpas | I01 |
| 2 | “Executar a pesquisa obrigatória antes de escolher framework” | Evidência antes da arquitetura | Streamlit, Pandas e SQLite escolhidos após comparação | I07 |
| 3 | “Pelo menos cinco ondas adaptativas” | Perguntar antes de especificar | 24 decisões sobre usuário, dados, motor e governança | I04–I05 |
| 4 | “Seguir com a metodologia SDD” | Converter escolhas em contrato | SPEC com critérios, arquitetura e Definition of Done | I02, I08–I09 |
| 5 | “Planejamento, Revisão, Execução, Teste” | Feedback antes de avançar | Implementação por ciclos vermelhos e verdes | I13–I27, I64–I68 |
| 6 | “Redundância Necessária” | Procurar lacunas depois de funcionar | Dez passadas e correções de borda, histórico e export | I29, I32–I51 |
| 7 | “Lapidar exaustivamente” | Melhorar técnica e experiência | Cache, precisão visual, segurança textual e nova UI | I30, I52–I61 |
| 8 | “Atingir pelo menos 9,5” | Responder diretamente ao Head | Ranking multivariado, break-even e estratégia de 30 dias | I63–I68 |

## Direção visual

- **Conceito:** mesa editorial de inteligência, consistente com o cockpit.
- **Cores:** papel `#F4F0E6`, carvão `#17201E`, coral `#ED6A5A`, verde de evidência `#3F6B58`.
- **Tipografia:** serifada editorial nos títulos; sans-serif legível no corpo; monoespaçada somente para IDs e método.
- **Composição:** fluxo vertical, oito marcos, uma relação causa e efeito por bloco, sem imagens decorativas.
- **Acessibilidade:** contraste AA, fonte mínima equivalente a 16 px em desktop, nenhuma informação dependente apenas de cor.

## Conversão e paridade documental

1. Editar somente `CONSTRUCTION-STORY.md`.
2. Gerar `CONSTRUCTION-STORY.txt` removendo apenas a sintaxe Markdown e preservando texto e URLs.
3. Gerar `CONSTRUCTION-STORY.docx` com títulos, tabelas, links e paginação.
4. Comparar títulos e os números críticos `52.214`, `1,56%`, `0,280`, `0,950`, `45/45` e `146` nos três formatos.
5. Renderizar o DOCX em PNG, inspecionar todas as páginas e repetir a geração se houver corte, sobreposição ou quebra ruim.

## Critérios finais

- README entrega valor em até 30 segundos.
- Arcade conclui o produto em 2–3 minutos.
- Vídeo explica a construção em 4–6 minutos.
- Todas as URLs externas abrem sem login em janela anônima.
- Duas passadas consecutivas terminam sem correção relevante.
