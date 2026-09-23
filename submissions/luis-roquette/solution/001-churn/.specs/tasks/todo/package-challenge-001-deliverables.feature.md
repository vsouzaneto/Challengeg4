---
title: Empacotar os entregáveis finais do Challenge 001
---

## Objetivo

Transformar a solução técnica e o diário contemporâneo em uma entrega multimodal curta, verificável e coerente, capaz de atender tanto um avaliador humano quanto uma IA sem esconder limitações ou duplicar fontes de verdade.

## Arquitetura da entrega

1. **Comece aqui:** README e brief de duas páginas com resposta, método e links.
2. **Veja funcionando:** tour do sistema no Arcade em oito passos e até 90 segundos.
3. **Entenda a construção:** vídeo obrigatório de arquitetura já gravado, com 6min05s e legendas.
4. **Veja a síntese:** Video Overview e infográfico produzidos no NotebookLM.
5. **Aprofunde se quiser:** relatório, código e Process Log.

## Público

- Avaliador executivo: precisa entender resposta, decisão e impacto em até 45 segundos.
- Avaliador técnico: precisa verificar números, causalidade, testes e reprodutibilidade.
- IA avaliadora: precisa receber Markdown limpo, sem depender de vídeo, imagem ou link externo.

## Mensagem central

O diferencial não é apenas o dashboard. É o método autoral de Luis para chegar a uma resposta confiável: absorção iterativa do briefing, cinco ondas socráticas adaptativas, SDD, lapidação até estabilidade, implementação em feedback looping, redundância necessária, auditoria adversarial e documentação contínua.

## Entregáveis

- `deliverables/delivery-brief.md`
- `deliverables/delivery-brief.docx`
- `deliverables/notebooklm/source-pack.md`
- `deliverables/notebooklm/generation-prompts.md`
- `deliverables/notebooklm/README.md`
- `deliverables/visuals/method-evolution-infographic.png`
- `deliverables/video/README.md`
- `deliverables/video/poster.png`
- `deliverables/arcade/arcade-script.md`
- `deliverables/arcade/README.md`
- `deliverables/delivery-manifest.md`

O vídeo original não entra no Git: possui 232.879.349 bytes, acima do limite comum do GitHub. O repositório guarda poster, metadados, checksum e URL de reprodução. Se o NotebookLM exportar outro formato de imagem, o manifesto registra o nome real; nenhum arquivo fictício será criado.

## Contrato narrativo

Todo formato deve preservar estes fatos:

1. Churn mensal ponderado recente de 12,4%, alta de 7,0 pp.
2. MRR perdido observado de US$ 1.622.337, sem chamá-lo de receita recuperável.
3. Uso agregado de 0,336→0,493 e uso dos futuros churners de 0,349→0,304.
4. Satisfação geral dos respondentes de 3,96→4,02, contra 4,50→3,67 entre futuros churners, com cobertura limitada.
5. Nenhum mecanismo passou todos os gates; causa não demonstrada.
6. Três validações: Dados em 7 dias, Produto em 30 dias e CS em 30 dias.

## Contrato metodológico

A narrativa deve mostrar, em ordem:

1. pesquisa de soluções existentes antes da criação;
2. leitura em loop até duas passadas sem novos achados;
3. cinco ondas socráticas adaptativas;
4. criação e lapidação da SPEC pela SDD;
5. implementação `Planejamento → Revisão → Execução → Teste`;
6. correções produzidas pelo feedback e pela redundância necessária;
7. elevação medida da resposta de 7,0 para 9,9;
8. auditoria de segurança proporcional ao beta.

## Regras

- O texto escrito é a fonte; os dois vídeos, o infográfico e o Arcade são derivados.
- Mostrar prompts decisivos e seus efeitos, não dumps integrais de conversa nem cadeia de pensamento privada.
- Não inventar certeza causal, impacto recuperável, score externo ou mecanismo vencedor.
- Não incluir segredos, dados pessoais, credenciais ou caminhos locais nas mídias públicas.
- Não publicar nem compartilhar externamente antes da confirmação final de Luis.
- Links externos são complementares; o PR deve continuar compreensível sozinho.

## Critérios de aceitação

1. O pacote principal pode ser avaliado apenas pelo PR e pelo Markdown.
2. `.md` e `.docx` têm o mesmo conteúdo substantivo; o brief não excede duas páginas ou 1.200 palavras.
3. As seis verdades quantitativas são idênticas em todos os formatos.
4. O Arcade possui oito passos, abre com valor, dura até 90 segundos e termina com decisão.
5. O vídeo obrigatório e o Video Overview são assistidos integralmente; o infográfico é revisado contra as fontes.
6. Cada link e arquivo do manifesto abre, possui tamanho maior que zero e identifica versão/data.
7. O Process Log explica ferramentas, erros da IA, correções humanas, iterações e contribuição autoral.
8. Cada recomendação declara prioridade, impacto mensurável, impacto financeiro e confiança; ausência de estimativa causal é explícita, nunca substituída por receita inventada.
9. O envio dos quatro desafios usa uma única branch `submission/luis-roquette`, um único PR por pessoa e o título `[Submission] Luis Fernando Roquette — Challenges 001–004`; nenhum arquivo fora de `submissions/luis-roquette/` entra no diff.
10. A data, o link do histórico Git e todos os links externos refletem o estado final e abrem sem autenticação.

## Fora de escopo

- Refazer a análise, o dashboard ou a identidade visual já aprovados.
- Criar site de campanha, landing page ou hospedagem de produção.
- Gerar novos números ou conclusões dentro do NotebookLM.
- Entregar mapa mental ou slide deck redundante.
- Automatizar publicação externa sem revisão humana.

## Referências de formato

- O guia do desafio exige solução e Process Log; aceita narrativa, screenshots, gravação, chat export e histórico Git combinados.
- O benchmark do Arcade recomenda 9–12 passos, mas o contexto de avaliação rápida justifica oito passos e até 90 segundos.
- NotebookLM será usado para Video Overview e infográfico; ambos exigem revisão factual.
