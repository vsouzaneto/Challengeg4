# G4 Analise

Sistema de análise do Emerson (desafio G4 AI Master) com 4 ferramentas que trabalham **sozinhas ou juntas**:
**Churn** (001), **Suporte** (002), **Leads** (003) e **Mídia** (004). Roda no computador, sem serviço externo, e usa
as MESMAS sessões da janela do G4 Analise: o que o agente cria aparece na janela, e o contrário também.

## Escopo

- Sessões de análise (dados do desafio ou arquivos CSV/Excel/JSON do usuário, com De/Para automático).
- Por sessão: resumo executivo com números, listas priorizadas, plano de ação com a força da evidência, método.
- Cooperativo: enviar o resultado de uma ferramenta para outra (ex.: contas em risco → Suporte).
- Protótipos: classificar um ticket novo (Suporte) e recomendar um post (Mídia).
- Exportar relatório PDF/Markdown, CSV dos dados analisados e Excel completo para Downloads\G4 Analise.

## Guidelines

- **Nunca calcule nem invente números**: use as ferramentas. Repita a ressalva de evidência que vem nos resultados
  ("sem comprovação", "indício", p-valor): várias bases do desafio são sintéticas e quase sem sinal.
- Comece por `listar_sessoes`. Se não houver sessão do módulo pedido, ofereça `criar_sessao` (dados do desafio).
- Para arquivos do usuário: `sugerir_depara` primeiro, mostre a sugestão, só depois `criar_sessao`.
- A primeira análise de uma sessão pode levar até ~40 s (Suporte treina o classificador; Mídia tem 52 mil posts).
- `criar_sessao`, `enviar_para_outra_ferramenta` e `exportar_sessao` criam coisas novas (nada é apagado ou
  sobrescrito) — por isso pedem confirmação no modo Explorar.
- Nenhuma ferramenta manda mensagem, e-mail ou executa ação no mundo: o sistema recomenda, a pessoa decide.

## Ferramentas

| Ferramenta | Para quê |
|---|---|
| `listar_ferramentas` | Módulos, tabelas, listas consultáveis e cruzamentos disponíveis |
| `listar_sessoes` | Sessões salvas (id, módulo, origem) |
| `obter_resumo` | Resumo executivo + qualidade dos dados (aceita `premissas`) |
| `obter_plano_de_acao` | Ações/estratégia priorizadas com evidência |
| `consultar_lista` | Uma lista da análise com filtros, ordenação e limite |
| `obter_metodo` | Como cada número foi calculado |
| `sugerir_depara` | De/Para automático para arquivos próprios |
| `classificar_ticket` | Suporte: categoria + confiança + automático/humano + tickets parecidos |
| `recomendar_post` | Mídia: engajamento esperado e se trocar formato/plataforma rende mais |
| `criar_sessao` | Nova sessão (dados do desafio ou arquivos) |
| `enviar_para_outra_ferramenta` | Cruza ferramentas (cria sub-sessão) |
| `exportar_sessao` | PDF, Markdown, CSV ou Excel em Downloads\G4 Analise |

Listas por módulo: churn (`contas_priorizadas`, `precisa_suporte`, `sinais`, `motivos`, `segmentos`) · suporte
(`chamados`, `gargalos`, `satisfacao`, `desperdicio`, `automacao`) · leads (`foco`, `requalificar`, `prospeccao`,
`vendedores`, `fatores`) · mídia (`dimensoes`, `combinacoes`, `patrocinio_por_faixa`, `custo_por_faixa`, `audiencia`,
`painel_semanal`).

## Examples

- "Quais contas eu salvo esta semana?" → `listar_sessoes` → `consultar_lista(lista="contas_priorizadas", limite=10)`
- "O que o vendedor da região West ataca na segunda?" → `consultar_lista(lista="foco", filtros={"regiao": "West"})`
- "Vale patrocinar influenciador?" → `obter_resumo` (sessão de Mídia) → `consultar_lista(lista="custo_por_faixa")`
- "Esse ticket pode ir direto pra fila?" → `classificar_ticket(texto=...)`
- "Manda as contas em risco pro suporte" → `enviar_para_outra_ferramenta(destino="suporte")` → `obter_resumo` da sub-sessão
- "Gera o relatório do churn" → `exportar_sessao(formato="pdf")`
