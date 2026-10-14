# Assistente executivo — contrato e operação

## Estado
Site v10 publicado em 13/10/2026; Edge `challenge-assistant` ACTIVE v8, verify_jwt=true. Modelo aprovado: `gpt-6-luna`, Responses API, reasoning none. Estrutura, consultas e interface implementadas. Chave e acesso ao modelo verificados em chamada real pelo servidor, com fixture sintético: consulta de contas, esclarecimento de MRR anual e recusa de previsão sem regra. A revisão de 13/10/2026 confirmou uma execução concluída no backend. Concluí a revisão visual do assistente em 13/10/2026. As verificações de integração abaixo mantêm o escopo registrado em cada etapa. Ver [Process Log](../process-log/assistant_2026-10-12.md).

## Contextos e responsabilidades
- Domínio: `web/domain/assistant.mjs`, catálogo tipado, validação de chamadas, limites e composição determinística da resposta numérica.
- Aplicação: `web/assistant/index.ts`, autenticação compartilhada, orquestração de até duas chamadas ao modelo, consulta de negócio e gravação atômica da resposta.
- Infraestrutura: Supabase Auth, Postgres privado/RLS, Edge e API OpenAI via HTTP. Credenciais exclusivas do runtime.
- Interface: `web/frontend/app/AssistantScreen.tsx`, também sincronizada no site. API e domínio separados da apresentação.

Bounded Context `assistant`: conversations, turns, executions, messages, tool_results e view quality_occurrences. Conversa pertence ao usuário e workspace verificados; todas as RPCs checam a sessão Auth ativa, membership e propriedade. Role não vem de formulário ou user_metadata. Mesmo administrador usa seu próprio histórico. Tabelas e funções não são concedidas a anon/authenticated; somente o gateway autenticado as executa.

## Dados e métricas
Uma ferramenta de negócio por pergunta, enum de nove métricas e parâmetros estritos; nenhum SQL arbitrário. País/setor usam valores do catálogo da versão, limitado a cem valores por dimensão e cem caracteres. Históricos de mudança desses atributos não existem: recortes usam atributos recebidos, não comprovação de segmento em uma época anterior.

| Métrica | Regra / granularidade |
|---|---|
| Contas | Cadastros distintos da versão, incluindo posteriores ao corte histórico; definição explícita. |
| Segmentos | Setor, país ou plano cadastral. Até cem grupos exibidos; aviso se a listagem for limitada. |
| MRR | Soma de snapshots de contratos no corte, sem trials, mesma regra do painel. |
| ARR anualizado | MRR contratual multiplicado por doze; não receita realizada ou previsão. |
| ARR declarado | Campo arr_amount nos mesmos contratos elegíveis; pode divergir da anualização. |
| Qualidade | Contas distintas por categorias suportadas, não soma de ocorrências ou amostra de exemplos. |
| Reconciliação | Flag de churn e zero cancelamentos no corte; ausência de qualquer evento e apenas reativação incluídas. |
| Uso | Registros qualificados na janela histórica; observação ausente não é uso zero comprovado. |
| Satisfação | Média ponderada pela quantidade de respondentes elegíveis; sem extrapolação para todos. |

Qualidade: view completa deriva campos obrigatórios ausentes do contrato registrado; notas opcionais ausentes em tickets encerrados; divergência ARR/MRR; reconciliação no snapshot. Uma conta entra uma única vez no total, mesmo com múltiplos registros/regras. Informações opcionais ausentes não são necessariamente erros. O catálogo não representa todas as 89 verificações; não inferir completude porque uma categoria retorna zero. Regras da fonte usam a versão inteira; reconciliação usa o corte. Fonte inválida rejeitada no importador não aparece como versão publicada.

Valores monetários retornados como texto decimal; cartão e resposta principal derivam do SQL, sem cálculo livre do modelo nem conversão monetária. Moeda continua não informada. O modelo seleciona uma consulta tipada; esclarecimentos e limitações exibidos usam frases fixas do servidor. A definição e as ressalvas numéricas vêm da consulta. A segunda chamada para produzir explicação livre foi retirada: dados importados não passam a uma etapa de geração de texto.

