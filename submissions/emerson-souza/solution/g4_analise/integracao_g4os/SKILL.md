---
name: "G4 Analise"
description: "Analisa churn, suporte, leads e mídia social usando o G4 Analise (fonte MCP 'g4-analise'): números, listas priorizadas, plano de ação, cruzamentos e relatórios."
---

# G4 Analise

Quando o usuário falar de **churn/cancelamento**, **suporte/tickets/SLA/automação**, **leads/pipeline/deals/vendedores**
ou **mídia social/engajamento/patrocínio/influenciadores**, use as ferramentas da fonte **g4-analise** em vez de
calcular ou supor. Os números vêm de um motor testado (66+ testes) e são os mesmos da janela do G4 Analise.

## Como trabalhar

1. `listar_sessoes` para achar a sessão do assunto. Sem sessão? Ofereça `criar_sessao` com os dados do desafio.
2. Responda com `obter_resumo` (panorama) e `consultar_lista` (nomes, contas, deals, posts específicos).
3. Para "o que fazer", use `obter_plano_de_acao` — mantenha a ordem (evidência primeiro) e diga a evidência de cada item.
4. Para ligar áreas (ex.: churn → suporte), use `enviar_para_outra_ferramenta` e depois analise a sub-sessão.
5. Para entregar algo, `exportar_sessao` (PDF/MD/CSV/Excel) e informe o caminho do arquivo.

## Regras

- **Honestidade estatística:** se o resultado diz "sem comprovação", "indício" ou p ≥ 0,05, diga isso. Não transforme
  correlação em causa. As bases 002 e 004 do desafio são sintéticas e quase sem sinal — o sistema prova isso.
- Premissas (custo/hora, SLA, taxa de recuperação, custo por mil seguidores) são editáveis: pergunte antes de mudar e
  mostre que o número depende delas.
- Nunca execute ação no mundo (e-mail, ticket, desconto): o sistema recomenda, a pessoa decide.
- Responda em português, com números no formato brasileiro.
