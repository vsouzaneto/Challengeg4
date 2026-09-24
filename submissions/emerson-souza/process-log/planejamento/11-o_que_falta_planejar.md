# O que falta planejar (decisões em aberto)

## A. Pendências de dados
| # | Pendência | Quem | Status |
|---|---|---|---|
| A1 | Baixar o **Dataset 2 do 002** (IT Service Ticket Classification, ~48 mil textos) → `02/dados/002-suporte/` | Emerson | ⬜ **bloqueia o classificador** |
| A2 | Definir como calcular **tempo de 1ª resposta e de resolução** no DS1 do 002 (não existe hora de abertura; as colunas são datas/horas) | Emerson + IA | ⬜ proposta abaixo |

**Proposta A2:** usar *resolução − 1ª resposta* só quando for positiva, e marcar como "inconsistente" as ~49% negativas. Mostrar na tela a regra e quantos tickets ela exclui. Alternativa: considerar o dataset inadequado para medir tempo e dizer isso no relatório.

## B. Decisões de negócio (premissas que aparecem nos números)
| # | Decisão | Sugestão (editável na tela) |
|---|---|---|
| B1 | **Custo/hora do agente de suporte** (para o desperdício em R$) | R$ 45/h (editável) |
| B2 | **Meta de SLA** por prioridade (para as "horas desperdiçadas") | Critical 4 h · High 8 h · Medium 24 h · Low 48 h |
| B3 | **Custo implícito de patrocínio** (o dataset não tem custo) | Custo por mil seguidores (editável) |
| B4 | **"Hoje"** do pipeline do 003 | 31/12/2017 (última data dos dados) |
| B5 | Limite de **queda de uso** para o alerta de churn | 30% |
| B6 | Limiares de **confiança do classificador** | ≥ 0,85 automático · 0,60–0,85 sugere e o humano confirma · < 0,60 humano |

## C. Decisões técnicas
| # | Decisão | Opções | Sugestão |
|---|---|---|---|
| C1 | Janela própria | pywebview + Streamlit · PySide6 | **pywebview + Streamlit** |
| C2 | LLM | nenhum · local (Ollama) · API (Anthropic) · os dois | Sistema **funciona sem LLM**; LLM opcional para respostas sugeridas e textos |
| C3 | Classificador | TF-IDF + linear · embeddings · zero-shot LLM | **Os 3 comparados**; o de produção é o que der melhor custo × acurácia |
| C4 | Onde guardar as sessões | pastas + JSON · SQLite | **SQLite** (sessões e sub-sessões ligadas) |
| C5 | Nome do sistema | — | Emerson escolhe |
| C6 | Idioma | PT-BR | PT-BR |

## D. Ordem de construção (proposta)
1. **Núcleo:** janela, sessões, entrada de dados, De/Para, relatório base.
2. **Retenção (001)**, obrigatórios 🔴.
3. **Suporte (002)**, obrigatórios 🔴 + classificador (depende de A1).
4. **Cruzamento Churn → Suporte** (exemplo-âncora).
5. **Vendas (003)**, obrigatórios 🔴 (+ filtros).
6. **Mídia (004)**, obrigatórios 🔴 + teste de sanidade.
7. Demais cruzamentos 🟡🔵.
8. Diferenciais 🟦.
9. Executável + documentação + entrega.

Cada etapa só fecha quando os testes de aceite dela (`07-requisitos_obrigatorios.md`) passam **com dados reais**, e ela é registrada no process log.

## E. Riscos
| Risco | Mitigação |
|---|---|
| Escopo grande (4 × 4–6 h) | Obrigatórios primeiro; diferenciais só depois |
| Dados sem sinal (002/004) parecerem "análise fraca" | Provar com estatística + teste de sanidade + recomendação por custo |
| `.exe` pesado (NLP + embeddings) | Embeddings opcionais; avaliar o tamanho cedo |
| Cruzamentos parecerem "inventados" | Selos 🟢🟡🔵 + texto de limite em cada botão |
