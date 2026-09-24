# Tecnologias e o painel gráfico

## O que o repositório sugere
| Desafio | Ferramentas prováveis (índice oficial `challenges/README.md`) |
|---|---|
| 001 Churn | Python/R, notebooks, ferramentas de visualização |
| 002 Suporte | Python, NLP/LLMs, frameworks web |
| 003 Lead Scorer | Qualquer stack: *"o que importa é funcionar"* (Streamlit, React, Dash, API, planilha, bot…) |
| 004 Social | Python/R, notebooks, visualização |

Regra geral: *"qualquer ferramenta de IA é permitida"* e *"um AI Master que consegue 'vibe code' uma solução funcional tem vantagem"*.

## Proposta de stack
| Camada | Tecnologia | Por quê |
|---|---|---|
| Dados e análise | Python, pandas, numpy | Padrão, atende os 4 desafios |
| Estatística / ML | scikit-learn (+ statsmodels, se precisar de testes) | Scores, validação cruzada, modelos interpretáveis |
| NLP (002) | TF-IDF + modelo linear (baseline) · embeddings (sentence-transformers) · zero-shot com LLM | Comparar 3 abordagens com números, como a dica do desafio pede |
| LLM (opcional) | Local (Ollama / LM Studio) **ou** API (Anthropic) | Respostas sugeridas, ações, De/Para automático; o sistema funciona sem LLM |
| Gráficos | Plotly | Interativo, funciona no painel e em relatório |
| Relatórios | PDF + Markdown + CSV/JSON | Executivo, BI e integração |
| Armazenamento das sessões | SQLite local (ou pastas + JSON) | Sessões, sub-sessões e histórico |

## O painel "como um software no computador"
**Ideia do Emerson:** abrir um painel gráfico no PC **numa janela própria, como um software**. ✅ Decidido. Opções avaliadas:

| Opção | Como fica | Prós | Contras |
|---|---|---|---|
| **A. Streamlit dentro de uma janela própria** (pywebview) ⭐ | Abre uma **janela de programa** (sem barra de endereço), por dentro é o painel web | Rápido de construir, gráficos ricos, já sabemos gerar `.exe` | Pacote grande (~300 MB+) |
| B. Streamlit no navegador | Abre uma aba do navegador | O mais simples | Não "parece software" |
| C. App nativo (PySide6/Qt) | Programa Windows clássico | Visual 100% nativo | Bem mais código de interface, mais lento para iterar |

**Recomendação:** **A**. A experiência é de software e, por baixo, os módulos são reaproveitáveis e testáveis. Entrega final: `.exe` na Release + código no PR.

## Estrutura de telas (rascunho)
1. **Início:** lista de sessões (e sub-sessões penduradas), botão **Nova sessão**.
2. **Nova sessão:** escolher **Churn / Suporte / Leads / Mídia** → enviar arquivos (ou "usar dados do desafio") → De/Para com sugestão automática → Rodar.
3. **Resultado do módulo:** abas de diagnóstico, listas acionáveis, recomendações, relatório → bloco **"Usar em outra ferramenta"** (botões com selo 🟢🟡🔵).
4. **Sub-sessão cooperativa:** mesma tela do módulo de destino, com a faixa *"veio de: Churn RavenStack → 38 contas em risco"*.
5. **Como usar:** ajuda embutida.