Antes da consulta SQL, o servidor confere nomes explícitos de setor e país na pergunta atual contra o catálogo limitado da versão. Exige nome inteiro, ignorando maiúsculas/minúsculas: `Tech` não coincide com a parte final de `EdTech`. Se a ferramenta escolher outro filtro ou omitir o filtro explicitado, devolve esclarecimento sem consultar os dados; se houver dois nomes na mesma dimensão, também pede um recorte por vez. Sem nome reconhecido, mantém a seleção anterior do modelo e as verificações tipadas existentes. Não interpreta sinônimos, abreviações ausentes do catálogo ou referências somente no histórico; a proteção é delimitada a nomes explícitos reconhecidos. [Registro da validação](../process-log/assistant_filter_guard_2026-10-14.md).

Perguntas ambíguas usam esclarecimento. “MRR anual” deve distinguir ARR anualizado de receita realizada no período. Projeção, inferência causal, operações fora do catálogo e cálculo sem regra/dados recebem limitação explícita. Instruções em dados importados não conferem autorização.

## Histórico e continuidade
Histórico persiste no Supabase: busca em títulos/mensagens, paginação de trinta conversas e sessenta mensagens por página, renomear, arquivar/restaurar e retomar. Mensagens/evidências antigas preservam versão e filtros. Nova conversa usa versão publicada atual. Atualização de contexto é explícita, gera evento, conserva histórico e reinicia contexto enviado ao modelo; conversa antiga avisa sobre nova publicação. O botão “Explorar contas deste recorte” só abre para evidência da versão atual. Limpa busca, reconciliação, ordenação e paginação anteriores e aplica setor/país da evidência. A lista é exploratória: não representa as ocorrências específicas da métrica de qualidade ou de reconciliação. O banner preserva valor, referência e versão, e o resultado integral permanece na conversa.

Contexto do modelo usa até oito perguntas anteriores do usuário (até 1.500 caracteres cada), sem reenviar respostas anteriores do assistente; histórico visível continua paginado integralmente. Pergunta até 2.000 caracteres. Request UUID protege idempotência; replay concluído não chama provedor. Tentativas falhas/interrompidas reutilizam pergunta/contexto, com até três execuções por pergunta. Lease de noventa segundos impede duplicação concorrente e finalização tardia. UI acompanha pendência, conserva rascunho em falha e permite retomada de execução expirada. Falhas de leitura do histórico têm até três tentativas consecutivas, com intervalos de 5, 10 e 20 segundos; o botão “Atualizar resposta” consulta apenas o histórico. Um temporizador independente libera a retomada após o lease, mesmo se a leitura falhar. Nenhuma pergunta é reenviada automaticamente por falha de rede. O adaptador limita a espera a 75 segundos para pergunta, 20 para GET e 45 para outros POSTs; timeout não afirma que o processamento remoto falhou. A única repetição automática de request é o refresh já existente após 401, uma vez.

Limites atuais: cinquenta execuções por usuário/dia BRT, duzentas por workspace/dia, trinta novas conversas por usuário em 24h; uma chamada de até 1.000 tokens de saída por pergunta; RPC com timeout de quinze segundos, provedor com timeout de 25 segundos por chamada. Consumo observado, modelo, versão das instruções e IDs de resposta registrados nas execuções. Falhas podem ter consumo desconhecido, marcado como tal; não tratar o registro parcial como fatura completa ou teto monetário garantido.

