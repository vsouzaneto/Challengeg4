# Telas do painel (janela própria, como software)

> Ideia do Emerson: o sistema abre **numa janela de programa**, não numa aba do navegador.

## Estrutura geral
```
┌───────────────────────────────────────────────────────────────┐
│ [logo] Nome do sistema                          [? Como usar] │
├──────────────┬────────────────────────────────────────────────┤
│ SESSÕES      │                                                │
│ + Nova       │   conteúdo da sessão aberta                    │
│ ▸ Churn Raven│   (abas do módulo)                             │
│   └ Suporte… │                                                │
│ ▸ Suporte DS1│                                                │
│ ▸ Leads CRM  │                                                │
│ ▸ Mídia 52k  │                                                │
└──────────────┴────────────────────────────────────────────────┘
```
Sub-sessões cooperativas ficam **penduradas** na sessão-mãe (└).

## Fluxo "Nova sessão"
1. **Nome** da sessão.
2. **Tipo de análise:** Retenção (Churn) · Suporte · Vendas (Leads) · Mídia (Social).
3. **Dados:** "Usar dados do desafio" (1 clique) **ou** enviar arquivos (CSV/Excel/JSON).
4. **De/Para:** cada campo do contrato ↔ coluna do arquivo (pré-preenchido quando reconhece), com os obrigatórios destacados.
5. **Rodar** → resultado.

## Telas de resultado por módulo (abas)
Todas terminam com dois blocos: **"Qualidade dos dados"** e **"Usar em outra ferramenta"** (botões com selo 🟢🟡🔵).

| Módulo | Abas (🔴 obrigatório) |
|---|---|
| **Retenção** | Resumo executivo 🔴 · Causa raiz 🔴 · Segmentos e contas 🔴 · Plano de ação 🔴 · Modelo 🟦 · Relatório 🔴 |
| **Suporte** | Resumo 🔴 · Gargalos 🔴 · Satisfação 🔴 · Desperdício 🔴 · Automação (o que sim/não + fluxo) 🔴 · Testar ticket (classificador/roteador) 🟦* · Relatório 🔴 |
| **Vendas** | Pipeline priorizado (com filtros e "por quê") 🔴 · Detalhe do deal 🔴 · Como o score funciona 🔴 · Visão do manager 🟦 · Relatório 🔴 |
| **Mídia** | Resumo 🔴 · Engajamento 🔴 · Patrocínio 🔴 · Audiência 🔴 · Estratégia (concentrar / política / parar / quick wins) 🔴 · Acompanhamento 🟦 · Relatório 🔴 |

## Padrões visuais
- Português do Brasil em tudo (os nomes das colunas originais aparecem entre parênteses).
- Todo número importante vem com a **frase do que ele significa**.
- Gráficos com n (tamanho da amostra) e intervalo de confiança quando houver comparação.
- Um botão **Relatório** por sessão (PDF + Markdown), e exportação CSV/JSON das listas.
