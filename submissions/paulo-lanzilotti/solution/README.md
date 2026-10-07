# Foco: fila de prioridade para o Challenge 003

Aplicação local, sem dependências externas, usando as oportunidades abertas do [dataset indicado pelo challenge](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics).

## Abrir

Na pasta deste projeto, execute:

```bash
python3 server.py
```

Abra `http://localhost:8765` no navegador. O servidor escuta apenas em `127.0.0.1`.

## O que faz

- Lista 2.089 oportunidades abertas (`Engaging` e `Prospecting`).
- Busca por empresa, produto ou ID.
- Filtra por estágio, vendedor, manager e região.
- Ordena ações disponíveis pelo prazo mais próximo e usa `priority_score` para desempatar.
- Mostra contexto e uma próxima ação ao selecionar uma oportunidade.
- Queue Mode abre um modal com um cliente por vez, respeitando vendedor, filtros e prazos da fila. Se nenhum vendedor estiver escolhido, solicita a carteira antes de começar.
- No modal, `No Answer`, `Pular` e `Contactado` ficam nessa ordem. Contactado substitui os botões por notas, resultado e retorno opcional; salvar avança ao próximo cliente.
- Depois da quinta ação da sessão, o Queue Mode mostra uma Builder Card editorial inspirada no portfolio do autor. Ela não é uma oportunidade, não altera a fila e pode ser fechada para continuar o fluxo.
- Casos enviados à revisão durante o Queue Mode ficam disponíveis na carteira e na próxima sessão; não reaparecem imediatamente no mesmo fluxo. Fechar com o botão ou Escape volta à carteira; rascunhos ficam na memória da página até o recarregamento.
- `Pular` adia sem contar ligação; `No Answer` conta uma tentativa e agenda retorno.
- `Contactado` registra observação, resultado e, quando necessário, uma data de retorno.
- Casos que pedem decisão ficam em revisão para reagendar ou encerrar.
- A última observação aparece quando a oportunidade é selecionada novamente.
- Normaliza `GTXPro` para `GTX Pro` ao juntar o catálogo.

A lista mostra oito oportunidades por página. O filtro de vendedor continua no próximo acesso; a ordem da fila vem do servidor. A visão de todos os vendedores é somente leitura.

## Notas e interações

As interações são salvas em `runtime/workflow.sqlite3`. `interaction_events` guarda cada decisão com horário, vendedor, resultado, data marcada e identificador único da ação. `opportunity_state` guarda observação, última tentativa real, prazo, estado da fila e versão do registro. A API só aceita ações do vendedor responsável; a versão impede salvar uma decisão baseada em estado antigo de outra aba. `Pular` e `No Answer` não apagam notas. O score não muda com essas ações; a ordem operacional muda.

## Cadência da fila

- A fila é separada por vendedor responsável. Casos para revisar vêm primeiro; depois, ações elegíveis ordenadas pelo prazo mais próximo e, em empate, pelo score. Retornos futuros ficam no fim.
- Prioridade protegida = 20% superiores da carteira de cada vendedor, incluindo todos os empates no corte. A primeira tentativa tem meta de dez dias úteis; as demais oportunidades, vinte. Uma tentativa real reinicia o ciclo; `Pular` preserva o prazo anterior.
- `Pular`: volta no próximo dia útil, sem contar como ligação. Dois pulos consecutivos exigem revisão.
- `No Answer`: conta como tentativa; retorno após 1 e depois 3 dias úteis. A terceira falta de resposta exige revisão, sem reagendamento automático.
- `Contactado`: positivo sugere 2 dias úteis, neutro 5; o vendedor pode indicar a data combinada. Negativo vai para revisão, sem ligação automática.
- Revisão permite marcar uma nova data ou encerrar. Retornos futuros podem ter a data alterada, mas não aceitam uma ligação antecipada pela fila. Uma data combinada pelo cliente prevalece sobre a cadência padrão.
- Round Robin distribui apenas a propriedade inicial. Após a distribuição, a oportunidade permanece com o vendedor responsável. Os deals do dataset já trazem essa atribuição; esta versão não importa leads novos.

Num CRM real, a atribuição inicial precisa ocorrer em uma transação única no servidor. Uma nova oportunidade de empresa que já tem responsável deve primeiro seguir a regra de propriedade da conta; o Round Robin vale para empresas sem dono. Reatribuições posteriores são decisões explícitas e preservam o histórico.

