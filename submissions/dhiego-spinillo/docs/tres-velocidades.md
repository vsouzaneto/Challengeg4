# Três caminhos para o atendimento

**Proposta de evolução, 21/09/2026.** O protótipo atual implementa classificação assistida, conferências humanas, rascunhos por regra e recap experimental. Os caminhos autônomos abaixo ainda não estão integrados nem avaliados.

## Decisão de produto

Reservar a atenção humana para exceções e julgamento. Um resultado insuficiente do classificador não deve obrigar todo procedimento conhecido a passar por revisão manual. A autorização de uma ação depende de regras, identidade e estado do sistema; a pontuação do modelo não a substitui.

| Caminho | Experiência proposta | Papel da IA e das regras | Prova necessária |
|---|---|---|---|
| **Resolve pelo autosserviço** | Pedido simples chega ao procedimento correto e o cliente conclui sem atendente. Ex.: iniciar recuperação de senha pelo provedor oficial. | IA sugere intenção ou recupera instrução aprovada. Cliente confirma o pedido no autosserviço; regras verificam elegibilidade, autenticação quando aplicável e execução. | Fluxo completo com resultado confirmado, falhas tratadas e resolução sem recontato. Abrir um link não conta como resolução. |
| **Chega preparado para atender** | Atendente recebe pedido, contexto consultado, lacunas e resposta proposta. Revisa exceções e a resposta final; não transcreve todas as verificações. | IA extrai pedidos e resume evidências; conectores consultam notas e sistemas; regras escolhem procedimento. Cada afirmação aponta sua origem. | Consulta real ou simulada explicitamente; cobertura do pedido, fidelidade e trabalho ativo total medidos. |
| **Exige investigação humana** | Caso sensível, ambíguo ou fora de procedimento chega à pessoa adequada com evidências organizadas. | IA ajuda a extrair relato e preparar perguntas; humano investiga, decide causa, prioridade e ação. | Não confundir hipótese com fato; preservar o relato e encaminhar corretamente as exceções. |

Não é uma escala de prioridade: uma solicitação urgente pode exigir humano imediatamente. Cada caminho precisa considerar prazo, impacto e canal; sentimento não determina urgência sozinho.

## O que encontramos para orientar a escolha

Busca integral sobre **47.837 textos do D2**, reproduzida por [script](../solution/mapear_oportunidades.py) e [JSON](../solution/reports/oportunidades.json). Expressões não exclusivas; seis exemplos por busca, sorteados com seed 42, foram inspecionados. A inspeção não estima precisão da busca.

| Sinal exploratório | Contagem | Leitura dos exemplos e decisão |
|---|---:|---|
| Menção a reset de senha | **685 (1,43%)** | Há pedido de instrução, link que não chega e erro de controlador. Priorizar separar recuperação simples de falha técnica. Não tratar todos os 685 como automatizáveis. |
| Alteração de perfil/dados | **161 (0,34%)** | Aparecem telefone no diretório, mudança de gestor e caminho de perfil técnico. Criar intenções específicas e lista de campos permitidos; a palavra “profile” não autoriza alteração cadastral. |
| Palavras de frustração/insatisfação | **78 (0,16%)** | Há frustração explícita, mas também texto padrão de pesquisa e palavras citadas. Não chamar isso de classificador de sentimento nem de taxa de clientes insatisfeitos. |

Exemplos auditáveis: reset **46.304** (onde redefinir), **5.309** (solicitação não recebida), **12.423** (erro ao trocar); perfil **15.546** (telefone), **3.128** (gestor), **9.374** (caminho de perfil); sentimento **17.001** (frustração), **4.579** e **35.132** (texto de avaliação que pode confundir a leitura). São números de linha de dados, sem o cabeçalho. Não extrapolar proporções para os 30 mil tickets/ano do cenário nem somar buscas como carteira de oportunidades.

## Recorte recomendado para uma próxima implementação

1. **Um autosserviço completo de recuperação de senha.** O cliente descreve o problema ou escolhe o procedimento; a intenção sugerida conduz ao fluxo oficial. Token, prazo de validade e mudança de senha pertencem ao provedor de identidade. Falha, ausência do canal de recuperação ou pedido diferente abrem atendimento com o que já foi tentado. Procedimento alinhado à [orientação OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html). Sem esse provedor, demonstrar em ambiente simulado identificado; nunca alegar que uma conta real foi alterada.
2. **Preparação automática do caso intermediário.** Buscar outros tickets e notas por identificador confiável, consultar estado da solicitação e montar resposta com fontes. No protótipo atual essas conferências são manuais. A integração pode retirar trabalho maior que apenas redigir uma frase.
3. **Exceção real discutida com Dhiego.** D2 45.725: relato de acesso a dados de colega, categoria RH preservada, evidências e possível encaminhamento a Segurança/Engenharia. A automação prepara a investigação sem decidir se houve vazamento.

Esses três exemplos demonstrariam a política completa. A previsão de esforço depende das integrações disponíveis; não incluir uma integração de produção como se fosse parte concluída do case.

## Sentimento e respostas

Sentimento é candidato a sinal auxiliar com trecho de origem e possibilidade de “não é possível determinar”. O D2 não tem referência rotulada para validá-lo; a avaliação exigiria amostra anotada por humanos, incluindo negação, citação e mensagens de atendentes. Não está implementado. Recorrência, temperatura e risco de churn precisam de identidade/histórico confiáveis.

Rascunhos atuais são determinísticos. Geração livre por LLM só deve avançar com conteúdo aprovado e teste de fidelidade; o recap experimental atual passou em fidelidade em 6/15 saídas no revisor automatizado. Mais geração, por si só, não demonstra mais valor.

## Valor e prova de entrega

Medir separadamente resolução sem atendente, minutos líquidos no atendimento preparado e qualidade/tempo de encaminhamento das exceções. Contar cada ticket uma vez e descontar falhas, correções e recontatos. [Cenários econômicos](economics.md).

A entrega pode ser revisada localmente via Docker. Capturas devem mostrar entrada, caminho, saída e limitação; não só a tela inicial. Já existem [evidências do fluxo atual](../process-log/evidencias/investigacao-v2/README.md). Para os caminhos futuros, produzir novas capturas somente após implementá-los. Publicação em VPS é complementar; uma URL não substitui reprodução e evidência.