## Secret e ativação
1. Abrir [challenge_g4_projeto → Edge Functions → Secrets](https://supabase.com/dashboard/project/uxpcrjryxrbwgpakesti/functions/secrets).
2. Criar `OPENAI_API_KEY`, com a chave da própria conta OpenAI como valor, e salvar. Nenhuma chave pelo chat/Git. Não existe campo de chave no site.
3. No Assistente IA, clicar “Verificar integração” ou reabrir a página. Configured indica apenas presença da chave; não valida crédito/permissão/modelo. Histórico continua legível sem chave.
4. Fazer uma pergunta simples, depois MRR/ARR, qualidade e seguimento; conferir evidência com o painel. Reabrir conversa após logout/login para aceitar persistência e isolamento.

Secrets ficam disponíveis sem novo deploy, conforme documentação Supabase. Chave OpenAI nunca enviada ao navegador/modelo como dado, nem lida/registrada pelo agente. `store:false` evita usar armazenamento de respostas OpenAI para o histórico; não significa ausência absoluta de retenção pelo provedor. Dados enviados: contexto recente, catálogo limitado e resultado necessário da consulta. Nenhum upload bruto, senha ou segredo de backend é enviado como contexto.

## Reproduzir
Após fundação, web, escopos e autenticação, aplicar `db/assistant.sql`, depois `db/assistant_context_catalog.sql` e `db/assistant_prompt_hardening.sql`. No frontend: npm ci, npm run check, npm run test:ui, npm run build. Domínio: `node --test web/tests/assistant.test.mjs`. Empacotar: `node scripts/build_assistant_edge.mjs --output .work/assistant-edge/index.js`; implantar como `index.js` em challenge-assistant, verify_jwt=true. Arquivo gerado não versionado.

`tests/db_assistant.sql` usa uma sessão real já existente, sob service_role, e rollback; não cria Auth.users/Auth.sessions. Testa catálogo, equivalência de MRR, anualização, contas distintas, replay, acesso privado e privilégios. Não executar sem sessão real ou interpretar falha de pré-condição como teste aprovado. `python web/tests/http_assistant.py` verifica três bloqueios HTTP anônimos, sem gravações. DOM/API/provedor nos testes JS são simulados; nenhum desses testes comprova chamada real OpenAI.

Documentação consultada: [function calling](https://developers.openai.com/api/docs/guides/function-calling), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [controles de dados](https://developers.openai.com/api/docs/guides/your-data), [Secrets Supabase](https://supabase.com/docs/guides/functions/secrets).

## Verificação real da integração — após cadastro do Secret

Confirmei o cadastro do Secret. Uma verificação separada chamou o mesmo executeQuestion canônico e a Responses API real, sem usar conversa, identidade Auth fictícia ou dados da carteira. Fixture explícito com três cadastros de teste. Passaram consulta factual, esclarecimento de MRR anual e recusa de forecast sem regra. Quatro respostas reais da OpenAI; 2.539 tokens de entrada e 198 de saída observados. Isso comprova chave/modelo/protocolo e os três exemplos, não aceitação de toda pergunta de negócio nem de interação no navegador.

Verificação temporária protegida por nonce aleatório de 256 bits, mantido só na memória do processo CLI. Somente SHA-256 armazenado na tabela privada assistant.integration_checks; validade de dez minutos, consumo atômico antes de chamadas e perguntas fixas. Sem prompt arbitrário ou acesso a dados de usuários. Chave OpenAI permaneceu no runtime. Ao terminar, challenge-assistant-probe foi substituída por resposta 410 incondicional, verify_jwt=true. A invocação anônima observada também retornou 410, sem acesso a dados ou chamadas ao provedor; a função permanece implantada, com o comportamento de diagnóstico retirado. Reuso, nonce desconhecido e sobrescrita de evidência bloqueados em teste SQL. Nenhum caminho de autenticação do assistente de produção foi alterado.

A migração auxiliar db/assistant_integration_checks.sql mantém apenas metadados privados da verificação. scripts/run_assistant_probe.py gera nonce na memória e imprime só hash; scripts/build_assistant_probe.mjs usa o módulo canônico. Esse procedimento é administrativo e opcional, exige nonce novo e retirada do endpoint após a verificação; não faz parte da aplicação pública. tests/db_assistant_integration_checks.sql verifica os controles com rollback, sem ler valores de Secrets.
