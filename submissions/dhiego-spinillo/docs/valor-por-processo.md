# Valor por processo: trabalho eliminado e trabalho que permanece

**21/09/2026.** Resposta à crítica de Dhiego: construir uma solução que aporte valor. A conta agregada anterior não sustentava escolher a intervenção. O novo recorte reúne contexto automaticamente e demonstra três caminhos completos em `/fluxos`; `/valor` calcula suas contribuições separadas.

## Problema e mecanismo

O D1 não mede tempo ativo nem duração confiável. O D2 contém pedidos de instrução, tentativas frustradas e históricos concatenados. Nossa leitura dos exemplos mostra trabalho possível de evitar: reenviar orientação já tentada, buscar fontes em sequência, reconstituir o histórico e perguntar ao cliente algo já registrado. Não conhecemos sua frequência ou duração na operação real.

Intervenção: IA extrai intenção, tentativas e sinais com trechos do texto; conectores consultam identidade, registros e notas; política escolhe procedimento elegível, preparação ou investigação. As consultas e ações desta demo são executadas contra registros locais fictícios. Isso prova comportamento do software, não integração de produção nem benefício operacional.

## Antes e depois demonstrados

| Processo | Trabalho convencional a observar no piloto | Com a solução | O que já funciona |
|---|---|---|---|
| Recuperação simples | Identificar pedido, conferir elegibilidade, orientar, acompanhar e registrar | Cliente inicia autosserviço; provedor confirma conclusão; sistema registra. Atendente só em exceção. | Emissão de token de demonstração, validade, consumo único, atualização de estado e trilha persistida. Nenhuma senha real. |
| Recuperação que falhou | Reabrir contexto, repetir instrução, pedir o mesmo relato, transferir sem histórico | Tentativa já informada é preservada; notas consultadas; resposta e encaminhamento preparados | D2 12.423: não repetir reset como solução. Falha durante autosserviço também transfere histórico e invalida o token. |
| Consulta de férias | Abrir outros tickets, ler notas, consultar lançamento e redigir | Fontes consultadas automaticamente; resposta por estado confirmado quando o pedido é único | D2 34.887: contexto fictício reunido. Na extração real com IA, pedidos múltiplos impedem uma resposta incompleta. |
| Possível incidente | Reconstituir relato e evidências, distinguir assunto de gravidade | Trechos preservados e contexto reunido para investigação | D2 45.725: investigação humana, sem atribuir causa, reset ou resolução automática. |

O classificador de oito categorias permanece disponível em `/classificador`, com seus resultados e limites preservados. Não controla os novos procedimentos. A extração restrita não usa o recap livre anterior como autorização.

## Hipóteses de minutos: decomposição para validar

Não foram cronometradas. Substituir por observação do trabalho ativo, incluindo falhas, revisão e recontatos.

| Procedimento | Antes: hipótese | Depois: hipótese |
|---|---|---|
| Recuperação simples | Identificar/conferir 2 min + orientar 3 + iniciar 2 + acompanhar 3 + registrar 2 = **12 min** | **1 min residual médio** por sucesso, para monitoramento/controle; não é clique obrigatório em cada ticket. Falha mantém os 12 min e acrescenta **2 min** da tentativa frustrada. |
| Atendimento preparado | Ler/entender 3 min + outros tickets/notas 3 + consultar estado 2 + redigir 2 + registrar 2 = **12 min** | Conferir fontes/rascunho 3 + tratar lacunas/correções 2 + responder/registrar 2 = **7 min**. |
| Investigação humana | Medir conforme complexidade | **Ganho atribuído zero** nesta projeção. Benefício de qualidade/continuidade exige avaliação própria. |

Não há ganho garantido por retirar cliques: consultas podem falhar e saídas podem custar mais revisão. É permitido aumentar o tempo posterior na calculadora para representar esse caso.

## Portfólio ilustrativo, não volume automatizável medido

2.500 tickets/mês, contexto anual de 30 mil. Hipótese: 50 elegíveis ao autosserviço, 1.000 à preparação e 1.450 à investigação. Esses volumes **não são estimativas derivadas dos datasets** nem meta aprovada. Os grupos são exclusivos, e falhas do primeiro não são novamente contadas como volume do segundo.

Com 80% de adoção e 80% de resolução sem recontato no autosserviço:

