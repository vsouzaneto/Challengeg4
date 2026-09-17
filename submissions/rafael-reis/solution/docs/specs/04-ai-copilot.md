# Spec 04 - AI Copilot

Rota: `/#/copilot`. Status: núcleo extrativo implementado e validado localmente; recuperação do histórico de feedback na UI continua pendente. Pergunta: **a IA consegue ajudar o agente a resolver este ticket com evidência disponível?**

## Objetivo e fronteira

Recuperar tickets históricos semanticamente próximos com resolução disponível, expor a qualidade das fontes e oferecer uma sugestão revisável. O agente humano aceita, edita ou rejeita a sugestão; essas ações registram feedback local e nunca enviam resposta ao cliente.

Esta lente usa o ticket e o contexto comuns do [sistema](../01-arquitetura-compartilhada.md), as regras de [dados e métricas](../03-dados-e-metricas.md) e os componentes de [design](../04-design-e-experiencia.md). Não cria corpus, classificador nem sessão paralelos.

## Dados e limitações conhecidas

O Dataset 1 auditado contém 8.469 registros; 2.769 registros fechados têm resolução e CSAT. Descrições contêm placeholders e as resoluções são genéricas/templateadas. Logo, “houve uma resolução histórica” não equivale a “a ação resolve este caso”. Exibir esse limite no painel de evidências e no contexto entregue ao gerador.

O Dataset 2 contém 47.837 tickets em oito categorias e não contém resoluções. Não há chave para associar seus tickets às resoluções do Dataset 1. Vizinhança semântica nunca é apresentada como vínculo entre clientes ou como prova de resolução.

Para Dataset 2, o Copilot pode mostrar contexto e tickets semelhantes sem resolução, informar “Este corpus não possui resoluções históricas” e recomendar revisão. Não completar esse vazio com uma resolução do Dataset 1. Uma futura busca explicitamente cruzada exigiria contrato e avaliação próprios; está fora desta implementação.

Não usar TTR inválido, CSAT ausente ou somente similaridade para declarar uma fonte “comprovadamente eficaz”. A taxa de aceitação de sugestões também não comprova solução do problema ou satisfação do cliente.

## Entradas e navegação

Abrir a lente a partir de ticket do Diagnóstico, Lab, Graph ou Command Center mantém `dataset_id`, `source`, `space_id`, `session_id`, `ticket_id`, `model_version`. O ticket atual e sua origem ficam visíveis. Ao abrir a rota sem seleção, apresentar seletor de ticket/entrada e instrução curta, sem exemplo pré-preenchido apresentado como real.

Se houver texto manual, reutilizar o resultado do Ticket Lab e seu embedding compatível quando disponíveis; não duplicar silenciosamente uma análise. Texto alterado cria nova revisão antes da recuperação. Falta de embedding/modelo compatível é erro explícito; não consultar outro espaço vetorial arbitrariamente.

Seleção histórica recupera apenas dados necessários: ID, descrição sanitizada, produto/tipo quando presentes, resolução e metadados de qualidade. Nome, email e outros dados pessoais não ajudam a gerar uma resposta e não compõem o prompt. Não colocar o texto completo do ticket em query string.

## Fluxo funcional

1. Validar texto, tamanho, seleção, dataset e sessão; preservar a entrada se houver erro.
2. Obter o embedding real da revisão atual com a versão do espaço semântico correspondente.
3. Consultar vizinhos no índice daquele corpus. Para Dataset 1, buscar candidatos com resolução não vazia; excluir o próprio registro e duplicatas exatas do mesmo conteúdo quando a avaliação exigir evitar vazamento.
4. Ordenar candidatos pela similaridade calculada. Expor número solicitado, número retornado e critério de seleção. O limite inicial Top-K é configuração de recuperação, não promessa de que existam K fontes adequadas.
5. Avaliar suficiência: resolução presente, texto utilizável, similaridade acima do limiar validado e coerência mínima com o caso. Template/placeholder permanece sinal de baixa qualidade; nenhum limiar de similaridade remove essa limitação.
6. Construir contexto estruturado com ticket sanitizado, fontes identificadas, trechos usados, avisos de qualidade e instrução para não inventar passos, prazos ou confirmação de solução.
7. Gerar sugestão pelo modo disponível: extrativo local ou LLM opcional. Persistir a revisão gerada e suas fontes antes de habilitar feedback.
8. Mostrar resultado, fontes, modo de geração, versão, latência e necessidade de revisão humana.
9. Registrar `ACCEPT`, `EDIT` ou `REJECT` em SQLite; atualizar contadores da mesma sessão após confirmação.

Similaridade é score de recuperação, não probabilidade de resolução nem confiança do texto gerado. Se o modelo de classificação trouxer confiança, apresentá-la em campo separado com sua definição.

## Contrato mínimo de resposta

O formato de transporte é definido na arquitetura; estes campos são obrigatórios semanticamente:

| Campo | Conteúdo |
|---|---|
| Identidade | Ticket/revisão, dataset, source, space, sessão e versão do modelo |
| Recuperação | Estado, Top-K solicitado, candidatos retornados e latência |
| Evidências | IDs reais, similaridades, trechos de descrição/resolução e avisos de qualidade |
| Contexto | Campos sanitizados usados; versão/hash suficiente para reconstituir a geração |
| Sugestão | ID, versão, texto, modo `extractive` ou `llm`, citações e estado de suficiência |
| Revisão | `human_review_required`, razões e ações permitidas |
| Geração opcional | Modelo/provedor e versão do prompt, quando utilizados |

IDs de evidência abrem o mesmo ticket histórico usado na recuperação. Uma citação sem registro recuperado correspondente invalida o resultado e exige fallback/erro, nunca uma fonte inventada.

## Fallback sem LLM