O dataset tem 2.089 negócios abertos em 27 carteiras com oportunidades. São 77,4 por vendedor em média; a maior tem 194. Para passar por toda a carteira uma vez em dez dias úteis, seriam necessárias cerca de 8 tentativas diárias por vendedor em média, ou 20 na maior carteira, antes dos retornos. A base não registra ligações históricas. A API passa a medir tentativas reais (`Contactado` + `No Answer`) separadamente de pulos e só calcula uma capacidade observada após cinco dias ativos, usando a mediana dos últimos dez dias ativos. A meta de dez dias depende de capacidade suficiente; nenhum algoritmo consegue garanti-la quando o trabalho devido excede a capacidade.

O dataset não contém IDs de contatos pessoais. Notas e eventos ficam vinculados ao `opportunity_id`. Empresas com outras tentativas nos últimos sete dias geram um aviso, sem bloquear automaticamente negócios distintos. O seletor de vendedor representa o operador nesta demonstração, mas não autentica uma pessoa; autenticação e reserva de trabalho seriam necessárias antes de uso simultâneo em produção. Os dados ficam nesta máquina e não são enviados a um CRM externo.

O campo é calculado para cada oportunidade aberta e gravado em `data.json` e `sales_pipeline_scored.csv`. Negócios fechados ficam com o score vazio no CSV. A tela mostra o número no detalhe; os fatores e a explicação ficam recolhidos em “Como foi priorizada”. O processo de desenvolvimento está em `PROCESS_LOG.md`.

## Priority Score

`priority_score = arredondar(momento + valor + fit + histórico)` (0 a 100).

| Componente | Pontos | Regra |
| --- | ---: | --- |
| Momento | 0–60 | `Engaging` até 104 dias = 60; 105–138 dias = 35; acima de 138 = 10; `Prospecting` = 30. |
| Valor | 0–25 | Logaritmo do preço de tabela, normalizado entre US$ 55 e US$ 26.768. O valor negociado ainda não existe nos deals abertos. |
| Fit | 0–10 | Até 8 pelo diferencial de vitória de `setor × produto` contra a média do produto; até 2 pelo quartil de funcionários. |
| Histórico | 0–5 | Taxa histórica de vitórias da conta comparada à média geral. |

As taxas de `setor × produto` são aproximadas da média do produto com o equivalente a 100 negócios prévios. O histórico da conta é aproximado da média geral com 50 negócios prévios. Essa suavização impede que amostras pequenas dominem o score. Sem conta vinculada, fit e histórico recebem valores neutros (5 e 2,5 pontos, respectivamente); a confiança dos dados fica `limited`. Com conta, fica `partial`, pois não há histórico de atividades.

Detalhe das parcelas:

```text
valor = 25 × limitar(log(preço / 55) / log(26768 / 55), 0, 1)

taxa_produto = vitórias_produto / fechados_produto
taxa_setor_produto = (vitórias_célula + 100 × taxa_produto) / (fechados_célula + 100)
fit_setor = limitar(4 + 50 × (taxa_setor_produto − taxa_produto), 0, 8)
fit_porte = 0,5 / 1 / 1,5 / 2 conforme o quartil de funcionários
fit = fit_setor + fit_porte (ou 5 sem conta)

taxa_geral = vitórias_total / fechados_total
taxa_conta = (vitórias_conta + 50 × taxa_geral) / (fechados_conta + 50)
histórico = limitar(2,5 + 20 × (taxa_conta − taxa_geral), 0, 5)
```

Todos os históricos usam apenas negócios fechados até a data de referência. O valor dos componentes e a confiança também ficam gravados no JSON para permitir auditoria.

O cálculo usa **31/12/2017** como data de referência do dataset. Num CRM ativo, o campo precisa ser recalculado diariamente e quando estágio, produto ou conta mudarem. Ele ordena trabalho comercial; não é probabilidade de fechamento.

## Limites dos dados

O dataset é histórico. Oportunidades abertas não possuem `close_value`; 1.425 das 2.089 também não têm conta vinculada. Não há histórico de atividades nem contatos pessoais. Por isso, a interface sugere revisão manual, sem alegar que um cliente está aguardando resposta.

## Atualizar dados

Baixe os CSVs do Kaggle e execute:

```bash
python3 scripts/build_data.py /caminho/para/os/csvs
```

O script gera `data.json` e `sales_pipeline_scored.csv` na pasta do projeto.