- Autosserviço: 40 usos, 32 conclusões e 8 falhas/mês. Ganho esperado = `80% × (12−1) − 20% × 2 = 8,4 min/uso` → **5,6 h/mês**.
- Preparação: 800 usos × `(12−7)` → **66,67 h/mês**.
- Total: **72,27 h/mês**, das quais aproximadamente 92% vêm da preparação. Reset isolado não paga a operação de R$ 500/mês neste cenário.

Mantendo as hipóteses anteriores — salário R$ 4 mil, fator 1,7, 160h produtivas, conversão de 50% em despesa evitada, R$ 6 mil de implantação e R$ 500/mês de operação — resulta em **R$ 1.035,67 de saldo mensal**, **53,57% de ROI no primeiro ano** e **5,79 meses de recuperação simples**. A melhoria vem de especificar a intervenção e suas etapas; o cenário continua hipotético, não uma promessa de retorno.

Os custos também precisam de orçamento: R$ 6 mil exemplificam 40h de implantação/integração/treinamento × R$ 150/h; R$ 500/mês exemplificam R$ 100 de infraestrutura + R$ 100 de APIs + 2h × R$ 150/h de manutenção. Essas taxas não são cotações nem custos observados do protótipo. Doze meses constantes, sem curva de adoção.

**Condição para investir:** sob esses custos e conversão, recuperar pelo menos **47,06 horas humanas/mês** para pagar o primeiro ano. Sem contribuição do autosserviço, 5 minutos líquidos e adoção de 80% exigiriam aproximadamente **706 tickets elegíveis à preparação/mês** (28,24% do volume do cenário). Isso é uma condição de equilíbrio a investigar, não elegibilidade já comprovada.

## Evidência e limites

- 204 testes do conjunto verificam contratos, regras, estados, cálculo e regressões.
- [Rodada com IA](../solution/reports/fluxos-desenvolvimento.json): sete cenários conhecidos, expectativas definidas por Codex, não avaliação independente. Seis usaram extração de IA aceita; um recorreu ao fallback por indisponibilidade ou rejeição da resposta, sem diagnóstico mais específico registrado. As sete rotas coincidiram com a expectativa de desenvolvimento. Isso não equivale a acurácia de produção.
- As citações literais reduzem invenção verificável, mas não garantem interpretação correta. Históricos concatenados detectados, pedidos múltiplos, fonte indisponível, restrição cadastral e falha de IA impedem a liberação autônoma.
- Recuperação de conta real pertence ao provedor de identidade, com canal verificado e controles próprios; a demo não implementa autenticação real. A máquina de estados segue princípios de token vinculado, expiração e uso único descritos pela [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html).
- Regras lexicais são fallback limitado, identificado na interface. Na demo sem IA, procedimentos elegíveis continuam exigindo escolha explícita do cliente. Os controles não são prova de cobertura de todas as formas de incidente ou ambiguidade.

## Próxima prova operacional

Integrar uma fonte real de tickets/notas e uma consulta somente leitura ao sistema; observar trabalho ativo antes/depois em grupos comparáveis. Validar elegibilidade com referência humana. Medir resolução sem recontato no autosserviço e ganho líquido/qualidade na preparação. Dimensionar amostra depois do baseline. Manter intervenção somente se atingir o benefício mínimo com qualidade preservada; se a busca contextual não tiver volume ou ganho suficiente, revisar o investimento.

### Iteração preservada

A primeira rodada de seis cenários passou nas expectativas, mas a repetição no navegador do D2 46.304 revelou que o modelo classificou solicitações/cabeçalhos como tentativas. Preservamos [rodada inicial](../solution/reports/fluxos-desenvolvimento-inicial.json) e [DOM observado](../process-log/evidencias/fluxos-v1/iteracao-extracao.txt). O prompt passou a distinguir pedidos/cabeçalhos; uma regra conservadora bloqueia autosserviço em cadeias detectadas. O caso simples agora usa D2 1.083; o texto anterior permanece como sétimo cenário de ambiguidade, sem ser removido da avaliação.

A revisão independente encontrou uma falha conhecida no contexto que não bloqueava reset quando omitida do texto; corrigida com estado estruturado consultado e revalidação. Também corrigimos edição durante aprovação e exibição do rascunho efetivamente aprovado. Os testes incluem ambas as regressões.