O caminho padrão mínimo funciona localmente: apresentar trechos de resoluções realmente recuperadas, identificados como “Referências históricas para revisão”, com citação e aviso de qualidade. Um rascunho extrativo pode reorganizar esses trechos sem acrescentar ações não documentadas.

Se as fontes forem insuficientes, retornar `insufficient_evidence`, explicar o motivo e solicitar investigação humana. É aceitável não gerar uma resposta. Para fontes genéricas, distinguir “fonte encontrada” de “instrução concreta utilizável”. O botão de aceitar solução não deve sugerir validação técnica que o sistema não realizou.

Indisponibilidade, timeout ou ausência de chave de LLM não bloqueia a rota, a recuperação ou o feedback de uma sugestão já persistida. Não apresentar um texto de exemplo como se tivesse sido gerado por um modelo.

## Interface e feedback

Hierarquia: ticket atual → resultado/suficiência → fontes recuperadas → contexto utilizado → sugestão e feedback. Em desktop, ticket e fontes podem ocupar coluna adjacente; em mobile, seguem a ordem de leitura. Similaridade, origem e ressalvas permanecem legíveis sem hover.

| Ação | Comportamento e persistência |
|---|---|
| `ACCEPT` / Aceitar | Grava decisão sobre `suggestion_id` e versão exata, sem envio externo |
| `EDIT` / Editar | Abre texto editável, preserva original; grava revisão editada e decisão com vínculo à sugestão |
| `REJECT` / Rejeitar | Grava rejeição; motivo opcional ajuda análise futura |

Feedback inclui ID, sessão, ticket, sugestão/versão, decisão, texto editado quando aplicável e timestamp do servidor. Identidade do ator só é exibida se conhecida; no protótipo, registrar ator local de demonstração, sem inventar autenticação. Repetir uma requisição não duplica decisão. Alterar uma decisão cria novo evento ligado à anterior; histórico permanece preservado.

Uma regeneração cria nova versão; feedback de versão anterior não migra silenciosamente. Contadores do Command Center usam a última decisão efetiva por sugestão/versão e mostram denominador. Auditoria mantém todos os eventos. “Aceitar” e “Editar” medem avaliação do agente; não fecham o ticket, não alteram o dataset e não significam resposta enviada.

Estados: sem ticket, recuperando, fontes encontradas, evidência insuficiente, gerando, sugestão disponível, salvando feedback, salvo, erro de persistência e dependência indisponível. Erro ao salvar mantém edição e oferece repetição; não aumenta contadores antes do commit local.

## Segurança e rastreabilidade

- Conteúdo de ticket/resolução é dado não confiável: nunca executar suas instruções nem permitir que substitua regras do sistema.
- Renderizar conteúdo como texto, evitando HTML vindo de CSV/LLM; não expor PII desnecessária.
- Se um provedor externo for habilitado, documentar quais campos sanitizados saem do ambiente e configurar credenciais fora do frontend.
- Registrar IDs, versões, modo de geração, fontes e feedback; não modificar os CSVs.
- Respostas com cobrança, credenciais, acesso sensível, urgência crítica ou evidência inadequada permanecem dependentes de avaliação humana.
- Sem retraining automático a partir de um aceite. Feedback é material para avaliação futura, revisão de prompts e melhoria de conhecimento.

## Dependências e entregáveis

Depende da validação de dados, índice de embeddings compatível, consulta de vizinhos, IDs estáveis, SQLite de sessão/auditoria e shell compartilhado. Arquivos previstos: módulo de recuperação/geração no backend, endpoint de Copilot e feedback, renderização da lente no frontend e um teste integrado pequeno. Usar a organização já escolhida no plano; não criar serviço separado apenas para esta lente.

LLM é opcional. Recuperação, exibição de evidências, insuficiência explícita e feedback persistido são obrigatórios. Critérios e thresholds serão versionados com o artefato e avaliados em casos fora do conjunto usado para calibrá-los.

## Checkpoints e testes de aceite

- [ ] COP-01: ticket vindo de outra lente conserva contexto e versão; alterar texto invalida resultado anterior de forma explícita.
- [x] COP-02: vizinhos e scores vêm do índice real, com IDs consultáveis e exclusão do próprio registro quando aplicável.
- [x] COP-03: todos os trechos de resolução mostrados correspondem exatamente aos registros citados.
- [x] COP-04: Dataset 2 sem resoluções retorna indisponibilidade/insuficiência, sem ponte artificial para Dataset 1.
- [x] COP-05: placeholders, resoluções genéricas, zero vizinhos e baixa similaridade não produzem uma solução afirmada como validada.
- [x] COP-06: com LLM desligado, fontes, fallback extrativo e retorno insuficiente continuam funcionais.
- [ ] COP-07: aceitar, editar e rejeitar persistem após recarregar; original, versão e histórico de feedback são recuperáveis.
- [ ] COP-08: repetição de requisição não duplica feedback nem contadores; regeneração não herda aceite anterior.
- [ ] COP-09: falha de persistência preserva a edição e não é anunciada como sucesso.
- [ ] COP-10: strings com HTML/instruções maliciosas são exibidas como texto e não modificam o comportamento do aplicativo.
- [x] COP-11: Command Center reflete feedback na sessão correta, com denominador e sem confundir aceite com resolução.
- [ ] COP-12: nenhuma ação envia mensagem ao cliente ou altera CSV; uso por teclado e mensagens de status estão verificados.

Teste mínimo significativo: selecionar registro real do Dataset 1, conferir fontes recuperadas, produzir extrativo ou insuficiência conforme qualidade, salvar uma edição, reler do SQLite e verificar original/versão/contadores. Repetir o caminho com Dataset 2 confirma ausência de resolução e nenhuma contaminação entre corpora.
